#!/usr/bin/env python3
"""Builds design/RimMandrake/dessicated_corpses_commission_2026-10-16.json: one artpipe row per SWAC-donor-bytes
dessicated corpse slot (63: 61 role=dessicated + the two Snoruuk ones the ledger leaves role-less). Inputs (scratch, rerunnable):
donorlive_207.json (ledger Index.live joined to donor variants), dess_found.json (XML scan of dessicatedBodyGraphicData),
jobindex.json (artpipe done jobs). Reference = the species' own body art as canon_reference (NEVER `reference`: that arms reskin-validate)."""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[2] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import json, glob, os, re, shutil, collections
from pathlib import Path
R = Path("/home/mandrake/rm/foundry"); os.chdir(R)
WORK = Path("/home/mandrake/.seat-tmp/FOUNDRY/work")
REFS = Path(rm_str("artpipe", "_refs", "dessicated")); REFS.mkdir(parents=True, exist_ok=True)
SW = "src/RimStarWars/SWBestiary/Textures/"
live = json.load(open(WORK/"donorlive_207.json"))
slots = [o for o in live if o["role"] == "dessicated" or (o["rel"].startswith("swanimals/Snoruuk/") and "Dessicated" in o["rel"])]
donor_rels = {o["rel"][:-4] for o in live}
found = json.load(open(WORK/"dess_found.json"))
jobs = json.load(open(WORK/"jobindex.json"))
SPECIAL = {"swanimals/JungleRancor/JungleRancor_Dessicated": ("RSW_JungleRancor", 8.0, "swanimals/JungleRancor/JungleRancor"),
           "swanimals/Mastmot/Mastmot_f_Dessicated": ("RSW_Mastmot", 4.75, "swanimals/Mastmot/Mastmot_f")}
STYLE = ("Painterly vanilla-RimWorld house style, matte, no outlines, never cute; one centred carcass on a transparent background, "
         "no ground, no props, no baked shadow. Realistic natural-history illustration, grounded anatomy.")

def find_png(tp):
    c = glob.glob(f"src/**/Textures/{tp}_east.png", recursive=True) + glob.glob(f"src/**/Textures/{tp}.png", recursive=True)
    return c[0] if c else None

def body_ref(body):
    """(path, kind): installed own art if not still donor bytes; else newest finished artpipe east render; else None."""
    p = find_png(body)
    if p and (p.split("/Textures/")[1][:-4].replace("_east", "")) not in {d.replace("_east", "") for d in donor_rels}:
        return p, "installed"
    done = sorted([j for j in jobs if j["tp"] == body and j["facing"] == "east" and j["state"] == "done"], key=lambda j: j["id"])
    for j in reversed(done):
        q = rm_path("artpipe", "_artsrc", j['id'], f"{j['id']}.png")
        if q.exists(): return str(q), "render:" + j["id"]
    return None, None

rows = []; kinds = collections.Counter()
for o in slots:
    tp = o["rel"][:-4].replace("_east", ""); ftail = tp.split("/")[-1]; sp = tp.split("/")[1]
    f = found.get(tp, [])
    if tp in SPECIAL: tdef, ds, body = SPECIAL[tp]
    else:
        tdef = (o["subjects"] or [f[0]["def_"]])[0]
        if tp.endswith("Rancor_Dessicated") and "Rancor/Rancor_" in tp: tdef = "RSW_Rancor"
        ds = max(float(x["ds"]) for x in f)
        c = collections.Counter(x["body"] for x in f if x["body"]); body = c.most_common(1)[0][0]
    ref, kind = body_ref(body); kinds[(kind or "none").split(":")[0]] += 1
    label = re.sub(r"(?<!^)([A-Z])", r" \1", sp).lower()
    stage = "a JUVENILE (young, smaller, softer proportions)" if re.search(r"_j_", ftail) else "the adult"
    canvas = 512 if ds <= 4 else 768
    prompt = (f"RimWorld creature corpse sprite, dessicated stage: the long-dead, sun-dried remains of {stage} {label}. "
              + ("The attached image shows the living animal: keep its exact proportions, limb count, head shape, horns, crests and tail, and draw only its dried remains. " if ref else "")
              + "VIEW: orthographic side view, head toward the right (east), the whole carcass slumped on its belly and filling the frame width, centred. "
              "SUBJECT: pale bleached bone and parchment-tan skin drawn tight over the frame; the skull with hollow sockets, the ribcage standing out rib by rib, "
              "the spine and limb bones, a few brittle strips of dried hide in the animal's own colours clinging at the joints and the hollow flank. "
              f"SCALE: {ds:g}x{ds:g} cells at its largest stage (a colonist is about 1 cell); the carcass spans the frame as the living animal would. "
              "Matte, dry, weathered, quiet.")
    multi = tp.endswith("FrogDog_Dessicated")
    sid = re.sub(r"[^a-z0-9]+", "_", ftail.lower()).strip("_")
    row = {"id": f"dessic_{sid}_v1", "rimflow_item_id": "DESSICATED_CORPSES_REDRAW_ONE_BY_ONE", "prompt": prompt,
           "canvas_w": canvas, "canvas_h": canvas, "drawsize": ds, "facings": "east" if multi else "", "priority": 51,
           "style_notes": STYLE, "target_def": tdef, "target_texpath": tp,
           "install_to": SW + tp + ("_{facing}.png" if multi else ".png"), "biome_neutral": True, "background": "transparent"}
    if canvas == 512 and ds < 4: row["oversize_reason"] = "detail floor: 512px so the painted bones read (owner: sizing errs generous)"
    if ref:
        d = REFS/sp.lower(); d.mkdir(exist_ok=True); dst = d/(Path(ref).stem + ".png"); shutil.copy2(ref, dst)
        row["canon_reference"] = [str(dst)]
    rows.append(row)
json.dump(rows, open(R/"design/RimMandrake/dessicated_corpses_commission_2026-10-16.json", "w"), indent=1)
print(len(rows), dict(kinds))
