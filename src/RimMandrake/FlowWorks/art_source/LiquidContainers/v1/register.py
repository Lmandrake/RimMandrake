"""File the 12 pilot sprites (+3 tint previews each) as finished artpipe render families and write the --textures
manifest for art_sheet.py. Column 'base' is the installable sprite (liquid region neutral grey, tinted in game by the
_m mask); the tint columns are PREVIEWS of the same file and carry no target_texpath, so nothing installs them."""
import json, shutil, time
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
AP = Path("/mnt/d/Luke/dev/_artpipe")
ITEM = "LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS"
DRAW = {"Bottle": 0.75, "Bucket": 1.0, "Barrel": 1.4}
LOOK = {"Scrapper": "junker: odd-shaped scavenged", "Industrial": "industrial: generic water bottle / steel pail / oil drum",
        "Modern": "modern: multicoloured soda bottle / plastic pail / plastic drum", "Futuristic": "futuristic: hexagonal canteen / hex pail / hex tank"}
VAR = ["base", "freshwater", "toxic", "tar"]
rows = []
for size in DRAW:
    for style in LOOK:
        d = HERE / "out" / size / style
        jobs = []
        for v in VAR:
            jid = f"liqcont_{size.lower()}_{style.lower()}_{v}"
            src = d / (f"RM_{size}.png" if v == "base" else f"tint_{v}.png")
            od = AP / "_artsrc" / jid; od.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, od / f"{jid}.png")
            rec = {"id": jid, "channel": "codex", "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "facing": "south", "drawsize": DRAW[size], "canvas": {"width": 256, "height": 256},
                   "background": "transparent", "rimflow_item_id": ITEM,
                   "source_file": str(src.relative_to(REPO)),
                   "prompt": (f"RM_{size} {style} ({LOOK[style]}). Installable sprite; liquid region neutral grey, "
                              f"mask RM_{size}_m.png red = liquid. Generator art_source/LiquidContainers/v1") if v == "base" else
                             f"TINT PREVIEW ONLY (never install): RM_{size} {style} filled with {v}, mask x LiquidDef colour"}
            if v == "base":
                rec["target_texpath"] = f"Things/Item/Resource/FlowWorks/{style}/RM_{size}"
            (AP / "done" / f"{jid}.json").write_text(json.dumps(rec, indent=2, sort_keys=True))
            jobs.append(jid)
        rows.append({"key": f"RM_{size}_{style}", "label": f"{size.lower()}, {LOOK[style]}  (columns: base, fresh water, toxic water, tar)",
                     "part": size.lower(), "look": style.lower(), "section": f"Liquid containers: {size.lower()}s",
                     "resources": [f"Things/Item/Resource/FlowWorks/{style}/RM_{size}"],
                     "former": [f"Things/Item/Resource/FlowWorks/RM_{size}"],
                     "size": {"drawSize": [DRAW[size], DRAW[size]], "footprint": [1, 1],
                              "source": f"RM_{size}ItemBase graphicData drawSize {DRAW[size]} (RM_LiquidBottles_Base.xml), 1x1 item"},
                     "jobs": jobs, "render_match": "|".join(jobs)})
print(json.dumps({"rows": rows}, indent=1)[:0], len(rows), "rows,", sum(len(r["jobs"]) for r in rows), "jobs filed")
Path(REPO / "Transient/liquid_containers_2026-10-16").mkdir(parents=True, exist_ok=True)
lead = Path(HERE / "lead.html").read_text()
(REPO / "Transient/liquid_containers_2026-10-16/liquid_containers_textures.json").write_text(
    json.dumps({"rows": rows, "lead_html": lead}, indent=1))
