"""Finish one render into the 512 px sprite: finish.py <raw.png> <out.png> [scale, default 1]. Area downscale (premultiplied), faint-alpha
dust removed, then a whole-pixel shift so the E/W port centre sits on y=256 and the N/S port centre on x=256."""
import sys
import numpy as np
from PIL import Image
a = np.array(Image.open(sys.argv[1]).convert("RGBA")).astype(np.float64)
a[..., 3][a[..., 3] < 24] = 0
p = a.copy(); p[..., :3] *= a[..., 3:] / 255
n = a.shape[0]; assert a.shape[:2] == (n, n) and n % 512 == 0, a.shape
k = n // 512
p = p.reshape(512, k, 512, k, 4).mean((1, 3))
sc = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
if sc != 1.0:
    m = int(round(512 * sc / 2)) * 2
    q = np.stack([np.array(Image.fromarray(p[..., c].astype(np.float32)).resize((m, m), Image.BOX)) for c in range(4)], -1)
    p = np.zeros((512, 512, 4)); g = (512 - m) // 2; p[g:g + m, g:g + m] = q
al = p[..., 3:]
rgb = np.where(al > 0, p[..., :3] * 255 / np.maximum(al, 1e-6), 0)
o = np.concatenate([rgb, al], -1)
o[o[..., 3] < 32] = 0
s = o[..., 3] > 128
def mid(b):
    w = np.where(b)[0]; return (w.min() + w.max() + 1) / 2
dx = int(round(256 - (mid(s[:60].any(0)) + mid(s[-60:].any(0))) / 2))
dy = int(round(256 - (mid(s[:, :50].any(1)) + mid(s[:, -50:].any(1))) / 2))
o = np.roll(o, (dy, dx), (0, 1))
print("shift", dx, dy)
Image.fromarray(np.clip(np.rint(o), 0, 255).astype(np.uint8), "RGBA").save(sys.argv[2])
