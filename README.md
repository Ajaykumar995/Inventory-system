# Smart Inventory & Stock Prediction System

Enterprise-grade inventory management for pharmacies, supermarkets, and retail warehouses.

## Module 1: Authentication & RBAC (Complete)

### Quick Start

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### Demo Login (auto-seeded on first run)

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123456` | Admin |
| `manager` | `manager123` | Inventory Manager |
| `cashier` | `cashier123` | Employee |

Reload demo data: `python -m app.database.seed --force`

Add only Ajay & Arif catalog: `python -m app.database.seed_ajay_arif`

| Username | Password | Role |
|----------|----------|------|
| `ajay` | `ajay123456` | Store Manager |
| `arif` | `arif123456` | Inventory Manager |

**Ajay products:** Honey, Face Wash, Green Tea, Almonds (brand: Ajay Naturals / Ajay Care)  
**Arif products:** Pain Balm, Multivitamin, Antiseptic, Cough Syrup, Vitamin D3, ORS (brand: Arif Pharma)

## Architecture

```
inventory-system/
├── backend/          # FastAPI + SQLAlchemy
└── frontend/         # React + Vite + Tailwind
```

## Modules Roadmap

| # | Module | Status |
|---|--------|--------|
| 1 | Authentication & RBAC | ✅ Done |
| 2 | Products & Categories | ✅ Done |
| 3 | Inventory & Stock | ✅ Done |
| 4 | Purchase Orders & Suppliers | ✅ Done |
| 5 | Sales & Invoicing | ✅ Done |
| 6 | Expiry Management & Notifications | ✅ Done |
| 7 | Prediction Engine | ✅ Done |
| 8 | Reports & CSV Export | ✅ Done |
| 9 | Global Search | ✅ Done |
| 10 | Activity / Audit Log | ✅ Done |
| 11 | User Management (Admin) | ✅ Done |
| 12 | Profile Settings | ✅ Done |

### Roles (5 total)

`admin` → `inventory_manager` → `store_manager` → `employee` → `supplier`

Admin can create users and assign roles from **Users** page in the app.
