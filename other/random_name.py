import os
import random
import string
import glob
import json
import shutil

def random_name():
    """Tạo tên random 45 ký tự chữ cái in thường và số xen kẽ"""
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=45))

def random_short_name():
    """Tạo tên random 15 ký tự chữ cái in thường và số"""
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def randomize_item_textures():
    """Random tên thư mục và file texture"""
    item_texture_path = "staging/target/rp/textures/item_texture.json"
    terrain_texture_path = "staging/target/rp/textures/terrain_texture.json"
    textures_root = "staging/target/rp/textures"
    
    if not os.path.exists(item_texture_path) and not os.path.exists(terrain_texture_path):
        return
    
    # Đọc cả 2 file JSON
    texture_data_combined = {}
    
    if os.path.exists(item_texture_path):
        with open(item_texture_path, 'r', encoding='utf-8') as f:
            item_texture_data = json.load(f)
            texture_data_combined['item'] = item_texture_data.get("texture_data", {})
    
    if os.path.exists(terrain_texture_path):
        with open(terrain_texture_path, 'r', encoding='utf-8') as f:
            terrain_texture_data = json.load(f)
            texture_data_combined['terrain'] = terrain_texture_data.get("texture_data", {})
    
    # Bước 1: Thu thập tất cả file và thư mục cần rename
    files_to_rename = []  # [(abs_path, relative_path_without_ext)]
    folders_to_rename = []  # [(abs_path, relative_path)]
    
    # Danh sách thư mục bỏ qua
    skip_folders = ['gui', 'campfire_item']
    
    for root, dirs, files in os.walk(textures_root):
        # Lọc bỏ thư mục cần skip
        rel_root = os.path.relpath(root, textures_root)
        
        # Kiểm tra xem có nằm trong thư mục skip không
        should_skip = False
        for skip_folder in skip_folders:
            if rel_root == skip_folder or rel_root.startswith(skip_folder + os.sep):
                should_skip = True
                break
        
        if should_skip:
            continue
        
        # Bỏ qua file item_texture.json và terrain_texture.json
        for file in files:
            if file in ['item_texture.json', 'terrain_texture.json']:
                continue
            if file.endswith('.png'):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, textures_root)
                rel_path_no_ext = rel_path[:-4]  # Bỏ .png
                files_to_rename.append((abs_path, rel_path_no_ext))
        
        # Thu thập thư mục (bỏ qua thư mục skip)
        for dir_name in dirs:
            if dir_name in skip_folders:
                continue
            
            abs_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(abs_path, textures_root)
            
            # Kiểm tra xem thư mục cha có phải skip không
            parent_skip = False
            for skip_folder in skip_folders:
                if rel_path.startswith(skip_folder + os.sep):
                    parent_skip = True
                    break
            
            if not parent_skip:
                folders_to_rename.append((abs_path, rel_path))
    
    # Bước 2: Tạo mapping cho file
    file_mapping = {}  # relative_path_no_ext -> new_name
    for abs_path, rel_path_no_ext in files_to_rename:
        new_name = random_short_name()
        file_mapping[rel_path_no_ext] = new_name
    
    # Bước 3: Tạo mapping cho thư mục (từ sâu nhất lên)
    folder_mapping = {}  # relative_path -> new_name
    folders_to_rename.sort(key=lambda x: x[1].count(os.sep), reverse=True)
    
    for abs_path, rel_path in folders_to_rename:
        new_name = random_short_name()
        folder_mapping[rel_path] = new_name
    
    # Bước 4: Rename files
    for abs_path, rel_path_no_ext in files_to_rename:
        if os.path.exists(abs_path):
            new_name = file_mapping[rel_path_no_ext]
            new_path = os.path.join(os.path.dirname(abs_path), new_name + '.png')
            shutil.move(abs_path, new_path)
    
    # Bước 4.5: Xáo trộn 70% file PNG giữa các thư mục
    all_png_files = []
    for root, dirs, files in os.walk(textures_root):
        rel_root = os.path.relpath(root, textures_root)
        should_skip = any(rel_root == skip or rel_root.startswith(skip + os.sep) for skip in skip_folders)
        
        if not should_skip:
            for file in files:
                if file.endswith('.png') and file not in ['item_texture.json', 'terrain_texture.json']:
                    all_png_files.append(os.path.join(root, file))
    
    # Chọn 100% file để xáo trộn
    num_to_shuffle = len(all_png_files)
    files_to_shuffle = all_png_files
    
    # Tạo danh sách thư mục đích
    target_dirs = set()
    for png_file in all_png_files:
        target_dirs.add(os.path.dirname(png_file))
    target_dirs = list(target_dirs)
    
    # Xáo trộn file
    for png_file in files_to_shuffle:
        if os.path.exists(png_file):
            target_dir = random.choice(target_dirs)
            new_path = os.path.join(target_dir, os.path.basename(png_file))
            
            # Nếu trùng tên, thêm suffix
            if os.path.exists(new_path):
                base_name = os.path.splitext(os.path.basename(png_file))[0]
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{base_name}_{counter}.png"
                    new_path = os.path.join(target_dir, new_name)
                    counter += 1
            
            shutil.move(png_file, new_path)
    
    # Bước 5: Rename folders (từ sâu nhất lên)
    for abs_path, rel_path in folders_to_rename:
        if os.path.exists(abs_path):
            new_name = folder_mapping[rel_path]
            new_path = os.path.join(os.path.dirname(abs_path), new_name)
            shutil.move(abs_path, new_path)
    
    # Bước 6: Tạo path mapping SAU KHI xáo trộn (để có đường dẫn chính xác)
    path_mapping = {}
    
    # Thu thập lại tất cả file PNG sau khi xáo trộn
    current_png_files = {}  # old_name -> new_full_path
    for root, dirs, files in os.walk(textures_root):
        rel_root = os.path.relpath(root, textures_root)
        should_skip = any(rel_root == skip or rel_root.startswith(skip + os.sep) for skip in skip_folders)
        
        if not should_skip:
            for file in files:
                if file.endswith('.png') and file not in ['item_texture.json', 'terrain_texture.json']:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, textures_root)
                    
                    # Tìm tên gốc từ file_mapping
                    for old_rel_path, new_name in file_mapping.items():
                        # Kiểm tra nếu file hiện tại khớp với new_name (có thể có suffix _1, _2)
                        file_base = os.path.splitext(file)[0]
                        if file_base == new_name or file_base.startswith(new_name + "_"):
                            old_texture_path = "textures/" + old_rel_path.replace(os.sep, '/')
                            new_texture_path = "textures/" + rel_path.replace(os.sep, '/')[:-4]  # Bỏ .png
                            path_mapping[old_texture_path] = new_texture_path
                            break
    
    # Bước 7: Cập nhật item_texture.json và terrain_texture.json
    if os.path.exists(item_texture_path):
        item_data = texture_data_combined.get('item', {})
        updated_textures = 0
        for key, value in item_data.items():
            old_texture_path = value.get("textures", "")
            if old_texture_path in path_mapping:
                item_data[key]["textures"] = path_mapping[old_texture_path]
                updated_textures += 1
        
        item_texture_data['texture_data'] = item_data
        with open(item_texture_path, 'w', encoding='utf-8') as f:
            json.dump(item_texture_data, f, ensure_ascii=False, indent=0)
    
    if os.path.exists(terrain_texture_path):
        terrain_data = texture_data_combined.get('terrain', {})
        updated_textures = 0
        for key, value in terrain_data.items():
            old_texture_path = value.get("textures", "")
            if old_texture_path in path_mapping:
                terrain_data[key]["textures"] = path_mapping[old_texture_path]
                updated_textures += 1
        
        terrain_texture_data['texture_data'] = terrain_data
        with open(terrain_texture_path, 'w', encoding='utf-8') as f:
            json.dump(terrain_texture_data, f, ensure_ascii=False, indent=0)
    
    # Bước 8: Cập nhật attachables
    attachables_dir = "staging/target/rp/attachables"
    updated_count = 0
    
    if os.path.exists(attachables_dir):
        json_files = list(glob.glob(f"{attachables_dir}/**/*.json", recursive=True))
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as jf:
                attachable_data = json.load(jf)
            
            desc = attachable_data.get("minecraft:attachable", {}).get("description", {})
            textures = desc.get("textures", {})
            updated = False
            
            for tex_key, tex_value in textures.items():
                if tex_value:
                    for old_path, new_path in path_mapping.items():
                        if old_path in tex_value:
                            textures[tex_key] = tex_value.replace(old_path, new_path)
                            updated = True
            
            if updated:
                with open(json_file, 'w', encoding='utf-8') as jf:
                    json.dump(attachable_data, jf, ensure_ascii=False, indent=0)
                updated_count += 1

def random_folder_name():
    """Tạo tên random 15 ký tự chữ cái in thường và số cho thư mục"""
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def rename_json_files():
    """Random tên tất cả file JSON trong attachables, animations, models/entity"""
    
    directories = [
        "staging/target/rp/attachables",
        "staging/target/rp/animations", 
        "staging/target/rp/models/entity",
        "staging/target/rp/render_controllers",
        "staging/target/rp/animation_controllers"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            # Random tên file JSON
            json_files = list(glob.glob(f"{directory}/**/*.json", recursive=True))
            
            for json_file in json_files:
                dir_path = os.path.dirname(json_file)
                new_name = f"{random_name()}.json"
                new_path = os.path.join(dir_path, new_name)
                os.rename(json_file, new_path)
            
            # Random tên thư mục con (chỉ với attachables và models/entity)
            if directory in ["staging/target/rp/attachables", "staging/target/rp/models/entity"]:
                folders = []
                for root, dirs, files in os.walk(directory, topdown=False):
                    for dir_name in dirs:
                        folders.append(os.path.join(root, dir_name))
                
                for old_dir_path in folders:
                    new_dir_path = os.path.join(os.path.dirname(old_dir_path), random_folder_name())
                    os.rename(old_dir_path, new_dir_path)

def check_randomized():
    """Kiểm tra xem tất cả file JSON và thư mục đã có prefix campfire_ chưa"""
    dirs = [
        "staging/target/rp/attachables",
        "staging/target/rp/animations",
        "staging/target/rp/models/entity",
        "staging/target/rp/render_controllers",
        "staging/target/rp/animation_controllers"
    ]
    
    skip_folders = ['gui', 'campfire_item']
    
    for directory in dirs:
        if os.path.exists(directory):
            for json_file in glob.glob(f"{directory}/**/*.json", recursive=True):
                if not os.path.basename(json_file).startswith("campfire_"):
                    print(f"[DEBUG] File chưa random: {json_file}")
                    return False
            
            if directory in ["staging/target/rp/attachables", "staging/target/rp/models/entity"]:
                for root, dirs_list, files in os.walk(directory):
                    for dir_name in dirs_list:
                        if not dir_name.startswith("campfire_"):
                            print(f"[DEBUG] Thư mục chưa random: {os.path.join(root, dir_name)}")
                            return False
    
    # Kiểm tra textures
    textures_root = "staging/target/rp/textures"
    if os.path.exists(textures_root):
        for root, dirs_list, files in os.walk(textures_root):
            rel_root = os.path.relpath(root, textures_root)
            should_skip = any(rel_root == skip or rel_root.startswith(skip + os.sep) for skip in skip_folders)
            
            if not should_skip:
                for file in files:
                    if file in ['item_texture.json', 'terrain_texture.json']:
                        continue
                    if file.endswith('.png') and not file.startswith("campfire_"):
                        print(f"[DEBUG] File PNG chưa random: {os.path.join(root, file)}")
                        return False
                for dir_name in dirs_list:
                    if dir_name not in skip_folders and not dir_name.startswith("campfire_"):
                        print(f"[DEBUG] Thư mục texture chưa random: {os.path.join(root, dir_name)}")
                        return False
    
    print("[DEBUG] Tất cả file và thư mục đã được random")
    return True

if __name__ == "__main__":
    randomize_item_textures()
    rename_json_files()
    
    if not check_randomized():
        randomize_item_textures()
        rename_json_files()
