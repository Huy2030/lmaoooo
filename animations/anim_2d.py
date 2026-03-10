import json
import os
from pathlib import Path
from PIL import Image
from geometry import GEOMETRY_2D_32x32

animation_counter = 0
render_controllers = {}
existing_configs = {}
texture_to_animation_info = {}  # Map texture path -> (controller_name, anim_name, frame_count)

def create_2d_geometry():
    """Tạo geometry file cho 2D animated items"""
    geometry_dir = Path("staging/target/rp/models/entity")
    geometry_dir.mkdir(parents=True, exist_ok=True)
    
    geometry_file = geometry_dir / "plaiiqhdbbbcassyay.geo.json"
    
    # Kiểm tra nếu file đã tồn tại thì không tạo lại
    if geometry_file.exists():
        return
    
    geometry_data = GEOMETRY_2D_32x32

    with open(geometry_file, 'w', encoding='utf-8') as f:
        json.dump(geometry_data, f, ensure_ascii=False, indent=2)

def load_existing_render_controllers():
    global existing_configs
    render_dir = Path("staging/target/rp/render_controllers")
    if not render_dir.exists():
        return
    for json_file in render_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            controllers = data.get("render_controllers", {})
            for controller_name, controller_data in controllers.items():
                textures = controller_data.get("textures", [])
                if not textures:
                    continue
                texture_formula = textures[0]
                if "q.life_time * 20 /" in texture_formula and "math.mod" in texture_formula:
                    try:
                        frametime_part = texture_formula.split("q.life_time * 20 /")[1].split(")")[0].strip()
                        frametime = int(frametime_part)
                        frame_count_part = texture_formula.split(",")[-1].split("]")[0].strip()
                        frame_count = int(frame_count_part)
                        existing_configs[(frametime, frame_count)] = controller_name
                    except:
                        pass
        except:
            pass

def update_attachables_with_controllers():
    """Cập nhật attachables với render controllers phù hợp"""
    global texture_to_animation_info
    
    attachables_dir = Path("staging/target/rp/attachables")
    if not attachables_dir.exists():
        return
    
    updated_count = 0
    for json_file in attachables_dir.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            attachable = data.get("minecraft:attachable", {})
            description = attachable.get("description", {})
            textures = description.get("textures", {})
            default_texture = textures.get("default", "")
            
            if not default_texture:
                continue
            
            # Kiểm tra xem texture path có trong mapping không
            matched_info = None
            matched_texture_path = None
            for texture_path, animation_info in texture_to_animation_info.items():
                # So sánh cả 2 chiều: texture_path in default_texture HOẶC default_texture endswith texture_path
                # Để xử lý cả trường hợp có prefix khác nhau
                texture_basename = texture_path.split('/')[-1]  # Lấy tên file cuối cùng
                default_basename = default_texture.split('/')[-1]
                
                if texture_basename == default_basename or texture_path in default_texture or default_texture.endswith(texture_path):
                    matched_info = animation_info
                    matched_texture_path = texture_path
                    break
            
            if matched_info:
                controller_name, anim_name, frame_count = matched_info
                
                # Cập nhật render_controllers
                description["render_controllers"] = [controller_name]
                
                # Cập nhật textures - thay "default" bằng các frame textures
                new_textures = {}
                for i in range(frame_count):
                    new_textures[f"{anim_name}_{i}"] = f"textures/{matched_texture_path}/{i}"
                
                # Giữ lại các texture khác (enchanted, etc.)
                for key, value in textures.items():
                    if key != "default":
                        new_textures[key] = value
                
                description["textures"] = new_textures
                
                # Cập nhật geometry - luôn dùng geometry.plaiiqhdbbbcassyay
                description["geometry"] = {anim_name: "geometry.plaiiqhdbbbcassyay"}
                
                # Cập nhật animations
                description["animations"] = {
                    "thirdperson_hand": "animation.campfire.thirdperson_hand",
                    "thirdperson_head": "animation.campfire.thirdperson_head",
                    "firstperson_hand": "animation.campfire.firstperson_hand",
                    "firstperson_head": "animation.campfire.disable"
                }
                
                # Cập nhật scripts
                description["scripts"] = {
                    "initialize": [
                        "v.thirdperson_mainhand_rot_x = 4.5;",
                        "v.thirdperson_mainhand_rot_y = 0;",
                        "v.thirdperson_mainhand_rot_z = 0;",
                        "v.thirdperson_mainhand_pos_x = 0;",
                        "v.thirdperson_mainhand_pos_y = 3;",
                        "v.thirdperson_mainhand_pos_z = 2;",
                        "v.thirdperson_mainhand_scale = 0.75;",
                        "v.thirdperson_hand_same = true;",
                        "v.firstperson_mainhand_rot_x = 0;",
                        "v.firstperson_mainhand_rot_y = 0;",
                        "v.firstperson_mainhand_rot_z = 0;",
                        "v.firstperson_mainhand_pos_x = 0.75;",
                        "v.firstperson_mainhand_pos_y = 1.5;",
                        "v.firstperson_mainhand_pos_z = 0.25;",
                        "v.firstperson_mainhand_scale = 0.8;",
                        "v.firstperson_hand_same = true;",
                        "v.thirdperson_head_rot_x = 0;",
                        "v.thirdperson_head_rot_y = 0;",
                        "v.thirdperson_head_rot_z = 0;",
                        "v.thirdperson_head_pos_x = 0;",
                        "v.thirdperson_head_pos_y = 0;",
                        "v.thirdperson_head_pos_z = 0;",
                        "v.thirdperson_head_scale = 0;"
                    ],
                    "pre_animation": [
                        "v.main_hand = c.item_slot=='main_hand';",
                        "v.off_hand = c.item_slot=='off_hand';",
                        "v.head = c.item_slot=='head';"
                    ],
                    "animate": [
                        {"thirdperson_hand": "(v.main_hand||v.off_hand)&&!c.is_first_person"},
                        {"thirdperson_head": "v.head&&!c.is_first_person"},
                        {"firstperson_hand": "(v.main_hand||v.off_hand)&&c.is_first_person"},
                        {"firstperson_head": "c.is_first_person&&v.head"}
                    ]
                }
                
                data["minecraft:attachable"]["description"] = description
                
                # Lưu lại file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
        
        except Exception as e:
            pass
    
    if updated_count > 0:
        pass

def scan_2d_animations():
    global animation_counter
    pack_dir = Path("./pack/assets")
    if not pack_dir.exists():
        return
    
    # Tạo geometry file trước khi xử lý
    create_2d_geometry()
    
    render_controllers_dir = Path("staging/target/rp/render_controllers")
    render_controllers_dir.mkdir(parents=True, exist_ok=True)
    load_existing_render_controllers()
    processed = 0
    
    for json_file in pack_dir.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get("parent") != "minecraft:item/generated":
                continue
            textures = data.get("textures", {})
            layer0 = textures.get("layer0", "")
            if not layer0:
                continue
            if ":" not in layer0:
                continue
            namespace, texture_path = layer0.split(":", 1)
            texture_file = pack_dir / namespace / "textures" / f"{texture_path}.png"
            if not texture_file.exists():
                continue
            
            img = Image.open(texture_file)
            width, height = img.size
            
            if height <= width:
                continue
            if height % width != 0:
                continue
            frame_count = height // width
            if frame_count <= 1:
                continue
            
            mcmeta_file = Path(str(texture_file) + ".mcmeta")
            frametime = 1
            if mcmeta_file.exists():
                try:
                    with open(mcmeta_file, 'r', encoding='utf-8') as f:
                        mcmeta_data = json.load(f)
                    animation = mcmeta_data.get("animation", {})
                    frametime = animation.get("frametime", 1)
                except:
                    pass
            
            if (frametime, frame_count) in existing_configs:
                continue
            
            # Tạo đường dẫn output trong staging/target/rp/textures
            # Lấy relative path từ pack/assets/namespace/textures/
            relative_texture_path = texture_file.relative_to(pack_dir / namespace / "textures")
            # Bỏ extension .png
            relative_texture_path = relative_texture_path.with_suffix('')
            
            # Tạo thư mục output trong staging/target/rp/textures
            frame_dir = Path("staging/target/rp/textures") / relative_texture_path
            frame_dir.mkdir(parents=True, exist_ok=True)
            
            frame_size = width
            
            for i in range(frame_count):
                frame_img = img.crop((0, i * frame_size, width, (i + 1) * frame_size))
                frame_output_path = frame_dir / f"{i}.png"
                frame_img.save(frame_output_path)
            
            animation_counter += 1
            anim_name = f"anim_{animation_counter}"
            texture_array = [f"texture.{anim_name}_{i}" for i in range(frame_count)]
            controller_name = f"controller.render.campfire_kaito.{anim_name}"
            render_controllers[controller_name] = {
                "arrays": {
                    "textures": {
                        f"array.anim": texture_array
                    }
                },
                "geometry": f"geometry.{anim_name}",
                "materials": [{"*": "variable.is_enchanted ? material.enchanted : material.default"}],
                "textures": [
                    f"array.anim[math.mod(math.floor(q.life_time * 20 / {frametime}),{frame_count})]",
                    "texture.enchanted"
                ]
            }
            existing_configs[(frametime, frame_count)] = controller_name
            
            # Lưu mapping texture path -> (controller_name, anim_name, frame_count)
            # Texture path trong attachable dạng: "textures/fuben/item/ia_auto/fb_12"
            texture_path_for_attachable = str(relative_texture_path).replace('\\', '/')
            texture_to_animation_info[texture_path_for_attachable] = (controller_name, anim_name, frame_count)
            
            processed += 1
        except Exception as e:
            pass
    
    # Cập nhật attachables với render controllers phù hợp
    if texture_to_animation_info:
        update_attachables_with_controllers()
    
    if render_controllers:
        output_path = Path("staging/target/rp/render_controllers/animations.render_controllers.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_data = {
            "format_version": "1.8.0",
            "render_controllers": render_controllers
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Random tên và xáo trộn texture
    randomize_2d_animation_textures()

if __name__ == "__main__":
    scan_2d_animations()

def random_short_name():
    """Tạo tên random 15 ký tự chữ cái in thường và số"""
    import random
    import string
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def randomize_2d_animation_textures():
    """Random tên và xáo trộn texture của 2D animations (chỉ trong phạm vi item/)"""
    import random
    import shutil
    
    textures_root = Path("staging/target/rp/textures")
    item_dir = textures_root / "item"
    
    if not item_dir.exists():
        return
    
    # Bước 1: Thu thập tất cả file PNG và thư mục con trong item/
    files_to_rename = []  # [(abs_path, relative_path_without_ext)]
    folders_to_rename = []  # [(abs_path, relative_path)]
    
    for root, dirs, files in os.walk(item_dir):
        rel_root = os.path.relpath(root, item_dir)
        
        # Thu thập file PNG
        for file in files:
            if file.endswith('.png'):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, item_dir)
                rel_path_no_ext = rel_path[:-4]  # Bỏ .png
                files_to_rename.append((abs_path, rel_path_no_ext))
        
        # Thu thập thư mục con (không bao gồm thư mục item root)
        for dir_name in dirs:
            abs_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(abs_path, item_dir)
            folders_to_rename.append((abs_path, rel_path))
    
    # Bước 2: Tạo mapping cho file
    file_mapping = {}  # relative_path_no_ext -> new_name
    for abs_path, rel_path_no_ext in files_to_rename:
        new_name = random_short_name()
        file_mapping[rel_path_no_ext] = new_name
    
    # Bước 3: Tạo mapping cho thư mục con (từ sâu nhất lên)
    folder_mapping = {}  # relative_path -> new_name
    folders_to_rename.sort(key=lambda x: x[1].count(os.sep), reverse=True)
    
    for abs_path, rel_path in folders_to_rename:
        new_name = random_short_name()
        folder_mapping[rel_path] = new_name
    
    # Bước 4: Rename files
    for abs_path, rel_path_no_ext in files_to_rename:
        if os.path.exists(abs_path):
            new_name = file_mapping[rel_path_no_ext]
            new_path = os.path.join(os.path.dirname(abs_path), new_name + '.png')
            shutil.move(abs_path, new_path)
    
    # Bước 5: Xáo trộn 100% file PNG trong phạm vi item/
    all_png_files = []
    for root, dirs, files in os.walk(item_dir):
        for file in files:
            if file.endswith('.png'):
                all_png_files.append(os.path.join(root, file))
    
    # Tạo danh sách thư mục đích (tất cả thư mục trong item/)
    target_dirs = []
    for root, dirs, files in os.walk(item_dir):
        target_dirs.append(root)
    
    # Nếu chỉ có thư mục root, tạo thêm một số thư mục con random
    if len(target_dirs) <= 1:
        for i in range(5):
            new_dir = item_dir / random_short_name()
            new_dir.mkdir(parents=True, exist_ok=True)
            target_dirs.append(str(new_dir))
    
    # Xáo trộn file trong phạm vi item/
    for png_file in all_png_files:
        if os.path.exists(png_file):
            target_dir = random.choice(target_dirs)
            new_path = os.path.join(target_dir, os.path.basename(png_file))
            
            # Nếu trùng tên, thêm suffix
            if os.path.exists(new_path):
                base_name = os.path.splitext(os.path.basename(png_file))[0]
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{base_name}_{counter}.png"
                    new_path = os.path.join(target_dir, new_name)
                    counter += 1
            
            shutil.move(png_file, new_path)
    
    # Bước 6: Rename folders (từ sâu nhất lên)
    for abs_path, rel_path in folders_to_rename:
        if os.path.exists(abs_path):
            new_name = folder_mapping[rel_path]
            new_path = os.path.join(os.path.dirname(abs_path), new_name)
            shutil.move(abs_path, new_path)
    
    # Bước 7: Random tên thư mục item
    new_item_name = random_short_name()
    new_item_path = textures_root / new_item_name
    shutil.move(str(item_dir), str(new_item_path))
    
    # Bước 8: Tạo path mapping SAU KHI xáo trộn và rename
    path_mapping = {}
    
    # Thu thập lại tất cả file PNG sau khi xáo trộn
    for root, dirs, files in os.walk(new_item_path):
        for file in files:
            if file.endswith('.png'):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, textures_root)
                
                # Tìm tên gốc từ file_mapping
                for old_rel_path, new_name in file_mapping.items():
                    file_base = os.path.splitext(file)[0]
                    if file_base == new_name or file_base.startswith(new_name + "_"):
                        old_texture_path = "textures/item/" + old_rel_path.replace(os.sep, '/')
                        new_texture_path = "textures/" + rel_path.replace(os.sep, '/')[:-4]  # Bỏ .png
                        path_mapping[old_texture_path] = new_texture_path
                        break
    
    # Bước 9: Cập nhật attachables
    attachables_dir = Path("staging/target/rp/attachables")
    
    if attachables_dir.exists():
        for json_file in attachables_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    attachable_data = json.load(f)
                
                desc = attachable_data.get("minecraft:attachable", {}).get("description", {})
                textures = desc.get("textures", {})
                updated = False
                
                for tex_key, tex_value in textures.items():
                    if tex_value:
                        for old_path, new_path in path_mapping.items():
                            if old_path in tex_value:
                                textures[tex_key] = tex_value.replace(old_path, new_path)
                                updated = True
                
                if updated:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(attachable_data, f, ensure_ascii=False, indent=2)
            except:
                pass
