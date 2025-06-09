from typing import List, Optional
from app.domain.product import Product
from app import db

class ProductRepository:
    """Repository class for handling database operations for Products."""
    
    def save_product(self, product: Product) -> Product:
        """
        Save a product to the database.
        
        Args:
            product: The Product instance to save
            
        Returns:
            Product: The saved product
        """
        db.session.add(product)
        db.session.commit()
        return product

    def find_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Find a product by its ID.
        
        Args:
            product_id: The ID of the product to find
            
        Returns:
            Optional[Product]: The found product, or None if not found
        """
        return Product.query.get(product_id)

    def find_all_products(self) -> List[Product]:
        """
        Retrieve all products from the database.
        
        Returns:
            List[Product]: A list of all products
        """
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