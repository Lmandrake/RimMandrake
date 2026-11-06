#!/usr/bin/env python3
"""build_flora_legibility_sheet.py — FLORA_LEGIBILITY_BAR_1 spec item 1: the flora legibility grading sheet. It
builds the sheet but never grades: the grade is the owner's.

The sheet shows game art, so it is built by the gated, true-scale builder (`src/RimMandrake/Utils/art/art_sheet.py
--subjects --question`), never by a hand-rolled page. That rule is enforced by serve_gated, the commit hook and
sheet_to_artifact. This script decides only WHICH flora to show and WHAT to ask:

  - subjects: our shipped plant ThingDefs (package `mandrake.*`, read from the live def dump), one per distinct
    texPath, split into three size strata: tree (treeCategory set), clump (maxMeshCount > 1, the grass-like
    plants) and single (bushes and flowers). Every def that continues the 2026-09-13 wave (its name matches a
    `drawsize_backfill.json` flora stem) is taken first. Each stratum is then filled to its share of
    `--target` by an even stride over its defNames, so the pick is deterministic.
  - no vanilla controls as rows: the gate (req 3) refuses a row with donor art only, and four of the five
    `class_convention.png` probes draw a retexture of ours in this mod set, so they would not be vanilla anyway.
    Spec item 2 checks the vanilla probes against the fitted model in code; they need no grade.
  - question `legibility`: works / borderline / mud at true in-game scale. There is NO prefill: the old
    2026-09-17 sheet's decisions file held only prefills, which could not be told apart from grades.

The 2026-09-13 renders that old sheet showed are gone (no PNG under `_artsrc`, no art-ledger entry). This sheet
grades the art that ships today, and the snapshot records the exact pictures (sha) each grade was made on.

    python3 build_flora_legibility_sheet.py [--target 120] [--date YYYY-MM-DD] [--plan-only]
    python3 build_flora_legibility_sheet.py --verify Transient/biome_ffar/flora_legibility_sheet_<date>.html
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent
REPO = UTILS.parent.parent.parent
BACKFILL_PATH = REPO / "infrastructure" / "artpipe" / "drawsize_backfill.json"
SHEET_DIR = REPO / "Transient" / "biome_ffar"
NAME = "flora_legibility"
QUESTION_PATH = SHEET_DIR / f"{NAME}.question.json"
ART_SHEET = UTILS / "art" / "art_sheet.py"

STRATA = ("tree", "clump", "single")
OPTIONS = [["works", "Works"], ["borderline", "Borderline"], ["mud", "Mud / regen"]]

# Same suffix-stripping artpiped.py's _job_art_info uses to get from a job id to the backfill stem.
_SUFFIX_RE = re.compile(r"(_east|_north|_south|_west|_r\d+|_improve(_[a-z])?|_v\d+)$")
_TIER_RE = re.compile(r"^(RM|RUT|RSW)_")


def resolve_stem(job_id: str) -> str:
    stem = job_id
    while True:
        s2 = _SUFFIX_RE.sub("", stem)
        if s2 == stem:
            return stem
        stem = s2


def job_art_info(job_id: str, job: dict, backfill_stems: dict):
    # Class and drawsize resolve independently (job field, else backfill):
    # fill_queue always writes drawsize, so it must never decide the class.
    info = backfill_stems.get(resolve_stem(job_id))
    info = info if isinstance(info, dict) else {}
    art_class = job.get("art_class") or info.get("class") or "creature"
    if job.get("drawsize"):
        return (art_class, float(job["drawsize"]), "job-field")
    if info:
        return (art_class, float(info.get("drawsize") or 1.0), info.get("ds_source") or "?")
    return (art_class, 1.0, "unresolved")


def stratum(plant: dict) -> str:
    if (plant.get("treeCategory") or "None") != "None":
        return "tree"
    if int(plant.get("maxMeshCount") or 1) > 1:
        return "clump"
    return "single"


def flora_stems(backfill: dict) -> set:
    stems = backfill.get("stems", backfill)
    return {k for k, v in stems.items() if isinstance(v, dict) and v.get("class") == "flora"}


def select(plants: list[dict], wave_stems: set, target: int) -> list[dict]:
    """plants: [{defName, texPath, stratum}] (our shipped plant defs). Returns the chosen rows, each with
    `why` ("wave" or "stride"). Pure: the selftest sweeps it."""
    seen_tex, uniq = set(), []
    for p in sorted(plants, key=lambda p: p["defName"]):
        tex = p.get("texPath") or p["defName"]
        if tex in seen_tex:
            continue
        seen_tex.add(tex)
        uniq.append(p)
    if target >= len(uniq):
        return [dict(p, why="all") for p in uniq]
    by = {s: [p for p in uniq if p["stratum"] == s] for s in STRATA}
    quota = {s: round(target * len(by[s]) / len(uniq)) for s in STRATA}
    chosen = []
    for s in STRATA:
        pool = by[s]
        wave = [p for p in pool if _TIER_RE.sub("", p["defName"]).lower() in wave_stems]
        rest = [p for p in pool if p not in wave]
        need = max(0, quota[s] - len(wave))
        if need and rest:
            step = len(rest) / min(need, len(rest))
            fill = [rest[int(i * step)] for i in range(min(need, len(rest)))]
        else:
            fill = []
        chosen += [dict(p, why="wave") for p in wave] + [dict(p, why="stride") for p in fill]
    return sorted(chosen, key=lambda p: (STRATA.index(p["stratum"]), p["defName"]))


def live_plants() -> list[dict]:
    sys.path.insert(0, str(UTILS))
    import game_paths  # the one LocalLow locator (ONE_PATH_SEAM)
    db = Path(game_paths.DUMP_ROOT) / "defs.sqlite"
    if not db.is_file():
        raise SystemExit(f"UNMEASURED: no live DefDump at {db}; refusing to pick flora blind")
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    out = []
    for dn, js in con.execute("SELECT def_name, json FROM defs WHERE def_type='ThingDef' AND package_id LIKE 'mandrake.%'"):
        f = json.loads(js).get("fields", {})
        plant = f.get("plant")
        if not plant:
            continue
        out.append({"defName": dn, "texPath": (f.get("graphicData") or {}).get("texPath"), "stratum": stratum(plant)})
    if len(out) < 50:
        raise SystemExit(f"only {len(out)} mandrake plant ThingDefs in {db}: a query bug until proven otherwise")
    return out


def question(chosen: list[dict]) -> dict:
    rows = {p["defName"]: {"context": f"{p['stratum']} · {'continues the 2026-09-13 wave' if p['why'] == 'wave' else 'size-stratified pick'}"}
            for p in chosen}
    return {"key": "legibility", "label": "Legibility at true scale",
            "explain": ("Grade the picture the game draws (the runtime-live column) at its true in-game size beside the "
                        "human: does the plant read? Works / borderline / mud. No keyline is expected on flora (vanilla "
                        "convention, measured 2026-09-13); judge value/shape contrast and silhouette. These grades fit "
                        "the flora legibility model (FLORA_LEGIBILITY_BAR_1). Nothing is pre-filled."),
            "options": OPTIONS, "rows": rows}


LEAD = ("<p><b>Flora legibility grading (FLORA_LEGIBILITY_BAR_1).</b> {n} of our {total} shipped plants (one per "
        "picture, split by size: {strata}). For each row, pick <b>Works / Borderline / "
        "Mud</b> for the picture the game draws, at true scale. Nothing is pre-filled. Column picks and notes work as "
        "on any art sheet but are optional here. A row you skip simply stays ungraded; the model is fitted from the "
        "rows you grade.</p>")


def build(target: int, day: str, plan_only: bool) -> int:
    plants = live_plants()
    chosen = select(plants, flora_stems(json.loads(BACKFILL_PATH.read_text())), target)
    q = question(chosen)
    counts = {s: sum(1 for p in chosen if p["stratum"] == s) for s in STRATA}
    n_wave = sum(1 for p in chosen if p["why"] == "wave")
    print(f"  plant defs (live dump, mandrake.*): {len(plants)}; chosen {len(chosen)} ({counts}; {n_wave} continue the wave)")
    SHEET_DIR.mkdir(parents=True, exist_ok=True)
    QUESTION_PATH.write_text(json.dumps(q, indent=1) + "\n")
    if plan_only:
        print(f"  plan only: wrote {QUESTION_PATH}")
        return 0
    subjects = [p["defName"] for p in chosen]
    lead = LEAD.format(n=len(chosen), total=len({p.get('texPath') or p['defName'] for p in plants}),
                       strata=", ".join(f"{v} {k}" for k, v in counts.items()))
    cmd = [sys.executable, str(ART_SHEET), "--subjects", *subjects, "--name", NAME, "--label",
           "Flora legibility — grading", "--lead", lead, "--question", str(QUESTION_PATH), "--date", day,
           "--hide-sets", "render ", "--reopen", *subjects]
    return subprocess.call(cmd, cwd=str(REPO), timeout=540)


def verify(html: Path) -> int:
    """The sheet the owner grades exists, is pinned in git (Transient decays), carries the scaled-review gate's
    stamp (scaled_review_gate.verify_stamp; the full gate check also needs the sheet's ~150 MB of scale images, which are
    never committed), and asks the legibility question on every row, with no answer and no prefill."""
    bad = []
    rel = html.resolve().relative_to(REPO)
    dec = html.parent / (html.name[:-len(".html")] + ".decisions.json")
    for p in (html, dec, QUESTION_PATH):
        if not p.is_file():
            bad.append(f"missing {p}")
        elif subprocess.run(["git", "ls-files", "--error-unmatch", str(p.resolve().relative_to(REPO))], cwd=str(REPO),
                            capture_output=True, timeout=120).returncode:
            bad.append(f"not pinned in git: {p.resolve().relative_to(REPO)}")
    if bad:
        print("\n".join(bad)); return 1
    text = html.read_text()
    sys.path.insert(0, str(UTILS / "art"))
    import scaled_review_gate as SG  # the gate's own stamp: written only on a pass, bound to the page's bytes
    stamped, why = SG.verify_stamp(text)
    if not stamped:
        bad.append(f"{rel}: {why}")
    items = SG._json_block(text, "ITEMS") or []
    if not items:
        print(f"{rel}: no ITEMS block"); return 1
    ids = {it["id"] for it in items}
    for it in items:
        iq = it.get("question")
        if not iq:
            bad.append(f"row {it['id']} asks no legibility question")
        elif iq.get("prefill"):
            bad.append(f"row {it['id']} carries an agent prefill {iq['prefill']!r}")
    d = json.loads(dec.read_text())
    recs = d.get("decisions", d) if isinstance(d, dict) else {}
    recs = recs if isinstance(recs, dict) else {}
    answered = [k for k, r in recs.items() if isinstance(r, dict) and (r.get("q") or {}).get("legibility")]
    guessed = [k for k, r in recs.items() if isinstance(r, dict) and (r.get("qPrefill") or {}).get("legibility")]
    if guessed:
        bad.append(f"{len(guessed)} decisions rows carry an agent legibility guess (qPrefill), e.g. {guessed[:3]}")
    if missing := sorted(ids - set(recs)):
        bad.append(f"{len(missing)} sheet rows have no decisions record, e.g. {missing[:3]}")
    our_rows = len(ids)
    if our_rows < 60:
        bad.append(f"only {our_rows} flora rows (want >= 60 to fit a model)")
    if bad:
        print("\n".join(bad)); return 1
    print(f"OK {rel}: {len(ids)} rows of our flora, gate stamp ok, legibility asked on every row, "
          f"no prefill; {len(answered)} graded so far; pinned")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--target", type=int, default=120, help="how many of our plants to show (default 120)")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--plan-only", action="store_true", help="write the question file, build no sheet")
    ap.add_argument("--verify", metavar="HTML")
    a = ap.parse_args(argv)
    if a.verify:
        return verify(Path(a.verify))
    return build(a.target, a.date, a.plan_only)


if __name__ == "__main__":
    sys.exit(main())
