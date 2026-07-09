def _token(client, username, email):
    client.post("/api/v1/auth/register", json={
        "email": email, "username": username, "password": "securepass123",
        "full_name": username.title(), "role_name": "employee",
    })
    return client.post("/api/v1/auth/login", json={"username": username, "password": "securepass123"}).json()["access_token"]


def _category_and_product(client, token):
    cat = client.post("/api/v1/catalog/categories", json={"name": "Pharma"},
                      headers={"Authorization": f"Bearer {token}"}).json()
    prod = client.post("/api/v1/catalog/products", json={
        "name": "Paracetamol", "sku": "PARA-500", "category_id": cat["id"],
        "cost_price": 10, "selling_price": 15,
    }, headers={"Authorization": f"Bearer {token}"}).json()
    return prod


def test_inventory_setup_and_movements(client):
    token = _token(client, "invadmin", "inv@x.com")
    prod = _category_and_product(client, token)

    r = client.post("/api/v1/inventory/setup", json={
        "product_id": prod["id"], "current_stock": 50, "min_stock": 20, "max_stock": 200,
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    assert r.json()["stock_status"] == "healthy"

    r = client.post(f"/api/v1/inventory/stock/{prod['id']}/issue", json={
        "quantity": 35, "reason": "Sales",
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["stock_status"] == "low_stock"

    r = client.get("/api/v1/inventory/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["low_stock"] >= 1
