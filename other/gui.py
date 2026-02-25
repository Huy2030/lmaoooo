
import json
import os
from pathlib import Path
from PIL import Image
import shutil
import random
import string

def random_name(length=50):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

used_names = set()
gui_mappings = []
processed_guis = set()  # Track đã xử lý

def get_unique_name():
    while True:
        name = random_name()
        if name not in used_names:
            used_names.add(name)
            return name

def center_and_align_bottom(image_path, bottom_margin=0):
    try:
        img = Image.open(image_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        width, height = img.size
        pixels = img.load()
        
        # Tìm bounding box của nội dung (pixel không trong suốt)
        min_x, min_y = width, height
        max_x, max_y = 0, 0
        
        for y in range(height):
            for x in range(width):
                if pixels[x, y][3] > 0:  # Alpha > 0
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        
        # Nếu không có nội dung, bỏ qua
        if max_x == 0 and max_y == 0:
            return False
        
        # Kích thước nội dung
        content_width = max_x - min_x + 1
        content_height = max_y - min_y + 1
        
        # Crop nội dung
        content = img.crop((min_x, min_y, max_x + 1, max_y + 1))
        
        # Tạo canvas 256x256 trong suốt
        canvas = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        
        # Tính vị trí mới: căn giữa theo chiều ngang, sát viền trên (cộng margin)
        new_x = (256 - content_width) // 2
        new_y = bottom_margin  # Đẩy lên trên, cách viền top = bottom_margin
        
        # Paste nội dung vào canvas
        canvas.paste(content, (new_x, new_y))
        
        # Lưu lại
        canvas.save(image_path)
        return True
        
    except Exception as e:
        return False

def find_image(base_path, namespace, relative_path):
    # Tìm theo namespace: ./pack/assets/{namespace}/{relative_path}
    full_path = base_path.parent / namespace / relative_path
    if full_path.exists():
        return str(full_path)
    
    # Fallback: tìm theo tên file
    image_name = os.path.basename(relative_path)
    for root, dirs, files in os.walk(base_path.parent):
        if image_name in files:
            return os.path.join(root, image_name)
    return None

def count_non_transparent_pixels(image_path):
    # Đếm số pixel không trong suốt (alpha > 0)
    try:
        img = Image.open(image_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Sử dụng img.load() thay vì getdata() để tránh DeprecationWarning
        width, height = img.size
        pixels = img.load()
        count = 0
        for y in range(height):
            for x in range(width):
                if pixels[x, y][3] > 0:  # Alpha > 0
                    count += 1
        return count
    except:
        return 0

def normalize_image_to_256(image_path, output_path):
    # Resize ảnh về 256x256 nếu cần, căn giữa và đẩy lên trên
    try:
        img = Image.open(image_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        width, height = img.size
        
        # Nếu ảnh đã là 256x256, chỉ cần copy
        if width == 256 and height == 256:
            img.save(output_path)
            return (width, height, 0, 0, 0, 0)
        
        # Tạo canvas 256x256 trong suốt
        canvas = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        
        # Tính vị trí để căn giữa theo chiều ngang, sát viền trên
        paste_x = (256 - width) // 2
        paste_y = 0  # Sát viền trên
        
        # Paste ảnh gốc vào canvas
        canvas.paste(img, (paste_x, paste_y))
        canvas.save(output_path)
        
        return (256, 256, 0, 0, 0, 0)
        
    except Exception as e:
        return (0, 0, 0, 0, 0, 0)

def calculate_offset(width, height, ascent):
    # Tất cả GUI đều có offset_y = 0 (sát viền trên canvas 256x256)
    offset_x = 0
    offset_y = 0
    
    return [offset_x, offset_y]

def process_fonts():
    campfire_path = Path("./pack/campfire.json")
    assets_path = Path("./pack/assets")
    output_dir = Path("staging/target/rp/textures/gui")
    
    if not campfire_path.exists():
        return
    
    # Đọc campfire.json để lấy danh sách font cần xử lý
    try:
        with open(campfire_path, 'r', encoding='utf-8') as f:
            campfire_data = json.load(f)
    except:
        return
    
    fonts_to_process = campfire_data.get("fonts", {})
    if not fonts_to_process:
        return
    
    # Tạo map: font_char -> texture_path
    font_texture_map = {}
    
    # Quét tất cả JSON trong assets để tìm font và texture path
    for json_file in assets_path.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for provider in data.get("providers", []):
                if provider.get("type") == "bitmap":
                    file_path = provider.get("file", "")
                    chars = provider.get("chars") or provider.get("symbols", [])
                    
                    if chars:
                        for char_item in (chars if isinstance(chars, list) else [chars]):
                            # Check xem char này có trong campfire.json không
                            if char_item in fonts_to_process:
                                font_texture_map[char_item] = file_path
        except:
            pass
    
    # Xử lý các font đã tìm được
    total_found = len(font_texture_map)
    total_processed = 0
    total_not_found = 0
    total_duplicate = 0
    
    for unicode_char, file_path in font_texture_map.items():
        gui_key = file_path
        
        if gui_key in processed_guis:
            total_duplicate += 1
            continue
        
        processed_guis.add(gui_key)
        
        # Tìm file texture
        full_path = None
        if ":" in file_path:
            namespace, path = file_path.split(":", 1)
            # Thử với /textures/
            full_path = assets_path / namespace / "textures" / f"{path}.png"
            if not full_path.exists():
                full_path = assets_path / namespace / f"{path}.png"
            if not full_path.exists():
                # Thử không có .png
                full_path = assets_path / namespace / "textures" / path
                if not full_path.exists():
                    full_path = assets_path / namespace / path
        else:
            # Không có namespace, mặc định minecraft
            full_path = assets_path / "minecraft" / "textures" / f"{file_path}.png"
            if not full_path.exists():
                full_path = assets_path / "minecraft" / f"{file_path}.png"
            if not full_path.exists():
                full_path = assets_path / "minecraft" / "textures" / file_path
                if not full_path.exists():
                    full_path = assets_path / "minecraft" / file_path
        
        if not full_path or not full_path.exists():
            total_not_found += 1
            continue
        
        try:
            img = Image.open(full_path)
            width, height = img.size
            
            folder1, folder2 = get_unique_name(), get_unique_name()
            img_name = get_unique_name() + ".png"
            gui_name = get_unique_name()
            
            dest_path = output_dir / folder1 / folder2
            dest_path.mkdir(parents=True, exist_ok=True)
            
            final_img_path = dest_path / img_name
            norm_width, norm_height, orig_x, orig_y, center_x, center_y = normalize_image_to_256(str(full_path), final_img_path)
            
            if norm_width == 0:
                norm_width, norm_height = width, height
            
            center_and_align_bottom(final_img_path, bottom_margin=0)
            
            gui_mappings.append({
                "char": unicode_char,
                "texture": f"textures/gui/{folder1}/{folder2}/{img_name[:-4]}",
                "name": gui_name,
                "width": 256,
                "height": 256,
                "offset": [0, 0]
            })
            total_processed += 1
        except Exception as e:
            pass
    
    create_chest_screen()

def create_chest_screen():
    chest_file = Path("staging/target/rp/ui/chest_screen.json")
    chest_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Tạo chest_label visible
    visible_chars = " - ".join([f"'{m['char']}'" for m in gui_mappings])
    chest_label_visible = f"(($container_title - {visible_chars}) = $container_title)" if visible_chars else "(($container_title) = $container_title)"
    
    data = {"namespace": "chest", "chest_label": {"type": "label", "text": "$container_title", "color": "$title_text_color", "layer": 5, "visible": chest_label_visible}}
    
    # Thêm GUI entries
    small_controls = [
        {"container_gamepad_helpers@common.container_gamepad_helpers": {}},
        {"flying_item_renderer@common.flying_item_renderer": {"layer": 14}},
        {"selected_item_details_factory@common.selected_item_details_factory": {}},
        {"item_lock_notification_factory@common.item_lock_notification_factory": {}}
    ]
    
    large_controls = [
        {"container_gamepad_helpers@common.container_gamepad_helpers": {}},
        {"flying_item_renderer@common.flying_item_renderer": {"layer": 11}},
        {"selected_item_details_factory@common.selected_item_details_factory": {"control_name": "@chest.selected_item_details"}},
        {"item_lock_notification_factory@common.item_lock_notification_factory": {"control_name": "@common.item_lock_notification"}}
    ]
    
    for m in gui_mappings:
        data[m["name"]] = {
            "type": "image", "texture": m["texture"], "offset": m["offset"], "size": [m["width"], m["height"]],
            "layer": 13, "fill": False, "$menu_name": "$container_title",
            "visible": f"(not (($menu_name - '{m['char']}') = $menu_name))"
        }
        small_controls.append({f"{m['name']}@{m['name']}": {}})
        large_controls.append({f"{m['name']}@{m['name']}": {}})
    
    # Thêm các panel
    data.update({
        "small_chest_panel_top_half": {"type": "panel", "size": ["100%", "50%"], "offset": [0, 12], "anchor_to": "top_left", "anchor_from": "top_left", "controls": [{"chest_label@chest.chest_label": {}}, {"small_chest_grid@chest.small_chest_grid": {"offset": [7, 9]}}]},
        "large_chest_panel_top_half": {"type": "panel", "size": ["100%", 132], "offset": [0, 11], "anchor_to": "top_left", "anchor_from": "top_left", "controls": [{"chest_label@chest.chest_label": {}}, {"large_chest_grid@chest.large_chest_grid": {"offset": [7, 10]}}]},
        "small_chest_panel": {"type": "panel", "controls": small_controls + [{"root_panel@common.root_panel": {"layer": 1, "controls": [{"common_panel@common.common_panel": {}}, {"chest_panel": {"type": "panel", "layer": 5, "controls": [{"small_chest_panel_top_half@chest.small_chest_panel_top_half": {}}, {"inventory_panel_bottom_half_with_label@common.inventory_panel_bottom_half_with_label": {}}, {"hotbar_grid@common.hotbar_grid_template": {}}, {"inventory_take_progress_icon_button@common.inventory_take_progress_icon_button": {}}]}}, {"inventory_selected_icon_button@common.inventory_selected_icon_button": {}}, {"gamepad_cursor@common.gamepad_cursor_button": {}}]}}]},
        "selected_item_details@common.selected_item_details": {"offset": [0, 0]},
        "large_chest_panel": {"type": "panel", "controls": large_controls + [{"root_panel@common.root_panel": {"size": [176, 220], "layer": 1, "controls": [{"common_panel@common.common_panel": {}}, {"chest_panel": {"type": "panel", "layer": 5, "controls": [{"large_chest_panel_top_half@chest.large_chest_panel_top_half": {}}, {"inventory_panel_bottom_half_with_label@common.inventory_panel_bottom_half_with_label": {}}, {"hotbar_grid@common.hotbar_grid_template": {}}, {"inventory_take_progress_icon_button@common.inventory_take_progress_icon_button": {}}]}}, {"inventory_selected_icon_button@common.inventory_selected_icon_button": {}}, {"gamepad_cursor@common.gamepad_cursor_button": {}}]}}]},
        "ender_chest_panel@chest.small_chest_panel": {}, "shulker_box_panel@chest.small_chest_panel": {}, "barrel_panel@chest.small_chest_panel": {},
        "small_chest_screen@common.inventory_screen_common": {"$close_on_player_hurt|default": True, "$show_background": False, "close_on_player_hurt": "$close_on_player_hurt", "variables": [{"requires": "$desktop_screen", "$screen_content": "chest.small_chest_panel", "$screen_bg_content": "common.screen_background"}, {"requires": "$pocket_screen", "$screen_content": "chest.small_chest_panel", "$screen_bg_content": "common.screen_background"}]},
        "large_chest_screen@common.inventory_screen_common": {"$close_on_player_hurt|default": True, "$show_background": False, "close_on_player_hurt": "$close_on_player_hurt", "variables": [{"requires": "$desktop_screen", "$screen_content": "chest.large_chest_panel", "$screen_bg_content": "common.screen_background"}, {"requires": "$pocket_screen", "$screen_content": "chest.large_chest_panel", "$screen_bg_content": "common.screen_background"}]},
        "ender_chest_screen@common.inventory_screen_common": {"$close_on_player_hurt|default": True, "close_on_player_hurt": "$close_on_player_hurt", "variables": [{"requires": "$desktop_screen", "$screen_content": "chest.ender_chest_panel", "$screen_bg_content": "common.screen_background"}, {"requires": "$pocket_screen", "$screen_content": "pocket_containers.ender_chest_panel"}]},
        "shulker_box_screen@chest.small_chest_screen": {"$close_on_player_hurt": True, "variables": [{"requires": "$desktop_screen", "$screen_content": "chest.shulker_box_panel", "$screen_bg_content": "common.screen_background"}, {"requires": "$pocket_screen", "$screen_content": "pocket_containers.shulker_box_panel"}]},
        "barrel_screen@chest.small_chest_screen": {"$close_on_player_hurt": True, "variables": [{"requires": "$desktop_screen", "$screen_content": "chest.barrel_panel", "$screen_bg_content": "common.screen_background"}, {"requires": "$pocket_screen", "$screen_content": "pocket_containers.barrel_panel"}]}
    })
    
    with open(chest_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Tạo _ui_defs.json
    ui_defs_file = Path("staging/target/rp/ui/_ui_defs.json")
    with open(ui_defs_file, 'w', encoding='utf-8') as f:
        json.dump({"ui_defs": ["ui/chest_screen.json", "ui/scoreboards.json"]}, f, ensure_ascii=False, indent=2)
    
    # Tạo scoreboards.json
    scoreboards_file = Path("staging/target/rp/ui/scoreboards.json")
    with open(scoreboards_file, 'w', encoding='utf-8') as f:
        json.dump({"scoreboard_sidebar_score": {"visible": False}}, f, ensure_ascii=False, indent=2)

def check_campfire_json():
    campfire_path = Path("./pack/campfire.json")
    chest_screen_path = Path("staging/target/rp/ui/chest_screen.json")
    
    if not campfire_path.exists():
        return
    
    if not chest_screen_path.exists():
        return
    
    try:
        # Đọc campfire.json
        with open(campfire_path, 'r', encoding='utf-8') as f:
            campfire_data = json.load(f)
        
        # Đọc chest_screen.json
        with open(chest_screen_path, 'r', encoding='utf-8') as f:
            chest_data = json.load(f)
        
        # Duyệt qua fonts trong campfire.json
        fonts = campfire_data.get("fonts", {})
        
        for font_char, font_info in fonts.items():
            gui_info = font_info.get("gui", {})
            custom_offset = gui_info.get("offset", [0, 0])
            
            # Tìm và cập nhật offset trong chest_screen.json
            for key, value in chest_data.items():
                if isinstance(value, dict):
                    # Chỉ xử lý nếu type là "image"
                    if value.get("type") == "image":
                        # Check visible field có chứa font character không
                        visible = value.get("visible", "")
                        if isinstance(visible, str) and font_char in visible:
                            # Cập nhật offset
                            chest_data[key]["offset"] = custom_offset
        
        # Lưu lại chest_screen.json
        with open(chest_screen_path, 'w', encoding='utf-8') as f:
            json.dump(chest_data, f, ensure_ascii=False, indent=2)
        
    except:
        pass

if __name__ == "__main__":
    process_fonts()
    check_campfire_json()
