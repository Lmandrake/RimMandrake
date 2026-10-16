"""blockout.py -- the geometry guide for the coupling edit: each look's Reel_Deployed crop (x 0-128, y 72-200, x8 ->
1024) with the old foreshortened coupling erased and a flat grey side-on cylinder drawn where the new one must sit:
flat end at u 9 (HoseReelRect.NozzleTip), centred on v 135 (MouthDZ), 42 px tall (the laid hose, 0.465 cells),
running right to the pump body at u JUNCTION[look]. Codex renders it in the look's material (image 1 of the edit)."""
import os, sys
from PIL import Image, ImageDraw
H = os.path.dirname(os.path.abspath(__file__))
T = H + '/../../src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/'
L = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
JUNCTION = {"Scrapper": 47, "Industrial": 47, "Modern": 47, "Futuristic": 47}
TIP, V0, V1, K = 9, 114, 156, 8
out = sys.argv[1]
for look, sub in L.items():
    im = Image.open(T + sub + 'Reel_Deployed.png').convert('RGBA')
    px = im.load()
    j = JUNCTION[look]
    for x in range(0, j):
        for y in range(96, 176):
            px[x, y] = (0, 0, 0, 0)
    c = im.crop((0, 72, 128, 200)).resize((1024, 1024), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    x0, x1, y0, y1 = TIP * K, (j + 2) * K, (V0 - 72) * K, (V1 - 72) * K
    d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=(40, 40, 40, 255))
    d.rounded_rectangle((x0 + 12, y0 + 12, x1, y1 - 12), radius=10, fill=(150, 150, 150, 255))
    d.rectangle((x0 + 24, y0 + 40, x1, y0 + 80), fill=(205, 205, 205, 255))
    c.save(os.path.join(out, look + '_block.png'))
