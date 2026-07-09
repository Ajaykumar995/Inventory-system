def _token(client, username, email):
    client.post("/api/v1/auth/register", json={
        "email": email, "username": username, "password": "securepass123",
        "full_name": username.title(), "role_name": "employee",
    })
    return client.post("/api/v1/auth/login", json={"username": username, "password": "securepass123"}).json()["access_token"]


def _product_with_stock(client, token, sku="SALE-001"):
    cat = client.post("/api/v1/catalog/categories", json={"name": "Retail"},
                      headers={"Authorization": f"Bearer {token}"}).json()
    prod = client.post("/api/v1/catalog/products", json={
        "name": "Shampoo", "sku": sku, "category_id": cat["id"],
        "selling_price": 199, "cost_price": 120,
    }, headers={"Authorization": f"Bearer {token}"}).json()
    client.post("/api/v1/inventory/setup", json={
        "product_id": prod["id"], "current_stock": 50, "min_stock": 5, "max_stock": 200,
    }, headers={"Authorization": f"Bearer {token}"})
    return prod


def test_create_sale_and_invoice(client):
    token = _token(client, "salesuser", "sales@x.com")
    prod = _product_with_stock(client, token)

    r = client.post("/api/v1/sales", json={
        "customer_name": "Walk-in Customer",
        "payment_method": "cash",
        "tax_percent": 5,
        "items": [{"product_id": prod["id"], "quantity": 2}],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    sale = r.json()
    assert sale["invoice_number"].startswith("INV-")
    assert sale["total_amount"] > 0
    assert len(sale["items"]) == 1

    # Stock reduced
    stock = client.get("/api/v1/inventory/stock", headers={"Authorization": f"Bearer {token}"}).json()
    assert stock["items"][0]["current_stock"] == 48

    # Invoice lookup
    r = client.get(f"/api/v1/sales/invoice/{sale['invoice_number']}",
                   headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

    # Summary
    r = client.get("/api/v1/sales/summary", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["today_count"] >= 1


def test_insufficient_stock_rejected(client):
    token = _token(client, "salesuser2", "sales2@x.com")
    prod = _product_with_stock(client, token, sku="SALE-002")

    r = client.post("/api/v1/sales", json={
        "items": [{"product_id": prod["id"], "quantity": 999}],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400
