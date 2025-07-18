import pandas as pd
import folium
from folium.plugins import HeatMap

# --- Configuration: Update these variables to match your file ---

# 1. Path to your geocoded CSV file
CSV_FILE_PATH = 'Geocoded_ITI_MSME_Locations.csv'

# 2. Column names in your CSV file (must match exactly)
LATITUDE_COL = 'Latitude'
LONGITUDE_COL = 'Longitude'
NAME_COL = 'Name'
TYPE_COL = 'Type' # This column is used for color-coding pins

# 3. Map settings
# Coordinates for the center of the Hubli-Dharwad region
MAP_CENTER = [15.40, 75.05] 
MAP_START_ZOOM = 11

# 4. Output file name
OUTPUT_MAP_FILE = 'hubli_dharwad_heatmap.html'

# --- Main Script ---

# Load the data from the CSV file
try:
    df = pd.read_csv(CSV_FILE_PATH)
    print(f"Successfully loaded {len(df)} entries from '{CSV_FILE_PATH}'.")
except FileNotFoundError:
    print(f"ERROR: The file '{CSV_FILE_PATH}' was not found.")
    print("Please make sure the script is in the same directory as your CSV file, or update the CSV_FILE_PATH variable.")
    exit()

# Drop rows with missing latitude or longitude data
df.dropna(subset=[LATITUDE_COL, LONGITUDE_COL], inplace=True)
print(f"Processing {len(df)} entries with valid geocodes.")

# Create a base map centered on Hubli/Dharwad
m = folium.Map(location=MAP_CENTER, zoom_start=MAP_START_ZOOM)

# --- Add Custom Heading ---
heading_html = '''
<div style="position: fixed; 
            top: 10px; left: 10px; width: 350px; height: 50px; 
            background-color: rgba(255, 255, 255, 0.9); 
            border: 2px solid #333;
            border-radius: 8px; 
            z-index: 9999; 
            font-family: Arial, sans-serif; 
            font-size: 22px; 
            font-weight: bold; 
            color: #333;
            display: flex; 
            align-items: center; 
            justify-content: center; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
    ITI VS MSMEs Hubli/Dharwad
</div>
'''

# Add the heading to the map
m.get_root().html.add_child(folium.Element(heading_html))

# --- Add a Pin for Each Location ---
# We will color-code pins: blue for ITI, red for MSME
for idx, row in df.iterrows():
    # Define pin color based on the 'Type' column
    pin_color = 'blue' if row[TYPE_COL] == 'ITI' else 'red'
    
    # Create a popup text with the name and type
    popup_text = f"<b>{row[NAME_COL]}</b><br>Type: {row[TYPE_COL]}"
    
    folium.Marker(
        location=[row[LATITUDE_COL], row[LONGITUDE_COL]],
        popup=popup_text,
        icon=folium.Icon(color=pin_color, icon='info-sign')
    ).add_to(m)

# --- Add the Heatmap Layer ---
# Create a list of [lat, lon] points for the heatmap
heat_data = df[[LATITUDE_COL, LONGITUDE_COL]].values.tolist()

# Add the heatmap to the map
HeatMap(heat_data).add_to(m)

# Add layer control to toggle pins and heatmap on/off
# folium.LayerControl().add_to(m) # Uncomment if you want layer controls

# --- Save the Map to an HTML File ---
try:
    m.save(OUTPUT_MAP_FILE)
    print(f"\nSuccess! Your map has been saved as '{OUTPUT_MAP_FILE}'.")
    print("Open this file in a web browser to view your interactive map with heading.")
except Exception as e:
    print(f"An error occurred while saving the map: {e}")
