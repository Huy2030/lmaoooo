import os
import random
import string
import glob

def random_name():
    """Tạo tên random 70 ký tự chữ cái in thường và số xen kẽ"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=70))

def random_folder_name():
    """Tạo tên random 15 ký tự chữ cái in thường và số cho thư mục"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

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
            for json_file in glob.glob(f"{directory}/**/*.json", recursive=True):
                dir_path = os.path.dirname(json_file)
                new_name = f"{random_name()}.json"
                new_path = os.path.join(dir_path, new_name)
                os.rename(json_file, new_path)
            
            # Random tên thư mục con (chỉ với attachables và models/entity)
            if directory in ["staging/target/rp/attachables", "staging/target/rp/models/entity"]:
                for root, dirs, files in os.walk(directory, topdown=False):
                    for dir_name in dirs:
                        old_dir_path = os.path.join(root, dir_name)
                        new_dir_path = os.path.join(root, random_folder_name())
                        os.rename(old_dir_path, new_dir_path)

if __name__ == "__main__":
    rename_json_files()