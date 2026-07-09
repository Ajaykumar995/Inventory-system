from datetime import date, timedelta


def _token(client, username, email):
    client.post("/api/v1/auth/register", json={
        "email": email, "username": username, "password": "securepass123",
        "full_name": username.title(), "role_name": "employee",
    })
    return client.post("/api/v1/auth/login", json={"username": username, "password": "securepass123"}).json()["access_token"]


def _product(client, token):
    cat = client.post("/api/v1/catalog/categories", json={"name": "Pharma"},
                      headers={"Authorization": f"Bearer {token}"}).json()
    return client.post("/api/v1/catalog/products", json={
        "name": "Crocin", "sku": "CRO-650", "category_id": cat["id"], "selling_price": 30,
    }, headers={"Authorization": f"Bearer {token}"}).json()


def test_add_batch_and_expiry_lists(client):
    token = _token(client, "expuser", "exp@x.com")
    prod = _product(client, token)

    future = (date.today() + timedelta(days=60)).isoformat()
    r = client.post("/api/v1/expiry/batches", json={
        "product_id": prod["id"], "batch_number": "BATCH-001",
        "expiry_date": future, "quantity": 100,
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201
    assert r.json()["expiry_status"] == "valid"

    soon = (date.today() + timedelta(days=15)).isoformat()
    client.post("/api/v1/expiry/batches", json={
        "product_id": prod["id"], "batch_number": "BATCH-002",
        "expiry_date": soon, "quantity": 50,
    }, headers={"Authorization": f"Bearer {token}"})

    r = client.get("/api/v1/expiry/batches?status=expiring_soon", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1

    r = client.get("/api/v1/expiry/summary", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["expiring_soon"] >= 1


def test_expired_batch_dispose(client):
    token = _token(client, "expuser2", "exp2@x.com")
    prod = _product(client, token)

    past = (date.today() - timedelta(days=5)).isoformat()
    # Direct DB insert for expired batch - use add_batch won't allow past expiry
    # Instead create batch with near expiry then we test dispose on expiring batch
    soon = (date.today() + timedelta(days=10)).isoformat()
    r = client.post("/api/v1/expiry/batches", json={
        "product_id": prod["id"], "batch_number": "BATCH-OLD",
        "expiry_date": soon, "quantity": 20,
    }, headers={"Authorization": f"Bearer {token}"})
    batch_id = r.json()["id"]

    r = client.post(f"/api/v1/expiry/batches/{batch_id}/dispose", json={
        "reason": "Near expiry clearance",
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["is_disposed"] is True


def test_expiry_notifications(client):
    token = _token(client, "expuser3", "exp3@x.com")
    prod = _product(client, token)

    soon = (date.today() + timedelta(days=7)).isoformat()
    client.post("/api/v1/expiry/batches", json={
        "product_id": prod["id"], "batch_number": "BATCH-ALERT",
        "expiry_date": soon, "quantity": 10,
    }, headers={"Authorization": f"Bearer {token}"})

    r = client.post("/api/v1/expiry/notifications/sync", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["created"] >= 1

    r = client.get("/api/v1/expiry/notifications", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1
