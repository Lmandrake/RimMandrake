#!/usr/bin/env python3
"""flyer_gate.py - the flyer gate: is a static fit to fly, and is a flip-book body-locked (FLYER_STABLE_BODY_GATE_1).

Design: design/RimMandrake/flyer_stable_body_study.md. Offline only; flight is never tested here.

The automatic G numbers are REFUTERS: a fail means a look is owed, a pass proves nothing, because alpha cannot tell a
wing from a torso (calibration in the study, section 3.2). What decides is the flip-book gate, the exit code of
flier_body_stabilize.py, run per facing against a reviewed cut-out annotation.

Verbs:
  cell DEF...          the `flyer:` cell of each def, from the committed plan
  static TEXPATH       G1/G2/G4 of a static, exit 1 on a refuted static
  flipbook SET...      the body-lock test of flyer_cutout_sets/<SET>.json; exit 0 only if every facing passes
  refresh              rerun census, statics and flip-book gates; rewrite design/RimMandrake/flyer_regen_plan.json
  audit [--strict]     does the plan cover the live census, is the study reconciled, does an open item own the rest
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import flier_frame_registration as FR  # noqa: E402

PLAN = REPO / "design/RimMandrake/flyer_regen_plan.json"
STUDY = REPO / "design/RimMandrake/flyer_stable_body_study.md"
SETS = HERE / "flyer_cutout_sets"
FACINGS = ("east", "south", "north")

G1_MIN_SHARE = 0.50   # body share of the opaque area, S/N: lowest by-eye convertible 0.54
G2_MIN_WIDTH = 0.33   # N/S width over E width: lowest by-eye convertible 0.349; Strill 0.30, a sliver
G4_MAX_BODY = 0.85    # body bbox over canvas width, S/N: highest by-eye convertible 0.80
NO_WINGS_DRAWN = {"RM_Thozzik": "G3 no wings drawn", "RM_ThozzikQueen": "G3 no wings drawn",
                  "RM_ThozzikColony": "G3 no wings drawn", "RM_ThozzikColonyQueen": "G3 no wings drawn",
                  "RSW_Strill": "G3 no wings drawn"}
# def -> the cut-out configs that must all pass for that def's flip-book to count as locked
DEF_SETS = {"RSW_Sketto": ["Sketto"], "RSW_PekoPeko": ["PekoPeko_f", "PekoPeko_m"], "RM_FireHawk": ["FireHawk"], "RSW_Uvak": ["Uvak"],
            "RSW_Hawkbat": ["Hawkbat", "Hawkbat_j"], "RSW_Bogwing": ["Bogwing"], "RM_Krizzak": ["Krizzak"],
            "RSW_Shyrack": ["Shyrack"], "RSW_Urusai": ["Urusai"], "RSW_Whisperbird": ["Whisperbird"]}
# def -> a body-plan word (study 3.3), for the defs the study assigned one
PLANS = ("bird", "bat", "insect", "ray", "floater", "swarm", "large")
TIERS = {
    1: "RSW_Hawkbat RSW_PekoPeko RSW_Beldon RSW_Convor RSW_Bogwing RSW_ScrapNestBird RM_Murrelith RM_Pirrik RM_Grimewing "
       "RM_BloodropMoth RSW_FacetMoth RSW_CanCell RSW_Dactillion RSW_Neebray".split(),
    2: "RSW_Shyrack RSW_Uvak RSW_Whisperbird RSW_Sketto RM_Soorrak RM_Sivvern RM_Sparkleech RM_Dustflutter RM_Vrisk "
       "RSW_Strill RM_FireHawk RM_Zellik RSW_Urusai".split(),
    3: "RM_Skellick RM_Skiralim RM_Dwommo RM_FeverSwarm RM_Skinflap RSW_Porg".split(),
}
TIER_ITEMS = {1: "FLYER_TIER_ONE_REBUILD_REDO_ROWS_FIRST", 2: "FLYER_TIER_TWO_REBUILD_KEPT_NEW_WINGS",
              3: "FLYER_TIER_THREE_REBUILD_EASY_WINGS_ONLY", 4: "FLYER_TIER_FOUR_REBUILD_UNRULED_AT_SITTING"}
ITEM_LIVE = ("proposed", "doing", "built", "implemented", "blocked", "open")


def tex_index() -> dict:
    idx = {}
    for p in (REPO / "src").rglob("*.png"):
        s = str(p)
        i = s.find("/Textures/")
        if i >= 0:
            idx.setdefault(s[i + 10:-4], p)
    return idx


def static_metrics(paths: dict) -> dict | None:
    """paths: facing -> PNG. None when a facing is missing or blank (UNMEASURED, never a pass)."""
    m = {}
    for f in FACINGS:
        if f not in paths:
            return None
        a = np.array(Image.open(paths[f]).convert("RGBA"))[..., 3]
        solid = a > FR.ALPHA
        if not solid.any():
            return None
        body = FR.body_of(a)
        xs = np.where(solid)[1]
        bx = np.where(body)[1]
        m[f] = {"w": (xs.max() - xs.min() + 1) / a.shape[1], "bw": (bx.max() - bx.min() + 1) / a.shape[1],
                "share": float(body.sum() / solid.sum())}
    return {"g1": round(float(min(m["south"]["share"], m["north"]["share"])), 3),
            "g2": round(float(min(m["south"]["w"], m["north"]["w"]) / m["east"]["w"]), 3),
            "g4": round(float(max(m["south"]["bw"], m["north"]["bw"])), 3)}


def refuted(g: dict | None) -> list[str]:
    if g is None:
        return ["G? static UNMEASURED"]
    out = []
    if g["g1"] < G1_MIN_SHARE:
        out.append(f"G1 body share {g['g1']:.2f} < {G1_MIN_SHARE}")
    if g["g2"] < G2_MIN_WIDTH:
        out.append(f"G2 N/S width {g['g2']:.2f} < {G2_MIN_WIDTH}")
    if g["g4"] > G4_MAX_BODY:
        out.append(f"G4 body width {g['g4']:.2f} > {G4_MAX_BODY}")
    return out


def cell_text(row: dict | None) -> str:
    """The sheet's `flyer:` cell. ✓ needs a passing flip-book; a refuted static or missing wings is ✗."""
    if row is None:
        return ""
    why = list(row.get("static_fails") or [])
    if row["flipbook"] == "locked":
        return "flyer: convertible ✓ flip-book body-locked"
    book = {"gate_fails": "flip-book fails the body lock", "unannotated": "flip-book not body-locked",
            "none": "no flip-book"}[row["flipbook"]]
    if why:
        return f"flyer: ✗ {'; '.join(why)}; {book}"
    return f"flyer: partial: {book}"


def plan_rows() -> dict:
    """A missing plan raises: a sheet with no flyer cells must not look like a sheet with no flyers."""
    return json.loads(PLAN.read_text())["flyers"]


_cache: dict | None = None


def cell_for(names) -> str:
    """The first cell any of these def names has. A sheet row passes every name it knows."""
    global _cache
    if _cache is None:
        _cache = dict(plan_rows())
        _cache.update({r["tex"]: r for r in list(_cache.values()) if r.get("tex")})   # a texPath row finds its flyer
    for n in names:
        if n and n in _cache:
            return cell_text(_cache[n])
    return ""


def flipbook_rc(name: str) -> int:
    """0 pass, 1 fail, 2 UNMEASURED. The exit code of the gate, never a parse of its prose."""
    if not (SETS / f"{name}.json").exists():
        return 2
    return subprocess.run([sys.executable, str(HERE / "flier_body_stabilize.py"), "--set", name],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=200, cwd=REPO).returncode


_rc: dict = {}


def book_rc(name: str) -> int:
    """flipbook_rc, once per process: a sheet asks per row and the frames do not change under it."""
    if name not in _rc:
        _rc[name] = flipbook_rc(name)
    return _rc[name]


def failing_sets(names) -> list[str]:
    """The cut-out sets of these defs that do not exit 0, as `Set (exit n)`."""
    sets = dict.fromkeys(s for n in names for s in DEF_SETS.get(n, []))
    return [f"{s} (exit {book_rc(s)})" for s in sets if book_rc(s) != 0]


def withhold_books(names, flips: list[dict]) -> tuple[list[dict], str]:
    """Criterion 3: the flip-book columns he may see, and the flag saying what was held back.

    A def with a cut-out set shows no frames until every set exits 0. A def with none keeps its old shipped frames, whose
    state the `flyer:` cell states, but a new render (kind artpipe) has no gate to pass, so it is held back."""
    names = [n for n in names if n]
    if not flips:
        return flips, ""
    bad = failing_sets(names)
    if bad:
        return [], f"flip-book withheld: {', '.join(bad)} fails the body lock"
    if any(n in DEF_SETS for n in names) or not cell_for(names):
        return flips, ""
    kept = [c for c in flips if c.get("kind") != "artpipe"]
    if len(kept) == len(flips):
        return flips, ""
    return kept, f"flip-book withheld: {len(flips) - len(kept)} render(s) with no cut-out set to pass the body lock"


def sheet_refusal(html: str) -> str:
    """The last door: a built sheet naming frames of a failing set in a live lane. Empty = may be served."""
    sets = {s for row in DEF_SETS.values() for s in row}     # not every json there is a set: Uvak_south_layers is a sidecar
    by_prefix = {json.loads((SETS / f"{s}.json").read_text())["prefix"]: s for s in sets if (SETS / f"{s}.json").exists()}
    seen = {m.rpartition("/")[2] for m in re.findall(r'"res": ?"_flip:([^"]+)"', html)}
    bad = [f"{by_prefix[s]} (exit {book_rc(by_prefix[s])})" for s in sorted(seen)
           if s in by_prefix and book_rc(by_prefix[s]) != 0]
    return f"flip-book fails the body lock: {', '.join(bad)}" if bad else ""


def run_census(out: Path) -> list[dict]:
    r = subprocess.run([sys.executable, str(HERE / "flyer_census.py"), "--no-art", "--out", str(out)],
                       capture_output=True, text=True, timeout=300, cwd=REPO)
    if r.returncode:
        raise SystemExit(f"flyer_census failed: {r.stderr[-400:]}")
    return [row for row in csv.DictReader(open(out)) if row["flies"].startswith(("flies", "should-fly"))]


def refresh() -> int:
    with tempfile.TemporaryDirectory() as td:
        rows = run_census(Path(td) / "c.csv")
    idx = tex_index()
    tier_of = {d: t for t, ds in TIERS.items() for d in ds}
    rc_memo: dict = {}
    out = {}
    for r in rows:
        d, tex = r["defName"], r["body_tex"]
        paths = {f: idx[f"{tex}_{f}"] for f in FACINGS if f"{tex}_{f}" in idx}
        g = static_metrics(paths) if tex else None
        fails = refuted(g)
        if d in NO_WINGS_DRAWN:
            fails.append(NO_WINGS_DRAWN[d])
        sets = DEF_SETS.get(d, [])
        rcs = [rc_memo.setdefault(s, flipbook_rc(s)) for s in sets]
        if not r["frame_prefix"]:
            book = "none"
        elif not sets or 2 in rcs:
            book = "unannotated"
        else:
            book = "locked" if not any(rcs) else "gate_fails"
        tier = 0 if book == "locked" else tier_of.get(d, 4)
        out[d] = {"tier": tier, "item": TIER_ITEMS.get(tier, ""), "flipbook": book, "sets": sets, "tex": tex, "static": g,
                  "static_fails": fails, "provenance": r["frame_provenance"], "frames": r["frame_count"]}
    PLAN.write_text(json.dumps({"schema": 1, "made_by": "flyer_gate.py refresh", "flyers": dict(sorted(out.items()))},
                               indent=1, ensure_ascii=False) + "\n")
    print(f"{len(out)} flyers -> {PLAN}")
    return 0


def item_state(item: str) -> str:
    r = subprocess.run([sys.executable, str(REPO / "src/RimMandrake/rimflow/cli.py"), "show", item],
                       capture_output=True, text=True, timeout=60, cwd=REPO)
    m = re.match(rf"{re.escape(item)}\s+(\S+)", r.stdout)
    return m.group(1) if m else "MISSING"


def audit(strict: bool) -> int:
    bad = []
    with tempfile.TemporaryDirectory() as td:
        rows = run_census(Path(td) / "c.csv")
    live = {r["defName"] for r in rows}
    if len(live) < 50 or not {"RM_FireHawk", "RSW_Hawkbat", "RSW_Mynock"} <= live:
        bad.append(f"census blind: {len(live)} flyers, sanity defs absent")   # the instrument must be able to see
    plan = plan_rows()
    bad += [f"{d}: in the census, not in the plan" for d in sorted(live - set(plan))]
    bad += [f"{d}: in the plan, no longer a flyer" for d in sorted(set(plan) - live)]
    text = STUDY.read_text() if STUDY.exists() else ""
    if not text:
        bad.append(f"missing {STUDY}")
    if "[R]" in text or "`[R]`" in text:
        bad.append("the study still carries an [R] value")
    states = {}
    for d, row in sorted(plan.items()):
        if row["flipbook"] == "locked":
            if row["tier"] != 0:
                bad.append(f"{d}: locked but tiered")
            continue
        it = row.get("item") or ""
        if not it:
            bad.append(f"{d}: not locked and no item owns it")
            continue
        st = states.setdefault(it, item_state(it))
        if st not in ITEM_LIVE:
            bad.append(f"{d}: owned by {it}, which is {st}")
    n = sum(1 for r in plan.values() if r["flipbook"] == "locked")
    print(f"{len(plan)} flyers, {n} body-locked, {len(plan) - n} owed under {sorted(states)}: {states}")
    for b in bad:
        print("BAD", b)
    return 1 if bad and strict else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("cell").add_argument("defs", nargs="+")
    sub.add_parser("static").add_argument("tex")
    sub.add_parser("flipbook").add_argument("sets", nargs="+")
    sub.add_parser("refresh")
    sub.add_parser("audit").add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    if a.verb == "cell":
        for d in a.defs:
            print(d, cell_for([d]) or "(not a flyer)")
        return 0
    if a.verb == "static":
        idx = tex_index()
        g = static_metrics({f: idx[f"{a.tex}_{f}"] for f in FACINGS if f"{a.tex}_{f}" in idx})
        print(g, refuted(g) or "not refuted (a look is still owed)")
        return 1 if refuted(g) else 0
    if a.verb == "flipbook":
        rcs = {s: flipbook_rc(s) for s in a.sets}
        print(rcs)
        return max(rcs.values())
    return refresh() if a.verb == "refresh" else audit(a.strict)


if __name__ == "__main__":
    sys.exit(main())
