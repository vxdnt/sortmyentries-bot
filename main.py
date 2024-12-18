from flask import Flask, request, jsonify, render_template
import re
import logging
from pymongo import MongoClient
from threading import Timer

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["ticket_reselling"]
user_collection = db["users"]  # Collection to store user data

# Store user state (basic in-memory)
user_state = {}

# Helper functions for validation
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone):
    return phone.isdigit() and len(phone) in [10, 12]  # Adjust for your region

def clear_user_state(user_id):
    """Clears user state after inactivity or session end."""
    user_state.pop(user_id, None)
    logging.info(f"Cleared state for user_id: {user_id}")

# Save user data to MongoDB
def save_user_data(user_id):
    user_data = user_state.get(user_id, {})
    if user_data:
        # Insert data into MongoDB
        user_collection.insert_one(user_data)
        logging.info(f"User data saved for user_id: {user_id}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_id = data.get("user_id")
    user_message = data.get("message", "").lower()

    if not user_id:
        return jsonify({"reply": "Invalid user ID."}), 400

    if user_id not in user_state:
        user_state[user_id] = {"step": 1}
        user_state[user_id]["step"] = 2  # Step 1: greeting
        logging.info(f"New session started for user_id: {user_id}")

    # Handling each step based on user state
    step = user_state[user_id]["step"]

    if step == 1:  # Greeting
        user_state[user_id]["step"] = 2  # Step 2: options
        Timer(600, clear_user_state, args=[user_id]).start()  # Clear state after 10 minutes
        return jsonify({"reply": "Hi!! Let me help you.", "options": ["Want to Sell", "Want to Buy"]})

    elif step == 2:  # Options
        if "sell" in user_message:
            user_state[user_id]["step"] = 3  # Step 3: ask_event_sell
            return jsonify({"reply": "Great! You want to sell. Tell me which event it is?"})
        elif "buy" in user_message:
            user_state[user_id]["step"] = 4  # Step 4: ask_event_buy
            return jsonify({"reply": "Great! You want to buy. Tell me which event you’re interested in?"})
        else:
            return jsonify({"reply": "Please select an option: Want to Sell or Want to Buy."})

    # Selling Flow
    elif step == 3:  # Ask event for selling
        user_state[user_id]["event"] = user_message
        user_state[user_id]["step"] = 5  # Step 5: ask_category_sell
        return jsonify({"reply": "Got it! What ticket category are you selling, and how many tickets?"})

    elif step == 5:  # Ask category for selling
        user_state[user_id]["category"] = user_message
        user_state[user_id]["step"] = 6  # Step 6: ask_price_sell
        return jsonify({"reply": "At what price do you want to sell one ticket (per category)?"})

    elif step == 6:  # Ask price for selling
        if not user_message.isdigit():
            return jsonify({"reply": "Please provide a valid numeric price."})
        user_state[user_id]["price"] = int(user_message)
        user_state[user_id]["step"] = 7  # Step 7: ask_name_sell
        return jsonify({"reply": "Got it! Now, May I know your name?"})

    elif step == 7:  # Ask name for selling
        user_state[user_id]["name"] = user_message
        user_state[user_id]["step"] = 8  # Step 8: ask_contact_sell
        return jsonify({"reply": "Thanks! Can you share your 10 digit mobile number?"})

    elif step == 8:  # Ask contact for selling
        if not is_valid_phone(user_message):
            return jsonify({"reply": "Please provide a valid phone number."})
        user_state[user_id]["contact"] = user_message
        user_state[user_id]["step"] = 9  # Step 9: ask_email_sell
        return jsonify({"reply": "Got it! Lastly, please provide your email address."})

    elif step == 9:  # Ask email for selling
        if not is_valid_email(user_message):
            return jsonify({"reply": "That doesn’t look like a valid email. Please try again."})
        user_state[user_id]["email"] = user_message
        user_state[user_id]["step"] = 10  # Step 10: end_sell
        save_user_data(user_id)  # Save user data to MongoDB
        return jsonify({"reply": "Thank you! We’ll let you know via email or WhatsApp. Click 'Start New Chat' to begin again.", "options": ["Start New Chat"]})

    # Buying Flow
    elif step == 4:  # Ask event for buying
        user_state[user_id]["event"] = user_message
        user_state[user_id]["step"] = 7  # Step 11: display_prices
        return jsonify({"reply": "We'll check availability for the tickets and notify you. May I know your name?"})

    # Restart Chat
    elif step in [10]:  # End steps
        if "start new chat" in user_message:
            user_state[user_id]["step"] = 2  # Step 2: options (skip greeting)
            return jsonify({"reply": "Hi!! Let me help you.", "options": ["Want to Sell", "Want to Buy"]})

    return jsonify({"reply": "I didn't understand that. Please try again."})

@app.route("/start_new_chat", methods=["POST"])
def start_new_chat():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"reply": "Invalid user ID."}), 400

    # Reset user state, start from options (skip greeting)
    user_state[user_id] = {"step": 2}  # Step 2: options
    return jsonify({"reply": "Hi!! Let me help you.", "options": ["Want to Sell", "Want to Buy"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
