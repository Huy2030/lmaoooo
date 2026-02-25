import os
import json
import glob

class Bow2D_Util:
    @staticmethod
    def create_bow_animation():
        animation_data = {"animations":{"animation.campfire.bow_custom":{"bones":{"rightitem":{"position":[0.5,-2,0]}},"loop":True},"animation.campfire.bow_custom.first_person":{"bones":{"rightitem":{"position":["c.is_first_person ? -6 : 0","c.is_first_person ? -5 : 0","c.is_first_person ? -2 : 0"],"rotation":["c.is_first_person ? 30 : 0","c.is_first_person ? -120 : 0","c.is_first_person ? -60 : 0"]}},"loop":True}},"format_version":"1.8.0"}
        
        file_path = "staging/target/rp/animations/bow_custom.animation.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(animation_data, f, separators=(',', ':'))
        except Exception as e:
            pass

    @staticmethod
    def create_2d_bow_attachable(attachable_file, textures, identifier):
        attachable_data = {"format_version":"1.10.0","minecraft:attachable":{"description":{"animations":{"third_person":"animation.campfire.bow_custom","wield":"animation.campfire.bow_custom.first_person","wield_first_person_pull":"animation.bow.wield_first_person_pull"},"geometry":{"bow_pulling_0":"geometry.bow_pulling_0","bow_pulling_1":"geometry.bow_pulling_1","bow_pulling_2":"geometry.bow_pulling_2","default":"geometry.bow_standby"},"identifier":identifier,"materials":{"default":"entity_alphatest_one_sided","enchanted":"entity_alphatest_glint"},"render_controllers":["controller.render.bow_custom"],"scripts":{"animate":[{"wield":"c.is_first_person"},{"third_person":"!c.is_first_person"},{"wield_first_person_pull":"query.main_hand_item_use_duration > 0.0f && c.is_first_person"}],"pre_animation":["v.charge_amount = math.clamp((q.main_hand_item_max_duration - (q.main_hand_item_use_duration - q.frame_alpha + 1.0)) / 10.0, 0.0, 1.0f);","v.total_frames = 3;","v.step = v.total_frames / 60;","v.frame = query.is_using_item ? math.clamp((v.frame ?? 0) + v.step, 1, v.total_frames) : 0;"]},"textures":{"bow_pulling_0":textures.get("bow_pulling_0",textures.get("default","")),"bow_pulling_1":textures.get("bow_pulling_1",textures.get("default","")),"bow_pulling_2":textures.get("bow_pulling_2",textures.get("default","")),"default":textures.get("default",""),"enchanted":"textures/misc/enchanted_item_glint"}}}}
        
        try:
            with open(attachable_file, 'w', encoding='utf-8') as f:
                json.dump(attachable_data, f, separators=(',', ':'))
        except Exception as e:
            pass

    @staticmethod
    def process_bow_2d():
        try:
            with open("pack/assets/minecraft/models/item/bow.json", 'r', encoding='utf-8') as f:
                bow_data = json.load(f)
        except Exception as e:
            return
        
        # Group overrides by model path
        bow_groups = {}
        for override in bow_data.get("overrides", []):
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
            
            # Get base name (bow1, bow1_0, bow1_1, bow1_2)
            base_name = path.split("/")[-1]
            
            # Group by base name without suffix
            group_key = base_name.split("_")[0] if "_" in base_name else base_name
            
            if group_key not in bow_groups:
                bow_groups[group_key] = {}
            
            bow_groups[group_key][base_name] = {
                "namespace": namespace,
                "path": path,
                "model_path": model_path
            }
        
        # Process each bow group
        for group_key, models in bow_groups.items():
            if len(models) < 4:
                # Tạo relative path cho error message
                first_model = list(models.values())[0]
                namespace = first_model["namespace"]
                model_path_parts = first_model["path"].split("/")
                attachables_path = "/".join(model_path_parts[:-1])
                base_name = model_path_parts[-1]
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_name}.json"
                print(f"❌ Không xử lý bow 2D: {relative_attachable_path}")
                continue
            
            # Find base model (without _0, _1, _2 suffix)
            base_model = None
            for name in models.keys():
                if not any(name.endswith(f"_{i}") for i in range(3)):
                    base_model = name
                    break
            
            if not base_model:
                # Tạo relative path cho error message
                first_model = list(models.values())[0]
                namespace = first_model["namespace"]
                model_path_parts = first_model["path"].split("/")
                attachables_path = "/".join(model_path_parts[:-1])
                base_name = model_path_parts[-1]
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_name}.json"
                print(f"❌ Không xử lý bow 2D: {relative_attachable_path}")
                continue
            
            namespace = models[base_model]["namespace"]
            
            # Get path from first model to determine attachables directory structure
            first_model = list(models.values())[0]
            model_path_parts = first_model["path"].split("/")
            attachables_path = "/".join(model_path_parts[:-1])  # Remove filename, keep directory path
            attachables_dir = f"staging/target/rp/attachables/{namespace}/{attachables_path}"
            
            if not os.path.exists(attachables_dir):
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_model}.json"
                print(f"❌ Không xử lý bow 2D: {relative_attachable_path}")
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
                            textures["bow_pulling_0"] = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                        elif model_name.endswith("_1"):
                            textures["bow_pulling_1"] = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                        elif model_name.endswith("_2"):
                            textures["bow_pulling_2"] = attachable_data["minecraft:attachable"]["description"]["textures"]["default"]
                        
                    except Exception as e:
                        pass
            
            if identifier and len(textures) == 4:
                # Create 2D bow attachable (overwrite base model)
                base_attachable_file = f"{attachables_dir}/{base_model}.json"
                Bow2D_Util.create_2d_bow_attachable(base_attachable_file, textures, identifier)
                
                # Tạo relative path cho success message
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_model}.json"
                print(f"✅ Xử lý bow 2D: {relative_attachable_path}")
                
                # Delete pulling models (_0, _1, _2)
                for model_name in models.keys():
                    if model_name != base_model and any(model_name.endswith(f"_{i}") for i in range(3)):
                        attachable_to_delete = f"{attachables_dir}/{model_name}.json"
                        try:
                            if os.path.exists(attachable_to_delete):
                                os.remove(attachable_to_delete)
                        except Exception as e:
                            pass
            else:
                # Tạo relative path cho error message
                relative_attachable_path = f"{namespace}/{attachables_path}/{base_model}.json"
                print(f"❌ Không xử lý bow 2D: {relative_attachable_path}")
                
                # Delete all bow models in staging/target/rp/models/entity/ (including base model)
                for model_name, model_info in models.items():
                    model_to_delete = f"staging/target/rp/models/entity/{model_info['namespace']}/{model_info['path']}.json"
                    try:
                        if os.path.exists(model_to_delete):
                            os.remove(model_to_delete)
                    except Exception as e:
                        pass

if __name__ == "__main__":
    Bow2D_Util.create_bow_animation()
    Bow2D_Util.process_bow_2d()