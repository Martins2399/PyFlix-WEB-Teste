document.addEventListener('DOMContentLoaded', () => {
    // Rolagem lateral das fileiras de filmes
    document.querySelectorAll('.row-container').forEach(container => {
        const row = container.querySelector('.cards-row');
        const leftBtn = container.querySelector('.scroll-left');
        const rightBtn = container.querySelector('.scroll-right');

        if (leftBtn && rightBtn && row) {
            leftBtn.addEventListener('click', () => {
                row.scrollBy({ left: -600, behavior: 'smooth' });
            });
            rightBtn.addEventListener('click', () => {
                row.scrollBy({ left: 600, behavior: 'smooth' });
            });
        }
    });
});