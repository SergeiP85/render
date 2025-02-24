const snowflakeCount = 10;
const snowflakeChars = ['❄', '❅', '❆'];

for (let i = 0; i < snowflakeCount; i++) {
    const snowflake = document.createElement('div');
    snowflake.className = 'snowflake';
    snowflake.textContent = snowflakeChars[Math.floor(Math.random() * snowflakeChars.length)];
    snowflake.style.left = Math.random() * 100 + 'vw';
    snowflake.style.fontSize = Math.random() * 20 + 10 + 'px';
    snowflake.style.animationDuration = Math.random() * 5 + 5 + 's';
    snowflake.style.animationDelay = Math.random() * 5 + 's';
    document.body.appendChild(snowflake);
}