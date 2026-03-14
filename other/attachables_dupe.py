import os
import json
import glob
import random
from pathlib import Path

def create_attachable_copies():
    """Tạo các file copy từ attachables với JSON template"""
    _ns = ["lmao:imlang","xyz:chaos","matrix:glitch","void:null","quantum:entangled",
           "paradox:loop","dimension:5th","binary:overflow","neural:network","crypto:hash"]
    _keys = ["zxzxzx","abc123","error404","empty","superposition",
             "infinite","tesseract","stack","synapse","blockchain"]

    def _make(i):
        return {"format_version": "1.10.0", _ns[i % len(_ns)]: {
            _keys[i % len(_keys)]: {"identifier": "campfire:kaito_sieu_cap_dep_trai"}
        }}

    attachable_templates = [_make(i) for i in range(19)]
    
    directories = [
        ("staging/target/rp/attachables", 3),
        ("staging/target/rp/animations", 3),
        ("staging/target/rp/render_controllers", 4),
        ("staging/target/rp/animation_controllers", 4)
    ]
    
    for directory, copy_count in directories:
        if not os.path.exists(directory):
            continue
            
        for json_file in glob.glob(f"{directory}/**/*.json", recursive=True):
            if json_file.endswith('.tmp'):
                continue
            
            # Skip shield.entity.json files
            file_name = Path(json_file).name
            if file_name.startswith('shield.entity'):
                continue
            
            # Skip files that are already copies (ending with numbers)
            base_name = Path(json_file).stem
            if len(base_name) > 1 and base_name[-1].isdigit():
                continue
                
            base_dir = Path(json_file).parent
            
            for i in range(1, copy_count + 1):
                new_file = base_dir / f"{base_name}{i}.json"
                template = random.choice(attachable_templates)
                with open(new_file, 'w', encoding='utf-8') as f:
                    json.dump(template, f, separators=(',', ':'), ensure_ascii=False)

if __name__ == "__main__":
    create_attachable_copies()