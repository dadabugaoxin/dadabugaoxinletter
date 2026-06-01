document.addEventListener('DOMContentLoaded', function() {
    const categories = document.querySelectorAll('.category');
    const articles = document.querySelectorAll('.article-card');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');

    categories.forEach(category => {
        category.addEventListener('click', function() {
            categories.forEach(cat => cat.classList.remove('active'));
            this.classList.add('active');
            
            const selectedCategory = this.dataset.category;
            
            articles.forEach(article => {
                if (selectedCategory === 'all') {
                    article.style.display = 'block';
                } else {
                    if (article.dataset.category === selectedCategory) {
                        article.style.display = 'block';
                    } else {
                        article.style.display = 'none';
                    }
                }
            });
        });
    });

    function searchArticles() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        
        articles.forEach(article => {
            const title = article.querySelector('.article-title').textContent.toLowerCase();
            const summary = article.querySelector('.article-summary').textContent.toLowerCase();
            
            if (title.includes(searchTerm) || summary.includes(searchTerm)) {
                article.style.display = 'block';
            } else {
                article.style.display = 'none';
            }
        });
        
        categories.forEach(cat => cat.classList.remove('active'));
    }

    searchBtn.addEventListener('click', searchArticles);
    
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchArticles();
        }
    });
});

function openArticle(url) {
    window.location.href = url;
}