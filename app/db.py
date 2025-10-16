"""
MongoDB database connection and configuration.

This module handles the connection to MongoDB using PyMongo
and provides database instance access for the application.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages MongoDB connection and database operations."""
    
    def __init__(self):
        self.client = None  # AsyncIOMotorClient instance
        self.database = None  # Database instance
    
    async def connect_to_database(self):
        """Establish connection to MongoDB."""
        try:
            # MongoDB connection string - use environment variable or default
            mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            database_name = os.getenv("DATABASE_NAME", "recommendation_db")
            
            # Create MongoDB client
            self.client = AsyncIOMotorClient(mongo_url)
            
            # Test the connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Get database instance
            self.database = self.client[database_name]
            
        except ServerSelectionTimeoutError:
            logger.error("Failed to connect to MongoDB. Please ensure MongoDB is running.")
            raise
        except Exception as e:
            logger.error(f"An error occurred while connecting to MongoDB: {e}")
            raise
    
    async def close_database_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")
    
    def get_database(self):
        """Get the database instance."""
        return self.database

# Global database manager instance
db_manager = DatabaseManager()

async def connect_to_mongo():
    """Connect to MongoDB - called during application startup."""
    await db_manager.connect_to_database()

async def close_mongo_connection():
    """Close MongoDB connection - called during application shutdown."""
    await db_manager.close_database_connection()

def get_database():
    """Get the database instance for use in route handlers."""
    return db_manager.get_database()

# Collection names
RECOMMENDATIONS_COLLECTION = "recommendations"
USERS_COLLECTION = "users"
PRODUCTS_COLLECTION = "products"

# Database CRUD Operations for Recommendations
class RecommendationCRUD:
    """
    CRUD operations for the recommendations collection.
    Provides async database operations with proper error handling.
    """
    
    def __init__(self, database):
        """
        Initialize CRUD operations with database instance.
        
        Args:
            database: MongoDB database instance
        """
        self.db = database
        self.collection = database[RECOMMENDATIONS_COLLECTION]
    
    async def create_recommendation(self, data: dict) -> str:
        """
        Create a new recommendation in the database.
        
        Args:
            data (dict): Recommendation data containing product_id, score, reason, etc.
            
        Returns:
            str: The ID of the created recommendation
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Creating new recommendation for product: {data.get('product_id')}")
            
            # Insert the recommendation document
            result = await self.collection.insert_one(data)
            
            if result.inserted_id:
                logger.info(f"Successfully created recommendation with ID: {result.inserted_id}")
                return str(result.inserted_id)
            else:
                raise Exception("Failed to insert recommendation - no ID returned")
                
        except Exception as e:
            logger.error(f"Error creating recommendation: {e}")
            raise Exception(f"Database error while creating recommendation: {e}")
    
    async def get_all_recommendations(self, limit: int = 50, skip: int = 0, category: str = None) -> list:
        """
        Retrieve all recommendations with optional filtering and pagination.
        
        Args:
            limit (int): Maximum number of recommendations to return
            skip (int): Number of recommendations to skip (for pagination)
            category (str, optional): Filter by product category
            
        Returns:
            list: List of recommendation documents
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Fetching recommendations - limit: {limit}, skip: {skip}, category: {category}")
            
            # Build query filter
            query_filter = {}
            if category:
                query_filter["category"] = category
            
            # Execute query with sorting (highest score first) and pagination
            cursor = (self.collection
                     .find(query_filter)
                     .sort("score", -1)  # Sort by score descending
                     .skip(skip)
                     .limit(limit))
            
            # Convert cursor to list
            recommendations = await cursor.to_list(length=limit)
            
            logger.info(f"Retrieved {len(recommendations)} recommendations from database")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching all recommendations: {e}")
            raise Exception(f"Database error while fetching recommendations: {e}")
    
    async def get_recommendation_by_product(self, product_id: str, limit: int = 10) -> list:
        """
        Get recommendations for a specific product (related products).
        
        Args:
            product_id (str): The product ID to find recommendations for
            limit (int): Maximum number of recommendations to return
            
        Returns:
            list: List of recommendation documents for the specified product
            
        Raises:
            Exception: If database operation fails or product not found
        """
        try:
            logger.info(f"Fetching recommendations for product: {product_id}")
            
            # Query for recommendations where this product is the target
            query_filter = {"target_product_id": product_id}
            
            # Execute query sorted by score
            cursor = (self.collection
                     .find(query_filter)
                     .sort("score", -1)
                     .limit(limit))
            
            recommendations = await cursor.to_list(length=limit)
            
            if not recommendations:
                logger.warning(f"No recommendations found for product: {product_id}")
                # Return empty list instead of raising exception for not found
                return []
            
            logger.info(f"Found {len(recommendations)} recommendations for product: {product_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching recommendations for product {product_id}: {e}")
            raise Exception(f"Database error while fetching product recommendations: {e}")
    
    async def get_recommendation_by_id(self, recommendation_id: str) -> dict:
        """
        Get a specific recommendation by its ID.
        
        Args:
            recommendation_id (str): The recommendation ID to fetch
            
        Returns:
            dict: The recommendation document
            
        Raises:
            Exception: If recommendation not found or database error occurs
        """
        try:
            from bson import ObjectId
            
            logger.info(f"Fetching recommendation by ID: {recommendation_id}")
            
            # Validate ObjectId format
            try:
                obj_id = ObjectId(recommendation_id)
            except Exception:
                raise Exception(f"Invalid recommendation ID format: {recommendation_id}")
            
            # Find the recommendation
            recommendation = await self.collection.find_one({"_id": obj_id})
            
            if not recommendation:
                raise Exception(f"Recommendation not found with ID: {recommendation_id}")
            
            logger.info(f"Successfully retrieved recommendation: {recommendation_id}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error fetching recommendation by ID {recommendation_id}: {e}")
            raise
    
    async def update_recommendation(self, recommendation_id: str, update_data: dict) -> bool:
        """
        Update an existing recommendation.
        
        Args:
            recommendation_id (str): The ID of the recommendation to update
            update_data (dict): The data to update
            
        Returns:
            bool: True if update was successful
            
        Raises:
            Exception: If recommendation not found or database error occurs
        """
        try:
            from bson import ObjectId
            from datetime import datetime
            
            logger.info(f"Updating recommendation: {recommendation_id}")
            
            # Validate ObjectId format
            try:
                obj_id = ObjectId(recommendation_id)
            except Exception:
                raise Exception(f"Invalid recommendation ID format: {recommendation_id}")
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update the recommendation
            result = await self.collection.update_one(
                {"_id": obj_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise Exception(f"Recommendation not found with ID: {recommendation_id}")
            
            logger.info(f"Successfully updated recommendation: {recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating recommendation {recommendation_id}: {e}")
            raise
    
    async def delete_recommendation(self, recommendation_id: str) -> bool:
        """
        Delete a recommendation by ID.
        
        Args:
            recommendation_id (str): The ID of the recommendation to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            Exception: If recommendation not found or database error occurs
        """
        try:
            from bson import ObjectId
            
            logger.info(f"Deleting recommendation: {recommendation_id}")
            
            # Validate ObjectId format
            try:
                obj_id = ObjectId(recommendation_id)
            except Exception:
                raise Exception(f"Invalid recommendation ID format: {recommendation_id}")
            
            # Delete the recommendation
            result = await self.collection.delete_one({"_id": obj_id})
            
            if result.deleted_count == 0:
                raise Exception(f"Recommendation not found with ID: {recommendation_id}")
            
            logger.info(f"Successfully deleted recommendation: {recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting recommendation {recommendation_id}: {e}")
            raise
    
    async def get_general_recommendations(self, limit: int = 10, category: str = None) -> list:
        """
        Get general recommendations (not tied to a specific product).
        
        Args:
            limit (int): Maximum number of recommendations to return
            category (str, optional): Filter by product category
            
        Returns:
            list: List of general recommendation documents
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Fetching general recommendations - limit: {limit}, category: {category}")
            
            # Build query for general recommendations
            query_filter = {"type": "general"}
            if category:
                query_filter["category"] = category
            
            # Execute query sorted by score
            cursor = (self.collection
                     .find(query_filter)
                     .sort("score", -1)
                     .limit(limit))
            
            recommendations = await cursor.to_list(length=limit)
            
            logger.info(f"Retrieved {len(recommendations)} general recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching general recommendations: {e}")
            raise Exception(f"Database error while fetching general recommendations: {e}")

# Product CRUD Operations
class ProductCRUD:
    """
    CRUD operations for the products collection.
    Provides async database operations for product management.
    """
    
    def __init__(self, database):
        """
        Initialize Product CRUD operations with database instance.
        
        Args:
            database: MongoDB database instance
        """
        self.db = database
        self.collection = database[PRODUCTS_COLLECTION]
    
    async def get_product_by_id(self, product_id: str) -> dict:
        """
        Get a product by its ID.
        
        Args:
            product_id (str): The product ID to fetch
            
        Returns:
            dict: The product document
            
        Raises:
            Exception: If product not found or database error occurs
        """
        try:
            from bson import ObjectId
            
            logger.info(f"Fetching product by ID: {product_id}")
            
            # Validate ObjectId format
            try:
                obj_id = ObjectId(product_id)
            except Exception:
                raise Exception(f"Invalid product ID format: {product_id}")
            
            # Find the product
            product = await self.collection.find_one({"_id": obj_id})
            
            if not product:
                raise Exception(f"Product not found with ID: {product_id}")
            
            logger.info(f"Successfully retrieved product: {product['name']}")
            return product
            
        except Exception as e:
            logger.error(f"Error fetching product by ID {product_id}: {e}")
            raise
    
    async def get_products_by_category(self, category: str, limit: int = 20) -> list:
        """
        Get products by category.
        
        Args:
            category (str): The product category to filter by
            limit (int): Maximum number of products to return
            
        Returns:
            list: List of product documents in the specified category
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Fetching products by category: {category}")
            
            cursor = (self.collection
                     .find({"category": category})
                     .limit(limit))
            
            products = await cursor.to_list(length=limit)
            
            logger.info(f"Retrieved {len(products)} products in category: {category}")
            return products
            
        except Exception as e:
            logger.error(f"Error fetching products by category {category}: {e}")
            raise Exception(f"Database error while fetching products by category: {e}")

# Factory functions to get CRUD instances
def get_recommendation_crud() -> RecommendationCRUD:
    """
    Get a CRUD operations instance for recommendations.
    
    Returns:
        RecommendationCRUD: Instance for database operations
        
    Raises:
        Exception: If database is not connected
    """
    database = get_database()
    if not database:
        raise Exception("Database not connected. Ensure MongoDB connection is established.")
    
    return RecommendationCRUD(database)

def get_product_crud() -> ProductCRUD:
    """
    Get a CRUD operations instance for products.
    
    Returns:
        ProductCRUD: Instance for database operations
        
    Raises:
        Exception: If database is not connected
    """
    database = get_database()
    if not database:
        raise Exception("Database not connected. Ensure MongoDB connection is established.")
    
    return ProductCRUD(database)