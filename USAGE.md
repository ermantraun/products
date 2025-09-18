1) Установите зависимости:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2) Запустите:
   uvicorn backend.api.v1.main:app --reload

3) Добавить товар в заказ:
   POST http://127.0.0.1:8000/orders/{order_id}/items
   body:
     {
       "product_id": 1,
       "quantity": 2
     }