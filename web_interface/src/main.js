document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatHistory = document.getElementById('chat-history');
    const sessionInfoDisplay = document.getElementById('session-info-display');
    const currentModeDisplay = document.getElementById('current-mode');

    const API_BASE_URL = 'http://127.0.0.1:8000'; // FastAPI backend URL

    // Function to fetch and display initial session info
    async function fetchSessionInfo() {
        try {
            const response = await fetch(`${API_BASE_URL}/session_info`);
            const data = await response.json();
            sessionInfoDisplay.textContent = JSON.stringify(data.session_info, null, 2);
        } catch (error) {
            console.error('Error fetching session info:', error);
            sessionInfoDisplay.textContent = 'Could not retrieve session information.';
        }
    }

    // Function to fetch and display conversation history
    async function fetchConversationHistory() {
        try {
            const response = await fetch(`${API_BASE_URL}/conversation_history`);
            const data = await response.json();
            chatHistory.innerHTML = ''; // Clear existing history
            data.history.forEach(msg => {
                appendMessage(msg.role, msg.content);
            });
            chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to bottom
        } catch (error) {
            console.error('Error fetching conversation history:', error);
        }
    }

    // Function to fetch and display current mode
    async function fetchCurrentMode() {
        try {
            const response = await fetch(`${API_BASE_URL}/current_mode`);
            const data = await response.json();
            currentModeDisplay.textContent = data.mode;
        } catch (error) {
            console.error('Error fetching current mode:', error);
        }
    }

    // Function to append messages to chat history
    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to bottom
    }

    // Function to send message to backend
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        appendMessage('You', message);
        userInput.value = ''; // Clear input field

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_input: message }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Something went wrong');
            }

            const data = await response.json();
            appendMessage('AI', data.response);
            fetchCurrentMode(); // Update mode after each response
        } catch (error) {
            console.error('Error sending message:', error);
            appendMessage('Error', `Failed to get response: ${error.message}`);
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Initial fetches
    fetchSessionInfo();
    fetchConversationHistory();
    fetchCurrentMode();
});
