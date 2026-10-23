"""phone.py -- build phone_defects.png from the audit captures (WSL python3, run in hose_audit/)."""
from PIL import Image, ImageDraw, ImageFont
T = [("C09_C3n_battery_wall.jpg", (150, 280, 1050, 560), "1  Hose runs UNDER the battery and THROUGH the wall (map C, C3 north)"),
     ("C08_C3n_junction.jpg", (480, 40, 1000, 470), "2  Reel o1: hose dives under the pump; stray pipe stub points at nothing"),
     ("C26_C7_vertical.jpg", (420, 0, 980, 798), "3  C7: pipe end sleeves stop short of both reels; loose end-cap piece"),
     ("C17_C4_pump_reel.jpg", (430, 250, 1060, 470), "4  C4: pump-to-reel stub floats behind the reel's crank (no inlet there)"),
     ("C21_C5_tank_end.jpg", (560, 390, 1080, 560), "5  C5: hose end stops ~0.4 cell short of the tank flange, kinked"),
     ("C33_X_reel237.jpg", (640, 260, 1080, 640), "6  Tank-to-reel stub rises to the reel's base, not its nozzle"),
     ("C02_C3park_r41683.jpg", (240, 270, 640, 470), "7  Every reel: hose collar floats ~0.1-0.3 cell off the nozzle"),
     ("C04_C3park_r41685.jpg", (0, 260, 1369, 680), "8  Every east target: hose leaves west and U-turns (reels staged facing West)")]
W, TW, TH, LH = 1600, 790, 420, 34
rows = (len(T) + 1) // 2
out = Image.new("RGB", (W, rows * (TH + LH) + 10), (24, 22, 20))
d = ImageDraw.Draw(out)
try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
except Exception:
    f = ImageFont.load_default()
for i, (fn, box, lab) in enumerate(T):
    im = Image.open(fn).convert("RGB").crop(box)
    s = min(TW / im.width, TH / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0 = 6 + (i % 2) * (TW + 8); y0 = 6 + (i // 2) * (TH + LH)
    out.paste(im, (x0 + (TW - im.width) // 2, y0 + LH))
    d.text((x0 + 4, y0 + 7), lab, fill=(255, 214, 90), font=f)
out.save("phone_defects.png"); print(out.size)
