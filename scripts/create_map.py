import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import os

# --- Configuration ---
CSV_FILE_PATH = 'Geocoded_ITI_MSME_Locations.csv'

# Column names from your CSV
LATITUDE_COL = 'Latitude'
LONGITUDE_COL = 'Longitude'
NAME_COL = 'Name'
TYPE_COL = 'Type'

# Map settings
MAP_CENTER = [15.40, 75.05]  # Centered on Hubli-Dharwad
MAP_START_ZOOM = 11
OUTPUT_MAP_FILE = 'aesthetic_hubli_dharwad_map.html'

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

# Count MSMEs and ITIs for the legend
msme_count = df[df[TYPE_COL] == 'MSME'].shape[0]
iti_count = df[df[TYPE_COL] == 'ITI'].shape[0]

print(f"MSMEs: {msme_count}, ITIs: {iti_count}")

# Create a map with aesthetic white background tiles
m = folium.Map(
    location=MAP_CENTER,
    zoom_start=MAP_START_ZOOM,
    tiles='CartoDB Positron',  # Clean white background
    attr='Map data © OpenStreetMap contributors'
)

# Add custom CSS for Roboto font and styling
title_html = '''
<div style="position: fixed; 
            top: 10px; right: 10px; width: 300px; height: 60px; 
            background-color: rgba(255, 255, 255, 0.9);
            border: 2px solid #4A90E2;
            border-radius: 8px;
            z-index: 9999; 
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 20px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
            line-height: 60px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            ">
    <p style="margin: 0; padding: 0;">Hubli/Dharwad Heatmap</p>
</div>
'''

# Add legend HTML
legend_html = f'''
<div style="position: fixed; 
            bottom: 20px; left: 20px; width: 200px; height: 100px; 
            background-color: rgba(255, 255, 255, 0.95);
            border: 2px solid #4A90E2;
            border-radius: 8px;
            z-index: 9999; 
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 14px;
            color: #2C3E50;
            padding: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            ">
    <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 16px; text-align: center;">Legend</p>
    <p style="margin: 5px 0; display: flex; align-items: center;">
        <span style="width: 15px; height: 15px; background-color: #87CEEB; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
        MSMEs: {msme_count}
    </p>
    <p style="margin: 5px 0; display: flex; align-items: center;">
        <span style="width: 15px; height: 15px; background-color: #708090; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
        ITIs: {iti_count}
    </p>
</div>
'''

# Add Roboto font
font_html = '''
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
'''

# Add the custom HTML elements to the map
m.get_root().html.add_child(folium.Element(font_html))
m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(legend_html))

# Create feature groups for different layers
heatmap_layer = folium.FeatureGroup(name='Heatmap View', show=True)
pins_layer = folium.FeatureGroup(name='Location Pins', show=True)

# Add heatmap layer with blue color scheme
heat_data = df[[LATITUDE_COL, LONGITUDE_COL]].values.tolist()
HeatMap(
    heat_data, 
    radius=15, 
    blur=10, 
    gradient={0.0: '#E3F2FD', 0.25: '#BBDEFB', 0.5: '#64B5F6', 0.75: '#2196F3', 1.0: '#0D47A1'}
).add_to(heatmap_layer)

# Add individual pins with correct colors (light blue for MSMEs, grey for ITIs)
for idx, row in df.iterrows():
    # Set colors according to requirements
    if row[TYPE_COL] == 'MSME':
        pin_color = '#87CEEB'  # Light blue for MSMEs
        border_color = '#4A90E2'
    else:  # ITI
        pin_color = '#708090'  # Grey for ITIs
        border_color = '#2C3E50'
    
    popup_text = f"""
    <div style="font-family: 'Roboto', Arial, sans-serif; max-width: 200px;">
        <b style="color: #2C3E50; font-size: 16px;">{row[NAME_COL]}</b><br>
        <span style="color: #4A90E2; font-weight: bold;">Type: {row[TYPE_COL]}</span><br>
        <span style="color: #666; font-size: 12px;">Click for details</span>
    </div>
    """
    
    folium.CircleMarker(
        location=[row[LATITUDE_COL], row[LONGITUDE_COL]],
        radius=6,
        color=border_color,
        weight=2,
        fill=True,
        fill_color=pin_color,
        fill_opacity=0.8,
        popup=folium.Popup(popup_text, max_width=250)
    ).add_to(pins_layer)

# Add the layers to the map
heatmap_layer.add_to(m)
pins_layer.add_to(m)

# Add layer control
folium.LayerControl(position='topright').add_to(m)

# Save the map
m.save(OUTPUT_MAP_FILE)
print(f"\nSuccess! Your aesthetic map has been saved as '{OUTPUT_MAP_FILE}'.")
print("Features added:")
print("- Blue and white color scheme")
print("- Light blue pins for MSMEs")
print("- Grey pins for ITIs")
print("- Custom legend with counts")
print("- Roboto font heading")
print("- Enhanced styling and shadows")
