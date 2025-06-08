from app.domain.product import Product
from app import db

class ProductRepository:
    def save_product(self, product):
        db.session.add(product)
        db.session.commit()
        return product

    def find_product_by_id(self, product_id):
        return Product.query.get(product_id)

    def find_all_products(self):
        return Product.query.all()