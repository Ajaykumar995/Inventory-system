from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import Inventory, MovementType, StockMovement
from app.repository.catalog_repository import CatalogRepository
from app.repository.inventory_repository import InventoryRepository
from app.schemas.inventory import (
    DashboardStats,
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    StockAdjustment,
    StockIssue,
    StockMovementResponse,
    StockReceive,
)


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = InventoryRepository(db)
        self.catalog = CatalogRepository(db)

    def _to_response(self, inv: Inventory) -> InventoryResponse:
        data = InventoryResponse.model_validate(inv)
        data.stock_status = inv.stock_status
        return data

    def setup_inventory(self, body: InventoryCreate) -> InventoryResponse:
        product = self.catalog.get_product(body.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if self.repo.get_by_product(body.product_id):
            raise HTTPException(status_code=409, detail="Inventory already exists for this product")

        inv = Inventory(
            product_id=body.product_id,
            current_stock=body.current_stock,
            min_stock=body.min_stock,
            max_stock=body.max_stock,
            location=body.location,
        )
        created = self.repo.create(inv)
        return self._to_response(created)

    def list_inventory(self, *, q: str | None, status: str | None, page: int, page_size: int) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_inventory(q=q, status=status, skip=skip, limit=page_size)
        return {
            "items": [self._to_response(i) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def update_thresholds(self, product_id: int, body: InventoryUpdate) -> InventoryResponse:
        inv = self.repo.get_by_product(product_id)
        if inv is None:
            raise HTTPException(status_code=404, detail="Inventory not found")
        if body.min_stock is not None:
            inv.min_stock = body.min_stock
        if body.max_stock is not None:
            inv.max_stock = body.max_stock
        if body.location is not None:
            inv.location = body.location
        updated = self.repo.save(inv)
        return self._to_response(updated)

    def _apply_movement(
        self, inv: Inventory, movement_type: str, quantity: int, reason: str, reference: str | None, user_id: int
    ) -> InventoryResponse:
        prev = inv.current_stock
        if movement_type == MovementType.OUT.value:
            new_qty = prev - quantity
        elif movement_type == MovementType.ADJUSTMENT.value:
            new_qty = prev + quantity
        else:
            new_qty = prev + quantity

        if new_qty < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        inv.current_stock = new_qty
        self.repo.save(inv)
        self.repo.add_movement(
            StockMovement(
                product_id=inv.product_id,
                movement_type=movement_type,
                quantity=quantity,
                previous_qty=prev,
                new_qty=new_qty,
                reason=reason,
                reference=reference,
                created_by=user_id,
            )
        )
        return self._to_response(inv)

    def receive_stock(self, product_id: int, body: StockReceive, user_id: int) -> InventoryResponse:
        inv = self.repo.get_by_product(product_id)
        if inv is None:
            raise HTTPException(status_code=404, detail="Inventory not found")
        return self._apply_movement(inv, MovementType.IN.value, body.quantity, body.reason, body.reference, user_id)

    def issue_stock(self, product_id: int, body: StockIssue, user_id: int) -> InventoryResponse:
        inv = self.repo.get_by_product(product_id)
        if inv is None:
            raise HTTPException(status_code=404, detail="Inventory not found")
        return self._apply_movement(inv, MovementType.OUT.value, body.quantity, body.reason, body.reference, user_id)

    def adjust_stock(self, product_id: int, body: StockAdjustment, user_id: int) -> InventoryResponse:
        inv = self.repo.get_by_product(product_id)
        if inv is None:
            raise HTTPException(status_code=404, detail="Inventory not found")
        return self._apply_movement(
            inv, MovementType.ADJUSTMENT.value, body.quantity, body.reason, body.reference, user_id
        )

    def list_movements(self, product_id: int | None, page: int, page_size: int) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_movements(product_id, skip, limit=page_size)
        return {
            "items": [StockMovementResponse.model_validate(m) for m in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def dashboard(self) -> DashboardStats:
        return DashboardStats(**self.repo.dashboard_stats())
