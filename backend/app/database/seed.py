"""
Demo / seed data for Smart Inventory System.

Runs automatically on startup when the database has no products
(and SEED_DEMO_DATA is enabled). Also runnable manually:

    python -m app.database.seed
"""

from datetime import date, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.batch import InventoryBatch
from app.models.category import Category
from app.models.inventory import Inventory, MovementType, StockMovement
from app.models.product import Product
from app.models.purchase import POStatus, PurchaseItem, PurchaseOrder
from app.models.sale import Sale, SaleItem, SaleStatus
from app.models.supplier import Supplier
from app.models.user import User
from app.repository.user_repository import UserRepository
from app.utils.constants import DEFAULT_ROLES, UserRole


DEMO_USERS = [
    {"username": "admin", "email": "admin@pharmacy.com", "password": "admin123456", "full_name": "System Admin", "role": UserRole.ADMIN},
    {"username": "manager", "email": "manager@pharmacy.com", "password": "manager123", "full_name": "Inventory Manager", "role": UserRole.INVENTORY_MANAGER},
    {"username": "cashier", "email": "cashier@pharmacy.com", "password": "cashier123", "full_name": "Store Cashier", "role": UserRole.EMPLOYEE},
    {"username": "ajay", "email": "ajay@inventory.com", "password": "ajay123456", "full_name": "Ajay Kumar", "role": UserRole.STORE_MANAGER},
    {"username": "arif", "email": "arif@inventory.com", "password": "arif123456", "full_name": "Arif Khan", "role": UserRole.INVENTORY_MANAGER},
]

DEMO_CATEGORIES = [
    ("Medicines", "Prescription & OTC medicines"),
    ("Personal Care", "Soaps, shampoos, skincare"),
    ("Grocery", "Daily essentials & packaged food"),
    ("Baby Care", "Diapers, baby food, wipes"),
]

DEMO_SUPPLIERS = [
    {"name": "Apollo Distributors", "contact_person": "Rajesh Kumar", "phone": "+91-9876543210", "email": "rajesh@apollo-dist.com", "rating": 4.8},
    {"name": "MedLife Wholesale", "contact_person": "Priya Sharma", "phone": "+91-9123456789", "email": "priya@medlife.com", "rating": 4.2},
    {"name": "FreshMart Supply", "contact_person": "Amit Patel", "phone": "+91-9988776655", "email": "amit@freshmart.com", "rating": 4.5},
    {"name": "Ajay Traders Pvt Ltd", "contact_person": "Ajay Kumar", "phone": "+91-9000010001", "email": "ajay@ajaytraders.com", "rating": 4.7},
    {"name": "Arif Pharma Distributors", "contact_person": "Arif Khan", "phone": "+91-9000020002", "email": "arif@arifpharma.com", "rating": 4.6},
]

# (name, sku, barcode, brand, category_idx, unit, cost, sell, stock, min, max, batch, expiry_days)
DEMO_PRODUCTS = [
    ("Paracetamol 500mg", "MED-PARA-500", "8901234567890", "Cipla", 0, "strip", 12, 18, 120, 30, 500, "BATCH-P001", 180),
    ("Amoxicillin 250mg", "MED-AMOX-250", "8901234567891", "Sun Pharma", 0, "strip", 45, 65, 8, 20, 200, "BATCH-A001", 25),
    ("Cetirizine 10mg", "MED-CET-10", "8901234567892", "Dr Reddy", 0, "strip", 8, 15, 5, 15, 300, "BATCH-C001", 10),
    ("Dove Soap 125g", "PC-DOVE-125", "8901234567900", "Dove", 1, "piece", 35, 55, 80, 20, 200, "BATCH-D001", 365),
    ("Colgate MaxFresh 150g", "PC-COLG-150", "8901234567901", "Colgate", 1, "tube", 55, 85, 45, 15, 150, "BATCH-COL01", 300),
    ("Basmati Rice 5kg", "GRO-RICE-5K", "8901234567910", "India Gate", 2, "bag", 380, 499, 25, 10, 100, "BATCH-R001", 180),
    ("Sunflower Oil 1L", "GRO-OIL-1L", "8901234567911", "Fortune", 2, "bottle", 120, 155, 60, 20, 200, "BATCH-O001", 120),
    ("Pampers Diapers M", "BAB-PAMP-M", "8901234567920", "Pampers", 3, "pack", 450, 599, 15, 5, 80, "BATCH-PMP01", 90),
    ("Cerelac Wheat 300g", "BAB-CERE-300", "8901234567921", "Nestle", 3, "box", 180, 245, 3, 10, 60, "BATCH-CR001", 14),
    ("Hand Sanitizer 500ml", "PC-SANI-500", "8901234567902", "Dettol", 1, "bottle", 90, 140, 0, 10, 100, None, None),
    # Ajay brand products
    ("Ajay Pure Honey 500g", "AJAY-HONEY-500", "8902001001001", "Ajay Naturals", 2, "jar", 180, 249, 45, 10, 120, "AJAY-B-H001", 365),
    ("Ajay Herbal Face Wash 100ml", "AJAY-FW-100", "8902001001002", "Ajay Care", 1, "bottle", 65, 99, 60, 15, 150, "AJAY-B-F001", 540),
    ("Ajay Organic Green Tea 25 Bags", "AJAY-GT-25", "8902001001003", "Ajay Naturals", 2, "box", 95, 145, 35, 10, 100, "AJAY-B-T001", 300),
    ("Ajay Almonds 250g", "AJAY-ALM-250", "8902001001004", "Ajay Naturals", 2, "pack", 220, 299, 28, 8, 80, "AJAY-B-A001", 180),
    # Arif brand products
    ("Arif Pain Relief Balm 25g", "ARIF-BALM-25", "8902002002001", "Arif Pharma", 0, "jar", 35, 55, 90, 20, 250, "ARIF-B-P001", 730),
    ("Arif Multivitamin Tablets 60s", "ARIF-MULTI-60", "8902002002002", "Arif Pharma", 0, "bottle", 120, 185, 55, 15, 200, "ARIF-B-M001", 365),
    ("Arif Antiseptic Liquid 100ml", "ARIF-ANTI-100", "8902002002003", "Arif Pharma", 0, "bottle", 45, 75, 70, 20, 180, "ARIF-B-A001", 540),
    ("Arif Cough Syrup 100ml", "ARIF-COUGH-100", "8902002002004", "Arif Pharma", 0, "bottle", 55, 89, 12, 15, 150, "ARIF-B-C001", 45),
    ("Arif Vitamin D3 60K 4 Tabs", "ARIF-VITD3-4", "8902002002005", "Arif Pharma", 0, "strip", 28, 45, 40, 10, 120, "ARIF-B-V001", 180),
    ("Arif ORS Powder 21g", "ARIF-ORS-21", "8902002002006", "Arif Pharma", 0, "sachet", 18, 30, 100, 25, 300, "ARIF-B-O001", 365),
]


def _get_role_id(db: Session, role_name: str) -> int:
    role = UserRepository(db).get_role_by_name(role_name)
    if role is None:
        raise RuntimeError(f"Role {role_name} not found")
    return role.id


def _clear_business_data(db: Session) -> None:
    """Remove transactional/catalog data but keep roles."""
    for model in (SaleItem, Sale, StockMovement, PurchaseItem, PurchaseOrder, InventoryBatch, Inventory, Product, Category, Supplier):
        db.execute(delete(model))
    db.commit()


def seed_demo_data(db: Session, force: bool = False) -> dict:
    """Insert demo data. Idempotent — skips if products already exist unless force=True."""
    product_count = db.execute(select(func.count()).select_from(Product)).scalar_one()
    if int(product_count) > 0 and not force:
        return {"seeded": False, "message": "Database already has products. Run with --force to reload."}

    if force and int(product_count) > 0:
        _clear_business_data(db)

    UserRepository(db).seed_roles(DEFAULT_ROLES)

    # Users
    user_ids: dict[str, int] = {}
    for u in DEMO_USERS:
        existing = db.execute(select(User).where(User.username == u["username"])).scalar_one_or_none()
        if existing:
            user_ids[u["username"]] = existing.id
            continue
        user = User(
            email=u["email"],
            username=u["username"],
            hashed_password=get_password_hash(u["password"]),
            full_name=u["full_name"],
            role_id=_get_role_id(db, u["role"].value),
            is_verified=True,
        )
        db.add(user)
        db.flush()
        user_ids[u["username"]] = user.id

    # Categories
    categories: list[Category] = []
    for name, desc in DEMO_CATEGORIES:
        cat = Category(name=name, description=desc)
        db.add(cat)
        categories.append(cat)
    db.flush()

    # Suppliers
    suppliers: list[Supplier] = []
    for s in DEMO_SUPPLIERS:
        sup = Supplier(**s)
        db.add(sup)
        suppliers.append(sup)
    db.flush()

    # Products + Inventory + Batches
    products: list[Product] = []
    admin_id = user_ids["admin"]
    today = date.today()

    for row in DEMO_PRODUCTS:
        name, sku, barcode, brand, cat_idx, unit, cost, sell, stock, min_s, max_s, batch_no, expiry_days = row
        prod = Product(
            name=name, sku=sku, barcode=barcode, brand=brand,
            category_id=categories[cat_idx].id, unit=unit,
            cost_price=cost, selling_price=sell, is_active=True,
        )
        db.add(prod)
        db.flush()
        products.append(prod)

        inv = Inventory(
            product_id=prod.id, current_stock=stock,
            min_stock=min_s, max_stock=max_s,
            location=f"Aisle-{cat_idx + 1}",
        )
        db.add(inv)

        if batch_no and expiry_days:
            db.add(InventoryBatch(
                product_id=prod.id, batch_number=batch_no,
                expiry_date=today + timedelta(days=expiry_days),
                quantity=stock, received_date=today - timedelta(days=30),
            ))

        if stock > 0:
            db.add(StockMovement(
                product_id=prod.id, movement_type=MovementType.IN.value,
                quantity=stock, previous_qty=0, new_qty=stock,
                reason="Initial seed stock", reference="SEED-001",
                created_by=admin_id,
            ))

    db.flush()

    # Purchase Order (received)
    po = PurchaseOrder(
        po_number=f"PO-{today.strftime('%Y%m%d')}-0001",
        supplier_id=suppliers[0].id,
        status=POStatus.RECEIVED.value,
        order_date=today - timedelta(days=15),
        expected_delivery=today - timedelta(days=5),
        received_date=today - timedelta(days=3),
        total_amount=float(products[0].cost_price or 0) * 50,
        notes="Monthly medicine replenishment",
        created_by=admin_id,
        items=[PurchaseItem(
            product_id=products[0].id, quantity_ordered=50,
            quantity_received=50, unit_price=float(products[0].cost_price or 0),
            batch_number="BATCH-P001",
        )],
    )
    db.add(po)

    # Sales history (last 14 days) for prediction engine
    sale_items_data = [
        (products[0], 5, 12),   # Paracetamol - fast mover
        (products[0], 3, 10),
        (products[0], 4, 8),
        (products[3], 2, 11),   # Dove soap
        (products[3], 1, 9),
        (products[5], 1, 7),    # Rice
        (products[6], 3, 6),    # Oil
        (products[1], 1, 13),   # Amoxicillin
    ]
    invoice_num = 1
    for prod, qty, days_ago in sale_items_data:
        inv = db.execute(select(Inventory).where(Inventory.product_id == prod.id)).scalar_one()
        if inv.current_stock < qty:
            continue
        prev = inv.current_stock
        inv.current_stock = prev - qty
        sale_date = today - timedelta(days=days_ago)
        price = float(prod.selling_price or 0)
        sale = Sale(
            invoice_number=f"INV-{sale_date.strftime('%Y%m%d')}-{invoice_num:04d}",
            customer_name="Walk-in Customer",
            subtotal=price * qty, tax_amount=0, discount=0,
            total_amount=price * qty, payment_method="cash",
            status=SaleStatus.COMPLETED.value,
            sale_date=sale_date, sold_by=user_ids["cashier"],
            items=[SaleItem(
                product_id=prod.id, quantity=qty,
                unit_price=price, line_total=price * qty,
            )],
        )
        db.add(sale)
        db.add(StockMovement(
            product_id=prod.id, movement_type=MovementType.OUT.value,
            quantity=qty, previous_qty=prev, new_qty=inv.current_stock,
            reason=f"Sale: {sale.invoice_number}", reference=sale.invoice_number,
            created_by=user_ids["cashier"],
        ))
        invoice_num += 1

    db.commit()

    return {
        "seeded": True,
        "message": "Demo data loaded successfully",
        "users": len(DEMO_USERS),
        "products": len(DEMO_PRODUCTS),
        "login": {"username": "admin", "password": "admin123456"},
    }


def run_seed(force: bool = False) -> dict:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        return seed_demo_data(db, force=force)
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    result = run_seed(force=force)
    print(result)
