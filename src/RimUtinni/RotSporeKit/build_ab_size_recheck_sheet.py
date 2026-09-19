#!/usr/bin/env python3
"""build_ab_size_recheck_sheet.py — the 11 AlphaBiomes rows, re-served at true size.

Owner ruling 2026-09-19: SERVE CORRECTED SHEET for the 11 Alpha Biomes mushroom
rows that were ruled against a wrong panel — current-vs-ruled size, one sitting,
he re-rules.

WHAT WENT WRONG (MEASURED 2026-09-19, see build_review_sheet.py's resolver note):
the 2026-09-18 sheet drew 11 of the 13 AB_ rows as a 1.0-cell quad, because a
hand-transcribed table claimed they set no visualSizeRange and inherited the
vanilla PlantBase 0.3~1.00. All 13 set their own. So he judged, and typed widths
for, mushrooms that were already 2x to 6x bigger than the picture in front of him.

Three classes came out of that, and they are the sheet's three groups:

  no-op       he typed the number the def ALREADY had. His ruling changed
              nothing, and he made it believing the plant was 1.0 wide.
  enlarged    he enlarged from a false 1.0 baseline, so his multiplier was
              anchored to a number that was never true.
  no width    he ruled only "rename"; no width decision was corrupted, but the
              panel still misled him.

This script does NOT regenerate the 2026-09-18 sheet or its decisions file —
that file is frozen and holds his 48-row ruling. It builds a NEW, scoped sheet.

    python3 build_ab_size_recheck_sheet.py            # dry run, writes nothing
    python3 build_ab_size_recheck_sheet.py --apply    # writes sheet + panels + prefill
"""

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = Path.home() / ".claude" / "skills" / "review-sheets"
TEMPLATE = SKILL / "assets" / "sheet_template.html"

OUT_HTML = REPO_ROOT / "Transient" / "ab_size_recheck_2026-09-19.html"
OUT_DEC = REPO_ROOT / "Transient" / "ab_size_recheck_2026-09-19.decisions.json"
PANELS = REPO_ROOT / "Transient" / "ab_size_recheck_panels_2026-09-19"
PANEL_REL = PANELS.name

# The frozen sheet whose rulings these rows came from — read for his notes, never written.
FROZEN_DECISIONS = REPO_ROOT / "Transient" / "rot_flora_fauna_review_2026-09-18.decisions.json"

# What the 2026-09-18 sheet PUT ON SCREEN for these rows: a 1.0-cell quad, from
# the wrong table. Kept as a historical constant — it is not derivable any more,
# because the resolver that replaced the table no longer produces it.
PANEL_SHOWED_MAX = 1.0

# The 11 rows whose panel was wrong. AB_Bryolux and AB_AgariluxPrime are NOT here:
# their table entries were correct, so he judged those two against a true picture.
ROWS = [
    # defName,                  group,      his ruled width or None
    ("AB_GiantAgarilux",        "no-op",    6),
    ("AB_RecurvedStropharia",   "no-op",    5),
    ("AB_SlimyPholiota",        "no-op",    5),
    ("AB_GlowingAgarilux",      "enlarged", 4),
    ("AB_LilacBeacon",          "enlarged", 3),
    ("AB_WitchesOyster",        "enlarged", 6),
    ("AB_ArbuscularMycorrhiza", "enlarged", 9),
    ("AB_AgaricusDomeCap",      "enlarged", 7),
    ("AB_DribblingCap",         "enlarged", 12),
    ("AB_Glowstool",            "no width", None),
    ("AB_Agarilux",             "no width", None),
]

GROUP_LABEL = {
    "no-op": "A · his number was already the def's number",
    "enlarged": "B · enlarged from a false 1.0 baseline",
    "no width": "C · no width ruled — panel was wrong anyway",
}


def load_builder():
    """Import build_review_sheet for its resolver, FLORA rows and panel painter."""
    spec = importlib.util.spec_from_file_location(
        "brs", Path(__file__).with_name("build_review_sheet.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_DONOR_INDEX = None


def donor_only_max(brs, defname):
    """visualSizeRange max BEFORE our own patches — the donor def's own number.

    The index is built once: it rglobs Core and two Workshop mods off a Windows
    mount, which takes ~30s, and rebuilding it per row made this script look hung."""
    global _DONOR_INDEX
    if _DONOR_INDEX is None:
        _DONOR_INDEX = brs._plant_def_index()   # deliberately un-patched
    (_, hi), _ = brs.resolve_visual_size_range(defname, _DONOR_INDEX)
    return hi


def compose_pair(brs, src, dst, was_cells, now_cells, mesh):
    """One PNG: the 1.0-cell quad he was shown, beside the plant's true size.

    Both panels are painted by build_review_sheet's own make_plant_scale_panel,
    so the human anchor and cell pitch are identical to the sheet he reviewed —
    the only thing that changes between the two halves is the cell count."""
    from PIL import Image, ImageDraw

    tmp_a, tmp_b = dst.with_suffix(".was.png"), dst.with_suffix(".now.png")
    brs.make_plant_scale_panel(src, tmp_a, was_cells, mesh)
    brs.make_plant_scale_panel(src, tmp_b, now_cells, mesh)
    a, b = Image.open(tmp_a).convert("RGBA"), Image.open(tmp_b).convert("RGBA")

    pad, cap = 10, 16
    h = max(a.height, b.height) + cap
    out = Image.new("RGBA", (a.width + b.width + pad * 3, h + pad), (14, 16, 20, 255))
    out.paste(a, (pad, cap + (h - cap - a.height)), a)
    out.paste(b, (pad * 2 + a.width, cap + (h - cap - b.height)), b)
    d = ImageDraw.Draw(out)
    # Precise labels: the right-hand panel is the size DEPLOYED today, which for
    # group B is his own ruling, not the def's original. Saying "really" there
    # would claim the donor's number and the deployed one are the same thing.
    d.text((pad, 2), f"sheet: {was_cells:g}", fill=(224, 108, 108, 255))
    d.text((pad * 2 + a.width, 2), f"deployed: {now_cells:g}", fill=(90, 195, 127, 255))
    # a hairline between the two so they never read as one picture
    x = pad + a.width + pad // 2
    d.line([(x, cap), (x, h)], fill=(42, 47, 55, 255))
    out.save(dst)
    tmp_a.unlink(missing_ok=True)
    tmp_b.unlink(missing_ok=True)


def build(apply_it):
    brs = load_builder()
    frozen = json.loads(FROZEN_DECISIONS.read_text(encoding="utf-8"))
    his = frozen["decisions"]
    flora = {r[0]: r for r in brs.FLORA}

    if apply_it:
        PANELS.mkdir(parents=True, exist_ok=True)

    items, prefill = [], {}
    for defname, group, ruled in ROWS:
        row = flora[defname]
        label, _source, _comm, _desc, _tex, _status, thumb_src, _note = row[1:]
        applied = brs.mature_cells_flora(defname)[1]
        donor = donor_only_max(brs, defname)
        note = (his.get(f"A_{defname}") or {}).get("note", "")
        mesh = min(brs.FLORA_MESH.get(defname, 1), brs.MESH_CAP)

        if group == "no-op":
            effect = (f"You ruled \"{ruled} wide\" — the def was ALREADY {donor:g}. "
                      f"Your ruling changed nothing, and you made it looking at a "
                      f"{PANEL_SHOWED_MAX:g}-cell picture. Deployed today: {applied:g}.")
        elif group == "enlarged":
            effect = (f"You ruled \"{ruled} wide\" against a {PANEL_SHOWED_MAX:g}-cell "
                      f"picture, but the def was {donor:g}. Deployed today: {applied:g} "
                      f"— {applied / donor:.1f}x the donor's own size.")
        else:
            effect = (f"No width ruled, only \"{note or 'rename'}\". The panel showed "
                      f"{PANEL_SHOWED_MAX:g} and the real size is {applied:g}, so you "
                      f"judged its look at the wrong scale.")

        thumb_rel = None
        if thumb_src:
            src = Path(thumb_src)
            src = src if src.is_absolute() else REPO_ROOT / src
            if src.exists():
                dst = PANELS / f"{defname}.png"
                thumb_rel = f"{PANEL_REL}/{dst.name}"
                if apply_it:
                    compose_pair(brs, src, dst, PANEL_SHOWED_MAX, applied, mesh)

        items.append({
            "id": defname,
            "group": GROUP_LABEL[group],
            "label": label,
            "effect": effect,
            "thumb": thumb_rel,
            "prefill": "confirm",
            "contested": group == "no-op",
            "meta": {"your note": note or "—",
                     "donor def": f"{donor:g}",
                     "deployed": f"{applied:g}"},
        })
        prefill[defname] = {"decision": "confirm", "prefill": "confirm", "note": ""}

    html = TEMPLATE.read_text(encoding="utf-8")
    config = {
        "sheetId": "ab_size_recheck_2026-09-19",
        "title": "Mushroom sizes, re-served at true scale",
        "subtitle": "11 AlphaBiomes rows from the 2026-09-18 Rot sheet",
        "briefHtml": (
            "<p>On the 2026-09-18 Rot sheet these 11 rows were drawn as a "
            "<b>1.0-cell</b> quad. That was a bug in the sheet, not the defs: a "
            "hand-transcribed table claimed they inherit the vanilla "
            "<code>PlantBase</code> 0.3~1.00, and <b>all of them set their own "
            "<code>visualSizeRange</code></b>. So the widths you typed were "
            "judged against pictures 2x to 6x too small.</p>"
            "<p>Each row shows <b>what you saw</b> beside <b>what the plant "
            "actually is</b>, at the same cell pitch and against the same human "
            "anchor. <b>Nothing here is undone</b> — the sizes you ruled are "
            "deployed right now, and the <code>deployed</code> chip on each row "
            "is the live number. This sheet only asks whether you still want "
            "them now that the picture is honest.</p>"
            "<p>Group A is the sharp one: there you typed a number the def "
            "<i>already had</i>, so your ruling changed nothing at all.</p>"
            "<p>To change a width, pick <b>resize</b> and put the number in the "
            "note. The 2026-09-18 sheet and its decisions file are frozen and "
            "untouched.</p>"),
        "criterion": ("Grouped by how the wrong panel corrupted the decision — which ranks "
                      "how SUSPECT each ruling is, not whether the size looks good. "
                      "Only you can rank that."),
        "invented": [
            "The three groups are my reading of how each ruling was corrupted, not yours.",
            "Every row is pre-filled CONFIRM — the deployed size stands. That is the "
            "conservative default, not a recommendation that the size is right.",
            "Group A assumes you meant an absolute width. If you meant '6x what I am "
            "looking at', all three of those rows are far too small and I have said the "
            "opposite.",
        ],
        "posture": {
            "mode": "whitelist",
            "explain": ("Default is CONFIRM: a row you leave alone keeps the size that is "
                        "deployed today. Nothing is stripped by not deciding."),
        },
        "options": [
            {"key": "confirm", "label": "Confirm", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "resize", "label": "Resize (say the number)", "hotkey": "2", "color": "#e8b64c", "counts": "out"},
            {"key": "revert", "label": "Revert to donor", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "how the wrong panel bit",
        "media": True,
        "decisionsFile": OUT_DEC.name,
        "decisionsPath": str(OUT_DEC),
        "sheetPath": str(OUT_HTML),
    }

    html = replace_block(html, "CONFIG", json.dumps(config, indent=2))
    html = replace_block(html, "ITEMS", json.dumps(items, indent=1))

    if not apply_it:
        print(f"Dry run. Would write:\n  {OUT_HTML}\n  {OUT_DEC}\n  {PANELS}/*.png")
        for it in items:
            print(f"  [{ 'thumb' if it['thumb'] else 'NO-THUMB'}] {it['id']:26} {it['effect'][:66]}…")
        return 0

    OUT_HTML.write_text(html, encoding="utf-8")
    OUT_DEC.write_text(json.dumps({
        "sheetId": config["sheetId"],
        "posture": "whitelist",
        "decidedCount": 0,
        "decisions": prefill,
        "frozen": False,
    }, indent=2), encoding="utf-8")
    print(f"wrote {OUT_HTML}\nwrote {OUT_DEC}\nwrote {len(items)} panels -> {PANELS}")
    return 0


def replace_block(html, block_id, payload):
    open_tag = f'<script id="{block_id}" type="application/json">'
    i = html.index(open_tag) + len(open_tag)
    j = html.index("</script>", i)
    return html[:i] + "\n" + payload + "\n" + html[j:]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the sheet, panels and prefill")
    args = ap.parse_args()
    if not TEMPLATE.exists():
        print(f"missing template: {TEMPLATE}", file=sys.stderr)
        return 2
    return build(args.apply)


if __name__ == "__main__":
    sys.exit(main())
