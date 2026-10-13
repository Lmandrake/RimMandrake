"""TANK_TALL_BUILD_TWICE_THE_DRINK placeholder art: stack the RM_LiquidTank drum `layers`+1 high.
usage: mk_tall.py <RM_LiquidTank.png> <out.png> <layers>   (canvas 512 x (512+256*...)): layers=1 -> 512x768, drawSize (2,3)
A procedural derivative, NOT a painted tall tank -- real art is owed on the item."""
import sys
from PIL import Image
src, dst, layers = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(src).convert("RGBA")
H = 512
step = 256 // layers
tall = H + 256
c = Image.new("RGBA", (512, tall), (0, 0, 0, 0))
upper = im.crop((0, 0, 512, 410))
for i in range(layers, 0, -1):
    c.alpha_composite(upper, (0, (layers - i) * step))
c.alpha_composite(im, (0, tall - H))
c.save(dst)
print(c.size)
