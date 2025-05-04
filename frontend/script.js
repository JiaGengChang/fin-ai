const sendButton = document.querySelector('.send-button');
const chatInput = document.querySelector('.chat-input');
const chatHistory = document.querySelector('.chat-history');
const sendButtonIcon = sendButton.querySelector('.icon'); 

let isResponding = false;

function switchMode() {
    if (isResponding) {
        sendButtonIcon.textContent = '↑';
        sendButton.disabled = false;
        isResponding = false;
    }
    else {
        sendButtonIcon.textContent = '◼';
        sendButton.disabled = false;
        isResponding = true;
    }
}

async function sendMessage() {
    const message = chatInput.value.trim();
  
    if (message) {
        switchMode();
        // Add user message to chat history
        const userMessageContainer = document.createElement('div');
        userMessageContainer.classList.add('chat-message-container');
        const userMessageElement = document.createElement('div');
        userMessageElement.classList.add('chat-message', 'user');

        // Replace newline characters with <br> for HTML rendering
        userMessageElement.innerHTML = message.replace(/\n/g, '<br>'); 

        userMessageContainer.appendChild(userMessageElement);
        chatHistory.appendChild(userMessageContainer);

        chatHistory.scrollTop = chatHistory.scrollHeight;
        chatInput.value = '';
        resizeInput();
    
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
            botMessageElement.innerHTML = botResponse.replace(/\n/g, '<br>');
            const botMessageContainer = document.createElement('div');
            botMessageContainer.classList.add('chat-message-container');
            botMessageContainer.appendChild(botMessageElement);
            chatHistory.appendChild(botMessageContainer);
    
            chatHistory.scrollTop = chatHistory.scrollHeight;
    
        } catch (error) {
            console.error('Error:', error);
        } finally {
            switchMode();
        }
    }
}

sendButton.addEventListener('click', () => {
    if (isResponding) {
        ;
    }
    else {
        sendMessage();
    }
});

chatInput.addEventListener('keydown', function (event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendButton.click();
  }
});

const resizeInput = () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = `${chatInput.scrollHeight}px`;
};

chatInput.addEventListener('input', resizeInput);
