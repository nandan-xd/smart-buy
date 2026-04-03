const rootElement = document.documentElement;
const themeToggle = document.getElementById("themeToggle");

function applyTheme(theme) {
  rootElement.setAttribute("data-theme", theme);
  localStorage.setItem("student-smart-buy-theme", theme);
}

function initialiseTheme() {
  const saved = localStorage.getItem("student-smart-buy-theme") || "light";
  applyTheme(saved);
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const nextTheme = rootElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
  });
}

initialiseTheme();
