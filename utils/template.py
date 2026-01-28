import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_template(output_path="template.png", grid_size=(10, 10), groups=None):
    if groups is None:
        groups = [("hiragana", "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん")]
    
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
    chars_per_page = grid_size[0] * grid_size[1]

    for label, chars in groups:
        char_list = list(chars)
        num_pages = (len(char_list) + chars_per_page - 1) // chars_per_page

        for p in range(num_pages):
            img = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            # Draw markers
            draw.rectangle([margin - marker_size, margin - marker_size, margin, margin], fill=(0, 0, 0))
            draw.rectangle([width - margin, margin - marker_size, width - margin + marker_size, margin], fill=(0, 0, 0))
            draw.rectangle([margin - marker_size, height - margin, margin, height - margin + marker_size], fill=(0, 0, 0))
            draw.rectangle([width - margin, height - margin, width - margin + marker_size, height - margin + marker_size], fill=(0, 0, 0))

            # Header label (Preset name and Page)
            page_text = f"{label} - Page {p + 1}"
            draw.text((width // 2 - 100, margin // 2), page_text, fill=(150, 150, 150), font=font)

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
                    
                    # Draw reference lines (center cross)
                    center_x = left + grid_width // 2
                    center_y = top + grid_height // 2
                    guide_color = (235, 235, 235)
                    draw.line([left + 10, center_y, right - 10, center_y], fill=guide_color, width=1)
                    draw.line([center_x, top + 10, center_x, bottom - 10], fill=guide_color, width=1)

                    # For alphabet, add baseline (80%) and mean line (40%) to match font metrics
                    char = char_list[idx]
                    if label == "alphabet" or (char.isascii() and char.isalpha()):
                        baseline_y = top + int(grid_height * 0.8)
                        mean_line_y = top + int(grid_height * 0.4)
                        # Slightly darker for baseline
                        draw.line([left + 10, baseline_y, right - 10, baseline_y], fill=(220, 220, 220), width=1)
                        # Slightly lighter for mean line
                        draw.line([left + 10, mean_line_y, right - 10, mean_line_y], fill=(240, 240, 240), width=1)

                    # Draw character label
                    draw.text((left + 5, top + 5), char, fill=(150, 150, 150), font=font)

            # Generate filename
            base, ext = os.path.splitext(output_path)
            if num_pages > 1:
                filename = f"{base}_{label}_{p + 1}{ext}"
            else:
                filename = f"{base}_{label}{ext}"
                
            img.save(filename)
            print(f"Template saved to {filename}")

if __name__ == "__main__":
    create_template()
