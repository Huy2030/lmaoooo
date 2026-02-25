import os
import json
import glob
import shutil
from item_utils import Item_Util

print()
print()
print("🚀 Bắt đầu xử lý converter items")

def cleanup_item_texture_duplicates():
    """Xóa các texture entries trùng lặp trong item_texture.json cho 2D items"""
    item_texture_file = "staging/target/rp/textures/item_texture.json"
    
    if not os.path.exists(item_texture_file):
        return 0
    
    try:
        with open(item_texture_file, 'r') as f:
            data = json.load(f)
        
        texture_data = data.get('texture_data', {})
        removed_count = 0
        keys_to_remove = []
        
        # Track textures đã thấy
        seen_textures = {}
        
        for key, value in texture_data.items():
            texture_path = value.get('textures', '')
            
            # Nếu texture path đã tồn tại, đánh dấu để xóa
            if texture_path in seen_textures:
                keys_to_remove.append(key)
                removed_count += 1
            else:
                seen_textures[texture_path] = key
        
        # Xóa các entries trùng lặp
        for key in keys_to_remove:
            del texture_data[key]
        
        # Ghi lại file
        if removed_count > 0:
            with open(item_texture_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        return removed_count
        
    except Exception as e:
        return 0

conversion_mode = 'both'

Item_Util.animations()

Item_Util.create_2d_animation_file()
Item_Util.create_2d_geometry_file()

attachable_files = glob.glob("staging/target/rp/attachables/**/*.json", recursive=True)

processed_3d_count = 0
processed_2d_count = 0
skipped_count = 0

for attachable_file in attachable_files:
    try:
        with open(attachable_file, "r") as f:
            attachable_data = json.load(f)
        
        render_controllers = attachable_data["minecraft:attachable"]["description"].get("render_controllers", [])
        if "controller.render.bow_custom" in render_controllers:
            skipped_count += 1
            continue
        
        identifier = attachable_data["minecraft:attachable"]["description"]["identifier"]
        materials = attachable_data["minecraft:attachable"]["description"]["materials"]
        textures = attachable_data["minecraft:attachable"]["description"]["textures"]
        geometry = attachable_data["minecraft:attachable"]["description"]["geometry"]
        animations = attachable_data["minecraft:attachable"]["description"]["animations"]
        
        relative_path = attachable_file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
        parts = relative_path.split("/")
        namespace = parts[0]
        model_path = "/".join(parts[1:-1]) if len(parts) > 2 else ""
        model_name = parts[-1].replace(".json", "")
        
        if model_path:
            source_model_file = f"staging/assets/{namespace}/models/{model_path}/{model_name}.json"
        else:
            source_model_file = f"staging/assets/{namespace}/models/{model_name}.json"
        
        display_data = {}
        is_2d_item = False
        
        if os.path.exists(source_model_file):
            with open(source_model_file, "r") as mf:
                model_json = json.load(mf)
                display_data = model_json.get("display", {})
                if "textures" in model_json and "elements" not in model_json:
                    is_2d_item = True
        
        if is_2d_item:
            Item_Util.update_attachable_2d(
                attachable_file,
                identifier,
                materials,
                textures,
                geometry
            )
            # Hiển thị đường dẫn tương đối từ staging/target/rp/attachables/
            relative_attachable_path = attachable_file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
            print(f"✅ Xử lý item 2D: {relative_attachable_path}")
            processed_2d_count += 1
            
        else:
            Item_Util.update_attachable(
                attachable_file,
                identifier,
                materials,
                textures,
                geometry,
                animations,
                display_data
            )
            # Hiển thị đường dẫn tương đối từ staging/target/rp/attachables/
            relative_attachable_path = attachable_file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
            print(f"✅ Xử lý item 3D: {relative_attachable_path}")
            processed_3d_count += 1
        
    except Exception as e:
        relative_attachable_path = attachable_file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
        print(f"❌ Không xử lý được item: {relative_attachable_path}")
        import traceback
        traceback.print_exc()

removed_2d_files = Item_Util.cleanup_2d_item_files()

removed_textures = cleanup_item_texture_duplicates()
