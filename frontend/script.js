// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Dynamic Bot Link (if needed to fetch from env later)
const telegramLinks = document.querySelectorAll('a[href*="t.me"]');
const BOT_USERNAME = "CV_EDITER_BOT"; // Updated to your actual bot username

telegramLinks.forEach(link => {
    link.href = `https://t.me/${BOT_USERNAME}`;
});

// Scroll Reveal Animation
window.addEventListener('scroll', () => {
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }
    });
});
