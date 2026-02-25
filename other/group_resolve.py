import json
import os
from pathlib import Path

def remove_empty_files():
    """Xóa các file JSON rỗng hoặc không có nội dung"""
    models_dir = Path("staging/target/rp/models/entity")
    removed_count = 0
    
    for json_file in models_dir.rglob("*.json"):
        try:
            if json_file.stat().st_size == 0:
                json_file.unlink()
                removed_count += 1
            else:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not data or data == {}:
                    json_file.unlink()
                    removed_count += 1
        except:
            json_file.unlink()
            removed_count += 1
    
    return removed_count

def resolve_groups():
    """Gộp rot_ bones hoặc cubes từ campfire_z thành 1 bone camfire_item"""
    models_dir = Path("staging/target/rp/models/entity")
    
    for json_file in models_dir.rglob("*.json"):
        # Bỏ qua campfire_block.json và campfire_tool_custom.json
        if json_file.name in ["campfire_block.json", "campfire_tool_custom.json"]:
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for geometry in data.get("minecraft:geometry", []):
                bones = geometry.get("bones", [])
                
                # Tìm rot_ bones
                rot_bones = [bone for bone in bones if bone.get("parent") == "campfire_z" and bone.get("name", "").startswith("rot_")]
                
                if rot_bones:
                    # Trường hợp 1: Có rot_ bones
                    all_cubes = []
                    for rot_bone in rot_bones:
                        for cube in rot_bone.get("cubes", []):
                            if "pivot" in rot_bone:
                                cube["pivot"] = rot_bone["pivot"]
                            if "rotation" in rot_bone:
                                cube["rotation"] = rot_bone["rotation"]
                            all_cubes.append(cube)
                    
                    # Xóa rot_ bones và tạo camfire_item
                    geometry["bones"] = [bone for bone in bones if not (bone.get("parent") == "campfire_z" and bone.get("name", "").startswith("rot_"))]
                    geometry["bones"].append({
                        "name": "camfire_item",
                        "parent": "campfire_z",
                        "pivot": [0, 8, 0],
                        "cubes": all_cubes
                    })
                else:
                    # Trường hợp 2: Chỉ có campfire_z với cubes
                    for bone in bones:
                        if bone.get("name") == "campfire_z" and "cubes" in bone:
                            geometry["bones"].append({
                                "name": "camfire_item",
                                "parent": "campfire_z",
                                "pivot": [0, 8, 0],
                                "cubes": bone["cubes"]
                            })
                            del bone["cubes"]
                            break
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
                
        except Exception:
            continue

if __name__ == "__main__":
    resolve_groups()
    remove_empty_files()