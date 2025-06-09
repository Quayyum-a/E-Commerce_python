from typing import List, Optional
from app.domain.product import Product
from app import db

class ProductRepository:
    
    def save_product(self, product: Product) -> Product:
        db.session.add(product)
        db.session.commit()
        return product

    def find_product_by_id(self, product_id: int) -> Optional[Product]:
        return Product.query.get(product_id)

    def find_all_products(self) -> List[Product]:
        return Product.query.all()
    
    def delete_product(self, product: Product) -> bool:
        """
        Delete a product from the database.
        
        Args:
            product: The Product instance to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            db.session.delete(product)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False