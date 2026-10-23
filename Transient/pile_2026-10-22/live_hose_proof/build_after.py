"""build_after.py -- live_hose_proof/after.png: the 8 audit defects, before (save b audit) | after (save c). WSL python3,
run from Transient/pile_2026-10-22."""
from PIL import Image, ImageDraw, ImageFont
A = 'hose_audit/'
L = 'live_hose_proof/'
R = [("D1/D2  Hose through the wall and under the battery (C3 north, reel o1)", A + "C09_C3n_battery_wall.jpg", (150, 280, 1050, 560),
      L + "o1_relay_gap.png", (100, 200, 1300, 760), "PASS: reel faces east, hose runs through the wall gap, clear of the battery"),
     ("D3/D4  Hose dives under the pump; stray pipe stub", A + "C08_C3n_junction.jpg", (480, 40, 1000, 470),
      L + "r49818_reel.png", (120, 100, 640, 420), "PASS: one hose from the nozzle, pipe feeds the reel, no stub"),
     ("D6  C7 pipe sleeves stop short of both reels; loose end cap", A + "C26_C7_vertical.jpg", (420, 0, 980, 798),
      L + "C7_vertical_after.png", (300, 60, 640, 960), "PASS: pipe links meet both reels, no loose cap"),
     ("D5  C4 pump-to-reel stub floats behind the crank", A + "C17_C4_pump_reel.jpg", (430, 250, 1060, 470),
      L + "r49838_reel.png", (180, 120, 600, 360), "PASS: link runs from the pump in under the reel"),
     ("D8  Hose end stops short of the tank flange", A + "C21_C5_tank_end.jpg", (560, 390, 1080, 560),
      L + "r49882_end.png", (0, 160, 640, 330), "PASS: coupling sits on the flange"),
     ("D7  Tank-to-reel stub rises to the reel's base", A + "C33_X_reel237.jpg", (640, 260, 1080, 640),
      L + "z_r50099.png", (100, 60, 457, 365), "PASS: link meets the nozzle elbow (shares it with the laid hose)"),
     ("D9  Collar floats off the nozzle (every reel)", A + "C02_C3park_r41683.jpg", (240, 270, 640, 470),
      L + "r49822_reel.png", (160, 230, 640, 420), "PASS: collar on the nozzle tip (all four looks)"),
     ("D10  Hose leaves west and U-turns (reels staged facing West)", A + "C04_C3park_r41685.jpg", (0, 260, 1369, 680),
      L + "r49823_path.png", (150, 40, 620, 470), "PASS: reels face their ends, straight lays")]
W, HW, TH, LH, SH = 1600, 794, 330, 30, 24
out = Image.new("RGB", (W, len(R) * (TH + LH + SH) + 46), (24, 22, 20))
d = ImageDraw.Draw(out)
try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    g = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except Exception:
    f = g = ImageFont.load_default()
d.text((8, 10), "Hose joints + walls: BEFORE (save b, 2026-10-22 audit)  |  AFTER (save c, fixes 849b1674ea / 7870b3b597)",
       fill=(255, 255, 255), font=f)
for i, (lab, bf, bb, af, ab, verd) in enumerate(R):
    y0 = 46 + i * (TH + LH + SH)
    d.text((8, y0 + 5), lab, fill=(255, 214, 90), font=f)
    for k, (fn, box) in enumerate(((bf, bb), (af, ab))):
        im = Image.open(fn).convert("RGB")
        if box:
            im = im.crop(box)
        s = min(HW / im.width, TH / im.height)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
        x0 = 4 + k * (HW + 8)
        out.paste(im, (x0 + (HW - im.width) // 2, y0 + LH))
    d.text((8, y0 + LH + TH + 2), "before", fill=(230, 120, 110), font=g)
    d.text((4 + HW + 8, y0 + LH + TH + 2), "after: " + verd, fill=(140, 220, 140), font=g)
out.save(L + "after.png")
print(out.size)
