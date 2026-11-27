# 🏬 Retail Inventory Management System (RIMS)

A Flask-based **Retail Inventory Management System** for managing products, categories, warehouses, stock levels, carts, orders, and operational workflows. The application uses SQLAlchemy models and role-aware Flask views to connect inventory and customer-facing commerce functions.

## ✨ Core modules

| Module | What it handles |
| --- | --- |
| Authentication | User sign-in, account flows, and admin access |
| Product catalogue | Products, categories, and catalogue browsing |
| Inventory | Stock quantities, warehouse allocation, and stock adjustments |
| Warehouse | Warehouse records and inventory relationships |
| Cart | User carts, cart items, quantity changes, and cart totals |
| Orders | Order creation, order details, and order-status management |
| Checkout | Checkout flow with a **mock payment** record |
| Providers & customers | Business contact records |
| Delivery & transfers | Delivery and stock movement workflows |
| Dashboards & reports | User/admin views and reporting endpoints |

The codebase also contains role-aware route handling, Flask-Login integration, form CSRF protection, and SQLAlchemy models for the application's core entities.

## 🧰 Technology stack

- **Python** — application language
- **Flask** — web application framework
- **Flask-Login** — user session and authentication integration
- **Flask-WTF / WTForms** — form handling and CSRF protection
- **Flask-SQLAlchemy / SQLAlchemy** — ORM and relational data access
- **PostgreSQL** — deployment database when configured through `DATABASE_URL`
- **SQLite** — safe local-development fallback
- **psycopg2-binary** — PostgreSQL driver
- **python-dotenv** — local environment configuration
- **Gunicorn** — production WSGI server

## 🗂️ Data model

The SQLAlchemy models include entities for:

- Users and roles
- Categories and products
- Warehouses and inventory records
- Carts and cart items
- Orders, order details, and payments
- Providers and customers
- Deliveries and delivery details

Inventory records associate products with warehouses and store available quantities, minimum stock levels, and reorder points.

## 🚀 Getting started

### 1. Clone the repository

```bash
git clone https://github.com/Kanduriavinash/dbms-project-.git
cd dbms-project-
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

Copy the safe template and replace the placeholders with your own local or deployment values:

```bash
cp .env.example .env
```

For PowerShell:

```powershell
Copy-Item .env.example .env
```

- Leave `DATABASE_URL` unset for the local SQLite database, or set it to a PostgreSQL connection string.
- Set `SECRET_KEY` to a long, random value. Use a different value for each deployment.
- Never commit `.env` or paste credentials into source files.

### 5. Run the application

```bash
python app.py
```

Open the local URL printed by Flask in your browser. For production, configure the environment variables in the hosting provider and run the application with a WSGI server such as Gunicorn.

## 🔐 Security and payment scope

- The repository uses environment variables for database connection details and the Flask secret key. Keep real values outside version control.
- The checkout implementation records a **mock payment**. It is not a live payment gateway and must not be presented as processing real financial transactions.
- Use HTTPS, a strong deployment secret, restricted database credentials, and production-safe logging before exposing an instance to real users.
- Do not enable SQL statement echoing or request-header logging in production.

## 📌 Project status

This repository contains an academic/portfolio application with catalogue, inventory, cart, order, and administrative workflows. Validate the workflows against your own database and deployment configuration before using it with real business data.

## 👨‍💻 Author

[Kanduri Avinash](https://github.com/Kanduriavinash)

---

Built to explore relational data modelling, Flask application structure, authentication, inventory workflows, and database-backed web development.
