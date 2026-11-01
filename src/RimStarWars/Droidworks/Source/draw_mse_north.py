"""MSE_north - the back of the MSE-6 repair droid.

The bundle (Outer Rim - Droid Depot) ships only MSE_south and MSE_east while the
def declares Graphic_Multi, so a north-facing droid silently falls back and shows
its FRONT while walking away. Measured facts, all from the extracted bundle art:
  * canvas 256x256, south bbox (97, 80, 159, 178)
  * black keyline, 3 px
  * upper plate 231, lower panel 178, vent seam 96, panel joints 148

The silhouette and keyline are taken PIXEL-FOR-PIXEL from MSE_south, so the north
registers perfectly by construction. Only the interior is re-authored: the front
bevel is replaced by a plain rear panel with a vent seam and two panel joints,
which is what the back of a box droid should read as.
"""
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGBA")
px = im.load()
W, H = im.size
X0, Y0, X1, Y1 = im.getchannel("A").getbbox()

TOP, LOW, SEAM, JOINT = 231, 178, 96, 148
split = Y0 + int((Y1 - Y0) * 0.55)          # where the top plate meets the rear panel

for y in range(H):
    for x in range(W):
        r, g, b, a = px[x, y]
        if a < 40 or r < 40:                 # transparent, or the keyline: leave alone
            continue
        if y < split:
            v = TOP
        elif y < split + 4:
            v = SEAM                          # horizontal vent seam
        else:
            v = LOW
        px[x, y] = (v, v, v, a)

# two vertical panel joints on the rear panel, and a shallow lip under the top edge
for y in range(split + 5, Y1):
    for x in (X0 + 20, X1 - 21):
        if px[x, y][3] > 40 and px[x, y][0] > 40:
            px[x, y] = (JOINT, JOINT, JOINT, px[x, y][3])
for x in range(X0, X1):
    for y in (Y0 + 6, Y0 + 7):
        if px[x, y][3] > 40 and px[x, y][0] > 40:
            px[x, y] = (255, 255, 255, px[x, y][3])

im.save(dst)
a = im.getchannel("A")
print("bbox", a.getbbox(), "alphaMax", max(a.get_flattened_data()))
