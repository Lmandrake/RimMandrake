#!/usr/bin/env python3
"""facing_view_fit.py — fit NEW south/north facings to an installed east before a judge sees them.

    python3 facing_view_fit.py fit --east E.png [--south S.png] [--north N.png] --new north [--plan P] --out DIR
    python3 facing_view_fit.py check-driver [--drv PATH]     exit 0: the facing driver's norm_view calls fit_new_views

The facing-audit redraw driver (drv.py, under the agent storage root, facing_backlog_20261026/batch) once scaled
every new N/S that stood more than 5% taller than east down to east's HEIGHT. For a long, low body drawn from a
high camera (Dragonsnake) a correct rear view then shrank by 0.2-0.26 (width .12-.16 of the canvas), and the judge
scored the shrunken picture, not the drawing. 26 of that batch's 60 view subjects shrank below 0.65.

THE RULE. facing_scale_lint is the one judge of facing size. A new facing is changed only when the lint flags it too
tall AND names a pure-scale fix (action rescale, factor >= facing_scale_lint.MIN_SHRINK): it gets the lint's own
rescale. A facing whose fix is `regenerate` (the proportions are wrong, not the scale: a high-angle drawing) is passed
on RAW, with the lint's reason in the report, so the judge sees and scores the real drawing. A facing that the lint
does not flag is passed on unchanged. No facing is ever enlarged here, and no facing shrinks below MIN_SHRINK.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facing_scale_lint as L  # noqa: E402

DRV_REL = "rimmandrake/facing_backlog_20261026/batch/drv.py"
DRV_HOST = "mandrake@archmagi-wsl"          # the machine whose agent storage holds the facing batch


def _plan(kind: str | None) -> str | None:
    if not kind:
        return None
    try:
        p, _ = L.kind_plan(kind)
    except Exception:                    # no DefDump or body: the lint's unclassified convention
        return None
    return None if p in (None, "UNCLASSIFIED") else p


def fit_new_views(imgs: dict, new: list, out_dir, kind: str | None = None, plan: str | None = None,
                  view: str = "elevation") -> tuple[dict, dict]:
    """imgs: facing -> png path (installed + new); new: the facings drawn this round. Writes each new facing to
    out_dir/<facing>.png (rescaled or a raw copy). -> (imgs with the new facings pointed at out_dir, report).
    report: heights_before (px), scaled {facing: factor}, kept_raw {facing: why}, flags (the lint's)."""
    from PIL import Image
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan = plan if plan is not None else _plan(kind)
    m = {f: L.measure_file(p) for f, p in imgs.items() if f in L.FACES}
    m = {f: v for f, v in m.items() if v}
    rep = {"heights_before": {f: round(v["h"] * v["H"]) for f, v in m.items()}, "plan": plan, "view": view,
           "scaled": {}, "kept_raw": {}, "flags": []}
    out = dict(imgs)
    j = L.judge(m, L.load_cal(), view, plan) if "east" in m and ({"south", "north"} & set(m)) else None
    if j:
        rep["flags"] = [{k: x[k] for k in ("facing", "key", "value", "band")} for x in j["flags"]]
    for f in new:
        if f not in imgs:
            continue
        o = out_dir / f"{f}.png"
        fx = (j or {}).get("fixes", {}).get(f) if f in m else None
        if fx and fx["action"] == "rescale" and fx["scale"] < 1:
            with Image.open(imgs[f]) as im:
                L.rescale(im, fx["scale"], m["east"]).save(o)
            rep["scaled"][f] = round(fx["scale"], 3)
        else:
            shutil.copyfile(imgs[f], o)
            if fx:
                rep["kept_raw"][f] = f"{fx['action']} x{fx['scale']}: {fx['why']}"
        out[f] = str(o)
    return out, rep


# ─────────────────────────────────────────────────────────── driver check ──

def _storage_root() -> Path | None:
    h = Path.home() / "dev/Lodestar/bin/lib/agent_storage.py"
    try:
        r = subprocess.run([sys.executable, str(h)], capture_output=True, text=True, timeout=30)
        return Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def read_driver(path: str | None) -> tuple[str | None, str]:
    """(text, where) of drv.py: --drv, ARTEVAL_FACING_DRV, the local storage root, else the batch host over ssh."""
    for p in (path, os.environ.get("ARTEVAL_FACING_DRV")):
        if p:
            return (Path(p).read_text(), p) if Path(p).is_file() else (None, f"{p} is not a file")
    root = _storage_root()
    if root and (root / DRV_REL).is_file():
        return (root / DRV_REL).read_text(), str(root / DRV_REL)
    remote = f"/mnt/d/ClaudeWork/{DRV_REL}"
    try:   # deadline: a hang guard for an unreachable host, far above a real read (about 1 s)
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", DRV_HOST, "cat", remote],
                           capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"ssh {DRV_HOST}: {e}"
    return (r.stdout, f"{DRV_HOST}:{remote}") if r.returncode == 0 and r.stdout else (None, f"ssh {DRV_HOST}: rc={r.returncode} {r.stderr.strip()[:200]}")


def driver_delegates(text: str) -> tuple[bool, str]:
    """True when drv.py's norm_view body calls fit_new_views and carries no private east-height target of its own."""
    mt = re.search(r"^def norm_view\(.*?(?=^def |\Z)", text, re.S | re.M)
    if not mt:
        return False, "drv.py has no norm_view"
    body = mt.group(0)
    if "fit_new_views" not in body:
        return False, "norm_view does not call facing_view_fit.fit_new_views"
    if re.search(r"hts\[['\"]east['\"]\]|target\s*/\s*hts", body):
        return False, "norm_view still computes its own east-height target"
    return True, "norm_view delegates to facing_view_fit.fit_new_views"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit")
    for x in ("east", "south", "north"):
        f.add_argument(f"--{x}")
    f.add_argument("--new", nargs="+", required=True)
    f.add_argument("--plan")
    f.add_argument("--kind")
    f.add_argument("--out", required=True)
    c = sub.add_parser("check-driver")
    c.add_argument("--drv")
    a = ap.parse_args(argv)
    if a.cmd == "fit":
        imgs = {x: getattr(a, x) for x in ("east", "south", "north") if getattr(a, x)}
        _, rep = fit_new_views(imgs, a.new, a.out, kind=a.kind, plan=a.plan)
        print(json.dumps(rep, indent=1))
        return 0
    text, where = read_driver(a.drv)
    if text is None:
        print(f"COULD NOT LOOK: {where}")
        return 2
    ok, why = driver_delegates(text)
    print(("OK " if ok else "NOT FIXED ") + f"{where}: {why}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
