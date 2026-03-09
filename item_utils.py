import json
import os

class Item_Util:
    @staticmethod
    def get_display_initialize(display_data):
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
        
        head_rot = get_value('head.rotation', [0, 0, 0])
        head_trans = get_value('head.translation', [0, 0, 0])
        head_scale = get_value('head.scale', [1, 1, 1])
        
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
            f"v.thirdperson_head_rot_x = {format_number(head_rot[0] if isinstance(head_rot, list) and len(head_rot) > 0 else 0)};",
            f"v.thirdperson_head_rot_y = {format_number(head_rot[1] if isinstance(head_rot, list) and len(head_rot) > 1 else 0)};",
            f"v.thirdperson_head_rot_z = {format_number(head_rot[2] if isinstance(head_rot, list) and len(head_rot) > 2 else 0)};",
            f"v.thirdperson_head_pos_x = {format_number(head_trans[0] if isinstance(head_trans, list) and len(head_trans) > 0 else 0)};",
            f"v.thirdperson_head_pos_y = {format_number(head_trans[1] if isinstance(head_trans, list) and len(head_trans) > 1 else 0)};",
            f"v.thirdperson_head_pos_z = {format_number(head_trans[2] if isinstance(head_trans, list) and len(head_trans) > 2 else 0)};",
            f"v.thirdperson_head_scale = {format_scale(head_scale)};"
        ]
    
    @staticmethod
    def animations():
        """Tạo file animations chung"""
        file = "staging/target/rp/animations/animations.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            data = {
                "format_version": "1.8.0",
                "animations": {
                    "animation.campfire.custom_bow.wield_first_person_pull": {
                        "bones": {
                            "campfire_x": {
                                "position": [
                                    0,
                                    " 0 + ( q.is_using_item&&q.main_hand_item_use_duration>0.0f ? math.sin( (q.life_time) * 1000.0 * 1.3) * 0.1 - math.sin(q.life_time * 45.0) * 0.5 : 0.0)",
                                    0
                                ]
                            }
                        },
                        "loop": True
                    },
                    "animation.campfire.custom_bow.wield_first_person_pull_pos": {
                        "bones": {
                            "campfire": {
                                "position": [-4.5, 19.5, -5.5],
                                "rotation": [135, 60, -15],
                                "scale": 1.4
                            },
                            "campfire_x": {
                                "position": [
                                    "-v.firstperson_pull_pos_x",
                                    "v.firstperson_pull_pos_y",
                                    "v.firstperson_pull_pos_z"
                                ],
                                "rotation": ["-v.firstperson_pull_rot_x", 0, 0],
                                "scale": "v.firstperson_pull_scale"
                            },
                            "campfire_y": {
                                "rotation": [0, "-v.firstperson_pull_rot_y", 0]
                            },
                            "campfire_z": {
                                "rotation": [0, 0, "v.firstperson_pull_rot_z"]
                            }
                        },
                        "loop": True
                    },
                    "animation.campfire.custom_crossbow.firstperson_main_hand_charged": {
                        "bones": {
                            "campfire": {
                                "position": [0, 22.5, -12.25],
                                "rotation": [65, 60, -71],
                                "scale": 1.4
                            },
                            "campfire_x": {
                                "position": [
                                    "-v.firstperson_charged_pos_x",
                                    "v.firstperson_charged_pos_y",
                                    "v.firstperson_charged_pos_z"
                                ],
                                "rotation": ["-v.firstperson_charged_rot_x", 0, 0],
                                "scale": "v.firstperson_charged_scale"
                            },
                            "campfire_y": {
                                "rotation": [0, "-v.firstperson_charged_rot_y", 0]
                            },
                            "campfire_z": {
                                "rotation": [0, 0, "v.firstperson_charged_rot_z"]
                            }
                        },
                        "loop": True
                    },
                    "animation.campfire.custom_crossbow.wield_first_person_pull_pos": {
                        "bones": {
                            "campfire": {
                                "position": [0, 22.5, -12.25],
                                "rotation": [65, 60, -71],
                                "scale": 1.4
                            },
                            "campfire_x": {
                                "position": [
                                    "-v.firstperson_pull_pos_x",
                                    "v.firstperson_pull_pos_y",
                                    "v.firstperson_pull_pos_z"
                                ],
                                "rotation": ["-v.firstperson_pull_rot_x", 0, 0],
                                "scale": "v.firstperson_pull_scale"
                            },
                            "campfire_y": {
                                "rotation": [0, "-v.firstperson_pull_rot_y", 0]
                            },
                            "campfire_z": {
                                "rotation": [0, 0, "v.firstperson_pull_rot_z"]
                            }
                        },
                        "loop": True
                    },
                    "animation.campfire.firstperson_hand": {
                        "bones": {
                            "campfire": {
                                "position": [
                                    "v.main_hand ? 0 : -18.5",
                                    "v.main_hand ? 15 : 18.3",
                                    "v.main_hand ? 2 : 15"
                                ],
                                "rotation": [
                                    "v.main_hand ? 90 : 180",
                                    "v.main_hand ? 60 : 0",
                                    "v.main_hand ? -40 : 180"
                                ],
                                "scale": "v.main_hand ? 1.4 : 1.2"
                            },
                            "campfire_x": {
                                "position": [
                                    "v.main_hand ? -v.firstperson_mainhand_pos_x : (v.firstperson_hand_same ? v.firstperson_mainhand_pos_x : v.firstperson_offhand_pos_x)",
                                    "v.main_hand ? v.firstperson_mainhand_pos_y : (v.firstperson_hand_same ? v.firstperson_mainhand_pos_y : v.firstperson_offhand_pos_y)",
                                    "v.main_hand ? v.firstperson_mainhand_pos_z : (v.firstperson_hand_same ? v.firstperson_mainhand_pos_z : v.firstperson_offhand_pos_z)"
                                ],
                                "rotation": [
                                    "v.main_hand ? -v.firstperson_mainhand_rot_x : (v.firstperson_hand_same ? -v.firstperson_mainhand_rot_x : -v.firstperson_offhand_rot_x)",
                                    0,
                                    0
                                ],
                                "scale": "v.main_hand ? v.firstperson_mainhand_scale : (v.firstperson_hand_same ? v.firstperson_mainhand_scale : v.firstperson_offhand_scale)"
                            },
                            "campfire_y": {
                                "rotation": [
                                    0,
                                    "v.main_hand ? -v.firstperson_mainhand_rot_y : (v.firstperson_hand_same ? v.firstperson_mainhand_rot_y : v.firstperson_offhand_rot_y)",
                                    0
                                ]
                            },
                            "campfire_z": {
                                "rotation": [
                                    0,
                                    0,
                                    "v.main_hand ? v.firstperson_mainhand_rot_z : (v.firstperson_hand_same ? -v.firstperson_mainhand_rot_z : -v.firstperson_offhand_rot_z)"
                                ]
                            }
                        },
                        "loop": True
                    },
                    "animation.campfire.firstperson_hand_blocking": {
                        "bones": {
                            "campfire": {
                                "position": [
                                    "v.main_hand ? 0 : -18.5",
                                    "v.main_hand ? 15 : 18.3",
                                    "v.main_hand ? 2 : 15"
                                ],
                                "rotation": [
                                    "v.main_hand ? 90 : 180",
                                    "v.main_hand ? 60 : 0",
                                    "v.main_hand ? -40 : 180"
                                ],
                                "scale": "v.main_hand ? 1.4 : 1.2"
                            },
                            "campfire_x": {
                                "position": [
                                    "v.main_hand ? -v.firstperson_blocking_pos_x : (!v.is_blocking_main_hand ? (v.firstperson_hand_same ? v.firstperson_blocking_pos_x : v.firstperson_offhand_blocking_pos_x) : (v.firstperson_hand_same ? v.firstperson_mainhand_pos_x : v.firstperson_offhand_pos_x))",
                                    "v.main_hand ? v.firstperson_blocking_pos_y : (!v.is_blocking_main_hand ? (v.firstperson_hand_same ? v.firstperson_blocking_pos_y : v.firstperson_offhand_blocking_pos_y) : (v.firstperson_hand_same ? v.firstperson_mainhand_pos_y : v.firstperson_offhand_pos_y))",
                                    "v.main_hand ? v.firstperson_blocking_pos_z : (!v.is_blocking_main_hand ? (v.firstperson_hand_same ? v.firstperson_blocking_pos_z : v.firstperson_offhand_blocking_pos_z) : (v.firstperson_hand_same ? v.firstperson_mainhand_pos_z : v.firstperson_offhand_pos_z))"
                                ],
                                "rotation": [
                                    "v.main_hand ? -v.firstperson_blocking_rot_x : (!v.is_blocking_main_hand ? (v.firstperson_hand_same ? -v.firstperson_blocking_rot_x : -v.firstperson_offhand_blocking_rot_x) : (v.firstperson_hand_same ? -v.firstperson_mainhand_rot_x : -v.firstperson_offhand_rot_x))",
                                    0,
                                    0
                                ],
                                "scale": "v.main_hand ? v.firstperson_blocking_scale : (!v.is_blocking_main_hand ? (v.firstperson_hand_same ? v.firstperson_blocking_scale : v.firstperson_offhand_blocking_scale) : (v.firstperson_hand_same ? v.firstperson_mainhand_scale : v.firstperson_offhand_scale))"
                            },
                            "campfire_y": {
                                "rotation": [
                                    0,
                                    "v.main_hand ? -v.firstperson_blocking_rot_y : (!v.is_blocking_main_hand ? (v.firstperson_hand_same ? v.firstperson_blocking_rot_y : v.firstperson_offhand_blocking_rot_y) : (v.firstperson_hand_same ? v.firstperson_mainhand_rot_y : v.firstperson_offhand_rot_y))",
                                    0
                                ]
                            },
                            "campfire_z": {
                                "rotation": [
                                    0,
                                    0,
                                    "v.main_hand ? v.firstperson_blocking_rot_z : (!v.is_blocking_main_hand ? (v.firstperson_hand_same ? -v.firstperson_blocking_rot_z : -v.firstperson_offhand_blocking_rot_z) : (v.firstperson_hand_same ? -v.firstperson_mainhand_rot_z : -v.firstperson_offhand_rot_z))"
                                ]
                            }
                        },
                        "loop": True
                    },
                    "animation.campfire.thirdperson_hand": {
                        "bones": {
                            "campfire": {
                                "position": [0, 13, -3],
                                "rotation": [90, 0, 0]
                            },
                            "campfire_x": {
                                "position": [
                                    "v.main_hand ? -v.thirdperson_mainhand_pos_x : (v.thirdperson_hand_same ? v.thirdperson_mainhand_pos_x : v.thirdperson_offhand_pos_x)",
                                    "v.main_hand ? v.thirdperson_mainhand_pos_y : (v.thirdperson_hand_same ? v.thirdperson_mainhand_pos_y : v.thirdperson_offhand_pos_y)",
                                    "v.main_hand ? v.thirdperson_mainhand_pos_z : (v.thirdperson_hand_same ? v.thirdperson_mainhand_pos_z : v.thirdperson_offhand_pos_z)"
                                ],
                                "rotation": [
                                    "v.main_hand ? -v.thirdperson_mainhand_rot_x : (v.thirdperson_hand_same ? -v.thirdperson_mainhand_rot_x : -v.thirdperson_offhand_rot_x)",
                                    0,
                                    0
                                ],
                                "scale": "v.main_hand ? v.thirdperson_mainhand_scale : (v.thirdperson_hand_same ? v.thirdperson_mainhand_scale : v.thirdperson_offhand_scale)"
                            },
                            "campfire_y": {
                                "rotation": [
                                    0,
                                    "v.main_hand ? -v.thirdperson_mainhand_rot_y : (v.thirdperson_hand_same ? v.thirdperson_mainhand_rot_y : v.thirdperson_offhand_rot_y)",
                                    0
                                ]
                            },
                            "campfire_z": {
                                "rotation": [
                                    0,
                                    0,
                                    "v.main_hand ? v.thirdperson_mainhand_rot_z : (v.thirdperson_hand_same ? -v.thirdperson_mainhand_rot_z : -v.thirdperson_offhand_rot_z)"
                                ]
                            }
                        },
                        "loop": True
                    },
                    "animation.campfire.thirdperson_hand_blocking": {
                        "bones": {
                            "campfire": {
                                "position": [0, 13, -3],
                                "rotation": [90, 0, 0]
                            },
                            "campfire_x": {
                                "position": [
                                    "v.main_hand ? -v.thirdperson_blocking_pos_x : (!v.is_blocking_main_hand ? (v.thirdperson_hand_same ? v.thirdperson_blocking_pos_x : v.thirdperson_offhand_blocking_pos_x) : (v.thirdperson_hand_same ? v.thirdperson_mainhand_pos_x : v.thirdperson_offhand_pos_x))",
                                    "v.main_hand ? v.thirdperson_blocking_pos_y : (!v.is_blocking_main_hand ? (v.thirdperson_hand_same ? v.thirdperson_blocking_pos_y : v.thirdperson_offhand_blocking_pos_y) : (v.thirdperson_hand_same ? v.thirdperson_mainhand_pos_y : v.thirdperson_offhand_pos_y))",
                                    "v.main_hand ? v.thirdperson_blocking_pos_z : (!v.is_blocking_main_hand ? v.thirdperson_blocking_pos_z : (v.thirdperson_hand_same ? v.thirdperson_mainhand_pos_z : v.thirdperson_offhand_pos_z))"
                                ],
                                "rotation": [
                                    "v.main_hand ? -v.thirdperson_blocking_rot_x : (!v.is_blocking_main_hand ? (v.thirdperson_hand_same ? -v.thirdperson_blocking_rot_x : -v.thirdperson_offhand_blocking_rot_x) : (v.thirdperson_hand_same ? -v.thirdperson_mainhand_rot_x : -v.thirdperson_offhand_rot_x))",
                                    0,
                                    0
                                ],
                                "scale": "v.main_hand ? v.thirdperson_blocking_scale : (!v.is_blocking_main_hand ? (v.thirdperson_hand_same ? v.thirdperson_blocking_scale : v.thirdperson_offhand_blocking_scale) : (v.thirdperson_hand_same ? v.thirdperson_mainhand_scale : v.thirdperson_offhand_scale))"
                            },
                            "campfire_y": {
                                "rotation": [
                                    0,
                                    "v.main_hand ? -v.thirdperson_blocking_rot_y : (!v.is_blocking_main_hand ? (v.thirdperson_hand_same ? v.thirdperson_blocking_rot_y : v.thirdperson_offhand_blocking_rot_y) : (v.thirdperson_hand_same ? v.thirdperson_mainhand_rot_y : v.thirdperson_offhand_rot_y))",
                                    0
                                ]
                            },
                            "campfire_z": {
                                "rotation": [
                                    0,
                                    0,
                                    "v.main_hand ? v.thirdperson_blocking_rot_z : (!v.is_blocking_main_hand ? (v.thirdperson_hand_same ? -v.thirdperson_blocking_rot_z : -v.thirdperson_offhand_blocking_rot_z) : (v.thirdperson_hand_same ? -v.thirdperson_mainhand_rot_z : -v.thirdperson_offhand_rot_z))"
                                ]
                            }
                        },
                        "loop": True
                    },
                    "animation.campfire.thirdperson_head": {
                        "bones": {
                            "campfire": {
                                "position": [0, 19.9, 0]
                            },
                            "campfire_x": {
                                "position": [
                                    "-v.thirdperson_head_pos_x*0.625",
                                    "v.thirdperson_head_pos_y*0.625",
                                    "v.thirdperson_head_pos_z*0.625"
                                ],
                                "rotation": ["-v.thirdperson_head_rot_x", 0, 0],
                                "scale": "(v.thirdperson_head_scale==1  ? 0.625 : v.thirdperson_head_scale*0.625)"
                            },
                            "campfire_y": {
                                "rotation": [0, "-v.thirdperson_head_rot_y", 0]
                            },
                            "campfire_z": {
                                "rotation": [0, 0, "v.thirdperson_head_rot_z"]
                            }
                        },
                        "loop": True
                    },
                    "animation.player.first_person.attack_rotation": {
                        "loop": True,
                        "bones": {
                            "rightarm": {
                                "position": [
                                    "math.sin(variable.attack_time * 180.0) * -12.0",
                                    "math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 200.0) * 8.0 - variable.attack_time * 10.0",
                                    "math.sin(variable.attack_time * 150.0) * 3.0"
                                ],
                                "rotation": [
                                    "math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 250.0) * -50.0",
                                    "math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 250.0) * 80.0",
                                    "math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 250.0) * -30.0"
                                ]
                            }
                        }
                    },
                    "animation.player.first_person.vr_attack_rotation": {
                        "loop": True,
                        "bones": {
                            "rightarm": {
                                "position": [
                                    "6.0 * math.sin(variable.attack_time * 130.0)",
                                    "(math.sin((1.0 - variable.attack_time) * (1.0 - variable.attack_time) * 190.0) - 0.7) * 9.0 + 5.0",
                                    "math.sin(variable.attack_time * 130.0) * 14.0"
                                ],
                                "rotation": [
                                    "32.0 * math.sin(variable.attack_time * -170.0 - 45.0) * 1.4",
                                    "15.0 * math.sin(variable.attack_time * 160.0)",
                                    "28.0 * math.sin(variable.attack_time * 190.0 + 25.0) * 1.3"
                                ]
                            }
                        }
                    }
                }
            }
            json.dump(data, f, indent=2)
    
    @staticmethod
    def update_attachable(file, identifier, materials, textures, geometry, animations, display_data=None):
        """Cập nhật attachable file"""
        if display_data is None:
            display_data = {}
        
        initialize = Item_Util.get_display_initialize(display_data)
        
        pre_animation = [
            "v.main_hand = c.item_slot=='main_hand';",
            "v.off_hand = c.item_slot=='off_hand';",
            "v.head = c.item_slot=='head';"
        ]
        
        animate = [
            {"thirdperson_hand": "(v.main_hand||v.off_hand)&&!c.is_first_person"},
            {"thirdperson_head": "v.head&&!c.is_first_person"},
            {"firstperson_hand": "(v.main_hand||v.off_hand)&&c.is_first_person"},
            {"firstperson_head": "c.is_first_person&&v.head"}
        ]
        
        animations_dict = {
            "thirdperson_hand": "animation.campfire.thirdperson_hand",
            "thirdperson_head": "animation.campfire.thirdperson_head",
            "firstperson_hand": "animation.campfire.firstperson_hand",
            "firstperson_head": "animation.campfire.disable"
        }
        
        with open(file, "w") as f:
            data = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": identifier,
                        "materials": materials,
                        "textures": textures,
                        "geometry": geometry,
                        "animations": animations_dict,
                        "scripts": {
                            "initialize": initialize,
                            "pre_animation": pre_animation,
                            "animate": animate
                        },
                        "render_controllers": ["controller.render.item_default"]
                    }
                }
            }
            json.dump(data, f, indent=2)
        return True
    
    @staticmethod
    def create_2d_animation_file():
        file = "staging/target/rp/animations/campfire_tool_custom.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        
        animation_data = {
            "format_version": "1.8.0",
            "animations": {
                "animation.player.tool_custom": {
                    "bones": {
                        "item": {
                            "position": [1.25, 21, -8],
                            "rotation": [180, 0, 180],
                            "scale": [0.8, 0.8, 0.8]
                        }
                    },
                    "loop": True
                },
                "animation.player.tool_custom.first_person": {
                    "bones": {
                        "item": {
                            "position": [
                                "v.main_hand ? -3 : -22",
                                "v.main_hand ? 20 : 30",
                                "v.main_hand ? -2 : 18"
                            ],
                            "rotation": [
                                "v.main_hand ? 30 : 110",
                                "v.main_hand ? -120 : 0",
                                "v.main_hand ? -60 : 0"
                            ]
                        }
                    },
                    "loop": True
                }
            }
        }
        
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(animation_data, f, indent=2)
    
    @staticmethod
    def create_2d_geometry_file():
        file = "staging/target/rp/models/entity/campfire_tool_custom.json"
        os.makedirs(os.path.dirname(file), exist_ok=True)
        
        geometry_data = {
            "format_version": "1.21.0",
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": "geometry.campfire.2d_gen",
                        "texture_width": 16,
                        "texture_height": 16,
                        "visible_bounds_width": 1,
                        "visible_bounds_height": 1,
                        "visible_bounds_offset": [0, 0, 0]
                    },
                    "bones": [
                        {
                            "name": "item",
                            "binding": "c.item_slot == 'head' ? 'head' : q.item_slot_to_bone_name(c.item_slot)",
                            "pivot": [0, 0, 0],
                            "texture_meshes": [
                                {
                                    "texture": "default",
                                    "position": [2, 1, -2],
                                    "local_pivot": [6, 0, 6],
                                    "rotation": [0, -135, 90]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(geometry_data, f, indent=2)
    
    
    @staticmethod
    def update_attachable_2d(file, identifier, materials, textures, geometry):
        pre_animation = [
            "v.main_hand = c.item_slot=='main_hand';",
            "v.off_hand = c.item_slot=='off_hand';",
            "v.head = c.item_slot == 'head';"
        ]
        
        animations_dict = {
            "thirdperson": "animation.player.tool_custom",
            "firstperson": "animation.player.tool_custom.first_person"
        }
        
        animate = [
            {"thirdperson": "!c.is_first_person"},
            {"firstperson": "c.is_first_person"}
        ]
        
        with open(file, "w") as f:
            data = {
                "format_version": "1.10.0",
                "minecraft:attachable": {
                    "description": {
                        "identifier": identifier,
                        "materials": materials,
                        "textures": textures,
                        "geometry": {"default": "geometry.campfire.2d_gen"},
                        "animations": animations_dict,
                        "scripts": {
                            "pre_animation": pre_animation,
                            "animate": animate
                        },
                        "render_controllers": ["controller.render.item_default"]
                    }
                }
            }
            json.dump(data, f, indent=2)
        return True
    
    @staticmethod
    def cleanup_2d_item_files():
        """Xóa file trùng tên trong models/entity và animations cho 2D items"""
        from pathlib import Path
        import shutil
        
        attachables_path = Path("staging/target/rp/attachables")
        processed_files = {}
        
        # Thu thập danh sách file 2D cần xóa
        for json_file in attachables_path.rglob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                geometry = data.get("minecraft:attachable", {}).get("description", {}).get("geometry", {})
                if geometry.get("default") == "geometry.campfire.2d_gen":
                    file_name = json_file.stem
                    relative_path = json_file.relative_to(attachables_path)
                    if len(relative_path.parts) > 1:
                        folder_path = relative_path.parts[0]
                        processed_files[file_name] = folder_path
            except:
                continue
        
        # Xóa file trùng tên
        removed_count = 0
        for file_name, folder_path in processed_files.items():
            for base_path in [f"staging/target/rp/models/entity/{folder_path}", f"staging/target/rp/animations/{folder_path}"]:
                folder = Path(base_path)
                if folder.exists():
                    for target_file in folder.rglob(f"{file_name}.json"):
                        target_file.unlink()
                        removed_count += 1
        
        return removed_count
