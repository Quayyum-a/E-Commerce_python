from typing import List, Dict, Any
from app.domain.product import Product
from app.dtos.responses.product_responses import ProductResponse, ProductListResponse, ProductMessageResponse
from app.dtos.requests.product_requests import ProductCreateRequest, ProductUpdateRequest

class ProductMapper:
    
    @staticmethod
    def to_response(product: Product) -> ProductResponse:
        return ProductResponse.model_validate(product)
    
    @staticmethod
    def to_list_response(products: List[Product], total: int) -> ProductListResponse:
        return ProductListResponse(
            products=[ProductMapper.to_response(p) for p in products],
            total=total
        )
    
    @staticmethod
    def to_message_response(message: str, product_id: int = None) -> ProductMessageResponse:

        return ProductMessageResponse(message=message, product_id=product_id)
    
    @staticmethod
    def create_to_entity(create_dto: ProductCreateRequest) -> Dict[str, Any]:
        return create_dto.model_dump()
    
    @staticmethod
    def update_to_entity(update_dto: ProductUpdateRequest) -> Dict[str, Any]:
        return {k: v for k, v in update_dto.model_dump().items() if v is not None}