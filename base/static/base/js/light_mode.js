// toggle light mode
document.addEventListener("DOMContentLoaded", function(event){
    const link = document.getElementById("toggleLightDarkMode");
    const currentTheme = localStorage.getItem("theme");

    document.getElementById("toggleMode").innerHTML="Light Mode: OFF";

    if (currentTheme == "light"){
        document.getElementById("toggleMode").innerHTML="Light Mode: ON";
        document.body.classList.add("light-mode");
    }

    link.addEventListener("click", function() {
        document.body.classList.toggle("light-mode");
        let theme = "dark";

        const containLightTheme = document.body.classList.contains("light-mode");
        if (containLightTheme){
            theme = "light";
            document.getElementById("toggleMode").innerHTML="Light Mode: ON";
            localStorage.setItem("theme", theme);
        } else {
            theme = "dark";
            document.getElementById("toggleMode").innerHTML="Light Mode: OFF";
            localStorage.setItem("theme", theme);
        }
    });
})