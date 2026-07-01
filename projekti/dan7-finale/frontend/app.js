document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatBox = document.getElementById('chatBox');
    const typingIndicator = document.getElementById('typingIndicator');
    const sendBtn = document.getElementById('sendBtn');

    // URL do našeg Chat API-ja
    const API_URL = 'http://127.0.0.1:8074/api/chat';

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'system-message');

        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        avatar.textContent = sender === 'user' ? 'Vi' : 'AI';

        const bubble = document.createElement('div');
        bubble.classList.add('bubble');

        // Prikaz novih redova korektno
        bubble.innerHTML = text.replace(/\n/g, '<br>');

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        chatBox.appendChild(messageDiv);

        // Scroll do dna
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage(message) {
        // Prikazi korisnikovu poruku
        addMessage(message, 'user');

        // Prikazi indikator kucanja
        typingIndicator.classList.remove('hidden');
        chatBox.scrollTop = chatBox.scrollHeight;

        // Onemoguci unos dok cekamo
        userInput.disabled = true;
        sendBtn.disabled = true;

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ poruka: message, temperature: 0.5 })
            });

            if (!response.ok) {
                throw new Error('Mreža je odgovorila greškom');
            }

            const data = await response.json();

            // Sakrij indikator i prikazi odgovor
            typingIndicator.classList.add('hidden');
            addMessage(data.odgovor, 'system');

        } catch (error) {
            console.error('Greška:', error);
            typingIndicator.classList.add('hidden');
            addMessage('Došlo je do greške prilikom komunikacije sa serverom. Provjerite da li je Chat API pokrenut.', 'system');
        } finally {
            // Omoguci unos
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (text) {
            userInput.value = '';
            sendMessage(text);
        }
    });
});
