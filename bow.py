import os
import json
import glob
from bow_util import Bow_Util
from item_utils import Item_Util
from bow2d import Bow2D_Util

print()
print("🚀 Bắt đầu xử lý converter bow")

# Create bow animation for 2D bows
Bow2D_Util.create_bow_animation()

if os.path.exists("pack/assets/minecraft/models/item/bow.json"):
    with open("pack/assets/minecraft/models/item/bow.json") as f:
        data = json.load(f)
        predicate = [d["predicate"] for d in data["overrides"]]
        model = [d["model"] for d in data["overrides"]]
    
    processed_models = set()  # Tránh xử lý trùng lặp
    
    for m, p in zip(model, predicate):
        if m in ["item/bow", "item/bow_pulling_0", "item/bow_pulling_1", "item/bow_pulling_2"] or not "custom_model_data" in p:
            continue
        
        # Tạo key unique cho model + custom_model_data
        model_key = f"{m}_{p['custom_model_data']}"
        if model_key in processed_models:
            continue
        
        processed_models.add(model_key)
        
        i = 0
        try:
            if p.get("pulling") == 1:
                # Nếu có pulling = 1 nhưng không có pull hoặc pull = 0 -> bow_0 (i=1)
                if "pull" not in p or p.get("pull") == 0:
                    i = 1
                elif p.get("pull") <= 0.65:
                    i = 2
                elif p.get("pull") > 0.65:
                    i = 3
        except:
            pass
        fpath = (f"cache/bow/{p['custom_model_data']}.json")
        if not os.path.exists(fpath):
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w") as f:
                f.write("{}")
        with open(fpath, "r") as f:
            data = json.load(f)
        with open(fpath, "w") as f:
            if "check" in data:
                data["check"] = data["check"] + 1
            else:
                data["check"] = 1
            data[f'texture_{i}'] = m
            json.dump(data, f, indent=2)

files = glob.glob("cache/bow/*.json")
Item_Util.animations()
Bow_Util.rendercontrollers()
gmdllist = []

for file in files:
    try:
        with open(file, "r") as f:
            data = json.load(f)
        if data["check"] == 4:
            textures = []
            geometry = []
            is2Dbow = False
            namespace = None
            
            for i in range(4):
                namespace = data[f"texture_{i}"].split(":")[0]
                path = data[f"texture_{i}"].split(":")[1]
                attachable_files = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
                
                fa = None
                for attachable_file in attachable_files:
                    if f"{path.split('/')[-1]}." in attachable_file:
                        fa = attachable_file
                        break
                
                if not fa or not os.path.exists(fa):
                    continue
                    
                with open(fa, "r") as f:
                    dataA = json.load(f)
                    f.close()
                    textures.append(dataA["minecraft:attachable"]["description"]["textures"]["default"])
                    is2Dbow =  Bow_Util.is2Dbow(glob.glob(f"staging/target/rp/models/entity/{namespace}/{path}.json")[0])
                    
                    if is2Dbow:
                        # Skip 2D bows - handled by Bow2D_Util.process_bow_2d()
                        continue
                    else: 
                        geometry.append(dataA["minecraft:attachable"]["description"]["geometry"]["default"])
                        
                    if i == 0:
                        java_model_path = f"pack/assets/{namespace}/models/{path}.json"
                        display_data = {}
                        if os.path.exists(java_model_path):
                            try:
                                with open(java_model_path, 'r', encoding='utf-8') as f:
                                    java_model = json.load(f)
                                    if 'display' in java_model:
                                        display_data = java_model['display']
                            except Exception as e:
                                pass
                        
                        animate = [
                            {
                                "thirdperson_hand": "(v.main_hand||v.off_hand)&&!c.is_first_person"
                            },
                            {
                                "firstperson_hand": "(v.main_hand||v.off_hand)&&c.is_first_person&&!v.frame"
                            },
                            {
                                "wield_first_person_pull_pos": "v.main_hand&&c.is_first_person&&v.frame"
                            },
                            {
                                "wield_first_person_pull": "v.main_hand&&q.is_using_item&&q.main_hand_item_use_duration>0.0f&&c.is_first_person"
                            }
                        ]
                        pre_animation = [
                            "v.main_hand = c.item_slot=='main_hand';",
                            "v.off_hand = c.item_slot=='off_hand';",
                            "v.charge_amount = math.clamp((q.main_hand_item_max_duration - (q.main_hand_item_use_duration - q.frame_alpha + 1.0)) / 10.0, 0.0, 1.0f);",
                            "v.total_frames = 3;",
                            "v.step = v.total_frames / 55;",
                            "v.frame = q.is_using_item ? math.clamp((v.frame ?? 0) + v.step, 1, v.total_frames) : 0;"
                        ]
                        mfile = fa
                        mdefault = dataA["minecraft:attachable"]["description"]["materials"]["default"]
                        menchanted = dataA["minecraft:attachable"]["description"]["materials"]["enchanted"]
                        gmdl = dataA["minecraft:attachable"]["description"]["identifier"].split(":")[1]
                        animations = dataA["minecraft:attachable"]["description"]["animations"]
                        
                        animations["thirdperson_hand"] = "animation.campfire.thirdperson_hand"
                        animations["firstperson_hand"] = "animation.campfire.firstperson_hand"
                        animations["wield_first_person_pull_pos"] = "animation.campfire.custom_bow.wield_first_person_pull_pos"
                        animations["wield_first_person_pull"] = "animation.campfire.custom_bow.wield_first_person_pull"
                        gmdllist.append(f"geyser_custom:{gmdl}")
                        Bow_Util.item_texture(gmdl, textures[0])
                    else:
                        os.remove(fa)
                        
            # Only process 3D bows
            if not is2Dbow:
                Bow_Util.write(mfile, gmdl, textures, geometry, mdefault, menchanted, animations, animate, pre_animation, display_data)
                relative_attachable_path = mfile.replace("staging/target/rp/attachables/", "").replace("\\", "/")
                print(f"✅ Xử lý bow 3D: {relative_attachable_path}")
            elif not is2Dbow:
                relative_attachable_path = mfile.replace("staging/target/rp/attachables/", "").replace("\\", "/")
                print(f"❌ Không xử lý được bow 3D: {relative_attachable_path}")
    except Exception as e:
        print(e)

# Process 2D bows after 3D bow processing
Bow2D_Util.process_bow_2d()

Bow_Util.merge_bow_models()
Bow_Util.acontroller(gmdllist)