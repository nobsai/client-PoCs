// Initialize speech recognition
let recognition = null;
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
}

// Scroll to the bottom of the chat
function scrollToBottom() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Create typing indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById("chat-messages");
    
    // Remove existing typing indicator if any
    const existingIndicator = document.querySelector('.typing-indicator');
    if (existingIndicator) existingIndicator.remove();
    
    const typingContainer = document.createElement('div');
    typingContainer.className = 'message-box bot-message typing-indicator';
    
    const typingContent = document.createElement('div');
    typingContent.className = 'typing-content';
    
    // Create three dots for typing animation
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        typingContent.appendChild(dot);
    }
    
    typingContainer.appendChild(typingContent);
    chatMessages.appendChild(typingContainer);
    scrollToBottom();
}

// Remove typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.classList.add('fade-out');
        setTimeout(() => typingIndicator.remove(), 300);
    }
}

// Function to display the bot's introduction and options
document.addEventListener("DOMContentLoaded", function () {
    const chatMessages = document.getElementById("chat-messages");

    // Display the bot's introduction
    const introMessage = document.createElement("div");
    introMessage.className = "message-box bot-message";
    introMessage.innerText = "Welcome! How can I assist you today? Please choose an option below:";
    chatMessages.appendChild(introMessage);

    // Add buttons dynamically
    const options = [
        "Bookings",
        "Flight Status",
        "Guest Miles",
        "Meal Options",
        "Destinations",
        "Queries/FAQs"
    ];

    const buttonContainer = document.createElement("div");
    buttonContainer.className = "button-container";
    options.forEach(option => {
        const button = document.createElement("button");
        button.className = "option-button";
        button.innerText = option;
        button.onclick = function () {
            handleOptionClick(option);
        };
        buttonContainer.appendChild(button);
    });

    // Add reset conversation button
    const resetButton = document.createElement("button");
    resetButton.className = "option-button reset-button";
    resetButton.innerText = "Reset Conversation";
    resetButton.onclick = resetConversation;
    buttonContainer.appendChild(resetButton);

    chatMessages.appendChild(buttonContainer);
    scrollToBottom();

    // Initialize voice button functionality
    const voiceButton = document.getElementById('voiceButton');
    if (recognition) {
        recognition.onstart = function() {
            voiceButton.classList.add('listening');
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('user-input').value = transcript;
            voiceButton.classList.remove('listening');
            sendMessage();
        };

        recognition.onerror = function(event) {
            voiceButton.classList.remove('listening');
            showErrorMessage('Speech recognition failed. Please try again.');
        };

        recognition.onend = function() {
            voiceButton.classList.remove('listening');
        };

        voiceButton.addEventListener('click', function() {
            if (voiceButton.classList.contains('listening')) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        voiceButton.disabled = true;
        showErrorMessage('Speech recognition is not supported in this browser.');
    }

    // Load conversation history
    loadConversationHistory();
});

// Function to load conversation history
function loadConversationHistory() {
    fetch('/get_history', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const chatMessages = document.getElementById("chat-messages");
        data.history.forEach(item => {
            const messageBox = document.createElement("div");
            messageBox.className = `message-box ${item.role === 'user' ? 'user-message' : 'bot-message'}`;
            messageBox.innerHTML = item.content;
            chatMessages.appendChild(messageBox);
        });
        scrollToBottom();
    })
    .catch(error => {
        console.error('Error loading history:', error);
    });
}

// Function to reset conversation
function resetConversation() {
    fetch('/reset_history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const chatMessages = document.getElementById("chat-messages");
        chatMessages.innerHTML = '';
        // Re-display intro message and options
        const introMessage = document.createElement("div");
        introMessage.className = "message-box bot-message";
        introMessage.innerText = "Welcome! How can I assist you today? Please choose an option below:";
        chatMessages.appendChild(introMessage);

        const options = [
            "Bookings",
            "Flight Status",
            "Guest Miles",
            "Meal Options",
            "Destinations",
            "Queries/FAQs"
        ];

        const buttonContainer = document.createElement("div");
        buttonContainer.className = "button-container";
        options.forEach(option => {
            const button = document.createElement("button");
            button.className = "option-button";
            button.innerText = option;
            button.onclick = function () {
                handleOptionClick(option);
            };
            buttonContainer.appendChild(button);
        });

        const resetButton = document.createElement("button");
        resetButton.className = "option-button reset-button";
        resetButton.innerText = "Reset Conversation";
        resetButton.onclick = resetConversation;
        buttonContainer.appendChild(resetButton);

        chatMessages.appendChild(buttonContainer);
        scrollToBottom();
    })
    .catch(error => {
        console.error('Error resetting conversation:', error);
        showErrorMessage('Failed to reset conversation. Please try again.');
    });
}

// Function to show error messages
function showErrorMessage(message) {
    const chatMessages = document.getElementById("chat-messages");
    const errorMessage = document.createElement("div");
    errorMessage.className = "message-box error-message";
    errorMessage.innerText = message;
    chatMessages.appendChild(errorMessage);
    scrollToBottom();
}

// Function to handle button click
function handleOptionClick(option) {
    const chatMessages = document.getElementById("chat-messages");

    // Display user's choice
    const userMessage = document.createElement("div");
    userMessage.className = "message-box user-message";
    userMessage.innerText = option;
    chatMessages.appendChild(userMessage);

    // Remove buttons
    const buttonContainer = document.querySelector(".button-container");
    buttonContainer.remove();

    // Show typing indicator
    showTypingIndicator();

    // Fetch response from the server
    fetch("/get_response", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: option })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        const botMessage = document.createElement("div");
        botMessage.className = "message-box bot-message";
        botMessage.innerHTML = data.response;
        chatMessages.appendChild(botMessage);
        scrollToBottom();
        
        // Speak the response
        const textToSpeak = botMessage.textContent;
        speakResponse(textToSpeak);
    })
    .catch(error => {
        hideTypingIndicator();
        console.error("Error:", error);
        showErrorMessage('Failed to get response. Please try again.');
    });
}

// Send message function for manual input
function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    if (message === "") return;

    const chatMessages = document.getElementById("chat-messages");

    // Display user message
    const userMessage = document.createElement("div");
    userMessage.className = "message-box user-message";
    userMessage.innerText = message;
    chatMessages.appendChild(userMessage);

    // Clear input field
    userInput.value = "";

    // Show typing indicator
    showTypingIndicator();

    // Fetch bot response
    fetch("/get_response", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        const botMessage = document.createElement("div");
        botMessage.className = "message-box bot-message";
        botMessage.innerHTML = data.response;
        chatMessages.appendChild(botMessage);
        scrollToBottom();
        
        // Speak the response
        const textToSpeak = botMessage.textContent;
        speakResponse(textToSpeak);
    })
    .catch(error => {
        hideTypingIndicator();
        console.error("Error:", error);
        showErrorMessage('Failed to get response. Please try again.');
    });
}

// Text-to-speech functionality using OpenAI TTS
function speakResponse(text) {
    if (!text) return;

    fetch('/synthesize_speech', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.audio) {
            const audio = new Audio(`data:${data.mimeType};base64,${data.audio}`);
            audio.play();
        }
    })
    .catch(error => {
        console.error('Error synthesizing speech:', error);
        showErrorMessage('Failed to play response audio. Please try again.');
    });
}