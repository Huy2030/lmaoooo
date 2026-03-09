import os
import json
import glob
import shutil
from pathlib import Path

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
    
    success_count = 0
    for json_file in json_files:
        # Bỏ qua mappings.json
        if json_file.endswith("mappings.json"):
            continue
        if minify_json_file(json_file):
            success_count += 1
    
    return success_count



def cleanup_fishing_cast_textures():
    """Xóa _cast khỏi texture paths có chứa fishing_cast hoặc fishing_rod_cast"""
    # Bỏ qua nếu mappings.py đã chạy
    if os.getenv("ITEM_MODEL") == "true":
        return
    
    item_texture_file = "staging/target/rp/textures/item_texture.json"
    
    if not os.path.exists(item_texture_file):
        return
    
    try:
        with open(item_texture_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "texture_data" in data:
            for key, value in data["texture_data"].items():
                if isinstance(value, dict) and "textures" in value:
                    texture_path = value["textures"]
                    if "fishing_cast" in texture_path or "fishing_rod_cast" in texture_path:
                        value["textures"] = texture_path.replace("_cast", "")
        
        with open(item_texture_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
    
    except Exception:
        pass

def cleanup_unwanted_files():
    """Xóa các thư mục và file không mong muốn"""
    
    # Remove _iainternal folders only (skip if mappings.py is running)
    if os.getenv("ITEM_MODEL") != "true":
        unwanted_dirs = [
            "staging/target/rp/animations/_iainternal",
            "staging/target/rp/attachables/_iainternal",
            "staging/target/rp/models/entity/_iainternal"
        ]
        
        removed_dirs_count = 0
        for dir_path in unwanted_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    removed_dirs_count += 1
                except Exception:
                    pass
    
    # Remove specific unwanted files
    unwanted_patterns = [
        "*trident_throwing*.json", "*staff_throwing*.json", "*backpack_*.json",
        "*back_*.json", "*backpack-*.json", "*back-*.json", "*wing_*.json",
        "*wings_*.json", "*wing-*.json", "*wings-*.json", "*cape_*.json",
        "*cape-*.json", "*capes_*.json", "*capes-*.json", "*shield_blocking*.json",
        "*shield_block*.json*", "*spear_throwing*.json"
    ]
    
    # Thêm fishing patterns nếu mappings.py không chạy
    if os.getenv("ITEM_MODEL") != "true":
        unwanted_patterns.extend(["*fishing_rod_cast*.json", "*fishing_cast*.json"])
    
    search_dirs = ["staging/target/rp/attachables", "staging/target/rp/models/entity"]
    
    removed_files_count = 0
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for pattern in unwanted_patterns:
                for file_path in glob.glob(f"{search_dir}/**/{pattern}", recursive=True):
                    try:
                        os.remove(file_path)
                        removed_files_count += 1
                    except Exception:
                        pass

def remove_empty_directories(directory):
    """Xóa tất cả thư mục rỗng"""
    removed_count = 0
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    removed_count += 1
            except:
                pass
    return removed_count

def remove_empty_sounds_folder():
    """Xóa thư mục sounds nếu không có thư mục con nào bên trong"""
    sounds_dir = "staging/target/rp/sounds"
    
    if not os.path.exists(sounds_dir):
        return
    
    try:
        # Lấy danh sách tất cả items trong sounds
        items = os.listdir(sounds_dir)
        
        # Kiểm tra xem có thư mục con nào không
        has_subdirs = False
        for item in items:
            item_path = os.path.join(sounds_dir, item)
            if os.path.isdir(item_path):
                has_subdirs = True
                break
        
        # Nếu không có thư mục con nào, xóa toàn bộ sounds folder
        if not has_subdirs:
            shutil.rmtree(sounds_dir)
    except Exception as e:
        pass

if __name__ == "__main__":
    cleanup_fishing_cast_textures()
    cleanup_unwanted_files()
    
    if os.path.exists("staging/target/rp"):
        minify_all_json("staging/target/rp")
        remove_empty_sounds_folder()
        remove_empty_directories("staging/target/rp")