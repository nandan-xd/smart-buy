import unittest

from app import create_app

class StudentSmartBuyTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app("file::memory:?cache=shared")
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def login(self):
        return self.client.post(
            "/login",
            data={"username": "admin", "password": "smartbuy123"},
            follow_redirects=True,
        )

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Find the Smartest Deals for Students", response.data)
        self.assertIn(b"Products tracked", response.data)
        self.assertIn(b"Skincare", response.data)
        self.assertIn(b"Fashion", response.data)

    def test_home_search_filters_products(self):
        response = self.client.get("/?q=calculator")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Scientific Calculator FX-991ES Plus", response.data)
        self.assertNotIn(b"Ergonomic Study Chair", response.data)

    def test_home_search_handles_no_results(self):
        response = self.client.get("/?q=tablet")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No products found", response.data)

    def test_admin_can_add_product_without_manual_history(self):
        self.login()
        response = self.client.post(
            "/admin/add",
            data={
                "name": "Budget Backpack",
                "category": "Tech",
                "image_url": "https://example.com/bag.jpg",
                "platform[]": ["Amazon", "Flipkart"],
                "price[]": ["1499", "1399"],
                "link[]": ["https://amazon.in/example-bag", "https://flipkart.com/example-bag"],
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI estimated the value rating", response.data)

    def test_product_page_loads(self):
        response = self.client.get("/product/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Score", response.data)

    def test_admin_can_import_multiple_products_from_json(self):
        self.login()
        response = self.client.post(
            "/admin/import",
            data={
                "import_json": """
                [
                  {
                    "name": "Samsung S26 Ultra",
                    "category": "Tech",
                    "image_url": "https://example.com/s26.jpg",
                    "prices": [
                      {"platform": "Amazon", "price": 124999, "link": "https://amazon.in/s26"},
                      {"platform": "Flipkart", "price": 122499, "link": "https://flipkart.com/s26"}
                    ]
                  },
                  {
                    "name": "Study Lamp Pro",
                    "category": "Tech",
                    "image_url": "https://example.com/lamp.jpg",
                    "prices": [
                      {"platform": "Amazon", "price": 2199, "link": "https://amazon.in/lamp"},
                      {"platform": "Croma", "price": 2399, "link": "https://croma.com/lamp"}
                    ]
                  }
                ]
                """
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Added 2 products and updated 0 existing products", response.data)
        self.assertIn(b"Samsung S26 Ultra", response.data)
        self.assertIn(b"HP 15s Ryzen 5 Laptop", response.data)

    def test_admin_requires_login(self):
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin Login", response.data)


if __name__ == "__main__":
    unittest.main()
