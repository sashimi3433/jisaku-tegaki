from fontTools.ttLib import TTFont, newTable
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
import cv2
import numpy as np
import os

class FontBuilderWrapper:
    def __init__(self, font_name="MyHandwriting"):
        self.font_name = font_name
        self.units_per_em = 1000
        self.ascender = 800
        self.descender = -200

    def build(self, char_data, output_path="output.ttf"):
        """
        char_data: list of dict {'char': 'あ', 'image_path': 'path/to/img'}
        """
        glyphs = {}
        # Add .notdef glyph (required)
        glyphs[".notdef"] = self._create_empty_glyph()
        
        cmap = {}
        
        for item in char_data:
            char = item['char']
            img_path = item['image_path']
            
            glyph_name = f"glyph{ord(char):04x}"
            glyph = self._create_glyph_from_image(img_path)
            
            glyphs[glyph_name] = glyph
            cmap[ord(char)] = glyph_name

        # Font setup
        fb = FontBuilder(self.units_per_em, isTTF=True)
        fb.setupGlyphOrder(list(glyphs.keys()))
        fb.setupCharacterMap(cmap)
        
        # Simple glyph metrics
        metrics = {name: (self.units_per_em, 0) for name in glyphs.keys()}
        fb.setupHorizontalMetrics(metrics)
        
        # ps_name must not contain spaces
        ps_name = self.font_name.replace(" ", "")
        
        # 1. Add .notdef and space (Required for stability in Word/Excel)
        if ".notdef" not in glyphs:
            glyphs[".notdef"] = self._create_empty_glyph()
        
        if 32 not in cmap: # Space
            space_name = "space"
            glyphs[space_name] = self._create_empty_glyph()
            cmap[32] = space_name

        # Font setup
        fb = FontBuilder(self.units_per_em, isTTF=True)
        fb.setupGlyphOrder(list(glyphs.keys()))
        fb.setupCharacterMap(cmap)
        
        # Metrics: all glyphs get 1000 unit width
        metrics = {name: (self.units_per_em, 0) for name in glyphs.keys()}
        fb.setupHorizontalMetrics(metrics)
        
        fb.setupHorizontalHeader(ascent=self.ascender, descent=self.descender)
        
        fb.setupNameTable({
            "copyright": "Created with MyHandwriting CLI",
            "familyName": self.font_name,
            "styleName": "Regular",
            "uniqueFontIdentifier": f"1.000;NONE;{ps_name}",
            "fullName": self.font_name,
            "version": "Version 1.000",
            "psName": ps_name,
        })
        
        # Setup OS/2 table with Japanese code page bits
        fb.setupOS2(
            sTypoAscender=self.ascender, 
            sTypoDescender=self.descender, 
            usWinAscent=self.ascender, 
            usWinDescent=abs(self.descender),
            # Set CodePageRange to Japanese (bit 17: Shift-JIS, bit 0: Latin)
            # This helps Word recognize it as a Japanese font
        )
        # Update OS/2 flags manually for better compatibility
        fb.font['OS/2'].ulCodePageRange1 = 1 << 17 | 1 << 0
        
        fb.setupPost()
        # Set post table version to 2.0 for better name mapping
        fb.font['post'].formatType = 2.0
        
        fb.setupGlyf(glyphs)
        fb.save(output_path)
        print(f"Font saved to {output_path}")

    def _create_empty_glyph(self):
        pen = TTGlyphPen(None)
        return pen.glyph()

    def _create_glyph_from_image(self, img_path):
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return self._create_empty_glyph()

        # Find contours with hierarchy (RETR_CCOMP retrieves all contours and organizes them into a two-level hierarchy)
        contours, hierarchy = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        
        if hierarchy is None:
            return self._create_empty_glyph()

        pen = TTGlyphPen(None)
        
        h, w = img.shape
        scale_x = self.units_per_em / w
        scale_y = (self.ascender - self.descender) / h
        
        # hierarchy[0] has [Next, Previous, First_Child, Parent]
        for i, cnt in enumerate(contours):
            if len(cnt) < 3:
                continue
            
            # If the contour has a parent, it's a hole.
            # TTF uses non-zero winding rule. To create a hole, 
            # the hole contour should have the opposite orientation of the outer contour.
            # OpenCV's default orientation might need to be checked or reversed.
            is_hole = hierarchy[0][i][3] != -1
            
            # Convert contour points to font coordinates
            points = []
            for p in cnt:
                px, py = p[0]
                tx = px * scale_x
                ty = self.ascender - (py * scale_y)
                points.append((tx, ty))

            # Draw the contour
            pen.moveTo(points[0])
            for p in points[1:]:
                pen.lineTo(p)
            pen.closePath()
            
        return pen.glyph()

if __name__ == "__main__":
    pass
