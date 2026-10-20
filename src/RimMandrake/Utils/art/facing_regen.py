#!/usr/bin/env python3
"""facing_regen.py — redraw a creature's S/N facing to match its approved EAST view (ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL).

The east (side) view is the anchor and is never touched. A regenerate-class facing (facing_scale_lint.py could not
fix it by rescaling, because the picture is a top-down view or the wrong surface) is redrawn by Codex from
[east, south] as a ground-camera rear (north) or front (south) view, then CONFORMED: cropped to its visible
silhouette (alpha >= 16), scaled so its height is the lint's target x east height, and placed on the old facing's
canvas with the EAST view's feet row and the canvas centre (a deliberate >5% offset is kept). Nothing is installed: candidates land in --out and are judged by
facing_scale_lint.judge() exactly as `lint` would judge them in place.

    facing_regen.py gen     --row <texPath suffix> --facing north --out DIR [--rows after2.json]
    facing_regen.py conform --row <texPath suffix> --facing north --out DIR
    facing_regen.py lint    --row <texPath suffix> --out DIR
"""
from __future__ import annotations

import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import facing_scale_lint as L  # noqa: E402

DEFAULT_ROWS = REPO / "Transient/facing_rescale_2026-10-16/after2.json"
CODEX = REPO / "skills/generating-images/scripts/codex_image.py"
MODEL = os.environ.get("CODEX_MODEL", "gpt-5.6-sol")      # what rm-artpiped runs; codex_image's gpt-5.5 default 400s on ChatGPT auth
CODEX_HOME = os.environ.get("FACING_REGEN_CODEX_HOME", rm_str("scratch", "codex_home_facing_regen"))   # own home (one per parallel worker): never harvest the daemon's renders

SURFACE = {
    "north": ("REAR view", "seen from directly behind: its back, hindquarters, tail base and the backs of its legs "
              "face the viewer; no face, no eyes, no mouth visible"),
    "south": ("FRONT view", "seen from directly in front: face, eyes and chest toward the viewer"),
}

PROMPT = """Image 1 is the APPROVED side view (profile) of a creature sprite for the game RimWorld. Image 2 is the same creature's {img2} view.
Draw the {label} of exactly this creature: {surface}.
CAMERA: a low, ground-level camera at the creature's own eye height, the same camera height as image 2. The camera is NOT overhead: do not draw a top-down view, do not show the length of its back from above, do not stretch the body or tail up the picture. The body recedes AWAY from the viewer and is foreshortened, so the creature is about as tall and as wide as it is in image 2. A tail points straight toward the viewer, foreshortened, not swung out to the side.{extra}
STYLE: the same species, anatomy, proportions, palette, colour pattern, materials, line weight and painterly rendering as images 1 and 2 — it must read as the same individual from another side.
One creature, centred, whole body visible, {pose}. Fully transparent background, no ground, no shadow, no text, no border."""


def rows_by_tex(rows_path: Path) -> dict:
    out = {}
    for r in json.loads(rows_path.read_text()):
        out.setdefault(r["texPath"], r)
    return out


def find_row(rows_path: Path, suffix: str) -> dict:
    hits = [r for t, r in rows_by_tex(rows_path).items() if t.endswith(suffix)]
    if len(hits) != 1:
        sys.exit(f"--row {suffix!r} matches {len(hits)} texPaths")
    return hits[0]


# Basenames shared by several texPaths (colour variants / sibling mods). The two rows that already own the plain
# slug (installed, state + workdirs keyed on it) keep it UNCHANGED; every other row of that basename gets a short
# hash of its full texPath so job ids, WORK dirs and candidates/<slug> never collide.
SHARED_BASENAMES = {"jewelbug", "smogapillar"}
PLAIN_SLUG_OWNERS = {
    "rm_lanterndeeps/fauna/bmt_caverns/things/animal/gembug/red/jewelbug",
    "rm_therot/fauna/bmt_pollutedlands/things/animal/smogmoth/smogapillar",
}


def slug(row) -> str:
    base = row["texPath"].split("/")[-1]
    low = row["texPath"].lower()
    if base.lower() in SHARED_BASENAMES and low not in PLAIN_SLUG_OWNERS:
        return f"{base}_{hashlib.sha1(low.encode()).hexdigest()[:8]}"
    return base


def gen(row, facing, out: Path, extra: str, pose: str, timeout: int) -> int:
    f = row["files"]
    label, surface = SURFACE[facing]
    img2 = f["south"]
    if facing == "south":                       # a redrawn south is anchored on the redrawn (or approved) rear view
        cand = out / "candidates" / Path(f["north"]).name
        img2 = str(cand) if cand.exists() else f["north"]
    prompt = PROMPT.format(label=label, surface=surface, extra=(" " + extra) if extra else "", pose=pose,
                           img2="rear" if facing == "south" else "front")
    raw = out / "raw" / f"{slug(row)}_{facing}_raw_{int(time.time())}.png"
    raw.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    p = subprocess.run([sys.executable, str(CODEX), "edit", "--out", str(raw), "--prompt", prompt,
                        "--image", f["east"], "--image", img2, "--timeout", str(timeout),
                        "--model", MODEL, "--codex-home", CODEX_HOME],
                       capture_output=True, text=True)
    dt = round(time.time() - t0, 1)
    rec = {"texPath": row["texPath"], "facing": facing, "raw": (str(raw.relative_to(REPO)) if raw.is_relative_to(REPO) else str(raw)), "seconds": dt,
           "ok": p.returncode == 0 and raw.exists(), "rc": p.returncode, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "prompt": prompt, "err": (p.stderr or "")[-400:] if p.returncode else ""}
    with open(out / "timing.jsonl", "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"{'OK' if rec['ok'] else 'FAIL'} {slug(row)} {facing} {dt}s -> {raw.name}")
    return 0 if rec["ok"] else 1


def target_ratio(row, facing) -> float:
    fx = (row.get("fixes") or {}).get(facing)
    if fx and fx.get("target"):
        return fx["target"]
    for fx in (row.get("fixes") or {}).values():   # the other facing's ground-camera target (plan median)
        if fx.get("target"):
            return fx["target"]
    return 1.06


def latest_raw(out: Path, row, facing) -> Path:
    c = sorted((out / "raw").glob(f"{slug(row)}_{facing}_raw_*.png"))
    if not c:
        sys.exit(f"no raw render for {slug(row)} {facing}")
    return c[-1]


def conform(row, facing, out: Path, raw: Path | None = None) -> Path:
    from PIL import Image
    raw = raw or latest_raw(out, row, facing)
    src = Image.open(raw).convert("RGBA")
    s = L.silhouette(src)
    src = src.crop((s["x0"], s["y0"], s["x1"] + 1, s["y1"] + 1))
    old = Image.open(row["files"][facing])
    W, H = old.size
    e = row["silhouette"]["east"]
    other = "south" if facing == "north" else "north"
    oc = out / "candidates" / Path(row["files"].get(other, "") or "x").name
    anchor = (L.measure_file(oc) if oc.exists() else None) or row["silhouette"].get(other) or row["silhouette"][facing]
    th = max(1, round(target_ratio(row, facing) * e["h"] * H))
    tw = max(1, round(src.width * th / src.height))
    if tw > W - 2:                                  # never wider than the canvas
        tw, th = W - 2, max(1, round(src.height * (W - 2) / src.width))
    small = src.convert("RGBa").resize((tw, th), Image.LANCZOS).convert("RGBA")
    bottom = min(H - 1, round(e["bottom"] * H))      # feet row = the EAST view's (the creature must not drop when it turns)
    cx = anchor["cx"] if abs(anchor["cx"] - 0.5) > L.CENTRE_KEEP else 0.5      # centred, unless deliberately offset
    x = round(cx * W - tw / 2)
    x = max(1, min(W - tw - 1, x))
    y = max(1, bottom - th)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(small, (x, y))
    a = canvas.getchannel("A").point(lambda v: 0 if v < 8 else v)   # strip sub-visible dust
    canvas.putalpha(a)
    dst = out / "candidates" / Path(row["files"][facing]).name
    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dst)
    print(f"conformed {raw.name} -> {dst} ({tw}x{th} on {W}x{H})")
    return dst


def lint_candidate(row, out: Path) -> dict:
    files = dict(row["files"])
    for f in ("north", "south"):
        c = out / "candidates" / Path(files.get(f, "") or "x").name
        if f in files and c.exists():
            files[f] = str(c)
    m = {f: L.measure_file(p) for f, p in files.items() if f in L.FACES}
    m = {f: v for f, v in m.items() if v}
    plan = row.get("plan")
    j = L.judge(m, L.load_cal(), row.get("view", "elevation"), None if plan in (None, "UNCLASSIFIED") else plan)
    res = {"texPath": row["texPath"], "verdict": "FLAG" if j["flags"] else "PASS",
           "ratios": {k: round(v, 3) for k, v in j["ratios"].items()},
           "flags": [{k: x[k] for k in ("facing", "key", "value", "band")} for x in j["flags"]],
           "files": {k: str(v) for k, v in files.items()}}
    print(f"{res['verdict']} {slug(row)} " + " ".join(f"{k}={v}" for k, v in res["ratios"].items()))
    return res


ARTPIPE = Path(os.environ.get("ARTPIPE_STATE_DIR") or rm_str("artpipe"))
ITEM = "ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL"


def register(row, out: Path, tag: str) -> list[str]:
    """File the candidate set as a finished artpipe render family (done/<id>.json + _artsrc/<id>/<id>.png, one job per
    facing) so `art.py backfill artpipe` puts it in the ledger and art_sheet shows it as ONE column beside the live
    set. Unredrawn facings are byte copies of the live (approved) picture and say so. No install_to: nothing collects
    or installs these; a keep on the sheet is what authorises `art.py install`."""
    import shutil
    ids = []
    timing = {}
    tf = out / "timing.jsonl"
    if tf.exists():
        for line in tf.read_text().splitlines():
            r = json.loads(line)
            if r["texPath"] == row["texPath"] and r["ok"]:
                timing[r["facing"]] = r
    for facing in ("east", "south", "north"):
        live = row["files"].get(facing)
        if not live:
            continue
        cand = out / "candidates" / Path(live).name
        redrawn = cand.exists() and facing != "east"
        jid = f"{tag}_{slug(row).lower()}_{facing}"
        d = ARTPIPE / "_artsrc" / jid
        d.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cand if redrawn else live, d / f"{jid}.png")
        from PIL import Image
        W, H = Image.open(d / f"{jid}.png").size
        rec = {"id": jid, "channel": "codex" if redrawn else "copy", "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "facing": facing, "facings": ["east", "north", "south"], "canvas": {"width": W, "height": H},
               "background": "transparent", "target_def": row["def"], "target_texpath": row["texPath"],
               "rimflow_item_id": ITEM, "reference": live, "style_notes": "",
               "prompt": (timing.get(facing, {}).get("prompt") if redrawn else
                          f"NOT REDRAWN: byte copy of the live {facing} picture ({'the approved anchor' if facing == 'east' else 'it already stands at ground-camera height'}), so the column shows a whole set")}
        (ARTPIPE / "done" / f"{jid}.json").write_text(json.dumps(rec, indent=2, sort_keys=True))
        ids.append(jid)
    print(" ".join(ids))
    return ids


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["gen", "conform", "lint", "register"])
    ap.add_argument("--tag", default="standtall_v1", help="register: job id prefix")
    ap.add_argument("--row", required=True, help="texPath suffix that names exactly one picture set")
    ap.add_argument("--facing", default="north", choices=["north", "south"])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--rows", default=DEFAULT_ROWS, type=Path)
    ap.add_argument("--extra", default="", help="creature-specific camera/pose note appended to the prompt")
    ap.add_argument("--pose", default="standing on all its legs in the same stance as image 1")
    ap.add_argument("--timeout", type=int, default=150)
    ap.add_argument("--raw", type=Path)
    a = ap.parse_args(argv)
    a.out = a.out.resolve()
    row = find_row(a.rows, a.row)
    a.out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "gen":
        return gen(row, a.facing, a.out, a.extra, a.pose, a.timeout)
    if a.cmd == "register":
        register(row, a.out, a.tag)
        return 0
    if a.cmd == "conform":
        conform(row, a.facing, a.out, a.raw)
        return 0
    res = lint_candidate(row, a.out)
    with open(a.out / "lint.jsonl", "a") as fh:
        fh.write(json.dumps(res) + "\n")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
