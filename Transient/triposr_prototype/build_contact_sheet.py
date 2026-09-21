from PIL import Image, ImageDraw, ImageFont

BASE = "/mnt/d/Luke/dev/Rimworld/Transient/triposr_prototype"
KLUDGED = "/mnt/d/Luke/dev/Rimworld/src/RimMandrake/WreckedMachines/art_source/AutomatedSmelter/kludged"

def load(path, target_h=320):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    scale = target_h / h
    return im.resize((int(w * scale), target_h), Image.LANCZOS)

def flatten_on_white(im):
    bg = Image.new("RGBA", im.size, (245, 245, 245, 255))
    bg.paste(im, (0, 0), im)
    return bg.convert("RGB")

cells = [
    ("ORIGINAL\nsouth (hero)", f"{BASE}/input_south.png"),
    ("TripoSR mesh\nsouth", f"{BASE}/output/0/facing_south.png"),
    ("TripoSR mesh\neast", f"{BASE}/output/0/facing_east.png"),
    ("TripoSR mesh\nnorth", f"{BASE}/output/0/facing_north.png"),
    ("current pipeline\n(kludged) east", f"{KLUDGED}/AutomatedSmelter_east.png"),
    ("current pipeline\n(kludged) north", f"{KLUDGED}/AutomatedSmelter_north.png"),
]

TARGET_H = 320
imgs = [flatten_on_white(load(p, TARGET_H)) for _, p in cells]
labels = [c[0] for c in cells]

pad = 20
label_h = 50
cell_w = max(im.width for im in imgs) + pad
total_w = cell_w * len(imgs) + pad
total_h = TARGET_H + label_h + pad * 2

sheet = Image.new("RGB", (total_w, total_h), (255, 255, 255))
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
except Exception:
    font = ImageFont.load_default()

x = pad
for im, label in zip(imgs, labels):
    sheet.paste(im, (x + (cell_w - pad - im.width) // 2, label_h))
    draw.multiline_text((x, 8), label, fill=(0, 0, 0), font=font, spacing=2)
    draw.rectangle([x, label_h, x + im.width, label_h + im.height], outline=(180, 180, 180), width=1)
    x += cell_w

out_path = f"{BASE}/contact_sheet.png"
sheet.save(out_path)
print("wrote", out_path, sheet.size)
