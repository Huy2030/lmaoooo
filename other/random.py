import os
import random
import string
import glob
import json
import shutil

def random_name():
    """Tạo tên random 45 ký tự chữ cái in thường và số xen kẽ"""
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=45))

def randomize_animations():
    """Random tên và xáo trộn tất cả file JSON trong animations"""
    animations_dir = "staging/target/rp/animations"
    
    if not os.path.exists(animations_dir):
        return
    
    # Bước 1: Thu thập tất cả file JSON
    json_files = list(glob.glob(f"{animations_dir}/**/*.json", recursive=True))
    
    if not json_files:
        return
    
    # Bước 2: Rename files với tên random
    renamed_files = []
    for json_file in json_files:
        if os.path.exists(json_file):
            dir_path = os.path.dirname(json_file)
            new_name = f"{random_name()}.json"
            new_path = os.path.join(dir_path, new_name)
            shutil.move(json_file, new_path)
            renamed_files.append(new_path)
    
    # Bước 3: Xáo trộn 100% file JSON giữa các thư mục
    # Thu thập tất cả thư mục có chứa file JSON
    target_dirs = set()
    for json_file in renamed_files:
        target_dirs.add(os.path.dirname(json_file))
    target_dirs = list(target_dirs)
    
    # Nếu chỉ có 1 thư mục thì không cần xáo trộn
    if len(target_dirs) <= 1:
        return
    
    # Xáo trộn file
    for json_file in renamed_files:
        if os.path.exists(json_file):
            target_dir = random.choice(target_dirs)
            new_path = os.path.join(target_dir, os.path.basename(json_file))
            
            # Nếu trùng tên, thêm suffix
            if os.path.exists(new_path):
                base_name = os.path.splitext(os.path.basename(json_file))[0]
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{base_name}_{counter}.json"
                    new_path = os.path.join(target_dir, new_name)
                    counter += 1
            
            shutil.move(json_file, new_path)

def check_randomized():
    """Kiểm tra xem tất cả file JSON trong animations đã có prefix campfire_ chưa"""
    animations_dir = "staging/target/rp/animations"
    
    if not os.path.exists(animations_dir):
        return True
    
    for json_file in glob.glob(f"{animations_dir}/**/*.json", recursive=True):
        if not os.path.basename(json_file).startswith("campfire_"):
            return False
    
    return True

if __name__ == "__main__":
    randomize_animations()
    
    if not check_randomized():
        randomize_animations()