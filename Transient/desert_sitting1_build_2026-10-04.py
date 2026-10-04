#!/usr/bin/env python3
"""Build desert re-review SITTING 1 (ART_VERSION_WRANGLING_1): the 14 at-risk creatures first,
then the rest of the Desert biome's rows. Biome split: Transient/desert_sittings_assignment_2026-10-04.json
(see Transient/desert_sittings_plan_2026-10-04.md). Generator: src/RimMandrake/Utils/art/art_sheet.py."""
import json, re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import art_sheet as A  # noqa: E402

rows = json.load(open(REPO / "Transient/desert_sittings_assignment_2026-10-04.json"))
d03 = json.load(open(REPO / "Transient/desert_art_review_2026-10-03.decisions.json"))["decisions"]
ATRISK = ['A_Anooba', 'A_Bolotaur', 'A_AA_BoulderMit', 'A_AA_Eyeling', 'A_IridonianReek', 'A_Jamel', 'A_Kreetle',
          'A_AA_MammothWorm', 'A_Ronto', 'A_AA_SandProwler', 'A_AA_Terramorph', 'A_Whisperbird', 'A_AA_Wildpod', 'A_Zeer']
by = {r['id']: r for r in rows}
order = [by[i] for i in ATRISK]
rest = sorted((r for r in rows if r['biome'] == 'desert' and not r['atrisk'] and 'INVENTED' not in r['why']), key=lambda r: r['word'].lower())
arid = sorted((r for r in rows if r['biome'] == 'desert' and not r['atrisk'] and 'INVENTED' in r['why']), key=lambda r: r['word'].lower())
res, meta, skipped = [], {}, []
for sec, label, rs in (("1", "AT RISK", order), ("2", "Desert", rest), ("3", "Arid-Shrubland-only (placed here)", arid)):
    for r in rs:
        if not r['res']:
            skipped.append(r); continue
        donor = re.sub(r'^[AP]_', '', r['id'])
        name = f"{r['word']} ({r['ported']})"
        for tp in r['res']:
            res.append(tp)
            dec = d03.get(r['id'])
            meta[tp] = {
                "group": f"{sec} {label} · {r['word']}", "name": name,
                "subject_keys": [r['id'], donor, r['ported'], r['word']],
                "canon_names": [r['word'], r['ported'], donor, re.sub(r'^AA_', '', donor)],
                "flags": (["AT RISK: your earlier keep would be replaced by the 10-03 'keep render'"] if r['atrisk'] else []),
                "flawed": ({"decision": dec.get('decision', ''), "note": dec.get('note', '')} if dec and (dec.get('decision') or dec.get('note')) else None),
                "context": f"biome: {r['biome']} — {r['why']}",
            }
BRIEF = """<p><b>Desert re-review, sitting 1 of 3.</b> The 14 creatures at risk come first: your earlier keep of their art
would be <i>replaced</i> by the 2026-10-03 sheet's 'keep render'. After them, the rest of the <b>Desert</b> biome's
creatures and plants; last, the rows cast only in Arid Shrubland (no desert, deep-desert or blue-desert roster names them),
placed here for now.</p>
<p><b>Per row, pick the ONE column the game should show</b> (keep a variant), or <b>none — redo</b> with a note saying what to
change. Every version is side by side: <b>IN GAME</b> (blue frame), other shipped copies, artpipe <b>renders</b>, <b>history</b>
from git, the <b>donor original</b>, and on the right the <b>canon reference</b> with its Must-show list (not pickable).
South / east / north are stacked. Masks and corpse textures are never offered as art.</p>
<p><b>✕ on any non-live picture = purge</b>: the erroneous render is deleted from the art store and stops appearing on any future
sheet. Rows prefill with your <b>latest keep</b>, else what the game shows now. Your 2026-10-03 verdict and note are shown per
row, marked as made against a flawed sheet. Nothing installs from here: picks become ledger rulings, then you see an install plan.</p>"""
INV = ["Biome split is MINE, derived from live roster commonality (Desert / ExtremeDesert+RM_Stillsand / RM_BlueDesert), "
       "with the design sheets as tiebreak; rows cast only in Arid Shrubland were placed in this Desert sitting (group 3) "
       "because none of the three rosters names them. Plan: Transient/desert_sittings_plan_2026-10-04.md."]
out = REPO / "Transient/desert_sitting1_2026-10-04.html"
r = A.generate(res, out, "Desert sitting 1: at-risk first", "desert_sitting1_2026-10-04", BRIEF, meta, INV)
r["skipped_no_graphic"] = [x['id'] for x in skipped]
print(json.dumps(r, indent=1))
