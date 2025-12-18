import base64
import os

# Main background image (outer)
bg_path = '/Users/layyzy/neuro_rehab_mvp/neuro_background_v2.jpg'
# Overlay container image (inner)
overlay_path = '/Users/layyzy/.gemini/antigravity/brain/d16dc5ce-ed45-4b0b-938c-599f2f6bef91/uploaded_image_1766059452695.jpg'

output_path = '/Users/layyzy/neuro_rehab_mvp/login_assets.py'

def get_b64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        print(f"Error: File not found {path}")
        return ""

try:
    bg_b64 = get_b64(bg_path)
    overlay_b64 = get_b64(overlay_path)
    
    if bg_b64 and overlay_b64:
        with open(output_path, "w") as f:
            f.write(f'LOGIN_BG_B64 = "data:image/png;base64,{bg_b64}"\n')
            f.write(f'CONTAINER_BG_B64 = "data:image/jpeg;base64,{overlay_b64}"')
        print(f"Successfully created {output_path} with both backgrounds")
    else:
        print("Failed to encode images")
except Exception as e:
    print(f"Error: {e}")
