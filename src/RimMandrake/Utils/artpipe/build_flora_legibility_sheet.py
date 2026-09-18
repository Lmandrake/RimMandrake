#!/usr/bin/env python3
"""build_flora_legibility_sheet.py — FLORA_LEGIBILITY_BAR_1 spec item 1: the
flora-specific grading sheet, mechanism only (never the grade — that's the
owner's, done by hand in the sheet the review-sheets skill serves).

Replicates the review-sheets skill's mechanism the creature legibility pass
used ad hoc (`Transient/legibility_grading_2026-09-13/`, `works`/`borderline`/
`mud` vocabulary) via the now-formalized `sheet_template.html` +
`check_sheet.py` + `serve_sheet.py` pipeline, rather than hand-rolling a page.

Rows:
  - every flora job under `infrastructure/artpipe/done/*.json` (excluding
    `*.manifest.json`) whose class — resolved the SAME way artpiped.py's
    `_job_art_info` resolves it (backfill by stem, job fields win) — is
    "flora" and whose background is "transparent" (the population the
    2026-09-13 regate exempted; MEASURED here at run time, not copied from
    the item file's "129", which this repo's live state no longer reproduces
    exactly — see the printed count).
  - five vanilla probes (grass/bush/agave/birch-tree/oak-tree — the same five
    `class_convention.png` used) resolved from the LIVE texture index, as
    fixed "known good" controls.

Pre-fill: every row defaults to "works" (flora ships with no keyline by
measured vanilla convention, so the null hypothesis is that it already
passes) EXCEPT it is sorted weakest-first by an ad hoc, INVENTED composite —
structure+ground+coverage at 32px, keyline excluded because it does not apply
to flora — purely to put the rows most likely to need a look in front of the
owner first. That composite is a queue order, not a model; `CONFIG.invented`
says so on the page. The bottom 15 by that composite are marked `contested`.

    python3 build_flora_legibility_sheet.py --out Transient/flora_legibility_sheet_<DATE>

Writes <out>/sheet.html (from the skill template) — hand it to
`skills/review-sheets/assets/serve_sheet.py --sheet <out>/sheet.html
--decisions <out>/decisions.json` for delivery. This script never serves and
never writes decisions.json (that file is the owner's, created by the
sidecar on first save).
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

try:
    from PIL import Image
except ImportError:
    print("build_flora_legibility_sheet: PIL (Pillow) is required", file=sys.stderr)
    raise

sys.path.insert(0, str(common.REPO_ROOT / "src" / "RimMandrake" / "Utils"))
import art_legibility as AL  # noqa: E402

REPO = common.REPO_ROOT
DONE_DIR = REPO / "infrastructure" / "artpipe" / "done"
ARTSRC_DIR = REPO / "infrastructure" / "artpipe" / "_artsrc"
BACKFILL_PATH = REPO / "infrastructure" / "artpipe" / "drawsize_backfill.json"
TEMPLATE = Path.home() / ".claude" / "skills" / "review-sheets" / "assets" / "sheet_template.html"
THUMB_MAX_SIDE = 128

# Same suffix-stripping regex artpiped.py's _job_art_info uses to get from a
# job id to the backfill stem — duplicated here deliberately rather than
# imported, because artpiped.py is the daemon's own module and this script
# must keep working even if the daemon is mid-restart.
_SUFFIX_RE = re.compile(r"(_east|_north|_south|_west|_r\d+|_improve(_[a-z])?|_v\d+)$")


def resolve_stem(job_id: str) -> str:
    stem = job_id
    changed = True
    while changed:
        s2 = _SUFFIX_RE.sub("", stem)
        changed = (s2 != stem)
        stem = s2
    return stem


def job_art_info(job_id: str, job: dict, backfill_stems: dict):
    if job.get("art_class") or job.get("drawsize"):
        return (job.get("art_class") or "creature", float(job.get("drawsize") or 1.0), "job-field")
    info = backfill_stems.get(resolve_stem(job_id))
    if isinstance(info, dict):
        return (info.get("class") or "creature", float(info.get("drawsize") or 1.0),
                info.get("ds_source") or "?")
    return ("creature", 1.0, "unresolved")


def find_flora_jobs(backfill_stems: dict) -> list[dict]:
    rows = []
    for p in sorted(DONE_DIR.glob("*.json")):
        if p.name.endswith(".manifest.json"):
            continue
        try:
            job = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        job_id = job.get("id") or p.stem
        if (job.get("background") or "transparent") != "transparent":
            continue
        art_class, drawsize, ds_source = job_art_info(job_id, job, backfill_stems)
        if art_class != "flora":
            continue
        png = ARTSRC_DIR / job_id / f"{job_id}.png"
        if not png.is_file():
            continue
        rows.append({
            "job_id": job_id,
            "png": png,
            "canvas": job.get("canvas") or {},
            "drawsize": drawsize,
            "ds_source": ds_source,
            "rimflow_item_id": job.get("rimflow_item_id"),
        })
    return rows


def data_uri(path: Path, max_side: int = THUMB_MAX_SIDE) -> str:
    im = Image.open(path).convert("RGBA")
    im.thumbnail((max_side, max_side), Image.NEAREST)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def vanilla_probes() -> list[dict]:
    """The same five probes `class_convention.png` used, re-resolved live
    (`gen_plant_register.py`'s own texture index + resolver) rather than
    cropped out of that committed PNG — so a stale texture index does not
    silently keep serving 2026-09-13's pixels."""
    sys.path.insert(0, str(common.REPO_ROOT / "src" / "RimMandrake" / "Utils"))
    import gen_plant_register as GPR  # noqa: E402
    import sqlite3

    dumpdb = Path("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
                   "RimWorld by Ludeon Studios/DefDump/defs.sqlite")
    if not dumpdb.is_file():
        print(f"  vanilla_probes: no live DefDump at {dumpdb} — probes skipped "
              f"(UNMEASURED, not zero)", file=sys.stderr)
        return []
    con = sqlite3.connect(f"file:{dumpdb}?mode=ro", uri=True)

    def get(defname):
        cur = con.execute(
            "SELECT json, package_id FROM defs WHERE def_name=? AND def_type='ThingDef'",
            (defname,))
        return [(json.loads(r), pkg) for r, pkg in cur.fetchall()]

    idx, _mods = GPR._texture_index()
    dir_idx = GPR.TCS.build_dir_index(idx)
    bundles, _n = GPR.ACS.load_bundle_index()

    probes = []
    for defname, group_label in (
        ("Plant_Grass", "vanilla grass"),
        ("Plant_Bush", "vanilla bush"),
        ("Plant_Agave", "vanilla agave"),
        ("Plant_TreeBirch", "vanilla tree"),
        ("Plant_TreeOak", "vanilla tree"),
    ):
        recs = get(defname)
        rec = next((r for r, pkg in recs if pkg == "ludeon.rimworld"), None)
        if rec is None and recs:
            rec = recs[0][0]
        if rec is None:
            continue
        fields = rec.get("fields", {})
        gd = fields.get("graphicData", {})
        cg = gd.get("cachedGraphic", {})
        row = {
            "defName": defname,
            "texPath": gd.get("texPath"),
            "graphicClass": gd.get("graphicClass"),
            "subGraphics": [s.get("path") for s in (cg.get("subGraphics") or [])],
            "packageId": rec.get("packageId"),
        }
        hit, how = GPR._resolve_plant(row, idx, dir_idx, bundles)
        if hit:
            probes.append({"defName": defname, "group_label": group_label,
                            "png": Path(hit), "how": how})
    return probes


def build_items(flora_rows: list[dict], probe_rows: list[dict]) -> list[dict]:
    scored = []
    for r in flora_rows:
        try:
            info = AL.score_file(str(r["png"]), tiers=[32])
        except Exception as exc:  # noqa: BLE001 — a bad file must not kill the whole sheet
            print(f"  score failed for {r['job_id']}: {exc}", file=sys.stderr)
            info = None
        m = (info or {}).get("tiers", {}).get("32", {})
        structure, ground, coverage = m.get("structure", 0.0), m.get("ground", 0.0), m.get("coverage", 0.0)
        composite = round(100.0 * (0.5 * structure + 0.3 * ground + 0.2 * coverage), 1)
        scored.append((composite, r, m))
    scored.sort(key=lambda t: t[0])  # weakest first

    n = len(scored)
    contested_cut = 15
    items = []
    for i, (composite, r, m) in enumerate(scored):
        canvas = r["canvas"] or {}
        cw, ch = canvas.get("width"), canvas.get("height")
        effect = (f"sizeBin/drawsize {r['drawsize']} ({r['ds_source']}) · canvas "
                  f"{cw}x{ch} · structure {m.get('structure', 0):.2f} ground "
                  f"{m.get('ground', 0):.2f} coverage {m.get('coverage', 0):.2f} "
                  f"(32px, no keyline term) · composite {composite}")
        items.append({
            "id": r["job_id"],
            "label": r["job_id"],
            "group": "flora backlog",
            "effect": effect,
            "thumb": data_uri(r["png"]),
            "prefill": "works",
            "contested": i < contested_cut,
            "meta": {"rimflow": r.get("rimflow_item_id") or ""},
        })

    for p in probe_rows:
        items.append({
            "id": f"probe_{p['defName']}",
            "label": f"{p['defName']} (vanilla)",
            "group": "vanilla probe (control)",
            "effect": f"known-good vanilla flora, resolved {p['how']} — not a candidate, a control",
            "thumb": data_uri(p["png"]),
            "prefill": "works",
            "contested": False,
            "meta": {},
        })
    return items


def build_config(n_flora: int, n_probes: int) -> dict:
    brief = (
        f"<p><b>FLORA_LEGIBILITY_BAR_1, spec item 1.</b> {n_flora} flora files exempted "
        "from the creature-fitted legibility gate and the outside-keyline stroke "
        "(MEASURED live from <code>infrastructure/artpipe/done/</code> + "
        "<code>drawsize_backfill.json</code> at sheet-build time — this repo's live "
        "state does not reproduce the item file's historical count of 129 exactly; "
        "trust this run's number, not that one), beside "
        f"{n_probes} vanilla grass/bush/agave/tree probes as known-good controls.</p>"
        "<p>MEASURED convention (2026-09-13, outline coverage 96px→32px): grass "
        "0.00→0.00, bush 0.18→0.01, agave 0.02, trees soft-edged 1.00→0.32-0.43 "
        "(shading, not a keyline) — versus fauna/pawns at 1.00→1.00 everywhere. So "
        "the creature-calibrated gate and the outside stroke do NOT apply to flora; "
        "grade for value/shape contrast and silhouette coherence, not for a keyline.</p>"
        "<p>Two flags already in hand from the owner: <b>alientree_v1</b> (\"generated "
        "at low resolution\") and <b>ambrosia_v1</b> (\"what the heck is this — supposed "
        "to have big golden blooms\") — both are called out below by note if you want to "
        "jump straight to them.</p>"
    )
    return {
        "sheetId": "flora_legibility_2026-09-17",
        "title": "Flora legibility — grading sheet",
        "subtitle": f"{n_flora} flora + {n_probes} vanilla probes",
        "briefHtml": brief,
        "criterion": ("Rows are sorted weakest-first by an INVENTED, ad hoc composite "
                      "(0.5*structure + 0.3*ground + 0.2*coverage at 32px, keyline "
                      "excluded since it does not apply to flora) — this ranks nothing "
                      "but queue order; it is not the flora model. The bottom 15 are "
                      "marked contested so they are easy to find. YOUR grade is the "
                      "actual target for fitting the flora model (spec item 2, not "
                      "built in this pass)."),
        "invented": [
            "Every row is pre-filled 'works' (null hypothesis: flora ships fine "
            "with no keyline, per the measured vanilla convention) rather than "
            "guessed per-row — only the SORT ORDER (weakest-first) and the "
            "'contested' flag on the bottom 15 are the composite's doing.",
            "The structure/ground/coverage weights (0.5/0.3/0.2) are not fitted "
            "to anything; they exist only to produce a reasonable-looking queue "
            "order for this sheet.",
        ],
        "posture": {"mode": "grading", "explain": (
            "This is a grading pass, not a keep/cut curation — 'works' is not "
            "'in' and 'mud' is not 'out'. Every row ships regardless; the grade "
            "feeds the flora legibility model (spec item 2).")},
        "options": [
            {"key": "works", "label": "Works", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "borderline", "label": "Borderline", "hotkey": "2", "color": "#e8b64c", "counts": "in"},
            {"key": "mud", "label": "Mud / regen", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "group",
        "media": True,
        "decisionsFile": "decisions.json",
        "decisionsPath": "",
        "sheetPath": "",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="output directory (created if missing)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    backfill = json.loads(BACKFILL_PATH.read_text())
    backfill_stems = backfill.get("stems", {})

    flora_rows = find_flora_jobs(backfill_stems)
    probe_rows = vanilla_probes()
    print(f"  flora rows (MEASURED, live): {len(flora_rows)}")
    print(f"  vanilla probe rows: {len(probe_rows)}")

    items = build_items(flora_rows, probe_rows)
    config = build_config(len(flora_rows), len(probe_rows))

    template_html = TEMPLATE.read_text()
    template_html = re.sub(
        r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(config, indent=2) + m.group(2),
        template_html, count=1, flags=re.S)
    template_html = re.sub(
        r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(items, indent=2) + m.group(2),
        template_html, count=1, flags=re.S)

    out_html = out_dir / "sheet.html"
    out_html.write_text(template_html)
    print(f"  wrote {out_html} ({len(items)} rows)")


if __name__ == "__main__":
    main()
