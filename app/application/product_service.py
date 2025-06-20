from typing import List, Optional

from app.domain.product import Product
from app.dtos.exceptions import NotFoundException, ValidationException
from app.infrastructure.product_repository import ProductRepository


class ProductService:
    def __init__(self, product_repo: Optional[ProductRepository] = None):
        self.product_repo = product_repo or ProductRepository()

    def create_product(self, **product_data) -> Product:
        try:
            product = Product(**product_data)
            return self.product_repo.save_product(product)
        except Exception as e:
            raise ValidationException(f"Failed to create product: {str(e)}")

    def get_products(self) -> List[Product]:
        return self.product_repo.find_all_products()

    def get_product_by_id(self, product_id: int) -> Product:
        product = self.product_repo.find_product_by_id(product_id)
        if not product:
            raise NotFoundException("Product")
        return product

    def update_product(self, product_id: int, **update_data) -> Product:
        product = self.get_product_by_id(product_id)
        
        try:
            for key, value in update_data.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            return self.product_repo.save_product(product)
        except Exception as e:
            raise ValidationException(f"Failed to update product: {str(e)}")
    
    def delete_product(self, product_id: int) -> bool:
        product = self.get_product_by_id(product_id)
        return self.product_repo.delete_product(product)