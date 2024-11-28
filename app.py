import os
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')


# Function to use AI for matching keywords from a list to the summary
def match_keywords_with_ai(summary, keyword_list):
    try:
        # Construct a prompt to ask AI to match only the relevant keywords
        prompt = f"""
        From the following text, identify which of these keywords are mentioned. Only return the keywords that appear in the text. Do not add any additional explanations or text.

        Text: "{summary}"

        Keywords: {', '.join(keyword_list)}

        Return only the keywords that appear in the text, separated by commas.
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
        
        # Clean and return the keywords as a list, ensuring no empty results
        if result:
            # Split the keywords by commas and clean up any extra spaces
            keywords = [keyword.strip() for keyword in result.split(',') if keyword.strip()]
            return keywords
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
        categories = data.get('categories', [])

        if not summary:
            return jsonify({"error": "Summary text is required"}), 400

        # Use AI to match keywords for each category
        selected_categories = match_keywords_with_ai(summary, categories)

        # Return the selected keywords
        return jsonify({"selected_categories": selected_categories})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
