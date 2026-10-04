#!/usr/bin/env python3
"""Deterministic tint candidates for Blue Desert (owner sheet 2026-10-04): Murrek yellower (hydrocarbon blood),
Qeshra orange-yellow. Hue/saturation shift of the straight-alpha colour, luma preserved, alpha untouched, so the
keyline and value structure survive. Registered as kind=artpipe variants (job <Id>_tint_v1[_facing]) bound to the
slot's res; NOT installed. Re-runnable: ids are deterministic and the store is content-addressed."""
import colorsys, io, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
import artledger as L

ART = Path("/mnt/d/Luke/dev/_artpipe/_artsrc")
JOBS = {  # id: (res, {facing|None: source sha}, target hue 0-1, min sat, hue-pull strength)
    "RM_Murrek": ("Things/Pawn/Animal/RM_Murrek/RM_Murrek",
                  {"east": "c3d820ad4aa34a2335c2160a746aef459aafd365805dab6c883bc5f8d916e263",
                   "north": "06fbf592fefbf142f7361a7c4bd1a3e149e5ebbecde300923bad030047fa946d",
                   "south": "159fe4a3402609050dbd5d37c14beb7fb9a94a0199ef1ad1da346cb6a45ab8cb"},
                  52 / 360, 0.17, 1.0),
    "RM_Qeshra": ("Things/Plant/RM_Qeshra/RM_Qeshra",
                  {None: "537d854c068db37f83ac4756a1abb71142460b322e8d4b6d5431b7a665bd0086"},
                  34 / 360, 0.0, 1.0),
}

def luma(r, g, b): return 0.299 * r + 0.587 * g + 0.114 * b

def tint(im, hue, min_sat, k):
    im = im.convert("RGBA"); px = im.load(); w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0: continue
            rf, gf, bf = r / 255, g / 255, b / 255
            hh, s, v = colorsys.rgb_to_hsv(rf, gf, bf)
            if min_sat:  # grey source: lift saturation, less in the darkest keyline pixels
                s = s + (max(s, min_sat * min(1, v * 1.6)) - s) * k
            hh2 = hue
            nr, ng, nb = colorsys.hsv_to_rgb(hh2, s, v)
            y0, y1 = luma(rf, gf, bf), luma(nr, ng, nb)
            if y1 > 1e-4:
                f = y0 / y1; nr, ng, nb = min(1, nr * f), min(1, ng * f), min(1, nb * f)
            px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a)
    return im

def main():
    w = L.Writer(); out = []
    for jid, (res, srcs, hue, ms, k) in JOBS.items():
        d = ART / f"{jid}_tint_v1"; d.mkdir(parents=True, exist_ok=True)
        for fac, sha in srcs.items():
            im = tint(Image.open(io.BytesIO(L.store_get(sha))), hue, ms, k)
            buf = io.BytesIO(); im.save(buf, "PNG"); b = buf.getvalue()
            nsha = L.store_put_bytes(b)
            job = f"{jid}_tint_v1" + (f"_{fac}" if fac else "")
            (d / f"{job}.png").write_bytes(b)
            ph, wd, ht = L.dhash(b)
            ev = {"type": "variant", "id": L.det_id("variant", "tint", nsha, job), "sha": nsha, "ph": ph, "w": wd, "h": ht,
                  "kind": "artpipe", "loc": f"_artsrc/{d.name}/{job}.png", "date": L.now(), "job": job,
                  "res": res, "facing": fac or "single", "mask": False,
                  "item": "BIOME_FLORAFAUNA_ART_REVIEW_1", "parent_sha": sha,
                  "prompt": f"deterministic tint to hue {round(hue*360)} deg, luma preserved (owner note, BlueDesert sheet 2026-10-04)"}
            w.add(ev); out.append((job, nsha[:12]))
    w.flush(); print(out)

main()
