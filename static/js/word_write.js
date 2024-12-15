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

document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
    }
});

var clickCount = 0;

function showPronunciation() {
    clickCount++;

    var pronunciationElement = document.getElementById("pronunciation");
    var wordElement = document.getElementById("word");

    if (clickCount === 1) {
        // 第一次点击，显示音标
        pronunciationElement.style.visibility = 'visible';
        wordElement.style.visibility = 'hidden';
    } else if (clickCount === 2) {
        // 第二次点击，显示单词
        pronunciationElement.style.visibility = 'hidden';
        wordElement.style.visibility = 'visible';
        clickCount = -1; // 重置点击计数
    }else if(clickCount===0){
        pronunciationElement.style.visibility = 'hidden';
        wordElement.style.visibility = 'hidden';
    }
}



