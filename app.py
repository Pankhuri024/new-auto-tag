import os
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')


# Function to use AI for matching keywords from a list to the summary
def match_keywords_with_ai(summary, keyword_list):
    try:
        # Construct a strict prompt to prevent inference
        prompt = f"""
        Identify which of these keywords are explicitly mentioned or partially matched in the given text. Return only the keywords from the provided list that are explicitly mentioned or partially matched in the text. Do not infer or guess relevance.

        Text: "{summary}"

        Keywords: {', '.join(keyword_list)}

        Return only the keywords explicitly mentioned or partially matched, separated by commas. Do not add extra text.
        """
        
        # Request AI for matches
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strict and accurate assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0,  # Strict, deterministic behavior
        )

        # AI response
        result = response['choices'][0]['message']['content'].strip()

        # Log the raw response for debugging
        print("AI Raw Response:", result)

        # Split and clean the response
        if result:
            ai_keywords = [kw.strip() for kw in result.split(',') if kw.strip()]

            # Ensure only valid keywords from the list are returned
            filtered_keywords = [kw for kw in ai_keywords if kw in keyword_list]
            return filtered_keywords
        else:
            return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []




@app.route('/process_insight', methods=['POST'])
def process_insight():
    try:
        data = request.get_json()
        summary = data.get('summary', '')  # Default to empty string if not provided
        
        # Extract all keyword categories from the request
        categories = data.get('categories', [])
        elements = data.get('elements', [])
        tools = data.get('tools', [])
        goals = data.get('goals', [])
        research_types = data.get('research_types', [])
        industries = data.get('industries', [])

        if not summary:
            return jsonify({"error": "Summary text is required"}), 400

        # Use AI to match keywords for each category
        selected_categories = match_keywords_with_ai(summary, categories)
        selected_elements = match_keywords_with_ai(summary, elements)
        selected_tools = match_keywords_with_ai(summary, tools)
        selected_goals = match_keywords_with_ai(summary, goals)
        selected_research_types = match_keywords_with_ai(summary, research_types)
        selected_industries = match_keywords_with_ai(summary, industries)

        # Return the selected keywords
        return jsonify({
            "selected_categories": selected_categories,
            "selected_elements": selected_elements,
            "selected_tools": selected_tools,
            "selected_goals": selected_goals,
            "selected_research_types": selected_research_types,
            "selected_industries": selected_industries,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
