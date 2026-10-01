import os
import httpx
from PIL import Image, ImageDraw, ImageFont
import io

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

IMAGE_URLS = {
    "hero_farmer": "https://images.unsplash.com/photo-1595273670150-bd0c3c392e46?w=800&q=80",
    "onion": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400&q=80",
    "tomato": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&q=80",
    "potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&q=80",
    "wheat": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&q=80",
    "soybean": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?w=400&q=80",
    "cotton": "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?w=400&q=80",
    "tur": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80",
    "rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&q=80",
    "maize": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400&q=80",
    "sugarcane": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&q=80",
    "chilli": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?w=400&q=80",
    "groundnut": "https://images.unsplash.com/photo-1567892328221-1c229f3458bf?w=400&q=80"
}

FALLBACK_COLORS = {
    "hero_farmer": ((46, 125, 50), (20, 83, 45), "🌾 KisanSaathi"),
    "onion": ((194, 65, 12), (154, 52, 18), "🧅 Onion"),
    "tomato": ((220, 38, 38), (185, 28, 28), "🍅 Tomato"),
    "potato": ((180, 83, 9), (146, 64, 14), "🥔 Potato"),
    "wheat": ((217, 119, 6), (180, 83, 9), "🌾 Wheat"),
    "soybean": ((101, 163, 13), (77, 124, 15), "🌱 Soybean"),
    "cotton": ((226, 232, 240), (203, 213, 225), "☁️ Cotton"),
    "tur": ((161, 98, 7), (133, 77, 14), "🥣 Tur"),
    "rice": ((234, 179, 8), (202, 138, 4), "🌾 Rice"),
    "maize": ((245, 158, 11), (217, 119, 6), "🌽 Maize"),
    "sugarcane": ((22, 101, 52), (20, 83, 45), "🎋 Sugarcane"),
    "chilli": ((239, 68, 68), (185, 28, 28), "🌶️ Chilli"),
    "groundnut": ((161, 98, 7), (120, 53, 15), "🥜 Groundnut")
}

def create_fallback_image(name, target_size):
    bg_color, accent, label = FALLBACK_COLORS.get(name, ((46, 125, 50), (20, 83, 45), name))
    img = Image.new("RGB", target_size, bg_color)
    draw = ImageDraw.Draw(img)
    w, h = target_size
    # Draw simple gradient/border
    draw.rectangle([6, 6, w-6, h-6], outline=accent, width=4)
    return img

print("Downloading and processing assets into frontend/assets/ ...")

for name, url in IMAGE_URLS.items():
    dest_path = os.path.join(ASSETS_DIR, f"{name}.webp")
    target_size = (600, 400) if name == "hero_farmer" else (240, 240)
    max_kb = 140 if name == "hero_farmer" else 25

    img = None
    try:
        with httpx.Client(timeout=6.0, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception as e:
        print(f"Network fetch failed for {name}: {e}")

    if img is None:
        img = create_fallback_image(name, target_size)

    # Resize with thumbnail
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # Save as WebP with quality compression
    quality = 80
    img.save(dest_path, "WEBP", quality=quality)
    
    # Check size constraint
    file_size_kb = os.path.getsize(dest_path) / 1024.0
    while file_size_kb > max_kb and quality > 30:
        quality -= 10
        img.save(dest_path, "WEBP", quality=quality)
        file_size_kb = os.path.getsize(dest_path) / 1024.0

    print(f"  [OK] {name}.webp saved ({file_size_kb:.1f} KB, quality={quality})")

print("All assets processed successfully.")
