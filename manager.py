import zipfile, os, subprocess

with zipfile.ZipFile("staging/input_pack.zip", "r") as file:
    file.extractall("pack/")

try:
    import item
except Exception as e: pass 
try:
    result = subprocess.run(["python", "other/layer_armor.py"], capture_output=True, text=True)
except Exception as e: 
    pass
try:
    import armor
except Exception as e: pass
try:
    import font
except Exception as e: pass
try:
    import bow
except Exception as e: pass
try:
    import crossbow
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
    item_model_enabled = os.environ.get('ITEM_MODEL', 'false').lower() == 'true'
    
    if item_model_enabled:
        import sys
        sys.path.insert(0, 'other')
        import mappings
except Exception as e: 
    pass


try:
    import shutil
    import time
    import requests
    
    icon_source = "staging/target/rp/textures"
    bedrock_target = "bedrock/textures"
    
    # Check if running in GitHub Actions
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPOSITORY")
    github_run_id = os.getenv("GITHUB_RUN_ID")
    
    if github_token and github_repo and github_run_id:
        print("Waiting for icon generation to complete...")
        max_attempts = 180
        attempt = 0
        icons_ready = False
        
        while attempt < max_attempts:
            # Check if generate-icons job completed
            try:
                headers = {"Authorization": f"token {github_token}"}
                jobs_url = f"https://api.github.com/repos/{github_repo}/actions/runs/{github_run_id}/jobs"
                response = requests.get(jobs_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    jobs_data = response.json()
                    for job in jobs_data.get("jobs", []):
                        if job.get("name") == "generate-icons":
                            job_status = job.get("status")
                            job_conclusion = job.get("conclusion")
                            
                            if job_status == "completed":
                                print(f"Icon generation completed with conclusion: {job_conclusion}")
                                
                                # Download artifact
                                artifacts_url = f"https://api.github.com/repos/{github_repo}/actions/runs/{github_run_id}/artifacts"
                                artifacts_response = requests.get(artifacts_url, headers=headers, timeout=10)
                                
                                if artifacts_response.status_code == 200:
                                    artifacts_data = artifacts_response.json()
                                    artifact_found = False
                                    
                                    for artifact in artifacts_data.get("artifacts", []):
                                        if artifact.get("name") == "generated-icons":
                                            artifact_found = True
                                            download_url = artifact.get("archive_download_url")
                                            
                                            # Download and extract
                                            print("Downloading icons...")
                                            zip_response = requests.get(download_url, headers=headers, timeout=60)
                                            if zip_response.status_code == 200:
                                                zip_path = "icons.zip"
                                                with open(zip_path, "wb") as f:
                                                    f.write(zip_response.content)
                                                
                                                # Extract
                                                import zipfile
                                                os.makedirs(icon_source, exist_ok=True)
                                                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                                                    zip_ref.extractall(icon_source)
                                                
                                                os.remove(zip_path)
                                                icons_ready = True
                                                print("Icons downloaded successfully!")
                                            break
                                    
                                    if not artifact_found:
                                        print("No icon artifact found - pack contains only 2D items")
                                        icons_ready = True
                                break
                
                if icons_ready:
                    break
                    
            except Exception as e:
                print(f"Error checking icon status: {e}")
            
            print(f"Icon generation in progress... (attempt {attempt}/{max_attempts})")
            time.sleep(10)
            attempt += 1
        
        if not icons_ready:
            print("Warning: Timeout waiting for icon generation, continuing without icons")
    
    # Copy icons to bedrock target
    if os.path.exists(icon_source):
        if not os.path.exists(bedrock_target):
            os.makedirs(bedrock_target, exist_ok=True)
        
        icon_count = 0
        for root, dirs, files in os.walk(icon_source):
            for file in files:
                if file.endswith('.png'):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, icon_source)
                    dst_path = os.path.join(bedrock_target, rel_path)
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    icon_count += 1
        
        if icon_count > 0:
            print(f"Copied {icon_count} icons to bedrock pack")
except Exception as e: 
    print(f"Error handling icons: {e}")
    pass

try:
    result1 = subprocess.run(["python", "other/animations_clear.py"], capture_output=True, text=True)
    result2 = subprocess.run(["python", "other/group_resolve.py"], capture_output=True, text=True)
    result3 = subprocess.run(["python", "other/merge_models.py"], capture_output=True, text=True)
    result4 = subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True)
    result5 = subprocess.run(["python", "other/directory_confusion.py"], capture_output=True, text=True)
    result6 = subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True)
except Exception as e: 
    pass


