const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");
const quickPicks = document.getElementById("quickPicks");
const emptyState = document.getElementById("emptyState");
const dashboard = document.getElementById("dashboard");
const winnerCard = document.getElementById("winnerCard");
const priceStats = document.getElementById("priceStats");
const productSpotlight = document.getElementById("productSpotlight");
const lineChart = document.getElementById("lineChart");
const donutChart = document.getElementById("donutChart");
const offersBody = document.getElementById("offersBody");
const lastUpdated = document.getElementById("lastUpdated");
const themeToggle = document.getElementById("themeToggle");

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

function formatPrice(value) {
  return currency.format(value || 0);
}

function formatDate(isoText) {
  const value = new Date(isoText);
  return value.toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

function setTheme(theme) {
  document.body.dataset.theme = theme;
  localStorage.setItem("pricepulse-theme", theme);
  document.querySelector(".toggle-label").textContent = theme === "dark" ? "Light mode" : "Dark mode";
}

function initTheme() {
  setTheme(localStorage.getItem("pricepulse-theme") || "dark");
}

function createQuickPick(label) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "chip";
  button.textContent = label;
  button.addEventListener("click", () => {
    searchInput.value = label;
    executeSearch(label);
  });
  return button;
}

async function loadQuickPicks() {
  const response = await fetch("/api/products");
  const data = await response.json();
  quickPicks.innerHTML = "";
  data.products.slice(0, 4).forEach((product) => quickPicks.appendChild(createQuickPick(product.name)));
}

function buildSparkline(points, stroke) {
  const width = 120;
  const height = 32;
  const values = points.map((entry) => entry.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const commands = points.map((entry, index) => {
    const x = (index / (points.length - 1 || 1)) * width;
    const y = height - ((entry.value - min) / range) * (height - 4) - 2;
    return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
  }).join(" ");
  return `<svg class="spark" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none"><path d="${commands}" stroke="${stroke}"></path></svg>`;
}

function getRetailerSeries(history, retailer) {
  return history.map((entry) => ({ date: entry.date, value: entry[retailer] })).filter((entry) => typeof entry.value === "number");
}

function renderWinner(summary) {
  const cheapest = summary.cheapest;
  winnerCard.innerHTML = `
    <p class="caps">Cheapest now</p>
    <div class="winner-grid">
      <div>
        <p class="tiny-label">${cheapest.retailer}</p>
        <div class="kpi">${formatPrice(cheapest.price)}</div>
      </div>
      <div><p class="muted">You save ${formatPrice(summary.spread)} against the next best live offer.</p></div>
      <div class="status-pill">${cheapest.stock}</div>
      <div class="winner-actions">
        <a class="action-link" href="${cheapest.url}" target="_blank" rel="noreferrer">Go to cheapest product</a>
      </div>
    </div>
  `;
}

function renderStats(summary, offers) {
  priceStats.innerHTML = `
    <p class="caps">Price spread</p>
    <div class="kpi">${formatPrice(summary.lowest_price)} - ${formatPrice(summary.highest_price)}</div>
    <p class="muted">Average across ${offers.length} tracked platforms: ${formatPrice(summary.average_price)}</p>
    <div class="line-legend">
      <div class="legend-item"><span class="legend-swatch" style="background: var(--accent);"></span> Cheapest live</div>
      <div class="legend-item"><span class="legend-swatch" style="background: var(--accent-3);"></span> Highest ask</div>
    </div>
  `;
}

function renderSpotlight(product) {
  productSpotlight.innerHTML = `
    <p class="caps">${product.category}</p>
    <div class="product-card">
      <img src="${product.image}" alt="${product.name}" />
      <div>
        <h3>${product.name}</h3>
        <p class="muted" style="margin-top: 8px;">${product.description}</p>
        <p class="tiny-label" style="margin-top: 14px;">Brand: ${product.brand}</p>
        <div class="spotlight-actions">
          <span class="status-pill">Category: ${product.category}</span>
        </div>
      </div>
    </div>
  `;
}

function buildLineChart(history, offers) {
  const width = 760;
  const height = 340;
  const padding = { top: 18, right: 12, bottom: 36, left: 56 };
  const usableWidth = width - padding.left - padding.right;
  const usableHeight = height - padding.top - padding.bottom;
  const series = offers.map((offer) => ({
    retailer: offer.retailer,
    accent: offer.accent,
    values: getRetailerSeries(history, offer.retailer),
  }));
  const allPrices = series.flatMap((entry) => entry.values.map((point) => point.value));
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const range = maxPrice - minPrice || 1;
  const dates = history.map((entry) => entry.date);

  const gridLines = Array.from({ length: 5 }, (_, index) => {
    const y = padding.top + (usableHeight / 4) * index;
    const labelPrice = Math.round(maxPrice - ((maxPrice - minPrice) / 4) * index);
    return `
      <line class="grid-line" x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}"></line>
      <text class="axis-label" x="8" y="${y + 4}">${formatPrice(labelPrice)}</text>
    `;
  }).join("");

  const dateLabels = dates.map((date, index) => {
    const x = padding.left + (usableWidth / (dates.length - 1 || 1)) * index;
    return `<text class="axis-label" x="${x}" y="${height - 8}" text-anchor="middle">${date.slice(5)}</text>`;
  }).join("");

  const defs = series.map((entry, index) => `
    <linearGradient id="area-${index}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${entry.accent}" stop-opacity="0.35"></stop>
      <stop offset="100%" stop-color="${entry.accent}" stop-opacity="0.01"></stop>
    </linearGradient>
  `).join("");

  const lines = series.map((entry, index) => {
    const pathPoints = entry.values.map((point, pointIndex) => {
      const x = padding.left + (usableWidth / (entry.values.length - 1 || 1)) * pointIndex;
      const y = padding.top + (1 - (point.value - minPrice) / range) * usableHeight;
      return { x, y };
    });
    const linePath = pathPoints.map((point, pointIndex) => `${pointIndex === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(" ");
    const areaPath = `${linePath} L ${pathPoints[pathPoints.length - 1].x.toFixed(2)} ${height - padding.bottom} L ${pathPoints[0].x.toFixed(2)} ${height - padding.bottom} Z`;
    return `
      <path class="series-area" d="${areaPath}" fill="url(#area-${index})"></path>
      <path class="series-line" d="${linePath}" stroke="${entry.accent}"></path>
    `;
  }).join("");

  const legend = series.map((entry) => `
    <div class="legend-item">
      <span class="legend-swatch" style="background:${entry.accent};"></span>
      ${entry.retailer}
    </div>
  `).join("");

  lineChart.innerHTML = `
    <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <defs>${defs}</defs>
      ${gridLines}
      ${dateLabels}
      ${lines}
    </svg>
    <div class="line-legend">${legend}</div>
  `;
}

function buildDonutChart(offers, summary) {
  const cheapestPrice = summary.lowest_price;
  const normalized = offers.map((offer) => ({
    ...offer,
    score: Math.max(0, 1 - (offer.price - cheapestPrice) / cheapestPrice),
  }));
  const total = normalized.reduce((sum, entry) => sum + entry.score, 0) || 1;
  const radius = 72;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  const segments = normalized.map((offer) => {
    const portion = offer.score / total;
    const dash = portion * circumference;
    const segment = `
      <circle
        class="donut-segment"
        cx="100"
        cy="100"
        r="${radius}"
        stroke="${offer.accent}"
        stroke-dasharray="${dash} ${circumference - dash}"
        stroke-dashoffset="${-offset}"
      ></circle>
    `;
    offset += dash;
    return segment;
  }).join("");

  const legend = normalized.map((offer) => `
    <div class="legend-item">
      <span class="legend-swatch" style="background:${offer.accent};"></span>
      ${offer.retailer} · ${formatPrice(offer.price)}
    </div>
  `).join("");

  donutChart.innerHTML = `
    <div class="donut-wrap">
      <svg class="donut-svg" viewBox="0 0 200 200">
        <circle class="donut-track" cx="100" cy="100" r="${radius}"></circle>
        ${segments}
      </svg>
      <div class="donut-center">
        <p class="caps">Best live</p>
        <h3>${summary.cheapest.retailer}</h3>
        <p class="muted">${formatPrice(summary.cheapest.price)}</p>
      </div>
    </div>
    <div class="donut-legend">${legend}</div>
  `;
}

function renderOffers(offers, history) {
  offersBody.innerHTML = offers.map((offer) => {
    const series = getRetailerSeries(history, offer.retailer);
    return `
      <tr>
        <td>
          <div class="retailer-cell">
            <span class="accent-dot" style="background:${offer.accent};"></span>
            <strong>${offer.retailer}</strong>
          </div>
        </td>
        <td>${formatPrice(offer.price)}</td>
        <td>${offer.seller}</td>
        <td>${offer.stock}</td>
        <td>${buildSparkline(series, offer.accent)}</td>
        <td><a class="table-link" href="${offer.url}" target="_blank" rel="noreferrer">View product</a></td>
      </tr>
    `;
  }).join("");
}

function showDashboard() {
  emptyState.classList.add("hidden");
  dashboard.classList.remove("hidden");
}

function showEmpty(message) {
  dashboard.classList.add("hidden");
  emptyState.classList.remove("hidden");
  emptyState.innerHTML = `
    <p class="caps">No match found</p>
    <h2>Try a clearer product name.</h2>
    <p>${message}</p>
  `;
}

function renderResult(payload) {
  if (!payload.best_match) {
    showEmpty(`We could not match "${payload.query}" to our current India demo catalogue.`);
    return;
  }

  const { product, offers, history, summary } = payload.best_match;
  renderWinner(summary);
  renderStats(summary, offers);
  renderSpotlight(product);
  buildLineChart(history, offers);
  buildDonutChart(offers, summary);
  renderOffers(offers, history);
  lastUpdated.textContent = `Updated ${formatDate(summary.last_updated)}`;
  showDashboard();
}

async function executeSearch(query) {
  if (!query.trim()) {
    return;
  }
  const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const data = await response.json();
  renderResult(data);
}

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  executeSearch(searchInput.value);
});

themeToggle.addEventListener("click", () => {
  const nextTheme = document.body.dataset.theme === "dark" ? "light" : "dark";
  setTheme(nextTheme);
});

initTheme();
loadQuickPicks();
