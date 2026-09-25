import sys
from PIL import Image, ImageDraw

src = sys.argv[1]
dst = sys.argv[2]

im = Image.open(src).convert("RGB")
w, h = im.size
px = im.load()

# Step 1: classify each pixel as "checker-candidate" (near-neutral gray AND bright)
mask = Image.new("L", (w, h), 0)
mpx = mask.load()
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        near_neutral = abs(r - g) <= 6 and abs(g - b) <= 6 and abs(r - b) <= 6
        bright = min(r, g, b) >= 190
        if near_neutral and bright:
            mpx[x, y] = 255

# Step 2: flood-fill from every border pixel that is a checker-candidate,
# marking the CONNECTED region reachable from the edge (so an isolated bright
# highlight deep inside a wood ring, if it happens to be neutral-bright, is
# left alone unless it actually touches the border network).
seeds = []
for x in range(w):
    seeds.append((x, 0))
    seeds.append((x, h - 1))
for y in range(h):
    seeds.append((0, y))
    seeds.append((w - 1, y))

MARK = 254
for sx, sy in seeds:
    if mpx[sx, sy] == 255:
        ImageDraw.floodfill(mask, (sx, sy), MARK, thresh=0)

# Step 3: build alpha - transparent where MARK, opaque elsewhere
out = im.convert("RGBA")
opx = out.load()
transparent_count = 0
for y in range(h):
    for x in range(w):
        if mpx[x, y] == MARK:
            r, g, b, a = opx[x, y]
            opx[x, y] = (r, g, b, 0)
            transparent_count += 1

out.save(dst)
print("saved", dst, "size", out.size, "transparent px", transparent_count, "of", w * h)
