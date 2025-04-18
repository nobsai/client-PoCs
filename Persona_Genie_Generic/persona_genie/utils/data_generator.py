import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker()

def generate_sample_dataset(n_customers=50, n_orders=200, output_path=None):
    """
    Generate a synthetic dataset for AlFahim HQ customer orders.
    
    Args:
        n_customers: Number of unique customers
        n_orders: Total number of orders
        output_path: Path to save the CSV file
        
    Returns:
        DataFrame of generated data
    """
    # Create customer IDs
    customer_ids = [f"CUS{fake.unique.random_int(min=10000, max=99999)}" for _ in range(n_customers)]
    
    # Define luxury brands (fictional but premium-sounding)
    brands = [
        "Velone", "Aurum Drive", "Zenith Wear", "Elysia", "Monarch Elite",
        "Lumiere", "Prestige Atelier", "Azure Legacy", "Opulent Craft", "Grandeur",
        "Royal Pursuit", "Ethereal", "Velocity Luxe", "Majestic Timeline", "Sublime Essence"
    ]
    
    # Define product categories
    categories = {
        "Footwear": ["Leather Loafers", "White Sneakers", "Oxford Shoes", "Chelsea Boots", 
                     "Driving Moccasins", "Racing Boots", "Suede Desert Boots", "Italian Brogues"],
        "Apparel": ["Cashmere Sweater", "Silk Shirt", "Tailored Blazer", "Merino Wool Coat", 
                    "Racing Jacket", "Linen Trousers", "Fitted Polo", "Designer Jeans"],
        "Accessories": ["Leather Satchel", "Chronograph Watch", "Driving Gloves", "Cashmere Scarf",
                        "Titanium Sunglasses", "Italian Leather Belt", "Silk Pocket Square", "Monogrammed Wallet"],
        "Automotive Gear": ["Racing Chronograph", "Driving Jacket", "Performance Gloves", "Carbon Fiber Keychain",
                           "Heritage Racing Helmet", "Limited Edition Car Model", "Luxury Car Care Kit"]
    }
    
    # Define colors with luxury palette
    colors = ["Midnight Black", "Pearl White", "Sapphire Blue", "Burgundy", "Charcoal Grey", 
              "Desert Sand", "Navy", "Racing Red", "Emerald Green", "Champagne Gold", 
              "Silver", "Cognac Brown", "Ivory", "Slate Grey", "Cobalt Blue"]
    
    # Define channels
    channels = ["Online", "In-store", "Personal Shopper", "Exclusive Event", "VIP Appointment"]
    
    # Create empty dataframe
    data = []
    
    # Generate random order dates in the last year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Generate orders
    for _ in range(n_orders):
        customer_id = random.choice(customer_ids)
        category = random.choice(list(categories.keys()))
        product_name = random.choice(categories[category])
        brand = random.choice(brands)
        color = random.choice(colors)
        
        # Price ranges based on category and brand prestige
        base_price = {
            "Footwear": random.uniform(200, 1500),
            "Apparel": random.uniform(150, 2000),
            "Accessories": random.uniform(100, 5000),
            "Automotive Gear": random.uniform(250, 3000)
        }[category]
        
        # Add brand premium (some brands are more expensive)
        brand_premium = random.uniform(0.8, 1.5)
        price = round(base_price * brand_premium, 2)
        
        # Generate random order date
        order_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        # Determine channel with weighted probabilities
        channel = random.choices(
            channels, 
            weights=[0.4, 0.3, 0.15, 0.1, 0.05],
            k=1
        )[0]
        
        data.append({
            "CustomerID": customer_id,
            "Product Name": product_name,
            "Category": category,
            "Color": color,
            "Brand": brand,
            "Price": price,
            "Order Date": order_date.strftime("%Y-%m-%d"),
            "Channel": channel
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Sort by CustomerID and Order Date
    df = df.sort_values(["CustomerID", "Order Date"])
    
    # Save to CSV if path provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Dataset saved to {output_path}")
    
    return df

if __name__ == "__main__":
    # Generate sample dataset when run directly
    generate_sample_dataset(
        n_customers=50,
        n_orders=200,
        output_path="../data/sample_customer_orders.csv"
    ) 