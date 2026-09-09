#!/usr/bin/env python3
"""gen_flora_assignment_sheet.py — the owner's override surface for the landed flora cast.

Companion to gen_fauna_assignment_sheet.py, same pass (BIOME_FAUNA_ASSIGNMENT_SITTING_1,
owner card 4: purge Earth-nameable planet-wide, refill from the best available alien donor,
thin is acceptable, and every sheet-demanded signature plant becomes a NEW-ART/DEF item).

Three kinds of row:
  * every landed flora row, grouped by biome sheet;
  * one purge summary per biome that lost plants, so the Earth-nameable purge is visible as
    a decision rather than as an absence;
  * the NEW ART/DEF ledger, in its own groups — these rows decide the new-art queue.

Same freeze discipline as the fauna generator (review-sheets skill §7): the HTML is always
safe to regenerate; the decisions file refuses to overwrite anything the sheet has stamped.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROSTERS = HERE.parent / "biomes" / "rosters"
PLANT_REGISTER = HERE / "plant_register_rows.json"
SHEET = HERE / "flora_assignment_register.html"
DECISIONS = HERE / "flora_assignment_register.decisions.json"

TEMPLATE_CANDIDATES = [
    pathlib.Path.home() / ".claude/skills/review-sheets/assets/sheet_template.html",
    pathlib.Path("/home/mandrake/.claude/skills/review-sheets/assets/sheet_template.html"),
]

NATIVE_DIR = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review"

LEDGER_PLANTS = "\U0001f195 NEW ART/DEF ledger \u2014 plants \u00b7 Keep = COMMISSION \u00b7 Defer \u00b7 Drop"
LEDGER_OTHER = "\U0001f195 NEW ART/DEF ledger \u2014 creatures & mechanics \u00b7 Keep = COMMISSION \u00b7 Defer \u00b7 Drop"

FLAGGED_STATUS = re.compile(
    r"CONFLICT|CONTRADICT|OWNER|FLAG|HELD|PENDING|DEFER|CAVEAT|PARTIAL|DISCREPANCY"
    r"|NOT FOUND|MEASURED-CONTRARY|^open|^DESIGN$|DESIGN INTENT",
    re.I,
)
CLOSED_STATUS = re.compile(r"^RESOLV|^RECONCIL|^DONE|^DECIDED|^N/A|^EXCLUDED", re.I)
UNMEASURED_NEEDS_OWNER = re.compile(
    r"owner review|owner sheet|owner eye|open call|may override|eye test|unruled", re.I
)
FLORA_WORDS = re.compile(r"plant|flora|wildPlants|shroom|scraggl|tree|grass|lichen|moss", re.I)
FAUNA_WORDS = re.compile(r"creature|fauna|animal|predator|herd|flier", re.I)

CONTESTED = "\u26a0 contested \u2014 the flora calls that need YOUR eye"


def load_template() -> str:
    for path in TEMPLATE_CANDIDATES:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    sys.exit(
        "cannot find the review-sheets template. Expected one of:\n  "
        + "\n  ".join(str(p) for p in TEMPLATE_CANDIDATES)
        + "\nThe chrome is not ours to author \u2014 install the skill or pass --template."
    )


def num(value) -> str:
    if value is None:
        return "?"
    text = f"{float(value):.4f}".rstrip("0").rstrip(".")
    return text or "0"


def words(text: str, limit: int) -> str:
    parts = str(text or "").split()
    return " ".join(parts) if len(parts) <= limit else " ".join(parts[:limit]) + "\u2026"


def read_rosters() -> list[dict]:
    out = []
    for path in sorted(ROSTERS.glob("*.json")):
        if path.name.startswith("_"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["_file"] = path.name
        out.append(doc)
    return out


def group_name(doc: dict) -> str:
    defs = ", ".join(doc.get("defNames") or []) or "\u2014"
    tiles = doc.get("tiles")
    tail = f" \u00b7 {tiles:,} tiles" if isinstance(tiles, int) else ""
    return f"{doc['sheet']} \u00b7 {defs}{tail}"


def plant_shape(row: dict) -> str:
    """What this plant IS on the ground, in three words. A defName is not a decision aid."""
    if row.get("isTree"):
        return "tree"
    size = row.get("visualSizeMax")
    if isinstance(size, (int, float)) and size >= 0.9:
        return "bush"
    if row.get("cavePlant"):
        return "cave growth"
    return "ground cover"


def build_items(sheets: list[dict], plants: dict) -> list[dict]:
    contested: list[dict] = []
    flora_rows: list[dict] = []
    purge_rows: list[dict] = []
    ledger_plants: list[dict] = []
    ledger_other: list[dict] = []

    for doc in sheets:
        gname = group_name(doc)
        own_defs = set(doc.get("defNames") or [])
        sheet_flora = {e["def"] for e in (doc.get("flora") or [])}

        for entry in doc.get("flora") or []:
            defname = entry["def"]
            row = plants.get(defname) or {}
            art = (row.get("art") or {}).get("scale")
            zeroed_here = [b["biomeDef"] for b in (row.get("zeroedBiomes") or [])
                           if b.get("biomeDef") in own_defs]
            bits = [plant_shape(row)]
            if row.get("growDays"):
                bits.append(f"grows {num(row['growDays'])}d")
            if row.get("cavePlant"):
                bits.append("cave-only")
            if str(row.get("pollution") or "").lower() not in ("", "any", "none"):
                bits.append(f"pollution: {row['pollution']}")
            product = row.get("product")
            if isinstance(product, dict) and (product.get("label") or product.get("defName")):
                bits.append(f"yields {product.get('label') or product['defName']}")
            effect = (f"comm {num(entry.get('commonality'))} \u00b7 " + " \u00b7 ".join(bits))
            law = entry.get("law") or ""
            if entry.get("note"):
                law += f"  \u2014 {entry['note']}"
            item = {
                "id": f"p:{doc['sheet']}:{defname}",
                "label": row.get("label") or defname,
                "group": gname,
                "thumb": art,
                "effect": effect,
                "law": law,
                "prefill": "keep",
                "inferred": "UNMEASURED" in law,
                "zeroed": zeroed_here[0] if zeroed_here else None,
            }
            if re.search(r"CONFLICT|flagged|flag for|owner review|interim|stand-in|placeholder",
                         law, re.I):
                item["contested"] = True
                item["group"] = CONTESTED
                item["origin"] = f"landed in {doc['sheet']}"
                contested.append(item)
            else:
                flora_rows.append(item)

        # ── one purge summary per biome that lost plants ─────────────────────────────
        purged = doc.get("flora_purged") or []
        if purged:
            earth = [p for p in purged if re.search(r"earth-nameable", p.get("reason", ""), re.I)]
            others = [p for p in purged if p not in earth]
            # label alone repeats ("grass, grass, grass") — six different defs really are all
            # called "grass", so the defName is the only thing that tells them apart.
            names = [f"{plants.get(p['def'], {}).get('label') or p['def']} ({p['def']})"
                     for p in purged]
            effect = (
                f"{len(purged)} plants removed from this biome \u2014 {len(earth)} as "
                f"Earth-nameable (owner card 4)"
                + (f", {len(others)} on sheet law" if others else "")
                + f". Left standing: {len(sheet_flora)} rostered plants."
            )
            purge_rows.append({
                "id": f"purge:{doc['sheet']}",
                "label": f"PURGE \u2014 {doc['sheet']}",
                "group": gname,
                "thumb": None,
                "effect": effect,
                "law": "Removed: " + ", ".join(sorted(names))
                       + "  \u2014 restore any of these by overruling this row to Keep and "
                         "naming them in the note.",
                "prefill": "purge",
                "inferred": False,
                "zeroed": None,
            })

        # ── the NEW ART/DEF ledger ───────────────────────────────────────────────────
        for index, new in enumerate(doc.get("new_defs") or []):
            kind = (new.get("kind") or "?").lower()
            load = new.get("mechanic_load") or "none"
            item = {
                "id": f"nd:{doc['sheet']}:{index}",
                "label": words(new.get("name") or "(unnamed)", 12),
                "group": LEDGER_PLANTS if kind == "plant" else LEDGER_OTHER,
                "thumb": None,
                "effect": f"NEW {kind} for {doc['sheet']} \u00b7 code needed: {words(load, 14)}",
                "law": f"demanded by {new.get('from_sheet') or doc['sheet']}"
                       f" \u2014 {new.get('name') or ''}"
                       + (f" \u2014 mechanic load: {load}" if load and load != "none" else ""),
                "prefill": "keep",
                "inferred": False,
                "zeroed": None,
            }
            (ledger_plants if kind == "plant" else ledger_other).append(item)

        # ── confidence[] calls about PLANTS (the fauna sheet takes the rest) ──────────
        for index, conf in enumerate(doc.get("confidence") or []):
            status = str(conf.get("status") or "")
            text = f"{conf.get('claim', '')} {conf.get('why', '')}"
            invites = bool(UNMEASURED_NEEDS_OWNER.search(text))
            open_call = (
                (bool(FLAGGED_STATUS.search(status))
                 or (status.upper().startswith("UNMEASURED") and invites))
                and not CLOSED_STATUS.search(status)
            ) or (CLOSED_STATUS.search(status) and invites)
            if not open_call:
                continue
            purged_defs = {p["def"] for p in purged}
            about_plants = any(
                re.search(rf"\b{re.escape(d)}\b", text) for d in sheet_flora | purged_defs
            ) or (FLORA_WORDS.search(text) and not FAUNA_WORDS.search(text))
            if not about_plants:
                continue
            contested.append({
                "id": f"c:{doc['sheet']}:{index}",
                "label": f"[{doc['sheet']}] {words(conf.get('claim'), 12)}",
                "group": CONTESTED,
                "thumb": None,
                "effect": f"UNSETTLED CLAIM [{status}] \u2014 {words(conf.get('why'), 22)}",
                "law": f"{conf.get('claim')} \u2014 {conf.get('why')}",
                "prefill": "defer",
                "contested": True,
                "inferred": status.upper().startswith("UNMEASURED"),
                "zeroed": None,
                "origin": f"confidence[] on {doc['sheet']}",
                "openNote": "left undecided on purpose: the pass could not settle this from "
                            "sheet law alone.",
            })

    for item in contested:
        item["contested"] = True
    contested.sort(key=lambda it: (it["id"].split(":")[0], it["label"].lower()))
    merged: list[dict] = []
    by_group: dict[str, list[dict]] = {}
    for item in flora_rows + purge_rows:
        by_group.setdefault(item["group"], []).append(item)
    for gname in sorted(by_group):
        rows = by_group[gname]
        rows.sort(key=lambda it: (it["id"].startswith("purge:"), it["label"].lower()))
        merged.extend(rows)
    return contested + merged + ledger_plants + ledger_other


CRITERION = (
    "Rows pass their biome sheet's admission tests \u2014 which rank LAWFULNESS, not worth; "
    "commonality values are agent-chosen throughout."
)

INVENTED = [
    "Every commonality value on every flora row is agent-chosen. Nothing measures how much "
    "of a plant a biome should carry \u2014 these are a first pass at relative abundance.",
    "Interim flora stand-ins: where a sheet demands a signature plant that does not exist, "
    "the biome is held together by the best-available alien donor plant and the real one sits "
    "in the NEW ART/DEF ledger. Those donor rows are place-holders, not designs \u2014 several "
    "biomes are thin on purpose and will read thin until the ledger is commissioned.",
    "\"Earth-nameable\" was applied by NAME, one agent's reading of each label. A plant whose "
    "label reads as a species you could point at on Earth was purged; the judgement is "
    "unverified per row and the purge summary lists exactly what went.",
    "Thin is acceptable (owner card 4) \u2014 so where the alien donor pool ran out, the pass "
    "left the biome sparse rather than refilling it with a near-miss. That is a choice, and "
    "the opposite choice is available to you row by row.",
    "The NEW ART/DEF ledger is a list of things the sheets DEMAND, not things anyone has "
    "agreed to build. Nothing here is authored (owner card: new creatures and plants are not "
    "authored in this pass) \u2014 Keep on a ledger row commissions it as a queue item.",
    "The ledger's creature and mechanic rows are carried on this sheet rather than the fauna "
    "one, because the new-art queue is one queue and splitting it across two sheets with "
    "different verbs would lose half of it.",
    "The Mynock \u22642-home resolution, the Aerofleet Fumerider exception, and the Dunealisk "
    "and Skalder imports are fauna calls \u2014 they are declared on the fauna sheet and named "
    "here so this page is not read as the whole of the pass's invented rules.",
]


def brief_html(counts: dict) -> str:
    return (
        "<p><b>The pass:</b> BIOME_FAUNA_ASSIGNMENT_SITTING_1, flora half \u2014 landed "
        f"2026-09-09. <b>{counts['flora']}</b> landed plant rows across "
        f"<b>{counts['biomes']}</b> biome sheets, <b>{counts['purge']}</b> purge summaries "
        f"covering <b>{counts['purged']}</b> removed plants, and <b>{counts['ledger']}</b> "
        "entries in the NEW ART/DEF ledger.</p>"
        "<p><b>The four owner cards this pass ran on (2026-09-09):</b> "
        "<b>1. Land now, review after</b> \u2014 the roster data and the generated wildPlants "
        "patches are already committed on the agent's calls; this sheet is the override "
        "surface. "
        "<b>2. The homeless pool defaults to reserve-for-events</b> (fauna side). "
        "<b>3. SW staples adjust-and-keep</b> (fauna side). "
        "<b>4. Flora: purge Earth-nameable planet-wide now, refill from the best available "
        "alien donor per sheet law, thin is acceptable</b> \u2014 sparseness is doctrine in "
        "half these biomes \u2014 <b>and every sheet-demanded signature plant becomes a "
        "NEW-ART/DEF queue item.</b> That card is what this sheet records.</p>"
        "<p><b>What a verdict here drives:</b> plant verdicts amend the roster JSONs under "
        "<code>design/Jawa/worldbuilding/biomes/rosters/</code> and the wildPlants patches are "
        "regenerated from them. <b>Ledger verdicts decide the new-art queue</b> \u2014 Keep "
        "files it as a queue item and it gets drawn; Defer parks it; Drop kills it, and the "
        "biome that asked for it stays thin permanently.</p>"
        "<p><b>The controls:</b> "
        "<b>Keep</b> the row as landed \u2014 <i>on a ledger row this means COMMISSION it</i> \u00b7 "
        "<b>Thin</b> \u2014 keep it but less of it, <i>say how much in the note</i> \u00b7 "
        "<b>Purge</b> \u2014 take it out of this biome (on a purge-summary row, Purge means the "
        "removal stands; overrule to <b>Keep</b> to restore, naming what in the note) \u00b7 "
        "<b>Defer</b> \u00b7 <b>Drop</b> \u2014 the ledger's park and kill. "
        "The note is worth more than the verdict.</p>"
        f"<p><b>Read the \u26a0 contested group first</b> \u2014 {counts['contested']} rows: the "
        "interim stand-ins that are holding a biome together, and the confidence[] claims about "
        "plants that no measurement closed.</p>"
        "<p class='sub'>Marks: <b>\u25c6 contested</b> = defensible both ways. "
        "<b>\u26a0 UNMEASURED</b> = the law line rests on by-name knowledge, not the register. "
        "<b>\u2298 zeroed</b> = Cherry Picker zeroes this def in this very biome, so the row "
        "will not spawn until the cut is lifted. Plant facts (shape, grow days, cave, "
        "pollution, yield) are read from "
        "<code>plant_register_rows.json</code>; commonality is ours.</p>"
    )


RENDER_BLOCK = """
<script id="RENDER">
  window.itemBody = it => {
    const marks = [];
    if (it.contested) marks.push('<span class="mark contested" title="defensible both ways \\u2014 the pass could not settle it from sheet law alone">\\u25c6 contested</span>');
    if (it.inferred)  marks.push('<span class="mark inferred" title="rests on by-name knowledge, not the register">\\u26a0 UNMEASURED</span>');
    if (it.zeroed)    marks.push('<span class="mark ovr" title="Cherry Picker zeroes this def in this biome \\u2014 the row cannot spawn until the cut is lifted">\\u2298 zeroed in ' + esc(it.zeroed) + '</span>');
    if (it.origin)    marks.push('<span class="mark absent">' + esc(it.origin) + '</span>');
    return '<div class="effect">' + esc(it.effect || '') + '</div>'
         + (it.law ? '<div class="sub" style="margin-top:3px">' + esc(it.law) + '</div>' : '')
         + (marks.length ? '<div class="marks">' + marks.join('') + '</div>' : '');
  };
</script>
"""


def fill(template: str, config: dict, items: list[dict]) -> str:
    out = re.sub(
        r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(config, indent=2, ensure_ascii=False) + m.group(2),
        template, count=1, flags=re.S,
    )
    out = re.sub(
        r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(items, indent=1, ensure_ascii=False) + m.group(2),
        out, count=1, flags=re.S,
    )
    anchor = '<script>\n"use strict";'
    if anchor not in out:
        sys.exit("template changed shape: could not find the main <script> to insert RENDER before")
    return out.replace(anchor, RENDER_BLOCK.strip() + "\n\n" + anchor, 1)


def guard_decisions(path: pathlib.Path, force: bool) -> None:
    if not path.is_file() or force:
        return
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if doc.get("savedBy") or doc.get("writeCount") or doc.get("frozen"):
        sys.exit(
            f"REFUSING to overwrite {path.name}: it carries savedBy={doc.get('savedBy')!r} "
            f"writeCount={doc.get('writeCount')!r} frozen={doc.get('frozen')!r} \u2014 keys "
            "only the sheet's own plumbing writes. These are the OWNER's decisions.\n"
            "If you genuinely mean to throw them away, re-run with "
            "--i-know-this-overwrites-the-owners-decisions."
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sheet-only", action="store_true")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true",
                    dest="force")
    ap.add_argument("--template")
    args = ap.parse_args()
    if args.template:
        TEMPLATE_CANDIDATES.insert(0, pathlib.Path(args.template))

    sheets = read_rosters()
    plants = {r["defName"]: r
              for r in json.loads(PLANT_REGISTER.read_text(encoding="utf-8"))["rows"]}
    items = build_items(sheets, plants)

    for item in items:
        if item.get("thumb") and not (HERE / item["thumb"]).is_file():
            item["thumb"] = None

    counts = {
        "flora": sum(1 for it in items if it["id"].startswith("p:")),
        "purge": sum(1 for it in items if it["id"].startswith("purge:")),
        "purged": sum(len(d.get("flora_purged") or []) for d in sheets),
        "ledger": sum(1 for it in items if it["id"].startswith("nd:")),
        "biomes": len(sheets),
        "contested": sum(1 for it in items if it.get("contested")),
        "rows": len(items),
    }

    config = {
        "sheetId": "flora_assignment_register",
        "title": "Flora assignment register \u2014 Ash'karr",
        "subtitle": f"{counts['flora']} landed plants \u00b7 {counts['purge']} purge summaries "
                    f"\u00b7 {counts['ledger']} new-art ledger \u00b7 "
                    f"{counts['contested']} contested",
        "briefHtml": brief_html(counts),
        "criterion": CRITERION,
        "invented": INVENTED,
        "posture": {
            "mode": "blacklist",
            "explain": "LANDED unless you overrule \u2014 every row below is already committed "
                       "data. Your overrides amend the roster JSONs and the patches are "
                       "regenerated from them; rows you leave alone stand exactly as they are.",
        },
        "options": [
            {"key": "keep",  "label": "Keep",  "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "thin",  "label": "Thin",  "hotkey": "2", "color": "#e8b64c", "counts": "in"},
            {"key": "purge", "label": "Purge", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
            {"key": "defer", "label": "Defer", "hotkey": "4", "color": "#6aa6e8", "counts": "out"},
            {"key": "drop",  "label": "Drop",  "hotkey": "5", "color": "#98a2b3", "counts": "out"},
        ],
        "groupLabel": "biome sheet",
        "media": True,
        "decisionsFile": DECISIONS.name,
        "decisionsPath": NATIVE_DIR + "\\" + DECISIONS.name,
        "sheetPath": NATIVE_DIR + "\\" + SHEET.name,
    }

    SHEET.write_text(fill(load_template(), config, items), encoding="utf-8")
    print(f"wrote {SHEET}  ({counts['rows']} rows: {counts['flora']} flora, "
          f"{counts['purge']} purge, {counts['ledger']} ledger, "
          f"{counts['contested']} contested, "
          f"{sum(1 for i in items if i.get('thumb'))} thumbs)")

    if args.sheet_only:
        return 0

    guard_decisions(DECISIONS, args.force)
    doc = {
        "sheet": "flora_assignment_register",
        "posture": "blacklist",
        "postureMeaning": "LANDED unless overruled. Rows with no entry stand as landed.",
        "criterion": CRITERION,
        "generatedBy": "gen_flora_assignment_sheet.py",
        "generatedFrom": "design/Jawa/worldbuilding/biomes/rosters/*.json @ 2026-09-09",
        "invented": INVENTED,
        "decisions": {
            it["id"]: {"decision": it["prefill"], "prefill": it["prefill"],
                       "note": it.get("openNote") or ""}
            for it in items
        },
    }
    DECISIONS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {DECISIONS}  ({len(doc['decisions'])} pre-filled rows \u2014 agent's guesses)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
