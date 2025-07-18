import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster

# --- Configuration ---
# Ensure this path points to your geocoded CSV file
CSV_FILE_PATH = 'Geocoded_ITI_MSME_Locations.csv' 

# Column names from your CSV
LATITUDE_COL = 'Latitude'
LONGITUDE_COL = 'Longitude'
NAME_COL = 'Name'
TYPE_COL = 'Type'

# Map settings
MAP_CENTER = [15.40, 75.05] # Centered on Hubli-Dharwad
MAP_START_ZOOM = 11
OUTPUT_MAP_FILE = 'minimalistic_hubli_dharwad_map.html'

# --- Main Script ---

# Load the data
try:
    df = pd.read_csv(CSV_FILE_PATH)
except FileNotFoundError:
    print(f"ERROR: The file '{CSV_FILE_PATH}' was not found.")
    exit()

# Clean data by removing entries without coordinates
df.dropna(subset=[LATITUDE_COL, LONGITUDE_COL], inplace=True)
print(f"Loaded and processing {len(df)} locations with valid geocodes.")

# 1. Create a map with a minimalistic tile layer
# 'CartoDB Positron' is a clean, light-gray map style that makes data stand out.
m = folium.Map(
    location=MAP_CENTER,
    zoom_start=MAP_START_ZOOM,
    tiles='CartoDB Positron'
)

# --- Create Layers for Toggling ---
# FeatureGroups allow us to add layers to a LayerControl widget.
heatmap_layer = folium.FeatureGroup(name='Heatmap View', show=True)
pins_layer = folium.FeatureGroup(name='Location Pins (Clustered)', show=True)

# 2. Add the Heatmap Layer
# Create a list of [lat, lon] points for the heatmap
heat_data = df[[LATITUDE_COL, LONGITUDE_COL]].values.tolist()
HeatMap(heat_data, radius=15, blur=10).add_to(heatmap_layer)

# 3. Add Clustered Pins for a Cleaner View
# MarkerCluster groups pins that are close together into a single numbered circle.
marker_cluster = MarkerCluster().add_to(pins_layer)

for idx, row in df.iterrows():
    pin_color = 'blue' if row[TYPE_COL] == 'ITI' else 'red'
    popup_text = f"<b>{row[NAME_COL]}</b><br>Type: {row[TYPE_COL]}"
    
    # Using CircleMarker for a cleaner, more modern pin style
    folium.CircleMarker(
        location=[row[LATITUDE_COL], row[LONGITUDE_COL]],
        radius=5,
        color=pin_color,
        fill=True,
        fill_color=pin_color,
        fill_opacity=0.7,
        popup=popup_text
    ).add_to(marker_cluster)

# Add the prepared layers to the map
heatmap_layer.add_to(m)
pins_layer.add_to(m)

# 4. Add Layer Control to Toggle Views
# This adds a control box in the top-right corner of the map.
folium.LayerControl().add_to(m)

# --- Save the final map to an HTML file ---
m.save(OUTPUT_MAP_FILE)
print(f"\nSuccess! Your new minimalistic map has been saved as '{OUTPUT_MAP_FILE}'.")
print("Open this file in a browser to see the interactive map.")
