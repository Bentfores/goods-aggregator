from fastapi import APIRouter, Query, Response, status, BackgroundTasks
from typing import List

from app.models.supplier import SupplierInfo, Product
from app.services.supplier_parser import start_parsing_with_lock, send_message

router = APIRouter()


@router.post("/suppliers", response_model=List[SupplierInfo])
def get_suppliers_info(products: List[Product], background_tasks: BackgroundTasks):
    background_tasks.add_task(start_parsing_with_lock, products=products)
    return Response(status_code=status.HTTP_200_OK)


@router.post("/message")
def post_send_message(productUrl: str = Query(...)):
    return send_message(productUrl)
