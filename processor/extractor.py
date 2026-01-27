import cv2
import numpy as np
import os

class CharacterExtractor:
    def __init__(self, grid_size=(10, 10), margin=100):
        self.grid_size = grid_size
        self.margin = margin

    def process(self, image_path, output_dir="extracted"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        # 1. Detect markers and correct perspective
        corrected = self._correct_perspective(img)
        
        # 2. Extract cells
        h, w = corrected.shape[:2]
        cell_w = (w - 2 * self.margin) // self.grid_size[0]
        cell_h = (h - 2 * self.margin) // self.grid_size[1]

        extracted_chars = []
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                left = self.margin + x * cell_w
                top = self.margin + y * cell_h
                right = left + cell_w
                bottom = top + cell_h
                
                cell = corrected[top:bottom, left:right]
                char_img = self._preprocess_char(cell)
                
                if char_img is not None:
                    char_path = os.path.join(output_dir, f"char_{y}_{x}.png")
                    cv2.imwrite(char_path, char_img)
                    extracted_chars.append(char_path)
        
        return extracted_chars

    def _correct_perspective(self, img):
        # A simplified version: search for corner markers
        # In a real scenario, we'd use contour detection or feature matching
        # For now, let's assume the user provided a reasonably aligned image 
        # but we'll try to find the outermost black squares.
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find 4 corners based on squares near the corners
        # This is a bit naive but works for a prototype
        points = []
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:
                area = cv2.contourArea(cnt)
                if 500 < area < 10000: # Heuristic for marker size
                    M = cv2.moments(cnt)
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    points.append([cx, cy])
        
        if len(points) < 4:
            # Fallback: if markers not found, just return original (maybe resized)
            return cv2.resize(img, (2480, 3508))

        # Sort points: top-left, top-right, bottom-left, bottom-right
        points = np.array(points)
        s = points.sum(axis=1)
        tl = points[np.argmin(s)]
        br = points[np.argmax(s)]
        
        diff = np.diff(points, axis=1)
        tr = points[np.argmin(diff)]
        bl = points[np.argmax(diff)]
        
        src = np.float32([tl, tr, bl, br])
        dst = np.float32([[100, 100], [2380, 100], [100, 3408], [2380, 3408]])
        
        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(img, M, (2480, 3508))
        
        return warped

    def _preprocess_char(self, cell):
        # crop a bit more to remove grid lines
        inner_margin = 10
        cell = cell[inner_margin:-inner_margin, inner_margin:-inner_margin]
        
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        # Binarization
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Noise removal
        kernel = np.ones((2,2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Check if empty
        if cv2.countNonZero(thresh) < 50:
            return None
            
        return thresh

if __name__ == "__main__":
    # Test stub
    pass
