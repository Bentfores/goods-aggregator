from pydantic import BaseModel


class SupplierInfo(BaseModel):
    article: str
    name: str
    profitPlace: int
    imageUrl: str
    rating: float
    years: float
    price: float
    minOrder: float
    supplierName: str
    supplierUrl: str
    supplierImageUrl: str
    supplierProductUrl: str

class Product(BaseModel):
    article: str
    name: str
    imageUrl: str
    profitPlace: int