const themeToggle = document.getElementById("themeToggle");
const productForm = document.getElementById("productForm");
const offersEditor = document.getElementById("offersEditor");
const addOfferButton = document.getElementById("addOfferButton");
const formStatus = document.getElementById("formStatus");
const historyInput = document.getElementById("historyInput");
const bulkInput = document.getElementById("bulkInput");
const bulkImportButton = document.getElementById("bulkImportButton");
const bulkStatus = document.getElementById("bulkStatus");
const customProductsList = document.getElementById("customProductsList");

function setTheme(theme) {
  document.body.dataset.theme = theme;
  localStorage.setItem("pricepulse-theme", theme);
  document.querySelector(".toggle-label").textContent = theme === "dark" ? "Light mode" : "Dark mode";
}

function initTheme() {
  setTheme(localStorage.getItem("pricepulse-theme") || "dark");
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function offerRowTemplate(values = {}) {
  const row = document.createElement("div");
  row.className = "offer-row";
  row.innerHTML = `
    <label><span>Retailer</span><input data-field="retailer" type="text" value="${escapeHtml(values.retailer || "")}" required /></label>
    <label><span>Price</span><input data-field="price" type="number" min="1" value="${escapeHtml(values.price || "")}" required /></label>
    <label><span>Stock</span><input data-field="stock" type="text" value="${escapeHtml(values.stock || "In Stock")}" required /></label>
    <label><span>Seller</span><input data-field="seller" type="text" value="${escapeHtml(values.seller || "")}" required /></label>
    <label><span>Product URL</span><input data-field="url" type="url" value="${escapeHtml(values.url || "")}" required /></label>
    <label><span>Accent color</span><input data-field="accent" type="text" value="${escapeHtml(values.accent || "#2874f0")}" required /></label>
    <button type="button" class="mini-button remove-offer">Remove</button>
  `;
  row.querySelector(".remove-offer").addEventListener("click", () => {
    row.remove();
    if (!offersEditor.children.length) {
      offersEditor.appendChild(offerRowTemplate());
    }
  });
  return row;
}

function collectOffers() {
  return Array.from(offersEditor.children).map((row) => {
    const result = {};
    row.querySelectorAll("[data-field]").forEach((input) => {
      result[input.dataset.field] = input.value;
    });
    return result;
  });
}

function parseOptionalHistory() {
  const raw = historyInput.value.trim();
  if (!raw) {
    return null;
  }
  return JSON.parse(raw);
}

async function refreshCustomProducts() {
  const response = await fetch("/api/admin/products");
  const data = await response.json();
  if (!data.products.length) {
    customProductsList.innerHTML = `<p class="muted">No custom products saved yet.</p>`;
    return;
  }
  customProductsList.innerHTML = data.products.map((product) => `
    <article class="custom-product-item">
      <strong>${escapeHtml(product.name)}</strong>
      <span class="muted">${escapeHtml(product.brand)} · ${escapeHtml(product.category)}</span>
      <a class="action-link" href="/?q=${encodeURIComponent(product.name)}">Open in storefront</a>
    </article>
  `).join("");
}

addOfferButton.addEventListener("click", () => {
  offersEditor.appendChild(offerRowTemplate());
});

productForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formStatus.textContent = "Saving...";
  let history = null;
  try {
    history = parseOptionalHistory();
  } catch (error) {
    formStatus.textContent = "History JSON is invalid.";
    return;
  }

  const formData = new FormData(productForm);
  const payload = {
    name: formData.get("name"),
    brand: formData.get("brand"),
    category: formData.get("category"),
    description: formData.get("description"),
    image: formData.get("image"),
    offers: collectOffers(),
  };
  if (history) {
    payload.history = history;
  }

  const response = await fetch("/api/admin/products", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    formStatus.textContent = data.error || "Could not save product.";
    return;
  }

  formStatus.textContent = `Saved ${data.product.name}.`;
  productForm.reset();
  historyInput.value = "";
  offersEditor.innerHTML = "";
  offersEditor.appendChild(offerRowTemplate({
    retailer: "Amazon India",
    stock: "In Stock",
    accent: "#ff9900",
  }));
  refreshCustomProducts();
});

bulkImportButton.addEventListener("click", async () => {
  bulkStatus.textContent = "Importing...";
  let parsed;
  try {
    parsed = JSON.parse(bulkInput.value || "[]");
  } catch (error) {
    bulkStatus.textContent = "Bulk JSON is not valid.";
    return;
  }

  const response = await fetch("/api/admin/import", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(parsed),
  });
  const data = await response.json();
  bulkStatus.textContent = response.ok ? `Imported ${data.count} products.` : (data.error || "Import failed.");
  if (response.ok) {
    refreshCustomProducts();
  }
});

themeToggle.addEventListener("click", () => {
  const nextTheme = document.body.dataset.theme === "dark" ? "light" : "dark";
  setTheme(nextTheme);
});

initTheme();
offersEditor.appendChild(offerRowTemplate({
  retailer: "Amazon India",
  stock: "In Stock",
  accent: "#ff9900",
}));
refreshCustomProducts();
