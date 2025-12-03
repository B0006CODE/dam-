import pandas as pd
import json
import requests
from collections import defaultdict
import time

def get_county_coordinates(province, city, county):
    """
    Get coordinates for a county using Gaode Map API (free tier)
    Returns (longitude, latitude) or None if not found
    """
    # For now, we'll use a simplified approach with a local database
    # In production, you might want to use an API or more complete database
    
    # Clean up the location strings
    if pd.isna(county) or county == '所在县':
        county = ''
    if pd.isna(city) or city == '所在市':
        city = ''
    if pd.isna(province) or province == '所在省份':
        province = ''
    
    # Build location string
    location = f"{province}{city}{county}".strip()
    
    return location

def main():
    print("Reading Excel file...")
    df = pd.read_excel('水库信息.xlsx')
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Rename unnamed columns
    df = df.rename(columns={
        'Unnamed: 3': '所在市',
        'Unnamed: 4': '所在县'
    })
    
    # Remove header row if it exists in data
    df = df[df['水库地点'] != '所在省份']
    
    print(f"Total reservoirs: {len(df)}")
    
    # Process each reservoir
    reservoirs = []
    province_stats = defaultdict(lambda: {
        'reservoirs': [],
        'damTypes': defaultdict(int),
        'basins': defaultdict(int),
        'totalCount': 0
    })
    
    for idx, row in df.iterrows():
        # Extract data
        reservoir_id = str(row['序号']) if pd.notna(row['序号']) else f"R-{idx}"
        name = str(row['水库名称']) if pd.notna(row['水库名称']) else ''
        province = str(row['水库地点']) if pd.notna(row['水库地点']) else ''
        city = str(row['所在市']) if pd.notna(row['所在市']) else ''
        county = str(row['所在县']) if pd.notna(row['所在县']) else ''
        basin = str(row['所在流域']) if pd.notna(row['所在流域']) else ''
        reservoir_type = str(row['水库型别']) if pd.notna(row['水库型别']) else ''
        capacity = float(row['总库容\n（万方）']) if pd.notna(row['总库容\n（万方）']) else None
        dam_type = str(row['主坝坝型']) if pd.notna(row['主坝坝型']) else ''
        max_height = float(row['最大坝高\n（m）']) if pd.notna(row['最大坝高\n（m）']) else None
        
        # Skip if essential data is missing
        if not name or not province:
            continue
        
        # Get location string for geocoding
        location = get_county_coordinates(province, city, county)
        
        # Create reservoir object
        reservoir = {
            'id': reservoir_id,
            'name': name,
            'province': province,
            'city': city,
            'county': county,
            'location': location,  # Will be used for geocoding
            'basin': basin if basin else None,
            'type': reservoir_type if reservoir_type else None,
            'capacity': capacity,
            'damType': dam_type if dam_type else None,
            'maxHeight': max_height
        }
        
        # Remove None values
        reservoir = {k: v for k, v in reservoir.items() if v is not None and v != ''}
        
        reservoirs.append(reservoir)
        
        # Update province statistics
        province_stats[province]['reservoirs'].append(reservoir_id)
        province_stats[province]['totalCount'] += 1
        
        if dam_type:
            province_stats[province]['damTypes'][dam_type] += 1
        
        if basin:
            province_stats[province]['basins'][basin] += 1
    
    print(f"Processed {len(reservoirs)} reservoirs")
    print(f"Provinces: {len(province_stats)}")
    
    # Convert province stats to regular dict
    province_stats_output = {}
    for province, stats in province_stats.items():
        province_stats_output[province] = {
            'totalCount': stats['totalCount'],
            'reservoirs': stats['reservoirs'],
            'damTypes': dict(stats['damTypes']),
            'basins': dict(stats['basins'])
        }
    
    # Save to JSON files
    print("\nSaving data...")
    
    # Save reservoirs
    with open('web/src/data/reservoirs.json', 'w', encoding='utf-8') as f:
        json.dump(reservoirs, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved {len(reservoirs)} reservoirs to web/src/data/reservoirs.json")
    
    # Save province statistics
    with open('web/src/data/provinceStats.json', 'w', encoding='utf-8') as f:
        json.dump(province_stats_output, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved statistics for {len(province_stats_output)} provinces to web/src/data/provinceStats.json")
    
    # Create unique locations list for geocoding
    locations = list(set([r['location'] for r in reservoirs if 'location' in r]))
    with open('web/src/data/locations.json', 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved {len(locations)} unique locations to web/src/data/locations.json")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total reservoirs: {len(reservoirs)}")
    print(f"Total provinces: {len(province_stats_output)}")
    print(f"\nTop 10 provinces by reservoir count:")
    sorted_provinces = sorted(province_stats_output.items(), key=lambda x: x[1]['totalCount'], reverse=True)
    for province, stats in sorted_provinces[:10]:
        print(f"  {province}: {stats['totalCount']} reservoirs")
    
    print("\nDam types distribution:")
    all_dam_types = defaultdict(int)
    for stats in province_stats_output.values():
        for dam_type, count in stats['damTypes'].items():
            all_dam_types[dam_type] += count
    for dam_type, count in sorted(all_dam_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {dam_type}: {count}")
    
    print("\nBasin distribution:")
    all_basins = defaultdict(int)
    for stats in province_stats_output.values():
        for basin, count in stats['basins'].items():
            all_basins[basin] += count
    for basin, count in sorted(all_basins.items(), key=lambda x: x[1], reverse=True):
        print(f"  {basin}: {count}")

if __name__ == '__main__':
    main()
