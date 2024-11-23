from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Simple user state to remember names
user_state = {}

# HTML template for the chat interface
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot</title>
</head>
<body>
    <h1>Simple Chatbot</h1>
    <div id="chatbox"></div>
    <input type="text" id="userInput" placeholder="Type a message...">
    <button onclick="sendMessage()">Send</button>

    <script>
        function sendMessage() {
            const userMessage = document.getElementById('userInput').value;
            fetch('/webhook', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: '12345', message: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('chatbox').innerHTML += '<p><b>You:</b> ' + userMessage + '</p>';
                document.getElementById('chatbox').innerHTML += '<p><b>Bot:</b> ' + data.reply + '</p>';
                document.getElementById('userInput').value = '';
            });
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(html_template)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_id = data.get("user_id")
    user_message = data.get("message", "").lower()

    if user_id not in user_state:
        user_state[user_id] = {"name": None}

        # Enhanced conversation logic
    if "hello" in user_message:
        response_text = "Hi there! What's your name?"
    elif "my name is" in user_message:
        name = user_message.split("my name is")[1].strip()
        user_state[user_id]["name"] = name
        response_text = f"Nice to meet you, {name}!"
    elif "weather" in user_message:
        response_text = "I can't provide weather updates yet, but I'm learning!"
    elif "joke" in user_message:
        response_text = "Why did the computer go to therapy? It had too many bytes of trauma! 😅"
    elif user_state[user_id]["name"]:
        response_text = f"Hello again, {user_state[user_id]['name']}! How can I assist you today?"
    else:
        response_text = "I'm not sure how to respond to that. Can you tell me your name?"

    return jsonify({"reply": response_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
