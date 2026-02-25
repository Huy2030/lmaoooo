import os
import glob
import shutil
import json
from typing import Dict, List, Optional

class ArmorLayerReader:
    def __init__(self, properties_dir: str = "./pack/assets/minecraft/optifine/cit/ia_generated_armors"):
        self.properties_dir = properties_dir
        self.excluded_files = {"base_leather.properties", "custom_base_leather.properties"}
    
    def read_properties_files(self) -> Dict[str, Dict[str, str]]:
        """Đọc tất cả file .properties trong thư mục"""
        properties_data = {}
        
        if not os.path.exists(self.properties_dir):
            return properties_data
        
        pattern = os.path.join(self.properties_dir, "*.properties")
        properties_files = glob.glob(pattern)
        
        for file_path in properties_files:
            filename = os.path.basename(file_path)
            
            if filename in self.excluded_files:
                continue
            
            try:
                file_data = self._parse_properties_file(file_path)
                properties_data[filename] = file_data
            except Exception as e:
                pass
        
        return properties_data
    
    def _parse_properties_file(self, file_path: str) -> Dict[str, str]:
        """Parse một file .properties thành dictionary"""
        properties = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    properties[key.strip()] = value.strip()
        
        return properties
    
    def get_armor_layers(self) -> Dict[str, List[str]]:
        """Lấy layer textures từ các file .properties"""
        armor_layers = {}
        
        if not os.path.exists(self.properties_dir):
            return armor_layers
        
        for file_path in glob.glob(os.path.join(self.properties_dir, "*.properties")):
            filename = os.path.basename(file_path)
            if filename in self.excluded_files:
                continue
            
            armor_name = filename.replace('.properties', '')
            layers = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            for line in content.split('\n'):
                if 'texture.leather_layer_' in line and '=' in line:
                    texture_file = line.split('=')[1].strip()
                    if texture_file.endswith('.png') and texture_file not in layers:
                        layers.append(texture_file)
            
            if layers:
                armor_layers[armor_name] = sorted(list(set(layers)))
        
        return armor_layers
    
    def copy_layers_to_target(self) -> None:
        """Copy layer textures to target directory"""
        target_dir = "staging/target/rp/textures/layer_armor"
        os.makedirs(target_dir, exist_ok=True)
        print(f"📁 Tạo thư mục: {target_dir}")
        
        armor_layers = self.get_armor_layers()
        
        if not armor_layers:
            return
        
        # Collect all unique layer files
        all_layers = set()
        for layers in armor_layers.values():
            all_layers.update(layers)
        
        for layer_file in all_layers:
            source_path = os.path.join(self.properties_dir, layer_file)
            target_path = os.path.join(target_dir, layer_file)
            
            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)
                print(f"📋 Copy: {layer_file}")

    def find_and_update_attachables(self) -> None:
        """Tìm và cập nhật attachables dựa trên properties files"""
        all_properties = self.read_properties_files()
        armor_layers = self.get_armor_layers()
        
        attachables_dir = "staging/target/rp/attachables"
        if not os.path.exists(attachables_dir):
            return
        
        updated_count = 0
        for filename, properties in all_properties.items():
            armor_name = filename.replace('.properties', '')
            layers = armor_layers.get(armor_name, [])
            if not layers:
                continue
            
            # Tìm đường dẫn file JSON
            file_path = self._find_attachable_path(attachables_dir, armor_name)
            if not file_path:
                print(f"❌ Không xử lý được armor: không tìm thấy file cho {armor_name}")
                continue
            
            # Xác định armor type
            items = properties.get('items', '')
            if 'helmet' in items:
                armor_type = 'helmet'
            elif 'chestplate' in items:
                armor_type = 'chestplate'
            elif 'leggings' in items:
                armor_type = 'leggings'
            elif 'boots' in items:
                armor_type = 'boots'
            else:
                relative_attachable_path = file_path.replace("staging/target/rp/attachables/", "").replace("\\", "/")
                print(f"❌ Không xử lý được armor: {relative_attachable_path}")
                continue
            
            # Xóa model file
            self._remove_model_by_filename(file_path)
            
            success = update_armor_attachable(file_path, f"minecraft:{armor_name}", armor_type, armor_name, layers)
            if success:
                # Hiển thị đường dẫn tương đối từ staging/target/rp/attachables/
                relative_attachable_path = file_path.replace("staging/target/rp/attachables/", "").replace("\\", "/")
                
                # Tìm layer được sử dụng
                used_layer = None
                if armor_type in ["helmet", "chestplate", "boots"]:
                    for layer in layers:
                        if "_1.png" in layer:
                            used_layer = layer
                            break
                else:  # leggings
                    for layer in layers:
                        if "_2.png" in layer:
                            used_layer = layer
                            break
                
                if used_layer:
                    print(f"✅ Đã xử lý armor: {relative_attachable_path} ({used_layer})")
                else:
                    print(f"✅ Đã xử lý armor: {relative_attachable_path}")
                updated_count += 1
            else:
                relative_attachable_path = file_path.replace("staging/target/rp/attachables/", "").replace("\\", "/")
                print(f"❌ Không xử lý được armor: {relative_attachable_path}")

    def _remove_model_by_filename(self, file_path):
        """Xóa model file theo đường dẫn tương ứng"""
        attachables_dir = "staging/target/rp/attachables"
        models_dir = "staging/target/rp/models/entity"
        
        if not os.path.exists(models_dir):
            return
        
        rel_path = os.path.relpath(file_path, attachables_dir)
        model_path = os.path.join(models_dir, rel_path)
        
        if os.path.exists(model_path):
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

    def generate_leather_armor_models(self) -> None:
        """Tạo custom_model_data entries cho leather armor từ mappings.json"""
        mappings_path = "./staging/mappings.json"
        if not os.path.exists(mappings_path):
            return
        
        try:
            with open(mappings_path, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
        except Exception as e:
            return
        
        items_data = mappings.get("items", {})
        leather_items = {
            "minecraft:leather_helmet": "leather_helmet.json",
            "minecraft:leather_chestplate": "leather_chestplate.json", 
            "minecraft:leather_leggings": "leather_leggings.json",
            "minecraft:leather_boots": "leather_boots.json"
        }
        
        base_path = "./pack/assets/minecraft/models/item"
        
        for material_key, filename in leather_items.items():
            if material_key not in items_data:
                continue
                
            file_path = os.path.join(base_path, filename)
            if not os.path.exists(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    leather_json = json.load(f)
            except Exception as e:
                continue
            
            existing_overrides = leather_json.get("overrides", [])
            trim_overrides = [o for o in existing_overrides if "trim_type" in o.get("predicate", {})]
            
            new_overrides = []
            items_list = items_data[material_key]
            
            for item in items_list:
                if isinstance(item, dict):
                    name = item.get("name", "")
                    custom_model_data = item.get("custom_model_data")
                    
                    if custom_model_data and name:
                        base_override = {
                            "predicate": {"custom_model_data": custom_model_data},
                            "model": f"{name.split('_')[0]}:item/ia_auto/{name}"
                        }
                        new_overrides.append(base_override)
                        
                        for trim_override in trim_overrides:
                            trim_type = trim_override["predicate"]["trim_type"]
                            trim_model_override = {
                                "predicate": {
                                    "trim_type": trim_type,
                                    "custom_model_data": custom_model_data
                                },
                                "model": f"{name.split('_')[0]}:item/ia_auto/{name}"
                            }
                            new_overrides.append(trim_model_override)
            
            all_overrides = trim_overrides + new_overrides
            leather_json["overrides"] = all_overrides
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(leather_json, f, indent=2)
            except Exception as e:
                pass

    def update_item_texture_json(self) -> None:
        """Copy armor icons từ mappings.json → pack JSON files → staging/target"""
        mappings_path = "./staging/mappings.json"
        item_texture_path = "./staging/target/rp/textures/item_texture.json"
        
        if not os.path.exists(mappings_path) or not os.path.exists(item_texture_path):
            return
        
        with open(mappings_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        with open(item_texture_path, 'r', encoding='utf-8') as f:
            item_textures = json.load(f)
        
        texture_data = item_textures.get("texture_data", {})
        items_data = mappings.get("items", {})
        all_properties = self.read_properties_files()
        
        attachables_dir = "staging/target/rp/attachables"
        available_folders = []
        if os.path.exists(attachables_dir):
            available_folders = [d for d in os.listdir(attachables_dir) if os.path.isdir(os.path.join(attachables_dir, d)) and d not in ["minecraft", "_iainternal"]]
        
        folder_mapping = {}
        for filename in all_properties.keys():
            armor_name = filename.replace('.properties', '')
            for folder in available_folders:
                if armor_name.startswith(folder + '_'):
                    folder_mapping[armor_name] = folder
                    break
        
        for material_key, items_list in items_data.items():
            if "leather_" not in material_key:
                continue
                
            for item in items_list:
                name = item.get("name", "")
                custom_model_data = item.get("custom_model_data")
                
                if name in texture_data:
                    texture_path = texture_data[name]["textures"]
                    target_path = f"./staging/target/rp/{texture_path}.png"
                    
                    path_parts = texture_path.split('/')
                    armor_name_from_path = path_parts[-1]
                    namespace = path_parts[1]
                    
                    found_armor = None
                    for prop_file in all_properties.keys():
                        armor_name = prop_file.replace('.properties', '')
                        folder = folder_mapping.get(armor_name)
                        if folder:
                            actual_name = armor_name.replace(folder + '_', '', 1)
                            if actual_name == armor_name_from_path:
                                found_armor = actual_name
                                break
                    
                    if not found_armor:
                        continue
                    
                    json_file = f"{found_armor}.json"
                    source_path = None
                    
                    for root, dirs, files in os.walk(f"./pack/assets/{namespace}"):
                            if json_file in files:
                                json_path = os.path.join(root, json_file)
                                
                                try:
                                    with open(json_path, 'r', encoding='utf-8') as f:
                                        json_content = json.load(f)
                                    
                                    textures = json_content.get("textures", {})
                                    layer1 = textures.get("layer1", "")
                                    
                                    if layer1 and ":" in layer1:
                                        layer_namespace, icon_path = layer1.split(":", 1)
                                        
                                        if layer_namespace == namespace:
                                            source_path = f"./pack/assets/{layer_namespace}/textures/{icon_path}.png"
                                            break
                                except Exception as e:
                                    pass
                    
                    if source_path and os.path.exists(source_path):
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        shutil.copy2(source_path, target_path)

def update_armor_attachable(file, identifier, armor_type, armor_name, armor_layers):
    """Cập nhật armor attachable với layer texture thực tế từ properties"""
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

print()
# Chạy khi được import từ manager.py
print("🚀 Bắt đầu xử lý converter armor")

# Kiểm tra có Nexo không
nexo_equipment = os.path.exists("./pack/assets/nexo/models/equipment/")
nexo_items = os.path.exists("./pack/assets/nexo/items/")

if nexo_equipment or nexo_items:
    from armor_util import process_armor_textures
    process_armor_textures()
else:
    reader = ArmorLayerReader()
    
    # Copy layers
    reader.copy_layers_to_target()
    
    # Tạo custom_model_data entries
    reader.generate_leather_armor_models()
    
    # Cập nhật attachables
    reader.find_and_update_attachables()
    
    # Cập nhật item texture
    reader.update_item_texture_json()

# Sử dụng khi chạy trực tiếp
if __name__ == "__main__":
    nexo_equipment = os.path.exists("./pack/assets/nexo/models/equipment/")
    nexo_items = os.path.exists("./pack/assets/nexo/items/")
    
    if nexo_equipment or nexo_items:
        from armor_util import process_armor_textures
        process_armor_textures()
    else:
        reader = ArmorLayerReader()
        
        reader.copy_layers_to_target()
        reader.generate_leather_armor_models()
        reader.find_and_update_attachables()
        reader.update_item_texture_json()