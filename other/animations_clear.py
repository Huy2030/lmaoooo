import os
import shutil

def cleanup_animation_folders():
    """Xóa TẤT CẢ các thư mục trong animations directory"""
    removed_count = 0
    
    animations_dir = "staging/target/rp/animations"
    if os.path.exists(animations_dir):
        for item in os.listdir(animations_dir):
            item_path = os.path.join(animations_dir, item)
            
            if os.path.isdir(item_path):
                try:
                    shutil.rmtree(item_path)
                    removed_count += 1
                except Exception:
                    pass
    
    return removed_count

if __name__ == "__main__":
    removed = cleanup_animation_folders()
