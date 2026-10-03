#!/usr/bin/env python3
"""Wire the artpipe Messy Conduit art families into the mod's Textures (lane C, 2026-10-02).

Source: D:\\Luke\\dev\\_artpipe\\_artsrc\\<job id>\\<job id>.png (finished jobs; item MESSY_CONDUIT_MOD_1).
Destination: src/RimMandrake/MessyConduit/Textures/RimMandrake/MessyConduit/...

Naming scheme (one folder per family, slot names fixed so CordMaterials maps slot -> file):
  Styles/<Family>/Strand[_<Variant>].png   128x32, tiles along u
  Styles/<Family>/Junction_T.png           128x128 (the Jawa set's Junction_Tape slot)
  Styles/<Family>/Junction_X.png           128x128 (the Jawa set's Junction_Tin slot)
  Styles/<Family>/Plug.png StubWall.png StubRock.png   128x128
  Styles/<Family>/EndFrayed_Dead.png       64x64
The Jawa default set stays where phase 1a put it (the folder root), so nothing that names those paths moves.
Slots a family has no art for (EndFrayed_Live, PowerStrip, StrandShadow) fall back to the Jawa root piece.

Per piece: RGBA with real transparency, exact canvas, strips cropped to the cord rows (+1 px) and stretched
back to the canvas (the Jawa recipe, belt_art_wiring3), seam test edge-column diff vs adjacent-column diff;
a failing seam gets one wrap crossfade and is re-tested; still failing -> placeholder kept (reported).
T junctions are shifted vertically so their side arms sit on the Jawa anchor row (CordBuilder.TapeAnchorZ).

Usage: python3 wire_style_art.py [--dry]   prints one line per piece and a JSON report to --report.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image

SRC = "/mnt/d/Luke/dev/_artpipe/_artsrc"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
TEX = os.path.join(REPO, "src/RimMandrake/MessyConduit/Textures/RimMandrake/MessyConduit")
J = "RM_MessyConduit_"

# (job id, dest relative to TEX, kind, canvas)
PIECES = []
def fam(family, strands, t, x, plug, wall, rock, fray):
    for job, name in strands:
        PIECES.append((J + job, f"Styles/{family}/{name}.png", "strip", (128, 32)))
    for job, name, size in ((t, "Junction_T", 128), (x, "Junction_X", 128), (plug, "Plug", 128),
                            (wall, "StubWall", 128), (rock, "StubRock", 128), (fray, "EndFrayed_Dead", 64)):
        PIECES.append((J + job, f"Styles/{family}/{name}.png", "tjunction" if name == "Junction_T" else "decal", (size, size)))

fam("Cybertek", [("Cybertek_Strand", "Strand")], "Cybertek_Node_T", "Cybertek_Node_X", "Cybertek_Plug_Casing",
    "Cybertek_Stub_Wall", "Cybertek_Stub_Rock", "Cybertek_Decal_FrayedEndDead_v2")
fam("ExtCord", [("ExtCord_Strand_" + c, "Strand_" + c) for c in ("Orange", "Green", "Brown", "Yellow", "Blue")],
    "ExtCord_Node_T_v2", "ExtCord_Node_X", "ExtCord_Plug_Casing", "ExtCord_Stub_Wall", "ExtCord_Stub_Rock",
    "ExtCord_Decal_FrayedEndDead")
fam("StarWars", [("StarWars_Strand_" + v, "Strand_" + v) for v in ("BlackRubber", "CorrugatedSteel", "CoiledBlack")],
    "StarWars_Node_T", "StarWars_Node_X", "StarWars_Plug_Casing", "StarWars_Stub_Wall", "StarWars_Stub_Rock",
    "StarWars_Decal_FrayedEndDead")
PIECES += [
    (J + "Shared_SparkGlow", "SparkGlow.png", "decal", (64, 64)),
    (J + "Aerial_Pole_Side", "Aerial/AerialMast.png", "decal", (128, 256)),
    (J + "Aerial_Pole_Side", "Aerial/AerialMastTop.png", "masttop", (128, 128)),
    (J + "Aerial_Hanger_Bracket", "Aerial/WallBracket.png", "upscale", (128, 128)),
    (J + "Aerial_Strand_WireShadow", "Aerial/SpanShadow.png", "strip", (128, 32)),
    (J + "Aerial_Strand_Wire", "Aerial/SpanWire.png", "strip", (128, 32)),
    (J + "Aerial_Insulator", "Aerial/Insulator.png", "decal", (64, 64)),
    (J + "Aerial_Pole_Top", "Aerial/PoleTopDown.png", "decal", (128, 128)),
    (J + "Hose_Strand_Flat_v2", "Hose/Strand_Flat.png", "strip", (256, 64)),
    (J + "Hose_Strand_Plump_v2", "Hose/Strand_Plump.png", "strip", (256, 64)),
    (J + "Hose_Strand_Shadow", "Hose/Strand_Shadow.png", "strip", (256, 64)),
    (J + "Hose_Coupling_Brass_v2", "Hose/Coupling_Brass.png", "decal", (128, 128)),
    (J + "Hose_Nozzle_v2", "Hose/Nozzle.png", "decal", (128, 128)),
    (J + "Hose_Reel_PumpHookup_v2", "Hose/Reel_PumpHookup.png", "decal", (128, 128)),
    (J + "Hose_EndCap_v2", "Hose/EndCap.png", "decal", (128, 128)),
]

JAWA_T_ARM_Z = 0.141          # measured on the shipped Jawa Junction_Tape at column 12 (same instrument below)


def seam(a):
    """(edge diff, mean adjacent-column diff) over premultiplied RGBA."""
    f = a.astype(np.float32)
    p = np.concatenate([f[:, :, :3] * (f[:, :, 3:4] / 255.0), f[:, :, 3:4]], axis=2)
    edge = np.abs(p[:, 0] - p[:, -1]).mean()
    adj = np.abs(np.diff(p, axis=1)).mean()
    return float(edge), float(adj)


def seam_ok(a):
    e, adj = seam(a)
    return e <= max(1.5 * adj, adj + 4.0), e, adj


def crossfade(a, k=16):
    """Wrap crossfade: drop the first k columns, blend them into the last k (continuous across the wrap)."""
    f = a.astype(np.float32)
    w = f.shape[1]
    out = f[:, k:].copy()
    n = out.shape[1]
    for i in range(k):
        t = (i + 1) / (k + 1)
        out[:, n - k + i] = (1 - t) * f[:, w - k + i] + t * f[:, i]
    return np.clip(out, 0, 255).astype(np.uint8)


def crop_rows(a, thr=16):
    rows = np.where(a[:, :, 3].max(axis=1) > thr)[0]
    lo, hi = max(0, rows.min() - 1), min(a.shape[0], rows.max() + 2)
    return a[lo:hi]


def t_arm_z(a, col=12):
    idx = np.where(a[:, col, 3] > 64)[0]
    if len(idx) == 0:
        return None
    return (a.shape[0] / 2 - (idx.min() + idx.max()) / 2) / a.shape[0]


def process(job, kind, canvas):
    p = os.path.join(SRC, job, job + ".png")
    if not os.path.exists(p):
        return None, {"fail": "missing source " + p}
    im = Image.open(p).convert("RGBA")
    a = np.array(im)
    info = {"src_size": list(im.size)}
    al = a[:, :, 3]
    info["alpha_transparent_frac"] = round(float((al < 8).mean()), 3)
    if (al < 8).mean() < 0.02:
        return None, dict(info, fail="no real transparency")
    if (al > 0).sum() == 0:
        return None, dict(info, fail="empty")
    if kind == "strip":
        c = crop_rows(a)
        info["cord_rows"] = int(c.shape[0])
        out = np.array(Image.fromarray(c).resize(canvas, Image.LANCZOS))
        ok, e, adj = seam_ok(out)
        info["seam"] = [round(e, 2), round(adj, 2)]
        if not ok:
            out2 = np.array(Image.fromarray(crossfade(c)).resize(canvas, Image.LANCZOS))
            ok, e, adj = seam_ok(out2)
            info["seam_after_crossfade"] = [round(e, 2), round(adj, 2)]
            if not ok:
                return None, dict(info, fail="seam")
            out = out2
        return Image.fromarray(out), info
    if im.size != canvas and kind not in ("masttop", "upscale"):
        return None, dict(info, fail=f"canvas {im.size} != {canvas}")
    if kind == "tjunction":
        z = t_arm_z(a)
        shift = int(round((JAWA_T_ARM_Z - z) * a.shape[0])) if z is not None else 0
        info["arm_z"] = round(z, 3) if z is not None else None
        info["shift_up_px"] = shift
        if shift:
            out = np.zeros_like(a)
            if shift > 0:
                out[:-shift] = a[shift:]
            else:
                out[-shift:] = a[:shift]
            a = out
        return Image.fromarray(a), info
    if kind == "masttop":
        return Image.fromarray(a[:128]), info
    if kind == "upscale":
        return im.resize(canvas, Image.LANCZOS), info
    return im, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--report", default=os.path.join(REPO, "Transient/messy_conduit_live_20261002/art_families_report.json"))
    args = ap.parse_args()
    rep = []
    for job, dest, kind, canvas in PIECES:
        img, info = process(job, kind, canvas)
        row = dict(job=job, dest=dest, kind=kind, canvas=list(canvas), **info)
        if img is not None:
            assert img.size == tuple(canvas), (dest, img.size)
            row["wired"] = True
            if not args.dry:
                d = os.path.join(TEX, dest)
                os.makedirs(os.path.dirname(d), exist_ok=True)
                img.save(d)
        else:
            row["wired"] = False
        rep.append(row)
        print(("WIRED " if row["wired"] else "KEPT  ") + dest, json.dumps({k: v for k, v in info.items()}))
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    json.dump(rep, open(args.report, "w"), indent=1)
    print(f"{sum(r['wired'] for r in rep)}/{len(rep)} wired; report {args.report}")


if __name__ == "__main__":
    sys.exit(main())
