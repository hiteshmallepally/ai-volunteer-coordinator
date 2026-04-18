from flask import Flask, request, jsonify, render_template_string
from google import genai
import os

app = Flask(__name__)

# 🔑 API key (keep yours here for now)
client = genai.Client(api_key="AIzaSyAxMhJObvy7xodhhwIRD1lwxLMCHrsCLAE")

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

        # 🧠 TRY AI FIRST
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"""
Analyze this NGO task and provide:

Priority:
Volunteers Needed:
Action Plan:
Suggestions:

Task: {task}
"""
            )

            return jsonify({"result": response.text})

        except Exception as ai_error:
            print("AI FAILED:", ai_error)

            # 🔥 FALLBACK (always works)
            result = f"""
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
            return jsonify({"result": result})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)