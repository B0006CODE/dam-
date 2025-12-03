#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为兵团等特殊行政区的水库设置坐标
基于现有坐标或地理位置推断
"""

import json

# 特殊行政区水库的坐标映射
# key: name
# value: {'coords': [lon, lat], 'province_keyword': str}
SPECIAL_COORDINATES = {
    # 新疆生产建设兵团水库
    "永安坝北库": {"coords": [79.92, 40.62], "province_keyword": "兵团"},
    "永安坝南库": {"coords": [79.92, 40.60], "province_keyword": "兵团"},
    "冰湖水库": {"coords": [86.15, 43.82], "province_keyword": "兵团"},
    "胜利水库": {"coords": [86.05, 44.30], "province_keyword": "兵团"},
    "西大桥": {"coords": [81.28, 40.54], "province_keyword": "兵团"},
    "新井子": {"coords": [81.28, 40.52], "province_keyword": "兵团"},
    "夹河子水库": {"coords": [86.60, 44.31], "province_keyword": "兵团"},
    "多浪水库": {"coords": [81.28, 40.55], "province_keyword": "兵团"},
    
    # 新疆其他难点水库
    "头屯河水库": {"coords": [87.30, 43.85], "province_keyword": "新疆"},
    "白碱滩水库": {"coords": [85.13, 45.69], "province_keyword": "新疆"},
    "黄羊泉水库": {"coords": [85.69, 46.09], "province_keyword": "新疆"},
    "车排子水库": {"coords": [84.90, 44.42], "province_keyword": "新疆"},
    "大泉沟水库": {"coords": [86.21, 43.82], "province_keyword": "新疆"},
    "红岩水库": {"coords": [87.62, 43.79], "province_keyword": "新疆"},
    "乌拉斯台水库": {"coords": [82.98, 46.75], "province_keyword": "新疆"},
    "鹰湖水库": {"coords": [87.52, 44.31], "province_keyword": "新疆"},
    
    # 广西特殊地区
    "土桥": {"coords": [108.64, 24.48], "province_keyword": "广西"},
}

def update_special_coordinates():
    """为特殊行政区水库更新坐标"""
    print("Loading reservoir data...")
    with open('web/src/data/reservoirs.json', 'r', encoding='utf-8') as f:
        reservoirs = json.load(f)
    
    updated_count = 0
    skipped_count = 0
    
    print(f"\nUpdating special administrative region reservoirs...")
    for reservoir in reservoirs:
        name = reservoir.get('name', '')
        province = reservoir.get('province', '')
        
        if name in SPECIAL_COORDINATES:
            target_info = SPECIAL_COORDINATES[name]
            keyword = target_info['province_keyword']
            
            # Check if province matches (or contains the keyword)
            if keyword in province:
                old_coords = reservoir.get('coordinates')
                new_coords = target_info['coords']
                reservoir['coordinates'] = new_coords
                updated_count += 1
                
                city = reservoir.get('city', '')
                county = reservoir.get('county', '')
                
                print(f"✓ {name} ({province}/{city}/{county})")
                print(f"  {old_coords} -> {new_coords}")
            else:
                skipped_count += 1
                # print(f"Skipped {name} in {province} (expected {keyword})")
    
    # Save updated data
    print(f"\nSaving updated data...")
    with open('web/src/data/reservoirs.json', 'w', encoding='utf-8') as f:
        json.dump(reservoirs, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Updated {updated_count} special region reservoirs")
    print(f"ℹ️  Skipped {skipped_count} reservoirs with same names but different provinces")

if __name__ == '__main__':
    update_special_coordinates()
