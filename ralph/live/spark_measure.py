#!/usr/bin/env python3
"""Where is the spark in each frame, against the end's tip as the probe read it? Runs here on fetched frames, no game.

    python3 ralph/live/spark_measure.py SHOTS_DIR TAG LABEL

Finds the spark as the hot pixels nearest the probe's tip, makes a sheet and GIF, and prints the spark's own travel beside its distance from the tip.
A spark stuck on a laid point while the cable moves shows as a large distance. A spark riding the tip shows a distance well under its travel.
"""
import json, math, os, sys
from PIL import Image, ImageDraw

d, tag, label = sys.argv[1:4]
meta = json.load(open(os.path.join(d, "%s_%s.json" % (tag, label))))
x0, z0, w, h = meta["rect"]
out, frames, tips = [], [], []
for r in meta["rows"]:
    t = r["tip"]
    if t and isinstance(t[0], list):  # a fallen span reads every wire's end: the first
        t = t[0]
    im = Image.open(os.path.join(d, "%s_%s_%02d.png" % (tag, label, r["frame"]))).convert("RGB")
    W, H = im.size
    sx, sz = W / float(w), H / float(h)
    px, py = (t[0] - x0) * sx, H - (t[1] - z0) * sz
    best = []
    pix = im.load()
    R = int(1.3 * sx)
    for y in range(max(0, int(py) - R), min(H, int(py) + R)):
        for x in range(max(0, int(px) - R), min(W, int(px) + R)):
            a, b, c = pix[x, y]
            if a > 225 and b > 150 and c < 170:
                best.append((x, y))
    if best:
        # only the spark nearest the tip: the window can catch a neighbouring wire's spark
        nx, ny = min(best, key=lambda q: (q[0] - px) ** 2 + (q[1] - py) ** 2)
        best = [q for q in best if (q[0] - nx) ** 2 + (q[1] - ny) ** 2 <= (0.55 * sx) ** 2]
        cx, cy = sum(p[0] for p in best) / len(best), sum(p[1] for p in best) / len(best)
        wx, wz = x0 + cx / sx, z0 + (H - cy) / sz
        dist = math.hypot(wx - t[0], wz - t[1])
    else:
        wx = wz = dist = None
    out.append((r["frame"], r["t"], t, wx, wz, dist, len(best)))
    frames.append(im)
    tips.append((px, py))
seen = [o for o in out if o[3] is not None]
for o in out:
    print("frame %2d t=%5.2f tip=(%.2f,%.2f) spark=%s dist=%s hot=%d" % (o[0], o[1], o[2][0], o[2][1], "(%.2f,%.2f)" % (o[3], o[4]) if o[3] is not None else "none", "%.2f" % o[5] if o[5] is not None else "-", o[6]))
if seen:
    xs, zs = [o[3] for o in seen], [o[4] for o in seen]
    tx, tz = [o[2][0] for o in seen], [o[2][1] for o in seen]
    print("frames with a spark %d/%d; tip travel %.2f cell, spark travel %.2f cell, mean spark-to-tip %.2f, worst %.2f" % (
        len(seen), len(out), math.hypot(max(tx) - min(tx), max(tz) - min(tz)), math.hypot(max(xs) - min(xs), max(zs) - min(zs)),
        sum(o[5] for o in seen) / len(seen), max(o[5] for o in seen)))
cols = 4
rows = (len(frames) + cols - 1) // cols
W, H = frames[0].size
sheet = Image.new("RGB", (cols * W, rows * H))
for i, im in enumerate(frames):
    sheet.paste(im, ((i % cols) * W, (i // cols) * H))
    ImageDraw.Draw(sheet).text(((i % cols) * W + 6, (i // cols) * H + 4), "%d  t=%.2fs" % (i, out[i][1]), fill=(255, 255, 255))
sheet.save(os.path.join(d, "%s_%s_sheet.png" % (tag, label)))
frames[0].save(os.path.join(d, "%s_%s.gif" % (tag, label)), save_all=True, append_images=frames[1:], duration=250, loop=0)
