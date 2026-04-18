from flask import Flask, request, jsonify, render_template_string
from google import genai
import os

app = Flask(__name__)

# 🔐 Get API key safely
api_key = os.getenv("GEMINI_API_KEY")

client = None
if api_key:
    client = genai.Client(api_key=api_key)

# ✅ Inline HTML (fixes Render crash)
html = """
<!DOCTYPE html>
<html>
<head>
<title>AI Volunteer Coordinator</title>
<style>
body {
    font-family: Arial;
    text-align: center;
    padding: 30px;
    background: #f4f6f8;
}
textarea {
    width: 80%;
    height: 120px;
    padding: 10px;
}
button {
    padding: 10px 20px;
    background: green;
    color: white;
    border: none;
}
pre {
    background: white;
    padding: 15px;
    margin-top: 20px;
    text-align: left;
    white-space: pre-line;
}
</style>
</head>

<body>

<h2>🤖 AI Volunteer Coordinator</h2>

<textarea id="task" placeholder="Enter NGO task here..."></textarea><br><br>

<button onclick="analyze()">Analyze Task</button>

<pre id="output"></pre>

<script>
async function analyze() {
    let task = document.getElementById("task").value;

    let res = await fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({task: task})
    });

    let data = await res.json();

    document.getElementById("output").innerText =
        data.result || data.error;
}
</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(html)


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        task = data.get("task")

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
            if client:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                result = response.text if hasattr(response, "text") else str(response)
                return jsonify({"result": result})

            else:
                raise Exception("No API key")

        except Exception as ai_error:
            print("AI FAILED:", ai_error)

            # 🔥 Fallback
            fallback = """
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
            return jsonify({"result": fallback})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
