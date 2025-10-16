"""
Sample data creation script for testing the Recommendation API.

This script creates sample products and recommendations in MongoDB
for testing the API endpoints.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Sample data
SAMPLE_PRODUCTS = [
    {
        "name": "iPhone 15 Pro",
        "category": "electronics", 
        "price": 999.99,
        "description": "Latest iPhone with advanced camera system",
        "rating": 4.8
    },
    {
        "name": "MacBook Air M2",
        "category": "electronics",
        "price": 1199.99, 
        "description": "Lightweight laptop with M2 chip",
        "rating": 4.7
    },
    {
        "name": "AirPods Pro",
        "category": "electronics",
        "price": 249.99,
        "description": "Wireless earbuds with noise cancellation", 
        "rating": 4.6
    },
    {
        "name": "The Great Gatsby",
        "category": "books",
        "price": 12.99,
        "description": "Classic American novel",
        "rating": 4.2
    },
    {
        "name": "Running Shoes",
        "category": "sports",
        "price": 89.99,
        "description": "Comfortable running shoes for daily training",
        "rating": 4.4
    }
]

async def create_sample_data():
    """Create sample products and recommendations."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["recommendation_db"]
    
    print("Creating sample products...")
    
    # Clear existing data
    await db["products"].delete_many({})
    await db["recommendations"].delete_many({})
    
    # Insert sample products
    product_results = await db["products"].insert_many(SAMPLE_PRODUCTS)
    product_ids = [str(pid) for pid in product_results.inserted_ids]
    
    print(f"Created {len(product_ids)} products")
    
    # Create sample recommendations
    sample_recommendations = [
        # General recommendations
        {
            "product_id": product_ids[0],  # iPhone
            "target_product_id": None,
            "score": 0.95,
            "reason": "Bestselling smartphone with excellent reviews",
            "type": "general",
            "category": "electronics",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "product_id": product_ids[1],  # MacBook
            "target_product_id": None, 
            "score": 0.90,
            "reason": "Top-rated laptop for professionals and students",
            "type": "general",
            "category": "electronics", 
            "created_at": datetime.utcnow().isoformat()
        },
        # Product-specific recommendations (for iPhone)
        {
            "product_id": product_ids[2],  # AirPods
            "target_product_id": product_ids[0],  # for iPhone
            "score": 0.88,
            "reason": "Perfect companion for your iPhone - seamless connectivity",
            "type": "specific",
            "category": "electronics",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "product_id": product_ids[1],  # MacBook
            "target_product_id": product_ids[0],  # for iPhone
            "score": 0.75,
            "reason": "Complete Apple ecosystem - works great with iPhone",
            "type": "specific", 
            "category": "electronics",
            "created_at": datetime.utcnow().isoformat()
        },
        # More general recommendations
        {
            "product_id": product_ids[3],  # Book
            "target_product_id": None,
            "score": 0.82,
            "reason": "Classic literature - highly rated by readers",
            "type": "general",
            "category": "books",
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    await db["recommendations"].insert_many(sample_recommendations)
    print(f"Created {len(sample_recommendations)} recommendations")
    
    print("\nSample data created successfully!")
    print("Product IDs for testing:")
    for i, pid in enumerate(product_ids):
        print(f"  {SAMPLE_PRODUCTS[i]['name']}: {pid}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_data())