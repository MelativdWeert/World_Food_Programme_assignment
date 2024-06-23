# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 21:31:46 2024

@author: Melati van der Weert
"""

# Import packages
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import os
from rasterstats import zonal_stats

# Define the directory containing the raster files
data_dir = r'C:\Users\nlmewl\Documents\0_Documenten\World_Food_Programme_assignment\Data\Regen'
output_dir = r'C:\Users\nlmewl\Documents\0_Documenten\World_Food_Programme_assignment\Output'
grenzen_shapefile = r'C:\Users\nlmewl\Documents\0_Documenten\World_Food_Programme_assignment\Data\Grenzen\geoBoundaries-MOZ-ADM2.geojson'
output_shapefile = os.path.join(output_dir, 'gemiddelde_percentile_95_neerslag_per_grens.shp')

# File paths for outputs
percentile_95_file = os.path.join(output_dir, 'percentile_95_blended_rainfall.tif')

# Get list of all raster files in the directory
raster_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.tif')]

# Function to calculate 95th percentile raster
def calculate_95th_percentile(rainfall_stack):
    return np.percentile(rainfall_stack, 95, axis=0)

# Stack all rasters for calculation
rainfall_stack = []
for raster_file in raster_files:
    with rasterio.open(raster_file) as src:
        rainfall_stack.append(src.read(1))
                
# Stack all rasters for all 3 dekads of March across all years
rainfall_stack = []
for raster_file in raster_files:
    if '03d3' in raster_file:  
        with rasterio.open(raster_file) as src:
            rainfall_stack.append(src.read(1))
           
# Convert list to numpy array for percentile calculation
rainfall_stack = np.array(rainfall_stack)

# Calculate 95th percentile data
percentile_95_data = calculate_95th_percentile(rainfall_stack)        
   
# Save 95th percentile raster
with rasterio.open(raster_files[0]) as src:
    meta = src.meta.copy()
    meta.update(dtype=percentile_95_data.dtype, count=1)

with rasterio.open(percentile_95_file, 'w', **meta) as dst:
    dst.write(percentile_95_data, 1)
    
     
# Open the administrative boundaries shapefile
grenzen_gdf = gpd.read_file(grenzen_shapefile)

# Function to calculate mean 95th percentile rainfall per administrative area
def calculate_mean_percentile_95(gdf, raster_data, affine_transform):
    # Mask the raster based on each administrative area
    stats = zonal_stats(gdf, raster_data, affine=affine_transform, stats=['mean'])
    
    # Add mean values to the GeoDataFrame
    gdf['mean_percentile_95'] = [stat['mean'] for stat in stats]
    
    return gdf

# Calculate mean 95th percentile rainfall per administrative area
grenzen_gdf = calculate_mean_percentile_95(grenzen_gdf, percentile_95_data, meta['transform'])

# Save the results to a new shapefile
grenzen_gdf.to_file(output_shapefile)    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    