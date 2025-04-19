import pandas as pd
import random
import uuid
from faker import Faker

fake = Faker()

# Define sample data for products
products = [
    {"name": "Samsung Galaxy Tab", "description": "10.4\" display with minimal bezel and maximum view"},
    {"name": "Apple Watch", "description": "The Apple Watch Series 6 lets you measure your health"},
    {"name": "Sony Alpha a6400 Mirrorless Camera", "description": "24.2MP APS-C Exmor sensor w/ advanced processing"},
    {"name": "Bose Noise Cancelling Headphones 700", "description": "Premium wireless headphones with adaptive noise cancelling"},
    {"name": "Dell XPS 13", "description": "13.3\" UHD display with 11th Gen Intel Core processor"},
    {"name": "iPad Pro", "description": "12.9\" Liquid Retina XDR display with M1 chip"},
    {"name": "Kindle Paperwhite", "description": "6.8\" display with adjustable warm light and waterproof design"},
    {"name": "GoPro HERO10", "description": "5.3K video and 23MP photos with revolutionary processor"},
    {"name": "Sony WH-1000XM4", "description": "Industry-leading noise cancellation headphones"},
    {"name": "Microsoft Surface Laptop 4", "description": "13.5\" touchscreen with AMD Ryzen processor"},
    {"name": "Logitech MX Master 3", "description": "Advanced wireless mouse with ergonomic design"},
    {"name": "Samsung QLED TV", "description": "4K UHD Smart TV with Quantum Dot technology"},
    {"name": "Nikon D7500 DSLR", "description": "20.9MP sensor with 4K UHD video capabilities"},
    {"name": "Anker PowerCore 20000", "description": "Ultra-high capacity portable charger with fast charging"},
    {"name": "Apple MacBook Pro", "description": "16\" display with M1 Pro chip and advanced thermal design"},
    {"name": "Dyson V11 Vacuum", "description": "Cordless stick vacuum with powerful suction"},
    {"name": "JBL Flip 5", "description": "Portable waterproof Bluetooth speaker"},
    {"name": "Ring Video Doorbell", "description": "1080p HD video doorbell with motion detection"},
    {"name": "Fitbit Charge 5", "description": "Advanced fitness tracker with stress management tools"},
    {"name": "Canon EOS R6", "description": "20MP full-frame mirrorless camera with 4K video"}
]

# Define a fixed list of cardholder names
card_names = [
    "Mark Richard", "Jennifer Diaz", "Crystal Stewart", "Timothy Hughes", "Kerry Sharp",
    "Angela Watson", "Matthew Carter", "Elizabeth Hall", "Nathan Scott", "Sandra Bryant",
    "Victor Collins", "Olivia Perez", "Benjamin Lee", "Sophia Morgan", "James Taylor",
    "Emma Davis", "Henry Johnson", "Chloe Harris", "William Moore", "Mia Thompson"
]

# Generate fictitious data
data = []
for _ in range(300):  # Generate 100 rows
    product = random.choice(products)
    price = round(random.uniform(150, 1000), 2)  # Random price between $150 and $1000
    product_id = str(uuid.uuid4())  # Random UUID
    category = "Electronics"
    timestamp = fake.date_between(start_date="-3y", end_date="today")  # Random date in the past 3 years
    card_name = random.choice(card_names)  # Randomly pick a name from the fixed list

    data.append({
        "price": price,
        "product": product["name"],
        "product_description": product["description"],
        "product_id": product_id,
        "category": category,
        "time_stamp": timestamp,
        "card_name": card_name
    })

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("fictitious_dataset.csv", index=False)
print("Dataset saved as 'fictitious_dataset.csv'")
