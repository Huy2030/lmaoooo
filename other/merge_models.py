import os
import json
from pathlib import Path

def merge_json_files(base_path):
    if not base_path.exists():
        return
    
    main_dirs = [d for d in base_path.iterdir() if d.is_dir()]
    
    for main_dir in main_dirs:
        # Thu thập tất cả JSON files từ main_dir và tất cả thư mục con của nó
        all_json_files = []
        for json_file in main_dir.rglob("*.json"):
            if json_file.name not in ["campfire_tool_custom.json", "campfire_block.json"]:
                all_json_files.append(json_file)
        
        if all_json_files:
            merge_and_save(all_json_files, main_dir / f"{main_dir.name}.json")
    
    remove_empty_dirs(base_path)

def remove_empty_dirs(base_path):
    for root, dirs, files in os.walk(base_path, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except:
                pass

def merge_and_save(json_files, output_file):
    merged_data = {"format_version": "1.21.0", "minecraft:geometry": []}
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "minecraft:geometry" in data:
                    merged_data["minecraft:geometry"].extend(data["minecraft:geometry"])
        except:
            pass
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, separators=(',', ':'), ensure_ascii=False)
        for json_file in json_files:
            json_file.unlink()
    except:
        pass

def merge_render_controllers(base_path):
    if not base_path.exists():
        return
    
    # Kiểm tra file JSON trực tiếp trong thư mục gốc
    direct_json_files = list(base_path.glob("*.json"))
    if direct_json_files:
        merge_and_save_render_controllers(direct_json_files, base_path / "render_controllers.json")
    
    # Kiểm tra các thư mục con
    main_dirs = [d for d in base_path.iterdir() if d.is_dir()]
    
    for main_dir in main_dirs:
        json_files = list(main_dir.glob("*.json"))
        if json_files:
            merge_and_save_render_controllers(json_files, main_dir / "render_controllers.json")
        else:
            sub_dirs = [d for d in main_dir.iterdir() if d.is_dir()]
            for sub_dir in sub_dirs:
                sub_json_files = list(sub_dir.glob("*.json"))
                if sub_json_files:
                    merge_and_save_render_controllers(sub_json_files, sub_dir / "render_controllers.json")
    
    remove_empty_dirs(base_path)

def merge_and_save_render_controllers(json_files, output_file):
    merged_data = {"format_version": "1.10", "render_controllers": {}}
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "render_controllers" in data:
                    merged_data["render_controllers"].update(data["render_controllers"])
        except:
            pass
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, separators=(',', ':'), ensure_ascii=False)
        for json_file in json_files:
            json_file.unlink()
    except:
        pass

if __name__ == "__main__":
    models_path = Path("staging/target/rp/models/entity")
    if models_path.exists():
        merge_json_files(models_path)
    
    render_controllers_path = Path("staging/target/rp/render_controllers")
    if render_controllers_path.exists():
        merge_render_controllers(render_controllers_path)