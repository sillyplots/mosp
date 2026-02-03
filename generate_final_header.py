from PIL import Image, ImageOps, ImageChops
import os

# Paths
source_path = '/Users/charliethompson/Documents/mosp/posts/super_bowl/assets/gravity_equation_twitter_bg.png'
output_path = '/Users/charliethompson/Documents/mosp/posts/super_bowl/assets/twitter_header_final.png'

def create_twitter_header():
    if not os.path.exists(source_path):
        print(f"Error: Source file not found at {source_path}")
        return

    try:
        # Open source image
        img = Image.open(source_path).convert("RGBA")
        print(f"Original size: {img.size}")

        # The image is likely White Text on Blue Background.
        # We want Black Text on #f4f4f0 Background.
        
        # 1. Convert to Grayscale
        gray = img.convert("L")
        
        # 2. Threshold/Invert to get a Mask of the Text
        # Since text is white (high value) and bg is blue (lower luminance?), 
        # White text in grayscale is close to 255. Blue bg is darker.
        # Let's inspect rough values or just threshold.
        # We can normalize to stretch contrast.
        gray = ImageOps.autocontrast(gray)
        
        # Now text should be white, bg black-ish.
        # Let's clean it up with a threshold.
        # Anything > 100 is text?
        threshold = 128
        mask = gray.point(lambda p: 255 if p > threshold else 0)
        
        # Crop mask to content
        bbox = mask.getbbox()
        if not bbox:
            print("Error: No text detected.")
            return
            
        print(f"Text bbox: {bbox}")
        cropped_mask = mask.crop(bbox)
        
        # 3. Create target Text image
        # We want the text to be BLACK.
        # So we create a Black image and use cropped_mask as alpha.
        text_layer = Image.new("RGBA", cropped_mask.size, (0, 0, 0, 255))
        text_layer.putalpha(cropped_mask)
        
        # 4. Create Background
        # User wants "get rid of light blue". 
        # Using the blog's standard off-white/beige: #f4f4f0
        bg_color = (244, 244, 240, 255) # #f4f4f0
        
        target_width = 1500
        target_height = 500
        final_img = Image.new("RGBA", (target_width, target_height), bg_color)
        
        # 5. Resize Text if needed to fit nicely
        safe_w = 1400
        safe_h = 400
        
        content_w, content_h = text_layer.size
        scale = 1.0
        
        if content_w > safe_w or content_h > safe_h:
            scale_w = safe_w / content_w
            scale_h = safe_h / content_h
            scale = min(scale_w, scale_h)
            new_w = int(content_w * scale)
            new_h = int(content_h * scale)
            text_layer = text_layer.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # 6. Compose
        x_offset = (target_width - text_layer.width) // 2
        y_offset = (target_height - text_layer.height) // 2
        
        final_img.alpha_composite(text_layer, (x_offset, y_offset))
        
        final_img.save(output_path)
        print(f"Successfully saved recolored header to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_twitter_header()
