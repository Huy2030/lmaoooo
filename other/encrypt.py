# Mã hóa Minecraft Bedrock Resource Pack
import os, subprocess, urllib.request, sys, zipfile, json, random, string

BINARY_URL = "https://www.dropbox.com/scl/fi/dsijqbsp8llium7ds2ixk/EncryptMyPack?rlkey=bwpwh2oc1b6193n523i2685t0&st=ik4hye9n&dl=1"
BINARY_PATH = "other/EncryptMyPack"

def generate_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def download_binary():
    if not os.path.exists(BINARY_PATH):
        os.makedirs(os.path.dirname(BINARY_PATH), exist_ok=True)
        urllib.request.urlretrieve(BINARY_URL, BINARY_PATH)
        os.chmod(BINARY_PATH, 0o755)
    return BINARY_PATH

def encrypt_pack_python(input_zip, output_zip, key):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "cryptography"], check=True, capture_output=True)
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
    
    with zipfile.ZipFile(input_zip, 'r') as zin:
        manifest = json.loads(zin.read('manifest.json'))
        content_id = manifest['header']['uuid']
    
    excluded = ['manifest.json', 'pack_icon.png', 'bug_pack_icon.png']
    content_entries = []
    
    with zipfile.ZipFile(input_zip, 'r') as zin:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.is_dir():
                    continue
                data = zin.read(item.filename)
                
                if item.filename in excluded:
                    zout.writestr(item, data)
                    content_entries.append({"path": item.filename, "key": None})
                else:
                    file_key = generate_key()
                    iv = file_key[:16].encode()
                    cipher = Cipher(algorithms.AES(file_key.encode()), modes.CFB8(iv), backend=default_backend())
                    encryptor = cipher.encryptor()
                    encrypted = encryptor.update(data) + encryptor.finalize()
                    zout.writestr(item, encrypted)
                    content_entries.append({"path": item.filename, "key": file_key})
            
            contents_json = json.dumps({"content": content_entries})
            iv = key[:16].encode()
            cipher = Cipher(algorithms.AES(key.encode()), modes.CFB8(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_contents = encryptor.update(contents_json.encode()) + encryptor.finalize()
            
            header = b'\x00\x00\x00\x00\xFC\xB9\xCF\x9B' + b'\x00' * 8
            content_id_bytes = content_id.encode()
            header += bytes([len(content_id_bytes)]) + content_id_bytes
            header += b'\x00' * (0x100 - len(header))
            zout.writestr('contents.json', header + encrypted_contents)
    return True

def encrypt_pack(input_zip, output_zip=None, key=None, delete_original=False):
    if not output_zip:
        output_zip = input_zip.replace('.mcpack', '_encrypted.mcpack').replace('.zip', '_encrypted.zip')
    if not key:
        key = generate_key()
    
    try:
        binary_path = download_binary()
        result = subprocess.run([binary_path, input_zip, output_zip, key], capture_output=True, text=True, timeout=300)
        if not os.path.exists(output_zip):
            encrypt_pack_python(input_zip, output_zip, key)
    except:
        encrypt_pack_python(input_zip, output_zip, key)
    
    if os.path.exists(output_zip):
        print(f"✓ Mã hóa: {output_zip}")
        print(f"✓ Key: {key}")
        key_file = output_zip.replace('.mcpack', '_key.txt').replace('.zip', '_key.txt')
        with open(key_file, 'w') as f:
            f.write(key)
        if delete_original and os.path.exists(input_zip):
            os.remove(input_zip)
        return key
    else:
        raise Exception(f"Encryption failed")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) >= 3 else None
        key = sys.argv[3] if len(sys.argv) >= 4 else None
        encrypt_pack(input_file, output_file, key)
    else:
        print("Dùng: python other/encrypt.py <input> [output] [key]")
