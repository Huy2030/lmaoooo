import zipfile, os, subprocess

with zipfile.ZipFile("staging/input_pack.zip", "r") as file:
    file.extractall("pack/")

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
    result = subprocess.run(["python", "other/free/animation.py"], capture_output=True, text=True)
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
                            if job_status == "completed":
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
                                            
                                            zip_response = requests.get(download_url, headers=headers, timeout=60)
                                            if zip_response.status_code == 200:
                                                zip_path = "icons.zip"
                                                with open(zip_path, "wb") as f:
                                                    f.write(zip_response.content)
                                                
                                                import zipfile
                                                os.makedirs(icon_source, exist_ok=True)
                                                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                                                    zip_ref.extractall(icon_source)
                                                
                                                os.remove(zip_path)
                                                icons_ready = True
                                            break
                                    
                                    if not artifact_found:
                                        icons_ready = True
                                break
                
                if icons_ready:
                    break
                    
            except Exception as e:
                pass
            
            time.sleep(10)
            attempt += 1
    
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
            try:
                import sys
                sys.path.insert(0, 'other')
                import resize_icon
                resize_icon.resize_icons()
            except Exception as e: 
                pass
except Exception as e: 
    pass

try:
    result4 = subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True)
    result5 = subprocess.run(["python", "other/directory_confusion.py"], capture_output=True, text=True)
    result6 = subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True)
except Exception as e: 
    pass


