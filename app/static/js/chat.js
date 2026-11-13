// Enhanced Chat Functionality for Intellica AI

// Global variable to store the submitChatMessage function
let submitChatMessageGlobal;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the chat interface
    initChatContainer();
    
    // Set up the chat form
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatSubmitButton = document.getElementById('chat-submit');
    
    // Function to handle message submission
    submitChatMessageGlobal = function() {
        const message = chatInput.value.trim();
        
        if (message) {
            console.log("Submitting message:", message);
            
            // Add user message to chat
            addMessageToChat('user', message);
            
            // Clear input
            chatInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send message to server
            sendMessageToServer(message);
        }
    };
    
    // Handle form submission
    if (chatForm) {
        // Handle Enter key in the input field
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                submitChatMessageGlobal();
            }
        });
        
        // Handle button click
        if (chatSubmitButton) {
            chatSubmitButton.addEventListener('click', function() {
                submitChatMessageGlobal();
            });
        }
        
        // Add event listener to the form for good measure
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitChatMessageGlobal();
        });
    }
    
    // Set up suggestion buttons after defining the submitChatMessage function
    setupSuggestionButtons();
    
    // Initialize chat container with greeting
    function initChatContainer() {
        const chatContainer = document.getElementById('chat-container');
        
        if (chatContainer && chatContainer.childElementCount === 0) {
            // Add welcome message
            const welcomeMessage = `
                <div class="chat-message chat-message-assistant">
                    <div class="chat-message-content">
                        <p><strong>Intellica AI</strong></p>
                        <p>Hello! I'm your intelligent research assistant. Smarter Research. Streamlined Intelligence. I can help you with:</p>
                        <ul>
                            <li>Finding and managing research papers and patents</li>
                            <li>Generating citations in different formats</li>
                            <li>Summarizing and analyzing research content</li>
                            <li>Discovering connections between research concepts</li>
                        </ul>
                        <p>What research task can I assist you with today?</p>
                    </div>
                </div>
            `;
            
            chatContainer.innerHTML = welcomeMessage;
            
            // Initialize typing indicator (hidden by default)
            const typingIndicator = document.createElement('div');
            typingIndicator.id = 'typing-indicator';
            typingIndicator.className = 'typing-indicator d-none';
            typingIndicator.innerHTML = '<p><em>Intellica is thinking<span></span><span></span><span></span></em></p>';
            chatContainer.appendChild(typingIndicator);
            
            // Scroll to bottom
            scrollToBottom();
        }
    }
    
    // Set up suggestion buttons
    function setupSuggestionButtons() {
        const suggestionButtons = document.querySelectorAll('.suggestion-btn');
        
        suggestionButtons.forEach(button => {
            button.addEventListener('click', function() {
                const suggestion = this.textContent.trim();
                console.log("Suggestion button clicked:", suggestion);
                
                // Fill the input with the suggestion
                const chatInput = document.getElementById('chat-input');
                chatInput.value = suggestion;
                
                // Focus the input
                chatInput.focus();
                
                // Submit the message automatically
                submitChatMessageGlobal();
            });
        });
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.classList.remove('d-none');
            scrollToBottom();
        }
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.classList.add('d-none');
        }
    }
    
    // Add a message to the chat
    function addMessageToChat(sender, message) {
        const chatContainer = document.getElementById('chat-container');
        const messageElement = document.createElement('div');
        
        messageElement.className = `chat-message chat-message-${sender}`;
        
        // Format the message with the sender label
        let formattedMessage = '';
        
        if (sender === 'user') {
            formattedMessage = `
                <div class="chat-message-content">
                    <p><strong>You</strong></p>
                    <p>${message}</p>
                </div>
            `;
        } else {
            // Process markdown-like formatting for assistant messages
            let processedMessage = message
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
                .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Italic
                .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')  // Code blocks
                .replace(/`([^`]+)`/g, '<code>$1</code>')          // Inline code
                .replace(/\n\n/g, '</p><p>')                       // Paragraphs
                .replace(/\n- (.*)/g, '<li>$1</li>')               // List items
                
            // Check if we have list items and wrap them in ul
            if (processedMessage.includes('<li>')) {
                processedMessage = processedMessage.replace(/<li>(.*?)(?=<\/p>|$)/g, '<ul><li>$1</li></ul>');
            }
            
            formattedMessage = `
                <div class="chat-message-content">
                    <p><strong>Intellica AI</strong></p>
                    <p>${processedMessage}</p>
                </div>
            `;
        }
        
        messageElement.innerHTML = formattedMessage;
        
        // Insert before typing indicator
        const typingIndicator = document.getElementById('typing-indicator');
        chatContainer.insertBefore(messageElement, typingIndicator);
        
        // Scroll to bottom
        scrollToBottom();
        
        // Add animation
        messageElement.style.animation = 'fadeIn 0.3s ease-out';
    }
    
    // Send message to server
    function sendMessageToServer(message) {
        console.log("Sending message to server:", message);
        
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
            credentials: 'same-origin'
        })
        .then(response => {
            console.log("Server response status:", response.status);
            if (!response.ok) {
                console.error("Response not OK:", response.status, response.statusText);
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received data from server:", data);
            
            // Hide typing indicator
            hideTypingIndicator();
            
            if (data && data.response) {
                // Add assistant message to chat
                addMessageToChat('assistant', data.response);
            } else {
                console.error("Invalid response data:", data);
                addMessageToChat('assistant', 'I received an invalid response. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            
            // Hide typing indicator
            hideTypingIndicator();
            
            // Add error message to chat
            addMessageToChat('assistant', 'Sorry, I encountered an error while processing your request. Please try again later.');
        });
    }
    
    // Scroll chat container to bottom
    function scrollToBottom() {
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
});