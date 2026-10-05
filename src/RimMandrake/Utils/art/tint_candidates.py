#!/usr/bin/env python3
"""Deterministic tint candidates for Blue Desert (owner sheet 2026-10-04): Murrek yellower (hydrocarbon blood),
Qeshra orange-yellow; Long Shade sheet: Dunejelly greener. Hue/saturation shift of the straight-alpha colour, luma preserved, alpha untouched, so the
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
    # owner, Stillsand sheet 2026-10-04: "Tint it towards grey please" -> hue None = keep each pixel's hue, pull
    # saturation toward grey (strength 0.6 = lose 60% of the saturation), luma preserved.
    "RM_ShadeMite": ("Things/Pawn/Animal/RM_ShadeMite/RM_ShadeMite",
                     {"east": "ae789ac5e4076c2e415db03ab7153c28a1ce7db6cffa066cb70f80488b9b139f",
                      "north": "9078c35b257ac0b34a6137557ab7c3f0b305d00486631cf499ab436b9d5324d9",
                      "south": "5ba66fa8e967f738aee8ce21e0e7821a940f4abdd99969e90a42132ea09d4cca"},
                     None, 0.0, 0.6),
    # owner, Long Shade sheet 2026-10-04: "Tint it more green. Rename to Dunejelly." The source is yellow (60-80 deg)
    # with orange (20-40 deg) accents, so two strengths of a hue PULL toward green (110 deg) — each pixel keeps its
    # own hue offset, rotated that fraction of the way — rather than flattening everything to one hue.
    "RM_Dunejelly": ("swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Jellypot/Jellypot",
                     {"east": "759aff4ab46d98b877125db29c9e2f3ab121399eadc02373201aba881a85ce2f",
                      "north": "515e5b7f39df8d90204f574fb3fdc06c2c1d728487ee754307b471fd289c40bc",
                      "south": "6032696606acb8a272112b5f908d4d849f56082fa7ce12bd48985d83fd101945"},
                     ("toward", 110 / 360, 0.5), 0.0, 1.0, "tint_v1"),
    "RM_Dunejelly#2": ("swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Jellypot/Jellypot",
                       {"east": "759aff4ab46d98b877125db29c9e2f3ab121399eadc02373201aba881a85ce2f",
                        "north": "515e5b7f39df8d90204f574fb3fdc06c2c1d728487ee754307b471fd289c40bc",
                        "south": "6032696606acb8a272112b5f908d4d849f56082fa7ce12bd48985d83fd101945"},
                       ("toward", 110 / 360, 0.85), 0.0, 1.0, "tint_v2"),
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
            if hue is None:  # desaturate toward grey, keep the pixel's own hue
                hh2 = hh; s = s * (1 - k)
            elif isinstance(hue, tuple):  # ("toward", target, frac): rotate the pixel's hue part-way, shortest arc
                d = ((hue[1] - hh + 0.5) % 1.0) - 0.5
                hh2 = (hh + d * hue[2]) % 1.0
            else:
                hh2 = hue
            nr, ng, nb = colorsys.hsv_to_rgb(hh2, s, v)
            y0, y1 = luma(rf, gf, bf), luma(nr, ng, nb)
            if y1 > 1e-4:
                f = y0 / y1; nr, ng, nb = min(1, nr * f), min(1, ng * f), min(1, nb * f)
            px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a)
    return im

def main():
    w = L.Writer(); out = []
    for key, (res, srcs, hue, ms, k, *tag) in JOBS.items():
        jid = key.split("#")[0]; tag = tag[0] if tag else "tint_v1"
        d = ART / f"{jid}_{tag}"; d.mkdir(parents=True, exist_ok=True)
        for fac, sha in srcs.items():
            im = tint(Image.open(io.BytesIO(L.store_get(sha))), hue, ms, k)
            buf = io.BytesIO(); im.save(buf, "PNG"); b = buf.getvalue()
            nsha = L.store_put_bytes(b)
            job = f"{jid}_{tag}" + (f"_{fac}" if fac else "")
            (d / f"{job}.png").write_bytes(b)
            ph, wd, ht = L.dhash(b)
            ev = {"type": "variant", "id": L.det_id("variant", "tint", nsha, job), "sha": nsha, "ph": ph, "w": wd, "h": ht,
                  "kind": "artpipe", "loc": f"_artsrc/{d.name}/{job}.png", "date": L.now(), "job": job,
                  "res": res, "facing": fac or "single", "mask": False,
                  "item": "BIOME_FLORAFAUNA_ART_REVIEW_1", "parent_sha": sha,
                  "prompt": (f"deterministic hue pull {hue[2]:.0%} toward {round(hue[1]*360)} deg, luma preserved (owner note 'Tint it more green', Long Shade sheet 2026-10-04)" if isinstance(hue, tuple) else
                             f"deterministic tint to hue {round(hue*360)} deg, luma preserved (owner note, BlueDesert sheet 2026-10-04)" if hue is not None else f"deterministic desaturation toward grey ({k:.0%}), luma preserved (owner note 'Tint it towards grey', Stillsand sheet 2026-10-04)")}
            w.add(ev); out.append((job, nsha[:12]))
    w.flush(); print(out)

main()
