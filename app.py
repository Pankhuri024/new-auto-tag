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
        print("keyword_list", elements)
        formatted_elements = ', '.join(elements)
       
        prompt = f"""
        You are a text analysis assistant. Your task is to extract words or phrases from the given text that match exactly with the provided list of elements. Always follow the strict rules mentioned below:

        ### Input:
        Summary: "{summary}"

        Elements: {formatted_elements}

        ### Strict Rules:
        1. *Extract only those words or phrases* that appear in both the *Summary* and *Elements* list *exactly as written*.
        2. Matching should be *case-insensitive, but it must be **exact* (i.e., no partial matches, substrings, or inferred context).
        3. If a word from the *Elements* list is *not explicitly found in the Summary, it should be **ignored*.
        4. If no matches are found in the *Summary* for any word in the *Elements* list, return an *empty response*.
        5. *Do not infer meaning or context. Only return those words or phrases from the **Elements* list that *appear exactly in the Summary*.

        ### Output:
        Provide the extracted words as a *comma-separated list* without any additional words or explanations. If no matches are found, return an empty response (blank).
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
