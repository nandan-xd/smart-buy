# Smart Buy Hub

Smart Buy Hub is a full-stack Flask web app to compare product prices, understand deal quality with a smart score, and make better purchase decisions.

## Features

- Home page with responsive product cards
- Product detail page with comparison table, cheapest-price highlight, and buy links
- Smart Score system with deal labels and insight text
- Chart.js line chart for price history and pie chart for platform price distribution
- Admin login with Flask session authentication
- Admin CRUD for adding, editing, and deleting products
- SQLite database with seeded sample products
- Dark and light mode toggle saved in `localStorage`

## Run locally

```bash
pip install flask
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Admin credentials

- Username: `admin`
- Password: `smartbuy123`

## File structure

- `app.py`
- `templates/base.html`
- `templates/home.html`
- `templates/product.html`
- `templates/admin.html`
- `templates/login.html`
- `static/css/style.css`
- `static/js/main.js`
- `static/js/admin.js`

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Deploy on Render

This project is ready for Render with:

- [requirements.txt](/D:/VIBEIN'/requirements.txt)
- [render.yaml](/D:/VIBEIN'/render.yaml)

Recommended steps:

```bash
pip install -r requirements.txt
```

Then:

1. Push this project to a GitHub repository.
2. In Render, create a new Blueprint or Web Service from that GitHub repo.
3. Render will use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`

Important:

- SQLite works for simple demos, but Render disks are not ideal for production data persistence.
- If you need reliable hosted persistence later, move the database to Postgres.
