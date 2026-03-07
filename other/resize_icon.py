import os
from PIL import Image
import glob

def resize_icons():
    """Resize tất cả icon từ 128x128 xuống 48x48 và xóa icon 64x64"""
    icon_dir = "tools/generated_icons"
    
    if not os.path.exists(icon_dir):
        print(f"[RESIZE_ICON] Directory not found: {icon_dir}")
        return
    
    png_files = list(glob.glob(f"{icon_dir}/**/*.png", recursive=True))
    print(f"[RESIZE_ICON] Found {len(png_files)} PNG files")
    
    resized_count = 0
    deleted_count = 0
    
    for png_file in png_files:
        try:
            with Image.open(png_file) as img:
                size = img.size
                
                # Xóa nếu kích thước là 64x64
                if size == (64, 64):
                    os.remove(png_file)
                    deleted_count += 1
                    print(f"[RESIZE_ICON] Deleted 64x64: {png_file}")
                    continue
                
                # Resize nếu kích thước là 128x128
                if size == (128, 128):
                    resized = img.resize((48, 48), Image.LANCZOS)
                    resized.save(png_file)
                    resized_count += 1
                    print(f"[RESIZE_ICON] Resized 128x128 -> 48x48: {png_file}")
        except Exception as e:
            print(f"[RESIZE_ICON] Error processing {png_file}: {e}")
            continue
    
    print(f"[RESIZE_ICON] Summary: Resized {resized_count}, Deleted {deleted_count}")

if __name__ == "__main__":
    resize_icons()
