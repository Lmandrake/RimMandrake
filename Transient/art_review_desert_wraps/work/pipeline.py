#!/usr/bin/env python3
"""raw -> key -> achromatic -> conform -> validate, for every candidate."""
import subprocess, sys, json
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path("/mnt/d/Luke/dev/Rimworld")
W = ROOT / "Transient/art_review_desert_wraps"
GI = ROOT / "skills/generating-images/scripts"
GS = ROOT / "skills/generating-rimworld-sprites/scripts"

REF = {"wrap": W / "ref/ref_body_male_south_512.png",
       "head": W / "ref/ref_head_male_south_512.png"}


def achromatic(src: Path, dst: Path):
    """Force R=G=B using the GREEN channel as the value.

    Green is the one channel a magenta (#FF00FF) key cannot contaminate, so
    this both guarantees zero saturation and removes any surviving key spill
    at the alpha rim, in one step.
    """
    im = np.asarray(Image.open(src).convert("RGBA")).astype(np.uint8)
    g = im[..., 1]
    out = np.dstack([g, g, g, im[..., 3]])
    Image.fromarray(out, "RGBA").save(dst)


def hue_report(p: Path):
    im = np.asarray(Image.open(p).convert("RGBA")).astype(int)
    a = im[..., 3] > 0
    rgb = im[..., :3][a]
    mx, mn = rgb.max(1), rgb.min(1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0.0)
    return float(sat.max()), float(sat.mean()), int(a.sum())


def main(names):
    rows = []
    for n in names:
        kind = "wrap" if n.startswith("wrap") else "head"
        raw, cut, gry, fin = (W / f"raw/{n}.png", W / f"cut/{n}.png",
                              W / f"cut/{n}_gray.png", W / f"final/{n}.png")
        subprocess.run([sys.executable, str(GI / "chroma_key.py"),
                        "--input", str(raw), "--out", str(cut)], check=True,
                       capture_output=True)
        achromatic(cut, gry)
        subprocess.run([sys.executable, str(GS / "conform_sprite.py"),
                        "--reference", str(REF[kind]), "--input", str(gry),
                        "--out", str(fin)], check=True, capture_output=True)
        v = subprocess.run([sys.executable, str(GS / "validate_sprite.py"),
                            "--reference", str(REF[kind]), "--candidate", str(fin)],
                           capture_output=True, text=True)
        mx, mean, npx = hue_report(fin)
        verdict = "PASS" if v.returncode == 0 else "REJECT"
        rows.append((n, verdict, mx, mean))
        print(f"### {n}  [{verdict}]  maxsat={mx:.4f} meansat={mean:.4f} alphapx={npx}")
        print(v.stdout.strip() or v.stderr.strip())
        print()
    print("SUMMARY")
    for n, verdict, mx, mean in rows:
        print(f"  {n:22s} {verdict:7s} maxsat={mx:.4f}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["wrap_A_bound", "wrap_B_coil", "wrap_C_cowl",
                          "wrap_D_weathered", "head_H1_pot", "head_H2_browridge"])
