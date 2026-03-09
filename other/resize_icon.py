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
    size_stats = {}
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            continue
        
        print(f"Đang xử lý thư mục: {target_dir}")
        
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
                            
                            # Track size statistics
                            size_key = f"{size[0]}x{size[1]}"
                            size_stats[size_key] = size_stats.get(size_key, 0) + 1
                            
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
    
    print(f"📊 Thống kê kích thước icon: {size_stats}")
    print(f"✓ Đã resize {total_resized} icons (128x128 → 48x48)")
    print(f"✓ Đã xóa {total_deleted} icons (64x64)")

if __name__ == "__main__":
    import sys
    
    # Chỉ chạy nếu được gọi từ thư mục staging
    cwd = os.getcwd()
    if not cwd.endswith('staging') and 'staging' not in cwd:
        print("[RESIZE_ICON] ⚠️ Bỏ qua - script này chỉ nên được gọi từ free.py")
        sys.exit(0)
    
    resize_icons()
