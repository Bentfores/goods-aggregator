from typing import List

import tempfile, os, requests, asyncio

from app.models.supplier import SupplierInfo, Product

from app.parser.parser import parse_alibaba_image
from app.message.message import message

parse_lock = asyncio.Lock()

async def start_parsing_with_lock(products: List[Product]):
    async with parse_lock:
        parse_suppliers(products)


def download_image_to_temp(image_url: str) -> str:
    response = requests.get(image_url)
    response.raise_for_status()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_file.write(response.content)
    temp_file.close()
    return temp_file.name


def parse_suppliers(products: List[Product]):
    print("Parsing suppliers has started...")
    result: List[SupplierInfo] = []

    for product in products:
        try:
            image_path = download_image_to_temp(product.imageUrl)
            parsed_items = parse_alibaba_image(image_path)
            os.remove(image_path)

            for index, item in enumerate(parsed_items):
                print(item)
                supplier_info = SupplierInfo(
                    article=product.article,
                    name=product.name,
                    profitPlace=product.profitPlace,
                    imageUrl=product.imageUrl,
                    rating=float(item.get("rating") or 0),
                    years=item.get("years"),
                    price=float(item.get("price") or 0),
                    minOrder=item.get("min_quantity"),
                    supplierName=item.get("supplier_name"),
                    supplierUrl=item.get("supplier_url"),
                    supplierImageUrl=item.get("image"),
                    supplierProductUrl=item.get("url")
                )
                result.append(supplier_info)

        except Exception as e:
            print(f"Ошибка при парсинге {product.article}: {e}")
            continue
    send_results_to_management_module(result)


def send_message(product_url: str):
    print(f"Sending message to: {product_url}")
    message(product_url)
    return {"status": "sent", "productUrl": product_url}


def send_results_to_management_module(suppliers: List[SupplierInfo]):
    url = "http://localhost:8085/analysis/suppliers/parsed"
    payload = [supplier.model_dump() for supplier in suppliers]
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Результаты успешно отправлены")
    else:
        print(f"Ошибка при отправке: {response.status_code} - {response.text}")
