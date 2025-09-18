from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.api.v1.application.dto import AddItemRequest
from backend.api.v1.application.exceptions import OrderNotFound, ProductNotFound, NotEnoughStock
from backend.api.v1.ioc import get_add_to_order_service

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderItemResponse(BaseModel):
    id: int | None
    order_id: int
    product_id: int
    quantity: int
    price: float

@router.post("/{order_id}/items", response_model=OrderItemResponse)
def add_item(order_id: int, req: AddItemRequest, service = Depends(get_add_to_order_service)):
    try:
        item = service.execute(order_id=order_id, product_id=req.product_id, quantity=req.quantity)
        return OrderItemResponse(
            id=item.id,
            order_id=item.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=float(item.price),
        )
    except OrderNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    except ProductNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    except NotEnoughStock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")