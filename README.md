# Smart Inventory & Stock Prediction System

Enterprise-grade inventory management for pharmacies, supermarkets, and retail warehouses.

Built with **FastAPI**, **React**, and **SQLAlchemy** — includes RBAC, stock tracking, POS sales, expiry alerts, demand prediction, and CSV reports.

**Author:** [Ajay Kumar](https://github.com/Ajaykumar995)

---

## Features

- Authentication & role-based access (5 roles)
- Products, categories, and image upload
- Inventory & stock movements with audit trail
- Purchase orders & supplier management
- Point of Sale (POS) & invoicing
- Expiry management & notifications
- Stock prediction & reorder suggestions
- Reports (CSV export), global search, user management

---

## Tech Stack

| Layer | Technologies |
|-------|----------------|
| Backend | Python, FastAPI, SQLAlchemy, Alembic, JWT, bcrypt |
| Frontend | React 19, Vite, TypeScript, Tailwind CSS 4 |
| Database | SQLite (dev) / PostgreSQL (production) |
| Charts / 3D | Recharts, Three.js |

---

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

| Service | URL |
|---------|-----|
| App UI | http://localhost:5173 |
| API Docs | http://localhost:8000/docs |

> On Windows PowerShell, use `npm.cmd run dev` if `npm` is blocked.

---

## Default Accounts

Demo data loads automatically on first run.

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123456` | Admin |
| `manager` | `manager123` | Inventory Manager |
| `cashier` | `cashier123` | Employee |
| `ajay` | `ajay123456` | Store Manager |
| `arif` | `arif123456` | Inventory Manager |

**Seed commands** (from `backend/` folder):

```bash
python -m app.database.seed --force          # reload full demo data
python -m app.database.seed_ajay_arif        # sync Ajay & Arif catalog only
```

---

## Project Structure

```
inventory-system/
├── backend/                 # FastAPI API, models, services, tests
│   └── app/
│       ├── routers/
│       ├── services/
│       ├── models/
│       └── database/
└── frontend/                # React SPA
    └── src/
        ├── pages/
        ├── components/
        └── services/
```

---

## User Roles

```
admin  →  inventory_manager  →  store_manager  →  employee  →  supplier
```

Admins can create users and assign roles from the **Users** page in the app.

---

## License

This project is for educational and portfolio use.
