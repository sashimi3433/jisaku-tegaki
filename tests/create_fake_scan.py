from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

def create_fake_scan(template_path="template.png", output_path="fake_scan.png"):
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font that looks like handwriting or just a clear font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/jp/Hiragino Sans GB.ttc", 150)
    except:
        font = ImageFont.load_default()

    margin = 100
    grid_w, grid_h = 228, 330 # (2480-2*100)/10, (3508-2*100)/10
    
    chars = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
    
    for i, char in enumerate(chars):
        y = i // 10
        x = i % 10
        
        pos_x = margin + x * grid_w + 40
        pos_y = margin + y * grid_h + 80
        
        draw.text((pos_x, pos_y), char, fill=(0, 0, 0), font=font)

    # Save and add some "scan noise" or rotation if needed, but let's keep it clean first
    img.save(output_path)
    print(f"Fake scan created at {output_path}")

if __name__ == "__main__":
    create_fake_scan()
