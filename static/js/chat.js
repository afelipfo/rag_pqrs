// Chat System for Infrastructure Assistant

document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const chatMessages = document.getElementById('chatMessages');

    if (chatInput && sendChatBtn && chatMessages) {
        // Event listeners
        sendChatBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Auto-resize textarea as user types
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });

        // Add some example questions
        addExampleQuestions();
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        
        if (!message) {
            NotificationSystem.show('Por favor escriba un mensaje', 'warning');
            return;
        }

        // Disable input while processing
        setInputState(false);

        // Add user message to chat
        addUserMessage(message);

        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';

        try {
            // Send to API
            const response = await Utils.apiRequest('/chat', {
                method: 'POST',
                body: JSON.stringify({
                    mensaje: message,
                    contexto: null
                })
            });

            // Add bot response
            addBotMessage(response.respuesta);

        } catch (error) {
            console.error('Chat error:', error);
            addBotMessage('Lo siento, hubo un error procesando tu consulta. Por favor intenta nuevamente.');
        } finally {
            setInputState(true);
        }
    }

    function addUserMessage(message) {
        const messageHtml = `
            <div class="message user-message">
                <div class="d-flex mb-3 justify-content-end">
                    <div class="flex-grow-1 text-end">
                        <div class="bg-primary text-white p-3 rounded d-inline-block" style="max-width: 80%;">
                            ${Utils.sanitizeHtml(message)}
                        </div>
                        <div class="small text-muted mt-1">
                            ${new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}
                        </div>
                    </div>
                    <div class="ms-2">
                        <i class="fas fa-user text-primary"></i>
                    </div>
                </div>
            </div>
        `;

        chatMessages.insertAdjacentHTML('beforeend', messageHtml);
        scrollToBottom();
    }

    function addBotMessage(message) {
        // Show typing indicator first
        const typingIndicator = addTypingIndicator();

        // Simulate typing delay
        setTimeout(() => {
            // Remove typing indicator
            if (typingIndicator) {
                typingIndicator.remove();
            }

            const messageHtml = `
                <div class="message bot-message">
                    <div class="d-flex mb-3">
                        <div class="me-2">
                            <i class="fas fa-robot text-primary"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="bg-light p-3 rounded" style="max-width: 80%;">
                                ${formatBotMessage(message)}
                            </div>
                            <div class="small text-muted mt-1">
                                ${new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}
                            </div>
                        </div>
                    </div>
                </div>
            `;

            chatMessages.insertAdjacentHTML('beforeend', messageHtml);
            scrollToBottom();
        }, 1000 + Math.random() * 1000); // Random delay between 1-2 seconds
    }

    function addTypingIndicator() {
        const typingHtml = `
            <div class="message bot-message typing-indicator">
                <div class="d-flex mb-3">
                    <div class="me-2">
                        <i class="fas fa-robot text-primary"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="bg-light p-3 rounded">
                            <div class="typing-dots">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        chatMessages.insertAdjacentHTML('beforeend', typingHtml);
        scrollToBottom();

        // Add typing animation CSS if not exists
        if (!document.querySelector('#typing-animation-css')) {
            const style = document.createElement('style');
            style.id = 'typing-animation-css';
            style.textContent = `
                .typing-dots {
                    display: flex;
                    gap: 4px;
                    align-items: center;
                }
                
                .typing-dots span {
                    height: 8px;
                    width: 8px;
                    background-color: #6c757d;
                    border-radius: 50%;
                    display: inline-block;
                    animation: typing 1.4s infinite ease-in-out;
                }
                
                .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
                .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
                
                @keyframes typing {
                    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
                    40% { transform: scale(1); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        return chatMessages.querySelector('.typing-indicator');
    }

    function formatBotMessage(message) {
        // Convert line breaks and format text
        return message
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^(.*)$/, '<p>$1</p>')
            .replace(/<p><\/p>/g, '');
    }

    function setInputState(enabled) {
        chatInput.disabled = !enabled;
        sendChatBtn.disabled = !enabled;
        
        if (enabled) {
            sendChatBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            chatInput.placeholder = 'Escribe tu pregunta sobre infraestructura...';
            chatInput.focus();
        } else {
            sendChatBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            chatInput.placeholder = 'Procesando...';
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addExampleQuestions() {
        // Only add if chat is empty (only has welcome message)
        if (chatMessages.children.length <= 1) {
            const examplesHtml = `
                <div class="message bot-message">
                    <div class="d-flex mb-3">
                        <div class="me-2">
                            <i class="fas fa-lightbulb text-warning"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="bg-light p-3 rounded">
                                <p class="mb-2"><strong>Puedes preguntarme sobre:</strong></p>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-outline-primary btn-sm text-start" onclick="askExample('¿Cómo reportar un hueco en la vía?')">
                                        <i class="fas fa-road me-2"></i>¿Cómo reportar un hueco en la vía?
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm text-start" onclick="askExample('¿Qué hacer si una luminaria está dañada?')">
                                        <i class="fas fa-lightbulb me-2"></i>¿Qué hacer si una luminaria está dañada?
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm text-start" onclick="askExample('¿Cómo solicitar mantenimiento de espacios públicos?')">
                                        <i class="fas fa-tree me-2"></i>¿Cómo solicitar mantenimiento de espacios públicos?
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm text-start" onclick="askExample('Tiempos de respuesta para PQRS')">
                                        <i class="fas fa-clock me-2"></i>Tiempos de respuesta para PQRS
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            chatMessages.insertAdjacentHTML('beforeend', examplesHtml);
        }
    }

    // Global function to handle example questions
    window.askExample = function(question) {
        chatInput.value = question;
        sendMessage();
    };

    // Clear chat function
    window.clearChat = function() {
        chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="d-flex mb-3">
                    <div class="me-2">
                        <i class="fas fa-robot text-primary"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="bg-light p-3 rounded">
                            ¡Hola! Soy tu asistente virtual de la Secretaría de Infraestructura de Medellín. 
                            Puedo ayudarte con consultas sobre vías, alumbrado público, espacios públicos y más. 
                            ¿En qué puedo asistirte hoy?
                        </div>
                    </div>
                </div>
            </div>
        `;
        addExampleQuestions();
        chatInput.focus();
    };

    // Export chat functions for external use
    window.ChatSystem = {
        sendMessage,
        addUserMessage,
        addBotMessage,
        clearChat: window.clearChat
    };
});