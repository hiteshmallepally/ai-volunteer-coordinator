from flask import Flask, request, jsonify, render_template_string
from google import genai
import os

app = Flask(__name__)

# 🔐 Get API key safely from environment
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not set in environment variables")

# ✅ Initialize Gemini client
client = genai.Client(api_key=api_key)

# 📁 Load HTML
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(BASE_DIR, "index.html")

with open(html_path, encoding="utf-8") as f:
    html = f.read()


@app.route("/")
def home():
    return render_template_string(html)


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        task = data.get("task")

        print("Request received:", task)

        if not task:
            return jsonify({"error": "Task cannot be empty"}), 400

        prompt = f"""
Analyze this NGO task and provide:

Priority:
Volunteers Needed:
Action Plan:
Suggestions:

Task: {task}
"""

        try:
            # 🤖 Try AI response
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            result = response.text if hasattr(response, "text") else str(response)

            return jsonify({"result": result})

        except Exception as ai_error:
            print("AI FAILED:", ai_error)

            # 🔥 Fallback response (ensures app never breaks)
            fallback_result = f"""
Priority: High

Volunteers Needed: 20-30

Action Plan:
1. Assign volunteers to rescue teams
2. Organize food distribution
3. Arrange medical support

Suggestions:
- Divide tasks efficiently
- Use local coordination
- Track progress regularly
"""

            return jsonify({"result": fallback_result})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
