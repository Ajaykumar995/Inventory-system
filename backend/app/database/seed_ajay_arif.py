"""
Ajay & Arif catalog — users, suppliers, and branded products.

Runs on every startup (idempotent). Safe to call even if DB already has data.
"""

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.models.batch import InventoryBatch
from app.models.category import Category
from app.models.inventory import Inventory, MovementType, StockMovement
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.repository.user_repository import UserRepository
from app.utils.constants import DEFAULT_ROLES, UserRole

AJAY_ARIF_USERS = [
    {
        "username": "ajay",
        "email": "ajay@inventory.com",
        "password": "ajay123456",
        "full_name": "Ajay Kumar",
        "role": UserRole.STORE_MANAGER,
    },
    {
        "username": "arif",
        "email": "arif@inventory.com",
        "password": "arif123456",
        "full_name": "Arif Khan",
        "role": UserRole.INVENTORY_MANAGER,
    },
]

AJAY_ARIF_SUPPLIERS = [
    {
        "name": "Ajay Traders Pvt Ltd",
        "contact_person": "Ajay Kumar",
        "phone": "+91-9000010001",
        "email": "ajay@ajaytraders.com",
        "rating": 4.7,
    },
    {
        "name": "Arif Pharma Distributors",
        "contact_person": "Arif Khan",
        "phone": "+91-9000020002",
        "email": "arif@arifpharma.com",
        "rating": 4.6,
    },
]

# (name, sku, barcode, brand, category_name, unit, cost, sell, stock, min, max, batch, expiry_days)
AJAY_ARIF_PRODUCTS = [
    # Ajay brand — grocery & wellness
    ("Ajay Pure Honey 500g", "AJAY-HONEY-500", "8902001001001", "Ajay Naturals", "Grocery", "jar", 180, 249, 45, 10, 120, "AJAY-B-H001", 365),
    ("Ajay Herbal Face Wash 100ml", "AJAY-FW-100", "8902001001002", "Ajay Care", "Personal Care", "bottle", 65, 99, 60, 15, 150, "AJAY-B-F001", 540),
    ("Ajay Organic Green Tea 25 Bags", "AJAY-GT-25", "8902001001003", "Ajay Naturals", "Grocery", "box", 95, 145, 35, 10, 100, "AJAY-B-T001", 300),
    ("Ajay Almonds 250g", "AJAY-ALM-250", "8902001001004", "Ajay Naturals", "Grocery", "pack", 220, 299, 28, 8, 80, "AJAY-B-A001", 180),
    # Arif brand — pharmacy & medicines
    ("Arif Pain Relief Balm 25g", "ARIF-BALM-25", "8902002002001", "Arif Pharma", "Medicines", "jar", 35, 55, 90, 20, 250, "ARIF-B-P001", 730),
    ("Arif Multivitamin Tablets 60s", "ARIF-MULTI-60", "8902002002002", "Arif Pharma", "Medicines", "bottle", 120, 185, 55, 15, 200, "ARIF-B-M001", 365),
    ("Arif Antiseptic Liquid 100ml", "ARIF-ANTI-100", "8902002002003", "Arif Pharma", "Medicines", "bottle", 45, 75, 70, 20, 180, "ARIF-B-A001", 540),
    ("Arif Cough Syrup 100ml", "ARIF-COUGH-100", "8902002002004", "Arif Pharma", "Medicines", "bottle", 55, 89, 12, 15, 150, "ARIF-B-C001", 45),
    ("Arif Vitamin D3 60K 4 Tabs", "ARIF-VITD3-4", "8902002002005", "Arif Pharma", "Medicines", "strip", 28, 45, 40, 10, 120, "ARIF-B-V001", 180),
    ("Arif ORS Powder 21g", "ARIF-ORS-21", "8902002002006", "Arif Pharma", "Medicines", "sachet", 18, 30, 100, 25, 300, "ARIF-B-O001", 365),
]


def _get_role_id(db: Session, role_name: str) -> int:
    role = UserRepository(db).get_role_by_name(role_name)
    if role is None:
        raise RuntimeError(f"Role {role_name} not found")
    return role.id


def _get_or_create_category(db: Session, name: str, description: str) -> Category:
    cat = db.execute(select(Category).where(func.lower(Category.name) == name.lower())).scalar_one_or_none()
    if cat:
        return cat
    cat = Category(name=name, description=description)
    db.add(cat)
    db.flush()
    return cat


def _get_or_create_supplier(db: Session, data: dict) -> Supplier:
    sup = db.execute(select(Supplier).where(func.lower(Supplier.name) == data["name"].lower())).scalar_one_or_none()
    if sup:
        return sup
    sup = Supplier(**data)
    db.add(sup)
    db.flush()
    return sup


def _get_admin_id(db: Session) -> int:
    admin = db.execute(select(User).where(User.username == "admin")).scalar_one_or_none()
    if admin:
        return admin.id
    user = db.execute(select(User).order_by(User.id)).scalar_one_or_none()
    if user:
        return user.id
    raise RuntimeError("No user found to attribute stock movements")


def ensure_ajay_arif_data(db: Session) -> dict:
    """Add Ajay & Arif users, suppliers, products if not already present."""
    UserRepository(db).seed_roles(DEFAULT_ROLES)

    users_added = 0
    for u in AJAY_ARIF_USERS:
        existing = db.execute(select(User).where(User.username == u["username"])).scalar_one_or_none()
        if existing:
            existing.hashed_password = get_password_hash(u["password"])
            existing.full_name = u["full_name"]
            existing.role_id = _get_role_id(db, u["role"].value)
            existing.is_verified = True
            continue
        db.add(User(
            email=u["email"],
            username=u["username"],
            hashed_password=get_password_hash(u["password"]),
            full_name=u["full_name"],
            role_id=_get_role_id(db, u["role"].value),
            is_verified=True,
        ))
        users_added += 1

    db.flush()

    suppliers_added = 0
    for s in AJAY_ARIF_SUPPLIERS:
        if db.execute(select(Supplier).where(func.lower(Supplier.name) == s["name"].lower())).scalar_one_or_none():
            continue
        db.add(Supplier(**s))
        suppliers_added += 1
    db.flush()

    # Ensure base categories exist
    category_map: dict[str, Category] = {}
    for cat_name in ("Medicines", "Personal Care", "Grocery"):
        category_map[cat_name] = _get_or_create_category(db, cat_name, f"{cat_name} products")

    products_added = 0
    admin_id = _get_admin_id(db)
    today = date.today()

    for row in AJAY_ARIF_PRODUCTS:
        name, sku, barcode, brand, cat_name, unit, cost, sell, stock, min_s, max_s, batch_no, expiry_days = row
        existing = db.execute(select(Product).where(Product.sku == sku)).scalar_one_or_none()
        if existing:
            continue

        cat = category_map[cat_name]
        prod = Product(
            name=name, sku=sku, barcode=barcode, brand=brand,
            category_id=cat.id, unit=unit,
            cost_price=cost, selling_price=sell, is_active=True,
            description=f"Official {brand} product — managed by Ajay & Arif catalog",
        )
        db.add(prod)
        db.flush()

        inv = Inventory(
            product_id=prod.id,
            current_stock=stock,
            min_stock=min_s,
            max_stock=max_s,
            location="Ajay-Arif-Aisle",
        )
        db.add(inv)

        if batch_no and expiry_days:
            db.add(InventoryBatch(
                product_id=prod.id,
                batch_number=batch_no,
                expiry_date=today + timedelta(days=expiry_days),
                quantity=stock,
                received_date=today - timedelta(days=14),
            ))

        db.add(StockMovement(
            product_id=prod.id,
            movement_type=MovementType.IN.value,
            quantity=stock,
            previous_qty=0,
            new_qty=stock,
            reason="Ajay & Arif catalog initial stock",
            reference=f"AJAY-ARIF-{sku}",
            created_by=admin_id,
        ))
        products_added += 1

    db.commit()

    return {
        "ajay_arif_synced": True,
        "users_added": users_added,
        "suppliers_added": suppliers_added,
        "products_added": products_added,
        "total_ajay_arif_products": len(AJAY_ARIF_PRODUCTS),
        "logins": [
            {"username": "ajay", "password": "ajay123456", "role": "store_manager"},
            {"username": "arif", "password": "arif123456", "role": "inventory_manager"},
        ],
    }


if __name__ == "__main__":
    import app.models  # noqa: F401 — register all ORM mappers
    from app.database.base import Base
    from app.database.session import SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print(ensure_ajay_arif_data(db))
    finally:
        db.close()
