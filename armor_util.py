import os
import glob
import shutil
import json
from typing import Dict, List, Optional
from pathlib import Path

class ArmorLayerReader:
    def __init__(self, equipment_dir: str = "./pack/assets/nexo/models/equipment/"):
        self.equipment_dir = equipment_dir
        self.textures_base = "./pack/assets/nexo/textures/entity/equipment/"
        self.models_item_dir = "./pack/assets/minecraft/models/item/"
    
    def get_armor_layers(self) -> Dict[str, List[str]]:
        """Lấy layer textures từ các file JSON equipment"""
        armor_layers = {}
        equipment_path = Path(self.equipment_dir)
        
        if not equipment_path.exists():
            armor_layers = self._read_armor_from_models()
        
        if equipment_path.exists():
            for json_file in equipment_path.glob("*.json"):
                armor_name = json_file.stem
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                layers = data.get("layers", {})
                humanoid = layers.get("humanoid", [])
                humanoid_leggings = layers.get("humanoid_leggings", [])
                
                layer_files = []
                
                if humanoid and len(humanoid) > 0:
                    texture_path = humanoid[0].get("texture", "")
                    if texture_path:
                        texture_name = texture_path.split(":")[-1]
                        layer_files.append(f"{texture_name}_1.png")
                
                if humanoid_leggings and len(humanoid_leggings) > 0:
                    texture_path = humanoid_leggings[0].get("texture", "")
                    if texture_path:
                        texture_name = texture_path.split(":")[-1]
                        layer_files.append(f"{texture_name}_2.png")
                
                if layer_files:
                    armor_layers[armor_name] = layer_files
        
        return armor_layers
    
    def _read_armor_from_models(self) -> Dict[str, List[str]]:
        """Đọc armor từ ./pack/assets/minecraft/models/item/"""
        armor_data = {}
        models_path = Path(self.models_item_dir)
        
        if not models_path.exists():
            return armor_data
        
        armor_types = ['_helmet', '_chestplate', '_leggings', '_boots']
        
        for json_file in models_path.glob("*.json"):
            filename = json_file.stem
            
            if any(armor_type in filename for armor_type in armor_types):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                overrides = data.get("overrides", [])
                for override in overrides:
                    model_name = override.get("model", "")
                    if model_name:
                        armor_type = None
                        if '_helmet' in filename:
                            armor_type = 'helmet'
                        elif '_chestplate' in filename:
                            armor_type = 'chestplate'
                        elif '_leggings' in filename:
                            armor_type = 'leggings'
                        elif '_boots' in filename:
                            armor_type = 'boots'
                        
                        if armor_type:
                            armor_data[model_name] = armor_type
        
        return armor_data

    def copy_layers_to_target(self) -> None:
        """Copy layer textures to target directory"""
        target_dir = "staging/target/rp/textures/layer_armor"
        os.makedirs(target_dir, exist_ok=True)
        print(f"📁 Tạo thư mục: {target_dir}")
        
        equipment_path = Path(self.equipment_dir)
        textures_base = Path(self.textures_base)
        
        if not equipment_path.exists():
            print(f"⚠️ Không tìm thấy: {equipment_path}")
            return
        
        copied_count = 0
        for json_file in equipment_path.glob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            layers = data.get("layers", {})
            humanoid = layers.get("humanoid", [])
            humanoid_leggings = layers.get("humanoid_leggings", [])
            
            if humanoid and len(humanoid) > 0:
                texture_path = humanoid[0].get("texture", "")
                if texture_path:
                    texture_name = texture_path.split(":")[-1]
                    source = textures_base / "humanoid" / f"{texture_name}.png"
                    if source.exists():
                        dest = Path(target_dir) / f"{texture_name}_1.png"
                        shutil.copy2(source, dest)
                        print(f"📋 Copy: {texture_name}_1.png")
                        copied_count += 1
            
            if humanoid_leggings and len(humanoid_leggings) > 0:
                texture_path = humanoid_leggings[0].get("texture", "")
                if texture_path:
                    texture_name = texture_path.split(":")[-1]
                    source = textures_base / "humanoid_leggings" / f"{texture_name}.png"
                    if source.exists():
                        dest = Path(target_dir) / f"{texture_name}_2.png"
                        shutil.copy2(source, dest)
                        print(f"📋 Copy: {texture_name}_2.png")
                        copied_count += 1

    def find_and_update_attachables(self) -> None:
        """Tìm và cập nhật attachables dựa trên equipment JSON files"""
        armor_layers = self.get_armor_layers()
        
        attachables_dir = "staging/target/rp/attachables"
        if not os.path.exists(attachables_dir):
            print(f"⚠️ Không tìm thấy: {attachables_dir}")
            return
        
        armor_data = self._read_armor_from_models()
        
        if not armor_data:
            print("⚠️ Không tìm thấy armor nào trong Minecraft models")
            return
        
        updated_count = 0
        for model_name, armor_type in armor_data.items():
            json_filename = f"{model_name}.json"
            for root, dirs, files in os.walk(attachables_dir):
                if json_filename in files:
                    file_path = os.path.join(root, json_filename)
                    self._remove_model_by_filename(file_path)
                    
                    layers = self._find_layers_for_armor(model_name, armor_type)
                    success = update_armor_attachable(file_path, f"minecraft:{model_name}", armor_type, model_name, layers)
                    if success:
                        relative_path = file_path.replace("staging/target/rp/attachables/", "").replace("\\", "/")
                        used_layer = layers[0] if layers else "no layer"
                        print(f"✅ Đã xử lý armor: {relative_path} ({used_layer})")
                        updated_count += 1
                    else:
                        relative_path = file_path.replace("staging/target/rp/attachables/", "").replace("\\", "/")
                        print(f"❌ Không xử lý được armor: {relative_path}")
                    break
    
    def _find_layers_for_armor(self, model_name, armor_type):
        """Tìm layer textures cho armor dựa trên tên"""
        armor_types = ['_helmet', '_chestplate', '_leggings', '_boots']
        base_name = model_name
        
        for atype in armor_types:
            if model_name.endswith(atype):
                base_name = model_name[:-len(atype)]
                break
        
        layer_dir = Path("staging/target/rp/textures/layer_armor")
        if not layer_dir.exists():
            return []
        
        layers = []
        for layer_file in layer_dir.glob("*.png"):
            filename = layer_file.stem
            if base_name in filename and (filename.endswith("_1") or filename.endswith("_2")):
                layers.append(layer_file.name)
        
        return layers

    def _detect_armor_type(self, file_path):
        """Phát hiện loại armor từ file path hoặc nội dung"""
        filename = os.path.basename(file_path).lower()
        if 'helmet' in filename:
            return 'helmet'
        elif 'chestplate' in filename:
            return 'chestplate'
        elif 'leggings' in filename:
            return 'leggings'
        elif 'boots' in filename:
            return 'boots'
        return None

    def _remove_model_by_filename(self, file_path):
        """Xóa model file theo tên file"""
        models_dir = "staging/target/rp/models/entity"
        
        if not os.path.exists(models_dir):
            return
        
        filename = os.path.basename(file_path)
        
        for root, dirs, files in os.walk(models_dir):
            if filename in files:
                model_path = os.path.join(root, filename)
                os.remove(model_path)

    def _find_attachable_path(self, attachables_dir, armor_name):
        """Tìm đường dẫn file JSON"""
        import re
        parts = re.split(r'([_-])', armor_name)
        
        for i in range(0, len(parts), 2):
            test_filename = ''.join(parts[i:]) + '.json'
            
            found_files = []
            for root, dirs, files in os.walk(attachables_dir):
                if test_filename in files:
                    found_files.append(os.path.join(root, test_filename))
            
            if len(found_files) == 1:
                return found_files[0]
            elif len(found_files) > 1:
                remaining_parts = parts[:i]
                target_file = self._find_matching_folder(attachables_dir, remaining_parts, found_files)
                if target_file:
                    return target_file
        
        return None
    
    def _find_matching_folder(self, attachables_dir, parts, found_files):
        """Tìm thư mục phù hợp để chọn file đúng"""
        remaining_text = ''.join(parts).rstrip('_-')
        
        for i in range(0, len(parts), 2):
            test_folder = ''.join(parts[i:]).rstrip('_-')
            if test_folder:
                for file_path in found_files:
                    if test_folder in file_path:
                        return file_path
        
        return found_files[0] if found_files else None

def update_armor_attachable(file, identifier, armor_type, armor_name, armor_layers):
    """Cập nhật armor attachable với layer texture thực tế"""
    try:
        with open(file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
            original_identifier = original_data.get("minecraft:attachable", {}).get("description", {}).get("identifier", identifier)
    except:
        original_identifier = identifier
    
    layer_file = None
    if armor_type in ["helmet", "chestplate", "boots"]:
        for layer in armor_layers:
            if "_1.png" in layer:
                layer_file = layer.replace('.png', '')
                break
    else:
        for layer in armor_layers:
            if "_2.png" in layer:
                layer_file = layer.replace('.png', '')
                break
    
    if not layer_file:
        return False
    
    texture_path = f"textures/layer_armor/{layer_file}"
    
    geometry_map = {
        "helmet": "geometry.player.armor.helmet",
        "chestplate": "geometry.player.armor.chestplate", 
        "leggings": "geometry.player.armor.leggings",
        "boots": "geometry.player.armor.boots"
    }
    
    script_map = {
        "helmet": "variable.helmet_layer_visible = 0.0;",
        "chestplate": "variable.chest_layer_visible = 0.0;",
        "leggings": "variable.leg_layer_visible = 0.0;",
        "boots": "variable.boot_layer_visible = 0.0;"
    }
    
    armor_attachable = {
        "format_version": "1.10.0",
        "minecraft:attachable": {
            "description": {
                "geometry": {"default": geometry_map[armor_type]},
                "identifier": original_identifier,
                "materials": {"default": "armor", "enchanted": "armor_enchanted"},
                "render_controllers": ["controller.render.armor"],
                "scripts": {"parent_setup": script_map[armor_type]},
                "textures": {
                    "default": texture_path,
                    "enchanted": "textures/misc/enchanted_item_glint"
                }
            }
        }
    }
    
    with open(file, "w") as f:
        json.dump(armor_attachable, f, indent=2)
    return True

def process_armor_textures():
    reader = ArmorLayerReader()
    reader.copy_layers_to_target()
    reader.find_and_update_attachables()

if __name__ == "__main__":
    process_armor_textures()
