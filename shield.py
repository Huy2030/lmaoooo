import os
import json
import glob
from shield_util import Shield_Util
from item_utils import Item_Util

print()
print("🚀 Bắt đầu xử lý converter shield")
# Xử lý shield overrides
if os.path.exists("pack/assets/minecraft/models/item/shield.json"):
    with open("pack/assets/minecraft/models/item/shield.json") as f:
        data = json.load(f)
        predicate = [d["predicate"] for d in data["overrides"]]
        model = [d["model"] for d in data["overrides"]]
    
    for m, p in zip(model, predicate):
        if m == "item/shield" or "custom_model_data" not in p: 
            continue
        try:
            fpath = (f"cache/shield/{p['custom_model_data']}.json")
            if not os.path.exists(fpath):
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                with open(fpath, "w") as f:
                    f.write("{}")
            with open(fpath, "r") as f:
                cache_data = json.load(f)
            with open(fpath, "w") as f:
                if "blocking" not in p:
                    cache_data["default"] = m
                    cache_data["check"] = 1
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            pass

files = glob.glob("cache/shield/*.json")
Item_Util.animations()
gmdllist = []
displayed_messages = set()  # Tránh duplicate display messages

for file in files:
    fa = None
    try:
        with open(file, "r") as f:
            cache_data = json.load(f)
        
        if cache_data.get("check") == 1 and "default" in cache_data:
            namespace = cache_data["default"].split(":")[0]
            path = cache_data["default"].split(":")[1]
            
            # Tìm attachable file
            files = glob.glob(f"staging/target/rp/attachables/{namespace}/{path}*.json")
            fa = None
            for attachable_file in files:
                if f"{path.split('/')[-1]}." in attachable_file:
                    fa = attachable_file
                    break
            
            if not fa:
                continue
            
            # Đọc attachable data
            with open(fa, "r") as f:
                dataA = json.load(f)
            
            texture = dataA["minecraft:attachable"]["description"]["textures"]["default"]
            
            # Kiểm tra 2D shield
            model_file = glob.glob(f"staging/target/rp/models/entity/{namespace}/{path}.json")
            if not model_file:
                continue
                
            is_2d = Shield_Util.is2Dshield(model_file[0])
            
            if is_2d:
                geometry = "geometry.shield"
            else:
                geometry = dataA["minecraft:attachable"]["description"]["geometry"]["default"]
            
            # Đọc display data từ Java model
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
            
            # Chuẩn bị animation data
            animate = [
                {"thirdperson_hand": "(v.main_hand||v.off_hand)&&!c.is_first_person"},
                {"firstperson_hand": "(v.main_hand||v.off_hand)&&c.is_first_person"},
                {"firstperson_head": "c.is_first_person&&v.head"}
            ]
            
            pre_animation = [
                "v.main_hand = c.item_slot == 'main_hand';",
                "v.off_hand = c.item_slot == 'off_hand';",
                "v.head = c.item_slot == 'head';"
            ]
            
            # Lấy thông tin từ attachable hiện tại
            mdefault = dataA["minecraft:attachable"]["description"]["materials"]["default"]
            menchanted = dataA["minecraft:attachable"]["description"]["materials"]["enchanted"]
            gmdl = dataA["minecraft:attachable"]["description"]["identifier"].split(":")[1]
            animations = dataA["minecraft:attachable"]["description"]["animations"]
            
            # Cập nhật animations
            animations["thirdperson_hand"] = "animation.campfire.thirdperson_hand"
            animations["firstperson_hand"] = "animation.campfire.firstperson_hand"
            animations["firstperson_head"] = "animation.campfire.disable"
            
            gmdllist.append(f"geyser_custom:{gmdl}")
            Shield_Util.item_texture(gmdl, texture)
            
            # Ghi đè nội dung attachable file
            Shield_Util.write(fa, gmdl, [texture], [geometry], mdefault, menchanted, animations, animate, pre_animation, display_data)
            
            # Hiển thị đường dẫn attachable tương đối
            relative_attachable_path = fa.replace("staging/target/rp/attachables/", "").replace("\\", "/")
            if relative_attachable_path not in displayed_messages:
                displayed_messages.add(relative_attachable_path)
                print(f"✅ Xử lý shield: {relative_attachable_path}")
            
    except Exception as e:
        if fa and fa not in displayed_messages:
            relative_attachable_path = fa.replace("staging/target/rp/attachables/", "").replace("\\", "/")
            if relative_attachable_path not in displayed_messages:
                displayed_messages.add(relative_attachable_path)
                print(f"❌ Không xử lý được shield: {relative_attachable_path}")
        pass

print()
print()
Shield_Util.acontroller(gmdllist)
Shield_Util.animation_controller(gmdllist)
Shield_Util.shield_attachable(gmdllist)

if os.path.exists("staging/target"):
    Shield_Util.render_controller(gmdllist)
