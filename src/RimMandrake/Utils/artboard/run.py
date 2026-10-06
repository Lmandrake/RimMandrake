"""Segment one contact-board frame into per-subject crops, run tier (a), write the tier (b)/(c) inputs.

    cd src/RimMandrake/Utils && python3 -m artboard.run <board.json> --out <dir> [--ref-dir <dir>]

Board JSON (paths relative to the board file):
  image          the captured frame (PNG)
  plate          optional: the same frame shot BEFORE staging (exact foreground)
  camera | markers   cell->pixel mapping (see geometry.py)
  pad            ring width in cells around each subject (default 0.5)
  config         overrides for checks.DEFAULTS
  defaults       an 'expect' block merged under every subject's own
  subjects       [{id, cell:[x,z], size:[w,h]=1x1, overhang=0.15, expect:{colour, organic, may_be_empty,
                   may_overflow, holes_ok}, differs_from:[ids], ref: png, question: str, canon: path}]

Outputs in --out: crops/<id>.png, report.json, report.html, vision_mosaic.png + vision_key.json +
vision_prompt.md (only the crops that PASSED tier a), owner_board.png (only what was flagged).
Exit code: 0 always for a completed run; the verdict is in report.json, not in the exit code.
"""
import argparse
import html
import json
import os
import sys

import numpy as np
from PIL import Image

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from artboard import checks, geometry, mosaic  # noqa: E402
else:
    from . import checks, geometry, mosaic


def _p(base, p):
    return p if (p is None or os.path.isabs(p)) else os.path.join(base, p)


def segment(board, img, mapping, pad):
    """Yield (subject, crop_box, core_box_in_crop) for each subject; boxes are pixel (l,t,r,b)."""
    for s in board["subjects"]:
        x, z = s["cell"]
        w, h = s.get("size", [1, 1])
        ov = float(s.get("overhang", board.get("overhang", 0.15)))
        crop = mapping.cell_box(x, z, w, h, pad + ov)
        core = mapping.cell_box(x, z, w, h, ov)
        yield s, crop, (core[0] - crop[0], core[1] - crop[1], core[2] - crop[0], core[3] - crop[1])


def run(board_path, out, ref_dir=None):
    base = os.path.dirname(os.path.abspath(board_path))
    board = json.load(open(board_path))
    img = np.asarray(Image.open(_p(base, board["image"])).convert("RGB"))
    plate = board.get("plate")
    plate = np.asarray(Image.open(_p(base, plate)).convert("RGB")) if plate else None
    mapping = geometry.mapping_from_board(board)
    pad = float(board.get("pad", 0.5))
    cfg = dict(checks.DEFAULTS, **board.get("config", {}))
    os.makedirs(os.path.join(out, "crops"), exist_ok=True)
    os.makedirs(os.path.join(out, "core"), exist_ok=True)
    H, W = img.shape[:2]
    rows, cores = [], {}
    for s, (l, t, r, b), (cl, ct, cr, cb) in segment(board, img, mapping, pad):
        s = dict(s)
        s["expect"] = dict(board.get("defaults", {}), **s.get("expect", {}))
        row = {"id": s["id"], "label": s.get("label", s["id"]), "cell": s["cell"], "box": [l, t, r, b],
               "findings": [], "metrics": {}}
        rows.append(row)
        if l < 0 or t < 0 or r > W or b > H:
            row["findings"].append({"check": "OUT_OF_FRAME", "detail": "crop %s exceeds the %dx%d frame — "
                                    "camera or geometry is wrong" % ([l, t, r, b], W, H)})
            continue
        crop = img[t:b, l:r]
        core = np.zeros(crop.shape[:2], bool)
        core[ct:cb, cl:cr] = True
        f, m = checks.run_checks(crop, core, ~core, s, None if plate is None else plate[t:b, l:r],
                                 mapping.ppc, cfg)
        row["findings"] += f
        row["metrics"] = m
        Image.fromarray(crop).save(os.path.join(out, "crops", "%s.png" % s["id"]))
        cores[s["id"]] = crop[ct:cb, cl:cr]
        Image.fromarray(cores[s["id"]]).save(os.path.join(out, "core", "%s.png" % s["id"]))
        ref = _p(base, s.get("ref")) or (ref_dir and os.path.join(ref_dir, "%s.png" % s["id"]))
        if ref and os.path.exists(ref):
            d = checks.changed_share(cores[s["id"]], np.asarray(Image.open(ref).convert("RGB")),
                                     cfg["fg_threshold"])
            m["ref_changed"] = round(d, 3)
            if d > cfg["ref_max"]:
                row["findings"].append({"check": "REF_DRIFT", "detail": "%.0f%% of the cell changed vs the "
                                        "owner-approved reference %s" % (100 * d, os.path.basename(ref))})
        row["subject"] = s
    by_id = {r["id"]: r for r in rows}
    for r in rows:
        for other in r.get("subject", {}).get("differs_from", []):
            if r["id"] in cores and other in cores:
                d = checks.mean_abs_diff(cores[r["id"]], cores[other])
                r["metrics"].setdefault("diff_vs", {})[other] = round(d, 1)
                if d < cfg["identical_max"]:
                    r["findings"].append({"check": "IDENTICAL", "detail": "renders the same as %s (mean "
                                          "difference %.1f) though the two states must differ" % (other, d)})
            elif other not in by_id:
                r["findings"].append({"check": "BAD_BOARD", "detail": "differs_from names unknown id %s" % other})

    # tier (b): survivors go to ONE vision read; tier (c): flagged go to the owner board
    passed = [r for r in rows if not r["findings"]]
    flagged = [r for r in rows if r["findings"]]
    key, tiles = [], []
    for i, r in enumerate(passed, 1):
        lab = "#%d" % i
        q = r["subject"].get("question") or board.get("question") or "Does this look like %s?" % r["label"]
        key.append({"tile": lab, "id": r["id"], "label": r["label"], "question": q,
                    "canon": r["subject"].get("canon")})
        tiles.append((lab, Image.open(os.path.join(out, "crops", "%s.png" % r["id"])), [r["label"]]))
    layout = mosaic.build(tiles, os.path.join(out, "vision_mosaic.png"))
    json.dump({"tiles": key, "layout": layout}, open(os.path.join(out, "vision_key.json"), "w"), indent=1)
    with open(os.path.join(out, "vision_prompt.md"), "w") as fh:
        fh.write("Read vision_mosaic.png ONCE. For each tile answer its question with PASS, FAIL <why> or "
                 "UNSURE <why>. Judge only what the question asks; anything subjective is UNSURE, not FAIL.\n\n")
        for k in key:
            fh.write("- %s `%s` — %s%s\n" % (k["tile"], k["id"], k["question"],
                                            " (canon: %s)" % k["canon"] if k["canon"] else ""))
    otiles = []
    for r in flagged:
        cp = os.path.join(out, "crops", "%s.png" % r["id"])
        im = Image.open(cp) if os.path.exists(cp) else Image.new("RGB", (32, 32), (90, 0, 0))
        otiles.append(("!", im, [r["label"], ",".join(f["check"] for f in r["findings"])]))
    mosaic.build(otiles, os.path.join(out, "owner_board.png"))

    rep = {"board": os.path.abspath(board_path), "frame": [W, H], "mapping": mapping.to_json(),
           "fg_mode": "plate" if plate is not None else "ring", "subjects": len(rows),
           "passed_tier_a": len(passed), "flagged": len(flagged),
           "by_check": {}, "rows": [{k: v for k, v in r.items() if k != "subject"} for r in rows]}
    for r in flagged:
        for f in r["findings"]:
            rep["by_check"].setdefault(f["check"], []).append(r["id"])
    json.dump(rep, open(os.path.join(out, "report.json"), "w"), indent=1)
    _html(rep, out)
    return rep


def approve(out, ids, ref_dir):
    """Copy the core crops of owner-ACCEPTED subjects into ref_dir as the references later runs diff
    against. Call this only on an owner Accept (or an art-ledger ruling) — never on an agent's own pass."""
    import shutil
    os.makedirs(ref_dir, exist_ok=True)
    done = []
    for i in ids:
        src = os.path.join(out, "core", "%s.png" % i)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(ref_dir, "%s.png" % i))
            done.append(i)
    return done


def _html(rep, out):
    css = (":root{--bg:#2a211b;--fg:#efe4d4;--bad:#e2725b;--ok:#9cbf7a}body{background:var(--bg);color:var(--fg);"
           "font:14px system-ui;margin:16px}td,th{padding:4px 8px;border-bottom:1px solid #4a3a2e;vertical-align:top}"
           "img{image-rendering:pixelated;height:96px}.bad{color:var(--bad)}.ok{color:var(--ok)}")
    rows = []
    for r in rep["rows"]:
        st = "<span class=bad>%s</span>" % "<br>".join(html.escape("%s: %s" % (f["check"], f["detail"]))
                                                       for f in r["findings"]) if r["findings"] else \
            "<span class=ok>passed tier a</span>"
        rows.append("<tr><td><img src='crops/%s.png' alt=''></td><td>%s<br><small>%s</small></td><td>%s</td></tr>"
                    % (html.escape(r["id"]), html.escape(r["label"]), r["cell"], st))
    open(os.path.join(out, "report.html"), "w").write(
        "<!doctype html><meta charset=utf-8><title>Artboard report</title><style>%s</style>"
        "<h1>Artboard: %d subjects, %d flagged</h1><p>mapping %.1f px/cell, residual %.1f px, foreground by %s</p>"
        "<table>%s</table>" % (css, rep["subjects"], rep["flagged"], rep["mapping"]["ppc"],
                               rep["mapping"]["residual_px"], rep["fg_mode"], "".join(rows)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("board")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref-dir", help="approved reference crops, <id>.png")
    a = ap.parse_args(argv)
    rep = run(a.board, a.out, a.ref_dir)
    print("ARTBOARD %d subjects: %d passed tier a, %d flagged %s -> %s"
          % (rep["subjects"], rep["passed_tier_a"], rep["flagged"],
             {k: len(v) for k, v in rep["by_check"].items()}, os.path.join(a.out, "report.json")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
