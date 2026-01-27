import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_template(output_path="template.png", grid_size=(10, 10), chars=None):
    if chars is None:
        chars = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
    
    char_list = list(chars)
    chars_per_page = grid_size[0] * grid_size[1]
    num_pages = (len(char_list) + chars_per_page - 1) // chars_per_page

    # Try to load a Japanese font, fallback to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/jp/Hiragino Sans GB.ttc", 40)
    except:
        font = ImageFont.load_default()

    width, height = 2480, 3508
    margin = 100
    grid_width = (width - 2 * margin) // grid_size[0]
    grid_height = (height - 2 * margin) // grid_size[1]
    marker_size = 50

    for p in range(num_pages):
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Draw markers in corners
        draw.rectangle([margin - marker_size, margin - marker_size, margin, margin], fill=(0, 0, 0))
        draw.rectangle([width - margin, margin - marker_size, width - margin + marker_size, margin], fill=(0, 0, 0))
        draw.rectangle([margin - marker_size, height - margin, margin, height - margin + marker_size], fill=(0, 0, 0))
        draw.rectangle([width - margin, height - margin, width - margin + marker_size, height - margin + marker_size], fill=(0, 0, 0))

        # Page label (optional but helpful)
        draw.text((width // 2, margin // 2), f"Page {p + 1}", fill=(150, 150, 150), font=font)

        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                idx = p * chars_per_page + y * grid_size[0] + x
                if idx >= len(char_list):
                    break
                    
                left = margin + x * grid_width
                top = margin + y * grid_height
                right = left + grid_width
                bottom = top + grid_height
                
                # Draw grid
                draw.rectangle([left, top, right, bottom], outline=(200, 200, 200), width=2)
                
                # Draw character label
                char = char_list[idx]
                draw.text((left + 5, top + 5), char, fill=(150, 150, 150), font=font)

        # Determine output filename
        if num_pages > 1:
            base, ext = os.path.splitext(output_path)
            current_path = f"{base}_{p + 1}{ext}"
        else:
            current_path = output_path
            
        img.save(current_path)
        print(f"Template saved to {current_path}")

if __name__ == "__main__":
    create_template()
