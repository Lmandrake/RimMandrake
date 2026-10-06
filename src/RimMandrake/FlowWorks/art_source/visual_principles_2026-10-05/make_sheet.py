#!/usr/bin/env python3
"""Builds the owner's review sheet for the five FlowWorks visual principles (2026-10-05).

Fills the review-sheets template (~/.claude/skills/review-sheets/assets/sheet_template.html)
with one row per picture strip: BEFORE (today) above AFTER (the change), plain sentences only.
Output: visual_principles_sheet.html beside this file; decisions in visual_principles_decisions.json.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")
OUT = os.path.join(HERE, "visual_principles_sheet.html")
WIN = r"\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\src\RimMandrake\FlowWorks\art_source\visual_principles_2026-10-05"


def pic(name):
    for ext in (".gif", ".png"):
        if os.path.exists(os.path.join(HERE, name + ext)):
            return name + ext
    return ""


ROWS = [
    ("1. Deep cuts look like walls", "p1_dirt",
     "A dug pit at depths 1 to 4, in soil. The far bank now shows a lit face with a dark rim line, drawn the "
     "way the game draws its own walls. A pit deep enough to hold a person (3) has a face about as tall as a "
     "wall's; the deepest (4) is taller again. A person standing at the near edge is hidden by the near bank, "
     "more the deeper they stand, with a faint outline left so you can still find them.",
     "dry_dirt"),
    ("1. Deep cuts look like walls", "p1_stone",
     "The same pit dug next to stone ground. Same heights; the face is stone.",
     "dry_stone"),
    ("2. Walls are dirt or stone", "p2_material",
     "The face is made from the ground beside it: soil gives a banded earth face, rock gives a jointed stone "
     "face in that rock's own colour. Compare this row's AFTER (stone) with the row above (soil). Nothing is "
     "set per biome: the game reads which ground is stone from the rock types themselves.",
     "dry_stone"),
    ("3. Water moves", "p3_dirt",
     "Water standing in the pit. Before: one flat colour. After: the surface shimmers with drifting ripples, "
     "and anyone wading leaves a V-shaped wake. Deeper fills keep their darker colour, so the depth still reads.",
     "water_dirt"),
    ("3. Water moves", "p3_stone",
     "The same in a stone-sided pit.",
     "water_stone"),
    ("4. Tar is a black liquid", "p4_dirt",
     "Tar in the pit. Before: flat black, like a burnt patch. After: black with slow, glossy highlights "
     "sliding across it, the way a thick wet surface catches light. It moves far slower than water.",
     "tar_dirt"),
    ("4. Tar is a black liquid", "p4_stone",
     "The same in a stone-sided pit.",
     "tar_stone"),
    ("4. Other liquids", "p4_oil",
     "Oil gets the same slow gloss with a faint rainbow sheen (picture shows after only).",
     "oil_dirt"),
    ("4. Other liquids", "p4_slime",
     "Slime is thick and gloopy: soft bright blobs that barely move (after only).",
     "slime_dirt"),
    ("5. A burned pit looks burned", "p5_dirt",
     "A pit after a liquid fire burned it dry. Before: an ordinary pit with a few ash specks. After: still an "
     "empty pit with the same walls, but charred: black ash floor, soot climbing the walls, a scorch ring on "
     "the ground around the edge. The scorch stays until the pit is refilled or filled in; it fades over 20 "
     "days on its own (faster in rain). Both the fade time and the effect are Mod Settings.",
     "scorched_dirt"),
    ("5. A burned pit looks burned", "p5_stone",
     "The same in a stone-sided pit.",
     "scorched_stone"),
]


def main():
    html = open(TEMPLATE, encoding="utf-8").read()
    items = []
    for group, rid, text, stem in ROWS:
        before = pic(stem + "_before")
        after = pic(stem + "_after")
        items.append({"id": rid, "group": group, "label": group, "effect": text,
                      "before": before, "after": after, "thumb": after or before, "prefill": "right"})
    config = {
        "sheetId": "flowworks_visual_principles_2026-10-05",
        "title": "Pits and liquids: how they look",
        "subtitle": "your five rules, before and after",
        "briefHtml": (
            "<p>You gave five rules for how dug pits and the liquids in them should look. Each row below shows "
            "<b>today</b> (top picture) and <b>the change</b> (bottom picture), at depths 1, 2, 3 and 4 from left "
            "to right. Moving pictures loop every two seconds.</p>"
            "<p>These are drawings made outside the game from the game's own ground textures. They show the "
            "direction. In-game pictures follow once the game is free.</p>"
            "<p>For each row pick <b>Looks right</b>, <b>Close, adjust</b> (say what in the note) or "
            "<b>Wrong direction</b>.</p>"),
        "criterion": "Does the bottom picture follow your rule?",
        "invented": [],
        "posture": {"mode": "whitelist", "explain": "Nothing changes in game direction until you mark a row."},
        "options": [
            {"key": "right", "label": "Looks right", "hotkey": "1", "color": "#7fb069", "counts": "in"},
            {"key": "adjust", "label": "Close, adjust", "hotkey": "2", "color": "#e0a458", "counts": "in"},
            {"key": "wrong", "label": "Wrong direction", "hotkey": "3", "color": "#d1603d", "counts": "out"},
        ],
        "groupLabel": "rule",
        "media": True,
        "decisionsFile": "visual_principles_decisions.json",
        "decisionsPath": WIN + r"\visual_principles_decisions.json",
        "sheetPath": WIN + r"\visual_principles_sheet.html",
    }
    html = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                  lambda m: m.group(1) + "\n" + json.dumps(config, indent=1) + "\n" + m.group(3), html, count=1, flags=re.S)
    html = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                  lambda m: m.group(1) + "\n" + json.dumps(items, indent=1) + "\n" + m.group(3), html, count=1, flags=re.S)
    render = """
<style>
:root{--bg:#2a1f17;--panel:#3a2b20;--panel2:#33261c;--line:#5a4532;--ink:#f1e6d2;--dim:#cdb89a;--accent:#e0a458;--rowh:auto}
html,body{font-size:17px}
.thumb{display:none}
.pair{display:flex;flex-direction:column;gap:6px;margin:6px 0}
.pair figure{margin:0}
.pair img{max-width:100%;height:auto;border:1px solid var(--line);cursor:zoom-in}
.pair figcaption{font-size:16px;color:var(--dim)}
.effect{font-size:17px;line-height:1.5}
</style>
<script id="RENDER">
  window.itemBody = it => {
    const f = (src, cap) => src ? `<figure><figcaption>${cap}</figcaption><img src="${esc(src)}" data-zoom="${esc(src)}" data-cap="${esc(cap)}" loading="lazy" alt=""></figure>` : '';
    return `<div class="effect">${esc(it.effect)}</div><div class="pair">${f(it.before, 'Today')}${f(it.after, 'The change')}</div>`;
  };
</script>
"""
    html = html.replace('<div id="keys">', render + '\n<div id="keys">', 1)
    open(OUT, "w", encoding="utf-8").write(html)
    print("WROTE", OUT)
    dpath = os.path.join(HERE, "visual_principles_decisions.json")
    if not os.path.exists(dpath):   # never overwrite his rulings
        import datetime
        doc = {"sheetId": config["sheetId"],
               "reviewStatus": {"state": "prefill", "by": "FOUNDRY agent",
                                "at": datetime.datetime.now().isoformat(timespec="seconds"),
                                "evidence": "agent pre-fill: every row guessed 'Looks right'; owner has not ruled"},
               "decisions": {it["id"]: {"decision": "right", "source": "prefill"} for it in items}}
        open(dpath, "w", encoding="utf-8").write(json.dumps(doc, indent=1))
        print("WROTE", dpath)


if __name__ == "__main__":
    main()
