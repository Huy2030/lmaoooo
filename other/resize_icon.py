import os
from PIL import Image, ImageFilter
import glob

def resize_icons():
    """Resize tất cả icon 128x128 xuống 48x48 và xóa icon 64x64"""
    target_dirs = [
        "staging/target/rp/textures",
        "bedrock/textures"
    ]
    
    skip_folder = "campfire_item"
    
    total_resized = 0
    total_deleted = 0
    
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
                            
                            # Delete 64x64 icons
                            if size == (64, 64):
                                os.remove(png_file)
                                total_deleted += 1
                                continue
                            
                            # Resize 128x128 to 48x48
                            if size == (128, 128):
                                # Convert to RGBA if needed
                                if img.mode != 'RGBA':
                                    img = img.convert('RGBA')
                                
                                # Use NEAREST to maintain sharp pixel edges (no anti-aliasing)
                                resized = img.resize((48, 48), Image.NEAREST)
                                
                                # Save as RGBA PNG
                                resized.save(png_file, 'PNG', optimize=True, compress_level=9)
                                total_resized += 1
                    except Exception as e:
                        continue

if __name__ == "__main__":
    import sys
    
    cwd = os.getcwd()
    if not cwd.endswith('staging') and 'staging' not in cwd:
        sys.exit(0)
    
    resize_icons()
