function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    const chatbox = document.getElementById('chatbox');

    if (userInput) {
        // Display user message
        chatbox.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;

        // Send message to the backend
        fetch('/webhook', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => response.json())
        .then(data => {
            // Display bot reply
            chatbox.innerHTML += `<p><strong>Bot:</strong> ${data.reply}</p>`;
            chatbox.scrollTop = chatbox.scrollHeight;
        });

        document.getElementById('userInput').value = '';  // Clear input field
    }
}
