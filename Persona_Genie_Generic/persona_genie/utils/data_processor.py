import pandas as pd
import os
from datetime import datetime

def load_data(file_path):
    """
    Load data from CSV or Excel file
    
    Args:
        file_path: Path to the data file
        
    Returns:
        DataFrame of loaded data
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.csv':
        return pd.read_csv(file_path)
    elif file_ext in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Please use CSV or Excel files.")

def group_by_customer(df):
    """
    Group order data by customer ID
    
    Args:
        df: DataFrame of order data
        
    Returns:
        Dictionary with customer IDs as keys and their orders as values
    """
    customer_groups = {}
    
    for customer_id, group in df.groupby('CustomerID'):
        customer_groups[customer_id] = group.to_dict('records')
    
    return customer_groups

def get_customer_stats(customer_orders):
    """
    Calculate basic statistics for a customer
    
    Args:
        customer_orders: List of order dictionaries for a customer
        
    Returns:
        Dictionary of customer statistics
    """
    if not customer_orders:
        return {}
    
    # Total spent
    total_spent = sum(order['Price'] for order in customer_orders)
    
    # Favorite brands
    brands = [order['Brand'] for order in customer_orders]
    brand_counts = pd.Series(brands).value_counts()
    favorite_brands = brand_counts.index.tolist()[:3]  # Top 3 brands
    
    # Favorite categories
    categories = [order['Category'] for order in customer_orders]
    category_counts = pd.Series(categories).value_counts()
    favorite_categories = category_counts.index.tolist()
    
    # Favorite colors
    colors = [order['Color'] for order in customer_orders]
    color_counts = pd.Series(colors).value_counts()
    favorite_colors = color_counts.index.tolist()[:3]  # Top 3 colors
    
    # Preferred channels
    channels = [order['Channel'] for order in customer_orders]
    channel_counts = pd.Series(channels).value_counts()
    preferred_channels = channel_counts.index.tolist()[:2]  # Top 2 channels
    
    # Average order value
    avg_order_value = total_spent / len(customer_orders)
    
    # Purchase frequency
    order_dates = pd.to_datetime([order['Order Date'] for order in customer_orders])
    date_range = (max(order_dates) - min(order_dates)).days + 1
    purchase_frequency = len(customer_orders) / max(date_range, 1) * 30  # Orders per month
    
    # Most recent purchase date
    most_recent = max(order_dates).strftime('%Y-%m-%d')
    
    # Extract product keywords
    product_keywords = []
    for order in customer_orders:
        words = order['Product Name'].split()
        product_keywords.extend(words)
    
    return {
        'total_spent': round(total_spent, 2),
        'order_count': len(customer_orders),
        'avg_order_value': round(avg_order_value, 2),
        'favorite_brands': favorite_brands,
        'favorite_categories': favorite_categories,
        'favorite_colors': favorite_colors,
        'preferred_channels': preferred_channels,
        'purchase_frequency': round(purchase_frequency, 2),
        'most_recent_purchase': most_recent,
        'product_keywords': product_keywords
    }

def export_profiles(profiles, output_path):
    """
    Export customer profiles to CSV
    
    Args:
        profiles: List of customer profile dictionaries
        output_path: Path to save the CSV file
        
    Returns:
        Path to the saved file
    """
    # Convert to DataFrame
    df = pd.DataFrame(profiles)
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    return output_path 