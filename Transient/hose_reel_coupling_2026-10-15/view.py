"""view.py <look> <out.png> -- 4x crops of the coupling: original | A | B (Deployed top row, stored bottom row)."""
import sys, os
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__))
T = H + '/../../src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/'
L = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
look, out = sys.argv[1], sys.argv[2]
W = Image.new('RGBA', (3 * 384, 2 * 384), (150, 120, 90, 255))
for j, st in enumerate(['Deployed', 'PumpHookup']):
    srcs = [T + L[look] + 'Reel_' + st + '.png'] + [H + f'/cand/{look}_{c}_{st}.png' for c in 'AB']
    for i, s in enumerate(srcs):
        if os.path.exists(s):
            W.alpha_composite(Image.open(s).convert('RGBA').crop((0, 88, 96, 184)).resize((384, 384), Image.NEAREST), (i * 384, j * 384))
W.save(out)
