#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update reservoir coordinates based on province-city-county location data
The coordinates from the GitHub source are already in GCJ-02 (Mars) coordinate system,
which is the same system used by ECharts and Aliyun DataV maps.
"""

import json
import requests
import math

def load_location_data():
    """Load China administrative division coordinates from GitHub (GCJ-02 system)"""
    url = "https://raw.githubusercontent.com/lyhmyd1211/GeoMapData_CN/master/location.json"
    response = requests.get(url)
    return response.json()

def find_coordinates(location_data, province, city=None, county=None):
    """
    Find coordinates for a given location
    Returns [longitude, latitude] in GCJ-02 coordinate system
    """
    # Normalize names - remove common suffixes
    def normalize_name(name):
        if not name:
            return name
        # Remove common administrative suffixes
        suffixes = ['省', '市', '自治区', '特别行政区', '县', '区', '旗', '自治县', '自治旗']
        for suffix in suffixes:
            if name.endswith(suffix):
                return name[:-len(suffix)]
        return name
    
    province_norm = normalize_name(province)
    city_norm = normalize_name(city) if city else None
    county_norm = normalize_name(county) if county else None
    
    # Try to find by county first (most specific)
    if county:
        for adcode, data in location_data.items():
            name = data.get('name', '')
            if (name == county or normalize_name(name) == county_norm) and data.get('level') == 'district':
                coords = data.get('center')
                if coords:
                    return coords
    
    # Try to find by city
    if city:
        for adcode, data in location_data.items():
            name = data.get('name', '')
            if (name == city or normalize_name(name) == city_norm) and data.get('level') == 'city':
                coords = data.get('center')
                if coords:
                    return coords
    
    # Fall back to province
    for adcode, data in location_data.items():
        name = data.get('name', '')
        if (name == province or normalize_name(name) == province_norm) and data.get('level') == 'province':
            coords = data.get('center')
            if coords:
                return coords
    
    return None

def update_reservoir_coordinates():
    """Update coordinates in reservoirs.json"""
    print("Loading location data (GCJ-02 coordinate system)...")
    location_data = load_location_data()
    
    print("Loading reservoir data...")
    with open('web/src/data/reservoirs.json', 'r', encoding='utf-8') as f:
        reservoirs = json.load(f)
    
    updated_count = 0
    changed_count = 0
    not_found = []
    
    print(f"Processing {len(reservoirs)} reservoirs...")
    for reservoir in reservoirs:
        province = reservoir.get('province', '').strip()
        city = reservoir.get('city', '').strip()
        county = reservoir.get('county', '').strip()
        
        # Find coordinates
        coords = find_coordinates(location_data, province, city, county)
        
        if coords:
            old_coords = reservoir.get('coordinates')
            reservoir['coordinates'] = coords
            updated_count += 1
            
            # Check if coordinates actually changed
            if old_coords and (abs(old_coords[0] - coords[0]) > 0.01 or abs(old_coords[1] - coords[1]) > 0.01):
                changed_count += 1
                print(f"Updated {reservoir['name']}: {old_coords} -> {coords}")
        else:
            not_found.append({
                'name': reservoir['name'],
                'province': province,
                'city': city,
                'county': county
            })
            print(f"⚠️  Could not find coordinates for {reservoir['name']} ({province}/{city}/{county})")
    
    # Save updated data
    print(f"\nSaving updated data...")
    with open('web/src/data/reservoirs.json', 'w', encoding='utf-8') as f:
        json.dump(reservoirs, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Updated {updated_count}/{len(reservoirs)} reservoirs")
    print(f"📝 {changed_count} coordinates were modified")
    print(f"ℹ️  All coordinates are now in GCJ-02 (Mars) coordinate system")
    print(f"   This matches the coordinate system used by ECharts and Aliyun DataV maps")
    
    if not_found:
        print(f"\n⚠️  {len(not_found)} reservoirs could not be geocoded:")
        for item in not_found[:10]:  # Show first 10
            print(f"   - {item['name']} ({item['province']}/{item['city']}/{item['county']})")
        if len(not_found) > 10:
            print(f"   ... and {len(not_found) - 10} more")

if __name__ == '__main__':
    update_reservoir_coordinates()
