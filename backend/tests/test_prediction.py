from datetime import date, timedelta


def _token(client, username, email):
    client.post("/api/v1/auth/register", json={
        "email": email, "username": username, "password": "securepass123",
        "full_name": username.title(), "role_name": "employee",
    })
    return client.post("/api/v1/auth/login", json={"username": username, "password": "securepass123"}).json()["access_token"]


def _setup_with_sales(client, token):
    cat = client.post("/api/v1/catalog/categories", json={"name": "FastCat"},
                      headers={"Authorization": f"Bearer {token}"}).json()
    fast_prod = client.post("/api/v1/catalog/products", json={
        "name": "Fast Seller", "sku": "FAST-01", "category_id": cat["id"], "selling_price": 100,
    }, headers={"Authorization": f"Bearer {token}"}).json()
    slow_prod = client.post("/api/v1/catalog/products", json={
        "name": "Slow Mover", "sku": "SLOW-01", "category_id": cat["id"], "selling_price": 50,
    }, headers={"Authorization": f"Bearer {token}"}).json()

    for pid, stock in [(fast_prod["id"], 20), (slow_prod["id"], 100)]:
        client.post("/api/v1/inventory/setup", json={
            "product_id": pid, "current_stock": stock, "min_stock": 10, "max_stock": 200,
        }, headers={"Authorization": f"Bearer {token}"})

    # Fast product: many sales
    for _ in range(5):
        client.post("/api/v1/sales", json={
            "items": [{"product_id": fast_prod["id"], "quantity": 3}],
        }, headers={"Authorization": f"Bearer {token}"})

    # Slow product: one sale
    client.post("/api/v1/sales", json={
        "items": [{"product_id": slow_prod["id"], "quantity": 1}],
    }, headers={"Authorization": f"Bearer {token}"})

    return fast_prod, slow_prod


def test_prediction_fast_and_slow_movers(client):
    token = _token(client, "preduser", "pred@x.com")
    fast_prod, slow_prod = _setup_with_sales(client, token)

    r = client.get("/api/v1/prediction/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["fast_moving_count"] >= 1
    assert data["slow_moving_count"] >= 1

    fast_skus = [p["sku"] for p in data["fast_movers"]]
    assert "FAST-01" in fast_skus

    r = client.get("/api/v1/prediction/reorder", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    # Fast seller sold 15 units from stock 20, should have reorder or forecast data
    assert isinstance(r.json(), list)

    r = client.get("/api/v1/prediction/next-month", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1
