"""Generator for KisanSaathi 30-Image Evaluation Benchmark Suite
Creates realistic, synthetic test images across diseased leaves, healthy foliage,
harvest produce grades (A/B/C), non-crops, and degraded/blurry images.
"""

import os
from PIL import Image, ImageDraw, ImageFilter

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


def create_gradient_leaf(base_color, bg_color=(235, 230, 220), size=(400, 400)):
    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)
    # Draw leaf shape
    draw.polygon([(200, 40), (320, 160), (300, 300), (200, 360), (100, 300), (80, 160)], fill=base_color)
    # Veins
    draw.line([(200, 60), (200, 350)], fill=(base_color[0]-25, base_color[1]-20, base_color[2]-20), width=3)
    draw.line([(200, 150), (270, 120)], fill=(base_color[0]-20, base_color[1]-15, base_color[2]-15), width=2)
    draw.line([(200, 180), (130, 150)], fill=(base_color[0]-20, base_color[1]-15, base_color[2]-15), width=2)
    draw.line([(200, 240), (280, 210)], fill=(base_color[0]-20, base_color[1]-15, base_color[2]-15), width=2)
    draw.line([(200, 260), (120, 230)], fill=(base_color[0]-20, base_color[1]-15, base_color[2]-15), width=2)
    return img


def generate_all():
    print("Generating 30 benchmark test images...")

    # 1. Onion Purple Blotch
    img = create_gradient_leaf((46, 125, 50))
    draw = ImageDraw.Draw(img)
    # Purple blotch with yellow halo
    draw.ellipse([160, 160, 240, 240], fill=(230, 215, 60))
    draw.ellipse([175, 175, 225, 225], fill=(90, 40, 110))
    draw.ellipse([210, 240, 250, 280], fill=(230, 215, 60))
    draw.ellipse([218, 248, 242, 272], fill=(90, 40, 110))
    img.save(os.path.join(IMAGES_DIR, "01_onion_purple_blotch.jpg"), "JPEG", quality=90)

    # 2. Tomato Early Blight
    img = create_gradient_leaf((34, 139, 34))
    draw = ImageDraw.Draw(img)
    # Concentric rings
    for r in [40, 30, 20, 10]:
        draw.ellipse([200-r, 200-r, 200+r, 200+r], fill=(139, 69, 19) if r%2==0 else (100, 50, 15))
    draw.ellipse([140, 260, 180, 300], fill=(110, 60, 20))
    img.save(os.path.join(IMAGES_DIR, "02_tomato_early_blight.jpg"), "JPEG", quality=90)

    # 3. Potato Late Blight
    img = create_gradient_leaf((40, 120, 40))
    draw = ImageDraw.Draw(img)
    # Dark water-soaked lesions on margin with pale rim
    draw.ellipse([80, 150, 160, 240], fill=(220, 220, 200))
    draw.ellipse([85, 155, 155, 235], fill=(30, 40, 30))
    draw.ellipse([250, 220, 310, 290], fill=(220, 220, 200))
    draw.ellipse([255, 225, 305, 285], fill=(25, 35, 25))
    img.save(os.path.join(IMAGES_DIR, "03_potato_late_blight.jpg"), "JPEG", quality=90)

    # 4. Cotton Pink Bollworm
    img = Image.new("RGB", (400, 400), (220, 225, 215))
    draw = ImageDraw.Draw(img)
    # Green cotton boll with entry hole & pink larva sign
    draw.ellipse([100, 100, 300, 300], fill=(50, 130, 50))
    draw.ellipse([180, 180, 220, 220], fill=(20, 20, 20)) # entry hole
    draw.arc([190, 190, 250, 250], 0, 180, fill=(230, 120, 160), width=6) # pink caterpillar curl
    img.save(os.path.join(IMAGES_DIR, "04_cotton_pink_bollworm.jpg"), "JPEG", quality=90)

    # 5. Soybean Yellow Mosaic
    img = create_gradient_leaf((34, 139, 34))
    draw = ImageDraw.Draw(img)
    # Mottled mosaic bright yellow patches
    draw.polygon([(140, 100), (180, 120), (160, 170), (120, 140)], fill=(240, 230, 30))
    draw.polygon([(220, 160), (270, 180), (250, 240), (200, 200)], fill=(245, 235, 40))
    draw.polygon([(130, 220), (180, 260), (150, 310), (110, 270)], fill=(240, 230, 30))
    img.save(os.path.join(IMAGES_DIR, "05_soybean_yellow_mosaic.jpg"), "JPEG", quality=90)

    # 6. Chilli Leaf Curl
    img = create_gradient_leaf((46, 125, 50))
    draw = ImageDraw.Draw(img)
    # Puckered wrinkling lines
    draw.arc([120, 100, 280, 250], 30, 150, fill=(20, 70, 20), width=5)
    draw.arc([100, 180, 260, 330], 40, 160, fill=(20, 70, 20), width=5)
    draw.arc([150, 80, 250, 200], 200, 320, fill=(210, 200, 40), width=4)
    img.save(os.path.join(IMAGES_DIR, "06_chilli_leaf_curl.jpg"), "JPEG", quality=90)

    # 7. Wheat Yellow Rust
    img = Image.new("RGB", (400, 400), (230, 230, 220))
    draw = ImageDraw.Draw(img)
    # Long wheat leaf
    draw.polygon([(170, 20), (230, 20), (230, 380), (170, 380)], fill=(40, 140, 40))
    # Linear stripes of orange-yellow pustules
    for y in range(40, 360, 25):
        draw.rectangle([185, y, 195, y+15], fill=(255, 170, 0))
        draw.rectangle([205, y+10, 215, y+25], fill=(255, 170, 0))
    img.save(os.path.join(IMAGES_DIR, "07_wheat_yellow_rust.jpg"), "JPEG", quality=90)

    # 8. Tomato Fruit Borer
    img = Image.new("RGB", (400, 400), (230, 230, 220))
    draw = ImageDraw.Draw(img)
    draw.ellipse([80, 80, 320, 320], fill=(220, 40, 30)) # red tomato
    draw.ellipse([170, 160, 220, 210], fill=(40, 20, 10)) # bore hole
    draw.ellipse([175, 210, 195, 230], fill=(139, 69, 19)) # frass
    img.save(os.path.join(IMAGES_DIR, "08_tomato_fruit_borer.jpg"), "JPEG", quality=90)

    # 9-13. Healthy foliage
    for fname, crop_color in [
        ("09_tomato_healthy_leaf.jpg", (30, 130, 40)),
        ("10_onion_healthy_leaf.jpg", (45, 140, 80)),
        ("11_potato_healthy_leaf.jpg", (35, 125, 45)),
        ("12_wheat_healthy_leaf.jpg", (50, 150, 50)),
        ("13_soybean_healthy_leaf.jpg", (40, 135, 45))
    ]:
        h_img = create_gradient_leaf(crop_color)
        h_img.save(os.path.join(IMAGES_DIR, fname), "JPEG", quality=90)

    # 14-16. Onion Produce Grades
    # 14. Grade A Onion (clean round red)
    img_a = Image.new("RGB", (400, 400), (240, 240, 235))
    draw_a = ImageDraw.Draw(img_a)
    draw_a.ellipse([100, 100, 300, 300], fill=(160, 35, 55)) # uniform red
    draw_a.arc([120, 120, 280, 280], 45, 135, fill=(185, 55, 75), width=3)
    img_a.save(os.path.join(IMAGES_DIR, "14_onion_grade_a.jpg"), "JPEG", quality=90)

    # 15. Grade B Onion (slight size/color variation)
    img_b = Image.new("RGB", (400, 400), (240, 240, 235))
    draw_b = ImageDraw.Draw(img_b)
    draw_b.ellipse([110, 100, 290, 310], fill=(155, 50, 60))
    draw_b.ellipse([180, 140, 210, 170], fill=(180, 90, 80)) # minor cosmetic peel
    img_b.save(os.path.join(IMAGES_DIR, "15_onion_grade_b.jpg"), "JPEG", quality=90)

    # 16. Grade C Onion (cuts, decay, bruised)
    img_c = Image.new("RGB", (400, 400), (240, 240, 235))
    draw_c = ImageDraw.Draw(img_c)
    draw_c.ellipse([90, 110, 310, 290], fill=(120, 40, 50)) # irregular
    draw_c.polygon([(140, 140), (200, 190), (160, 220)], fill=(50, 20, 20)) # dark rot/cut
    draw_c.line([(180, 200), (250, 250)], fill=(30, 10, 10), width=6) # skin crack
    img_c.save(os.path.join(IMAGES_DIR, "16_onion_grade_c_poor.jpg"), "JPEG", quality=90)

    # 17-19. Tomato Produce Grades
    # 17. Grade A Tomato
    img_ta = Image.new("RGB", (400, 400), (240, 240, 235))
    draw_ta = ImageDraw.Draw(img_ta)
    draw_ta.ellipse([90, 90, 310, 310], fill=(225, 30, 20)) # perfect glossy red
    draw_ta.arc([110, 110, 290, 290], 30, 90, fill=(255, 100, 80), width=5) # gloss highlight
    img_ta.save(os.path.join(IMAGES_DIR, "17_tomato_grade_a.jpg"), "JPEG", quality=90)

    # 18. Grade B Tomato
    img_tb = Image.new("RGB", (400, 400), (240, 240, 235))
    draw_tb = ImageDraw.Draw(img_tb)
    draw_tb.ellipse([95, 95, 305, 305], fill=(215, 45, 25))
    draw_tb.ellipse([170, 95, 230, 135], fill=(130, 160, 40)) # green shoulder
    img_tb.save(os.path.join(IMAGES_DIR, "18_tomato_grade_b.jpg"), "JPEG", quality=90)

    # 19. Grade C Tomato (cracked, soft bruised)
    img_tc = Image.new("RGB", (400, 400), (240, 240, 235))
    draw_tc = ImageDraw.Draw(img_tc)
    draw_tc.ellipse([85, 100, 315, 300], fill=(170, 30, 20))
    draw_tc.line([(140, 130), (230, 240)], fill=(70, 10, 10), width=8) # big skin split
    draw_tc.ellipse([210, 200, 270, 260], fill=(90, 20, 15)) # soft rot bruise
    img_tc.save(os.path.join(IMAGES_DIR, "19_tomato_grade_c_poor.jpg"), "JPEG", quality=90)

    # 20-23. Non-Crop Images
    # 20. Person
    img_p = Image.new("RGB", (400, 400), (200, 220, 240))
    draw_p = ImageDraw.Draw(img_p)
    draw_p.ellipse([140, 60, 260, 180], fill=(235, 180, 140)) # head
    draw_p.rectangle([100, 180, 300, 380], fill=(40, 80, 160)) # blue shirt
    img_p.save(os.path.join(IMAGES_DIR, "20_not_crop_person.jpg"), "JPEG", quality=90)

    # 21. Street
    img_s = Image.new("RGB", (400, 400), (80, 80, 85))
    draw_s = ImageDraw.Draw(img_s)
    draw_s.line([(200, 0), (200, 400)], fill=(240, 230, 40), width=10) # road yellow divider
    img_s.save(os.path.join(IMAGES_DIR, "21_not_crop_street.jpg"), "JPEG", quality=90)

    # 22. Food on Plate
    img_f = Image.new("RGB", (400, 400), (230, 230, 230))
    draw_f = ImageDraw.Draw(img_f)
    draw_f.ellipse([50, 50, 350, 350], fill=(255, 255, 255)) # plate
    draw_f.ellipse([100, 100, 300, 300], fill=(240, 240, 220)) # rice
    draw_f.ellipse([140, 140, 230, 230], fill=(210, 140, 20)) # dal
    img_f.save(os.path.join(IMAGES_DIR, "22_not_crop_plate_food.jpg"), "JPEG", quality=90)

    # 23. Screenshot
    img_ss = Image.new("RGB", (400, 400), (30, 30, 30))
    draw_ss = ImageDraw.Draw(img_ss)
    draw_ss.rectangle([20, 20, 380, 80], fill=(50, 50, 60))
    for i in range(100, 360, 25):
        draw_ss.rectangle([40, i, 200 + (i*13)%140, i+10], fill=(120, 180, 240))
    img_ss.save(os.path.join(IMAGES_DIR, "23_not_crop_screenshot.jpg"), "JPEG", quality=90)

    # 24-27. Blurry, Dark, Overexposed
    # 24. Heavy Blur
    img_b = create_gradient_leaf((46, 125, 50))
    img_b = img_b.filter(ImageFilter.GaussianBlur(radius=22))
    img_b.save(os.path.join(IMAGES_DIR, "24_blurry_leaf.jpg"), "JPEG", quality=90)

    # 25. Dark Leaf (underexposed)
    img_d = Image.new("RGB", (400, 400), (12, 18, 12))
    draw_d = ImageDraw.Draw(img_d)
    draw_d.polygon([(200, 40), (320, 160), (300, 300), (200, 360), (100, 300), (80, 160)], fill=(8, 22, 10))
    img_d.save(os.path.join(IMAGES_DIR, "25_dark_leaf.jpg"), "JPEG", quality=90)

    # 26. Overexposed (glare)
    img_o = Image.new("RGB", (400, 400), (250, 252, 250))
    draw_o = ImageDraw.Draw(img_o)
    draw_o.ellipse([50, 50, 350, 350], fill=(255, 255, 255))
    img_o.save(os.path.join(IMAGES_DIR, "26_overexposed_leaf.jpg"), "JPEG", quality=90)

    # 27. Distant Blurry Plant
    img_dist = create_gradient_leaf((60, 100, 50), size=(200, 200))
    img_dist = img_dist.filter(ImageFilter.GaussianBlur(radius=12)).resize((400, 400))
    img_dist.save(os.path.join(IMAGES_DIR, "27_distant_blurry_plant.jpg"), "JPEG", quality=90)

    # 28-30. Field Mixed / Unclear / Physical Damage
    # 28. Ambiguous dust spots
    img_28 = create_gradient_leaf((46, 125, 50))
    draw_28 = ImageDraw.Draw(img_28)
    for p in [(150, 150), (210, 190), (180, 260), (240, 220)]:
        draw_28.ellipse([p[0], p[1], p[0]+8, p[1]+8], fill=(180, 175, 160)) # dust spots
    img_28.save(os.path.join(IMAGES_DIR, "28_field_unclear_leaves.jpg"), "JPEG", quality=90)

    # 29. Sunburn / Drought Stress
    img_29 = create_gradient_leaf((140, 145, 60))
    draw_29 = ImageDraw.Draw(img_29)
    draw_29.polygon([(180, 120), (260, 160), (220, 240)], fill=(180, 150, 50))
    img_29.save(os.path.join(IMAGES_DIR, "29_field_mixed_stress.jpg"), "JPEG", quality=90)

    # 30. Physical Wind Tear
    img_30 = create_gradient_leaf((46, 125, 50))
    draw_30 = ImageDraw.Draw(img_30)
    draw_30.polygon([(200, 140), (280, 200), (240, 200), (180, 140)], fill=(235, 230, 220)) # jagged tear
    img_30.save(os.path.join(IMAGES_DIR, "30_field_wind_damage.jpg"), "JPEG", quality=90)

    print("Successfully generated all 30 test images in tests/images/")


if __name__ == "__main__":
    generate_all()
