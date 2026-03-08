import os
import re
import yaml
import random
import string
import shutil

if os.path.exists("pack/assets/nexo"):
    exit()

def remove_ia_generated_armors():
    folder_path = "pack/assets/minecraft/optifine/cit/ia_generated_armors"
    
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(folder_path, exist_ok=True)

def generate_random_name():
    return ''.join(random.choices(string.ascii_lowercase, k=8))

def process_armor_items():
    contents_folder = "pack/contents"
    storage_folder = "pack/storage"
    
    if not os.path.exists(contents_folder):
        return
    
    if not os.path.exists(storage_folder):
        return
    
    yml_path = "pack/storage/items_ids_cache.yml"
    
    if not os.path.exists(yml_path):
        return
    
    with open(yml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse file để tìm material type cho mỗi armor item
    armor_to_material = {}  # {namespace:item_name: material_type}
    current_material = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Kiểm tra xem có phải section header không (pattern: *_HELMET:, *_CHESTPLATE:, etc.)
        if line.endswith(':') and not ' ' in line:
            upper_line = line.upper()
            if '_HELMET:' in upper_line:
                current_material = line[:-1].lower()  # Bỏ dấu : và lowercase
            elif '_CHESTPLATE:' in upper_line:
                current_material = line[:-1].lower()
            elif '_LEGGINGS:' in upper_line:
                current_material = line[:-1].lower()
            elif '_BOOTS:' in upper_line:
                current_material = line[:-1].lower()
            else:
                current_material = None
        
        # Parse armor items trong section hiện tại
        if current_material and ':' in line and not line.endswith(':'):
            match = re.match(r'(\S+?):(\S+?):\s*(\d+)', line)
            if match:
                namespace, item_name, cmd = match.groups()
                full_name = f"{namespace}:{item_name}"
                armor_to_material[full_name] = current_material
    
    armor_patterns = [
        r'(\S+?):([\w]+helmet):\s*(\d+)',
        r'(\S+?):([\w]+chestplate):\s*(\d+)',
        r'(\S+?):([\w]+leggings):\s*(\d+)',
        r'(\S+?):([\w]+boots):\s*(\d+)'
    ]
    
    armor_items = []
    for pattern in armor_patterns:
        matches = re.findall(pattern, content)
        armor_items.extend(matches)
    
    cit_folder = "pack/assets/minecraft/optifine/cit/ia_generated_armors"
    os.makedirs(cit_folder, exist_ok=True)
    
    # Quét đệ quy tất cả file yml trong contents
    yml_files = []
    for root, dirs, files in os.walk(contents_folder):
        for file in files:
            if file.endswith('.yml'):
                yml_files.append(os.path.join(root, file))
    
    # Bước 1: Thu thập tất cả layers và copy ảnh vào ia_generated_armors
    all_layers = set()
    layer_to_armor = {}
    
    for namespace, item_name, custom_model_data in armor_items:
        for yml_file_path in yml_files:
            try:
                with open(yml_file_path, 'r', encoding='utf-8') as f:
                    yml_data = yaml.safe_load(f)
                
                if yml_data and 'info' in yml_data and 'items' in yml_data:
                    if item_name in yml_data['items']:
                        layer_1_original = None
                        layer_2_original = None
                        
                        if 'armors_rendering' in yml_data:
                            for armor_key, armor_data in yml_data['armors_rendering'].items():
                                if 'layer_1' in armor_data and 'layer_2' in armor_data:
                                    layer_1_original = armor_data['layer_1']
                                    layer_2_original = armor_data['layer_2']
                                    break
                        
                        if not layer_1_original and 'equipments' in yml_data:
                            for equip_key, equip_data in yml_data['equipments'].items():
                                if 'layer_1' in equip_data and 'layer_2' in equip_data:
                                    layer_1_original = equip_data['layer_1']
                                    layer_2_original = equip_data['layer_2']
                                    break
                        
                        if layer_1_original and layer_2_original:
                            layer_1_name = layer_1_original.split('/')[-1]
                            layer_2_name = layer_2_original.split('/')[-1]
                            
                            if layer_1_name not in layer_to_armor:
                                layer_to_armor[layer_1_name] = []
                            layer_to_armor[layer_1_name].append((namespace, item_name))
                            
                            if layer_1_name not in all_layers:
                                all_layers.add(layer_1_name)
                                all_layers.add(layer_2_name)
                                
                                layer_1_src = None
                                layer_2_src = None
                                
                                for root, dirs, files in os.walk("pack"):
                                    if f"{layer_1_name}.png" in files:
                                        layer_1_src = os.path.join(root, f"{layer_1_name}.png")
                                    if f"{layer_2_name}.png" in files:
                                        layer_2_src = os.path.join(root, f"{layer_2_name}.png")
                                    if layer_1_src and layer_2_src:
                                        break
                                
                                if layer_1_src:
                                    dst = os.path.join(cit_folder, f"{layer_1_name}.png")
                                    shutil.copy2(layer_1_src, dst)
                                
                                if layer_2_src:
                                    dst = os.path.join(cit_folder, f"{layer_2_name}.png")
                                    shutil.copy2(layer_2_src, dst)
                            
                            break
            except:
                pass
    
    # Bước 2: Random name và tạo .properties
    layer_mapping = {}
    
    for namespace, item_name, custom_model_data in armor_items:
        for yml_file_path in yml_files:
            try:
                with open(yml_file_path, 'r', encoding='utf-8') as f:
                    yml_data = yaml.safe_load(f)
                
                if yml_data and 'info' in yml_data and 'items' in yml_data:
                    if item_name in yml_data['items']:
                        layer_1_original = None
                        layer_2_original = None
                        
                        if 'armors_rendering' in yml_data:
                            for armor_key, armor_data in yml_data['armors_rendering'].items():
                                if 'layer_1' in armor_data and 'layer_2' in armor_data:
                                    layer_1_original = armor_data['layer_1']
                                    layer_2_original = armor_data['layer_2']
                                    break
                        
                        if not layer_1_original and 'equipments' in yml_data:
                            for equip_key, equip_data in yml_data['equipments'].items():
                                if 'layer_1' in equip_data and 'layer_2' in equip_data:
                                    layer_1_original = equip_data['layer_1']
                                    layer_2_original = equip_data['layer_2']
                                    break
                        
                        if layer_1_original and layer_2_original:
                            layer_1_name = layer_1_original.split('/')[-1]
                            layer_2_name = layer_2_original.split('/')[-1]
                            
                            if layer_1_name not in layer_mapping:
                                random_name = generate_random_name()
                                layer_mapping[layer_1_name] = f"{random_name}_1"
                                layer_mapping[layer_2_name] = f"{random_name}_2"
                                
                                old_1 = os.path.join(cit_folder, f"{layer_1_name}.png")
                                old_2 = os.path.join(cit_folder, f"{layer_2_name}.png")
                                new_1 = os.path.join(cit_folder, f"{random_name}_1.png")
                                new_2 = os.path.join(cit_folder, f"{random_name}_2.png")
                                
                                if os.path.exists(old_1):
                                    os.rename(old_1, new_1)
                                
                                if os.path.exists(old_2):
                                    os.rename(old_2, new_2)
                            
                            # Tạo .properties
                            file_name = f"{namespace}_{item_name}"
                            properties_file = os.path.join(cit_folder, f"{file_name}.properties")
                            random_name = layer_mapping[layer_1_name].replace("_1", "")
                            
                            # Lấy material type từ armor_to_material
                            full_name = f"{namespace}:{item_name}"
                            armor_material = armor_to_material.get(full_name, "leather_helmet")
                            
                            with open(properties_file, 'w', encoding='utf-8') as f:
                                f.write(f"items={armor_material}\n")
                                f.write(f"texture.leather_layer_1={random_name}_1.png\n")
                                f.write(f"texture.leather_layer_2={random_name}_2.png\n")
                            
                            break
            except:
                pass

if __name__ == "__main__":
    remove_ia_generated_armors()
    process_armor_items()
