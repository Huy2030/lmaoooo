import os
from PIL import Image, ImageFilter
import glob

def resize_icons():
    """Resize tất cả icon 128x128 xuống 48x48 với độ mờ nhẹ và xóa icon 64x64"""
    target_dirs = [
        "staging/target/rp/textures",
        "bedrock/textures"
    ]
    
    skip_folder = "campfire_item"
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            continue
        
        for root, dirs, files in os.walk(target_dir):
            rel_root = os.path.relpath(root, target_dir)
            
            if skip_folder in rel_root.split(os.sep):
                continue
            
            for file in files:
                if file.endswith('.png'):
                    png_file = os.path.join(root, file)
                    try:
                        with Image.open(png_file) as img:
                            size = img.size
                            
                            if size == (64, 64):
                                os.remove(png_file)
                                continue
                            
                            if size == (128, 128):
                                # Apply slight blur before resize for smoother result
                                blurred = img.filter(ImageFilter.GaussianBlur(radius=0.5))
                                # Resize with high quality
                                resized = blurred.resize((48, 48), Image.LANCZOS)
                                resized.save(png_file)
                    except Exception as e:
                        continue

if __name__ == "__main__":
    resize_icons()
