import pandas as pd
import json
import requests

# Read Excel file
print("Reading Excel file...")
df = pd.read_excel('水库信息.xlsx', header=0)

# Remove the header row if it exists
if df.iloc[0]['水库地点'] == '所在省份':
    df = df.iloc[1:].reset_index(drop=True)

print(f"Total reservoirs: {len(df)}")

# County coordinates mapping (approximate center coordinates)
county_coords = {}

def get_coordinates(province, city, county):
    """Get coordinates for a location using geocoding API or fallback"""
    # This is a simplified version - in production you'd use a proper geocoding service
    # For now, we'll use approximate province center coordinates
    
    province_centers = {
        '福建': [119.3, 26.1],
        '湖北': [114.3, 30.6],
        '吉林': [126.5, 43.9],
        '江苏': [118.8, 32.0],
        '山东': [117.0, 36.7],
        '广西': [108.3, 22.8],
        '贵州': [106.7, 26.6],
        '湖南': [112.0, 28.2],
        '四川': [104.1, 30.7],
        '甘肃': [103.8, 36.1],
        '广东': [113.3, 23.1],
        '黑龙江': [126.6, 45.8],
        '河北': [114.5, 38.0],
        '河南': [113.7, 34.8],
        '江西': [115.9, 28.7],
        '辽宁': [123.4, 41.8],
        '内蒙古': [111.7, 40.8],
        '宁夏': [106.3, 38.5],
        '青海': [101.8, 36.6],
        '山西': [112.5, 37.9],
        '陕西': [108.9, 34.3],
        '云南': [102.7, 25.0],
        '浙江': [120.2, 30.3],
        '重庆': [106.5, 29.6],
        '安徽': [117.3, 31.9],
        '海南': [110.3, 20.0],
        '新疆': [87.6, 43.8],
        '西藏': [91.1, 29.7],
        '兵团': [87.6, 44.0],
        '新疆兵团': [87.6, 44.0]
    }
    
    # Clean province name
    province_clean = province.strip()
    
    # Get base coordinates
    base_coords = province_centers.get(province_clean, [105.0, 35.0])
    
    # Add some variation based on city/county to spread points
    import hashlib
    location_str = f"{province_clean}{city}{county}"
    hash_val = int(hashlib.md5(location_str.encode()).hexdigest(), 16)
    
    # Add random offset within province (±2 degrees)
    offset_lon = ((hash_val % 400) - 200) / 100.0
    offset_lat = ((hash_val // 400 % 400) - 200) / 100.0
    
    return [base_coords[0] + offset_lon, base_coords[1] + offset_lat]

# Convert data
reservoirs = []
for idx, row in df.iterrows():
    try:
        reservoir_id = str(row['序号']).strip() if pd.notna(row['序号']) else f"R-{idx+1:04d}"
        name = str(row['水库名称']).strip() if pd.notna(row['水库名称']) else f"水库{idx+1}"
        province = str(row['水库地点']).strip() if pd.notna(row['水库地点']) else ""
        city = str(row['Unnamed: 3']).strip() if pd.notna(row['Unnamed: 3']) else ""
        county = str(row['Unnamed: 4']).strip() if pd.notna(row['Unnamed: 4']) else ""
        basin = str(row['所在流域']).strip() if pd.notna(row['所在流域']) else None
        reservoir_type = str(row['水库型别']).strip() if pd.notna(row['水库型别']) else None
        capacity = float(row['总库容\n（万方）']) if pd.notna(row['总库容\n（万方）']) else None
        dam_type = str(row['主坝坝型']).strip() if pd.notna(row['主坝坝型']) else None
        max_height = float(row['最大坝高\n（m）']) if pd.notna(row['最大坝高\n（m）']) else None
        
        # Skip if essential data is missing
        if not name or not province:
            continue
        
        # Get coordinates
        coordinates = get_coordinates(province, city, county)
        
        # Build location string
        location_parts = [province]
        if city:
            location_parts.append(city)
        if county:
            location_parts.append(county)
        location = ''.join(location_parts)
        
        reservoir = {
            'id': reservoir_id,
            'name': name,
            'province': province,  # Already stripped
            'location': location,
            'coordinates': coordinates
        }
        
        # Add optional fields
        if city:
            reservoir['city'] = city
        if county:
            reservoir['county'] = county
        if basin and basin != 'nan':
            reservoir['basin'] = basin
        if reservoir_type and reservoir_type != 'nan':
            reservoir['type'] = reservoir_type
        if capacity is not None:
            reservoir['capacity'] = capacity
        if dam_type and dam_type != 'nan':
            reservoir['damType'] = dam_type
        if max_height is not None:
            reservoir['maxHeight'] = max_height
        
        reservoirs.append(reservoir)
        
    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        continue

print(f"\nSuccessfully processed {len(reservoirs)} reservoirs")

# Verify no Taiwan
taiwan_count = sum(1 for r in reservoirs if '台湾' in r['province'])
print(f"Taiwan reservoirs: {taiwan_count}")

# Check province distribution
provinces = {}
for r in reservoirs:
    p = r['province']
    if p not in provinces:
        provinces[p] = 0
    provinces[p] += 1

print(f"\nTotal unique provinces: {len(provinces)}")
print("\nProvince distribution:")
for province, count in sorted(provinces.items()):
    print(f"  {province}: {count}")

# Save to JSON
output_file = 'web/src/data/reservoirs.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(reservoirs, f, ensure_ascii=False, indent=2)

print(f"\n✅ Data saved to {output_file}")

# Also generate province stats
province_stats = {}
for reservoir in reservoirs:
    province = reservoir['province']
    
    if province not in province_stats:
        province_stats[province] = {
            'totalCount': 0,
            'reservoirs': [],
            'damTypes': {},
            'basins': {}
        }
    
    stats = province_stats[province]
    stats['totalCount'] += 1
    stats['reservoirs'].append(reservoir['id'])
    
    # Count dam types
    dam_type = reservoir.get('damType', '未知')
    if dam_type not in stats['damTypes']:
        stats['damTypes'][dam_type] = 0
    stats['damTypes'][dam_type] += 1
    
    # Count basins
    basin = reservoir.get('basin', '未知')
    if basin not in stats['basins']:
        stats['basins'][basin] = 0
    stats['basins'][basin] += 1

# Save province stats
stats_file = 'web/src/data/provinceStats.json'
with open(stats_file, 'w', encoding='utf-8') as f:
    json.dump(province_stats, f, ensure_ascii=False, indent=2)

print(f"✅ Province stats saved to {stats_file}")
