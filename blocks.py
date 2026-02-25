import json
from pathlib import Path

print()
print("🚀 Bắt đầu xử lý converter blocks")

# Tạo geometry file
geometry_data = {"format_version":"1.21.0","minecraft:geometry":[{"description":{"identifier":"geometry.campfire_block","texture_width":16,"texture_height":16,"visible_bounds_width":6,"visible_bounds_height":6,"visible_bounds_offset":[0,2,0]},"bones":[{"name":"campfire","pivot":[0,8,0],"binding":"c.item_slot == 'head' ? 'head' : q.item_slot_to_bone_name(c.item_slot)"},{"name":"campfire_x","parent":"campfire","pivot":[0,8,0]},{"name":"campfire_y","parent":"campfire_x","pivot":[0,8,0]},{"name":"campfire_z","parent":"campfire_y","pivot":[0,8,0],"cubes":[{"origin":[-8,0,-8],"size":[16,16,16],"uv":{"north":{"uv":[0,0],"uv_size":[16,16]},"east":{"uv":[0,0],"uv_size":[16,16]},"south":{"uv":[0,0],"uv_size":[16,16]},"west":{"uv":[0,0],"uv_size":[16,16]},"up":{"uv":[16,16],"uv_size":[-16,-16]},"down":{"uv":[16,16],"uv_size":[-16,-16]}}}]}]}]}

Path("staging/target/rp/textures/campfire_block").mkdir(parents=True, exist_ok=True)
with open("staging/target/rp/models/entity/campfire_block.json", 'w', encoding='utf-8') as f:
    json.dump(geometry_data, f, separators=(',', ':'), ensure_ascii=False)

# Tạo animation file
animation_data = {"format_version":"1.8.0","animations":{"animation.campfire_block.thirdperson_main_hand":{"loop":True,"bones":{"campfire_x":{"rotation":[-75,0,0],"position":[0,2.5,0],"scale":0.375},"campfire_y":{"rotation":[0,-45,0]},"campfire":{"rotation":[90,0,0],"position":[0,13,-3]}}},"animation.campfire_block.thirdperson_off_hand":{"loop":True,"bones":{"campfire_x":{"rotation":[-75,0,0],"position":[0,2.5,0],"scale":0.375},"campfire_y":{"rotation":[0,-45,0]},"campfire":{"rotation":[90,0,0],"position":[0,13,-3]}}},"animation.campfire_block.firstperson_main_hand":{"loop":True,"bones":{"campfire":{"rotation":[90,60,-40],"position":[-2.68272,26.05571,1.643]},"campfire_x":{"position":[-2,0,0]},"campfire_y":{"rotation":[0,-52.5,0],"position":[7,6,2]},"campfire_z":{"rotation":[0,0,-2.5],"position":[-9,0,-1],"scale":0.45}}},"animation.campfire_block.firstperson_off_hand":{"loop":True,"bones":{"campfire":{"rotation":[90,60,-40],"position":[4,10,4],"scale":1.5},"campfire_x":{"scale":[0.4,0.4,0.4]},"campfire_y":{"rotation":[0,-225,0]}}}}}

with open("staging/target/rp/animations/campfire_block.json", 'w', encoding='utf-8') as f:
    json.dump(animation_data, f, separators=(',', ':'), ensure_ascii=False)

# Đọc blockstates và lưu model paths
model_variants = {}
block_files = {}
blockstates_path = Path("./pack/assets/minecraft/blockstates")
for json_file in blockstates_path.glob("*.json"):
    block_name = f"minecraft:{json_file.stem}"
    block_files[block_name] = json_file.stem
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for variant_key, variant_data in data.get("variants", {}).items():
        model_path = variant_data.get("model", "")
        if not model_path.startswith("block/"):
            model_variants[model_path] = (variant_key, block_name)

# Đọc models/item và tìm custom_model_data
model_cmd_map = {}
models_path = Path("./pack/assets/minecraft/models/item")
for json_file in models_path.glob("*.json"):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for override in data.get("overrides", []):
        model = override.get("model", "")
        cmd = override.get("predicate", {}).get("custom_model_data")
        if model in model_variants and cmd:
            # Đọc model file để check loại
            model_file_path = Path(f"./pack/assets/{model.replace(':', '/models/')}.json")
            if model_file_path.exists():
                try:
                    with open(model_file_path, 'r', encoding='utf-8') as mf:
                        model_data = json.load(mf)
                    has_parent = "parent" in model_data
                    has_elements = "elements" in model_data
                    if has_elements:
                        model_cmd_map[model] = {"cmd": cmd, "material": f"minecraft:{json_file.stem}", "type": "elements"}
                    elif has_parent:
                        model_cmd_map[model] = {"cmd": cmd, "material": f"minecraft:{json_file.stem}", "type": "parent"}
                except:
                    pass

# Đọc mappings và tìm name
with open("./staging/mappings.json", 'r', encoding='utf-8') as f:
    mappings = json.load(f)

names_found = []
terrain_data = {}
for model_path, info in model_cmd_map.items():
    material = info["material"]
    cmd = info["cmd"]
    for item in mappings.get("items", {}).get(material, []):
        if item.get("custom_model_data") == cmd:
            names_found.append(item['name'])

# Tìm blocks 16x16x16 bằng cách check file rỗng trong models/entity
blocks_16x16_names = set()
models_entity_path = Path("staging/target/rp/models/entity")
attachables_path = Path("staging/target/rp/attachables")
if models_entity_path.exists():
    for model_file in models_entity_path.rglob("*.json"):
        if model_file.stat().st_size == 0:
            # Tìm attachable tương ứng
            attachable_file = attachables_path / model_file.relative_to(models_entity_path)
            if attachable_file.exists():
                try:
                    with open(attachable_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    identifier = data.get("minecraft:attachable", {}).get("description", {}).get("identifier", "")
                    if identifier.startswith("geyser_custom:"):
                        name = identifier.replace("geyser_custom:", "")
                        blocks_16x16_names.add(name)
                except Exception as e:
                    continue

# Quét attachables và thay thế
import shutil
attachables_path = Path("staging/target/rp/attachables")
processed_count = 0
geometry_map = {}

# Tạo danh sách model names từ blockstates
model_names = set()
for model_path in model_variants.keys():
    model_name = model_path.split("/")[-1]
    model_names.add(model_name)

# Quét tất cả JSON files trong attachables
for json_file in attachables_path.rglob("*.json"):
    file_name = json_file.stem
    
    if file_name in model_names:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            identifier = data.get("minecraft:attachable", {}).get("description", {}).get("identifier", "")
            if identifier.startswith("geyser_custom:"):
                name = identifier.replace("geyser_custom:", "")
                
                # Đọc geometry cũ
                old_geometry = data.get("minecraft:attachable", {}).get("description", {}).get("geometry", {}).get("default", "geometry.block")
                
                # Lấy đường dẫn texture cũ
                old_texture = data.get("minecraft:attachable", {}).get("description", {}).get("textures", {}).get("default", "")
                texture_name = name
                
                if old_texture:
                    texture_parts = old_texture.split("/")
                    if len(texture_parts) >= 3:
                        folder_name = texture_parts[1]
                        file_name_texture = texture_parts[2]
                        texture_name = file_name_texture
                        
                        # Tìm và di chuyển file ảnh
                        source_folder = Path(f"staging/target/rp/textures/{folder_name}")
                        for img_file in source_folder.glob(f"{file_name_texture}.*"):
                            dest_path = Path(f"staging/target/rp/textures/campfire_block/{file_name_texture}.png")
                            shutil.move(str(img_file), str(dest_path))
                            break
                
                # Thêm vào terrain_data
                terrain_data[f"block_{name}"] = {"textures": f"textures/campfire_block/{texture_name}"}
                
                # Check xem có phải block 16x16x16 không (dựa vào name trong blocks_16x16_names)
                is_16x16 = name in blocks_16x16_names
                
                if is_16x16:
                    # Block 16x16x16 - dùng geometry.campfire_block
                    geometry_map[name] = "geometry.campfire_block"
                    new_data = {
                        "format_version": "1.10.0",
                        "minecraft:attachable": {
                            "description": {
                                "identifier": f"geyser_custom:{name}",
                                "materials": {"default": "entity_alphatest_one_sided", "enchanted": "entity_alphatest_glint"},
                                "textures": {"default": f"textures/campfire_block/{texture_name}", "enchanted": "textures/misc/enchanted_item_glint"},
                                "geometry": {"default": "geometry.campfire_block"},
                                "scripts": {
                                    "pre_animation": ["v.main_hand = c.item_slot == 'main_hand';", "v.off_hand = c.item_slot == 'off_hand';", "v.head = c.item_slot == 'head';"],
                                    "animate": [{"thirdperson_main_hand": "v.main_hand && !c.is_first_person"}, {"thirdperson_off_hand": "v.off_hand && !c.is_first_person"}, {"thirdperson_head": "v.head && !c.is_first_person"}, {"firstperson_main_hand": "v.main_hand && c.is_first_person"}, {"firstperson_off_hand": "v.off_hand && c.is_first_person"}, {"firstperson_head": "c.is_first_person && v.head"}]
                                },
                                "animations": {"thirdperson_main_hand": "animation.campfire_block.thirdperson_main_hand", "thirdperson_off_hand": "animation.campfire_block.thirdperson_off_hand", "thirdperson_head": "animation.geyser_custom.disable", "firstperson_main_hand": "animation.campfire_block.firstperson_main_hand", "firstperson_off_hand": "animation.campfire_block.firstperson_off_hand", "firstperson_head": "animation.geyser_custom.disable"},
                                "render_controllers": ["controller.render.item_default"]
                            }
                        }
                    }
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(new_data, f, separators=(',', ':'), ensure_ascii=False)
                    # Hiển thị đường dẫn tương đối
                    relative_path = json_file.relative_to(attachables_path)
                    print(f"✅ Xử lý block 16x16: {relative_path}")
                else:
                    # Block 3D - dùng item_utils với geometry gốc
                    geometry_map[name] = old_geometry
                    from item_utils import Item_Util
                    materials = {"default": "entity_alphatest_one_sided", "enchanted": "entity_alphatest_glint"}
                    textures = {"default": f"textures/campfire_block/{texture_name}", "enchanted": "textures/misc/enchanted_item_glint"}
                    geometry = {"default": old_geometry}
                    Item_Util.update_attachable(str(json_file), identifier, materials, textures, geometry, {})
                    # Hiển thị đường dẫn tương đối
                    relative_path = json_file.relative_to(attachables_path)
                    print(f"✅ Xử lý block 3D: {relative_path}")
                processed_count += 1
        except Exception as e:
            # Hiển thị block không được convert
            relative_path = json_file.relative_to(attachables_path)
            print(f"❌ Không xử lý được block: {relative_path}")
            continue

# Cập nhật terrain_texture.json
with open("staging/target/rp/textures/terrain_texture.json", 'r', encoding='utf-8') as f:
    terrain_json = json.load(f)

terrain_json["texture_data"].update(terrain_data)

with open("staging/target/rp/textures/terrain_texture.json", 'w', encoding='utf-8') as f:
    json.dump(terrain_json, f, separators=(',', ':'), ensure_ascii=False)

# Tạo block mappings và gộp vào mappings.json
if "blocks" not in mappings:
    mappings["blocks"] = {}

block_mappings_count = 0
for model_path, (variant_key, block_name) in model_variants.items():
    if block_name not in mappings["blocks"]:
        mappings["blocks"][block_name] = {
            "name": block_files[block_name], 
            "included_in_creative_inventory": False, 
            "only_override_states": True, 
            "place_air": True, 
            "state_overrides": {}
        }
    
    for name in names_found:
        if model_path in model_cmd_map:
            info = model_cmd_map[model_path]
            for item in mappings.get("items", {}).get(info["material"], []):
                if item.get("custom_model_data") == info["cmd"] and item["name"] == name:
                    # Check xem có phải block 16x16x16 không
                    is_16x16 = name in blocks_16x16_names
                    
                    # Quyết định geometry
                    if is_16x16:
                        geometry_type = "geometry.campfire_block"
                    else:
                        geometry_type = geometry_map.get(name, "geometry.campfiregeo_default")
                    
                    block_name_prefix = f"block_{name}"
                    
                    mappings["blocks"][block_name]["state_overrides"][variant_key] = {
                        "name": block_name_prefix,
                        "display_name": block_name_prefix,
                        "geometry": geometry_type,
                        "material_instances": {"*": {"texture": block_name_prefix, "render_method": "alpha_test", "face_dimming": True, "ambient_occlusion": True}}
                    }
                    
                    block_mappings_count += 1

# Sắp xếp state_overrides của tripwire
if "minecraft:tripwire" in mappings.get("blocks", {}):
    tripwire_block = mappings["blocks"]["minecraft:tripwire"]
    if "state_overrides" in tripwire_block:
        sorted_overrides = {}
        for key, value in tripwire_block["state_overrides"].items():
            # Tách các thuộc tính và sắp xếp
            properties = key.split(",")
            sorted_properties = sorted(properties)
            sorted_key = ",".join(sorted_properties)
            sorted_overrides[sorted_key] = value
        tripwire_block["state_overrides"] = sorted_overrides

with open("./staging/mappings.json", 'w', encoding='utf-8') as f:
    json.dump(mappings, f, indent=2, ensure_ascii=False)