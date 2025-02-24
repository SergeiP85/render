const form = document.querySelector("[data-search-form]");
const input = document.querySelector("[data-search-input]");
const userInfoContainer = document.querySelector("[data-user-info-container]");
const reposContainer = document.querySelector("[data-repos-container]");

const API_GITHUB = "https://api.github.com/users";

async function fetchGitHubUser(username) {
    userInfoContainer.innerHTML = `<p>Loading...</p>`;
    reposContainer.innerHTML = "";
    
    try {
        const userResponse = await fetch(`${API_GITHUB}/${username}`);
        if (!userResponse.ok) throw new Error("User not found");

        const userData = await userResponse.json();

        userInfoContainer.innerHTML = `
            <div>
                <img src="${userData.avatar_url}" alt="${userData.login}"/>
                <h3>${userData.name || userData.login}</h3>
                <p>${userData.bio || "No Bio Available"}</p>
            </div>
        `;

        const reposResponse = await fetch(userData.repos_url);
        if (!reposResponse.ok) throw new Error("Repos not found");

        const repos = await reposResponse.json();

        if (repos.length) {
            reposContainer.innerHTML = `<h3>Repositories:</h3>`;

            reposContainer.innerHTML += `
            <table class="repo-table">
                <tr>
                    <th>Name</th>
                    <th>⭐ Stars</th>
                    <th>💻 Language</th>
                    <th>📅 Updated</th>
                </tr>
                ${repos.map(repo => `
                    <tr>
                        <td><a href="${repo.html_url}" target="_blank">${repo.name}</a></td>
                        <td>${repo.stargazers_count}</td>
                        <td>${repo.language || "Unknown"}</td>
                        <td>${new Date(repo.updated_at).toLocaleDateString()}</td>
                    </tr>
                `).join("")}
            </table>
        `;
        

        } else {
            reposContainer.innerHTML = `<p>No repositories found</p>`;
        }
       
    } catch (error) {
        userInfoContainer.innerHTML = `<p>${error.message}</p>`;
    }
}

// 📌 Загружаем пользователя "SergeiP85" при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
    fetchGitHubUser("SergeiP85");
});

form.addEventListener("submit", async (e) => {  
    e.preventDefault();

    const username = input.value.trim();
    if (!username) {
        alert("Please enter a GitHub username.");
        return;
    }

    fetchGitHubUser(username);
});
