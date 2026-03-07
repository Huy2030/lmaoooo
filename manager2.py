import zipfile, os, subprocess

with zipfile.ZipFile("staging/input_pack.zip", "r") as file:
    file.extractall("pack/")
offhand_enabled = False
try:
    issue_title = os.environ.get('GITHUB_ISSUE_TITLE', '').upper()
    print(f"DEBUG: Issue title = '{issue_title}'")
    if 'OFFHAND' in issue_title and 'NON-OFFHAND' not in issue_title:
        offhand_enabled = True
except Exception as e:
    pass

if offhand_enabled:
    try:
        result = subprocess.run(["python", "manager.py"], capture_output=True, text=True)
        if result.returncode != 0:
            pass
    except Exception as e:
        pass
else:
    try:
        import item_non_offhand
    except Exception as e: pass 
    try:
        import armor
    except Exception as e: pass
    try:
        import font
    except Exception as e: pass
    try:
        import bow_non_offhand
    except Exception as e: pass
    try:
        import crossbow_non_offhand
    except Exception as e: pass
    try:
        import shield
    except Exception as e: pass
    try:
        import blocks
    except Exception as e: pass
    try:
        import sound
    except Exception as e: pass
    try:
        result = subprocess.run(["python", "other/gui.py"], capture_output=True, text=True)
    except Exception as e: 
        pass
    try:
        result = subprocess.run(["python", "other/remove.py"], capture_output=True, text=True)
    except Exception as e: 
        pass
    try:
        result = subprocess.run(["python", "other/auto_sprites.py"], capture_output=True, text=True)
    except Exception as e: pass

    try:
        result = subprocess.run(["python", "other/resize_armor.py"], capture_output=True, text=True)
    except Exception as e: 
        pass

    try:
        result = subprocess.run(
            ["node", "tools/generate-simple.js"],
            cwd=".",
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            import shutil
            icon_source = "tools/generated_icons"
            targets = [
                "staging/target/rp/textures",
                "bedrock/textures"
            ]
            for target in targets:
                if os.path.exists(icon_source):
                    for root, dirs, files in os.walk(icon_source):
                        for file in files:
                            if file.endswith('.png'):
                                src_path = os.path.join(root, file)
                                rel_path = os.path.relpath(src_path, icon_source)
                                dst_path = os.path.join(target, rel_path)
                                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                                shutil.copy2(src_path, dst_path)
    except Exception as e: 
        pass

    try:
        result1 = subprocess.run(["python", "other/animations_clear.py"], capture_output=True, text=True)
        result2 = subprocess.run(["python", "other/group_resolve.py"], capture_output=True, text=True)
        result3 = subprocess.run(["python", "other/merge_models.py"], capture_output=True, text=True)
        result4 = subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True)
        result5 = subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True)
    except Exception as e: 
        pass


