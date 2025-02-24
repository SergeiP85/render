document.addEventListener("DOMContentLoaded", function () { 
    const frontendSkillsList = document.getElementById("frontend-skills-list");
    const commSkillsList = document.getElementById("comm-skills-list");
    const toggleCommSkillsButton = document.getElementById("toggleCommSkillsButton");

    // Фронтенд навыки (всегда отображаются)
    const frontendSkills = [
        "HTML", "CSS", "JavaScript", "Slack", "Python", "Flask", "SQL", "CMS", "Bootstrap", "Data bases", "VS Code", "Figma", "Prototyping", "React", "Git", "Next.js", "Chatbots", "AI"
    ];

    // Навыки корпоративных коммуникаций (часть скрывается на маленьких экранах)
    const commSkills = [
        "Internal Comms", "Intranet", "Events", "Newsletters", "CSR", "Culture", "DEI",
        "HR Brand", "Communities", "Content Administration", "Media Relations",
        "Employee Engagement", "Cross-functional Collaboration", "Administrative Management"
    ];

    let hiddenSkillsElements = []; // Массив для скрытых элементов

    function renderSkills() {
        const screenWidth = window.innerWidth;
        
        // Очистка списков перед рендером
        frontendSkillsList.innerHTML = "";
        commSkillsList.innerHTML = "";

        // Добавляем все фронтенд-навыки (они всегда видны)
        frontendSkills.forEach(skill => {
            const listItem = document.createElement("li");
            listItem.textContent = skill;
            frontendSkillsList.appendChild(listItem);
        });

        // Отображаем первые 7 навыков для Corporate Communications
        commSkills.slice(0, 7).forEach(skill => {
            const listItem = document.createElement("li");
            listItem.textContent = skill;
            commSkillsList.appendChild(listItem);
        });

        hiddenSkillsElements = []; // Очищаем массив перед добавлением новых скрытых элементов

        // Если экран маленький, скрываем часть навыков Corporate Communications
        if (screenWidth < 1024) {
            commSkills.slice(7).forEach(skill => {
                const listItem = document.createElement("li");
                listItem.textContent = skill;
                listItem.classList.add("hidden-skill");
                listItem.style.display = "none"; // Изначально скрываем
                commSkillsList.appendChild(listItem);
                hiddenSkillsElements.push(listItem);
            });

            // Показываем кнопку "more", если есть скрытые навыки
            toggleCommSkillsButton.style.display = hiddenSkillsElements.length > 0 ? "inline-block" : "none";
        } else {
            // Если экран большой, отображаем все навыки
            commSkills.slice(7).forEach(skill => {
                const listItem = document.createElement("li");
                listItem.textContent = skill;
                commSkillsList.appendChild(listItem);
            });

            // Скрываем кнопку "more"
            toggleCommSkillsButton.style.display = "none";
        }
    }

    // Обработчик кнопки "more/less" для скрытых навыков Corporate Communications
    toggleCommSkillsButton.addEventListener("click", function () {
        if (hiddenSkillsElements.length > 0) {
            if (hiddenSkillsElements[0].style.display === "none") {
                hiddenSkillsElements.forEach(skill => skill.style.display = "inline-block");
                toggleCommSkillsButton.textContent = "less";
            } else {
                hiddenSkillsElements.forEach(skill => skill.style.display = "none");
                toggleCommSkillsButton.textContent = "more";
            }
        }
    });

    // Первоначальный рендер
    renderSkills();

    // Перерисовка при изменении размера экрана
    window.addEventListener("resize", renderSkills);
});
