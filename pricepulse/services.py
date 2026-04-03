from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

from pricepulse.db import load_custom_products, load_products, replace_custom_products, upsert_custom_product


def _serialize_product(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "brand": row["brand"],
        "category": row["category"],
        "description": row["description"],
        "image": row["image"],
    }


def list_products() -> list[dict[str, Any]]:
    rows = sorted(load_products(), key=lambda product: product["name"])
    return [_serialize_product(row) for row in rows]


def get_product(product_id: str) -> dict[str, Any] | None:
    row = next((product for product in load_products() if product["id"] == product_id), None)
    return _serialize_product(row) if row else None


def get_offers(product_id: str) -> list[dict[str, Any]]:
    product = next((item for item in load_products() if item["id"] == product_id), None)
    if not product:
        return []
    return sorted(
        [
            {
                "retailer": offer["retailer"],
                "price": offer["price"],
                "stock": offer["stock"],
                "seller": offer["seller"],
                "url": offer["url"],
                "accent": offer["accent"],
            }
            for offer in product["offers"]
        ],
        key=lambda offer: offer["price"],
    )


def get_history(product_id: str) -> list[dict[str, Any]]:
    product = next((item for item in load_products() if item["id"] == product_id), None)
    if not product:
        return []
    return list(product["history"])


def _rank_product(query: str, product: dict[str, Any]) -> float:
    haystack = f"{product['name']} {product['brand']} {product['category']}".lower()
    normalized_query = query.lower().strip()
    if not normalized_query:
        return 0.0

    direct_bonus = 0.25 if normalized_query in haystack else 0.0
    token_bonus = sum(0.1 for token in normalized_query.split() if token in haystack)
    similarity = SequenceMatcher(None, normalized_query, haystack).ratio()
    return similarity + direct_bonus + token_bonus


def search_products(query: str) -> list[dict[str, Any]]:
    products = list_products()
    ranked = [(product, _rank_product(query, product)) for product in products]
    filtered = [item for item in ranked if item[1] > 0.2]
    filtered.sort(key=lambda item: item[1], reverse=True)
    return [product for product, _ in filtered]


def summarize_offers(offers: list[dict[str, Any]]) -> dict[str, Any]:
    in_stock = [offer for offer in offers if offer["stock"] != "Out of Stock"]
    ranked = in_stock or offers
    cheapest = ranked[0] if ranked else None
    runner_up = ranked[1] if len(ranked) > 1 else None
    spread = runner_up["price"] - cheapest["price"] if cheapest and runner_up else 0
    average = round(sum(offer["price"] for offer in offers) / len(offers)) if offers else 0
    lowest = min((offer["price"] for offer in offers), default=0)
    highest = max((offer["price"] for offer in offers), default=0)
    return {
        "cheapest": cheapest,
        "runner_up": runner_up,
        "spread": spread,
        "average_price": average,
        "lowest_price": lowest,
        "highest_price": highest,
        "last_updated": "2026-04-02T09:00:00+05:30",
    }


def build_product_payload(product_id: str) -> dict[str, Any] | None:
    product = get_product(product_id)
    if not product:
        return None

    offers = get_offers(product_id)
    history = get_history(product_id)
    summary = summarize_offers(offers)
    return {
        "product": product,
        "offers": offers,
        "history": history,
        "summary": summary,
    }


def search_payload(query: str) -> dict[str, Any]:
    matches = search_products(query)
    if not matches:
        return {"query": query, "matches": [], "best_match": None}

    best_match = matches[0]
    analytics = build_product_payload(best_match["id"])
    return {
        "query": query,
        "matches": matches[:4],
        "best_match": analytics,
    }


def list_custom_products() -> list[dict[str, Any]]:
    products = sorted(load_custom_products(), key=lambda product: product["name"].lower())
    return [_serialize_product(product) for product in products]


def _build_default_history(offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    multipliers = [1.08, 1.06, 1.04, 1.03, 1.01, 1.0]
    dates = ["2026-03-10", "2026-03-14", "2026-03-18", "2026-03-22", "2026-03-26", "2026-03-30"]
    history = []
    for date, multiplier in zip(dates, multipliers):
        snapshot = {"date": date}
        for offer in offers:
            snapshot[offer["retailer"]] = round(offer["price"] * multiplier)
        history.append(snapshot)
    return history


def _normalize_id(name: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else "-" for char in name.strip())
    return "-".join(chunk for chunk in normalized.split("-") if chunk)[:64]


def _validate_offer(offer: dict[str, Any]) -> dict[str, Any]:
    required = ["retailer", "price", "stock", "seller", "url", "accent"]
    missing = [field for field in required if not offer.get(field)]
    if missing:
        raise ValueError(f"Offer is missing fields: {', '.join(missing)}")
    return {
        "retailer": str(offer["retailer"]).strip(),
        "price": int(offer["price"]),
        "stock": str(offer["stock"]).strip(),
        "seller": str(offer["seller"]).strip(),
        "url": str(offer["url"]).strip(),
        "accent": str(offer["accent"]).strip(),
    }


def _validate_history(history: list[dict[str, Any]], offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    retailers = {offer["retailer"] for offer in offers}
    normalized = []
    for snapshot in history:
        if "date" not in snapshot:
            raise ValueError("Each history snapshot needs a date")
        item = {"date": str(snapshot["date"])}
        for retailer in retailers:
            if retailer in snapshot:
                item[retailer] = int(snapshot[retailer])
        normalized.append(item)
    return normalized


def validate_product_payload(payload: dict[str, Any]) -> dict[str, Any]:
    required = ["name", "brand", "category", "description", "image", "offers"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"Product is missing fields: {', '.join(missing)}")
    offers = [_validate_offer(offer) for offer in payload["offers"]]
    if not offers:
        raise ValueError("At least one offer is required")
    history = payload.get("history") or _build_default_history(offers)
    return {
        "id": str(payload.get("id") or _normalize_id(payload["name"])),
        "name": str(payload["name"]).strip(),
        "brand": str(payload["brand"]).strip(),
        "category": str(payload["category"]).strip(),
        "description": str(payload["description"]).strip(),
        "image": str(payload["image"]).strip(),
        "offers": offers,
        "history": _validate_history(history, offers),
    }


def save_admin_product(payload: dict[str, Any]) -> dict[str, Any]:
    product = validate_product_payload(payload)
    return upsert_custom_product(product)


def bulk_import_products(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    products = [validate_product_payload(item) for item in payload]
    return replace_custom_products(products)
