"""
Recommendation API routes.

This module contains all API endpoints related to recommendation functionality.
Provides endpoints for retrieving recommendations and adding new ones with proper validation.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.db import (
    get_database, 
    get_recommendation_crud, 
    get_product_crud,
    RECOMMENDATIONS_COLLECTION, 
    PRODUCTS_COLLECTION
)
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

# Pydantic models for request/response validation
class ProductInfo(BaseModel):
    """Product information model for recommended products."""
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    price: float = Field(..., ge=0, description="Product price")
    description: Optional[str] = Field(default=None, description="Product description")
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Product rating")

class RecommendationResponse(BaseModel):
    """Response model for recommendation data."""
    id: str = Field(..., description="Recommendation ID")
    product: ProductInfo = Field(..., description="Recommended product information")
    score: float = Field(..., ge=0.0, le=1.0, description="Recommendation confidence score")
    reason: str = Field(..., description="Reason for recommendation")
    created_at: str = Field(..., description="Creation timestamp")

class CreateRecommendationRequest(BaseModel):
    """Request model for creating a new recommendation."""
    product_id: str = Field(..., description="Product ID to recommend")
    target_product_id: Optional[str] = Field(default=None, description="Product this recommendation is for (optional)")
    score: float = Field(..., ge=0.0, le=1.0, description="Recommendation confidence score")
    reason: str = Field(..., min_length=1, description="Reason for the recommendation")

class CreateRecommendationResponse(BaseModel):
    """Response model for created recommendation."""
    id: str = Field(..., description="Created recommendation ID")
    message: str = Field(..., description="Success message")
    recommendation: RecommendationResponse = Field(..., description="Created recommendation data")

@router.get("/recommendations", 
           response_model=List[RecommendationResponse],
           status_code=status.HTTP_200_OK,
           summary="Get list of recommended products")
async def get_recommendations(
    limit: Optional[int] = 10,
    category: Optional[str] = None
):
    """
    Returns a list of recommended products.
    
    This endpoint retrieves general product recommendations that can be shown
    to users as featured or popular products.
    
    - **limit**: Maximum number of recommendations to return (1-100, default: 10)
    - **category**: Optional category filter to get recommendations for specific product types
    - **Returns**: List of recommended products with scores and reasons (HTTP 200)
    """
    try:
        # Use CRUD operations for database access
        recommendation_crud = get_recommendation_crud()
        product_crud = get_product_crud()
        
        # Fetch general recommendations using CRUD operations
        recommendations = await recommendation_crud.get_general_recommendations(
            limit=limit, 
            category=category
        )
        
        # Convert to response format with product information
        result = []
        for rec in recommendations:
            try:
                # Get product details using CRUD operations
                product_doc = await product_crud.get_product_by_id(rec["product_id"])
                
                product_info = ProductInfo(
                    id=str(product_doc["_id"]),
                    name=product_doc["name"],
                    category=product_doc["category"],
                    price=product_doc["price"],
                    description=product_doc.get("description"),
                    rating=product_doc.get("rating")
                )
                
                result.append(RecommendationResponse(
                    id=str(rec["_id"]),
                    product=product_info,
                    score=rec["score"],
                    reason=rec["reason"],
                    created_at=rec["created_at"]
                ))
            except Exception as e:
                # Log error but continue with other recommendations
                logger.warning(f"Could not fetch product info for recommendation {rec.get('_id')}: {e}")
                continue
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching general recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error"
        )

@router.get("/recommendations/{product_id}",
           response_model=List[RecommendationResponse], 
           status_code=status.HTTP_200_OK,
           summary="Get recommendations for a specific product")
async def get_product_recommendations(product_id: str):
    """
    Returns recommendations for a specific product.
    
    This endpoint finds products that are commonly recommended together with
    the specified product (e.g., "people who viewed this also viewed").
    
    - **product_id**: The ID of the product to get recommendations for
    - **Returns**: List of recommended products related to the specified product (HTTP 200)
    - **Raises**: HTTP 404 if the product is not found
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )
        
        # First, verify the product exists - handle both integer and ObjectId formats
        try:
            # Try integer ID first (our sample data uses integer IDs)
            product_int_id = int(product_id)
            target_product = await db[PRODUCTS_COLLECTION].find_one({"_id": product_int_id})
        except ValueError:
            try:
                # Fallback to ObjectId format
                product_obj_id = ObjectId(product_id)
                target_product = await db[PRODUCTS_COLLECTION].find_one({"_id": product_obj_id})
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid product ID format"
                )
        if not target_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Find recommendations for this specific product
        query_filter = {"target_product_id": product_id}
        cursor = (db[RECOMMENDATIONS_COLLECTION]
                 .find(query_filter)
                 .sort("score", -1)  # Sort by score descending
                 .limit(10))  # Limit to top 10 recommendations
        
        recommendations = await cursor.to_list(length=10)
        
        # Convert to response format with product information
        result = []
        for rec in recommendations:
            # Get recommended product details - handle both integer and ObjectId formats
            try:
                # Try integer ID first (our sample data uses integer IDs)
                product_int_id = int(rec["product_id"])
                product_doc = await db[PRODUCTS_COLLECTION].find_one({"_id": product_int_id})
            except (ValueError, TypeError):
                try:
                    # Fallback to ObjectId format
                    product_doc = await db[PRODUCTS_COLLECTION].find_one({"_id": ObjectId(rec["product_id"])})
                except Exception:
                    product_doc = None
            
            if product_doc:
                product_info = ProductInfo(
                    id=str(product_doc["_id"]),
                    name=product_doc["name"],
                    category=product_doc["category"],
                    price=product_doc["price"],
                    description=product_doc.get("description"),
                    rating=product_doc.get("rating")
                )
                
                result.append(RecommendationResponse(
                    id=str(rec["_id"]),
                    product=product_info,
                    score=rec["score"],
                    reason=rec["reason"],
                    created_at=rec["created_at"]
                ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recommendations for product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/recommendations",
            response_model=CreateRecommendationResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Add a new recommendation")
async def create_recommendation(request: CreateRecommendationRequest):
    """
    Adds a new product recommendation to the system.
    
    This endpoint allows adding new recommendation relationships between products
    or general product recommendations with scoring and reasoning.
    
    - **request**: Recommendation data including product ID, score, and reason
    - **Returns**: Created recommendation with generated ID (HTTP 201)
    - **Raises**: HTTP 404 if the product is not found, HTTP 400 for validation errors
    """
    try:
        # Use CRUD operations for database access
        recommendation_crud = get_recommendation_crud()
        product_crud = get_product_crud()
        
        # Verify the recommended product exists using CRUD operations
        try:
            recommended_product = await product_crud.get_product_by_id(request.product_id)
        except Exception as e:
            if "not found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recommended product not found"
                )
            elif "invalid" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid product ID format"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error validating product"
                )
        
        # If target_product_id is provided, verify it exists
        if request.target_product_id:
            try:
                await product_crud.get_product_by_id(request.target_product_id)
            except Exception as e:
                if "not found" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Target product not found"
                    )
                elif "invalid" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid target product ID format"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error validating target product"
                    )
        
        # Create recommendation document
        recommendation_doc = {
            "product_id": request.product_id,
            "target_product_id": request.target_product_id,
            "score": request.score,
            "reason": request.reason,
            "type": "specific" if request.target_product_id else "general",
            "created_at": datetime.utcnow().isoformat(),
            "category": recommended_product["category"]  # Store category for filtering
        }
        
        # Create recommendation using CRUD operations
        recommendation_id = await recommendation_crud.create_recommendation(recommendation_doc)
        
        # Create product info for response
        product_info = ProductInfo(
            id=str(recommended_product["_id"]),
            name=recommended_product["name"],
            category=recommended_product["category"],
            price=recommended_product["price"],
            description=recommended_product.get("description"),
            rating=recommended_product.get("rating")
        )
        
        # Create recommendation response
        recommendation_response = RecommendationResponse(
            id=recommendation_id,
            product=product_info,
            score=recommendation_doc["score"],
            reason=recommendation_doc["reason"],
            created_at=recommendation_doc["created_at"]
        )
        
        return CreateRecommendationResponse(
            id=recommendation_id,
            message="Recommendation created successfully",
            recommendation=recommendation_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Additional utility endpoints can be added here as needed
# For example: delete recommendations, bulk operations, analytics endpoints