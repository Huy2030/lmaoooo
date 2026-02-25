import json
import os
import glob

class Shield_Util:
    @staticmethod
    def get_shield_blocking_display_data(namespace, model_path, model_name):
        """Lấy display data từ shield_blocking tương ứng với shield đang xử lý"""
        import glob
        import os
        
        try:
            # Đọc shield.json từ pack để tìm custom_model_data của shield hiện tại
            with open("pack/assets/minecraft/models/item/shield.json", 'r', encoding='utf-8') as f:
                shield_data = json.load(f)
            
            # Tìm custom_model_data của shield hiện tại
            current_cmd = None
            target_model = f"{namespace}:{model_path}/{model_name}" if model_path else f"{namespace}:{model_name}"
            
            for override in shield_data.get("overrides", []):
                predicate = override.get("predicate", {})
                model = override.get("model", "")
                
                if model == target_model and "custom_model_data" in predicate:
                    current_cmd = predicate["custom_model_data"]
                    break
            
            if not current_cmd:
                return None
            
            # Tìm shield_blocking có cùng custom_model_data
            for override in shield_data.get("overrides", []):
                predicate = override.get("predicate", {})
                model = override.get("model", "")
                
                if (predicate.get("custom_model_data") == current_cmd and 
                    predicate.get("blocking") == 1):
                    
                    if ":" in model:
                        ns, path = model.split(":", 1)
                        blocking_file = f"pack/assets/{ns}/models/{path}.json"
                        
                        if os.path.exists(blocking_file):
                            try:
                                with open(blocking_file, 'r', encoding='utf-8') as f:
                                    blocking_data = json.load(f)
                                
                                if 'display' in blocking_data:
                                    display = blocking_data['display']
                                    result = {}
                                    
                                    # Đọc firstperson_righthand cho firstperson_blocking
                                    if 'firstperson_righthand' in display:
                                        fp_rh = display['firstperson_righthand']
                                        result['firstperson_blocking'] = {
                                            'translation': fp_rh.get('translation', [0, 0, 0]),
                                            'rotation': fp_rh.get('rotation', [0, 0, 0]),
                                            'scale': fp_rh.get('scale', [1, 1, 1])
                                        }
                                    
                                    # Đọc firstperson_lefthand cho firstperson_offhand_blocking
                                    if 'firstperson_lefthand' in display:
                                        fp_lh = display['firstperson_lefthand']
                                        result['firstperson_offhand_blocking'] = {
                                            'translation': fp_lh.get('translation', [0, 0, 0]),
                                            'rotation': fp_lh.get('rotation', [0, 0, 0]),
                                            'scale': fp_lh.get('scale', [1, 1, 1])
                                        }
                                    
                                    # Nếu chỉ có firstperson_righthand, copy sang firstperson_offhand_blocking
                                    if 'firstperson_righthand' in display and 'firstperson_lefthand' not in display:
                                        fp_rh = display['firstperson_righthand']
                                        result['firstperson_offhand_blocking'] = {
                                            'translation': fp_rh.get('translation', [0, 0, 0]),
                                            'rotation': fp_rh.get('rotation', [0, 0, 0]),
                                            'scale': fp_rh.get('scale', [1, 1, 1])
                                        }
                                    
                                    if result:
                                        return result
                            except Exception as e:
                                continue
            
        except Exception as e:
            pass
        
        return None

    @staticmethod
    def get_display_initialize(display_data, namespace=None, model_path="", model_name="shield"):
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
        
        def format_scale(scale):
            if isinstance(scale, list) and len(scale) >= 1:
                return scale[0]
            return scale
        
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
        
        # Shield blocking display data
        def get_shield_blocking_display_data_fallback():
            import glob
            import os
            
            # Tìm file shield_blocking.json cụ thể
            shield_blocking_files = []
            for pattern in ['**/shield_blocking.json', '**/shield-blocking.json']:
                for search_root in ['pack/', 'assets/', './']:
                    found = glob.glob(f'{search_root}**/{pattern}', recursive=True)
                    shield_blocking_files.extend(found)
            
            for shield_file in shield_blocking_files:
                try:
                    with open(shield_file, 'r', encoding='utf-8') as f:
                        shield_data = json.load(f)
                        
                        if 'display' in shield_data:
                            display = shield_data['display']
                            blocking_data = {}
                            
                            # Đọc firstperson_righthand cho firstperson_blocking
                            if 'firstperson_righthand' in display:
                                fp_rh = display['firstperson_righthand']
                                blocking_data['firstperson_blocking'] = {
                                    'translation': fp_rh.get('translation', [0, 0, 0]),
                                    'rotation': fp_rh.get('rotation', [0, 0, 0]),
                                    'scale': fp_rh.get('scale', [1, 1, 1])
                                }
                            
                            # Đọc firstperson_lefthand cho firstperson_offhand_blocking
                            if 'firstperson_lefthand' in display:
                                fp_lh = display['firstperson_lefthand']
                                blocking_data['firstperson_offhand_blocking'] = {
                                    'translation': fp_lh.get('translation', [0, 0, 0]),
                                    'rotation': fp_lh.get('rotation', [0, 0, 0]),
                                    'scale': fp_lh.get('scale', [1, 1, 1])
                                }
                            
                            # Nếu chỉ có firstperson_righthand, copy sang cả firstperson_offhand_blocking
                            if 'firstperson_righthand' in display and 'firstperson_lefthand' not in display:
                                fp_rh = display['firstperson_righthand']
                                blocking_data['firstperson_offhand_blocking'] = {
                                    'translation': fp_rh.get('translation', [0, 0, 0]),
                                    'rotation': fp_rh.get('rotation', [0, 0, 0]),
                                    'scale': fp_rh.get('scale', [1, 1, 1])
                                }
                            
                            if blocking_data:
                                return blocking_data
                                
                except Exception as e:
                    continue
            
            # Default shield blocking values nếu không tìm thấy file
            return {
                'firstperson_blocking': {
                    'translation': [0, 0, 0],
                    'rotation': [0, 0, 0],
                    'scale': [1, 1, 1]
                },
                'firstperson_offhand_blocking': {
                    'translation': [0, 0, 0],
                    'rotation': [0, 0, 0],
                    'scale': [1, 1, 1]
                }
            }
        
        # Shield blocking display data - ưu tiên từ shield_blocking tương ứng
        shield_blocking_data = Shield_Util.get_shield_blocking_display_data(namespace, model_path, model_name)
        
        # Nếu không tìm thấy shield_blocking tương ứng, fallback về logic cũ
        if not shield_blocking_data:
            shield_blocking_data = get_shield_blocking_display_data_fallback()
        
        # Firstperson blocking data (từ firstperson_righthand của shield_blocking)
        fp_blocking_trans = shield_blocking_data.get('firstperson_blocking', {}).get('translation', [0, 0, 0])
        fp_blocking_rot = shield_blocking_data.get('firstperson_blocking', {}).get('rotation', [0, 0, 0])
        fp_blocking_scale = shield_blocking_data.get('firstperson_blocking', {}).get('scale', [1, 1, 1])
        
        # Firstperson offhand blocking data (từ firstperson_lefthand của shield_blocking)
        fp_offhand_blocking_trans = shield_blocking_data.get('firstperson_offhand_blocking', {}).get('translation', [0, 0, 0])
        fp_offhand_blocking_rot = shield_blocking_data.get('firstperson_offhand_blocking', {}).get('rotation', [0, 0, 0])
        fp_offhand_blocking_scale = shield_blocking_data.get('firstperson_offhand_blocking', {}).get('scale', [1, 1, 1])
        
        def format_number(num):
            if isinstance(num, (int, float)):
                if num == int(num):
                    return int(num)
            return num
        
        return [
            f"v.thirdperson_mainhand_rot_x = {format_number(tp_rh_rot[0] if isinstance(tp_rh_rot, list) and len(tp_rh_rot) > 0 else 0)};",
            f"v.thirdperson_mainhand_rot_y = {format_number(tp_rh_rot[1] if isinstance(tp_rh_rot, list) and len(tp_rh_rot) > 1 else 0)};",
            f"v.thirdperson_mainhand_rot_z = {format_number(tp_rh_rot[2] if isinstance(tp_rh_rot, list) and len(tp_rh_rot) > 2 else 0)};",
            f"v.thirdperson_mainhand_pos_x = {format_number(tp_rh_trans[0] if isinstance(tp_rh_trans, list) and len(tp_rh_trans) > 0 else 0)};",
            f"v.thirdperson_mainhand_pos_y = {format_number(tp_rh_trans[1] if isinstance(tp_rh_trans, list) and len(tp_rh_trans) > 1 else 0)};",
            f"v.thirdperson_mainhand_pos_z = {format_number(tp_rh_trans[2] if isinstance(tp_rh_trans, list) and len(tp_rh_trans) > 2 else 0)};",
            f"v.thirdperson_mainhand_scale = {json.dumps(format_scale(tp_rh_scale)) if isinstance(tp_rh_scale, list) else 1};",
            "v.thirdperson_hand_same = false;",
            f"v.thirdperson_offhand_rot_x = {format_number(tp_lh_rot[0] if isinstance(tp_lh_rot, list) and len(tp_lh_rot) > 0 else 0)};",
            f"v.thirdperson_offhand_rot_y = {format_number(tp_lh_rot[1] if isinstance(tp_lh_rot, list) and len(tp_lh_rot) > 1 else 0)};",
            f"v.thirdperson_offhand_rot_z = {format_number(tp_lh_rot[2] if isinstance(tp_lh_rot, list) and len(tp_lh_rot) > 2 else 0)};",
            f"v.thirdperson_offhand_pos_x = {format_number(tp_lh_trans[0] if isinstance(tp_lh_trans, list) and len(tp_lh_trans) > 0 else 0)};",
            f"v.thirdperson_offhand_pos_y = {format_number(tp_lh_trans[1] if isinstance(tp_lh_trans, list) and len(tp_lh_trans) > 1 else 0)};",
            f"v.thirdperson_offhand_pos_z = {format_number(tp_lh_trans[2] if isinstance(tp_lh_trans, list) and len(tp_lh_trans) > 2 else 0)};",
            f"v.thirdperson_offhand_scale = {json.dumps(format_scale(tp_lh_scale)) if isinstance(tp_lh_scale, list) else 1};",
            f"v.firstperson_mainhand_rot_x = {format_number(fp_rh_rot[0] if isinstance(fp_rh_rot, list) and len(fp_rh_rot) > 0 else 0)};",
            f"v.firstperson_mainhand_rot_y = {format_number(fp_rh_rot[1] if isinstance(fp_rh_rot, list) and len(fp_rh_rot) > 1 else 0)};",
            f"v.firstperson_mainhand_rot_z = {format_number(fp_rh_rot[2] if isinstance(fp_rh_rot, list) and len(fp_rh_rot) > 2 else 0)};",
            f"v.firstperson_mainhand_pos_x = {format_number(fp_rh_trans[0] if isinstance(fp_rh_trans, list) and len(fp_rh_trans) > 0 else 0)};",
            f"v.firstperson_mainhand_pos_y = {format_number(fp_rh_trans[1] if isinstance(fp_rh_trans, list) and len(fp_rh_trans) > 1 else 0)};",
            f"v.firstperson_mainhand_pos_z = {format_number(fp_rh_trans[2] if isinstance(fp_rh_trans, list) and len(fp_rh_trans) > 2 else 0)};",
            f"v.firstperson_mainhand_scale = {json.dumps(format_scale(fp_rh_scale)) if isinstance(fp_rh_scale, list) else 1};",
            "v.firstperson_hand_same = false;",
            f"v.firstperson_offhand_rot_x = {format_number(fp_lh_rot[0] if isinstance(fp_lh_rot, list) and len(fp_lh_rot) > 0 else 0)};",
            f"v.firstperson_offhand_rot_y = {format_number(fp_lh_rot[1] if isinstance(fp_lh_rot, list) and len(fp_lh_rot) > 1 else 0)};",
            f"v.firstperson_offhand_rot_z = {format_number(fp_lh_rot[2] if isinstance(fp_lh_rot, list) and len(fp_lh_rot) > 2 else 0)};",
            f"v.firstperson_offhand_pos_x = {format_number(fp_lh_trans[0] if isinstance(fp_lh_trans, list) and len(fp_lh_trans) > 0 else 0)};",
            f"v.firstperson_offhand_pos_y = {format_number(fp_lh_trans[1] if isinstance(fp_lh_trans, list) and len(fp_lh_trans) > 1 else 0)};",
            f"v.firstperson_offhand_pos_z = {format_number(fp_lh_trans[2] if isinstance(fp_lh_trans, list) and len(fp_lh_trans) > 2 else 0)};",
            f"v.firstperson_offhand_scale = {json.dumps(format_scale(fp_lh_scale)) if isinstance(fp_lh_scale, list) else 1};",
            f"v.firstperson_blocking_rot_x = {format_number(fp_blocking_rot[0])};",
            f"v.firstperson_blocking_rot_y = {format_number(fp_blocking_rot[1])};",
            f"v.firstperson_blocking_rot_z = {format_number(fp_blocking_rot[2])};",
            f"v.firstperson_blocking_pos_x = {format_number(fp_blocking_trans[0])};",
            f"v.firstperson_blocking_pos_y = {format_number(fp_blocking_trans[1])};",
            f"v.firstperson_blocking_pos_z = {format_number(fp_blocking_trans[2])};",
            f"v.firstperson_blocking_scale = {json.dumps(format_scale(fp_blocking_scale))};",
            f"v.firstperson_offhand_blocking_rot_x = {format_number(fp_offhand_blocking_rot[0])};",
            f"v.firstperson_offhand_blocking_rot_y = {format_number(fp_offhand_blocking_rot[1])};",
            f"v.firstperson_offhand_blocking_rot_z = {format_number(fp_offhand_blocking_rot[2])};",
            f"v.firstperson_offhand_blocking_pos_x = {format_number(fp_offhand_blocking_trans[0])};",
            f"v.firstperson_offhand_blocking_pos_y = {format_number(fp_offhand_blocking_trans[1])};",
            f"v.firstperson_offhand_blocking_pos_z = {format_number(fp_offhand_blocking_trans[2])};",
            f"v.firstperson_offhand_blocking_scale = {json.dumps(format_scale(fp_offhand_blocking_scale))};"
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
        model_name = parts[-1].replace(".json", "") if len(parts) > 0 else "shield"
        
        initialize = Shield_Util.get_display_initialize(display_data, namespace, model_path, model_name)
        
        pre_animation = [
            "v.main_hand = c.item_slot == 'main_hand';",
            "v.off_hand = c.item_slot == 'off_hand';",
            "v.head = c.item_slot == 'head';",
            "v.is_blocking_main_hand = (q.get_equipped_item_name(0)=='shield'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_shield'));"
        ]
        
        animate = [
            {"thirdperson_hand": "(v.main_hand||v.off_hand)&&!c.is_first_person"},
            {"firstperson_hand": "(v.main_hand||v.off_hand)&&c.is_first_person&&!q.blocking"},
            {"firstperson_head": "(c.is_first_person||!c.is_first_person)&&v.head||(v.off_hand&&c.is_first_person&&(q.get_equipped_item_name(0)=='bow'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_bow'))&&q.is_using_item&&q.main_hand_item_use_duration>0.0f)"},
            {"firstperson_hand_blocking": "(v.main_hand||v.off_hand)&&c.is_first_person&&q.blocking"}
        ]
        
        animations_dict = {
            "thirdperson_hand": "animation.campfire.thirdperson_hand",
            "firstperson_hand": "animation.campfire.firstperson_hand",
            "firstperson_head": "animation.campfire.disable",
            "firstperson_hand_blocking": "animation.campfire.firstperson_hand_blocking"
        }
        
        with open(file, "w") as f:
            data = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": f"geyser_custom:{gmdl}",
                        "materials": {
                            "default": f"{mdefault}",
                            "enchanted": f"{menchanted}"
                        },
                        "textures": {
                            "default": f"{textures[0]}",
                            "enchanted": "textures/misc/enchanted_item_glint"
                        },
                        "geometry": {
                            "default": f"{geometry[0]}"
                        },
                        "animations": animations_dict,
                        "scripts": {
                            "initialize": initialize,
                            "pre_animation": pre_animation,
                            "animate": animate,
                        },
                        "render_controllers": ["controller.render.custom_shield"]
                    }
                }
            }
            json.dump(data, f, indent=2)
    


    @staticmethod
    def is2Dshield(file):
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
    def item_texture(gmdl, texture):
        with open("staging/target/rp/textures/item_texture.json", "r") as f:
            data = json.load(f)
        if gmdl in data["texture_data"]:
            with open("staging/target/rp/textures/item_texture.json", "w") as f:
                data["texture_data"][gmdl]["textures"] = texture
                json.dump(data,f, indent=4)
    
    @staticmethod
    def acontroller(gmdllist):
        strlist = str(gmdllist)
        strlist = strlist.replace("[", "").replace("]", "")
        file = "staging/target/rp/animations/player.animation.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.8",
                "animations": {
                    "animation.player.shield_block_main_hand": {
                        "bones": {
                            "rightarm": {
                                "rotation": [-20, -30, -25]
                            },
                            "rightitem": {
                                "position": [
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_thirdperson_shield_block_anim') ? 0 : -1",
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_thirdperson_shield_block_anim') ? 0 : -3",
                                    0
                                ],
                                "rotation": [
                                    0,
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_thirdperson_shield_block_anim') ? 5 : -60",
                                    "q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:remove_thirdperson_shield_block_anim') ? 35 : -45"
                                ]
                            }
                        },
                        "loop": True
                    },
                    "animation.player.shield_block_off_hand": {
                        "bones": {
                            "leftarm": {
                                "rotation": [-20, 20, 20]
                            },
                            "leftitem": {
                                "position": [
                                    "q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:remove_thirdperson_shield_block_anim') ? 0 : 1 + query.item_is_charged * 1.5",
                                    "q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:remove_thirdperson_shield_block_anim') ? 1 : -3 + query.item_is_charged",
                                    0
                                ],
                                "rotation": [
                                    "q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:remove_thirdperson_shield_block_anim') ? 0 : query.item_is_charged * 30",
                                    "q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:remove_thirdperson_shield_block_anim') ? 5 : 70 - query.item_is_charged * 60",
                                    "q.equipped_item_any_tag('slot.weapon.offhand','geyser_custom:remove_thirdperson_shield_block_anim') ? -25 : 65 - query.item_is_charged * 15"
                                ]
                            }
                        },
                        "loop": True
                    }
                }
            }
            json.dump(data, f, separators=(',', ':'))
    
    @staticmethod
    def animation_controller(gmdllist):
        strlist = str(gmdllist)
        strlist = strlist.replace("[", "").replace("]", "")
        file = "staging/target/rp/animation_controllers/shield.animation_controllers.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.10.0",
                "animation_controllers": {
                    "controller.animation.shield.wield": {
                        "initial_state": "default",
                        "states": {
                            "blocking": {
                                "animations": [
                                    {"wield_main_hand_first_person": "!variable.is_blocking_main_hand&&c.item_slot=='main_hand'"},
                                    {"wield_off_hand_first_person": "variable.is_blocking_main_hand&&c.item_slot=='off_hand'"},
                                    {"wield_main_hand_first_person_block": "variable.is_blocking_main_hand&&c.item_slot=='main_hand'"},
                                    {"wield_off_hand_first_person_block": "variable.is_blocking_off_hand&&c.item_slot=='off_hand'&&c.item_slot!='main_hand'"}
                                ],
                                "transitions": [
                                    {"default": "!q.blocking"},
                                    {"third_person": "!c.is_first_person"}
                                ]
                            },
                            "default": {
                                "animations": [
                                    {"wield_main_hand_first_person": "c.item_slot=='main_hand'"},
                                    {"wield_off_hand_first_person": "c.item_slot!='main_hand'"}
                                ],
                                "transitions": [
                                    {"blocking": "q.blocking"},
                                    {"third_person": "!c.is_first_person"}
                                ]
                            },
                            "third_person": {
                                "animations": ["wield_third_person"],
                                "transitions": [
                                    {"default": "c.is_first_person"}
                                ]
                            }
                        }
                    }
                }
            }
            json.dump(data, f, separators=(',', ':'))

    @staticmethod
    def render_controller(gmdllist):
        strlist = str(gmdllist)
        strlist = strlist.replace("[", "").replace("]", "")
        file = "staging/target/rp/render_controllers/shield_custom.render_controllers.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.10",
                "render_controllers": {
                    "controller.render.custom_shield": {
                        "arrays": {
                            "textures": {
                                "array.shield_texture_frames": [
                                    "texture.default"
                                ]
                            },
                            "geometries": {
                                "array.shield_geo_frames": [
                                    "geometry.default"
                                ]
                            }
                        },
                        "geometry": "array.shield_geo_frames[0]",
                        "materials": [
                            {"*": "variable.is_enchanted ? material.enchanted : material.default"}
                        ],
                        "textures": [
                            "array.shield_texture_frames[0]",
                            "texture.enchanted"
                        ]
                    }
                }
            }
            json.dump(data, f, separators=(',', ':'))

    @staticmethod
    def shield_attachable(gmdllist):
        strlist = str(gmdllist)
        strlist = strlist.replace("[", "").replace("]", "")
        file = "staging/target/rp/attachables/shield.entity.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": "minecraft:shield",
                        "materials": {
                            "default": "entity_alphatest",
                            "enchanted": "entity_alphatest_glint"
                        },
                        "textures": {
                            "default": "textures/entity/shield",
                            "enchanted": "textures/misc/enchanted_item_glint"
                        },
                        "geometry": {
                            "default": "geometry.shield"
                        },
                        "animations": {
                            "wield": "controller.animation.shield.wield",
                            "wield_first_person_block": "animation.shield.wield_first_person_blocking",
                            "wield_main_hand_first_person": "animation.shield.wield_main_hand_first_person",
                            "wield_main_hand_first_person_block": "animation.shield.wield_main_hand_first_person_blocking",
                            "wield_off_hand_first_person": "animation.shield.wield_off_hand_first_person",
                            "wield_off_hand_first_person_block": "animation.shield.wield_off_hand_first_person_blocking",
                            "wield_third_person": "animation.shield.wield_third_person"
                        },
                        "scripts": {
                            "initialize": [
                                "variable.main_hand_first_person_pos_x =  5.3;",
                                "variable.main_hand_first_person_pos_y = 26.0;",
                                "variable.main_hand_first_person_pos_z = 0.4;",
                                "variable.main_hand_first_person_rot_x = 91.0;",
                                "variable.main_hand_first_person_rot_y = 65.0;",
                                "variable.main_hand_first_person_rot_z = -43.0;",
                                "variable.off_hand_first_person_pos_x = -13.5;",
                                "variable.off_hand_first_person_pos_y = -5.8;",
                                "variable.off_hand_first_person_pos_z = 5.1;",
                                "variable.off_hand_first_person_with_bow_pos_z = -25.0;",
                                "variable.off_hand_first_person_rot_x = 1.0;",
                                "variable.off_hand_first_person_rot_y = 176.0;",
                                "variable.off_hand_first_person_rot_z = -2.5;"
                            ],
                            "pre_animation": [
                                "variable.is_blocking_main_hand = q.blocking&&(q.get_equipped_item_name(0)=='shield'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_shield'));",
                                "variable.is_blocking_off_hand = q.blocking&&q.get_equipped_item_name(0)!='shield'&&!q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_shield');",
                                "variable.is_using_bow = (q.get_equipped_item_name(0)=='bow'||q.equipped_item_any_tag('slot.weapon.mainhand','geyser_custom:custom_bow'))&&(q.main_hand_item_use_duration>0.0f);"
                            ],
                            "animate": ["wield"]
                        },
                        "render_controllers": ["controller.render.item_default"]
                    }
                }
            }
            json.dump(data, f, separators=(',', ':'))