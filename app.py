from flask import Flask, request, jsonify, render_template_string
from google import genai
import os

app = Flask(__name__)

# 🔐 Get API key safely
api_key = os.getenv("GEMINI_API_KEY")

client = None
if api_key:
    client = genai.Client(api_key=api_key)

# ✅ Inline HTML (safe for Render)
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
            # 🤖 Try AI (correct model)
            if client:
                response = client.models.generate_content(
                    model="gemini-1.5-flash-latest",
                    contents=prompt
                )

                result = response.text if hasattr(response, "text") else str(response)
                return jsonify({"result": result})

            else:
                raise Exception("API key not available")

        except Exception as ai_error:
            print("AI FAILED:", ai_error)

            # 🔥 Smart fallback (dynamic)
            task_lower = task.lower()

            priority = "High" if any(x in task_lower for x in ["flood", "earthquake", "cyclone", "disaster"]) else "Medium"
            volunteers = "20-30" if priority == "High" else "10-15"

            fallback = f"""
Priority: {priority}

Volunteers Needed: {volunteers}

Action Plan:
1. Analyze the situation: {task}
2. Assign volunteers based on required activities
3. Coordinate tasks efficiently
4. Monitor progress

Suggestions:
- Customize actions based on task type
- Improve coordination among volunteers
- Ensure proper resource allocation
"""
            return jsonify({"result": fallback})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
