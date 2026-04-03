from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path

from pricepulse.sample_data import PRODUCTS


BASE_DIR = Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    return Path(os.environ.get("PRICEPULSE_DATA_DIR", BASE_DIR / "data"))


def get_custom_products_path() -> Path:
    return get_data_dir() / "custom_products.json"


def init_db() -> None:
    data_dir = get_data_dir()
    custom_products_path = get_custom_products_path()
    data_dir.mkdir(parents=True, exist_ok=True)
    if not custom_products_path.exists():
        custom_products_path.write_text("[]", encoding="utf-8")


def load_products() -> list[dict]:
    init_db()
    custom_products = json.loads(get_custom_products_path().read_text(encoding="utf-8"))
    return deepcopy(PRODUCTS + custom_products)


def load_custom_products() -> list[dict]:
    init_db()
    return json.loads(get_custom_products_path().read_text(encoding="utf-8"))


def save_custom_products(products: list[dict]) -> None:
    init_db()
    get_custom_products_path().write_text(json.dumps(products, indent=2), encoding="utf-8")


def upsert_custom_product(product: dict) -> dict:
    products = load_custom_products()
    existing_index = next((index for index, item in enumerate(products) if item["id"] == product["id"]), None)
    if existing_index is None:
        products.append(product)
    else:
        products[existing_index] = product
    save_custom_products(products)
    return product


def replace_custom_products(products: list[dict]) -> list[dict]:
    save_custom_products(products)
    return products
