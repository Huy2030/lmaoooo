import json
import os
from PIL import Image

# Bỏ qua nếu mappings.py đã chạy
if os.getenv("ITEM_MODEL") == "true":
    exit(0)

with open('staging/mappings.json', 'r') as f:
    mappings = json.load(f)

with open('staging/target/rp/textures/item_texture.json', 'r') as f:
    item_textures = json.load(f)

render_offsets = {
    80: :{"main_hand":{"first_person":{"scale":{"x":0.005,"y":0.005,"z":0.005}},"third_person":{"scale":{"x":0.0125,"y":0.0125,"z":0.0125}}},"off_hand":{"first_person":{"scale":{"x":0.005,"y":0.005,"z":0.005}},"third_person":{"scale":{"x":0.0125,"y":0.0125,"z":0.0125}}}}
}

for key, value in mappings['items'].items():
    if key.startswith('minecraft:') and any(armor_type in key for armor_type in ['_helmet', '_chestplate', '_leggings', '_boots']):
        for item in value:
            name = item['name']
            if name in item_textures['texture_data']:
                texture_path = item_textures['texture_data'][name]['textures']
                icon_path = f"staging/target/rp/{texture_path}.png"
                try:
                    with Image.open(icon_path) as img:
                        size = img.size[0]
                    if size == 16:
                        item.pop('render_offsets', None)
                    elif size in render_offsets:
                        item['render_offsets'] = render_offsets[size]
                except:
                    pass

with open('staging/mappings.json', 'w') as f:
    json.dump(mappings, f, indent=2)