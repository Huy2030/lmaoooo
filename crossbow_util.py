import json
import os
import glob
import shutil

class Crossbow_Util:
    @staticmethod
    def get_crossbow_variants_info(namespace, model_path=""):
        """
        Lấy thông tin geometry và texture từ các crossbow model files riêng biệt
        TRƯỚC KHI chúng bị gộp bởi merge_crossbow_models()
        """
        model_dir = f"staging/target/rp/models/entity/{namespace}"
        if model_path:
            model_dir = f"{model_dir}/{model_path}"
        
        # Tìm các geometry names từ model files (trước khi merge)
        def get_geometry_from_model(model_file_path):
            if os.path.exists(model_file_path):
                try:
                    with open(model_file_path, "r") as mf:
                        model_data = json.load(mf)
                        if "minecraft:geometry" in model_data and len(model_data["minecraft:geometry"]) > 0:
                            return model_data["minecraft:geometry"][0]["description"]["identifier"]
                except:
                    pass
            return None
        
        # Map các model files với geometry (tìm tất cả variants có thể)
        crossbow_variants = []
        if os.path.exists(model_dir):
            for json_file in glob.glob(os.path.join(model_dir, "*.json")):
                filename = os.path.basename(json_file).lower()
                if "crossbow" in filename:
                    crossbow_variants.append(json_file)
        
        # Tìm các file cụ thể
        crossbow_model = None
        crossbow_1_model = None  
        crossbow_charged_model = None
        
        for variant_file in crossbow_variants:
            filename = os.path.basename(variant_file).lower()
            if filename.endswith("crossbow.json"):
                crossbow_model = variant_file
            elif filename.endswith("crossbow_1.json") or filename.endswith("crossbow-1.json"):
                crossbow_1_model = variant_file
            elif filename.endswith("crossbow_charged.json") or filename.endswith("crossbow-charged.json"):
                crossbow_charged_model = variant_file
        
        # Lấy geometry identifiers
        default_geometry = get_geometry_from_model(crossbow_model) if crossbow_model else None
        pulling_1_geometry = get_geometry_from_model(crossbow_1_model) if crossbow_1_model else None
        pulling_2_geometry = get_geometry_from_model(crossbow_charged_model) if crossbow_charged_model else None
        
        # Tạo texture paths từ model files
        def get_texture_from_model(model_file_path, namespace, model_path, model_name):
            # Tạo texture path dựa trên cấu trúc thư mục
            if model_path:
                return f"textures/{namespace}/{model_path}/{model_name}"
            else:
                return f"textures/{namespace}/{model_name}"
        
        # Map texture paths
        default_texture = get_texture_from_model(crossbow_model, namespace, model_path, "crossbow") if crossbow_model else None
        pulling_1_texture = get_texture_from_model(crossbow_1_model, namespace, model_path, "crossbow_1") if crossbow_1_model else None
        pulling_2_texture = get_texture_from_model(crossbow_charged_model, namespace, model_path, "crossbow_charged") if crossbow_charged_model else None
        
        return {
            "textures": [
                default_texture,
                pulling_1_texture,
                pulling_2_texture
            ],
            "geometry": [
                default_geometry,
                pulling_1_geometry,
                pulling_2_geometry
            ],
            "found_files": {
                "crossbow": crossbow_model is not None,
                "crossbow_1": crossbow_1_model is not None,
                "crossbow_charged": crossbow_charged_model is not None
            }
        }

    @staticmethod
    def merge_crossbow_models():
        merged_count = 0
        
        # Tìm tất cả thư mục models/entity/*/ và models/entity/*/*/
        model_dirs = glob.glob("staging/target/rp/models/entity/*/", recursive=True)
        model_dirs.extend(glob.glob("staging/target/rp/models/entity/*/*/", recursive=True))
        
        for model_dir in model_dirs:
            # Tìm các file crossbow để gộp với pattern linh hoạt
            crossbow_files_to_merge = []
            
            # Tìm tất cả file JSON trong thư mục
            all_json_files = glob.glob(os.path.join(model_dir, "*.json"))
            
            for json_file in all_json_files:
                filename = os.path.basename(json_file).lower()
                
                # Kiểm tra các pattern được phép gộp - linh hoạt hơn với prefix
                if (filename.endswith("crossbow.json") or 
                    filename.endswith("crossbow_1.json") or 
                    filename.endswith("crossbow_charged.json") or
                    filename.endswith("crossbow-1.json") or 
                    filename.endswith("crossbow-charged.json") or
                    ("crossbow" in filename and (filename.endswith("_1.json") or filename.endswith("-1.json"))) or
                    ("crossbow" in filename and (filename.endswith("_charged.json") or filename.endswith("-charged.json")))):
                    crossbow_files_to_merge.append(json_file)
            
            if not crossbow_files_to_merge:
                continue
                
            # Đọc và gộp các crossbow models được phép
            merged_data = {}
            
            for crossbow_file in crossbow_files_to_merge:
                try:
                    with open(crossbow_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Gộp vào merged_data
                    if not merged_data:
                        # File đầu tiên - copy toàn bộ structure
                        merged_data = data.copy()
                    else:
                        # Gộp geometries từ các file khác
                        if "minecraft:geometry" in data:
                            if "minecraft:geometry" not in merged_data:
                                merged_data["minecraft:geometry"] = []
                            
                            # Thêm geometries mới vào merged_data
                            for geometry in data["minecraft:geometry"]:
                                merged_data["minecraft:geometry"].append(geometry)
                                
                except Exception as e:
                    continue
            
            if merged_data:
                # Tạo file merge2.json
                merge_file = os.path.join(model_dir, "merge2.json")
                try:
                    with open(merge_file, 'w', encoding='utf-8') as f:
                        json.dump(merged_data, f, indent=2)
                    
                    # Tìm và xóa TẤT CẢ file có tên chứa "crossbow" (bao gồm cả những file không được gộp)
                    all_json_files = glob.glob(os.path.join(model_dir, "*.json"))
                    for json_file in all_json_files:
                        filename = os.path.basename(json_file).lower()
                        if "crossbow" in filename:
                            try:
                                os.remove(json_file)
                            except Exception as e:
                                pass
                    
                    # Đổi tên merge2.json thành crossbow.json
                    final_file = os.path.join(model_dir, "crossbow.json")
                    os.rename(merge_file, final_file)
                    
                    merged_count += 1
                    
                except Exception as e:
                    pass
        
        return merged_count

    @staticmethod
    def cleanup_crossbow_variants():
        """Xóa các crossbow variant files trong attachables, chỉ giữ lại crossbow.json chính"""
        removed_count = 0
        
        # Tìm trong tất cả thư mục có thể chứa attachables
        search_paths = [
            "staging/target/rp/attachables/**/*crossbow*.json",
            "staging/target/bp/attachables/**/*crossbow*.json", 
            "staging/bedrock/rp/attachables/**/*crossbow*.json",
            "staging/bedrock/bp/attachables/**/*crossbow*.json"
        ]
        
        crossbow_files = []
        for path in search_paths:
            found_files = glob.glob(path, recursive=True)
            crossbow_files.extend(found_files)
        
        for json_file in crossbow_files:
            filename = os.path.basename(json_file).lower()
            
            # Kiểm tra nếu là crossbow 2D (có parent trong model)
            try:
                # Lấy namespace và path từ attachable file
                relative_path = json_file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
                parts = relative_path.split("/")
                if len(parts) >= 2:
                    namespace = parts[0]
                    model_path = "/".join(parts[1:-1]) if len(parts) > 2 else ""
                    model_name = parts[-1].replace(".json", "")
                    
                    # Kiểm tra model file tương ứng
                    if model_path:
                        model_file = f"pack/assets/{namespace}/models/{model_path}/{model_name}.json"
                    else:
                        model_file = f"pack/assets/{namespace}/models/{model_name}.json"
                    
                    if os.path.exists(model_file):
                        with open(model_file, 'r', encoding='utf-8') as f:
                            model_data = json.load(f)
                            if "parent" in model_data:
                                continue
            except Exception as e:
                pass
            
            # Chỉ giữ lại file crossbow.json chính, xóa tất cả variants
            if filename != "crossbow.json":
                try:
                    os.remove(json_file)
                    removed_count += 1
                except Exception as e:
                    pass
        
        return removed_count

    @staticmethod
    def get_crossbow_charged_display_data(namespace, model_path, model_name):
        """Lấy display data từ crossbow_charged tương ứng với crossbow đang xử lý"""
        import glob
        import os
        
        try:
            # Đọc crossbow.json từ pack để tìm custom_model_data của crossbow hiện tại
            with open("pack/assets/minecraft/models/item/crossbow.json", 'r', encoding='utf-8') as f:
                crossbow_data = json.load(f)
            
            # Tìm custom_model_data của crossbow hiện tại
            current_cmd = None
            target_model = f"{namespace}:{model_path}/{model_name}" if model_path else f"{namespace}:{model_name}"
            
            for override in crossbow_data.get("overrides", []):
                predicate = override.get("predicate", {})
                model = override.get("model", "")
                
                if model == target_model and "custom_model_data" in predicate:
                    current_cmd = predicate["custom_model_data"]
                    break
            
            if not current_cmd:
                return {
                    'translation': [0, -0.75, -0.75],
                    'rotation': [0, 0, 0],
                    'scale': [0.56, 0.56, 0.56]
                }
            
            # Tìm crossbow_charged có cùng custom_model_data
            for override in crossbow_data.get("overrides", []):
                predicate = override.get("predicate", {})
                model = override.get("model", "")
                
                if (predicate.get("custom_model_data") == current_cmd and 
                    predicate.get("charged") == 1 and 
                    "firework" not in predicate):
                    
                    if ":" in model:
                        ns, path = model.split(":", 1)
                        charged_file = f"pack/assets/{ns}/models/{path}.json"
                        
                        if os.path.exists(charged_file):
                            try:
                                with open(charged_file, 'r', encoding='utf-8') as f:
                                    charged_data = json.load(f)
                                
                                if 'display' in charged_data and 'firstperson_righthand' in charged_data['display']:
                                    fp_rh = charged_data['display']['firstperson_righthand']
                                    return {
                                        'translation': fp_rh.get('translation', [0, 0, 0]),
                                        'rotation': fp_rh.get('rotation', [0, 0, 0]),
                                        'scale': fp_rh.get('scale', [1, 1, 1])
                                    }
                            except Exception as e:
                                continue
            
        except Exception as e:
            pass
        
        return {
            'translation': [0, -0.75, -0.75],
            'rotation': [0, 0, 0],
            'scale': [0.56, 0.56, 0.56]
        }

    @staticmethod
    def get_display_initialize(display_data, namespace=None, model_path="", model_name="crossbow"):
        def get_value(path, default):
            keys = path.split('.')
            value = display_data
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                    if value is None:
                        return default
                elif isinstance(value, list):
                    try:
                        index = int(key)
                        if 0 <= index < len(value):
                            value = value[index]
                        else:
                            return default
                    except (ValueError, IndexError):
                        return default
                else:
                    return default
            return value if value is not None else default
        
        def format_number(num):
            if isinstance(num, (int, float)):
                if num == int(num):
                    return int(num)
            return num
        
        def format_scale(scale):
            if isinstance(scale, list) and len(scale) >= 1:
                return format_number(scale[0])
            return format_number(scale)
        
        tp_rh_rot = get_value('thirdperson_righthand.rotation', [0, 0, 0])
        tp_rh_trans = get_value('thirdperson_righthand.translation', [0, 0, 0])
        tp_rh_scale = get_value('thirdperson_righthand.scale', [1, 1, 1])
        
        tp_lh_rot = get_value('thirdperson_lefthand.rotation', [0, 0, 0])
        tp_lh_trans = get_value('thirdperson_lefthand.translation', [0, 0, 0])
        tp_lh_scale = get_value('thirdperson_lefthand.scale', [1, 1, 1])
        
        fp_rh_rot = get_value('firstperson_righthand.rotation', [0, 0, 0])
        fp_rh_trans = get_value('firstperson_righthand.translation', [0, 0, 0])
        fp_rh_scale = get_value('firstperson_righthand.scale', [1, 1, 1])
        
        fp_lh_rot = get_value('firstperson_lefthand.rotation', [0, 0, 0])
        fp_lh_trans = get_value('firstperson_lefthand.translation', [0, 0, 0])
        fp_lh_scale = get_value('firstperson_lefthand.scale', [1, 1, 1])
        

        def get_crossbow_charged_display_data():
            import glob
            import os
            
            # Đọc crossbow.json từ pack để tìm mapping
            try:
                with open("pack/assets/minecraft/models/item/crossbow.json", 'r', encoding='utf-8') as f:
                    crossbow_data = json.load(f)
                
                # Tạo mapping từ custom_model_data đến crossbow_charged model
                charged_models = {}
                for override in crossbow_data.get("overrides", []):
                    predicate = override.get("predicate", {})
                    model_path = override.get("model", "")
                    
                    if "custom_model_data" in predicate and "charged" in predicate and predicate.get("charged") == 1:
                        if "firework" not in predicate:  # Chỉ lấy crossbow_charged, không lấy crossbow_firework
                            cmd = predicate["custom_model_data"]
                            charged_models[cmd] = model_path
                
                # Tìm crossbow_charged model tương ứng với namespace đang xử lý
                for cmd, model_path in charged_models.items():
                    if ":" in model_path:
                        namespace, path = model_path.split(":", 1)
                        charged_file = f"pack/assets/{namespace}/models/{path}.json"
                        
                        if os.path.exists(charged_file):
                            try:
                                with open(charged_file, 'r', encoding='utf-8') as f:
                                    charged_data = json.load(f)
                                    
                                if 'display' in charged_data and 'firstperson_righthand' in charged_data['display']:
                                    fp_rh = charged_data['display']['firstperson_righthand']
                                    return {
                                        'translation': fp_rh.get('translation', [0, 0, 0]),
                                        'rotation': fp_rh.get('rotation', [0, 0, 0]),
                                        'scale': fp_rh.get('scale', [1, 1, 1])
                                    }
                            except Exception as e:
                                continue
                
            except Exception as e:
                pass
            
            return {
                'translation': [0, -0.75, -0.75],
                'rotation': [0, 0, 0],
                'scale': [0.56, 0.56, 0.56]
            }
        
        crossbow_charged_data = Crossbow_Util.get_crossbow_charged_display_data(namespace, model_path, model_name)
        crossbow_charged_fp_trans = crossbow_charged_data['translation']
        crossbow_charged_fp_rot = crossbow_charged_data['rotation']
        crossbow_charged_fp_scale = crossbow_charged_data['scale']
        
        return [
            f"v.thirdperson_mainhand_rot_x = {format_number(tp_rh_rot[0] if isinstance(tp_rh_rot, list) and len(tp_rh_rot) > 0 else 0)};",
            f"v.thirdperson_mainhand_rot_y = {format_number(tp_rh_rot[1] if isinstance(tp_rh_rot, list) and len(tp_rh_rot) > 1 else 0)};",
            f"v.thirdperson_mainhand_rot_z = {format_number(tp_rh_rot[2] if isinstance(tp_rh_rot, list) and len(tp_rh_rot) > 2 else 0)};",
            f"v.thirdperson_mainhand_pos_x = {format_number(tp_rh_trans[0] if isinstance(tp_rh_trans, list) and len(tp_rh_trans) > 0 else 0)};",
            f"v.thirdperson_mainhand_pos_y = {format_number(tp_rh_trans[1] if isinstance(tp_rh_trans, list) and len(tp_rh_trans) > 1 else 0)};",
            f"v.thirdperson_mainhand_pos_z = {format_number(tp_rh_trans[2] if isinstance(tp_rh_trans, list) and len(tp_rh_trans) > 2 else 0)};",
            f"v.thirdperson_mainhand_scale = {format_scale(tp_rh_scale)};",
            "v.thirdperson_hand_same = false;",
            f"v.thirdperson_offhand_rot_x = {format_number(tp_lh_rot[0] if isinstance(tp_lh_rot, list) and len(tp_lh_rot) > 0 else 0)};",
            f"v.thirdperson_offhand_rot_y = {format_number(tp_lh_rot[1] if isinstance(tp_lh_rot, list) and len(tp_lh_rot) > 1 else 0)};",
            f"v.thirdperson_offhand_rot_z = {format_number(tp_lh_rot[2] if isinstance(tp_lh_rot, list) and len(tp_lh_rot) > 2 else 0)};",
            f"v.thirdperson_offhand_pos_x = {format_number(tp_lh_trans[0] if isinstance(tp_lh_trans, list) and len(tp_lh_trans) > 0 else 0)};",
            f"v.thirdperson_offhand_pos_y = {format_number(tp_lh_trans[1] if isinstance(tp_lh_trans, list) and len(tp_lh_trans) > 1 else 0)};",
            f"v.thirdperson_offhand_pos_z = {format_number(tp_lh_trans[2] if isinstance(tp_lh_trans, list) and len(tp_lh_trans) > 2 else 0)};",
            f"v.thirdperson_offhand_scale = {format_scale(tp_lh_scale)};",
            f"v.firstperson_mainhand_rot_x = {format_number(fp_rh_rot[0] if isinstance(fp_rh_rot, list) and len(fp_rh_rot) > 0 else 0)};",
            f"v.firstperson_mainhand_rot_y = {format_number(fp_rh_rot[1] if isinstance(fp_rh_rot, list) and len(fp_rh_rot) > 1 else 0)};",
            f"v.firstperson_mainhand_rot_z = {format_number(fp_rh_rot[2] if isinstance(fp_rh_rot, list) and len(fp_rh_rot) > 2 else 0)};",
            f"v.firstperson_mainhand_pos_x = {format_number(fp_rh_trans[0] if isinstance(fp_rh_trans, list) and len(fp_rh_trans) > 0 else 0)};",
            f"v.firstperson_mainhand_pos_y = {format_number(fp_rh_trans[1] if isinstance(fp_rh_trans, list) and len(fp_rh_trans) > 1 else 0)};",
            f"v.firstperson_mainhand_pos_z = {format_number(fp_rh_trans[2] if isinstance(fp_rh_trans, list) and len(fp_rh_trans) > 2 else 0)};",
            f"v.firstperson_mainhand_scale = {format_scale(fp_rh_scale)};",
            "v.firstperson_hand_same = false;",
            f"v.firstperson_offhand_rot_x = {format_number(fp_lh_rot[0] if isinstance(fp_lh_rot, list) and len(fp_lh_rot) > 0 else 0)};",
            f"v.firstperson_offhand_rot_y = {format_number(fp_lh_rot[1] if isinstance(fp_lh_rot, list) and len(fp_lh_rot) > 1 else 0)};",
            f"v.firstperson_offhand_rot_z = {format_number(fp_lh_rot[2] if isinstance(fp_lh_rot, list) and len(fp_lh_rot) > 2 else 0)};",
            f"v.firstperson_offhand_pos_x = {format_number(fp_lh_trans[0] if isinstance(fp_lh_trans, list) and len(fp_lh_trans) > 0 else 0)};",
            f"v.firstperson_offhand_pos_y = {format_number(fp_lh_trans[1] if isinstance(fp_lh_trans, list) and len(fp_lh_trans) > 1 else 0)};",
            f"v.firstperson_offhand_pos_z = {format_number(fp_lh_trans[2] if isinstance(fp_lh_trans, list) and len(fp_lh_trans) > 2 else 0)};",
            f"v.firstperson_offhand_scale = {format_scale(fp_lh_scale)};",
            f"v.firstperson_pull_rot_x = {format_number(crossbow_charged_fp_rot[0])};",
            f"v.firstperson_pull_rot_y = {format_number(crossbow_charged_fp_rot[1])};",
            f"v.firstperson_pull_rot_z = {format_number(crossbow_charged_fp_rot[2])};",
            f"v.firstperson_pull_pos_x = {format_number(crossbow_charged_fp_trans[0])};",
            f"v.firstperson_pull_pos_y = {format_number(crossbow_charged_fp_trans[1])};",
            f"v.firstperson_pull_pos_z = {format_number(crossbow_charged_fp_trans[2])};",
            f"v.firstperson_pull_scale = {format_scale(crossbow_charged_fp_scale)};",
            f"v.firstperson_charged_rot_x = {format_number(crossbow_charged_fp_rot[0])};",
            f"v.firstperson_charged_rot_y = {format_number(crossbow_charged_fp_rot[1])};",
            f"v.firstperson_charged_rot_z = {format_number(crossbow_charged_fp_rot[2])};",
            f"v.firstperson_charged_pos_x = {format_number(crossbow_charged_fp_trans[0])};",
            f"v.firstperson_charged_pos_y = {format_number(crossbow_charged_fp_trans[1])};",
            f"v.firstperson_charged_pos_z = {format_number(crossbow_charged_fp_trans[2])};",
            f"v.firstperson_charged_scale = {format_scale(crossbow_charged_fp_scale)};"
        ]
    
    @staticmethod
    def update_attachable(file, identifier, materials, textures, geometry, animations, display_data=None):
        """Cập nhật crossbow attachable file - dùng cho cả 2D và 3D"""
        if display_data is None:
            display_data = {}
        
        # Lấy namespace và model info từ file path
        relative_path = file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
        parts = relative_path.split("/")
        namespace = parts[0] if len(parts) > 0 else ""
        model_path = "/".join(parts[1:-1]) if len(parts) > 2 else ""
        model_name = parts[-1].replace(".json", "") if len(parts) > 0 else "crossbow"
        
        initialize = Crossbow_Util.get_display_initialize(display_data, namespace, model_path, model_name)
        
        pre_animation = [
            "v.main_hand = c.item_slot=='main_hand';",
            "v.off_hand = c.item_slot=='off_hand';",
            "v.charge_amount = math.clamp((q.main_hand_item_max_duration - (q.main_hand_item_use_duration - q.frame_alpha + 1.0)) / 10.0, 0.0, 1.0f);",
            "v.total_frames = 3;",
            "v.step = v.total_frames / 70;",
            "v.frame = q.is_using_item ? math.clamp((v.frame ?? 0) + v.step, 1, v.total_frames) : 0;",
            "v.frame = q.item_is_charged('main_hand') && !q.is_item_name_any('slot.weapon.offhand', 0, 'minecraft:firework_rocket') ? 3 : v.frame;",
            "v.frame = q.item_is_charged('main_hand') && q.is_item_name_any('slot.weapon.offhand', 0, 'minecraft:firework_rocket') ? 4 : v.frame;"
        ]
        
        animate = [
            {"thirdperson_hand": "(v.main_hand||v.off_hand)&&!c.is_first_person"},
            {"thirdperson_head": "v.head&&!c.is_first_person"},
            {"firstperson_hand": "!q.item_is_charged&&(v.main_hand||v.off_hand)&&c.is_first_person&&!v.frame"},
            {"firstperson_head": "c.is_first_person&&v.head"},
            {"firstperson_main_hand_charged": "q.item_is_charged&&v.main_hand&&c.is_first_person"},
            {"wield_first_person_pull_pos": "!q.item_is_charged&&v.main_hand&&c.is_first_person&&v.frame"},
            {"wield_first_person_pull": "v.main_hand&&q.is_using_item&&q.main_hand_item_use_duration>0.0f&&c.is_first_person"}
        ]
        
        animations_dict = {
            "thirdperson_hand": "animation.campfire.thirdperson_hand",
            "thirdperson_head": "animation.campfire.thirdperson_head",
            "firstperson_hand": "animation.campfire.firstperson_hand",
            "firstperson_head": "animation.campfire.disable",
            "firstperson_main_hand_charged": "animation.campfire.custom_crossbow.firstperson_main_hand_charged",
            "wield_first_person_pull_pos": "animation.campfire.custom_crossbow.wield_first_person_pull_pos",
            "wield_first_person_pull": "animation.campfire.custom_crossbow.wield_first_person_pull"
        }
        
        with open(file, "w") as f:
            data = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": identifier,
                        "materials": materials,
                        "textures": {
                            "default": textures[0],
                            "crossbow_pulling_1": textures[1],
                            "crossbow_pulling_2": textures[2],
                            "enchanted": "textures/misc/enchanted_item_glint"
                        },
                        "geometry": {
                            "default": geometry[0],
                            "crossbow_pulling_1": geometry[1],
                            "crossbow_pulling_2": geometry[2]
                        },
                        "animations": animations_dict,
                        "scripts": {
                            "initialize": initialize,
                            "pre_animation": pre_animation,
                            "animate": animate
                        },
                        "render_controllers": ["controller.render.custom_crossbow"]
                    }
                }
            }
            json.dump(data, f, indent=2)
        return True

    @staticmethod
    def rendercontrollers():
        file = "staging/target/rp/render_controllers/crossbow_custom.render_controllers.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.10",
                "render_controllers": {
                    "controller.render.custom_crossbow": {
                        "arrays": {
                            "textures": {
                                "array.crossbow_texture_frames": [
                                    "texture.default",
                                    "texture.default",
                                    "texture.crossbow_pulling_1",
                                    "texture.crossbow_pulling_2"
                                ]
                            },
                            "geometries": {
                                "array.crossbow_geo_frames": [
                                    "geometry.default",
                                    "geometry.default",
                                    "geometry.crossbow_pulling_1",
                                    "geometry.crossbow_pulling_2"
                                ]
                            }
                        },
                        "geometry": "array.crossbow_geo_frames[math.floor(v.frame)]",
                        "materials": [
                            {
                                "*": "variable.is_enchanted ? material.enchanted : material.default"
                            }
                        ],
                        "textures": [
                            "array.crossbow_texture_frames[math.floor(v.frame)]",
                            "texture.enchanted"
                        ]
                    }
                }
            }
            json.dump(data, f, indent=2)

    @staticmethod
    def acontroller(gmdllist):
        """Tạo player firstperson animation controller cho crossbow"""
        strlist = str(gmdllist)
        strlist = strlist.replace("[", "").replace("]", "")
        file = "staging/target/rp/animations/player_firstperson.animation.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.8.0",
                "animations": {
                    "animation.player.first_person.crossbow_equipped": {
                        "bones": {
                            "leftarm": {
                                "position": [
                                    "1.5 - variable.item_use_normalized * 3.5",
                                    "-3.799999952316284 + variable.short_arm_offset_left",
                                    "8.25 - (1 - variable.item_use_normalized)"
                                ],
                                "rotation": [165, -60, 45],
                                "scale": [0.4, 0.4, 0.4]
                            },
                            "rightitem": {
                                "position": [
                                    0,
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_firstperson_crossbow_load_anim') ? 0 : 2",
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_firstperson_crossbow_load_anim') ? 0 : 2.5 - query.item_remaining_use_duration('main_hand', 1) * 1.5"
                                ],
                                "rotation": [
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_firstperson_crossbow_load_anim') ? 0 : -20",
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_firstperson_crossbow_load_anim') ? 0 : -15",
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_firstperson_crossbow_load_anim') ? 0 : -30"
                                ],
                                "scale": [
                                    1,
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_firstperson_crossbow_load_anim') ? 1 : 1.15 - query.item_remaining_use_duration('main_hand', 1) * 0.15",
                                    1
                                ]
                            }
                        },
                        "loop": True,
                        "override_previous_animation": True
                    }
                }
            }
            json.dump(data, f, indent=2)
    @staticmethod
    def is2Dcrossbow(file):
        """Kiểm tra xem crossbow có phải là 2D không dựa vào cấu trúc bones"""
        try:
            with open(file, "r") as f:
                model_data = json.load(f)
                modelbone = model_data["minecraft:geometry"][0]["bones"]
        except:
            modelbone = []
        
        # Kiểm tra cấu trúc bones đặc trưng của 2D crossbow (tương tự 2D bow)
        if modelbone == [{"name":"campfire","binding":"c.item_slot == 'head' ? 'head' : q.item_slot_to_bone_name(c.item_slot)","pivot":[0,8,0]},{"name":"campfire_x","parent":"campfire","pivot":[0,8,0]},{"name":"campfire_y","parent":"campfire_x","pivot":[0,8,0]},{"name":"campfire_z","parent":"campfire_y","pivot":[0,8,0],"texture_meshes":[{"texture":"default","position":[0,8,0],"rotation":[90,0,-180],"local_pivot":[8,0.5,8]}]}]:
            return True
        else:
            return False