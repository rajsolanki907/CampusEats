## CampusEats Backend

FastAPI + SQLAlchemy backend for a campus food ordering app with users, vendors, menus, carts, and orders.

### 1. Project structure

- `Backend/`
  - `main.py` – FastAPI app and all HTTP routes
  - `models.py` – SQLAlchemy models
  - `schemas.py` – Pydantic models (request/response)
  - `database.py` – DB engine/session setup
  - `token_logic.py` – JWT token creation
  - `hashing.py` – password hashing with bcrypt
  - `config.py` – central configuration (DB URL, JWT, CORS)
  - `requirements.txt` – Python dependencies
- `automation/` – personal scripts integrating with Google Sheets/Tasks

### 2. Setup (local development)

From your terminal:

```bash
cd /Users/raj/Desktop/CampusEats
cd Backend
python -m venv venv        # if you don't already have one
source venv/bin/activate   # macOS / Linux
# .\venv\Scripts\activate  # Windows PowerShell

pip install -r requirements.txt
```

Create a `.env` file in the project root based on `.env.example` and set at least:

- `SECRET_KEY` – long random string
- `DATABASE_URL` – leave as SQLite for dev, or point to Postgres/MySQL for production
- `CORS_ORIGINS` – your frontend URL(s), e.g. `http://localhost:5173`

### 3. Run the API

**Important:** You must run uvicorn from the `Backend` directory where `main.py` is located.

With your virtualenv activated:

```bash
cd Backend
uvicorn main:app --reload
```

**Alternative:** If you prefer to run from the project root, use:

```bash
uvicorn Backend.main:app --reload
```

Then open the interactive docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 4. Key features

- **Authentication**
  - `POST /register` – create user
  - `POST /login` – obtain JWT access token (OAuth2 password flow)
  - `GET /users/me` – check current logged-in user
- **Vendors & menu**
  - `POST /vendors/` – create vendor profile for current user
  - `POST /vendors/my-menu/items` – add food items for your restaurant
  - `GET /menu/` – all food items from all vendors
  - `GET /vendors/{vendor_id}/menu` – items for a specific vendor
- **Cart & orders**
  - `POST /cart/` – add item to cart (aggregates quantity)
  - `GET /cart/` – view current cart
  - `POST /cart/checkout` – create an order from the cart
    - Enforces **single-vendor carts**: cart must only contain items from one restaurant
    - Persists line items in `OrderItem` so past orders remember what was purchased
  - `GET /orders/me` – authenticated user's order history
  - `GET /vendor/dashboard` – vendor's orders
  - `PUT /vendor/orders/{order_id}/status` – vendor updates order status

### 5. Configuration and environment

All configuration is centralized in `config.py` and read from environment variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CORS_ORIGINS`

For deployment, set these via your platform's environment settings instead of committing secrets.

### 6. Git & GitHub (first push)

From `/Users/raj/Desktop/CampusEats`:

```bash
git init
git status
git add .
git commit -m "Initial CampusEats backend"
```

Then on GitHub:

1. Create a new empty repository (no README or .gitignore) called `CampusEats`.
2. Follow the "push an existing repository" instructions, e.g.:

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/CampusEats.git
git push -u origin main
```

### 7. Deployment notes

For a simple deployment (Render, Railway, etc.):

- Set `DATABASE_URL` to a managed Postgres instance.
- Set `SECRET_KEY` to a strong random string.
- Set `CORS_ORIGINS` to your production frontend URL.
- Use a start command similar to:

```bash
uvicorn Backend.main:app --host 0.0.0.0 --port 8000
```

Later, you can introduce database migrations (Alembic) and split routes into separate modules for larger teams and features.

