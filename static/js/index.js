function toggleMobileMenu(event){
    event.preventDefault();  // предотвращаем прокрутку страницы в начало
    document.getElementById("menu").classList.toggle("active");
}

document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggleMainTextButton");
    const hiddenText = document.getElementById("hiddenText");

    toggleButton.addEventListener("click", function () {
        if (hiddenText.style.display === "none" || hiddenText.style.display === "") {
            hiddenText.style.display = "inline";
            toggleButton.textContent = "less";
        } else {
            hiddenText.style.display = "none";
            toggleButton.textContent = "more";
        }
    });
});
