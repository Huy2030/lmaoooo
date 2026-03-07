import os
from PIL import Image
import glob

def resize_icons():
    """Resize tất cả icon từ 128x128 xuống 48x48 và xóa icon 64x64"""
    icon_dir = "tools/generated_icons"
    
    if not os.path.exists(icon_dir):
        return
    
    png_files = list(glob.glob(f"{icon_dir}/**/*.png", recursive=True))
    
    for png_file in png_files:
        try:
            with Image.open(png_file) as img:
                # Xóa nếu kích thước là 64x64
                if img.size == (64, 64):
                    os.remove(png_file)
                    continue
                
                # Resize nếu kích thước là 128x128
                if img.size == (128, 128):
                    resized = img.resize((48, 48), Image.LANCZOS)
                    resized.save(png_file)
        except Exception as e:
            continue

if __name__ == "__main__":
    resize_icons()
