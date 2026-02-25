import json
import os
import shutil

def process_sounds():
    """Đọc sound.json và copy các file sound tương ứng"""
    sound_json_path = "./pack/assets/minecraft/sounds.json"
    source_sound_dir = "./pack/assets/minecraft/sounds/"
    target_sound_dir = "staging/target/rp/sounds/"
    
    if not os.path.exists(sound_json_path):
        return
    
    with open(sound_json_path, 'r', encoding='utf-8') as f:
        sound_data = json.load(f)
    
    sound_definitions = {"format_version": "1.14.0", "sound_definitions": {}}
    all_sounds = []
    
    # Gộp tất cả sounds vào một mảng
    for sound_key, sound_info in sound_data.items():
        if "sounds" in sound_info:
            for sound_path in sound_info["sounds"]:
                # Tìm file trong thư mục source
                sound_dir = os.path.join(source_sound_dir, os.path.dirname(sound_path))
                sound_name = os.path.basename(sound_path)
                
                if os.path.exists(sound_dir):
                    for file in os.listdir(sound_dir):
                        if file.startswith(sound_name + "."):
                            source_file = os.path.join(sound_dir, file)
                            target_file = os.path.join(target_sound_dir, os.path.dirname(sound_path), file)
                            
                            os.makedirs(os.path.dirname(target_file), exist_ok=True)
                            shutil.copy2(source_file, target_file)
                            all_sounds.append({
                                "name": f"sounds/{sound_path}",
                                "volume": 1.0,
                                "interruptible": False,
					            "is3D": False,
				            	"min_distance": 100.0,
				            	"max_distance": 105.0,
                                "load_on_low_memory": True
                            })
                            break
    
    # Tạo một sound definition duy nhất chứa tất cả sounds
    if all_sounds:
        sound_definitions["sound_definitions"]["custom.camfire_sound"] = {
            "category": "hostile",
            "sounds": all_sounds
        }
    
    # Tạo sound_definitions.json
    sound_def_path = "staging/target/rp/sounds/sound_definitions.json"
    os.makedirs(os.path.dirname(sound_def_path), exist_ok=True)
    with open(sound_def_path, 'w', encoding='utf-8') as f:
        json.dump(sound_definitions, f, indent=2)

# Gọi function ngay khi import
process_sounds()

if __name__ == "__main__":
    process_sounds()