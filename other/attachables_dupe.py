import os
import json
import glob
import random
from pathlib import Path

def create_attachable_copies():
    """Tạo các file copy từ attachables với JSON template"""
    attachable_templates = [
        {"format_version": "1.21.0","lmao:imlang": {"zxzxzx": {"identifier": "campfire:kaito_sieu_cap_dep_trai"}}},
        {"format_version": "1.21.0","lmao:imlang": {"zxzxzx": {"identifier": "campfire:kaito_sieu_cap_dep_trai","321323121": {"12312121": [{"dungnghicopyduocfile": "kaito_dep_trai_nhat_vu_tru"},{"dungnghicopyduocfile": "kaito_dep_trai_nhat_vu_tru"}]}}}},
        {"format_version": "1.21.0","lmao:imlang": {"lmao:imlang": {"zxzxzx2323213": {"identifier": "campfire:kaito_sieu_cap_dep_trai","identifier": "campfire:kaito_sieu_cap_dep_trai","3213221333121": {"123121123221": [{"dungnghicopyduocfile": "kaito_dep_trai_nhat_vu_tru"},{"dungnghicopyduocfile": "kaito_dep_trai_nhat_vu_tru"}]}}}}},
        {"format_version": "1.21.0","lmao:imlang": {"zxzxzx": {"identifier": "campfire:kaito_sieu_cap_dep_trai","321323121": {"12312121": [{"dungnghicopyduocfile": "kaito_dep_trai_nhat_vu_tru"}]}}}},
        {"format_version": "1.21.0","xyz:chaos": {"abc123": {"identifier": "campfire:kaito_sieu_cap_dep_trai","nested": {"deep": {"deeper": [{"random": "data123"},{"chaos": "mode"}]}}}}},
        {"format_version": "1.21.0","broken:json": {"invalid": {"identifier": "campfire:kaito_sieu_cap_dep_trai","duplicate": "key","duplicate": "value2","array": [1,2,3,{"nested": True}]}}},
        {"format_version": "1.21.0","matrix:glitch": {"error404": {"identifier": "campfire:kaito_sieu_cap_dep_trai","glitch": {"matrix": {"red": "pill","blue": "pill","choice": [{"neo": "chosen"},{"agent": "smith"}]}}}}},
        {"format_version": "1.21.0","void:null": {"empty": {"identifier": "campfire:kaito_sieu_cap_dep_trai","void": None,"infinity": {"loop": {"recursive": {"data": [{"null": None},{"undefined": "chaos"}]}}}}}},
        {"format_version": "1.21.0","quantum:entangled": {"superposition": {"identifier": "campfire:kaito_sieu_cap_dep_trai","wave": {"particle": [{"spin": "up"},{"spin": "down"},{"spin": "sideways"}]}}}},
        {"format_version": "1.21.0","paradox:loop": {"infinite": {"identifier": "campfire:kaito_sieu_cap_dep_trai","recursion": {"self": {"reference": {"loop": [{"start": "end"},{"end": "start"}]}}}}}},
        {"format_version": "1.21.0","dimension:5th": {"tesseract": {"identifier": "campfire:kaito_sieu_cap_dep_trai","hypercube": {"axis": {"x": 1,"y": 2,"z": 3,"w": 4,"v": [{"beyond": "reality"}]}}}}},
        {"format_version": "1.21.0","binary:overflow": {"stack": {"identifier": "campfire:kaito_sieu_cap_dep_trai","buffer": {"overflow": [1,0,1,1,0,0,1,{"segfault": "core_dumped"}]}}}},
        {"format_version": "1.21.0","neural:network": {"synapse": {"identifier": "campfire:kaito_sieu_cap_dep_trai","neurons": {"fire": {"pattern": [{"input": "data"},{"hidden": "layer"},{"output": "chaos"}]}}}}},
        {"format_version": "1.21.0","fractal:mandelbrot": {"iteration": {"identifier": "campfire:kaito_sieu_cap_dep_trai","complex": {"plane": {"z": {"real": 0.5,"imaginary": 0.8,"escape": [{"radius": 2}]}}}}}},
        {"format_version": "1.21.0","crypto:hash": {"blockchain": {"identifier": "campfire:kaito_sieu_cap_dep_trai","merkle": {"tree": {"root": [{"hash": "0x1234"},{"nonce": 42},{"proof": "work"}]}}}}},
        {"format_version": "1.21.0","dna:helix": {"genetic": {"identifier": "campfire:kaito_sieu_cap_dep_trai","sequence": {"base": {"pairs": [{"A": "T"},{"G": "C"},{"mutation": "evolution"}]}}}}},
        {"format_version": "1.21.0","time:paradox": {"temporal": {"identifier": "campfire:kaito_sieu_cap_dep_trai","causality": {"loop": {"past": {"future": [{"cause": "effect"},{"effect": "cause"}]}}}}}},
        {"format_version": "1.21.0","multiverse:theory": {"parallel": {"identifier": "campfire:kaito_sieu_cap_dep_trai","reality": {"branch": {"infinite": [{"universe": "A"},{"universe": "B"},{"universe": "∞"}]}}}}},
        {"format_version": "1.21.0","singularity:event": {"horizon": {"identifier": "campfire:kaito_sieu_cap_dep_trai","gravity": {"well": {"escape": [{"velocity": "c"},{"time": "dilated"},{"space": "curved"}]}}}}}
    ]
    
    directories = [
        ("staging/target/rp/attachables", 2),
        ("staging/target/rp/animations", 2),
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