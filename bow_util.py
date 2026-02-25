import json
import os

class Bow_Util:
    @staticmethod
    def get_bow2_display_data(namespace, model_path, model_name):
        """Lấy display data từ bow_2 tương ứng với bow đang xử lý"""
        import glob
        import os
        
        try:
            # Đọc bow.json từ pack để tìm custom_model_data của bow hiện tại
            with open("pack/assets/minecraft/models/item/bow.json", 'r', encoding='utf-8') as f:
                bow_data = json.load(f)
            
            # Tìm custom_model_data của bow hiện tại
            current_cmd = None
            target_model = f"{namespace}:{model_path}/{model_name}" if model_path else f"{namespace}:{model_name}"
            
            for override in bow_data.get("overrides", []):
                predicate = override.get("predicate", {})
                model = override.get("model", "")
                
                if model == target_model and "custom_model_data" in predicate:
                    current_cmd = predicate["custom_model_data"]
                    break
            
            if not current_cmd:
                return None
            
            # Tìm bow_2 có cùng custom_model_data
            for override in bow_data.get("overrides", []):
                predicate = override.get("predicate", {})
                model = override.get("model", "")
                
                if (predicate.get("custom_model_data") == current_cmd and 
                    predicate.get("pulling") == 1 and 
                    predicate.get("pull") == 0.9):
                    
                    if ":" in model:
                        ns, path = model.split(":", 1)
                        bow2_file = f"pack/assets/{ns}/models/{path}.json"
                        
                        if os.path.exists(bow2_file):
                            try:
                                with open(bow2_file, 'r', encoding='utf-8') as f:
                                    bow2_data = json.load(f)
                                
                                if 'display' in bow2_data and 'firstperson_righthand' in bow2_data['display']:
                                    fp_rh = bow2_data['display']['firstperson_righthand']
                                    return {
                                        'translation': fp_rh.get('translation', [0, 0, 0]),
                                        'rotation': fp_rh.get('rotation', [0, 0, 0]),
                                        'scale': fp_rh.get('scale', [1, 1, 1])
                                    }
                            except Exception as e:
                                continue
            
        except Exception as e:
            pass
        
        return None

    @staticmethod
    def get_display_initialize(display_data, namespace=None, model_path="", model_name="bow"):
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

        def get_bow2_display_data():
            # Lấy bow2 display data từ bow_2 tương ứng
            bow2_data = Bow_Util.get_bow2_display_data(namespace, model_path, model_name)
            
            if bow2_data:
                return bow2_data
            else:
                # Fallback: sử dụng giá trị firstperson_righthand hiện tại
                return {
                    'translation': fp_rh_trans,
                    'rotation': fp_rh_rot,
                    'scale': fp_rh_scale
                }
        
        bow2_data = get_bow2_display_data()
        bow_pull_trans = bow2_data['translation']
        bow_pull_rot = bow2_data['rotation']
        bow_pull_scale = bow2_data['scale']
        
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
            f"v.firstperson_pull_rot_x = {format_number(bow_pull_rot[0] if isinstance(bow_pull_rot, list) and len(bow_pull_rot) > 0 else 0)};",
            f"v.firstperson_pull_rot_y = {format_number(bow_pull_rot[1] if isinstance(bow_pull_rot, list) and len(bow_pull_rot) > 1 else 0)};",
            f"v.firstperson_pull_rot_z = {format_number(bow_pull_rot[2] if isinstance(bow_pull_rot, list) and len(bow_pull_rot) > 2 else 0)};",
            f"v.firstperson_pull_pos_x = {format_number(bow_pull_trans[0] if isinstance(bow_pull_trans, list) and len(bow_pull_trans) > 0 else 0)};",
            f"v.firstperson_pull_pos_y = {format_number(bow_pull_trans[1] if isinstance(bow_pull_trans, list) and len(bow_pull_trans) > 1 else 0)};",
            f"v.firstperson_pull_pos_z = {format_number(bow_pull_trans[2] if isinstance(bow_pull_trans, list) and len(bow_pull_trans) > 2 else 0)};",
            f"v.firstperson_pull_scale = {format_scale(bow_pull_scale)};"
        ]

    @staticmethod
    def write(file, gmdl, textures, geometry, mdefault, menchanted, animations, animate, pre_animation, display_data=None):
        if display_data is None:
            display_data = {}
        
        # Lấy namespace và model info từ file path
        relative_path = file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
        parts = relative_path.split("/")
        namespace = parts[0] if len(parts) > 0 else ""
        model_path = "/".join(parts[1:-1]) if len(parts) > 2 else ""
        model_name = parts[-1].replace(".json", "") if len(parts) > 0 else "bow"
        
        initialize = Bow_Util.get_display_initialize(display_data, namespace, model_path, model_name)
        
        pre_animation = [
            "v.main_hand = c.item_slot=='main_hand';",
            "v.off_hand = c.item_slot=='off_hand';",
            "v.charge_amount = math.clamp((q.main_hand_item_max_duration - (q.main_hand_item_use_duration - q.frame_alpha + 1.0)) / 10.0, 0.0, 1.0f);",
            "v.total_frames = 3;",
            "v.step = v.total_frames / 55;",
            "v.frame = q.is_using_item ? math.clamp((v.frame ?? 0) + v.step, 1, v.total_frames) : 0;"
        ]
        
        animate = [
            {
                "thirdperson_hand": "(v.main_hand||v.off_hand)&&!c.is_first_person"
            },
            {
                "firstperson_hand": "(v.main_hand||v.off_hand)&&c.is_first_person&&!v.frame"
            },
            {
                "firstperson_head": "(c.is_first_person||!c.is_first_person)&&v.head"
            },
            {
                "wield_first_person_pull_pos": "v.main_hand&&c.is_first_person&&v.frame"
            },
            {
                "wield_first_person_pull": "v.main_hand&&q.is_using_item&&q.main_hand_item_use_duration>0.0f&&c.is_first_person"
            }
        ]
        
        animations_dict = {
            "thirdperson_hand": "animation.campfire.thirdperson_hand",
            "firstperson_hand": "animation.campfire.firstperson_hand",
            "firstperson_head": "animation.campfire.disable",
            "wield_first_person_pull_pos": "animation.campfire.custom_bow.wield_first_person_pull_pos",
            "wield_first_person_pull": "animation.campfire.custom_bow.wield_first_person_pull"
        }
        
        with open(file, "w") as f:
            data = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": f"geyser_custom:{gmdl}",
                        "materials": {
                            "default": mdefault,
                            "enchanted": menchanted
                        },
                        "textures": {
                            "default": textures[0],
                            "bow_pulling_0": textures[1],
                            "bow_pulling_1": textures[2],
                            "bow_pulling_2": textures[3],
                            "enchanted": "textures/misc/enchanted_item_glint"
                        },
                        "geometry": {
                            "default": geometry[0],
                            "bow_pulling_0": geometry[1],
                            "bow_pulling_1": geometry[2],
                            "bow_pulling_2": geometry[3]
                        },
                        "animations": animations_dict,
                        "scripts": {
                            "initialize": initialize,
                            "pre_animation": pre_animation,
                            "animate": animate
                        },
                        "render_controllers": ["controller.render.bow_custom"]
                    }
                }
            }
            json.dump(data, f, separators=(',', ':'))

    @staticmethod
    def rendercontrollers():
        file = "staging/target/rp/render_controllers/bow_custom.render_controllers.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.10",
                "render_controllers": {
                    "controller.render.bow_custom": {
                        "arrays": {
                            "textures": {
                                "array.bow_texture_frames": [
                                    "texture.default",
                                    "texture.bow_pulling_0",
                                    "texture.bow_pulling_1",
                                    "texture.bow_pulling_2"
                                ]
                            },
                            "geometries": {
                                "array.bow_geo_frames": [
                                    "geometry.default",
                                    "geometry.bow_pulling_0",
                                    "geometry.bow_pulling_1",
                                    "geometry.bow_pulling_2"
                                ]
                            }
                        },
                        "geometry": "array.bow_geo_frames[math.floor(v.frame)]",
                        "materials": [ { "*": "variable.is_enchanted ? material.enchanted : material.default" } ],
                        "textures": [ "array.bow_texture_frames[math.floor(v.frame)]", "texture.enchanted" ]
                    }
                }
            }
            json.dump(data, f, separators=(',', ':'))

    @staticmethod
    def item_texture(gmdl, texture):
        with open("staging/target/rp/textures/item_texture.json", "r") as f:
            data = json.load(f)
        if gmdl in data["texture_data"]:
            with open("staging/target/rp/textures/item_texture.json", "w") as f:
                data["texture_data"][gmdl]["textures"] = texture
                json.dump(data, f, indent=2)
    
    @staticmethod
    def is2Dbow(file):
        with open(file, "r") as f:
            try:
                modelbone = json.load(f)["minecraft:geometry"][0]["bones"]
            except:
                modelbone = []
        if modelbone == [{"name":"campfire","binding":"c.item_slot == 'head' ? 'head' : q.item_slot_to_bone_name(c.item_slot)","pivot":[0,8,0]},{"name":"campfire_x","parent":"campfire","pivot":[0,8,0]},{"name":"campfire_y","parent":"campfire_x","pivot":[0,8,0]},{"name":"campfire_z","parent":"campfire_y","pivot":[0,8,0],"texture_meshes":[{"texture":"default","position":[0,8,0],"rotation":[90,0,-180],"local_pivot":[8,0.5,8]}]}]:
            return True
        else:
            return False

    @staticmethod
    def merge_bow_models():
        """Merge bow.json, bow_0.json, bow_1.json, bow_2.json into merge.json, then rename to bow.json"""
        import glob
        import os
        
        # Find all bow model directories ở nhiều cấp độ sâu
        bow_dirs = glob.glob("staging/target/rp/models/entity/*/", recursive=True)
        bow_dirs.extend(glob.glob("staging/target/rp/models/entity/*/*/", recursive=True))
        
        for bow_dir in bow_dirs:
            # Tìm tất cả file JSON trong thư mục
            all_json_files = glob.glob(os.path.join(bow_dir, '*.json'))
            
            # Lọc chỉ các file có tên chứa "bow" nhưng không chứa "crossbow"
            bow_files = []
            for json_file in all_json_files:
                filename = os.path.basename(json_file).lower()
                if 'bow' in filename and 'crossbow' not in filename:
                    bow_files.append(json_file)
            
            # Sắp xếp để đảm bảo thứ tự: bow.json, bow_0.json, bow_1.json, bow_2.json
            bow_files.sort(key=lambda x: (
                0 if os.path.basename(x) == 'bow.json' else
                1 if os.path.basename(x) == 'bow_0.json' else
                2 if os.path.basename(x) == 'bow_1.json' else
                3 if os.path.basename(x) == 'bow_2.json' else
                999
            ))
            
            # Check which bow files exist
            existing_files = [f for f in bow_files if os.path.exists(f)]
            
            if len(existing_files) >= 2:  # At least 2 bow files exist
                try:
                    merged_geometries = []
                    
                    # Load and merge all geometries
                    for bow_file in existing_files:
                        with open(bow_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'minecraft:geometry' in data:
                                geometries = data['minecraft:geometry']
                                if isinstance(geometries, list):
                                    merged_geometries.extend(geometries)
                    
                    if merged_geometries:
                        # Create merged data
                        merged_data = {
                            "format_version": "1.21.0",
                            "minecraft:geometry": merged_geometries
                        }
                        
                        # Step 1: Write to merge.json first
                        merge_file = os.path.join(bow_dir, 'merge.json')
                        with open(merge_file, 'w', encoding='utf-8') as f:
                            json.dump(merged_data, f, separators=(',', ':'))
                        
                        # Step 2: Remove all original bow files
                        for bow_file in existing_files:
                            if os.path.exists(bow_file):
                                os.remove(bow_file)
                        
                        # Step 3: Rename merge.json to bow.json
                        final_bow_file = os.path.join(bow_dir, 'bow.json')
                        os.rename(merge_file, final_bow_file)
                
                except Exception as e:
                    pass
            else:
                pass

    @staticmethod
    def acontroller(gmdllist):
        strlist = str(gmdllist)
        strlist = strlist.replace("[", "").replace("]", "")
        file = "staging/target/rp/animation_controllers/player.animation_controllers.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.10.0",
                "animation_controllers": {
                    "controller.animation.player.crossbow": {
                        "initial_state": "default",
                        "states": {
                            "charge": {
                                "animations": [
                                    "third_person_crossbow_equipped"
                                ],
                                "transitions": [
                                    {
                                        "default": "(q.get_equipped_item_name(0)!='crossbow'&&!q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_crossbow'))||(!q.is_using_item&&q.item_remaining_use_duration<=0.0&&!q.item_is_charged)"
                                    },
                                    {
                                        "hold": "q.item_is_charged"
                                    }
                                ]
                            },
                            "default": {
                                "transitions": [
                                    {
                                        "hold": "q.item_is_charged"
                                    },
                                    {
                                        "charge": "q.is_using_item&&q.item_remaining_use_duration>0.0&&!q.item_is_charged"
                                    }
                                ]
                            },
                            "hold": {
                                "animations": [
                                    "crossbow_hold"
                                ],
                                "transitions": [
                                    {
                                        "default": "(q.get_equipped_item_name(0)!='crossbow'&&!q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_crossbow'))||(!q.is_using_item&&q.item_remaining_use_duration<=0.0&&!q.item_is_charged)"
                                    },
                                    {
                                        "charge": "q.is_using_item&&q.item_remaining_use_duration>0.0&&!q.item_is_charged"
                                    }
                                ]
                            }
                        }
                    },
                    "controller.animation.player.first_person_map": {
                        "initial_state": "default",
                        "states": {
                            "default": {
                                "transitions": [
                                    {
                                        "one_hand": "q.get_equipped_item_name(1)=='filled_map'||(q.get_equipped_item_name(1)=='shield'||q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:custom_shield'))"
                                    },
                                    {
                                        "two_hand": "q.get_equipped_item_name(1)!='filled_map'&&(q.get_equipped_item_name(1)!='shield'&&!q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_shield'))"
                                    }
                                ]
                            },
                            "one_hand": {
                                "animations": [
                                    {
                                        "first_person_map_hold_main_hand": "q.get_equipped_item_name(0, 1)=='filled_map'"
                                    },
                                    {
                                        "first_person_map_hold_off_hand": "q.get_equipped_item_name(1)=='filled_map'&&((q.get_equipped_item_name(0)=='bow'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_bow')) ? !(variable.item_use_normalized>0&&variable.item_use_normalized<1.0) : 1.0)"
                                    }
                                ],
                                "transitions": [
                                    {
                                        "default": "q.get_equipped_item_name(0, 1)!='filled_map'&&q.get_equipped_item_name(1)!='filled_map'"
                                    },
                                    {
                                        "two_hand": "q.get_equipped_item_name(1)!='filled_map'&&(q.get_equipped_item_name(1)!='shield'&&!q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:custom_shield'))"
                                    }
                                ]
                            },
                            "two_hand": {
                                "animations": [
                                    "first_person_map_hold",
                                    "first_person_map_hold_attack"
                                ],
                                "transitions": [
                                    {
                                        "default": "q.get_equipped_item_name(0, 1)!='filled_map'&&q.get_equipped_item_name(1)!='filled_map'"
                                    },
                                    {
                                        "one_hand": "q.get_equipped_item_name(1)=='filled_map'||(q.get_equipped_item_name(1)=='shield'||q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:custom_shield'))"
                                    }
                                ]
                            }
                        }
                    },
                    "controller.animation.player.root": {
                        "initial_state": "first_person",
                        "states": {
                            "first_person": {
                                "animations": [
                                    {
                                        "first_person_swap_item": "!q.blocking"
                                    },
                                    {
                                        "first_person_shield_block": "q.blocking"
                                    },
                                    {
                                        "first_person_attack_controller": "variable.attack_time>0.0f&&q.get_equipped_item_name!='filled_map'"
                                    },
                                    "first_person_base_pose",
                                    {
                                        "first_person_empty_hand": "q.get_equipped_item_name(0, 1)!='filled_map'"
                                    },
                                    {
                                        "first_person_walk": "variable.bob_animation"
                                    },
                                    {
                                        "first_person_map_controller": "(q.get_equipped_item_name(0, 1)=='filled_map'||q.get_equipped_item_name(1)=='filled_map')"
                                    },
                                    {
                                        "first_person_crossbow_equipped": "(q.get_equipped_item_name(0)=='crossbow'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_crossbow'))&&(variable.item_use_normalized>0&&variable.item_use_normalized<1.0)"
                                    },
                                    {
                                        "first_person_breathing_bob": "variable.attack_time<=0.0"
                                    }
                                ],
                                "transitions": [
                                    {
                                        "paperdoll": "variable.is_paperdoll"
                                    },
                                    {
                                        "map_player": "variable.map_face_icon"
                                    },
                                    {
                                        "third_person": "!variable.is_first_person"
                                    }
                                ]
                            },
                            "map_player": {
                                "transitions": [
                                    {
                                        "paperdoll": "variable.is_paperdoll"
                                    },
                                    {
                                        "first_person": "variable.is_first_person"
                                    },
                                    {
                                        "third_person": "!variable.map_face_icon&&!variable.is_first_person"
                                    }
                                ]
                            },
                            "paperdoll": {
                                "animations": [
                                    "humanoid_base_pose",
                                    "look_at_target_ui",
                                    "move.arms",
                                    "move.legs",
                                    "cape"
                                ],
                                "transitions": [
                                    {
                                        "first_person": "!variable.is_paperdoll&&variable.is_first_person"
                                    },
                                    {
                                        "map_player": "variable.map_face_icon"
                                    },
                                    {
                                        "third_person": "!variable.is_paperdoll&&!variable.is_first_person"
                                    }
                                ]
                            },
                            "third_person": {
                                "animations": [
                                    "humanoid_base_pose",
                                    {
                                        "look_at_target": "!q.is_sleeping&&!q.is_emoting"
                                    },
                                    "move.arms",
                                    "move.legs",
                                    "cape",
                                    {
                                        "riding.arms": "q.is_riding"
                                    },
                                    {
                                        "riding.legs": "q.is_riding"
                                    },
                                    "holding",
                                    {
                                        "brandish_spear": "variable.is_brandishing_spear"
                                    },
                                    {
                                        "holding_spyglass": "variable.is_holding_spyglass"
                                    },
                                    {
                                        "charging": "q.is_charging"
                                    },
                                    {
                                        "sneaking": "q.is_sneaking&&!q.is_sleeping"
                                    },
                                    {
                                        "bob": "!variable.is_holding_spyglass&&!variable.is_tooting_goat_horn"
                                    },
                                    {
                                        "damage_nearby_mobs": "variable.damage_nearby_mobs"
                                    },
                                    {
                                        "swimming": "variable.swim_amount>0.0"
                                    },
                                    {
                                        "swimming.legs": "variable.swim_amount>0.0"
                                    },
                                    {
                                        "use_item_progress": "( variable.use_item_interval_progress>0.0 )||( variable.use_item_startup_progress>0.0 )&&!variable.is_brandishing_spear&&!variable.is_holding_spyglass&&!variable.is_tooting_goat_horn&&!q.is_item_name_any('slot.weapon.mainhand','minecraft:bow')&&!q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_bow')"
                                    },
                                    {
                                        "sleeping": "q.is_sleeping&&q.is_alive"
                                    },
                                    {
                                        "attack.positions": "variable.attack_time>=0.0"
                                    },
                                    {
                                        "attack.rotations": "variable.attack_time>=0.0"
                                    },
                                    {
                                        "shield_block_main_hand": "q.blocking&&(q.get_equipped_item_name(0)=='shield'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_shield'))"
                                    },
                                    {
                                        "shield_block_off_hand": "q.blocking&&(q.get_equipped_item_name(0)!='shield'&&!q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_shield'))&&(q.get_equipped_item_name(1)=='shield'||q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:custom_shield'))"
                                    },
                                    {
                                        "crossbow_controller": "q.get_equipped_item_name(0)=='crossbow'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_crossbow')"
                                    },
                                    {
                                        "third_person_bow_equipped": "(q.get_equipped_item_name(0)=='bow'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_bow'))&&(q.is_using_item)"
                                    },
                                    {
                                        "tooting_goat_horn": "variable.is_tooting_goat_horn"
                                    }
                                ],
                                "transitions": [
                                    {
                                        "paperdoll": "variable.is_paperdoll"
                                    },
                                    {
                                        "first_person": "variable.is_first_person"
                                    },
                                    {
                                        "map_player": "variable.map_face_icon"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
            json.dump(data, f, separators=(',', ':'))