import os
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')


# Function to use AI for matching keywords from a list to the summary
def match_keywords_with_ai(summary, elements):
    try:
        # Construct a strict prompt
       
        formatted_elements = ', '.join(elements)
        print("formatted_elements", formatted_elements)
       
        prompt = f"""
        You are a text analysis assistant. Your task is to extract exact matches from the following summary using the provided list of elements.

        Summary: "{summary}"

        Elements: {formatted_elements}

        Your task is to **only** return the exact words or phrases from the summary that **exactly match** any of the elements (case-insensitive). If no exact match is found, return an empty string. Do not infer or add anything beyond exact matches. For example, if the summary does not mention "A/B Test", do not return "Data Analysis" or other terms that are not directly present in the summary.

        Return only the exact matches, comma-separated, and no extra words. If no matches are found, return an empty string.
        """





        
        # Requesting AI to check which keywords are in the summary
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0,  # Lower temperature for deterministic responses
        )

        result = response['choices'][0]['message']['content'].strip()
         # Log the raw response for debugging
        print("AI Raw Response:", result)
        
        # Clean and filter AI output
        if result:
            matched_keywords = [kw.strip() for kw in result.split(',') if kw.strip()]
            print("matched_keywords:", matched_keywords)
            # Ensure only valid keywords from the original list are returned
            return [kw for kw in matched_keywords if kw in elements]
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
