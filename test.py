import requests
import json

url = "http://localhost:8080/webhook"  # Replit URL

# Step 1: Start the conversation
data = {"user_id": "12345", "message": "hello"}
response = requests.post(url, json=data)
print("Bot's Reply:", response.json()["reply"])

# Step 2: Send your name
data = {"user_id": "12345", "message": "My name is Vedant"}
response = requests.post(url, json=data)
print("Bot's Reply:", response.json()["reply"])

# Step 3: Continue the conversation
data = {"user_id": "12345", "message": "how are you?"}
response = requests.post(url, json=data)
print("Bot's Reply:", response.json()["reply"])
