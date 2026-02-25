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
        
        # Bỏ qua file item_texture.json
        for file in files:
            if file == 'item_texture.json':
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
    
    # Bước 5: Rename folders (từ sâu nhất lên)
    for abs_path, rel_path in folders_to_rename:
        if os.path.exists(abs_path):
            new_name = folder_mapping[rel_path]
            new_path = os.path.join(os.path.dirname(abs_path), new_name)
            shutil.move(abs_path, new_path)
    
    # Bước 6: Tạo path mapping cho item_texture.json
    path_mapping = {}
    
    for rel_path_no_ext, new_file_name in file_mapping.items():
        # Chuyển đổi đường dẫn Windows sang Unix style
        rel_path_unix = rel_path_no_ext.replace(os.sep, '/')
        
        # Tách thành parts
        parts = rel_path_unix.split('/')
        
        # Thay thế tên thư mục theo mapping
        new_parts = []
        for i in range(len(parts) - 1):  # Bỏ phần file name
            # Tính relative path của thư mục này
            folder_rel = '/'.join(parts[:i+1])
            folder_rel_os = folder_rel.replace('/', os.sep)
            
            if folder_rel_os in folder_mapping:
                new_parts.append(folder_mapping[folder_rel_os])
            else:
                new_parts.append(parts[i])
        
        # Thêm tên file mới
        new_parts.append(new_file_name)
        
        # Tạo mapping
        old_texture_path = "textures/" + rel_path_unix
        new_texture_path = "textures/" + "/".join(new_parts)
        path_mapping[old_texture_path] = new_texture_path
    
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

if __name__ == "__main__":
    randomize_item_textures()
    rename_json_files()
