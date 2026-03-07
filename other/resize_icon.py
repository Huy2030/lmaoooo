import os
from PIL import Image
import glob

def resize_icons():
    """Resize tất cả icon từ 128x128 xuống 48x48 và xóa icon 64x64"""
    possible_dirs = ["tools/generated_icons", "../tools/generated_icons"]
    icon_dir = None
    
    for dir_path in possible_dirs:
        if os.path.exists(dir_path):
            icon_dir = dir_path
            break
    
    if not icon_dir:
        return
    
    png_files = list(glob.glob(f"{icon_dir}/**/*.png", recursive=True))
    
    for png_file in png_files:
        try:
            with Image.open(png_file) as img:
                size = img.size
                
                if size == (64, 64):
                    os.remove(png_file)
                    continue
                
                if size == (128, 128):
                    resized = img.resize((48, 48), Image.LANCZOS)
                    resized.save(png_file)
        except Exception as e:
            continue

if __name__ == "__main__":
    resize_icons()
