from app.domain.product import Product
     from app.infrastructure.product_repository import ProductRepository

     class ProductService:
         def __init__(self):
             self.product_repo = ProductRepository()

         def create_product(self, name, price, stock):
             product = Product(name=name, price=price, stock=stock)
             return self.product_repo.save_product(product)

         def get_products(self):
             return self.product_repo.find_all_products()

         def update_product(self, product_id, name, price, stock):
             product = self.product_repo.find_product_by_id(product_id)
             if not product:
                 raise ValueError("Product not found")
             product.name = name
             product.price = price
             product.stock = stock
             return self.product_repo.save_product(product)