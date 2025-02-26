document.addEventListener("DOMContentLoaded", () => {
    const chatLog = document.getElementById("chat-log");
    const inputField = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");

    function addMessage(sender, text) {
        const messageElement = document.createElement("li");
        messageElement.innerHTML = `
            <span class="avatar ${sender}">${sender === "bot" ? "AI" : "User"}</span>
            <div class="message">${text}</div>
        `;
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    const delayResponse = (message) => {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(message);
            }, 1000); // Задержка 1 секунда
        });
    };

    sendButton.addEventListener("click", async () => {
        const messageText = inputField.value.trim();
        if (messageText) {
            addMessage("user", messageText);
            inputField.value = "";

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message: messageText })
                });

                if (!response.ok) {
                    console.error(`Ошибка сервера: ${response.status}`);
                    addMessage("bot", `Ошибка сервера: ${response.status}`);
                    return;
                }

                try {
                    const data = await response.json();
                    const botReply = await delayResponse(data.reply || "Нет ответа от сервера.");
                    addMessage("bot", botReply);
                } catch (jsonError) {
                    console.error("Ошибка при обработке JSON:", jsonError);
                    addMessage("bot", "Ошибка при обработке ответа сервера.");
                }

            } catch (error) {
                console.error("Ошибка при выполнении запроса:", error);
                const errorMessage = await delayResponse("Извините, что-то пошло не так.");
                addMessage("bot", errorMessage);
            }
        }
    });

    inputField.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendButton.click();
        }
    });
});
