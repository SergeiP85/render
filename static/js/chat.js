document.addEventListener("DOMContentLoaded", () => {
    const chatLog = document.getElementById("chat-log");
    const inputField = document.getElementById("user-input");  // Ссылка на поле ввода
    const sendButton = document.getElementById("send-button");  // Ссылка на кнопку отправки

    // Функция для добавления сообщения в чат
    function addMessage(sender, text) {
        const messageElement = document.createElement("li");
        messageElement.innerHTML = `
            <span class="avatar ${sender}">${sender === "bot" ? "AI" : "User"}</span>
            <div class="message">${text}</div>
        `;
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight; // Автопрокрутка вниз
    }

    // Обработчик для кнопки "Send"
    sendButton.addEventListener("click", async () => {
        const messageText = inputField.value.trim();
        if (messageText) {
            // Отправка сообщения пользователя в чат
            addMessage("user", messageText);
            inputField.value = "";  // Очистка поля ввода

            // Задержка, прежде чем начать отправку или получение ответа
            const delayResponse = (message) => {
                return new Promise((resolve) => {
                    setTimeout(() => {
                        resolve(message);
                    }, 1000); // Задержка в 1 секунду
                });
            };

            // Отправляем запрос на сервер (например, Flask API)
            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message: messageText })
                });

                const data = await response.json();

                // Добавляем задержку перед отправкой ответа от бота
                const botReply = await delayResponse(data.reply);
                addMessage("bot", botReply);  // Добавление ответа от бота в чат
            } catch (error) {
                console.error("Error:", error);

                // Добавляем задержку перед отображением ошибки
                const errorMessage = await delayResponse("Sorry, something went wrong.");
                addMessage("bot", errorMessage);  // Отображаем ошибку после задержки
            }
        }
    });

    // Обработчик для отправки сообщения по нажатию клавиши Enter
    inputField.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendButton.click();
        }
    });
});
