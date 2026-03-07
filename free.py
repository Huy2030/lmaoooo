import zipfile, os, subprocess

with zipfile.ZipFile("staging/input_pack.zip", "r") as file:
    file.extractall("pack/")

# Tự động bật tất cả các conversion
try:
    import armor
except Exception as e: pass
try:
    import font
except Exception as e: pass
try:
    import sound
except Exception as e: pass
try:
    result = subprocess.run(["python", "other/remove.py"], capture_output=True, text=True)
except Exception as e: 
    pass
try:
    result = subprocess.run(["python", "other/auto_sprites.py"], capture_output=True, text=True)
except Exception as e: pass



try:
    result = subprocess.run(
        ["node", "tools/generate-simple.js"],
        cwd=".",
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        # Resize icons
        resize_result = subprocess.run(["python", "other/resize_icon.py"], capture_output=True, text=True)
        print(f"[FREE.PY] Resize output: {resize_result.stdout}")
        if resize_result.stderr:
            print(f"[FREE.PY] Resize error: {resize_result.stderr}")
        
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
    print(f"[FREE.PY] Exception: {e}")
    pass

try:
    result3 = subprocess.run(["python", "other/merge_models.py"], capture_output=True, text=True)
    result4 = subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True)
    result5 = subprocess.run(["python", "other/directory_confusion.py"], capture_output=True, text=True)
    result6 = subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True)
except Exception as e: 
    pass


