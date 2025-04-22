import pandas as pd
import random
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# Generate Flight Status Dataset
def generate_flight_status_data(n=100):
    flight_statuses = ['On Time', 'Delayed', 'Cancelled', 'Boarding', 'Landed']
    airports = ['AUH', 'JFK', 'LHR', 'ORD', 'DXB', 'SIN', 'SYD', 'CDG', 'FRA', 'BOM']
    data = []
    
    for _ in range(n):
        data.append({
            "Flight Number": f"EY{random.randint(100, 999)}",
            "Date": fake.date_between(start_date='-1y', end_date='today'),
            "Origin": random.choice(airports),
            "Destination": random.choice([a for a in airports if not data or a != data[-1]['Origin']]),

            "Departure Time": fake.time(),
            "Arrival Time": fake.time(),
            "Status": random.choice(flight_statuses)
        })
    
    return pd.DataFrame(data)

# Generate Booking Details Dataset
def generate_booking_details(n=100):
    travel_classes = ['Economy', 'Business', 'First Class']
    destinations = ['Abu Dhabi', 'New York', 'London', 'Chicago', 'Dubai', 'Singapore', 'Sydney', 'Paris', 'Frankfurt', 'Mumbai']
    
    data = []
    for _ in range(n):
        data.append({
            "User Name": fake.name(),
            "Booking Date": fake.date_between(start_date='-1y', end_date='today'),
            "Destination": random.choice(destinations),
            "Class": random.choice(travel_classes),
            "Price (USD)": round(random.uniform(300, 5000), 2)
        })
    
    return pd.DataFrame(data)

# Generate the datasets
flight_status_df = generate_flight_status_data()
booking_details_df = generate_booking_details()

# Save to CSV
flight_status_df.to_csv("flight_status_data.csv", index=False)
booking_details_df.to_csv("booking_details_data.csv", index=False)

print("Datasets generated and saved as CSV files.")
