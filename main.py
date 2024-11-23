from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Store user state (basic in-memory)
user_state = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_id = data.get("user_id")  # Unique ID for the user
    user_message = data.get("message", "").lower()

    # Initialize user memory if it's their first message
    if user_id not in user_state:
        user_state[user_id] = {"name": None}

    # Logic for user memory
    if "hello" in user_message:
        user_state[user_id]["name"] = "User"  # Set default name
        response_text = "Hi there! What's your name?"
    elif "my name is" in user_message:
        name = user_message.split("my name is")[1].strip()
        user_state[user_id]["name"] = name
        response_text = f"Nice to meet you, {name}!"
    elif user_state[user_id]["name"]:
        response_text = f"Hello again, {user_state[user_id]['name']}!"
    else:
        response_text = "I'm not sure how to respond to that. Can you tell me your name?"

    return jsonify({"reply": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
