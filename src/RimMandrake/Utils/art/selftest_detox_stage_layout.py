#!/usr/bin/env python3
"""DetoxWorks stages are one plant (DETOX_WORKS_REDRAW_SAME_PLANT_EACH_STAGE).

Repaired is the master (its texture also serves RM_FilterWorks and
RM_VexxithFilterWorks) and must stay the same picture; Kludged and Wrecked are
condition-only redraws of it. Checks: Repaired unchanged, the other two
replaced, their alpha silhouettes overlap Repaired's (IoU; the old art scored
0.765 Kludged / 0.563 Wrecked), and the committed naive-judge verdict passes
both stages on the very pictures now installed. Exit 0 pass, 1 fail.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
TEX = ROOT / "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Machinery"
VERDICT = ROOT / "infrastructure/state/art/detox_stage_layout_verdict.json"

REPAIRED_SHA = "2f136f92a801"          # master, must not change
OLD = {"Kludged": "0a95bb06543c", "Wrecked": "c3362bbfe69a"}  # the mismatched layouts
MIN_IOU = {"Kludged": 0.85, "Wrecked": 0.75}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mask(p: Path) -> np.ndarray:
    im = Image.open(p).convert("RGBA")
    if im.size != (768, 768):
        raise SystemExit(f"FAIL {p.name}: canvas {im.size}, want (768, 768)")
    return np.array(im)[:, :, 3] > 128


def main() -> int:
    fails = []
    rep = TEX / "RM_DetoxWorks_Repaired.png"
    if not sha(rep).startswith(REPAIRED_SHA):
        fails.append(f"Repaired changed: {sha(rep)[:12]} != {REPAIRED_SHA}")
    r = mask(rep)
    verdict = json.loads(VERDICT.read_text())
    for stage, floor in MIN_IOU.items():
        p = TEX / f"RM_DetoxWorks_{stage}.png"
        h = sha(p)
        if h.startswith(OLD[stage]):
            fails.append(f"{stage} is still the old layout {OLD[stage]}")
        m = mask(p)
        iou = float((r & m).sum() / (r | m).sum())
        ok = iou >= floor
        print(f"{stage}: IoU vs Repaired {iou:.3f} (floor {floor}) {'ok' if ok else 'LOW'}")
        if not ok:
            fails.append(f"{stage} IoU {iou:.3f} < {floor}")
        name = f"RM_DetoxWorks_{stage}"
        if verdict["candidates"].get(name) != h:
            fails.append(f"{stage}: verdict judged {verdict['candidates'].get(name, '?')[:12]}, installed {h[:12]}")
        v = verdict["stages"].get(name, {})
        need = ("same_tank_layout", "same_silhouette", "condition_only")
        if v.get("verdict") != "PASS" or not all(v.get(k) is True for k in need):
            fails.append(f"{stage}: judge verdict not a full PASS: {v}")
    if not str(verdict["master"].get("RM_DetoxWorks_Repaired", "")).startswith(REPAIRED_SHA):
        fails.append("verdict judged a different Repaired master")
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
