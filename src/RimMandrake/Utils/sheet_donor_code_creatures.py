#!/usr/bin/env python3
"""sheet_donor_code_creatures.py -- the "is the donor-code behaviour integral?" sheet (DONOR_DEFS_PORT_TO_OURS_1).

    python3 sheet_donor_code_creatures.py     writes Transient/donor_code_creatures_sheet_2026-10-09.{html,decisions.json}
                                              + _img/ thumbnails. The decisions file is written only when absent.

Owner, by question card 2026-10-09: "Walk me through the behaviors and the current creature definition and appearance
to see if it's still integral. Review sheet just for this."

Rows come from donor_code_census.py (re-measured today, not copied from the item's 2026-09-24 table): every creature
in an owned BiomeDef roster that resolves to the Alpha Animals mod and carries a class from its private
AlphaBehavioursAndEvents.dll. Label/description/texPath are resolved THROUGH our own patches (the game reads the
patched value). Behaviour text was written from the donor's published C# (github.com/juanosarg/AlphaAnimals, 1.6
source) -- each row says which class. Changes no def.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import donor_code_census as C  # noqa: E402

REPO = C.REPO
SKILL = Path.home() / ".claude" / "skills" / "review-sheets" / "assets"
SHEET_ID = "donor_code_creatures_sheet_2026-10-09"
OUT = REPO / "Transient" / f"{SHEET_ID}.html"
IMG = REPO / "Transient" / f"{SHEET_ID}_img"
SRC_SOURCE = "github.com/juanosarg/AlphaAnimals 1.6/Source/AlphaBehavioursAndEvents"

# ── what each donor class does, in plain words (read from the donor's C#) ──
BEHAVIOUR = {
    "DeathActionWorker_AcidExplosion":
        "When it dies it bursts: an acid splash 2, 3 or 4 cells wide (baby, juvenile, adult) that burns everyone in it "
        "(10 acid damage plus acid build-up) and leaves green slime.",
    "DeathActionWorker_RedAcidExplosion":
        "When it dies it bursts: an acid splash 2, 3 or 4 cells wide (by age) that burns everyone in it (10 acid damage "
        "plus acid build-up) and leaves red slime.",
    "DeathActionWorker_SmallRedAcidExplosion":
        "When it dies it pops: a 2-cell acid splash (10 acid damage plus acid build-up) that leaves red slime.",
    "DeathActionWorker_LuciferiumExplosion":
        "When it dies it detonates: a 2-cell burst (30 damage) that doses everyone in it with luciferium: a luciferium "
        "high AND luciferium addiction, scaled down by toxic resistance.",
    "DeathActionWorker_SummonFlashstorm":
        "When it dies, a flashstorm (a dry lightning storm that starts fires) begins over the whole map.",
    "CompProperties_GraphicsRefresher":
        "Nothing you can see in play. With the donor's 'alternate Pokemon-style graphics' option switched on (it is OFF "
        "by default) it swaps to a second picture set; with it off it draws the normal picture.",
    "PawnRenderNode_Alternates":
        "(same as above: the drawing half of the optional alternate-picture switch)",
    "PawnRenderNodeProperties_SpasticScaled":
        "Appearance only: its separately-drawn limbs (tentacles/claws) twitch and jerk at random. The base game has the "
        "same twitch built in (PawnRenderNode_Spastic); the donor's version only keeps the limbs the right size on babies.",
    "Pawn_GrowOnCombat":
        "When it fights in melee it swells into a hulking brute for a few hours: armour +75%, near-painless, 26-damage "
        "claws, drawn 3x bigger from its own '_Enlarged' picture; afterwards it is exhausted and four times as hungry.",
    "PawnRenderNode_CrescendoAnole":
        "(the drawing half of the above: swaps to the 3x '_Enlarged' picture while swollen)",
    "CompProperties_BlackSwarmlingToCocoon":
        "About 4 in-game hours after it appears it spins a black-hive cocoon (a VFE Insectoids 2 thing), splashes slime, "
        "and disappears; an adult Black Hive insect hatches from the cocoon later.",
}

# ── per-creature judgement: integral grade, why, recommendation (prefill), contested flag ──
# grade: CORE = the behaviour IS the creature · PART = one of its defining traits · FLAVOUR = minor colour · NONE = invisible
J = {
    "AA_AcanthamoebaGiganteaLarge": ("PART", "Its identity is eating trash and splitting in two (VEF framework, not donor code); "
        "the acid burst is a second trait.", "rebuild",
        "Rebuild: one small shared 'burst on death' class of ours covers all five acid creatures (same code, three numbers), so keeping it costs almost nothing extra."),
    "AA_AcanthamoebaGiganteaSmall": ("PART", "As the large form: trash-eater and splitter first, acid burst second.", "rebuild",
        "Rebuild with the same shared burst class as the large form; the two must stay one species."),
    "AA_GreenGoo": ("CORE", "A cell of a superorganism that bursts into acid when killed: the burst is what makes killing it costly.",
        "rebuild", "Rebuild the burst (shared class) and swap its twitching tentacles to the base game's twitch node."),
    "AA_RedGoo": ("CORE", "Same shape as the wuum: the acid burst is the price of killing it.", "rebuild",
        "Rebuild the burst (shared class) and swap its twitching tentacles to the base game's twitch node."),
    "AA_RedSpore": ("CORE", "Its own description says it is 'inherently unstable'; the burst is its whole threat.", "rebuild",
        "Rebuild the burst with the shared class."),
    "AA_InfectedAerofleet": ("CORE", "A pustule-covered gas sac; popping when killed is the point of the 'infected' variant.",
        "rebuild", "Rebuild the small burst with the shared class."),
    "AA_LuciferBug": ("CORE", "Its whole description is the detonation that doses everyone near it with luciferium.",
        "rebuild", "Rebuild: the shared burst class with the luciferium damage type instead of acid; nothing else needed."),
    "AA_Thunderbeast": ("FLAVOUR", "Our Blue Desert description is about static arcs it discharges while alive; the "
        "flashstorm on death is not in it, and it spawns at 0.005.", "rebuild",
        "Rebuild: about five lines of ours (start the vanilla Flashstorm incident on death). Port plain is just as defensible: the description never promises it."),
    "AA_CrescendoAnole": ("CORE", "The creature is the transformation: a harmless lizard that becomes a hulking brute when it fights.",
        "rebuild", "Rebuild: three small classes (the swelling trigger, the enlarged picture, the hediff hook). Without them it is just a weak lizard and should be replaced instead."),
    "VFEI2_BlackSwarmling": ("CORE", "A larva whose only purpose is to become a cocoon of VFE Insectoids 2's Black Hive; "
        "porting it keeps us tied to that donor too.", "replace",
        "Replace: the creature exists to feed another donor's insect ecosystem, so porting it buys a second dependency. Also mis-guarded on sarg.alphaanimals in our XML."),
    "AA_ColossalAerofleet": ("NONE", "Twitching tentacles only; no behaviour.", "port",
        "Port plain, swapping to the base game's twitch node: it still twitches, only the baby-size correction is lost."),
    "AA_Mantrap": ("FLAVOUR", "A predatory flytrap; the writhing tentacles sell it, but it is a look, not a behaviour.", "port",
        "Port plain with the base game's twitch node: same writhing, no code of ours."),
    "AA_OcularJelly": ("FLAVOUR", "The writhing tentacles are most of its weirdness, but the base game's twitch node gives the same look.",
        "port", "Port plain with the base game's twitch node."),
    "AA_RipperHound": ("NONE", "Twitching claws only; no behaviour.", "port", "Port plain with the base game's twitch node."),
    "AA_Agaripawn": ("NONE", "The donor code only matters if the donor's optional alternate-picture setting is on.", "port",
        "Port plain: drop both classes; nothing changes in play."),
    "AA_Agaripod": ("NONE", "As agaripawn: optional alternate-picture switch only.", "port", "Port plain: drop both classes."),
    "AA_DecayDrake": ("NONE", "Optional alternate-picture switch only; its rot-spreading is VEF framework, not donor code.", "port",
        "Port plain: drop both classes."),
    "AA_MycoidColossus": ("NONE", "Optional alternate-picture switch only.", "port", "Port plain: drop both classes."),
    "AA_Radyak": ("NONE", "Optional alternate-picture switch only.", "port", "Port plain: drop both classes."),
    "AA_Thermadon": ("NONE", "Optional alternate-picture switch only; its fire-breathing is not donor code.", "port",
        "Port plain: drop both classes."),
}
GROUP = {
    "rebuild-burst": "Bursts or storms when it dies",
    "transform": "Changes shape or life stage",
    "twitch": "Twitching limbs (appearance only)",
    "none": "Optional picture switch (nothing in play)",
}


def group_of(classes):
    s = " ".join(classes)
    if "GrowOnCombat" in s or "Cocoon" in s:
        return GROUP["transform"]
    if "DeathActionWorker" in s:
        return GROUP["rebuild-burst"]
    if "Spastic" in s:
        return GROUP["twitch"]
    return GROUP["none"]


def our_patched_values():
    """{(defType, defName, field): (value, file)} from every src PatchOperation(Replace|Add) xpath ending in a field."""
    out = {}
    pat = re.compile(r'(ThingDef|PawnKindDef)\[defName\s*=\s*["\']([^"\']+)["\']\]/(label|description|race/baseBodySize|.*texPath)$')
    for p in C.SRC.rglob("*.xml"):
        if "/Patches/" not in str(p):
            continue
        root = C.parse(p)
        if root is None:
            continue
        for op in root.iter():
            if not isinstance(op.tag, str):
                continue
            xp, val = op.find("xpath"), op.find("value")
            if xp is None or val is None or not xp.text:
                continue
            m = pat.search(xp.text.strip())
            if not m:
                continue
            field = m.group(3).rsplit("/", 1)[-1]
            ch = val.find(field)
            if ch is not None and ch.text:
                out[(m.group(1), m.group(2), field)] = (ch.text.strip(), str(p.relative_to(REPO)))
    return out


def find_png(tex: str):
    """(path, owner) of the south (else east) picture: ours under src/**/Textures first, then the donor's."""
    for face in ("south", "east"):
        hits = sorted(C.SRC.glob(f"*/*/Textures/{tex}_{face}.png")) + sorted(C.SRC.glob(f"*/*/*/Textures/{tex}_{face}.png"))
        if hits:
            return hits[0], "ours", face
    for face in ("south", "east"):
        for base in (C.DONOR / "Textures", C.DONOR / "1.6" / "Textures"):
            p = base / f"{tex}_{face}.png"
            if p.is_file():
                return p, "donor", face
    return None, None, None


def thumb(src: Path, name: str) -> str:
    from PIL import Image
    IMG.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGBA")
    im.thumbnail((256, 256))
    out = IMG / f"{name}.png"
    im.save(out)
    return f"{IMG.name}/{out.name}"


RENDER = r"""<script id="RENDER">
window.itemBody = it => `
<div style="display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap">
  <figure style="margin:0;text-align:center;flex:0 0 auto">
    <div style="background:#2a1f16;border:1px solid #5a4320;border-radius:6px;padding:6px">
      ${it.pic ? `<img src="${esc(it.pic)}" width="200" height="200" style="display:block;object-fit:contain" alt="${esc(it.label)}">`
               : `<div style="width:200px;height:200px;display:flex;align-items:center;justify-content:center">no picture found</div>`}</div>
    <figcaption style="margin-top:4px;max-width:212px;font-size:12px"><b>${esc(it.picWho)}</b><br>${esc(it.picSrc)}</figcaption></figure>
  <div style="flex:1 1 420px;min-width:300px">
    <div class="effect"><b>${esc(it.label)}</b> <code>${esc(it.id)}</code> &middot; integral: <b>${esc(it.grade)}</b></div>
    <table style="border-collapse:collapse;margin-top:6px;font-size:13px">
      <tr><td style="color:#98a2b3;padding:3px 10px 3px 0;vertical-align:top;white-space:nowrap">what it is</td><td>${esc(it.what)}</td></tr>
      <tr><td style="color:#98a2b3;padding:3px 10px 3px 0;vertical-align:top">lives in</td><td>${esc(it.homes)}</td></tr>
      <tr><td style="color:#98a2b3;padding:3px 10px 3px 0;vertical-align:top">size / threat</td><td>${esc(it.stats)}</td></tr>
      <tr><td style="color:#98a2b3;padding:3px 10px 3px 0;vertical-align:top">donor code does</td><td>${it.behaviour.map(b => `<div style="margin-bottom:4px">${esc(b)}</div>`).join('')}</td></tr>
      <tr><td style="color:#98a2b3;padding:3px 10px 3px 0;vertical-align:top">how integral</td><td><b>${esc(it.grade)}</b> &mdash; ${esc(it.why)}</td></tr>
      <tr><td style="color:#98a2b3;padding:3px 10px 3px 0;vertical-align:top">recommend</td><td>${esc(it.rec)}</td></tr>
    </table>
  </div>
</div>`;
</script>
"""


def main() -> int:
    rows = C.roster_rows()
    things, named, kinds, trees = C.donor_defs()
    patched = our_patched_values()
    census = []
    for dn in sorted(k for k in rows if k in things):
        el, p = things[dn]
        cls = set()
        for c in C.chain(el, named):
            cls |= C.classes_in(c)
        tree = None
        for c in C.chain(el, named):
            t = c.findtext(".//renderTree")
            if t:
                tree = t.strip()
                break
        if tree and tree in trees:
            cls |= C.classes_in(trees[tree])
        if dn in kinds:
            cls |= C.classes_in(kinds[dn])
        priv = sorted({c.split(".", 1)[1] for c in cls if c.startswith(C.PRIVATE_NS)})
        if priv:
            census.append((dn, el, priv))
    print(f"SANITY AA_RedGoo roster rows={len(rows.get('AA_RedGoo', []))}; donor-code creatures={len(census)}")
    missing = [dn for dn, _, _ in census if dn not in J]
    if missing:
        raise SystemExit(f"no judgement written for {missing} -- add them to J before building")

    def first(el, path):
        for c in C.chain(el, named):
            v = c.findtext(path)
            if v:
                return v.strip()
        return None

    items = []
    for dn, el, priv in census:
        label, lsrc = patched.get(("ThingDef", dn, "label"), (first(el, "label"), "donor"))
        desc, dsrc = patched.get(("ThingDef", dn, "description"), (first(el, "description") or "", "donor"))
        desc = desc.replace("\\n", " ").strip()
        what = desc if len(desc) <= 360 else desc[:357].rsplit(" ", 1)[0] + "..."
        k = kinds.get(dn)
        tex = None
        if k is not None:
            ls = k.findall("lifeStages/li")
            if ls:
                tex = (ls[-1].findtext("bodyGraphicData/texPath") or "").strip()
        tex, tsrc = patched.get(("PawnKindDef", dn, "texPath"), (tex, "donor"))
        png, who, face = find_png(tex) if tex else (None, None, None)
        pic = thumb(png, dn) if png else ""
        homes = sorted({(b, c) for b, c, _, _ in rows[dn]})
        rm = [f"{b} {c}" for b, c in homes if b.startswith("RM_")]
        rut = [f"{b} {c}" for b, c in homes if not b.startswith("RM_")]
        home_txt = ("free biome mod: " + (", ".join(rm) if rm else "none")) + " · campaign twins: " + (", ".join(rut) if rut else "none")
        size = first(el, "race/baseBodySize")
        if ("ThingDef", dn, "baseBodySize") in patched:
            size = patched[("ThingDef", dn, "baseBodySize")][0]
        pred = first(el, "race/predator") == "true"
        cp = k.findtext("combatPower") if k is not None else "?"
        grade, why, prefill, rec = J[dn]
        beh = []
        for c in priv:
            beh.append(f"{c}: {BEHAVIOUR.get(c, 'UNREAD - no plain-words entry for this class')}")
        items.append({
            "id": dn, "group": group_of(priv), "label": label, "effect": f"{grade}: {why}",
            "what": what + ("" if dsrc == "donor" else f"  [our description, {Path(dsrc).name}]"),
            "homes": home_txt, "stats": f"body size {size}, combat power {cp}{', predator' if pred else ''}",
            "behaviour": beh, "grade": grade, "why": why, "rec": rec, "prefill": prefill,
            "pic": pic, "picWho": ("OUR art (in game now)" if who == "ours" else "DONOR art (in game now)") if png else "",
            "picSrc": (f"{png.relative_to(REPO) if who == 'ours' else png.relative_to(C.DONOR)} ({face}"
                       + ("; body only, the twitching limbs are separate pictures)" if any("Spastic" in c for c in priv) else ")")) if png else f"texPath {tex}",
            "contested": dn in ("VFEI2_BlackSwarmling", "AA_Thunderbeast"),
            "meta": [label if lsrc == "donor" else f"{label} (our name)"],
        })
    order = list(GROUP.values())
    items.sort(key=lambda it: (order.index(it["group"]), it["id"]))

    dec = OUT.with_suffix(".decisions.json")
    cfg = {
        "sheetId": SHEET_ID, "title": "Donor-code creatures",
        "subtitle": f"{len(items)} borrowed Alpha Animals creatures that run the donor's own code - changes no def",
        "briefHtml": (
            "<p><b>What this is.</b> You asked (card, 2026-10-09) to walk through each borrowed creature that depends on "
            "<b>Alpha Animals' own compiled code</b> (<code>AlphaBehavioursAndEvents.dll</code>) and judge whether that "
            "behaviour is still integral. That code disappears the moment the donor mod is removed, so each of these "
            f"needs a decision before it can become ours. Re-measured today: <b>{len(items)}</b> creatures in our biome "
            "rosters (the item's 2026-09-24 table said 15; five are new since, and one, the darkbeast, is no longer on any roster).</p>"
            "<p><b>Each row:</b> what the creature is (our description where we rewrote it), where it lives today, what "
            "the donor code actually does in plain words (read from the donor's published C#), how integral that is, the "
            "picture the game shows now, and my recommendation.</p>"
            "<p><b>The four choices.</b> <b>Port plain</b> = copy the creature into our own defs and drop or swap the donor "
            "class (no new C#). <b>Rebuild</b> = copy it and re-write the behaviour in our own assembly. <b>Replace</b> = "
            "cut it and fill its roster slot with a new creature of ours. <b>Other / hold</b> = say what in the note. "
            "Nothing changes until a later pass reads your picks; this sheet edits no def.</p>"
            "<p><b>Pictures are context, not the question.</b> 16 of these rows were already covered by your 2026-09-20 "
            "blanket 'replace donor art' ruling on the Alpha Animals port sheet; that stands and is not re-asked here. "
            "Twitching-limb creatures show the body picture only.</p>"),
        "criterion": "Grouped by what the donor code does; my pick follows how integral it is to the creature, not art quality or how often it spawns.",
        "invented": [
            "The integral grades (CORE / PART / FLAVOUR / NONE) are my judgement from the descriptions and the C#, not a measurement.",
            "I assumed the five acid/luciferium bursts would share ONE class of ours, which is why 'rebuild' is cheap for all of them.",
            "Swapping the twitching limbs to the base game's PawnRenderNode_Spastic is from reading both classes; it has not been tried in game.",
        ],
        "posture": {"mode": "pick-one", "explain": "Every row needs one of the four. Port plain and rebuild keep the creature; replace cuts it."},
        "options": [
            {"key": "port", "label": "Port plain", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "rebuild", "label": "Rebuild behaviour", "hotkey": "2", "color": "#6aa6e8", "counts": "in"},
            {"key": "replace", "label": "Cut & replace with new cast", "hotkey": "3", "color": "#e06c6c", "counts": "out"},
            {"key": "other", "label": "Other / hold (say in note)", "hotkey": "4", "color": "#e8b64c", "counts": "out"},
        ],
        "groupLabel": "what the donor code does", "media": True,
        "decisionsFile": dec.name, "decisionsPath": str(dec), "sheetPath": str(OUT),
    }
    tpl = (SKILL / "sheet_template.html").read_text()
    tpl = re.sub(r'(<script id="CONFIG" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(cfg, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = re.sub(r'(<script id="ITEMS" type="application/json">)(.*?)(</script>)',
                 lambda m: m.group(1) + "\n" + json.dumps(items, indent=1).replace("</", "<\\/") + "\n" + m.group(3), tpl, count=1, flags=re.S)
    tpl = tpl.replace("<!-- ══ FILL IN #3 (optional)", RENDER + "\n<!-- ══ FILL IN #3 (optional)", 1)
    tpl = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", tpl, count=1, flags=re.S)
    OUT.write_text(tpl)
    if not dec.exists():
        dec.write_text(json.dumps({
            "sheetId": SHEET_ID, "posture": "pick-one", "criterion": cfg["criterion"],
            "reviewStatus": {"state": "prefill", "by": None, "at": None,
                             "evidence": "generated by sheet_donor_code_creatures.py; no human has ruled"},
            "decisions": {it["id"]: {"decision": it["prefill"], "note": "", "prefill": it["prefill"]} for it in items}}, indent=1))
    print("OK", OUT, len(items), "rows;", sum(1 for it in items if it["pic"]), "with pictures;",
          sum(1 for it in items if it["picWho"].startswith("OUR")), "ours")
    return 0


if __name__ == "__main__":
    sys.exit(main())
