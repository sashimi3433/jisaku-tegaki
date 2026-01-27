import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_template(output_path="template.png", grid_size=(10, 10), chars=None):
    # A4 size at 300 DPI
    width, height = 2480, 3508
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    margin = 100
    grid_width = (width - 2 * margin) // grid_size[0]
    grid_height = (height - 2 * margin) // grid_size[1]

    # Draw markers in corners (Black squares)
    marker_size = 50
    # Top-left
    draw.rectangle([margin - marker_size, margin - marker_size, margin, margin], fill=(0, 0, 0))
    # Top-right
    draw.rectangle([width - margin, margin - marker_size, width - margin + marker_size, margin], fill=(0, 0, 0))
    # Bottom-left
    draw.rectangle([margin - marker_size, height - margin, margin, height - margin + marker_size], fill=(0, 0, 0))
    # Bottom-right
    draw.rectangle([width - margin, height - margin, width - margin + marker_size, height - margin + marker_size], fill=(0, 0, 0))

    if chars is None:
        # Default characters (ひらがな example)
        chars = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
    
    char_list = list(chars)
    
    # Try to load a Japanese font, fallback to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/jp/Hiragino Sans GB.ttc", 40)
    except:
        font = ImageFont.load_default()

    for y in range(grid_size[1]):
        for x in range(grid_size[0]):
            idx = y * grid_size[0] + x
            if idx >= len(char_list):
                break
                
            left = margin + x * grid_width
            top = margin + y * grid_height
            right = left + grid_width
            bottom = top + grid_height
            
            # Draw grid
            draw.rectangle([left, top, right, bottom], outline=(200, 200, 200), width=2)
            
            # Draw character label (small)
            char = char_list[idx]
            draw.text((left + 5, top + 5), char, fill=(150, 150, 150), font=font)

    img.save(output_path)
    print(f"Template saved to {output_path}")

if __name__ == "__main__":
    create_template()
