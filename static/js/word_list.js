function jumpToPage() {
    const pageInput = document.getElementById('pageInput');
    const page = parseInt(pageInput.value, 10);
    const maxPages = document.querySelector('.pagination-container').dataset.maxPages;
    
    if (isNaN(page) || page < 1 || page > maxPages) {
        alert('请输入有效的页码');
        pageInput.value = '';
        return;
    }
    
    window.location.href = `${window.location.pathname}?page=${page}`;
}

function toggleVisibility(type, button) {
    const isHidden = $(button).hasClass('is-dark');
    $(button).toggleClass('is-dark is-white');
    
    const elements = type === 'word' ? $('.is-word') :
                   type === 'phonetic' ? $('.is-phonetic') :
                   $('.is-interpretation');
    
    elements.css({
        visibility: isHidden ? 'visible' : 'hidden',
        position: 'relative',
        opacity: isHidden ? 0 : 1
    }).animate({
        opacity: isHidden ? 1 : 0
    }, 300);
}

function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    const isDark = body.getAttribute('data-theme') === 'dark';
    
    if (isDark) {
        body.removeAttribute('data-theme');
        themeIcon.classList.remove('fa-sun-o');
        themeIcon.classList.add('fa-moon-o');
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        themeIcon.classList.remove('fa-moon-o');
        themeIcon.classList.add('fa-sun-o');
        localStorage.setItem('theme', 'dark');
    }
    
    document.body.style.transition = 'var(--transition-normal)';
}

document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('themeIcon');
    
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        themeIcon.classList.remove('fa-moon-o');
        themeIcon.classList.add('fa-sun-o');
    }

    const rows = document.querySelectorAll('#myTable tr');
    rows.forEach((row, index) => {
        if (index > 0) {
            const startIndex = document.querySelector('.pagination-container').dataset.startIndex;
            row.cells[0].innerText = index + parseInt(startIndex) - 1;
        }
    });
}); 