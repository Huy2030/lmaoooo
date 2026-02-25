#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# JSON Unicode Obfuscator

import json
import shutil
from pathlib import Path


def unicode_escape_string(s):
    """Convert string to \\uXXXX format"""
    return "".join(f"\\u{ord(c):04x}" for c in s)


def obfuscate_to_string(obj, indent=0):
    """Convert object to obfuscated JSON string manually"""
    if isinstance(obj, str):
        # Return escaped string with quotes
        return '"' + unicode_escape_string(obj) + '"'
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif obj is None:
        return "null"
    elif isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            key_str = '"' + unicode_escape_string(k) + '"'
            val_str = obfuscate_to_string(v, indent)
            items.append(f"{key_str}:{val_str}")
        return "{" + ",".join(items) + "}"
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        items = [obfuscate_to_string(item, indent) for item in obj]
        return "[" + ",".join(items) + "]"
    else:
        return str(obj)


def process_file(path):
    """Process a JSON file"""
    try:
        # Backup
        backup = path.with_suffix(".json.bak")
        shutil.copy2(path, backup)
        
        # Read JSON
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Obfuscate to string
        obfuscated_str = obfuscate_to_string(data)
        
        # Write back as raw string
        with open(path, 'w', encoding='utf-8') as f:
            f.write(obfuscated_str)
        
        return True
    except Exception:
        return False


def main():
    """Main function"""
    paths = [
        'staging/target/rp/models/entity',
        'staging/target/rp/attachables',
        'staging/target/rp/ui',
        'staging/target/rp/sounds',
        'staging/target/rp/animations',
        'staging/target/rp/render_controllers',
        'staging/target/rp/animation_controllers',
        'staging/target/rp/manifest.json',
        'staging/target/rp/textures/item_texture.json',
        'staging/target/rp/textures/terrain_texture.json',
        'staging/bedrock/models/entity',
        'staging/bedrock/attachables',
        'staging/bedrock/ui',
        'staging/bedrock/sounds',
        'staging/bedrock/animations',
        'staging/bedrock/render_controllers',
        'staging/bedrock/animation_controllers',
        'staging/bedrock/manifest.json',
        'staging/bedrock/textures/item_texture.json',
        'staging/bedrock/textures/terrain_texture.json'
    ]
    
    all_files = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        if p.is_file():
            all_files.append(p)
        else:
            all_files.extend(p.glob('**/*.json'))
    
    for f in all_files:
        process_file(f)
    
    # Remove all .bak files
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        if p.is_file():
            backup = p.with_suffix(".json.bak")
            if backup.exists():
                backup.unlink()
        else:
            for backup in p.glob('**/*.json.bak'):
                backup.unlink()


if __name__ == "__main__":
    main()

