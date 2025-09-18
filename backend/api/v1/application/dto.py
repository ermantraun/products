from pydantic import BaseModel, conint

class AddItemRequest(BaseModel):
    product_id: int
    quantity: conint(ge=1)