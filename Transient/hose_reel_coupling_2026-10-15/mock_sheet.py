"""mock_sheet.py -- one picture: per look, the laid reel with its hose joined (mock.py geometry), old | A | B, at 2x."""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
H = os.path.dirname(os.path.abspath(__file__))
T = H + "/../../src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/"
SUB = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
out = sys.argv[1]
tiles = []
with tempfile.TemporaryDirectory() as td:
    for look, sub in SUB.items():
        row = []
        for lab, src in (("current", T + sub + "Reel_Deployed.png"), ("A", f"{H}/cand/{look}_A_Deployed.png"),
                         ("B", f"{H}/cand/{look}_B_Deployed.png")):
            p = os.path.join(td, f"{look}_{lab}.png")
            subprocess.run([sys.executable, H + "/mock.py", src, look, p], check=True)
            im = Image.open(p).convert("RGBA").crop((300, 120, 972, 560))
            ImageDraw.Draw(im).text((8, 6), f"{look} - {lab}", fill=(255, 255, 255, 255))
            row.append(im)
        tiles.append(row)
w, h = tiles[0][0].size
S = Image.new("RGBA", (3 * w + 8, 4 * h + 12), (40, 30, 20, 255))
for j, row in enumerate(tiles):
    for i, im in enumerate(row):
        S.alpha_composite(im, (i * (w + 4), j * (h + 4)))
S.save(out)
print(out, S.size)
