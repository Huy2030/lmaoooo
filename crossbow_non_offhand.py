import os
import json
import glob
import shutil
import importlib.util
import sys
from crossbow2d import Crossbow2D_Util
from crossbow_util import Crossbow_Util


print()
print("🚀 Bắt đầu xử lý converter crossbow")
# Load crossbow_non_offhand_utils
spec = importlib.util.spec_from_file_location("crossbow_non_offhand_utils", "crossbow_non_offhand_utils.py")
crossbow_non_offhand_utils = importlib.util.module_from_spec(spec)
sys.modules["crossbow_non_offhand_utils"] = crossbow_non_offhand_utils
spec.loader.exec_module(crossbow_non_offhand_utils)

Crossbow_non_offhand_Util = crossbow_non_offhand_utils.Crossbow_non_offhand_Util

# Đọc conversion mode từ environment variable
conversion_mode = 'both'

# Tạo crossbow animation và render controller cho 2D crossbows
Crossbow2D_Util.create_crossbow_animation()
Crossbow2D_Util.create_crossbow_render_controller()

# Tạo render controllers
Crossbow_non_offhand_Util.rendercontrollers()

# Lấy tất cả các attachable files đã được tạo bởi converter.sh
attachable_files = glob.glob("staging/target/rp/attachables/**/*.json", recursive=True)

processed_3d_count = 0
skipped_count = 0
gmdllist = []
processed_crossbows = set()  # Tránh duplicate messages
displayed_messages = set()  # Tránh duplicate display messages

for attachable_file in attachable_files:
    try:
        # Chỉ xử lý crossbow attachables - kiểm tra tên file
        filename = os.path.basename(attachable_file).lower()
        if 'crossbow' not in filename:
            continue
            
        with open(attachable_file, "r") as f:
            attachable_data = json.load(f)
        
        # Lấy thông tin từ attachable
        identifier = attachable_data["minecraft:attachable"]["description"]["identifier"]
        materials = attachable_data["minecraft:attachable"]["description"]["materials"]
        textures = attachable_data["minecraft:attachable"]["description"]["textures"]
        geometry = attachable_data["minecraft:attachable"]["description"]["geometry"]
        animations = attachable_data["minecraft:attachable"]["description"]["animations"]
        
        # Tìm model gốc tương ứng
        relative_path = attachable_file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
        parts = relative_path.split("/")
        namespace = parts[0]
        model_path = "/".join(parts[1:-1]) if len(parts) > 2 else ""
        model_name = parts[-1].replace(".json", "")
        
        # Tạo base crossbow name (loại bỏ suffix _0, _1, _2, _charged)
        base_name = model_name
        for suffix in ["_0", "_1", "_2", "_charged"]:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        crossbow_key = f"{namespace}:{model_path}/{base_name}" if model_path else f"{namespace}:{base_name}"
        
        # Đường dẫn đến model gốc trong staging
        if model_path:
            source_model_file = f"staging/assets/{namespace}/models/{model_path}/{model_name}.json"
        else:
            source_model_file = f"staging/assets/{namespace}/models/{model_name}.json"
        
        # Đọc display từ model gốc
        display_data = {}
        if os.path.exists(source_model_file):
            with open(source_model_file, "r") as mf:
                model_json = json.load(mf)
                display_data = model_json.get("display", {})
        
        # Kiểm tra xem có phải 2D crossbow không
        model_files = glob.glob(f"staging/target/rp/models/entity/{namespace}/{model_path}/{model_name}.json" if model_path else f"staging/target/rp/models/entity/{namespace}/{model_name}.json")
        is2Dcrossbow = False
        if model_files and os.path.exists(model_files[0]):
            is2Dcrossbow = Crossbow_Util.is2Dcrossbow(model_files[0])
        
        # Bỏ qua 2D crossbows - sẽ được xử lý bởi Crossbow2D_Util.process_crossbow_2d()
        if is2Dcrossbow:
            continue
        
        # Sử dụng texture và geometry từ attachable gốc
        default_texture = textures.get("default", "textures/items/crossbow")
        crossbow_textures = [default_texture, default_texture, default_texture]
        default_geometry = geometry.get("default", "geometry.crossbow")
        crossbow_geometry = [default_geometry, default_geometry, default_geometry]
        
        # Cập nhật attachable với initialize section mới
        Crossbow_non_offhand_Util.update_attachable(
            attachable_file,
            identifier,
            materials,
            crossbow_textures,
            crossbow_geometry,
            animations,
            display_data
        )
        
        processed_3d_count += 1
        
        # Chỉ hiển thị message 1 lần cho mỗi crossbow base
        if crossbow_key not in processed_crossbows:
            processed_crossbows.add(crossbow_key)
            # Hiển thị đường dẫn attachable tương đối
            relative_attachable_path = attachable_file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
            
            # Loại bỏ các suffix để hiển thị tên gọn
            display_path = relative_attachable_path
            for suffix in ["_firework.json", "_charged.json", "_3.json", "_2.json", "_1.json", "_0.json"]:
                if display_path.endswith(suffix):
                    display_path = display_path[:-len(suffix)] + ".json"
                    break
            
            # Chỉ hiển thị nếu chưa được hiển thị trước đó
            if display_path not in displayed_messages:
                displayed_messages.add(display_path)
                print(f"✅ Xử lý crossbow 3D: {display_path}")
        
        # Thêm vào gmdllist để tạo animation controller
        gmdl = identifier.split(":")[-1]
        gmdllist.append(identifier)
        
    except Exception as e:
        skipped_count += 1
        relative_attachable_path = attachable_file.replace("staging/target/rp/attachables/", "").replace("\\", "/")
        display_path = relative_attachable_path.replace("_firework.json", ".json").replace("crossbow_2.json", "crossbow.json")
        # Chỉ hiển thị nếu chưa được hiển thị trước đó
        if display_path not in displayed_messages:
            displayed_messages.add(display_path)
            print(f"❌ Không xử lý được crossbow 3D: {display_path}")

# Post-processing
Crossbow_non_offhand_Util.merge_crossbow_models()
Crossbow_non_offhand_Util.cleanup_crossbow_variants()

# Xử lý 2D crossbows sau khi xử lý 3D crossbows
Crossbow2D_Util.process_crossbow_2d()

# Create animation controller
if gmdllist:
    Crossbow_non_offhand_Util.acontroller(gmdllist)