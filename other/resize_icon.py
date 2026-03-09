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
    
    total_resized = 0
    total_deleted = 0
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            print(f"Directory not found: {target_dir}")
            continue
        
        print(f"Processing directory: {target_dir}")
        
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
                            
                            # Delete 64x64 icons
                            if size == (64, 64):
                                os.remove(png_file)
                                total_deleted += 1
                                continue
                            
                            # Resize 128x128 to 48x48
                            if size == (128, 128):
                                # Apply slight blur before resize for smoother result
                                blurred = img.filter(ImageFilter.GaussianBlur(radius=0.7))
                                # Resize with high quality
                                resized = blurred.resize((48, 48), Image.LANCZOS)
                                resized.save(png_file)
                                total_resized += 1
                    except Exception as e:
                        continue
    
    print(f"Resized {total_resized} icons (128x128 -> 48x48)")
    print(f"Deleted {total_deleted} icons (64x64)")

if __name__ == "__main__":
    resize_icons()
