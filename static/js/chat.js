class ChatApp {
    constructor() {
        this.currentConversationId = null;
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadConversations();
        this.ensureSession();
    }

    bindEvents() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        // Enter key to send
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Input validation
        messageInput.addEventListener('input', () => {
            sendButton.disabled = messageInput.value.trim() === '';
        });

        // Initially disable send button
        sendButton.disabled = true;
    }

    ensureSession() {
        // Ensure Django session is created
        fetch('/')
            .then(response => {
                console.log('Session ensured');
            })
            .catch(error => {
                console.error('Session error:', error);
            });
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message || this.isLoading) return;

        // Add user message to UI
        this.addMessage(message, true);
        messageInput.value = '';
        document.getElementById('sendButton').disabled = true;

        // Show loading
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/send-message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.currentConversationId
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Add bot response to UI
                this.hideTypingIndicator();
                this.addMessage(data.response, false);
                
                // Update conversation ID if this is a new conversation
                if (!this.currentConversationId) {
                    this.currentConversationId = data.conversation_id;
                    this.loadConversations();
                }
            } else {
                throw new Error(data.error || 'Failed to send message');
            }
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', false);
        } finally {
            this.setLoading(false);
        }
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('messagesContainer');
        
        // Remove existing typing indicator if any
        this.hideTypingIndicator();
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <div class="typing-text">Edu is typing...</div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    addMessage(content, isUser) {
        const messagesContainer = document.getElementById('messagesContainer');
        
        // Remove welcome message if it's the first real message
        const welcomeMessage = messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage && this.currentConversationId === null && isUser) {
            welcomeMessage.remove();
        }

        // Remove typing indicator if it exists
        this.hideTypingIndicator();

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;

        // Format the content to handle markdown-like syntax
        bubbleDiv.innerHTML = this.formatMessage(content);

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString([], { 
            hour: '2-digit', minute: '2-digit' 
        });

        bubbleDiv.appendChild(timeDiv);
        messageDiv.appendChild(bubbleDiv);
        messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    formatMessage(content) {
        // Simple markdown formatting
        let formatted = content
            // Bold text: **text** to <strong>text</strong>
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Bullet points: * item or - item to • item
            .replace(/^[\*\-]\s+(.+)$/gm, '• $1')
            // Numbered lists
            .replace(/^(\d+)\.\s+(.+)$/gm, '$1. $2')
            // Line breaks
            .replace(/\n/g, '<br>');

        return formatted;
    }

   setLoading(loading) {
        this.isLoading = loading;
        const sendButton = document.getElementById('sendButton');
        
        if (loading) {
            sendButton.disabled = true;
        } else {
            // Only re-enable if there's text in the input
            const messageInput = document.getElementById('messageInput');
            sendButton.disabled = messageInput.value.trim() === '';
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/conversations/');
            const data = await response.json();

            if (response.ok) {
                this.renderConversations(data.conversations);
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    renderConversations(conversations) {
        const container = document.getElementById('conversationsList');
        
        if (conversations.length === 0) {
            container.innerHTML = '<div class="no-conversations">No conversations yet</div>';
            return;
        }

        container.innerHTML = conversations.map(conv => `
            <div class="conversation-item ${conv.id === this.currentConversationId ? 'active' : ''}" 
                 onclick="chatApp.loadConversation(${conv.id})">
                <div class="conv-title">${this.escapeHtml(conv.title)}</div>
                <div class="conv-meta">
                    ${new Date(conv.updated_at).toLocaleDateString()} • 
                    ${conv.message_count} messages
                </div>
            </div>
        `).join('');
    }

    async loadConversation(conversationId) {
        try {
            const response = await fetch(`/api/conversation/${conversationId}/`);
            const data = await response.json();

            if (response.ok) {
                this.currentConversationId = conversationId;
                this.renderConversation(data);
                this.loadConversations(); // Refresh list to update active state
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    }

    renderConversation(conversationData) {
        const messagesContainer = document.getElementById('messagesContainer');
        const chatTitle = document.getElementById('chatTitle');

        // Update title
        chatTitle.textContent = conversationData.title;

        // Clear messages
        messagesContainer.innerHTML = '';

        // Add messages
        conversationData.messages.forEach(message => {
            this.addMessage(message.content, message.is_user);
        });
    }

    startNewChat() {
        this.currentConversationId = null;
        
        // Clear messages and show welcome
        const messagesContainer = document.getElementById('messagesContainer');
        const chatTitle = document.getElementById('chatTitle');
        
        chatTitle.textContent = 'Welcome to EduBot';
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <p>Hello! I'm EduBot, your university assistant. I can help you with:</p>
                <ul>
                    <li>Course information and prerequisites</li>
                    <li>Academic deadlines and schedules</li>
                    <li>Campus resources and services</li>
                    <li>General student guidance</li>
                </ul>
                <p>How can I help you today?</p>
            </div>
        `;

        // Refresh conversations list
        this.loadConversations();
    }

    insertSuggestion(text) {
        const messageInput = document.getElementById('messageInput');
        messageInput.value = text;
        messageInput.focus();
        document.getElementById('sendButton').disabled = false;
    }

    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Global functions for HTML onclick attributes
function sendMessage() {
    chatApp.sendMessage();
}

function startNewChat() {
    chatApp.startNewChat();
}

function insertSuggestion(text) {
    chatApp.insertSuggestion(text);
}

// Initialize the chat app when page loads
document.addEventListener('DOMContentLoaded', () => {
    chatApp = new ChatApp();
});