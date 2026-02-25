import json
import os
import glob
import sys

try:
    with open("staging/mappings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    sys.exit(1)

data["format_version"] = 2
new_items = {}

item_texture = {}
item_texture_path = "staging/target/rp/textures/item_texture.json"
if os.path.exists(item_texture_path):
    with open(item_texture_path, "r", encoding="utf-8") as f:
        item_texture = json.load(f)

for material, items_list in data.get("items", {}).items():
    material_name = material.split(":")[-1]
    new_items[material] = []
    
    if material_name == "fishing_rod":
        fishing_rod_groups = {}  # Key: custom_model_data, Value: {normal, cast}
        
        for item in items_list:
            item_name = item.get("name")
            custom_model_data = item.get("custom_model_data")
            tags = item.get("tags", [])
            
            attachable_files = glob.glob("staging/target/rp/attachables/**/*.json", recursive=True)
            
            for file_path in attachable_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        attachable_data = json.load(f)
                    
                    identifier = attachable_data.get("minecraft:attachable", {}).get("description", {}).get("identifier", "")
                    
                    if f"geyser_custom:{item_name}" in identifier:
                        rel_path = os.path.relpath(file_path, "staging/target/rp/attachables")
                        rel_path = rel_path.replace(".json", "")
                        
                        bedrock_identifier = rel_path.replace("/", ":", 1).replace("\\", ":", 1)
                        icon = bedrock_identifier.replace(":", ".").replace("/", "_").replace("\\", "_")
                        
                        is_cast = "_cast" in bedrock_identifier
                        
                        if custom_model_data not in fishing_rod_groups:
                            fishing_rod_groups[custom_model_data] = {}
                        
                        if is_cast:
                            base_identifier = bedrock_identifier.replace("_cast", "")
                            base_icon = icon.replace("_cast", "")
                            fishing_rod_groups[custom_model_data]["cast"] = {
                                "identifier": bedrock_identifier,
                                "icon": icon,
                                "base_identifier": base_identifier,
                                "base_icon": base_icon
                            }
                        else:
                            fishing_rod_groups[custom_model_data]["normal"] = {
                                "identifier": bedrock_identifier,
                                "icon": icon
                            }
                        
                        attachable_data["minecraft:attachable"]["description"]["identifier"] = bedrock_identifier
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(attachable_data, f, indent=2, ensure_ascii=False)
                        
                        if item_name in item_texture.get("texture_data", {}):
                            texture_value = item_texture["texture_data"][item_name]
                            del item_texture["texture_data"][item_name]
                            
                            # Cập nhật texture path để khớp với file name
                            if isinstance(texture_value, dict) and "textures" in texture_value:
                                old_path = texture_value["textures"]
                                # Thay thế phần cuối của path bằng tên file hiện tại
                                path_parts = old_path.rsplit("/", 1)
                                if len(path_parts) == 2:
                                    # Lấy tên file từ bedrock_identifier (phần sau dấu :)
                                    file_name = bedrock_identifier.split(":")[-1].replace(":", "/")
                                    texture_value["textures"] = f"{path_parts[0]}/{file_name}"
                            
                            item_texture["texture_data"][icon] = texture_value
                        
                        break
                except:
                    pass
        
        for cmd, rod_items in fishing_rod_groups.items():
            if "normal" in rod_items:
                base_id = rod_items["normal"]["identifier"]
                base_icon = rod_items["normal"]["icon"]
            elif "cast" in rod_items:
                base_id = rod_items["cast"]["base_identifier"]
                base_icon = rod_items["cast"]["base_icon"]
            else:
                continue
            
            cast_id = rod_items.get("cast", {}).get("identifier", base_id + "_cast")
            cast_icon = rod_items.get("cast", {}).get("icon", base_icon + "_cast")
            
            # Tạo texture entries cho cả normal và cast
            has_cast = cast_icon in item_texture.get("texture_data", {})
            has_normal = base_icon in item_texture.get("texture_data", {})
            
            if has_cast and not has_normal:
                # Có cast, thiếu normal → tạo normal từ cast
                cast_texture = item_texture["texture_data"][cast_icon]
                if isinstance(cast_texture, dict) and "textures" in cast_texture:
                    normal_texture_path = cast_texture["textures"].replace("_cast", "")
                    item_texture["texture_data"][base_icon] = {"textures": normal_texture_path}
            elif has_normal and not has_cast:
                # Có normal, thiếu cast → tạo cast từ normal
                normal_texture = item_texture["texture_data"][base_icon]
                if isinstance(normal_texture, dict) and "textures" in normal_texture:
                    cast_texture_path = normal_texture["textures"] + "_cast"
                    item_texture["texture_data"][cast_icon] = {"textures": cast_texture_path}
            
            new_item = {
                "type": "group",
                "definitions": [
                    {
                        "bedrock_identifier": base_id,
                        "priority": 1,
                        "custom_model_data": cmd,
                        "icon": base_icon,
                        "type": "legacy",
                        "bedrock_options": {"creative_category": "items"}
                    },
                    {
                        "predicate": {
                            "type": "condition",
                            "property": "fishing_rod_cast"
                        },
                        "bedrock_identifier": cast_id,
                        "priority": 2,
                        "custom_model_data": cmd,
                        "icon": cast_icon,
                        "type": "legacy",
                        "bedrock_options": {"creative_category": "items"}
                    }
                ]
            }
            new_items[material].append(new_item)
        
        # Update identifier trong attachable files dựa vào bedrock_identifier trong groups
        for new_item in new_items[material]:
            if new_item.get("type") == "group":
                for definition in new_item.get("definitions", []):
                    bedrock_id = definition.get("bedrock_identifier")
                    if bedrock_id and ":" in bedrock_id:
                        # Parse: "elitecreatures:heavenly_emperor_animated/fishing_rod_cast"
                        # → staging/target/rp/attachables/elitecreatures/heavenly_emperor_animated/fishing_rod_cast.json
                        path_after_attachables = bedrock_id.replace(":", "/", 1)
                        attachable_path = f"staging/target/rp/attachables/{path_after_attachables}.json"
                        
                        if os.path.exists(attachable_path):
                            try:
                                with open(attachable_path, "r", encoding="utf-8") as f:
                                    attachable_data = json.load(f)
                                attachable_data["minecraft:attachable"]["description"]["identifier"] = bedrock_id
                                with open(attachable_path, "w", encoding="utf-8") as f:
                                    json.dump(attachable_data, f, indent=2, ensure_ascii=False)
                            except:
                                pass
        
        continue
    
    for item in items_list:
        item_name = item.get("name")
        custom_model_data = item.get("custom_model_data")
        tags = item.get("tags", [])
        
        attachable_files = glob.glob("staging/target/rp/attachables/**/*.json", recursive=True)
        
        for file_path in attachable_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    attachable_data = json.load(f)
                
                identifier = attachable_data.get("minecraft:attachable", {}).get("description", {}).get("identifier", "")
                
                if f"geyser_custom:{item_name}" in identifier:
                    rel_path = os.path.relpath(file_path, "staging/target/rp/attachables")
                    rel_path = rel_path.replace(".json", "")
                    
                    bedrock_identifier = rel_path.replace("/", ":", 1).replace("\\", ":", 1)
                    icon = bedrock_identifier.replace(":", ".").replace("/", "_").replace("\\", "_")
                    
                    attachable_data["minecraft:attachable"]["description"]["identifier"] = bedrock_identifier
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(attachable_data, f, indent=2, ensure_ascii=False)
                    
                    if item_name in item_texture.get("texture_data", {}):
                        texture_value = item_texture["texture_data"][item_name]
                        del item_texture["texture_data"][item_name]
                        
                        if material_name == "fishing_rod" and isinstance(texture_value, dict):
                            texture_path = texture_value.get("textures", "")
                            if "_rod" in texture_path:
                                item_texture["texture_data"][icon + "_cast"] = texture_value
                            else:
                                item_texture["texture_data"][icon] = texture_value
                        else:
                            item_texture["texture_data"][icon] = texture_value
                    
                    if material_name == "fishing_rod":
                        cast_identifier = bedrock_identifier + "_cast"
                        cast_icon = icon + "_cast"
                        
                        new_item = {
                            "type": "group",
                            "definitions": [
                                {
                                    "bedrock_identifier": bedrock_identifier,
                                    "priority": 1,
                                    "custom_model_data": custom_model_data,
                                    "icon": icon,
                                    "type": "legacy",
                                    "bedrock_options": {"creative_category": "items"}
                                },
                                {
                                    "predicate": {
                                        "type": "condition",
                                        "property": "fishing_rod_cast"
                                    },
                                    "bedrock_identifier": cast_identifier,
                                    "priority": 2,
                                    "custom_model_data": custom_model_data,
                                    "icon": cast_icon,
                                    "type": "legacy",
                                    "bedrock_options": {"creative_category": "items"}
                                }
                            ]
                        }
                    else:
                        new_item = {
                            "bedrock_identifier": bedrock_identifier,
                            "custom_model_data": custom_model_data,
                            "icon": icon,
                            "type": "legacy",
                            "bedrock_options": {"creative_category": "items"}
                        }
                        if tags:
                            new_item["tags"] = tags
                    
                    new_items[material].append(new_item)
                    break
            except Exception as e:
                pass

data["items"] = new_items
data["items"] = {k: v for k, v in new_items.items() if v}

# Tách blocks ra file riêng (mappingsv1.json)
if "blocks" in data:
    blocks_data = {
        "format_version": 1,
        "blocks": data["blocks"]
    }
    with open("staging/mappingsv1.json", "w", encoding="utf-8") as f:
        json.dump(blocks_data, f, indent=2, ensure_ascii=False)
    
    # Xóa blocks khỏi data trước khi lưu mappingsv2.json
    del data["blocks"]

# Lưu items vào mappingsv2.json (chỉ chạy khi v2)
with open("staging/mappingsv2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Created mappingsv2.json (item_model format)")

# Xóa file gốc mappings.json
if os.path.exists("staging/mappings.json"):
    os.remove("staging/mappings.json")

if item_texture and os.path.exists(item_texture_path):
    # Fix duplicate paths in texture_data
    import re
    for key, value in item_texture.get("texture_data", {}).items():
        if isinstance(value, dict) and "textures" in value:
            texture_path = value["textures"]
            original_path = texture_path
            
            # Fix pattern 1: /segment/segment/ (single segment duplicate)
            pattern1 = r'/([^/]+)/\1/'
            while re.search(pattern1, texture_path):
                texture_path = re.sub(pattern1, r'/\1/', texture_path)
            
            # Fix pattern 2: /segment1/segment2/segment1/segment2/ (two segments duplicate)
            pattern2 = r'/([^/]+)/([^/]+)/\1/\2/'
            while re.search(pattern2, texture_path):
                texture_path = re.sub(pattern2, r'/\1/\2/', texture_path)
            
            if texture_path != original_path:
                value["textures"] = texture_path
    
    with open(item_texture_path, "w", encoding="utf-8") as f:
        json.dump(item_texture, f, indent=2, ensure_ascii=False)

# Cleanup _iainternal folders after processing mappings
import shutil
unwanted_dirs = [
    "staging/target/rp/animations/_iainternal",
    "staging/target/rp/attachables/_iainternal",
    "staging/target/rp/models/entity/_iainternal"
]

for dir_path in unwanted_dirs:
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except Exception:
            pass

# Minify all JSON files
def minify_json_file(file_path):
    """Nén JSON file thành 1 dòng"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
        
        return True
    except:
        return False

def minify_all_json(directory):
    """Nén tất cả JSON files trong directory"""
    json_files = glob.glob(f"{directory}/**/*.json", recursive=True)
    
    for json_file in json_files:
        # Bỏ qua mappings.json - nếu không có mappingsv1.json thì đổi tên mappingsv2.json thành mappings.json
        if json_file.endswith("mappings.json") or json_file.endswith("mappingsv1.json") or json_file.endswith("mappingsv2.json"):
            continue
        minify_json_file(json_file)

if os.path.exists("staging/target/rp"):
    minify_all_json("staging/target/rp")
