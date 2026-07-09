def _register_and_login(client, *, username: str, email: str, role_name: str):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": "securepass123",
            "full_name": username.title(),
            "role_name": role_name,
        },
    )
    login = client.post("/api/v1/auth/login", json={"username": username, "password": "securepass123"})
    return login.json()["access_token"]


def test_category_crud_with_rbac(client):
    # First user becomes admin
    admin_token = _register_and_login(client, username="admin", email="admin@x.com", role_name="employee")
    emp_token = _register_and_login(client, username="emp", email="emp@x.com", role_name="employee")

    # Employee cannot create category
    r = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Medicines"},
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert r.status_code == 403

    # Admin can create category
    r = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Medicines", "description": "All medicines"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 201
    cat_id = r.json()["id"]

    # Anyone authenticated can list
    r = client.get("/api/v1/catalog/categories", headers={"Authorization": f"Bearer {emp_token}"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1

    # Admin update
    r = client.put(
        f"/api/v1/catalog/categories/{cat_id}",
        json={"description": "Medicines & health products"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200


def test_product_create_and_search(client):
    admin_token = _register_and_login(client, username="admin", email="admin2@x.com", role_name="employee")

    # Create category
    cat = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Grocery"},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()

    # Create product
    r = client.post(
        "/api/v1/catalog/products",
        json={
            "name": "Rice 5kg",
            "sku": "RICE-5KG",
            "barcode": "1234567890123",
            "brand": "Acme",
            "category_id": cat["id"],
            "unit": "bag",
            "cost_price": 250,
            "selling_price": 299,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 201

    # Search by sku
    r = client.get(
        "/api/v1/catalog/products?q=rice-5kg",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["total"] == 1

