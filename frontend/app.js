document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotContainer = document.querySelector('.chatbot-container');

    // Verify all elements exist
    if (!imageUpload || !imagePreview || !analyzeBtn || !resultsSection || 
        !chatInput || !sendBtn || !chatMessages || !chatbotToggle || !chatbotContainer) {
        console.error('Critical elements missing from DOM');
        return;
    }

    // ✅ Cleaned-up Image Upload and Preview
    imageUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Check if image file
        if (!file.type.match('image.*')) {
            showAlert('Please select an image file (JPEG, PNG)', 'warning');
            return;
        }

        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showAlert('Image must be less than 5MB', 'warning');
            return;
        }

        const reader = new FileReader();
    
        reader.onloadstart = () => {
            imagePreview.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
        };

        reader.onload = (event) => {
            imagePreview.innerHTML = '';
            const img = document.createElement('img');
            img.src = event.target.result;
            img.alt = 'Uploaded preview';
            img.classList.add('img-preview');
            imagePreview.appendChild(img);
        };

        reader.onerror = () => {
            imagePreview.innerHTML = '<p class="text-danger">Error loading image</p>';
        };

        reader.readAsDataURL(file);
    });

    // Analyze Button Click
    analyzeBtn.addEventListener('click', async function() {
        if (!imageUpload.files[0]) {
            showAlert('Please upload an image first', 'warning');
            return;
        }

        // Set loading state
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Analyzing...';

        try {
            const formData = new FormData();
            formData.append('file', imageUpload.files[0]);

            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            showResults(data);
            showAlert('Analysis complete!', 'success');
        } catch (error) {
            console.error('Analysis error:', error);
            showAlert(error.message || 'Analysis failed. Please try again.', 'danger');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze';
        }
    });

    // Chat Functionality
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendMessage());

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage('user', message);
        chatInput.value = '';
        const typingId = showTypingIndicator();
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to get response');
            }

            removeTypingIndicator(typingId);
            addMessage('bot', data.response);
        } catch (error) {
            console.error('Chat error:', error);
            removeTypingIndicator(typingId);
            addMessage('bot', "Sorry, I'm having trouble responding. Please try again.");
        }
    }

    function showResults(data) {
        resultsSection.classList.remove('d-none');
        resultsSection.innerHTML = `
            <h3 class="card-title">Your Fashion Analysis</h3>
            <div class="row mt-3">
                <div class="col-md-6">
                    <h5>Body Type</h5>
                    <p class="fs-5">${data.bodyType}</p>
                    <h5>Skin Tone</h5>
                    <p class="fs-5">${data.skinTone}</p>
                </div>
                <div class="col-md-6">
                    <h5>Recommended Colors</h5>
                    <div class="d-flex flex-wrap gap-2">
                        ${data.recommendations.colors.map(color => 
                            `<span class="badge rounded-pill bg-primary">${color}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
            <h5 class="mt-3">Outfit Suggestions</h5>
            <ul class="list-group">
                ${data.recommendations.outfits.map(outfit => 
                    `<li class="list-group-item">${outfit}</li>`
                ).join('')}
            </ul>
        `;
    }

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} animate__animated animate__fadeInUp`;
        messageDiv.innerHTML = `<p>${text}</p>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = id;
        typingDiv.className = 'message bot typing d-flex gap-1';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const typing = document.getElementById(id);
        if (typing) typing.remove();
    }

    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        setTimeout(() => alert.remove(), 5000);
    }

    chatbotToggle.addEventListener('click', () => {
        chatbotContainer.style.display = chatbotContainer.style.display === 'none' ? 'block' : 'none';
    });
});
