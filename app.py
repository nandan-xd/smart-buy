from __future__ import annotations

import copy
import json
from functools import wraps
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "products.json"

SAMPLE_PRODUCTS = [
    {
        "id": 1,
        "name": "HP 15s Ryzen 5 Laptop",
        "category": "Tech",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80",
        "rating": 4.3,
        "prices": [
            {"platform": "Amazon", "price": 52990, "link": "https://www.amazon.in/dp/B0CEXAMPLE1"},
            {"platform": "Flipkart", "price": 51990, "link": "https://www.flipkart.com/hp-15s-ryzen-5/p/itmexample1"},
            {"platform": "Reliance Digital", "price": 53990, "link": "https://www.reliancedigital.in/hp-15s-ryzen-5/p/491902001"},
        ],
        "history": [
            {"date": "2026-03-03", "price": 55990},
            {"date": "2026-03-08", "price": 54990},
            {"date": "2026-03-13", "price": 54490},
            {"date": "2026-03-18", "price": 53990},
            {"date": "2026-03-23", "price": 52990},
            {"date": "2026-03-30", "price": 51990},
        ],
    },
    {
        "id": 2,
        "name": "Noise Cancelling Study Headphones",
        "category": "Tech",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
        "rating": 4.1,
        "prices": [
            {"platform": "Amazon", "price": 5999, "link": "https://www.amazon.in/dp/B0CEXAMPLE2"},
            {"platform": "Flipkart", "price": 5799, "link": "https://www.flipkart.com/noise-cancelling-study-headphones/p/itmexample2"},
            {"platform": "Croma", "price": 6249, "link": "https://www.croma.com/noise-cancelling-study-headphones/p/270451"},
        ],
        "history": [
            {"date": "2026-03-03", "price": 6799},
            {"date": "2026-03-08", "price": 6599},
            {"date": "2026-03-13", "price": 6399},
            {"date": "2026-03-18", "price": 6199},
            {"date": "2026-03-23", "price": 5999},
            {"date": "2026-03-30", "price": 5799},
        ],
    },
    {
        "id": 3,
        "name": "Scientific Calculator FX-991ES Plus",
        "category": "Tech",
        "image_url": "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=900&q=80",
        "rating": 4.8,
        "prices": [
            {"platform": "Amazon", "price": 1199, "link": "https://www.amazon.in/dp/B0CEXAMPLE3"},
            {"platform": "Flipkart", "price": 1149, "link": "https://www.flipkart.com/casio-fx-991es-plus/p/itmexample3"},
            {"platform": "Moglix", "price": 1235, "link": "https://www.moglix.com/casio-fx-991es-plus/mp/msnexample3"},
        ],
        "history": [
            {"date": "2026-03-03", "price": 1299},
            {"date": "2026-03-08", "price": 1279},
            {"date": "2026-03-13", "price": 1249},
            {"date": "2026-03-18", "price": 1219},
            {"date": "2026-03-23", "price": 1189},
            {"date": "2026-03-30", "price": 1149},
        ],
    },
    {
        "id": 4,
        "name": "Ergonomic Study Chair",
        "category": "Fashion",
        "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80",
        "rating": 4.0,
        "prices": [
            {"platform": "Amazon", "price": 7499, "link": "https://www.amazon.in/dp/B0CEXAMPLE4"},
            {"platform": "Flipkart", "price": 7699, "link": "https://www.flipkart.com/ergonomic-study-chair/p/itmexample4"},
            {"platform": "Pepperfry", "price": 7899, "link": "https://www.pepperfry.com/ergonomic-study-chair-1893201.html"},
        ],
        "history": [
            {"date": "2026-03-03", "price": 7099},
            {"date": "2026-03-08", "price": 7249},
            {"date": "2026-03-13", "price": 7399},
            {"date": "2026-03-18", "price": 7499},
            {"date": "2026-03-23", "price": 7599},
            {"date": "2026-03-30", "price": 7499},
        ],
    },
    {
        "id": 5,
        "name": "Minimal Skincare Repair Serum",
        "category": "Skincare",
        "image_url": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=900&q=80",
        "rating": 4.2,
        "prices": [
            {"platform": "Amazon", "price": 549, "link": "https://www.amazon.in/dp/B0CEXAMPLE5"},
            {"platform": "Nykaa", "price": 525, "link": "https://www.nykaa.com/minimal-serum/p/example5"},
            {"platform": "Flipkart", "price": 579, "link": "https://www.flipkart.com/minimal-serum/p/itmexample5"},
        ],
        "history": [
            {"date": "2026-03-03", "price": 619},
            {"date": "2026-03-08", "price": 599},
            {"date": "2026-03-13", "price": 589},
            {"date": "2026-03-18", "price": 569},
            {"date": "2026-03-23", "price": 549},
            {"date": "2026-03-30", "price": 525},
        ],
    },
    {
        "id": 6,
        "name": "Campus Everyday Sneakers",
        "category": "Fashion",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
        "rating": 4.1,
        "prices": [
            {"platform": "Amazon", "price": 1499, "link": "https://www.amazon.in/dp/B0CEXAMPLE6"},
            {"platform": "Myntra", "price": 1399, "link": "https://www.myntra.com/shoes/campus/example6"},
            {"platform": "Flipkart", "price": 1599, "link": "https://www.flipkart.com/campus-sneakers/p/itmexample6"},
        ],
        "history": [
            {"date": "2026-03-03", "price": 1699},
            {"date": "2026-03-08", "price": 1649},
            {"date": "2026-03-13", "price": 1599},
            {"date": "2026-03-18", "price": 1549},
            {"date": "2026-03-23", "price": 1499},
            {"date": "2026-03-30", "price": 1399},
        ],
    },
]


def clamp(value: float, minimum: float = 0, maximum: float = 10) -> float:
    return max(minimum, min(maximum, value))


def create_app(database_path: str | None = None) -> Flask:
    app = Flask(__name__)
    storage_path = database_path or str(DATA_PATH)
    use_memory_store = str(storage_path).startswith("file:")
    app.config.update(
        SECRET_KEY="student-smart-buy-secret",
        ADMIN_USERNAME="admin",
        ADMIN_PASSWORD="smartbuy123",
        DATABASE=storage_path,
        USE_MEMORY_STORE=use_memory_store,
    )
    app.extensions["catalog_data"] = []

    def default_products() -> list[dict]:
        return copy.deepcopy(SAMPLE_PRODUCTS)

    def normalize_product(product: dict, product_id: int | None = None) -> dict:
        normalized = {
            "id": int(product_id if product_id is not None else product.get("id", 0) or 0),
            "name": str(product.get("name", "")).strip(),
            "category": str(product.get("category", "Tech")).strip() or "Tech",
            "image_url": str(product.get("image_url", "")).strip(),
            "rating": round(float(product.get("rating", 0)), 1),
            "prices": [],
            "history": [],
        }

        for price in product.get("prices", []):
            platform = str(price.get("platform", "")).strip()
            if not platform:
                continue
            normalized["prices"].append(
                {
                    "platform": platform,
                    "price": float(price.get("price", 0)),
                    "link": str(price.get("link", "#")).strip() or "#",
                }
            )

        for entry in product.get("history", []):
            if isinstance(entry, dict):
                date_text = str(entry.get("date", "")).strip()
                price_value = float(entry.get("price", 0))
            else:
                date_text = str(entry[0]).strip()
                price_value = float(entry[1])
            if date_text:
                normalized["history"].append({"date": date_text, "price": price_value})

        normalized["prices"].sort(key=lambda item: item["price"])
        normalized["history"].sort(key=lambda item: item["date"])
        return normalized

    def write_catalog(products: list[dict]) -> None:
        normalized = [normalize_product(product, product.get("id")) for product in products]
        if app.config["USE_MEMORY_STORE"]:
            app.extensions["catalog_data"] = copy.deepcopy(normalized)
            return

        catalog_path = Path(app.config["DATABASE"])
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        with catalog_path.open("w", encoding="utf-8") as handle:
            json.dump(normalized, handle, indent=2)

    def read_catalog() -> list[dict]:
        if app.config["USE_MEMORY_STORE"]:
            if not app.extensions["catalog_data"]:
                app.extensions["catalog_data"] = default_products()
            return copy.deepcopy(app.extensions["catalog_data"])

        catalog_path = Path(app.config["DATABASE"])
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        if not catalog_path.exists():
            write_catalog(default_products())
        with catalog_path.open("r", encoding="utf-8") as handle:
            raw_catalog = json.load(handle)
        if not raw_catalog:
            raw_catalog = default_products()
            write_catalog(raw_catalog)
        return [normalize_product(item) for item in raw_catalog]

    def next_product_id(products: list[dict]) -> int:
        return max((int(product["id"]) for product in products), default=0) + 1

    def extract_prices_from_form(form) -> list[dict]:
        platforms = form.getlist("platform[]")
        prices = form.getlist("price[]")
        links = form.getlist("link[]")
        items = []
        for platform, price, link in zip(platforms, prices, links):
            if not platform.strip():
                continue
            items.append({"platform": platform.strip(), "price": float(price), "link": link.strip() or "#"})
        return items

    def estimate_ai_rating(name: str, prices: list[dict]) -> float:
        normalized_name = name.lower()
        lowest_price = min(price["price"] for price in prices) if prices else 0
        spread_ratio = 0
        if prices and lowest_price:
            spread_ratio = (max(price["price"] for price in prices) - lowest_price) / lowest_price

        rating = 3.6
        keywords = {
            "laptop": 0.45,
            "calculator": 0.7,
            "chair": 0.2,
            "headphones": 0.35,
            "study": 0.18,
            "backpack": 0.3,
            "tablet": 0.28,
            "desk": 0.22,
        }
        for keyword, bonus in keywords.items():
            if keyword in normalized_name:
                rating += bonus

        if lowest_price and lowest_price < 2000:
            rating += 0.35
        elif lowest_price < 10000:
            rating += 0.18
        elif lowest_price > 60000:
            rating -= 0.2

        if "skincare" in normalized_name or "serum" in normalized_name:
            rating += 0.2
        if "fashion" in normalized_name or "sneakers" in normalized_name:
            rating += 0.15
        rating += min(spread_ratio * 3.5, 0.45)
        return round(clamp(rating, 2.8, 4.9), 1)

    def generate_history_from_prices(prices: list[dict], rating: float) -> list[dict]:
        if not prices:
            return []
        lowest_price = min(price["price"] for price in prices)
        highest_price = max(price["price"] for price in prices)
        spread = max(highest_price - lowest_price, max(1, lowest_price * 0.06))
        rating_modifier = max(0.92, 1.08 - (rating / 25))
        anchors = [1.16, 1.11, 1.08, 1.05, 1.02, 1.0]
        dates = ["2026-03-03", "2026-03-08", "2026-03-13", "2026-03-18", "2026-03-23", "2026-03-30"]
        history = []
        for date_text, anchor in zip(dates, anchors):
            synthetic_price = round((lowest_price + spread * 0.35) * anchor * rating_modifier, 2)
            history.append({"date": date_text, "price": synthetic_price})
        history[-1]["price"] = round(lowest_price, 2)
        return history

    def parse_bulk_import(raw_text: str) -> list[dict]:
        payload = json.loads(raw_text)
        if not isinstance(payload, list):
            raise ValueError("Import data must be a JSON array.")

        normalized_products = []
        for item in payload:
            if not isinstance(item, dict):
                raise ValueError("Each imported product must be a JSON object.")
            name = str(item.get("name", "")).strip()
            category = str(item.get("category", "Tech")).strip() or "Tech"
            image_url = str(item.get("image_url") or item.get("image") or "").strip()
            prices = item.get("prices", [])
            if not name or not image_url or not prices:
                raise ValueError("Each imported product needs name, image_url, and prices.")

            normalized_prices = []
            for price_item in prices:
                normalized_prices.append(
                    {
                        "platform": str(price_item.get("platform", "")).strip(),
                        "price": float(price_item.get("price", 0)),
                        "link": str(price_item.get("link", "#")).strip() or "#",
                    }
                )
            rating = estimate_ai_rating(name, normalized_prices)
            normalized_products.append(
                {
                    "name": name,
                    "category": category,
                    "image_url": image_url,
                    "rating": rating,
                    "prices": normalized_prices,
                    "history": generate_history_from_prices(normalized_prices, rating),
                }
            )
        return normalized_products

    def save_product(payload: dict, product_id: int | None = None) -> int:
        products = read_catalog()
        assigned_id = product_id or next_product_id(products)
        normalized = normalize_product({**payload, "id": assigned_id}, assigned_id)
        updated = False

        for index, product in enumerate(products):
            if int(product["id"]) == int(assigned_id):
                products[index] = normalized
                updated = True
                break

        if not updated:
            products.append(normalized)

        products.sort(key=lambda item: int(item["id"]))
        write_catalog(products)
        return assigned_id

    def delete_product(product_id: int) -> None:
        products = [product for product in read_catalog() if int(product["id"]) != int(product_id)]
        write_catalog(products)

    def get_product(product_id: int) -> dict | None:
        for product in read_catalog():
            if int(product["id"]) == int(product_id):
                return product
        return None

    def get_product_by_name(name: str) -> dict | None:
        for product in read_catalog():
            if product["name"].strip().lower() == name.strip().lower():
                return product
        return None

    def score_product(product: dict) -> dict:
        current_prices = [item["price"] for item in product["prices"]]
        current_lowest = min(current_prices)
        current_highest = max(current_prices)
        history_prices = [item["price"] for item in product["history"]] or [current_lowest]
        average_price = sum(history_prices) / len(history_prices)
        first_price = history_prices[0]
        last_price = history_prices[-1]

        price_score = clamp(5 + ((average_price - current_lowest) / average_price) * 12 if average_price else 5)
        trend_score = clamp(5 + ((first_price - last_price) / first_price) * 20 if first_price else 5)
        discount_score = clamp(((current_highest - current_lowest) / current_highest) * 10 if current_highest else 0)
        value_score = clamp(product["rating"] * 2)
        score = round((price_score * 0.4) + (trend_score * 0.2) + (discount_score * 0.2) + (value_score * 0.2), 1)

        if score >= 9:
            label = "Steal Deal"
        elif score >= 7:
            label = "Good Buy"
        elif score >= 5:
            label = "Average"
        else:
            label = "Wait"

        if score >= 8.5:
            tag = "Best Deal"
        elif current_lowest > average_price * 1.08:
            tag = "Overpriced"
        else:
            tag = "Fair Price"
        decision = "BUY NOW" if score >= 7 else "WAIT"
        is_best_deal = ((current_highest - current_lowest) / current_highest) >= 0.08 if current_highest else False

        insights = []
        insights.append(
            "Price is lower than last 30-day average." if current_lowest < average_price else "Current price is above last 30-day average."
        )
        if last_price < first_price:
            insights.append("Price trend is decreasing.")
        elif last_price > first_price:
            insights.append("Price trend is increasing.")
        else:
            insights.append("Price trend is stable.")
        insights.append("Good time to buy." if score >= 7 else "Monitor the trend before buying.")

        return {
            "score": score,
            "label": label,
            "tag": tag,
            "decision": decision,
            "is_best_deal": is_best_deal,
            "price_score": round(price_score, 1),
            "trend_score": round(trend_score, 1),
            "discount_score": round(discount_score, 1),
            "value_score": round(value_score, 1),
            "average_price": round(average_price, 2),
            "current_lowest": round(current_lowest, 2),
            "current_highest": round(current_highest, 2),
            "cheapest_platform": product["prices"][0]["platform"],
            "insights": insights,
        }

    def load_products() -> list[dict]:
        products = []
        for product in sorted(read_catalog(), key=lambda item: int(item["id"]), reverse=True):
            enriched = copy.deepcopy(product)
            enriched["analytics"] = score_product(enriched)
            products.append(enriched)
        return products

    def search_products(query: str) -> list[dict]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            return load_products()

        results = []
        for product in load_products():
            searchable = " ".join(
                [
                    product["name"],
                    product["category"],
                    " ".join(price["platform"] for price in product["prices"]),
                    product["analytics"]["cheapest_platform"],
                    product["analytics"]["tag"],
                    product["analytics"]["label"],
                ]
            ).lower()
            if normalized_query in searchable:
                results.append(product)
        return results

    def build_dashboard_metrics(products: list[dict]) -> dict:
        if not products:
            return {
                "total_products": 0,
                "average_score": 0,
                "best_deals": 0,
                "platforms_tracked": 0,
            }
        platforms = {price["platform"] for product in products for price in product["prices"]}
        average_score = round(sum(product["analytics"]["score"] for product in products) / len(products), 1)
        best_deals = sum(1 for product in products if product["analytics"]["tag"] == "Best Deal")
        return {
            "total_products": len(products),
            "average_score": average_score,
            "best_deals": best_deals,
            "platforms_tracked": len(platforms),
        }

    def import_products_into_catalog(products: list[dict]) -> tuple[int, int]:
        added = 0
        updated = 0
        for product in products:
            existing_product = get_product_by_name(product["name"])
            if existing_product:
                save_product(product, product_id=existing_product["id"])
                updated += 1
            else:
                save_product(product)
                added += 1
        return added, updated

    def admin_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not session.get("admin_logged_in"):
                flash("Please log in as admin to continue.", "warning")
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)

        return wrapped_view

    @app.before_request
    def boot_catalog() -> None:
        read_catalog()

    @app.template_filter("currency")
    def currency_filter(value):
        return f"₹{value:,.0f}"

    @app.route("/")
    def home():
        query = request.args.get("q", "").strip()
        products = search_products(query)
        return render_template(
            "home.html",
            products=products,
            dashboard_metrics=build_dashboard_metrics(products),
            featured_product=products[0] if products else None,
            search_query=query,
            active_page="home",
        )

    @app.route("/product/<int:product_id>")
    def product_detail(product_id: int):
        product = get_product(product_id)
        if not product:
            flash("Product not found.", "danger")
            return redirect(url_for("home"))
        product = copy.deepcopy(product)
        product["analytics"] = score_product(product)
        return render_template(
            "product.html",
            product=product,
            chart_dates=[item["date"] for item in product["history"]],
            chart_prices=[item["price"] for item in product["history"]],
            pie_labels=[item["platform"] for item in product["prices"]],
            pie_values=[item["price"] for item in product["prices"]],
            active_page="home",
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            if username == app.config["ADMIN_USERNAME"] and password == app.config["ADMIN_PASSWORD"]:
                session["admin_logged_in"] = True
                flash("Welcome back, admin.", "success")
                return redirect(url_for("admin"))
            flash("Invalid admin credentials.", "danger")
        return render_template("login.html", active_page="login")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("home"))

    @app.route("/admin")
    @admin_required
    def admin():
        edit_id = request.args.get("edit", type=int)
        editing_product = get_product(edit_id) if edit_id else None
        return render_template(
            "admin.html",
            products=load_products(),
            editing_product=editing_product,
            active_page="admin",
        )

    @app.route("/admin/add", methods=["POST"])
    @admin_required
    def add_product():
        payload = {
            "name": request.form.get("name", "").strip(),
            "category": request.form.get("category", "Tech").strip() or "Tech",
            "image_url": request.form.get("image_url", "").strip(),
            "prices": extract_prices_from_form(request.form),
        }
        if not payload["name"] or not payload["image_url"] or not payload["prices"]:
            flash("Name, image URL, and at least one platform price are required.", "danger")
            return redirect(url_for("admin"))
        payload["rating"] = estimate_ai_rating(payload["name"], payload["prices"])
        payload["history"] = generate_history_from_prices(payload["prices"], payload["rating"])
        save_product(payload)
        flash(f"Product added successfully. AI estimated the value rating at {payload['rating']}/5 and calculated the smart score automatically.", "success")
        return redirect(url_for("admin"))

    @app.route("/admin/edit/<int:product_id>", methods=["POST"])
    @admin_required
    def edit_product(product_id: int):
        payload = {
            "name": request.form.get("name", "").strip(),
            "category": request.form.get("category", "Tech").strip() or "Tech",
            "image_url": request.form.get("image_url", "").strip(),
            "prices": extract_prices_from_form(request.form),
        }
        if not payload["name"] or not payload["image_url"] or not payload["prices"]:
            flash("Name, image URL, and at least one platform price are required.", "danger")
            return redirect(url_for("admin", edit=product_id))
        payload["rating"] = estimate_ai_rating(payload["name"], payload["prices"])
        payload["history"] = generate_history_from_prices(payload["prices"], payload["rating"])
        save_product(payload, product_id=product_id)
        flash(f"Product updated successfully. AI recalculated the value rating to {payload['rating']}/5 and refreshed the smart score.", "success")
        return redirect(url_for("admin"))

    @app.route("/admin/import", methods=["POST"])
    @admin_required
    def import_products():
        raw_json = request.form.get("import_json", "").strip()
        if not raw_json:
            flash("Paste a JSON array before importing.", "danger")
            return redirect(url_for("admin"))
        try:
            products = parse_bulk_import(raw_json)
        except (ValueError, json.JSONDecodeError) as error:
            flash(f"Import failed: {error}", "danger")
            return redirect(url_for("admin"))
        added, updated = import_products_into_catalog(products)
        flash(
            f"Import complete. Added {added} products and updated {updated} existing products with AI-generated ratings and smart scores.",
            "success",
        )
        return redirect(url_for("admin"))

    @app.route("/admin/delete/<int:product_id>", methods=["POST"])
    @admin_required
    def remove_product(product_id: int):
        delete_product(product_id)
        flash("Product deleted.", "info")
        return redirect(url_for("admin"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
