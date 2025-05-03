const sendButton = document.querySelector('.send-button');
const chatInput = document.querySelector('.chat-input');
const chatHistory = document.querySelector('.chat-history');

async function sendMessage() {
    const message = chatInput.value.trim();
  
    if (message) {
        // Add user message to chat history
        const userMessageElement = document.createElement('div');
        userMessageElement.classList.add('chat-message', 'user');

        // Replace newline characters with <br> for HTML rendering
        userMessageElement.innerHTML = message.replace(/\n/g, '<br>'); 

        chatHistory.appendChild(userMessageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        chatInput.value = '';
    
        // Send user message to backend
        try {
            const response = await fetch('http://localhost:3000/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),  
            });
    
            if (!response.ok) throw new Error('Failed to send message');
    
            // Parse JSON response from backend
            const data = await response.json();
            const botResponse = data.response;
    
            // Add bot's response to chat history
            const botMessageElement = document.createElement('div');
            botMessageElement.classList.add('chat-message', 'assistant');
            botMessageElement.textContent = botResponse;
            chatHistory.appendChild(botMessageElement);
    
            chatHistory.scrollTop = chatHistory.scrollHeight;
    
        } catch (error) {
            console.error('Error:', error);
        }
    }
}

sendButton.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', function (event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});