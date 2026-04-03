const addPriceRowButton = document.getElementById("addPriceRow");
const priceRows = document.getElementById("priceRows");

if (addPriceRowButton && priceRows) {
  addPriceRowButton.addEventListener("click", () => {
    const wrapper = document.createElement("div");
    wrapper.className = "price-row";
    wrapper.innerHTML = `
      <input type="text" class="form-control smart-input" name="platform[]" placeholder="Platform" required>
      <input type="number" step="0.01" class="form-control smart-input" name="price[]" placeholder="Price" required>
      <input type="url" class="form-control smart-input" name="link[]" placeholder="Affiliate Link" required>
    `;
    priceRows.appendChild(wrapper);
  });
}
