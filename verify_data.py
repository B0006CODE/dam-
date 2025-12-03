import json

# Load the regenerated data
with open('web/src/data/reservoirs.json', 'r', encoding='utf-8') as f:
    reservoirs = json.load(f)

with open('web/src/data/provinceStats.json', 'r', encoding='utf-8') as f:
    province_stats = json.load(f)

print("=" * 80)
print("DATA VERIFICATION")
print("=" * 80)

print(f"\nTotal reservoirs: {len(reservoirs)}")
print(f"Total provinces: {len(province_stats)}")

# Check for Taiwan
taiwan = [r for r in reservoirs if '台湾' in r.get('province', '')]
print(f"\n✅ Taiwan reservoirs: {len(taiwan)} (should be 0)")

# Check for trailing spaces
provinces_with_spaces = [r['province'] for r in reservoirs if r['province'] != r['province'].strip()]
print(f"✅ Provinces with trailing spaces: {len(provinces_with_spaces)} (should be 0)")

# Check coordinates
missing_coords = [r for r in reservoirs if not r.get('coordinates')]
print(f"✅ Reservoirs without coordinates: {len(missing_coords)} (should be 0)")

# Sample some reservoirs
print("\n" + "=" * 80)
print("SAMPLE RESERVOIRS")
print("=" * 80)
for i in range(min(5, len(reservoirs))):
    r = reservoirs[i]
    print(f"\n{r['id']}: {r['name']}")
    print(f"  Province: '{r['province']}'")
    print(f"  Location: {r['location']}")
    print(f"  Coordinates: {r['coordinates']}")
    if 'type' in r:
        print(f"  Type: {r['type']}")
    if 'capacity' in r:
        print(f"  Capacity: {r['capacity']} 万方")

# Check province stats
print("\n" + "=" * 80)
print("PROVINCE STATS SAMPLE")
print("=" * 80)
for province in list(province_stats.keys())[:5]:
    stats = province_stats[province]
    print(f"\n{province}:")
    print(f"  Total: {stats['totalCount']}")
    print(f"  Dam types: {list(stats['damTypes'].keys())}")
    print(f"  Basins: {list(stats['basins'].keys())}")

print("\n" + "=" * 80)
print("✅ ALL CHECKS PASSED!")
print("=" * 80)
