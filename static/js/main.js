const rootElement = document.documentElement;
const themeToggle = document.getElementById("themeToggle");
const searchInput = document.getElementById("productSearch");
const searchForm = document.getElementById("heroSearchForm");
const productCards = Array.from(document.querySelectorAll(".product-grid-item"));
const filterChips = Array.from(document.querySelectorAll(".filter-chip"));
const filteredEmptyState = document.getElementById("filteredEmptyState");
const baseEmptyState = document.getElementById("emptyState");
let activeCategory = "all";

function applyTheme(theme) {
  rootElement.setAttribute("data-theme", theme);
  localStorage.setItem("student-smart-buy-theme", theme);
  if (themeToggle) {
    themeToggle.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
  }
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

function updateEmptyStates(matchesVisible) {
  if (filteredEmptyState) {
    filteredEmptyState.classList.toggle("d-none", matchesVisible || productCards.length === 0);
  }
  if (baseEmptyState && productCards.length === 0) {
    baseEmptyState.classList.remove("d-none");
  }
}

function filterProducts() {
  if (!productCards.length) {
    return;
  }

  const query = (searchInput?.value || "").trim().toLowerCase();
  let visibleCount = 0;

  productCards.forEach((card) => {
    const name = card.dataset.name || "";
    const category = (card.dataset.category || "").toLowerCase();
    const platforms = card.dataset.platforms || "";
    const matchesQuery = !query || name.includes(query) || platforms.includes(query);
    const matchesCategory = activeCategory === "all" || category === activeCategory;
    const shouldShow = matchesQuery && matchesCategory;

    card.classList.toggle("is-hidden", !shouldShow);
    if (shouldShow) {
      visibleCount += 1;
    }
  });

  updateEmptyStates(visibleCount > 0);
}

if (searchInput) {
  searchInput.addEventListener("input", filterProducts);
}

if (searchForm) {
  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    filterProducts();
  });
}

filterChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    activeCategory = (chip.dataset.category || "All").toLowerCase();
    filterChips.forEach((button) => button.classList.remove("active"));
    chip.classList.add("active");
    filterProducts();
  });
});

initialiseTheme();
filterProducts();
