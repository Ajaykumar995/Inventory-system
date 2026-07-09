from datetime import date, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale, SaleItem, SaleStatus


class PredictionRepository:
    """Aggregates sales + inventory data for demand forecasting."""

    DEFAULT_LEAD_TIME_DAYS = 7

    def __init__(self, db: Session) -> None:
        self.db = db

    def sales_velocity(self, days: int) -> list[dict]:
        since = date.today() - timedelta(days=days)

        stmt = (
            select(
                SaleItem.product_id,
                func.coalesce(func.sum(SaleItem.quantity), 0).label("units_sold"),
            )
            .join(Sale, SaleItem.sale_id == Sale.id)
            .where(and_(Sale.status == SaleStatus.COMPLETED.value, Sale.sale_date >= since))
            .group_by(SaleItem.product_id)
        )
        rows = self.db.execute(stmt).all()
        velocity_map = {int(r.product_id): int(r.units_sold) for r in rows}

        inv_stmt = select(Inventory).options(joinedload(Inventory.product).joinedload(Product.category))
        inventories = list(self.db.execute(inv_stmt).unique().scalars().all())

        results = []
        for inv in inventories:
            units_sold = velocity_map.get(inv.product_id, 0)
            daily = round(units_sold / max(days, 1), 2)
            monthly = int(round(daily * 30))
            results.append({
                "product_id": inv.product_id,
                "product_name": inv.product.name,
                "sku": inv.product.sku,
                "category": inv.product.category.name if inv.product.category else "",
                "current_stock": inv.current_stock,
                "units_sold": units_sold,
                "daily_velocity": daily,
                "monthly_forecast": monthly,
                "min_stock": inv.min_stock,
                "max_stock": inv.max_stock,
            })

        return results

    def classify_velocity(self, items: list[dict], days: int) -> list[dict]:
        if not items:
            return []

        velocities = [i["daily_velocity"] for i in items]
        avg_vel = sum(velocities) / len(velocities) if velocities else 0
        fast_threshold = max(avg_vel * 1.5, 0.1)
        slow_threshold = max(avg_vel * 0.3, 0.01)

        for item in items:
            v = item["daily_velocity"]
            if v >= fast_threshold and v > 0:
                item["classification"] = "fast_moving"
            elif v <= slow_threshold or (v == 0 and item["current_stock"] > 0):
                item["classification"] = "slow_moving"
            else:
                item["classification"] = "normal"

        # With few products, ensure clear fast/slow labels when velocity gap is large
        if len(items) >= 2:
            sold_items = [i for i in items if i["units_sold"] > 0]
            if len(sold_items) >= 2:
                sold_items.sort(key=lambda x: x["daily_velocity"], reverse=True)
                if sold_items[0]["daily_velocity"] >= sold_items[-1]["daily_velocity"] * 2:
                    sold_items[0]["classification"] = "fast_moving"
                    sold_items[-1]["classification"] = "slow_moving"

        return items

    def reorder_recommendations(self, items: list[dict], lead_time_days: int) -> list[dict]:
        recs = []
        for item in items:
            daily = item["daily_velocity"]
            current = item["current_stock"]
            min_s = item["min_stock"]
            max_s = item["max_stock"]

            reorder_point = int(daily * lead_time_days + min_s)
            days_left = round(current / daily, 1) if daily > 0 else None

            if current <= 0:
                priority, reason = "critical", "Out of stock"
                recommended = max_s - current
            elif current <= reorder_point:
                priority = "high" if current <= min_s else "medium"
                reason = f"Stock below reorder point ({reorder_point})"
                recommended = max(0, max_s - current)
            elif daily > 0 and days_left is not None and days_left <= lead_time_days:
                priority, reason = "medium", f"Only {days_left} days of stock left"
                recommended = max(0, int(daily * 30 + min_s - current))
            else:
                continue

            if recommended > 0:
                recs.append({
                    **item,
                    "avg_daily_sales": daily,
                    "days_of_stock_left": days_left,
                    "recommended_qty": recommended,
                    "priority": priority,
                    "reason": reason,
                })

        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recs.sort(key=lambda x: priority_order.get(x["priority"], 9))
        return recs

    def next_month_forecast(self, items: list[dict]) -> list[dict]:
        forecasts = []
        for item in items:
            demand = item["monthly_forecast"]
            current = item["current_stock"]
            projected = current - demand
            min_s = item["min_stock"]
            max_s = item["max_stock"]
            shortfall = max(0, min_s - projected)

            if projected < min_s:
                status = "reorder_needed"
            elif projected > max_s:
                status = "overstock_risk"
            else:
                status = "sufficient"

            forecasts.append({
                "product_id": item["product_id"],
                "product_name": item["product_name"],
                "sku": item["sku"],
                "current_stock": current,
                "predicted_demand": demand,
                "projected_stock": projected,
                "shortfall": shortfall,
                "status": status,
            })

        forecasts.sort(key=lambda x: x["shortfall"], reverse=True)
        return forecasts
