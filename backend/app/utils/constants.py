from enum import Enum


class UserRole(str, Enum):
    """System roles with distinct business responsibilities."""

    ADMIN = "admin"
    INVENTORY_MANAGER = "inventory_manager"
    STORE_MANAGER = "store_manager"
    EMPLOYEE = "employee"
    SUPPLIER = "supplier"


# Role hierarchy: higher index = more privileges for authorization checks
ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.SUPPLIER: 1,
    UserRole.EMPLOYEE: 2,
    UserRole.STORE_MANAGER: 3,
    UserRole.INVENTORY_MANAGER: 4,
    UserRole.ADMIN: 5,
}

DEFAULT_ROLES: list[dict[str, str]] = [
    {
        "name": UserRole.ADMIN.value,
        "description": "Full system access, user management, and configuration",
    },
    {
        "name": UserRole.INVENTORY_MANAGER.value,
        "description": "Manages stock levels, purchase orders, and supplier relations",
    },
    {
        "name": UserRole.STORE_MANAGER.value,
        "description": "Oversees store operations, sales, and staff",
    },
    {
        "name": UserRole.EMPLOYEE.value,
        "description": "Records sales, receives stock, and updates inventory",
    },
    {
        "name": UserRole.SUPPLIER.value,
        "description": "Views purchase orders and delivery schedules",
    },
]
