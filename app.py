import os
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')


# Function to use AI for matching keywords from a list to the summary
def match_keywords_with_ai(summary, keyword_list):
    try:
        # Construct a strict prompt
        prompt = f"""
        You are a text analysis assistant. Your task is to extract only exact matches between a provided text and a list of keywords.

        ### Rules:
        1. Extract words or phrases **exactly** as they appear in both the text and the keyword list.
        2. Matches are **case-insensitive**, but must otherwise be exact (no substrings, partial matches, or inferred context).
        3. Do not infer meaning or context. If a keyword is not explicitly present in the text, do not include it.
        4. If no matches are found, return an empty response (leave blank).
        5. The response must be a **plain, comma-separated list** of the matching keywords. Do not include explanations, prefixes, or suffixes.
        6. The response must be present in the text or list of keyword.

        ### Input:
        Text: "{summary}"
        Keywords: {', '.join(keyword_list)}

        ### Output:
        Provide only the matching keywords as a comma-separated list. If no matches are found, return an empty response.
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
            return [kw for kw in matched_keywords if kw in keyword_list]
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
