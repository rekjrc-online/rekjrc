document.addEventListener('DOMContentLoaded', () => {
    let page = 2;
    let loading = false;
    let hasMore = true;
    const feed = document.getElementById('feed');
    const loadingIndicator = document.getElementById('loading');
    const endMessage = document.getElementById('end-message');
    if (!feed) console.error('Feed container not found!');
    if (!loadingIndicator) console.error('Loading indicator not found!');
    if (!endMessage) console.error('End message not found!');
    // Intersection Observer
    const observer = new IntersectionObserver(entries => {
        const entry = entries[0];
        if (entry.isIntersecting && !loading && hasMore) {
            loading = true;
            loadingIndicator.style.display = 'block';
            setTimeout(() => {
                fetch(`?page=${page}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(response => response.text())
                    .then(html => {
                        if (html.trim() === '') {
                            hasMore = false;
                            endMessage.style.display = 'block';
                        } else {
                            feed.insertAdjacentHTML('beforeend', html);
                            page += 1;
                        }
                    })
                    .catch(err => console.error('Error fetching posts:', err))
                    .finally(() => {
                        loading = false;
                        loadingIndicator.style.display = hasMore ? 'block' : 'none';
                    });
            }, 2000);  // <-- 2 seconds
        }
    }, {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    });
    observer.observe(loadingIndicator);
});