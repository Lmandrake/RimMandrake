#!/usr/bin/env python3
"""gen_creature_art_register.py — CREATURE_ART_REVIEW_SHEET_1: the owner's art
verdict surface for every creature that is actually ON Ash'karr.

The 2026-08-23 sheet ranked 621 sprites by measurable art quality and the owner
froze his verdicts into design/Jawa/fauna/creature_art_decisions.json. Since then
the planet got a roster (BIOME_FAUNA_ASSIGNMENT_SITTING_1, 2026-09-09), which
changed the question: no longer "is this sprite good" over the whole mod stack,
but "is this sprite good ENOUGH FOR THE BIOME IT NOW LIVES IN". So this sheet is
grouped by biome, drawn at true relative in-game scale, and pre-filled by carrying
his frozen verdicts forward.

Three sources, in strict precedence:

  1. infrastructure/state/items/CREATURE_ART_REVIEW_SHEET_1.md  owner rulings of
     2026-09-06, hard-coded below as RULINGS_2026_09_06. Atispec and Revenant are
     CANCELLED and are never re-asked.
  2. design/Jawa/fauna/creature_art_decisions.json              owner-frozen
     2026-08-23. READ-ONLY here, always. This generator never writes it.
  3. the register's own art metrics                             agent guesses for
     rows source 1 and 2 say nothing about.

Two outputs, and only ONE of them is dangerous to re-run (review-sheets skill §7):

  creature_art_register.html            SAFE to regenerate at any time.
  creature_art_register.decisions.json  THE AGENT'S PRE-FILL. Refuses to overwrite
                                        a file the sheet has written (savedBy /
                                        writeCount) or a frozen one, unless
                                        --i-know-this-overwrites-the-owners-decisions.

    python3 gen_creature_art_register.py            # both, guarded
    python3 gen_creature_art_register.py --sheet-only

The chrome is NOT ours: assets/sheet_template.html from the review-sheets skill is
copied verbatim and only its CONFIG / ITEMS / RENDER blocks are filled.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from rosters_residency import load, load_register_stats  # noqa: E402

FROZEN = HERE.parent.parent / "fauna" / "creature_art_decisions.json"
SHEET = HERE / "creature_art_register.html"
DECISIONS = HERE / "creature_art_register.decisions.json"

TEMPLATE_CANDIDATES = [
    pathlib.Path.home() / ".claude/skills/review-sheets/assets/sheet_template.html",
    pathlib.Path("/home/mandrake/.claude/skills/review-sheets/assets/sheet_template.html"),
]

NATIVE_DIR = r"D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review"

# ── true relative in-game scale ───────────────────────────────────────────────
# creature_art/<def>.scale.png is already a TRUE-SCALE panel: the sprite contained
# in its drawSize box at RimWorld's own 64 px/cell, a 1-cell grid behind it and a
# constant 1.5-cell colonist beside it (gen_creature_register.py::_scale_panel).
# So every panel shares one physical ruler, and displaying each at its natural size
# times ONE global factor keeps every creature in true proportion to every other.
SRC_PX_PER_CELL = 64.0        # what the panels were rendered at
MAX_PANEL_PX = 380            # the cap: the biggest row's panel, longest side
HUMAN_CELLS = 1.5             # the colonist anchor drawn in every panel

# 2026-08-23 vocabulary -> this sheet's five options. The mapping is the agent's.
VERDICT_2026_08_23 = {
    "keep": "approve",
    "shrink": "revise",
    "replace": "replace",
    "redraw": "redraw",
}

# ── source 1: the owner's rulings of 2026-09-06 (item file), verbatim ─────────
RULINGS_2026_09_06 = {
    "AA_Atispec": ("cancel",
                   "CANCELLED, not parked (2026-09-06): \"Revenant and Atispec are separate "
                   "from the terrestrial three. They should just be dropped and no longer "
                   "reskinned. Unneeded.\" Not re-asked here; the row is on the sheet only so "
                   "nothing re-opens it by accident."),
    "Revenant": ("cancel",
                 "CANCELLED, not parked (2026-09-06): same ruling as Atispec. Also open, and "
                 "NOT an art question: \"Do we really NEED this?\" — whether the creature is "
                 "wanted in the campaign at all."),
    "Enhydriodon": ("redraw",
                    "REJECTED 2026-09-06: \"This is just some kind of lava beast, boring. Don't "
                    "need.\" A redraw is still owed, but it must find a different BODY PLAN — "
                    "the glowing-plate reskin of the terrestrial shape is refused."),
    "Gorilla": ("redraw",
                "REJECTED 2026-09-06: \"Again, these 'make a terrestrial shape made out of "
                "glowing plates' isn't a good solution.\" Redraw owed, different body plan."),
    "Capybara": ("revise",
                 "Left at revise 2026-09-06 (agent's own pre-fill; you did not override it). "
                 "The no-reskin constraint applies before another attempt."),
    "AA_Behemoth": ("approve",
                    "APPROVED 2026-09-06, overriding the 2026-08-23 redraw: \"Might be "
                    "interesting for the nightside beasts.\" Casting it there is a design "
                    "question for BENCH, not an art task."),
}

# The six flagged `replace` rows the owner never gave a reason for. Their verdict is
# HIS and stands; what is missing is the rationale, and nothing can be generated
# without it. They are the deliberately-undecided rows of this sheet.
NEEDS_RATIONALE = {
    "GR_Catbear", "BMT_SandPillar", "Horax",
    "BMT_BiliousVarog", "BMT_ShatterjawBeetle", "DA_BlackScribe",
}
RATIONALE_ASK = (
    "BLOCKED ON YOU: your 2026-08-23 `replace` stands, but it carries no reason, so "
    "nobody can generate a candidate that would satisfy it. Say in this note what is "
    "wrong with it — silhouette, legibility, too terrestrial, wrong register — and the "
    "art task becomes runnable."
)

VANILLA_K, VANILLA_P = 1.995, 0.375   # vanilla's own fitted size law (creature_size_model.md)

GROUP_RULED = "\u26a1 Ruled & flagged \u2014 off the roster"
GROUP_RESERVE = "\u2693 Reserve highlights \u2014 sea beasts and flagged reserves"


def load_template() -> str:
    for path in TEMPLATE_CANDIDATES:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    sys.exit(
        "cannot find the review-sheets template. Expected one of:\n  "
        + "\n  ".join(str(p) for p in TEMPLATE_CANDIDATES)
        + "\nThe chrome is not ours to author — install the skill or pass --template."
    )


def png_size(path: pathlib.Path) -> tuple[int, int] | None:
    """Width/height from the IHDR. Cheaper than PIL and this file has no other need."""
    try:
        with path.open("rb") as fh:
            head = fh.read(24)
    except OSError:
        return None
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def num(value) -> str:
    if value is None:
        return "?"
    text = f"{float(value):.4f}".rstrip("0").rstrip(".")
    return text or "0"


def draw_cells(row: dict) -> float | None:
    v = row.get("drawSize")
    if isinstance(v, list):
        vv = [x for x in v if isinstance(x, (int, float))]
        return max(vv) if vv else None
    return v if isinstance(v, (int, float)) else None


def mismatch(row: dict) -> float | None:
    bs, cells = row.get("bodySize"), draw_cells(row)
    if not bs or not cells:
        return None
    return cells / (VANILLA_K * bs ** VANILLA_P)


def biome_labels(reg: dict) -> dict[str, str]:
    lab: dict[str, str] = {}
    for row in reg.values():
        for b in (row.get("biomes") or []) + (row.get("zeroedBiomes") or []):
            lab.setdefault(b["biomeDef"], b["biome"])
    return lab


def build_rows(R, reg: dict) -> tuple[list[dict], dict]:
    """Every rostered def once, in its highest-commonality biome, plus the two
    off-roster groups. Returns (raw rows, stats)."""
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))["decisions"]
    labels = biome_labels(reg)
    rostered = set(R.residency)
    reserve = R.reserve

    def home(defname: str) -> tuple[str, float, list[str]]:
        rs = R.residency[defname]
        best = sorted(rs, key=lambda r: (-r.commonality, r.biome))[0]
        others = sorted({r.biome for r in rs} - {best.biome})
        return best.biome, best.commonality, others

    selected: list[tuple[str, str, dict]] = []      # (defName, group, extra)
    for defname in sorted(rostered):
        biome, comm, others = home(defname)
        name = labels.get(biome) or biome
        sheets = ", ".join(sorted(R.sheets_of_biome.get(biome, [])))
        group = f"{name} \u00b7 {biome}" + (f" \u00b7 {sheets}" if sheets else "")
        selected.append((defname, group, {"comm": comm, "others": others, "biome": biome}))

    reserve_hi = sorted(
        {d for d in reserve if d.startswith("RSW_")}
        | {d for d in reserve if frozen.get(d, {}).get("state", "keep") != "keep"}
    )
    for defname in reserve_hi:
        selected.append((defname, GROUP_RESERVE, {"comm": None, "others": [], "biome": None}))

    off = sorted(d for d, v in frozen.items()
                 if v.get("state") != "keep" and d not in rostered and d not in reserve)
    for defname in off:
        selected.append((defname, GROUP_RULED, {"comm": None, "others": [], "biome": None}))

    rows = []
    for defname, group, extra in selected:
        row = reg.get(defname)
        if row is None:
            continue
        art = row.get("art") or {}
        scale = art.get("scale")
        natural = png_size(HERE / scale) if scale else None
        rows.append({
            "defName": defname, "group": group, "reg": row, "art": art,
            "natural": natural, "frozen": frozen.get(defname), **extra,
        })

    stats = {
        "rostered": len(rostered), "reserveHi": len(reserve_hi), "off": len(off),
        "frozenEntries": len(frozen),
    }
    return rows, stats


def prefill_for(row: dict) -> tuple[str, str, str, str]:
    """-> (verdict, provenance key, provenance chip, note)."""
    defname = row["defName"]
    if defname in RULINGS_2026_09_06:
        verdict, note = RULINGS_2026_09_06[defname]
        return verdict, "ruled", "owner ruling 2026-09-06", note
    fz = row["frozen"]
    if fz:
        verdict = VERDICT_2026_08_23.get(fz.get("state"), "approve")
        note = fz.get("note") or ""
        stamp = f"your 2026-08-23 verdict `{fz.get('state')}`"
        note = f"{stamp}: \u201c{note}\u201d" if note else f"{stamp} (no note)"
        return verdict, "owner0823", "owner 2026-08-23", note
    art = row["art"]
    if not art.get("scale"):
        return "", "agent", "agent \u2014 undecided", (
            "Left undecided on purpose: the texture does not resolve on disk "
            f"({art.get('reason') or 'unknown'}), so there is nothing to judge. It renders in "
            "game or it does not — that is a deploy question, not an art verdict.")
    ppc = art.get("pxPerCell")
    if ppc is not None and ppc < 0.7:
        return "revise", "agent", "agent guess", (
            f"Agent guess: the source sprite carries only {num(ppc)} source px per drawn px, so "
            "it is upscaled and soft at the size the game actually draws it. Nothing else is "
            "wrong with it.")
    return "approve", "agent", "agent guess", (
        "Agent guess: no measurable art defect \u2014 the sprite is at or above its drawn "
        "resolution and its drawn size sits inside vanilla's own size band.")


def build_items(rows: list[dict]) -> tuple[list[dict], dict]:
    natural_max = max((max(r["natural"]) for r in rows if r["natural"]), default=1)
    k = MAX_PANEL_PX / float(natural_max)

    items: list[dict] = []
    for row in rows:
        defname, reg_row, art = row["defName"], row["reg"], row["art"]
        cells, bs = draw_cells(reg_row), reg_row.get("bodySize")
        mm = mismatch(reg_row)
        verdict, prov_key, prov, note = prefill_for(row)

        src = art.get("srcPx")
        ppc = art.get("pxPerCell")
        effect = f"{num(cells)} cells drawn \u00b7 bodySize {num(bs)}"
        if mm:
            effect += f" \u00b7 {mm:.2f}\u00d7 vanilla's size law"
        if src:
            effect += f" \u00b7 source {src[0]}\u00d7{src[1]} px"
        if ppc is not None:
            effect += f", {num(ppc)} src px per drawn px"
        if not art.get("scale"):
            effect += " \u00b7 \u26a0 NO TEXTURE ON DISK"

        law = f"{defname} \u00b7 {reg_row.get('mod') or '?'} \u00b7 {reg_row.get('texPath') or '?'}"
        if row["comm"] is not None:
            law += f" \u00b7 commonality {num(row['comm'])}"
        if row["others"]:
            law += " \u00b7 also in " + ", ".join(row["others"])
        if row["group"] == GROUP_RULED:
            law += (" \u00b7 CUT by Cherry Picker \u2014 not in the game"
                    if reg_row.get("cut") else
                    " \u00b7 anomaly entity \u2014 never rosters into a biome")
        law += "  \u2014  " + note

        needs_rationale = defname in NEEDS_RATIONALE
        if needs_rationale:
            law += "  \u2014  " + RATIONALE_ASK

        item = {
            "id": f"c:{defname}",
            "label": reg_row.get("label") or defname,
            "group": row["group"],
            "thumb": art.get("detail"),
            "effect": effect,
            "law": law,
            "prefill": verdict,
            "prov": prov,
            "provKey": prov_key,
            "cells": cells,
            "ruled": prov_key == "ruled",
            "rationale": needs_rationale,
            "soft": bool(ppc is not None and ppc < 0.9),
            "missing": not art.get("scale"),
        }
        if row["natural"]:
            item["scaleImg"] = art["scale"]
            item["sw"] = max(6, int(round(row["natural"][0] * k)))
            item["sh"] = max(6, int(round(row["natural"][1] * k)))
        if not verdict:
            item["openNote"] = note
        items.append(item)

    # ⧫ contested = a LIVE def carrying an open art flag. Counted before it was added:
    # off-roster rows are excluded (their def is cut or is an entity, so the flag is
    # moot), and ruled rows are excluded (they are settled, not contested).
    for it in items:
        it["contested"] = bool(
            it["prefill"] not in ("approve", "") and not it["ruled"]
            and it["group"] != GROUP_RULED
        )

    order = {GROUP_RULED: 0, GROUP_RESERVE: 1}
    group_size: dict[str, int] = {}
    for it in items:
        group_size[it["group"]] = group_size.get(it["group"], 0) + 1
    items.sort(key=lambda it: (
        order.get(it["group"], 2),
        -group_size[it["group"]] if it["group"] not in order else 0,
        it["group"],
        it["cells"] if it["cells"] is not None else 0,
        it["label"].lower(),
    ))

    counts = {
        "rows": len(items),
        "groups": len(group_size),
        "biomes": len([g for g in group_size if g not in order]),
        "contested": sum(1 for it in items if it["contested"]),
        "ruled": sum(1 for it in items if it["ruled"]),
        "rationale": sum(1 for it in items if it["rationale"]),
        "soft": sum(1 for it in items if it["soft"]),
        "missing": sum(1 for it in items if it["missing"]),
        "owner0823": sum(1 for it in items if it["provKey"] == "owner0823"),
        "agent": sum(1 for it in items if it["provKey"] == "agent"),
        "undecided": sum(1 for it in items if not it["prefill"]),
        "pxPerCell": round(SRC_PX_PER_CELL * k, 1),
        "maxPanel": MAX_PANEL_PX,
        "maxCells": max((it["cells"] or 0) for it in items),
        "minCells": min((it["cells"] or 99) for it in items),
    }
    for key in ("approve", "revise", "redraw", "replace", "cancel"):
        counts[key] = sum(1 for it in items if it["prefill"] == key)
    return items, counts


CRITERION = (
    "Pre-fill carries the owner's own frozen 2026-08-23 verdicts forward unchanged, plus the "
    "2026-09-06 rulings on top of them; only rows neither of those touched are agent guesses, "
    "and those were made on MEASURABLE art quality \u2014 source resolution against the size the "
    "game draws the sprite at. That ranks QUALITY, not WORTH: it cannot see that a shape is too "
    "terrestrial, too familiar, or unreadable as a creature, which is exactly what the owner "
    "overruled it on last time."
)


def invented(counts: dict) -> list[str]:
    return [
        f"THE SCALE CAP. Rows are drawn at true relative in-game scale \u2014 "
        f"{counts['pxPerCell']} px per map cell \u2014 and the biggest creature on the sheet "
        f"({counts['maxCells']:g} cells) sets it by being capped at {counts['maxPanel']} px on "
        "its longest side. Everything else is proportional to that ONE cap. The smallest row "
        f"({counts['minCells']:g} cells) therefore comes out about "
        f"{round(counts['minCells'] * counts['pxPerCell'])} px across and is genuinely hard to "
        "see \u2014 that is the true proportion, not a rendering fault. The 64px thumbnail beside "
        "it is the legible one; press Z to zoom it.",
        "BIOME CLUSTERING IS THE REVIEW ORDER, and it is a choice. The 2026-08-23 sheet ranked "
        "by measured art quality (worst first). This one groups by where the creature now lives, "
        "because the question changed: a sprite is judged against the biome it has to sell. "
        "Inside a group, rows run smallest to largest so the scale ladder reads.",
        "A creature in several biomes appears ONCE, in its highest-commonality home; the others "
        "are named on its row. Ties break alphabetically so two runs never disagree — which "
        f"is why {counts['biomes']} groups stand for 30 bound BiomeDefs: biomes served by one "
        "roster sheet (the Forge's lava field and volcano, the two propane lakes) collapse into "
        "whichever of them sorts first, and their group header names all the sheets involved.",
        f"{counts['agent']} rows carry an AGENT GUESS, not your verdict \u2014 the 2026-08-23 "
        "file has no entry for them. The guess is mechanical: revise if the source sprite has "
        "under 0.7 source px per drawn px (upscaled and soft at its drawn size), approve "
        "otherwise. It is blind to silhouette, legibility and \u2018too terrestrial\u2019.",
        "MAPPING YOUR 2026-08-23 WORDS ONTO THESE FIVE OPTIONS IS THE AGENT'S: keep\u2192approve, "
        "shrink\u2192revise, replace\u2192replace, redraw\u2192redraw. `shrink` in particular is "
        "read as a size revision, not a new drawing \u2014 if you meant a redraw, say so.",
        "\u2018Contested\u2019 here means a LIVE def carrying an open art flag \u2014 a verdict "
        "other than approve on a creature that is actually on the planet or in the reserve. Rows "
        "whose def is cut from the game, and rows you already ruled on, are deliberately NOT "
        "marked contested even though they are not approve.",
        "The register's art metrics (source px, px-per-drawn-px, the size-law ratio) are "
        "MEASURED from the 595-mod def dump of 2026-09-05. Everything derived from them is only "
        "as current as that dump.",
    ]


def brief_html(counts: dict) -> str:
    return (
        "<p><b>The pass:</b> CREATURE_ART_REVIEW_SHEET_1 \u2014 the art verdict on every "
        f"creature that is actually on Ash'karr. <b>{counts['rows']}</b> rows: "
        f"<b>{counts['biomes']}</b> biome groups holding the rostered cast, plus two off-roster "
        "groups you should read first.</p>"
        "<p><b>Every row is drawn at TRUE RELATIVE IN-GAME SCALE.</b> The wide panel on each row "
        f"is the creature at the size RimWorld actually draws it \u2014 {counts['pxPerCell']} px "
        "per map cell, one 1-cell grid behind it, and the SAME 1.5-cell colonist beside every "
        "single one as the ruler. A krayt dragon dwarfing a scalefish on this page is not a "
        f"layout accident, it is the game. The cap: the biggest creature ({counts['maxCells']:g} "
        f"cells) is held to {counts['maxPanel']} px and everything else is proportional to it, so "
        "the smallest rows are a few pixels across on purpose. The square 64px thumbnail is the "
        "art itself at a legible size \u2014 press <b>Z</b> to blow it up.</p>"
        "<p><b>Where the pre-fill comes from,</b> in strict precedence: your six rulings of "
        "2026-09-06 (marked <b>\u25c6 ruled</b>) beat your frozen verdicts of 2026-08-23 "
        f"(<b>{counts['owner0823']}</b> rows), which beat the agent's guess "
        f"(<b>{counts['agent']}</b> rows, on creatures neither file had an entry for). "
        "<b>Your 2026-08-23 file is never rewritten by this sheet or its generator</b> \u2014 it "
        "is read, carried forward and left alone. Note that every one of those verdicts was made "
        "BEFORE the biome assignment landed on 2026-09-09, when the question was still \u2018is "
        "this sprite good\u2019 rather than \u2018is it good enough for the biome it now lives "
        "in\u2019. That is the main thing worth re-reading here.</p>"
        "<p>\U0001f534 <b>The doctrine that binds any redraw</b> (your ruling, 2026-09-06): "
        "<i>\u201cWe shouldn't just \u2018reskin terrestrials\u2019 anymore, it's not "
        "productive.\u201d</i> Reskinning a terrestrial animal with glowing plates is rejected as "
        "a SOLUTION CLASS, not just for the two rows it was tried on. Any redraw of a "
        "\u2018too terrestrial\u2019 creature must find a genuinely different body plan and "
        "silhouette \u2014 a material reskin of the existing shape does not satisfy it.</p>"
        f"<p><b>\u2298 {counts['rationale']} rows are deliberately blocked on you.</b> These are "
        "the flagged <code>replace</code> calls from 2026-08-23 that carry no reason. The verdict "
        "is yours and it stands \u2014 what is missing is WHY, and without it nobody can generate "
        "a candidate that would satisfy you. One line in the note unblocks each of them.</p>"
        "<p><b>The controls:</b> "
        "<b>Approve</b> the art as it stands \u00b7 "
        "<b>Revise</b> \u2014 keep this drawing, change something about it (size, colour, a "
        "detail); say what in the note \u00b7 "
        "<b>Redraw</b> \u2014 same creature, new art, new silhouette \u00b7 "
        "<b>Replace</b> \u2014 this creature's art is not worth fixing; find a different creature "
        "for the slot \u00b7 "
        "<b>Cancel</b> \u2014 drop the art task entirely, do not chase it again. "
        "Only <b>Approve</b> counts as in; everything else puts the row on the art work queue. "
        "The note is worth more than the verdict: last time your twelve notes carried a criterion "
        "nobody had written down, and 588 agreements carried none.</p>"
        f"<p class='sub'>Marks: <b>\u25c6 ruled</b> = you ruled on this on 2026-09-06 "
        f"({counts['ruled']} rows; Atispec and Revenant are CANCELLED and are shown only so "
        "nothing quietly re-opens them). <b>\u26a0 contested</b> = a live def with an open art "
        f"flag ({counts['contested']} rows) \u2014 the real work queue. <b>\u2298 needs your "
        f"rationale</b> ({counts['rationale']}). <b>\u25cc soft</b> = under 0.9 source px per "
        f"drawn px, so it is upscaled at its own draw size ({counts['soft']} rows). Every row also "
        "carries a plain provenance chip saying whose call the pre-fill is. All 242 rostered "
        "creatures use <code>Graphic_Multi</code>, so no row is marked for that.</p>"
    )


RENDER_BLOCK = """
<style>
  .scalepanel{margin:6px 0 4px;overflow-x:auto;max-width:100%}
  .scalepanel img{image-rendering:pixelated;display:block;border-radius:4px;
                  border:1px solid var(--line);background:#12151a}
  .scalecap{font-size:10px;color:var(--dim);margin-top:2px}
  .mark.prov{opacity:.85}
</style>
<script id="RENDER">
  window.itemBody = it => {
    const marks = [];
    if (it.ruled)      marks.push('<span class="mark contested" title="you ruled on this on 2026-09-06 \\u2014 it is settled, not open">\\u25c6 ruled 2026-09-06</span>');
    if (it.contested)  marks.push('<span class="mark contested" title="a live def carrying a verdict other than approve \\u2014 this is the art work queue">\\u26a0 contested</span>');
    if (it.rationale)  marks.push('<span class="mark ovr" title="your replace verdict stands but carries no reason \\u2014 nothing can be generated until you give one">\\u2298 needs your rationale</span>');
    if (it.soft)       marks.push('<span class="mark inferred" title="under 0.9 source px per drawn px \\u2014 the sprite is upscaled and soft at the size the game draws it">\\u25cc soft</span>');
    if (it.missing)    marks.push('<span class="mark absent" title="the texture does not resolve on disk">\\u26a0 no texture</span>');
    if (it.prov)       marks.push('<span class="mark absent prov">' + esc(it.prov) + '</span>');
    const panel = it.scaleImg
      ? '<div class="scalepanel"><img src="' + esc(it.scaleImg) + '" width="' + it.sw
        + '" height="' + it.sh + '" loading="lazy" decoding="async" alt="'
        + esc(it.label) + ' at true in-game scale beside a colonist">'
        + '<div class="scalecap">true scale \\u00b7 ' + esc(String(it.cells)) + ' cells \\u00b7 colonist for scale</div></div>'
      : '';
    return '<div class="effect">' + esc(it.effect || '') + '</div>'
         + panel
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
    if doc.get("savedBy") or doc.get("writeCount") or doc.get("frozen"):
        sys.exit(
            f"REFUSING to overwrite {path.name}: it carries savedBy={doc.get('savedBy')!r} "
            f"writeCount={doc.get('writeCount')!r} frozen={doc.get('frozen')!r} \u2014 keys only "
            "the sheet's own plumbing writes. These are the OWNER's decisions, not the pre-fill.\n"
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

    R = load()
    reg = load_register_stats()
    rows, stats = build_rows(R, reg)
    items, counts = build_items(rows)

    # thumbnails that do not resolve are dropped rather than shipped broken
    for it in items:
        if it.get("thumb") and not (HERE / it["thumb"]).is_file():
            it["thumb"] = None

    config = {
        "sheetId": "creature_art_register",
        "title": "Creature art register \u2014 Ash'karr, at true in-game scale",
        "subtitle": (f"{counts['rows']} creatures \u00b7 {counts['biomes']} biomes \u00b7 "
                     f"{counts['contested']} contested \u00b7 {counts['ruled']} already ruled"),
        "briefHtml": brief_html(counts),
        "criterion": CRITERION,
        "invented": invented(counts),
        "posture": {
            "mode": "blacklist",
            "explain": "APPROVED unless you flag it. Nothing on this page edits art \u2014 a "
                       "verdict other than approve puts the creature on the art work queue, and "
                       "your note is what makes that task runnable.",
        },
        "options": [
            {"key": "approve", "label": "Approve", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "revise",  "label": "Revise",  "hotkey": "2", "color": "#e8b64c", "counts": "out"},
            {"key": "redraw",  "label": "Redraw",  "hotkey": "3", "color": "#6aa6e8", "counts": "out"},
            {"key": "replace", "label": "Replace", "hotkey": "4", "color": "#e06c6c", "counts": "out"},
            {"key": "cancel",  "label": "Cancel",  "hotkey": "5", "color": "#98a2b3", "counts": "out"},
        ],
        "groupLabel": "biome",
        "media": True,
        "decisionsFile": DECISIONS.name,
        "decisionsPath": NATIVE_DIR + "\\" + DECISIONS.name,
        "sheetPath": NATIVE_DIR + "\\" + SHEET.name,
    }

    SHEET.write_text(fill(load_template(), config, items), encoding="utf-8")
    print(f"wrote {SHEET}")
    print(f"  {counts['rows']} rows in {counts['groups']} groups "
          f"({counts['biomes']} biomes + 2 off-roster) \u00b7 "
          f"rostered {stats['rostered']}, reserve highlights {stats['reserveHi']}, "
          f"off-roster flagged {stats['off']}")
    print(f"  prefill: approve {counts['approve']} \u00b7 revise {counts['revise']} \u00b7 "
          f"redraw {counts['redraw']} \u00b7 replace {counts['replace']} \u00b7 "
          f"cancel {counts['cancel']} \u00b7 undecided {counts['undecided']}")
    print(f"  provenance: owner 08-23 {counts['owner0823']} \u00b7 ruled 09-06 {counts['ruled']} "
          f"\u00b7 agent {counts['agent']}")
    print(f"  marks: contested {counts['contested']} \u00b7 needs-rationale "
          f"{counts['rationale']} \u00b7 soft {counts['soft']} \u00b7 no texture "
          f"{counts['missing']}")
    print(f"  scale: {counts['pxPerCell']} px/cell, largest {counts['maxCells']:g} cells capped "
          f"at {counts['maxPanel']} px, smallest {counts['minCells']:g} cells")

    if args.sheet_only:
        return 0

    guard_decisions(DECISIONS, args.force)
    doc = {
        "sheet": "creature_art_register",
        "item": "CREATURE_ART_REVIEW_SHEET_1",
        "posture": "blacklist",
        "postureMeaning": "APPROVED unless flagged. A row with no entry stands as approved. "
                          "Nothing in this file edits art; a non-approve verdict is a work item.",
        "criterion": CRITERION,
        "generatedBy": "gen_creature_art_register.py",
        "generatedFrom": (
            "design/Jawa/worldbuilding/biomes/rosters/*.json (residency, 2026-09-09) + "
            "creature_register_rows.json (art metrics, 595-mod dump 2026-09-05) + "
            "design/Jawa/fauna/creature_art_decisions.json (owner-frozen 2026-08-23, READ ONLY) + "
            "infrastructure/state/items/CREATURE_ART_REVIEW_SHEET_1.md (owner rulings 2026-09-06)"
        ),
        "invented": invented(counts),
        "decisions": {
            it["id"]: {
                "decision": it["prefill"],
                "prefill": it["prefill"],
                "prefillSource": it["provKey"],
                "note": it.get("openNote") or "",
            }
            for it in items
        },
    }
    DECISIONS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {DECISIONS}  ({len(doc['decisions'])} pre-filled rows \u2014 "
          f"{counts['owner0823'] + counts['ruled']} of them the owner's own words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
