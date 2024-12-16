// Script básico para o chatbot
document.addEventListener('DOMContentLoaded', function() {
    const chatbotButton = document.createElement('button');
    chatbotButton.textContent = 'ChatBot';
    chatbotButton.style.position = 'fixed';
    chatbotButton.style.bottom = '20px';
    chatbotButton.style.right = '20px';
    chatbotButton.style.backgroundColor = '#790f1d';
    chatbotButton.style.color = 'white';
    chatbotButton.style.border = 'none';
    chatbotButton.style.borderRadius = '5px';
    chatbotButton.style.padding = '10px';
    
    chatbotButton.onclick = function() {
        alert('Bem-vindo ao ChatBot! Como posso ajudar você hoje?');
    };
    
    document.body.appendChild(chatbotButton);
});
