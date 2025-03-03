const petalCount = 10; // Измените количество лепестков, если нужно
const petalChars = ['❀']; // Символ лепестка сакуры

for (let i = 0; i < petalCount; i++) {
    const petal = document.createElement('div');
    petal.className = 'petal'; // Меняем класс на 'petal'
    petal.textContent = petalChars[Math.floor(Math.random() * petalChars.length)];
    petal.style.left = Math.random() * 100 + 'vw'; // случайное положение по горизонтали
    petal.style.fontSize = Math.random() * 20 + 10 + 'px'; // случайный размер
    petal.style.animationDuration = Math.random() * 5 + 5 + 's'; // случайная продолжительность анимации
    petal.style.animationDelay = Math.random() * 5 + 's'; // случайная задержка анимации
    document.body.appendChild(petal);
}