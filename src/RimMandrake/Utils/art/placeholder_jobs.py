#!/usr/bin/env python3
"""placeholder_jobs.py — build artpipe jobs for every census row whose live art is PLACEHOLDER
(owner, 2026-10-05: the Grey Sea sheet showed flat shapes and vanilla cactus).

    python3 src/RimMandrake/Utils/art/placeholder_jobs.py [--out Transient/biome_ffar/placeholder_regen_jobs_2026-10-05.json]

Reads the census + placeholder_detect.sweep(); skips rows that already have a finished or pending render in the
artpipe state dir (those are listed under 'render_exists_not_installed' in the report JSON next to the jobs file).
Prompts come from the def's own description; the biome register is a one-line summary of the biome's design doc.
Never puts facing-set words in a prompt. Creature = east master + south/north (fill_queue derives N/S from east);
plant = one job, no facings; catch item = item sprite, anatomy-referenced to the floor creature's render if any.
"""
from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placeholder_detect as P  # noqa: E402

REPO = P.REPO
ART = Path("/mnt/d/Luke/dev/_artpipe")
OWNER_NOTE = ("Ok, I did half the Grey Sea... something very wrong with that sheet. Most of the images look like nothing, "
              "trivially simple imagery, or cactus. Please investigate and repair.")
ITEM = "BIOME_FLORAFAUNA_ART_REVIEW_1"
HOUSE = "Painterly vanilla-RimWorld house style, matte, no outlines, never cute; one centred subject on a transparent background, no ground, no props, no baked shadow."

REGISTER = {
 "RM_GreySea": "grey sea floor register: hypersaline grey-green murk, a few metres of dim diffuse light, salt pillars, white brine haze, crusted mineral surfaces; muted grey, bone and verdigris with one accent colour; must read against pale grey sediment through value and rim",
 "RM_TwilightSea": "twilight sea register: a deep hypersaline sea lidded by living stained glass, dim blue-green light filtered through waveglass from above; cool teal and violet with glints of coloured glass; reads against dark blue-green silt",
 "RM_TheChill": "the chill register: a black mirror of liquid fuel under a very bright sky, ringed by frozen white propane crust; stark, cold, high-contrast; pale ice, black fuel sheen",
 "RM_TheScald": "the scald register: a boiling perched ocean in the hottest basin, pale scalded stone, rust-orange mineral crust, steam haze; hot saturated light; reads against bleached rock and murky hot water",
 "RM_TheSump": "the sump register: permanent dusk over flat black tar pools and cooled glassy sheets, low waxy plants glowing faintly from lamp-gardens; dim warm amber against black",
 "RM_Webwork": "webwork register: a dense nightmare thicket in green gloom, pale dust-lit shafts, silk and tangled vegetation; dim greens, bruise purples, bone-white silk",
 "RM_FeverWood": "fever wood register: great solid trunks, dark still pools beneath, dappled humid light in the crown; deep greens, wet black, feverish amber accents",
 "RM_WeepingStones": "weeping stones register: high pale wind-scoured stone in bright dry light, black seep streaks, moss and green-ringed pools; pale chalk, black wet streaks, moss green",
 "RM_Greentide": "greentide register: a gallery jungle in permanent ground-hugging warm steam, deep mud, fast green growth; saturated greens, wet browns, soft fog",
 "RM_Miasma": "miasma register: a salt-crusted mangal forest under a green-gold haze, brackish channels, rainbow-hued plants; gold-green light, pale salt crust",
 "RM_GelatinousSlime": "gelatinous slime register: a country-sized living body open to the sky, translucent wet sheen, soft bright light; pale green-grey translucence, no rock, no soil",
 "RM_FloodedCanyon": "flooded canyon register: dry cracked canyon floor under a hard sun, deep shadow, red-ochre rock; hard directional light",
}
DEFAULT_REG = "the subject keeps its own colours in the biome's natural light; muted, matte, painterly"
PRIORITY = {"RM_GreySea": 8, "RM_TheSump": 10, "RM_TheScald": 10, "RM_Webwork": 10, "RM_TheChill": 10,
            "RM_TwilightSea": 10, "RM_LanternDeeps": 10}
BIG = 1.9


def load_defs():
    d = {}
    for f in SRC_XML():
        try:
            t = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for e in t.iter("ThingDef"):
            n = e.findtext("defName")
            if n:
                d[n] = e
        for e in t.iter("PawnKindDef"):
            r = e.findtext("race")
            if r:
                d.setdefault("kind:" + r, e)
    return d


def SRC_XML():
    return (p for p in P.SRC.rglob("*.xml") if "/Defs/" in str(p) or "/Patches/" in str(p))


def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("\\n", " ")).strip()


def draw_size(e, kind_e):
    for node in ([kind_e] if kind_e is not None else []) + [e]:
        for ds in node.iter("drawSize"):
            m = re.findall(r"[\d.]+", ds.text or "")
            if m:
                return float(m[0])
    return 1.0


def existing(defname, row):
    """Finished/pending render in artpipe state for this row's artpipe_state_jobs."""
    found = []
    for j in row.get("artpipe_state_jobs", []):
        for d in ("done", "pending", "active"):
            if any(x.startswith(j) for x in os.listdir(ART / d)):
                found.append((j, d))
    return found


def build(out: Path):
    census = json.load(open(P.CENSUS))
    sw = P.sweep()
    defs = load_defs()
    rows = {}
    for b in census["biome_order"]:
        for r in census["biomes"][b]["rows"]:
            rows[(b, (r["defNames"] or [r["key"]])[0])] = r
    jobs, have, seen = [], [], set()
    artsrc = os.listdir(ART / "_artsrc")
    for b, lst in sw.items():
        for x in lst:
            if x["verdict"] != "PLACEHOLDER":
                continue
            dn = x["def"]
            r = rows[(b, dn)]
            ex = existing(dn, r)
            key = (dn,)
            if key in seen:
                continue
            seen.add(key)
            if ex:
                have.append({"biome": b, "def": dn, "kind": x["kind"], "renders": ex})
                continue
            e = defs.get(dn)
            kind = x["kind"]
            is_catch = kind == "fish"
            floor = re.sub(r"Catch$", "", dn) if is_catch else dn
            sub = defs.get(floor) if is_catch else e
            desc = clean((sub if sub is not None else e).findtext("description")) if (sub is not None or e is not None) else ""
            label = r.get("label") or dn
            ke = defs.get("kind:" + dn)
            reg = REGISTER.get(b, DEFAULT_REG)
            base = {"rimflow_item_id": ITEM, "target_def": dn, "priority": PRIORITY.get(b, 15), "background": "transparent",
                    "channel": "codex", "biome_register": reg, "owner_note": OWNER_NOTE, "style_notes": HOUSE}
            if kind == "flora":
                prompt = f"RimWorld plant sprite, painterly: the {label}. {desc} Our own original design, drawn fresh; not a recognisable Earth houseplant, not a cactus. One plant, centred."
                job = dict(base, id=f"phreg_{dn}_v1", prompt=prompt, canvas_w=256, canvas_h=256, facings=[])
            elif is_catch:
                prompt = f"RimWorld item sprite, painterly: a single freshly caught {label.lower().replace(' catch','')} laid out as a harvested catch, whole body. {desc} Match the floor creature's anatomy. Our own original design; not a plant, not generic meat. One item, centred."
                job = dict(base, id=f"phreg_{dn}_v1", prompt=prompt, canvas_w=128, canvas_h=128, facings=[])
                pick = [a for a in artsrc if a.startswith(("greysea_" + floor[3:].lower(), floor)) and a.endswith("_east")]
                for a in pick:
                    pngs = sorted((ART / "_artsrc" / a).glob("*.png"))
                    if pngs:
                        job["canon_reference"] = [str(pngs[0])]
                        break
            else:
                ds = draw_size(e, ke) if e is not None else 1.0
                px = 512 if ds >= BIG else 256
                prompt = f"RimWorld creature sprite, painterly: the {label}. {desc} Our own original design, drawn fresh; no recognisable Earth animal. One animal, whole body, centred."
                job = dict(base, id=f"phreg_{dn}_v1", prompt=prompt, canvas_w=px, canvas_h=px, drawsize=ds,
                           facings=["east", "south", "north"])
            if not desc:
                job["no_description_in_def"] = True
            job["biome"] = b
            jobs.append(job)
    out.write_text(json.dumps(jobs, indent=1))
    rep = out.with_name(out.stem + "_render_exists_not_installed.json")
    rep.write_text(json.dumps(have, indent=1))
    return jobs, have


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else REPO / "Transient/biome_ffar/placeholder_regen_jobs_2026-10-05.json"
    jobs, have = build(out)
    from collections import Counter
    print("jobs rows:", len(jobs), Counter(j["biome"] for j in jobs).most_common())
    print("render exists, not installed:", len(have), "; no description:", sum(1 for j in jobs if j.get("no_description_in_def")))
