import os
from flask import Flask, request, jsonify
import openai
from urllib.parse import quote as url_quote
import logging

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')


# Function to use AI for matching keywords from a list to the summary
def match_keywords_with_ai(summary, keyword_list, category_name):
    try:
        # Construct a prompt for the AI to match the keywords from the list to the summary
        prompt = f"""
        From the following text, identify which of these keywords are mentioned. The list of keywords is related to {category_name}. 
        Only include the keywords that are present in the text.

        Text: "{summary}"

        Keywords: {', '.join(keyword_list)}

        Return a list of keywords from the provided list that appear in the text.
        """
        
        # Requesting AI to check which keywords are in the summary
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can also use other models
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )

        result = response['choices'][0]['message']['content'].strip()
        
        if result:
            # Clean and return the keywords in a list
            return [keyword.strip() for keyword in result.split(',') if keyword.strip()]
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

        # Use the predefined values if they are not passed in the request
        goals = data.get('goals', [])
        categories = data.get('categories', [])
        tools = data.get('tools', [])
        elements = data.get('elements', [])
        research_types = data.get('research_types', [])
        industries = data.get('industries', [])

        if not summary:
            return jsonify({"error": "Summary text is required"}), 400

        # Use AI to match keywords for each category
        selected_categories = match_keywords_with_ai(summary, categories, "categories")
        selected_elements = match_keywords_with_ai(summary, elements, "elements")
        selected_tools = match_keywords_with_ai(summary, tools, "tools")
        selected_goals = match_keywords_with_ai(summary, goals, "goals")
        selected_research_types = match_keywords_with_ai(summary, research_types, "research types")
        selected_industries = match_keywords_with_ai(summary, industries, "industries")

        # Return the auto-selected values
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
