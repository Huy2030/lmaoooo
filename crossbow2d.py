import os
import json
import glob

class Crossbow2D_Util:
    @staticmethod
    def create_crossbow_animation():
        animation_data = {"format_version":"1.10.0","animations":{"animation.crossbow_custom.wield":{"loop":True,"bones":{"rightitem":{"position":["c.is_first_person ? 13.0 : 0.5","c.is_first_person ? 7.0 : -0.5","c.is_first_person ? 2.0 : -1.5"],"rotation":["c.is_first_person ? -9.0 : 0.0","c.is_first_person ? 60.0 : -3.0","c.is_first_person ? -47.0 : 3.25"]}}},"animation.crossbow_custom.wield_first_person_pull":{"loop":True,"bones":{"rightitem":{"position":[0,"0.0 + ( variable.charge_amount  >= 1.0 ? math.sin( (q.life_time) * 1000.0 * 1.3) * 0.1 - math.sin(q.life_time * 45.0) * 0.25 : 0.0)",0]}}}}}
        
        file_path = "staging/target/rp/animations/crossbow_custom.animation.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(animation_data, f, separators=(',', ':'))

    @staticmethod
    def create_crossbow_render_controller():
        render_data = {"format_version": "1.10","render_controllers": {"controller.render.custom_crossbow2d": {"arrays": {"textures": {"array.crossbow_texture_frames": ["texture.default","texture.crossbow_pulling_0","texture.crossbow_pulling_1","texture.crossbow_pulling_2"]},"geometries": {"array.crossbow_geo_frames": ["geometry.default","geometry.crossbow_pulling_0","geometry.crossbow_pulling_1","geometry.crossbow_pulling_2"]}},"geometry": "array.crossbow_geo_frames[math.floor(v.frame)]","materials": [ { "*": "variable.is_enchanted ? material.enchanted : material.default" } ],"textures": [ "array.crossbow_texture_frames[math.floor(v.frame)]", "texture.enchanted" ]}}}
        
        file_path = "staging/target/rp/render_controllers/crossbow2d.render_controllers.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(render_data, f, separators=(',', ':'))

    @staticmethod
    def process_crossbow_2d():
        try:
            with open("pack/assets/minecraft/models/item/crossbow.json", 'r', encoding='utf-8') as f:
                crossbow_data = json.load(f)
        except Exception as e:
            return
        
        # Group overrides by model path
        crossbow_groups = {}
        for override in crossbow_data.get("overrides", []):
            predicate = override.get("predicate", {})
            model_path = override.get("model", "")
            
            if not model_path:
                continue
                
            parts = model_path.split(":")
            if len(parts) != 2:
                continue
            namespace, path = parts
            
            # Check if model is 2D
            model_file = f"pack/assets/{namespace}/models/{path}.json"
            if not os.path.exists(model_file):
                continue
                
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
                if "parent" not in model_data:
                    continue
            except:
                continue
            
            # Get base name
            base_name = path.split("/")[-1]
            
            # Group by base name without suffix
            group_key = base_name.split("_")[0] if "_" in base_name else base_name
            
            if group_key not in crossbow_groups:
                crossbow_groups[group_key] = {}
            
            crossbow_groups[group_key][base_name] = {
                "namespace": namespace,
                "path": path,
                "model_path": model_path
            }
        
        # Process each crossbow group
        for group_key, models in crossbow_groups.items():
            # Cần ít nhất base + 2 variants (_0, _1, _charged, _firework)
            if len(models) < 3:
                # Tạo relative path cho error message
                first_model = list(models.values())[0]
                namespace = first_model["namespace"]
                model_path_parts = first_model["path"].split("/")
                attachables_path = "/".join(model_path_parts[:-1])
                base_name = model_path_parts[-1]
                
                # Loại bỏ các suffix để hiển thị tên gọn
                for suffix in ["_0", "_1", "_2", "_3", "_charged", "_firework"]:
                    if base_name.endswith(suffix):
                        base_name = base_name[:-len(suffix)]
                        break
                
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_name}.json"
                print(f"❌ Không xử lý crossbow 2D: {relative_attachable_path} (không đủ variants)")
                continue
            
            # Find base model (without _0, _1, _2, _3, _charged, _firework suffix)
            base_model = None
            for name in models.keys():
                if not any(name.endswith(suffix) for suffix in ["_0", "_1", "_2", "_3", "_charged", "_firework"]):
                    base_model = name
                    break
            
            if not base_model:
                # Tạo relative path cho error message
                first_model = list(models.values())[0]
                namespace = first_model["namespace"]
                model_path_parts = first_model["path"].split("/")
                attachables_path = "/".join(model_path_parts[:-1])
                base_name = model_path_parts[-1]
                
                # Loại bỏ các suffix để hiển thị tên gọn
                for suffix in ["_0", "_1", "_2", "_3", "_charged", "_firework"]:
                    if base_name.endswith(suffix):
                        base_name = base_name[:-len(suffix)]
                        break
                
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_name}.json"
                print(f"❌ Không xử lý crossbow 2D: {relative_attachable_path} (không tìm thấy base model)")
                continue
            
            namespace = models[base_model]["namespace"]
            
            # Get path from first model to determine attachables directory structure
            first_model = list(models.values())[0]
            model_path_parts = first_model["path"].split("/")
            attachables_path = "/".join(model_path_parts[:-1])
            attachables_dir = f"staging/target/rp/attachables/{namespace}/{attachables_path}"
            if not os.path.exists(attachables_dir):
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_model}.json"
                print(f"❌ Không xử lý crossbow 2D: {relative_attachable_path}")
                continue
            
            # Read attachables to get identifier and textures
            identifier = None
            textures = {}
            
            for model_name, model_info in models.items():
                attachable_file = f"{attachables_dir}/{model_name}.json"
                if os.path.exists(attachable_file):
                    try:
                        with open(attachable_file, 'r', encoding='utf-8') as f:
                            attachable_data = json.load(f)
                        
                        # Get identifier from base model
                        if model_name == base_model:
                            identifier = attachable_data["minecraft:attachable"]["description"]["identifier"]
                            textures["default"] = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                        
                        # Get textures from pulling models
                        if model_name.endswith("_0"):
                            textures["crossbow_pulling_0"] = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                        elif model_name.endswith("_1"):
                            textures["crossbow_pulling_1"] = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                        elif model_name.endswith("_charged"):
                            texture_path = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                            textures["crossbow_pulling_2"] = texture_path
                        elif model_name.endswith("_firework"):
                            texture_path = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                            # _firework có thể dùng làm texture cho charged state hoặc bỏ qua
                            if "crossbow_pulling_2" not in textures:
                                textures["crossbow_pulling_2"] = texture_path
                        elif model_name.endswith("_2"):
                            texture_path = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                            # Chỉ sử dụng nếu cần, không xóa
                        
                    except Exception as e:
                        pass
            
            if identifier and len(textures) >= 3:  # Cần ít nhất default + 2 pulling textures
                # Đảm bảo có đủ 4 textures, dùng default nếu thiếu
                if "crossbow_pulling_0" not in textures:
                    textures["crossbow_pulling_0"] = textures.get("default", "")
                if "crossbow_pulling_1" not in textures:
                    textures["crossbow_pulling_1"] = textures.get("default", "")
                if "crossbow_pulling_2" not in textures:
                    textures["crossbow_pulling_2"] = textures.get("default", "")
                
                # Create 2D crossbow attachable (overwrite base model)
                base_attachable_file = f"{attachables_dir}/{base_model}.json"
                Crossbow2D_Util.create_2d_crossbow_attachable(base_attachable_file, textures, identifier)
                
                # Tạo relative path cho success message
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_model}.json"
                print(f"✅ Xử lý crossbow 2D: {relative_attachable_path}")
                
                # Delete pulling models (_0, _1, _2, _3, _charged, _firework)
                for model_name in models.keys():
                    if model_name != base_model and any(model_name.endswith(suffix) for suffix in ["_0", "_1", "_2", "_3", "_charged", "_firework"]):
                        attachable_to_delete = f"{attachables_dir}/{model_name}.json"
                        try:
                            if os.path.exists(attachable_to_delete):
                                os.remove(attachable_to_delete)
                        except Exception as e:
                            pass
                
                # Delete all crossbow models in staging/target/rp/models/entity/
                for model_name, model_info in models.items():
                    model_to_delete = f"staging/target/rp/models/entity/{model_info['namespace']}/{model_info['path']}.json"
                    try:
                        if os.path.exists(model_to_delete):
                            os.remove(model_to_delete)
                    except Exception as e:
                        pass
            else:
                # Tạo relative path cho error message
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_model}.json"
                print(f"❌ Không xử lý crossbow 2D: {relative_attachable_path} (thiếu textures: {len(textures)}/4)")

    @staticmethod
    def create_2d_crossbow_attachable(attachable_file, textures, identifier):
        attachable_data = {"format_version": "1.10.0","minecraft:attachable": {"description": {"identifier": identifier,"materials": {"default": "entity_alphatest_one_sided","enchanted": "entity_alphatest_glint"},"textures": {"default": textures.get("default",""),"crossbow_pulling_0": textures.get("crossbow_pulling_0",textures.get("default","")),"crossbow_pulling_1": textures.get("crossbow_pulling_1",textures.get("default","")),"crossbow_pulling_2": textures.get("crossbow_pulling_2",textures.get("default","")),"enchanted": "textures/misc/enchanted_item_glint"},"geometry": {"default": "geometry.crossbow_standby","crossbow_pulling_0": "geometry.crossbow_pulling_0","crossbow_pulling_1": "geometry.crossbow_pulling_1","crossbow_pulling_2": "geometry.crossbow_pulling_2"},"animations": {"wield": "animation.crossbow.wield","wield_first_person_pull": "animation.crossbow.wield_first_person_pull"},"scripts": {"pre_animation": ["v.charge_amount = math.clamp((q.main_hand_item_max_duration - (q.main_hand_item_use_duration - q.frame_alpha + 1.0)) / 10.0, 0.0, 1.0);","v.total_frames = 5;","v.frame = v.frame ?? 0;","v.step = q.delta_time;","v.frame = query.is_using_item ? math.clamp(v.frame + v.step, 1, 3) : 0;","v.frame = v.frame == 3 && !query.is_using_item ? 4 : v.frame;","v.frame = query.is_using_item ? math.clamp((v.frame ?? 0) + v.step, 1, 3) : 0;","v.frame = query.item_is_charged('main_hand') && !query.is_item_name_any('slot.weapon.offhand', 0, 'minecraft:firework_rocket') ? 4 : v.frame;","v.frame = query.item_is_charged('main_hand') && query.is_item_name_any('slot.weapon.offhand', 0, 'minecraft:firework_rocket') ? 5 : v.frame;"],"animate": ["wield", {"wield_first_person_pull": "query.main_hand_item_use_duration > 0.0f && c.is_first_person"}]},"render_controllers": ["controller.render.custom_crossbow2d"]}}}
        
        try:
            with open(attachable_file, 'w', encoding='utf-8') as f:
                json.dump(attachable_data, f, separators=(',', ':'))
        except Exception as e:
            pass

if __name__ == "__main__":
    Crossbow2D_Util.create_crossbow_animation()
    Crossbow2D_Util.create_crossbow_render_controller()
    Crossbow2D_Util.process_crossbow_2d()