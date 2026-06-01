document.addEventListener('DOMContentLoaded', function() {
    const envelope = document.getElementById('envelope');
    const envelopeHeart = document.getElementById('envelopeHeart');
    
    envelopeHeart.addEventListener('click', function() {
        envelope.classList.toggle('opened');
        createHearts();
    });
    
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                if (!envelope.classList.contains('opened')) {
                    envelope.classList.add('opened');
                    createHearts();
                }
                
                setTimeout(() => {
                    targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 500);
            }
        });
    });
});

function createHearts() {
    const container = document.querySelector('.envelope-container');
    const hearts = ['💕', '💗', '💖', '💝', '💘'];
    
    for (let i = 0; i < 10; i++) {
        const heart = document.createElement('span');
        heart.textContent = hearts[Math.floor(Math.random() * hearts.length)];
        heart.style.cssText = `
            position: fixed;
            font-size: ${20 + Math.random() * 20}px;
            pointer-events: none;
            animation: floatUp 3s ease-out forwards;
            z-index: 100;
        `;
        
        const rect = document.getElementById('envelope').getBoundingClientRect();
        heart.style.left = rect.left + rect.width / 2 + (Math.random() - 0.5) * 100 + 'px';
        heart.style.top = rect.top + 'px';
        
        document.body.appendChild(heart);
        
        setTimeout(() => {
            heart.remove();
        }, 3000);
    }
}

function openArticle(url) {
    window.location.href = url;
}

document.addEventListener('DOMContentLoaded', function() {
    const articles = document.querySelectorAll('.article-card');
    
    articles.forEach(article => {
        article.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        article.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-5px) scale(1)';
        });
    });
});