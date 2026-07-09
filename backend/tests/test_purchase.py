def _token(client, username, email):
    client.post("/api/v1/auth/register", json={
        "email": email, "username": username, "password": "securepass123",
        "full_name": username.title(), "role_name": "employee",
    })
    return client.post("/api/v1/auth/login", json={"username": username, "password": "securepass123"}).json()["access_token"]


def _setup_product(client, token):
    cat = client.post("/api/v1/catalog/categories", json={"name": "Medical"},
                      headers={"Authorization": f"Bearer {token}"}).json()
    prod = client.post("/api/v1/catalog/products", json={
        "name": "Aspirin", "sku": "ASP-100", "category_id": cat["id"], "cost_price": 5,
    }, headers={"Authorization": f"Bearer {token}"}).json()
    return prod


def test_supplier_and_purchase_flow(client):
    token = _token(client, "poadmin", "po@x.com")
    prod = _setup_product(client, token)

    # Create supplier
    r = client.post("/api/v1/purchases/suppliers", json={
        "name": "MedSupply Co", "contact_person": "Raj", "phone": "+91-9999999999",
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    supplier_id = r.json()["id"]

    # Create PO
    r = client.post("/api/v1/purchases/orders", json={
        "supplier_id": supplier_id,
        "expected_delivery": "2026-12-31",
        "items": [{"product_id": prod["id"], "quantity_ordered": 100, "unit_price": 5}],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    po = r.json()
    assert po["status"] == "ordered"
    assert po["total_amount"] == 500

    # Receive stock
    item_id = po["items"][0]["id"]
    r = client.post(f"/api/v1/purchases/orders/{po['id']}/receive", json={
        "items": [{"purchase_item_id": item_id, "quantity": 100}],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["status"] == "received"

    # Verify inventory updated
    r = client.get("/api/v1/inventory/stock", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["items"][0]["current_stock"] == 100

    # Supplier performance
    r = client.get(f"/api/v1/purchases/suppliers/{supplier_id}/performance",
                   headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["total_orders"] >= 1
