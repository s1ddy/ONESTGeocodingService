import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os
import time

# Create the CSV data if it doesn't exist
def create_sample_csv():
    data = {
        'Name': [
            'Govt. Industrial Training Institute', 'Dr. Ambedkar Shikshan Sam ITI',
            'Mahila Vidyapeeta ITI', 'Shri Guru Gorakshanath ITI',
            'Smt. Kamalamma Lahoti ITI', 'Sri Siddeshwar ITI',
            'Govt. ITI for Women', 'Basaveshwar ITI',
            'Karnataka Lingayat Education Society ITI', 'Gurumallappa Chabbi Rural ITI',
            'MSME Development Institute (Hubli)', 'Hubli Engineering Cluster',
            'Auto Cluster', 'Readymade Garment Cluster',
            'Belur Industrial Estate', 'Mummigatti Industrial Estate',
            'Kotur Industrial Estate', 'Tungabhadra Industrial Estate',
            'Gandhi Nagar Industrial Area', 'Garment Manufacturing Cluster'
        ],
        'Type': [
            'ITI', 'ITI', 'ITI', 'ITI', 'ITI', 'ITI', 'ITI', 'ITI', 'ITI', 'ITI',
            'MSME', 'MSME', 'MSME', 'MSME', 'MSME', 'MSME', 'MSME', 'MSME', 'MSME', 'MSME'
        ],
        'Address': [
            'Vidyanagar, Hubli', 'Nekar Nagar, Hubli', 'Vidyanagar, Hubli',
            'Tarihal Road, Hubli', 'Station Road, Hubli', 'Hosur Road, Hubli',
            'Gokul Road, Hubli', 'Industrial Area, Dharwad', 'Vidyanagar, Hubli',
            'Hosa Yellapur, Dharwad', 'Industrial Estate, Gokul Road, Hubli',
            'Tarihal Industrial Area, Gokul Road, Hubli', 'Gokul Road, Hubli',
            'Gokul Road, Hubli', 'Belur, Dharwad', 'Mummigatti, Dharwad',
            'Kotur, Dharwad', 'Navanagar, Hubli', 'Gandhi Nagar, Hubli',
            'Gokul Road, Hubli'
        ],
        'City': ['Hubli'] * 10 + ['Hubli'] * 10,
        'Region': ['Hubli/Dharwad'] * 20
    }
    return pd.DataFrame(data)

# File paths
input_path = 'Hubli_Dharwad_ITI_MSME_Locations.csv'
output_path = 'Geocoded_ITI_MSME_Locations.csv'

# Check if input file exists, if not create it
if not os.path.exists(input_path):
    print(f"File {input_path} not found. Creating sample CSV...")
    df = create_sample_csv()
    df.to_csv(input_path, index=False)
    print(f"Sample CSV created: {input_path}")
else:
    print(f"Loading existing file: {input_path}")

# Load the CSV
try:
    df = pd.read_csv(input_path)
    print(f"Successfully loaded {len(df)} entries from CSV")
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

# Set up geocoder with error handling
geolocator = Nominatim(user_agent="hubli_dharwad_geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Function to get lat/lon with better error handling
def get_latlon(address):
    try:
        # Add Karnataka and India for better geocoding accuracy
        full_address = f"{address}, Karnataka, India"
        location = geolocator.geocode(full_address, timeout=10)
        
        if location:
            return pd.Series([location.latitude, location.longitude])
        else:
            # Try with just India if Karnataka doesn't work
            location = geolocator.geocode(f"{address}, India", timeout=10)
            if location:
                return pd.Series([location.latitude, location.longitude])
            else:
                print(f"Could not geocode: {address}")
                return pd.Series([None, None])
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return pd.Series([None, None])

# Apply geocoding with progress tracking
print("Starting geocoding process...")
df[['Latitude', 'Longitude']] = df['Address'].apply(get_latlon)

# Show results
geocoded_count = df[['Latitude', 'Longitude']].notna().all(axis=1).sum()
total_count = len(df)
print(f"Geocoding complete: {geocoded_count}/{total_count} addresses successfully geocoded")

# Save to new CSV file
try:
    df.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")
except Exception as e:
    print(f"Error saving file: {e}")

# Display first few results
print("\nFirst 5 geocoded entries:")
print(df[['Name', 'Address', 'Latitude', 'Longitude']].head())
