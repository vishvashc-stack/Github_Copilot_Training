"""
Example usage of MongoDB CRUD operations for the Recommendation Microservice.

This file demonstrates how to use the CRUD operations defined in db.py
for managing recommendations and products in MongoDB.
"""

import asyncio
from datetime import datetime
from app.db import connect_to_mongo, get_recommendation_crud, get_product_crud, close_mongo_connection

async def example_crud_operations():
    """
    Demonstrate CRUD operations for recommendations.
    This function shows how to use all the database operations.
    """
    
    print("=== MongoDB CRUD Operations Example ===\n")
    
    # Connect to MongoDB
    print("1. Connecting to MongoDB...")
    await connect_to_mongo()
    print("✅ Connected to MongoDB\n")
    
    try:
        # Get CRUD instances
        recommendation_crud = get_recommendation_crud()
        product_crud = get_product_crud()
        
        # Example 1: Create a new recommendation
        print("2. Creating a new recommendation...")
        sample_recommendation = {
            "product_id": "6708b123456789abcdef0001",  # Sample product ID
            "target_product_id": None,  # General recommendation
            "score": 0.92,
            "reason": "Highly rated product with excellent customer reviews",
            "type": "general",
            "category": "electronics",
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            recommendation_id = await recommendation_crud.create_recommendation(sample_recommendation)
            print(f"✅ Created recommendation with ID: {recommendation_id}\n")
        except Exception as e:
            print(f"❌ Error creating recommendation: {e}\n")
        
        # Example 2: Get all recommendations
        print("3. Fetching all recommendations...")
        try:
            all_recommendations = await recommendation_crud.get_all_recommendations(limit=5)
            print(f"✅ Retrieved {len(all_recommendations)} recommendations:")
            for i, rec in enumerate(all_recommendations, 1):
                print(f"   {i}. Product: {rec.get('product_id')}, Score: {rec.get('score')}")
            print()
        except Exception as e:
            print(f"❌ Error fetching recommendations: {e}\n")
        
        # Example 3: Get recommendations by product
        print("4. Fetching recommendations for a specific product...")
        try:
            sample_product_id = "6708b123456789abcdef0001"
            product_recommendations = await recommendation_crud.get_recommendation_by_product(
                sample_product_id, limit=3
            )
            
            if product_recommendations:
                print(f"✅ Found {len(product_recommendations)} recommendations for product {sample_product_id}:")
                for i, rec in enumerate(product_recommendations, 1):
                    print(f"   {i}. Recommended: {rec.get('product_id')}, Score: {rec.get('score')}")
            else:
                print(f"ℹ️  No specific recommendations found for product {sample_product_id}")
            print()
        except Exception as e:
            print(f"❌ Error fetching product recommendations: {e}\n")
        
        # Example 4: Get general recommendations
        print("5. Fetching general recommendations...")
        try:
            general_recs = await recommendation_crud.get_general_recommendations(
                limit=3, category="electronics"
            )
            print(f"✅ Retrieved {len(general_recs)} general electronics recommendations:")
            for i, rec in enumerate(general_recs, 1):
                print(f"   {i}. Product: {rec.get('product_id')}, Score: {rec.get('score')}")
            print()
        except Exception as e:
            print(f"❌ Error fetching general recommendations: {e}\n")
        
        # Example 5: Get a product by ID (if products exist)
        print("6. Fetching product information...")
        try:
            sample_product_id = "6708b123456789abcdef0001"
            product = await product_crud.get_product_by_id(sample_product_id)
            print(f"✅ Retrieved product: {product.get('name')} - ${product.get('price')}")
            print()
        except Exception as e:
            print(f"❌ Error fetching product (expected if no sample data): {e}\n")
        
        # Example 6: Update a recommendation (if we have one)
        if 'recommendation_id' in locals():
            print("7. Updating a recommendation...")
            try:
                update_data = {
                    "score": 0.95,
                    "reason": "Updated: Even higher customer satisfaction scores"
                }
                success = await recommendation_crud.update_recommendation(recommendation_id, update_data)
                if success:
                    print(f"✅ Successfully updated recommendation {recommendation_id}")
                print()
            except Exception as e:
                print(f"❌ Error updating recommendation: {e}\n")
        
        print("=== CRUD Operations Demonstration Complete ===")
        
    except Exception as e:
        print(f"❌ General error during CRUD operations: {e}")
    
    finally:
        # Close MongoDB connection
        print("8. Closing MongoDB connection...")
        await close_mongo_connection()
        print("✅ MongoDB connection closed")

async def demonstrate_error_handling():
    """
    Demonstrate error handling in CRUD operations.
    Shows how the functions handle various error conditions.
    """
    
    print("\n=== Error Handling Demonstration ===\n")
    
    await connect_to_mongo()
    
    try:
        recommendation_crud = get_recommendation_crud()
        product_crud = get_product_crud()
        
        # Test 1: Invalid product ID format
        print("1. Testing invalid product ID format...")
        try:
            await product_crud.get_product_by_id("invalid_id")
        except Exception as e:
            print(f"✅ Correctly caught error: {e}\n")
        
        # Test 2: Non-existent product ID
        print("2. Testing non-existent product ID...")
        try:
            await product_crud.get_product_by_id("6708b123456789abcdef9999")
        except Exception as e:
            print(f"✅ Correctly caught error: {e}\n")
        
        # Test 3: Invalid recommendation ID
        print("3. Testing invalid recommendation ID...")
        try:
            await recommendation_crud.get_recommendation_by_id("invalid_id")
        except Exception as e:
            print(f"✅ Correctly caught error: {e}\n")
        
        # Test 4: Product with no recommendations
        print("4. Testing product with no recommendations...")
        try:
            recs = await recommendation_crud.get_recommendation_by_product("6708b123456789abcdef9999")
            print(f"✅ Correctly returned empty list: {len(recs)} recommendations found\n")
        except Exception as e:
            print(f"❌ Unexpected error: {e}\n")
        
        print("=== Error Handling Demonstration Complete ===")
        
    except Exception as e:
        print(f"❌ General error during error handling demo: {e}")
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    print("Starting MongoDB CRUD Operations Examples...\n")
    
    # Run the main CRUD operations example
    asyncio.run(example_crud_operations())
    
    # Run the error handling demonstration  
    asyncio.run(demonstrate_error_handling())
    
    print("\n🎉 All examples completed!")