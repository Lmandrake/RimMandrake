#!/usr/bin/env python3
"""gen_fauna_assignment_sheet.py — the owner's override surface for the landed fauna cast.

BIOME_FAUNA_ASSIGNMENT_SITTING_1, owner card 1: "land now, review after". The rosters in
design/Jawa/worldbuilding/biomes/rosters/*.json ARE the landed data; this builds the sheet
that lets the owner overrule any row of it.

Two outputs, and only ONE of them is dangerous to re-run (review-sheets skill §7):

  fauna_assignment_register.html            SAFE to regenerate at any time. It renders from
                                            the decisions file at runtime, so a fixed
                                            renderer can be picked up mid-review.
  fauna_assignment_register.decisions.json  THE AGENT'S GUESSES. Refuses to overwrite a file
                                            the sheet has written (savedBy/writeCount) or a
                                            frozen one, unless
                                            --i-know-this-overwrites-the-owners-decisions.

    python3 gen_fauna_assignment_sheet.py            # both, guarded
    python3 gen_fauna_assignment_sheet.py --sheet-only

The chrome is NOT ours: assets/sheet_template.html from the review-sheets skill is copied
verbatim and only its CONFIG / ITEMS / RENDER blocks are filled.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROSTERS = HERE.parent / "biomes" / "rosters"
REGISTER = HERE / "creature_register_rows.json"
SHEET = HERE / "fauna_assignment_register.html"
DECISIONS = HERE / "fauna_assignment_register.decisions.json"

TEMPLATE_CANDIDATES = [
    pathlib.Path.home() / ".claude/skills/review-sheets/assets/sheet_template.html",
    pathlib.Path("/home/mandrake/.claude/skills/review-sheets/assets/sheet_template.html"),
]

NATIVE_DIR = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review"

# Rows landed with this action carry a stat change, so their landed call IS "adjust".
ACTION_PREFILL = {"keep": "keep", "import": "keep", "adjust-keep": "adjust"}

# A confidence[] row is contested when its status says a human still has to look. Statuses
# that merely record a measurement (MEASURED, RESOLVED, RULED, N/A, DONE...) are not.
FLAGGED_STATUS = re.compile(
    r"CONFLICT|CONTRADICT|OWNER|FLAG|HELD|PENDING|DEFER|CAVEAT|PARTIAL|DISCREPANCY"
    r"|NOT FOUND|MEASURED-CONTRARY|^open|^DESIGN$|DESIGN INTENT",
    re.I,
)
# Anything already RESOLVED — including "RESOLVED WRONG", which records an error the pass
# then corrected — is closed. It is provenance, not an open call.
CLOSED_STATUS = re.compile(r"^RESOLV|^RECONCIL|^DONE|^DECIDED|^N/A|^EXCLUDED", re.I)
# A confidence[] claim about plants belongs on the flora sheet, not this one.
FLORA_WORDS = re.compile(r"plant|flora|wildPlants|shroom|scraggl|tree|grass|lichen|moss", re.I)
# UNMEASURED only counts as contested when the row itself says the owner has to settle it.
UNMEASURED_NEEDS_OWNER = re.compile(
    r"owner review|owner sheet|owner eye|open call|may override|eye test|unruled", re.I
)
REVIEW_FLAG = re.compile(r"CONFLICT|flagged|flag for|owner review", re.I)


def load_template() -> str:
    for path in TEMPLATE_CANDIDATES:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    sys.exit(
        "cannot find the review-sheets template. Expected one of:\n  "
        + "\n  ".join(str(p) for p in TEMPLATE_CANDIDATES)
        + "\nThe chrome is not ours to author — install the skill or pass --template."
    )


def num(value) -> str:
    """1.0 -> '1', 0.05 -> '0.05'. Commonality values read as noise with trailing zeros."""
    if value is None:
        return "?"
    text = f"{float(value):.4f}".rstrip("0").rstrip(".")
    return text or "0"


def words(text: str, limit: int) -> str:
    parts = str(text or "").split()
    return " ".join(parts) if len(parts) <= limit else " ".join(parts[:limit]) + "…"


def read_rosters() -> tuple[list[dict], dict]:
    sheets = []
    for path in sorted(ROSTERS.glob("*.json")):
        if path.name.startswith("_"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["_file"] = path.name
        sheets.append(doc)
    glob = json.loads((ROSTERS / "_global.json").read_text(encoding="utf-8"))
    return sheets, glob


def group_name(doc: dict) -> str:
    defs = ", ".join(doc.get("defNames") or []) or "—"
    tiles = doc.get("tiles")
    tail = f" · {tiles:,} tiles" if isinstance(tiles, int) else ""
    return f"{doc['sheet']} · {defs}{tail}"


CONTESTED = "\u26a0 contested — the calls that need YOUR eye"


def build_items(sheets: list[dict], glob: dict, reg: dict) -> list[dict]:
    contested_rows: list[dict] = []
    biome_rows: list[dict] = []
    flagged_ids: dict[str, dict] = {}

    for doc in sheets:
        gname = group_name(doc)
        own_defs = set(doc.get("defNames") or [])
        adjustments: dict[str, list[str]] = {}
        for adj in doc.get("stat_adjustments") or []:
            adjustments.setdefault(adj["def"], []).append(
                f"{adj.get('field')} {num(adj.get('from'))}\u2192{num(adj.get('to'))}"
            )

        for entry in doc.get("fauna") or []:
            defname = entry["def"]
            row = reg.get(defname) or {}
            art = (row.get("art") or {}).get("scale")
            law = entry.get("law") or ""
            note = entry.get("note") or ""
            ubex = entry.get("ubiquity_exception")
            blob = f"{law} {note} {ubex or ''}"

            zeroed_here = [
                b["biomeDef"]
                for b in (row.get("zeroedBiomes") or [])
                if b.get("biomeDef") in own_defs
            ]
            stats = f"bs {num(row.get('bodySize'))} spd {num(row.get('moveSpeed'))}"
            tuned = adjustments.get(defname)
            effect = (
                f"{entry.get('band', '?')} \u00b7 {stats} (MEASURED) \u00b7 comm "
                f"{num(entry.get('commonality'))}"
                + (f" \u00b7 tuned: {'; '.join(tuned)}" if tuned else "")
            )
            detail = law
            if note:
                detail += f"  \u2014 {note}"
            if ubex:
                detail += f"  \u2014 ubiquity-25 exception: {ubex}"

            item = {
                "id": f"f:{doc['sheet']}:{defname}",
                "label": row.get("label") or defname,
                "group": gname,
                "thumb": art,
                "effect": effect,
                "law": detail,
                "prefill": ACTION_PREFILL.get(entry.get("action"), "keep"),
                "inferred": "UNMEASURED" in blob,
                "zeroed": zeroed_here[0] if zeroed_here else None,
                "biome": gname,
            }
            if ubex or REVIEW_FLAG.search(blob):
                item["contested"] = True
                item["group"] = CONTESTED
                item["origin"] = f"landed in {doc['sheet']}"
                contested_rows.append(item)
            else:
                biome_rows.append(item)
            flagged_ids[f"{doc['sheet']}|{defname}"] = item

        # ── flagged evictions: a def the pass sent home with a conflict on the record ──
        for entry in doc.get("evictions") or []:
            reason = entry.get("reason") or ""
            note = entry.get("note") or ""
            if not REVIEW_FLAG.search(f"{reason} {note}"):
                continue
            defname = entry["def"]
            row = reg.get(defname) or {}
            disp = entry.get("disposition") or "homeless-reserve"
            prefill = "move" if disp.startswith("move:") else "evict"
            contested_rows.append({
                "id": f"e:{doc['sheet']}:{defname}",
                "label": row.get("label") or defname,
                "group": CONTESTED,
                "thumb": (row.get("art") or {}).get("scale"),
                "effect": (
                    f"EVICTED from {doc['sheet']} \u00b7 bs {num(row.get('bodySize'))} "
                    f"spd {num(row.get('moveSpeed'))} (MEASURED) \u00b7 {disp}"
                ),
                "law": f"{reason}{('  \u2014 ' + note) if note else ''}",
                "prefill": prefill,
                "contested": True,
                "inferred": "UNMEASURED" in f"{reason} {note}",
                "zeroed": None,
                "origin": f"evicted from {doc['sheet']}",
            })

        # ── confidence[] calls the pass could not close ──────────────────────────────
        for index, conf in enumerate(doc.get("confidence") or []):
            status = str(conf.get("status") or "")
            claim = conf.get("claim") or ""
            why = conf.get("why") or ""
            text = f"{claim} {why}"
            invites_owner = bool(UNMEASURED_NEEDS_OWNER.search(text))
            open_call = (
                (bool(FLAGGED_STATUS.search(status))
                 or (status.upper().startswith("UNMEASURED") and invites_owner))
                and not CLOSED_STATUS.search(status)
            ) or (CLOSED_STATUS.search(status) and invites_owner)
            if not open_call:
                continue
            # Attach to the landed row it is about, rather than making a second row the
            # owner has to reconcile by hand.
            attached = [
                key for key in flagged_ids
                if key.startswith(f"{doc['sheet']}|")
                and re.search(rf"\b{re.escape(key.split('|', 1)[1])}\b", text)
            ]
            if not attached:
                flora_defs = {e["def"] for e in (doc.get("flora") or [])
                              } | {e["def"] for e in (doc.get("flora_purged") or [])}
                if any(re.search(rf"\b{re.escape(d)}\b", text) for d in flora_defs) or (
                        FLORA_WORDS.search(text) and not re.search(r"creature|fauna|animal|predator|herd|flier", text, re.I)):
                    continue  # the flora sheet carries this one
            if attached:
                for key in attached:
                    item = flagged_ids[key]
                    item["contested"] = True
                    item["law"] = f"{item['law']}  \u2014 OPEN [{status}]: {claim} \u2014 {why}"
                    if item in biome_rows:
                        biome_rows.remove(item)
                        item["group"] = CONTESTED
                        item["origin"] = f"landed in {doc['sheet']}"
                        contested_rows.append(item)
                continue
            contested_rows.append({
                "id": f"c:{doc['sheet']}:{index}",
                "label": f"[{doc['sheet']}] {words(claim, 12)}",
                "group": CONTESTED,
                "thumb": None,
                "effect": f"UNSETTLED CLAIM [{status}] \u2014 {words(why, 22)}",
                "law": f"{claim} \u2014 {why}",
                "prefill": "open",
                "contested": True,
                "inferred": status.upper().startswith("UNMEASURED"),
                "zeroed": None,
                "origin": f"confidence[] on {doc['sheet']}",
                "openNote": "left undecided on purpose: the pass could not settle this "
                            "from sheet law alone.",
            })

    # ── the in-joke calibration animal with no home, straight from _global ────────────
    in_jokes = ((glob.get("ruled") or {}).get("in_jokes_kept_reskinned") or {})
    for defname, text in in_jokes.items():
        if defname in {key.split("|", 1)[1] for key in flagged_ids}:
            continue  # it landed somewhere; not homeless
        row = reg.get(defname) or {}
        contested_rows.append({
            "id": f"h:{defname}",
            "label": row.get("label") or defname,
            "group": CONTESTED,
            "thumb": (row.get("art") or {}).get("scale"),
            "effect": (
                f"NO WILD HOME LANDED \u00b7 bs {num(row.get('bodySize'))} "
                f"spd {num(row.get('moveSpeed'))} (MEASURED) \u00b7 reserve-for-events only"
            ),
            "law": f"_global.json in_jokes_kept_reskinned: {text}",
            "prefill": "evict",
            "contested": True,
            "inferred": False,
            "zeroed": None,
            "origin": "_global.json",
            "openNote": "",
        })

    contested_rows.sort(key=lambda it: (it["id"].split(":")[0], it["label"].lower()))
    biome_rows.sort(key=lambda it: (it["group"], -float(it["effect"].split("comm ")[1].split()[0])
                                    if "comm " in it["effect"] else 0))
    return contested_rows + biome_rows


CRITERION = (
    "Rows pass their biome sheet's admission tests \u2014 which rank LAWFULNESS, not worth; "
    "commonality values are agent-chosen throughout."
)

INVENTED = [
    "Every commonality value on every row is agent-chosen. No sheet, ruling or measurement "
    "fixes them \u2014 they are a first pass at relative abundance and nothing else.",
    "Mynock's \u22642-named-homes resolution: poison forest + the Scarlands. The Rust Cathedral's "
    "own frozen sheet also rosters mynock flocks; that third home was dropped to satisfy "
    "prep \u00a79's trim, using R17 (fliers cross biomes) as the cover story.",
    "AA_Aerofleet keeps a named home in the Forge as the \"Fumerider\" \u2014 an exception taken "
    "against prep \u00a79's terminator-adjacent-only trim, on the argument that a sheet's own "
    "ruled name outranks the prep's guess.",
    "AA_Dunealisk imported into the merged dune sea / deep desert as its single legal "
    "subsurface predator, and the Skalder imported likewise \u2014 neither import is named by a "
    "sheet; both were chosen to fill an archetype the sheet demanded and had no def for.",
    "Interim flora stand-ins: several biomes are held together by the best-available alien "
    "donor plant while the sheet-demanded signature plant sits in the NEW-ART ledger. Those "
    "rows are place-holders, not designs.",
    "Sending a def home is 'reserve-for-events' by default (owner card 2), so an eviction "
    "here never means the def dies \u2014 only that it stops spawning wild.",
    "The 'contested' set is the agent's own reading of which calls are defensible both ways: "
    "ubiquity-25 exceptions, rows whose own note records a conflict, and confidence[] entries "
    "no measurement closed. A quiet row is not a proven row.",
]


def brief_html(counts: dict) -> str:
    return (
        "<p><b>The pass:</b> BIOME_FAUNA_ASSIGNMENT_SITTING_1 \u2014 every wild-animal roster on "
        "Ash'karr, assigned from the frozen biome sheets, "
        f"landed 2026-09-09. <b>{counts['rows']}</b> landed rows across "
        f"<b>{counts['biomes']}</b> biome sheets, drawn from {counts['defs']} distinct defs; "
        f"{counts['reserve']} live wild creatures got no home and sit in "
        "reserve-for-events.</p>"
        "<p><b>The four owner cards this pass ran on (2026-09-09):</b> "
        "<b>1. Land now, review after</b> \u2014 the roster data and the generated "
        "wildAnimals patches are already committed on the agent's calls; this sheet is the "
        "override surface. "
        "<b>2. The homeless pool defaults to reserve-for-events</b> \u2014 no wild spawn "
        "anywhere, the def stays live for quests, raids and traders. Cherry Picker cuts only "
        "where already ruled. "
        "<b>3. SW staples adjust-and-keep</b> \u2014 Wraid and Gutkurr slowed under 4.5 to pass "
        "the pursuit ban, WarWyrm ruled a burrower, Mudhorn kept as the shrubland's one "
        "huge-predator exception. Icons survive by fitting the law, not by being icons. "
        "<b>4. Flora: purge Earth-nameable planet-wide</b> \u2014 tracked on the flora sheet.</p>"
        "<p><b>What a verdict here drives:</b> your overrides amend the roster JSONs under "
        "<code>design/Jawa/worldbuilding/biomes/rosters/</code>, and the wildAnimals patches "
        "are regenerated from them. Nothing is applied from this file until that regeneration "
        "runs, and the generator that wrote these guesses refuses to run over your answers.</p>"
        "<p><b>The controls:</b> "
        "<b>Keep</b> the row as landed \u00b7 "
        "<b>Evict</b> it from this biome (it falls to reserve-for-events, it does not die) \u00b7 "
        "<b>Move</b> it \u2014 <i>put the target biome in the note</i> \u00b7 "
        "<b>Adjust</b> \u2014 the row carries a change to commonality, stats or band. "
        f"{counts['adjust']} rows arrive pre-filled Adjust because the pass already tuned them "
        "(the tune is named in the row); leave it if the tune is right, or say in the note what "
        "it should be instead \u00b7 "
        "<b>Open</b> \u2014 still undecided, on purpose. "
        "The note is worth more than the verdict: a disagreement with a reason tells us the "
        "rule we got wrong, and a bare override only tells us one row.</p>"
        f"<p><b>Read the \u26a0 contested group first.</b> {counts['contested']} rows of "
        f"{counts['rows']} \u2014 every ubiquity-25 exception, every row whose own note records "
        "a conflict, every eviction flagged at the time, and every confidence[] claim no "
        "measurement closed. They carry nearly all the real judgement; the rest is the pass "
        "working through sheet law.</p>"
        "<p class='sub'>Marks: <b>\u25c6 contested</b> = defensible both ways (this row is in "
        "the contested group). <b>\u26a0 UNMEASURED</b> = a claim in the law line rests on "
        "by-name knowledge, not the register \u2014 the register's <code>flies</code> flag is "
        "broken and juvenile sizes are absent, so every flier and life-stage argument is one "
        "of these. <b>\u2298 zeroed</b> = Cherry Picker has this def zeroed in this very biome, "
        "so the row will not spawn until the cut is lifted. Every bs/spd figure is MEASURED "
        "from <code>creature_register_rows.json</code> (595-mod dump, 2026-09-05).</p>"
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
    """A comment saying 'do not run this' is not a guard (review-sheets skill §7)."""
    if not path.is_file() or force:
        return
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    stamped = doc.get("savedBy") or doc.get("writeCount") or doc.get("frozen")
    if stamped:
        sys.exit(
            f"REFUSING to overwrite {path.name}: it carries "
            f"savedBy={doc.get('savedBy')!r} writeCount={doc.get('writeCount')!r} "
            f"frozen={doc.get('frozen')!r} \u2014 keys only the sheet's own plumbing writes. "
            "These are the OWNER's decisions, not the pre-fill.\n"
            "If you genuinely mean to throw them away, re-run with "
            "--i-know-this-overwrites-the-owners-decisions."
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sheet-only", action="store_true",
                    help="rebuild the HTML only; never touch the decisions file")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true",
                    dest="force")
    ap.add_argument("--template", help="path to the review-sheets sheet_template.html")
    args = ap.parse_args()

    if args.template:
        TEMPLATE_CANDIDATES.insert(0, pathlib.Path(args.template))

    sheets, glob = read_rosters()
    reg = {r["defName"]: r for r in json.loads(REGISTER.read_text(encoding="utf-8"))["rows"]}
    items = build_items(sheets, glob, reg)

    missing_art = [it["id"] for it in items if it.get("thumb") and
                   not (HERE / it["thumb"]).is_file()]
    for item_id in missing_art:
        for item in items:
            if item["id"] == item_id:
                item["thumb"] = None

    counts = {
        "rows": len(items),
        "biomes": len(sheets),
        "defs": len({it["id"].split(":")[-1] for it in items if it["id"].startswith("f:")}),
        "reserve": (glob.get("measured") or {}).get("reserve_pool", "?"),
        "contested": sum(1 for it in items if it.get("contested")),
        "adjust": sum(1 for it in items if it["prefill"] == "adjust"),
    }

    config = {
        "sheetId": "fauna_assignment_register",
        "title": "Fauna assignment register \u2014 Ash'karr",
        "subtitle": f"{counts['rows']} landed rows \u00b7 {counts['biomes']} biome sheets "
                    f"\u00b7 {counts['contested']} contested",
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
            {"key": "keep",   "label": "Keep",   "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "adjust", "label": "Adjust", "hotkey": "2", "color": "#e8b64c", "counts": "in"},
            {"key": "move",   "label": "Move",   "hotkey": "3", "color": "#6aa6e8", "counts": "out"},
            {"key": "evict",  "label": "Evict",  "hotkey": "4", "color": "#e06c6c", "counts": "out"},
            {"key": "open",   "label": "Open",   "hotkey": "5", "color": "#98a2b3", "counts": "out"},
        ],
        "groupLabel": "biome sheet",
        "media": True,
        "decisionsFile": DECISIONS.name,
        "decisionsPath": NATIVE_DIR + "\\" + DECISIONS.name,
        "sheetPath": NATIVE_DIR + "\\" + SHEET.name,
    }

    SHEET.write_text(fill(load_template(), config, items), encoding="utf-8")
    print(f"wrote {SHEET}  ({counts['rows']} rows, {counts['contested']} contested, "
          f"{sum(1 for i in items if i.get('thumb'))} thumbs)")

    if args.sheet_only:
        return 0

    guard_decisions(DECISIONS, args.force)
    doc = {
        "sheet": "fauna_assignment_register",
        "posture": "blacklist",
        "postureMeaning": "LANDED unless overruled. Rows with no entry stand as landed.",
        "criterion": CRITERION,
        "generatedBy": "gen_fauna_assignment_sheet.py",
        "generatedFrom": "design/Jawa/worldbuilding/biomes/rosters/*.json @ 2026-09-09",
        "invented": INVENTED,
        "decisions": {
            it["id"]: {
                "decision": it["prefill"],
                "prefill": it["prefill"],
                "note": it.get("openNote") or "",
            }
            for it in items
        },
    }
    DECISIONS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {DECISIONS}  ({len(doc['decisions'])} pre-filled rows \u2014 agent's guesses)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
