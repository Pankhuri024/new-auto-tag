import os
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')


# Function to analyze text using AI
def analyze_text_with_ai(text, keyword_list, category_name):
    try:
        prompt = f"""
        Analyze the following text and extract only the most relevant keywords or phrases related to {category_name} from this list: {', '.join(keyword_list)}.

        Text: "{text}"

        Return a list of the most relevant keywords.
        """
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7,
        )
        result = response['choices'][0]['text'].strip()
        # Convert the result to a Python list
        return result.split(", ") if result else []
    except Exception as e:
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

         # Use AI to analyze the text and extract relevant keywords
        selected_categories = analyze_text_with_ai(summary, categories, "categories")
        selected_elements = analyze_text_with_ai(summary, elements, "elements")
        selected_tools = analyze_text_with_ai(summary, tools, "tools")
        selected_goals = analyze_text_with_ai(summary, goals, "goals")
        selected_research_types = analyze_text_with_ai(summary, research_types, "research types")
        selected_industries = analyze_text_with_ai(summary, industries, "industries")

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
