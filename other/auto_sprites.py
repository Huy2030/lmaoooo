#!/usr/bin/env python3
import json
import os
import glob

def scan_all_items():
    """Quét tất cả 3D items từ attachables"""
    texture_entries = {}
    
    # Xác định đường dẫn base dựa trên cấu trúc thực tế
    if os.path.exists("staging/target/rp"):
        base_path = "staging/target/rp"
    elif os.path.exists("target/rp"):
        base_path = "target/rp"
    elif os.path.exists("bedrock"):
        base_path = "bedrock"
    else:
        return {}
    
    # Quét 3D items từ attachables
    attachable_files = glob.glob(f"{base_path}/attachables/**/*.json", recursive=True)
    
    for file_path in attachable_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Lấy gmdl từ identifier
            identifier = data.get("minecraft:attachable", {}).get("description", {}).get("identifier", "")
            if not identifier or ":" not in identifier:
                continue
                
            gmdl = identifier.split(":")[1]
            
            # Tạo texture path từ đường dẫn file - giữ nguyên cấu trúc thư mục
            parts = file_path.replace("\\", "/").split("/")
            for i, part in enumerate(parts):
                if part == "attachables" and i + 1 < len(parts):
                    # Lấy tất cả phần từ namespace trở đi
                    namespace_and_path = parts[i + 1:]
                    item_name = os.path.splitext(namespace_and_path[-1])[0]  # Tên file không có .json
                    
                    # Tạo đường dẫn đầy đủ
                    if len(namespace_and_path) > 1:
                        # Có thư mục con (như item/ia_auto)
                        namespace = namespace_and_path[0]
                        sub_path = "/".join(namespace_and_path[1:-1])  # Các thư mục con
                        
                        # Xử lý đặc biệt cho bow, crossbow, shield - loại bỏ số ở cuối
                        if item_name.startswith(("bow", "crossbow", "shield")):
                            if item_name in ["bow", "crossbow", "shield"]:
                                base_name = item_name
                            else:
                                base_name = item_name.split("_")[0]
                            if sub_path:
                                texture_path = f"textures/{namespace}/{sub_path}/{base_name}"
                            else:
                                texture_path = f"textures/{namespace}/{base_name}"
                        else:
                            if sub_path:
                                texture_path = f"textures/{namespace}/{sub_path}/{item_name}"
                            else:
                                texture_path = f"textures/{namespace}/{item_name}"
                    else:
                        # Không có thư mục con
                        namespace = namespace_and_path[0]
                        
                        # Xử lý đặc biệt cho bow, crossbow, shield - loại bỏ số ở cuối
                        if item_name.startswith(("bow", "crossbow", "shield")):
                            if item_name in ["bow", "crossbow", "shield"]:
                                base_name = item_name
                            else:
                                base_name = item_name.split("_")[0]
                            texture_path = f"textures/{namespace}/{base_name}"
                        else:
                            texture_path = f"textures/{namespace}/{item_name}"
                    
                    texture_entries[gmdl] = {"textures": texture_path}
                    break
                    
        except Exception:
            continue
    
    return texture_entries

def main():
    print("🚀 Bắt đầu xử lý auto sprites")
    
    # Quét tất cả 3D items
    texture_entries = scan_all_items()
    
    if not texture_entries:
        print("❌ Không tìm thấy 3D items nào để xử lý")
        return 1
    
    print(f"✅ Tìm thấy {len(texture_entries)} 3D items để xử lý")
    
    # Xác định đường dẫn output dựa trên cấu trúc hiện tại
    if os.path.exists("staging/target/rp/textures"):
        item_texture_path = "staging/target/rp/textures/item_texture.json"
    elif os.path.exists("target/rp/textures"):
        item_texture_path = "target/rp/textures/item_texture.json"
    elif os.path.exists("bedrock/textures"):
        item_texture_path = "bedrock/textures/item_texture.json"
    else:
        # Tạo thư mục nếu không tồn tại
        os.makedirs("target/rp/textures", exist_ok=True)
        item_texture_path = "target/rp/textures/item_texture.json"
    
    if os.path.exists(item_texture_path):
        try:
            with open(item_texture_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_entries = existing_data.get("texture_data", {})
        except Exception:
            existing_entries = {}
    else:
        existing_entries = {}
    
    # Thêm entries mới vào existing entries (chỉ nếu chưa có)
    added_count = 0
    for gmdl, texture_info in texture_entries.items():
        if gmdl not in existing_entries:
            existing_entries[gmdl] = texture_info
            added_count += 1
    
    # Fix duplicate paths in texture_data
    import re
    for key, value in existing_entries.items():
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
                print(f"🔧 Fixed duplicate path: {original_path} → {texture_path}")
    
    # Lưu lại file với entries đã được thêm
    item_texture_data = {
        "resource_pack_name": "geyser_custom",
        "texture_name": "atlas.items",
        "texture_data": existing_entries
    }
    
    os.makedirs(os.path.dirname(item_texture_path), exist_ok=True)
    with open(item_texture_path, "w", encoding="utf-8") as f:
        json.dump(item_texture_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Đã thêm {added_count} entries mới vào item_texture.json (Tổng: {len(existing_entries)})")
    
    # Xóa các thư mục minecraft/item không cần thiết
    import shutil
    minecraft_item_dirs = [
        "staging/target/rp/animations/minecraft/item",
        "staging/target/rp/attachables/minecraft/item",
        "staging/target/rp/models/entity/minecraft/item",
        "staging/target/rp/textures/minecraft/item"
    ]
    
    for dir_path in minecraft_item_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
            except Exception:
                pass
    
    # Copy to other locations if needed
    if "target/rp" in item_texture_path:
        # Copy to root directory
        root_path = "item_texture.json"
        with open(root_path, "w", encoding="utf-8") as f:
            json.dump(item_texture_data, f, indent=2, ensure_ascii=False)
        
        # Copy to bedrock if exists
        if os.path.exists("bedrock/textures"):
            bedrock_path = "bedrock/textures/item_texture.json"
            os.makedirs("bedrock/textures", exist_ok=True)
            with open(bedrock_path, "w", encoding="utf-8") as f:
                json.dump(item_texture_data, f, indent=2, ensure_ascii=False)
    elif "bedrock" in item_texture_path:
        # Copy to root directory
        root_path = "item_texture.json"
        with open(root_path, "w", encoding="utf-8") as f:
            json.dump(item_texture_data, f, indent=2, ensure_ascii=False)
        
        # Copy to staging if exists
        if os.path.exists("staging/target/rp/textures"):
            staging_path = "staging/target/rp/textures/item_texture.json"
            os.makedirs("staging/target/rp/textures", exist_ok=True)
            with open(staging_path, "w", encoding="utf-8") as f:
                json.dump(item_texture_data, f, indent=2, ensure_ascii=False)
    elif "staging" in item_texture_path:
        # Copy to root directory
        root_path = "item_texture.json"
        with open(root_path, "w", encoding="utf-8") as f:
            json.dump(item_texture_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()