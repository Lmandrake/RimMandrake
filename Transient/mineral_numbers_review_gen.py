#!/usr/bin/env python3
"""Generates Transient/mineral_numbers_review_2026-10-03.html + .decisions.json prefill.
Reads design/RimMandrake/mineral_abundance_registry_2026-10-03.csv. Safe to rerun for the SHEET;
refuses to rewrite the decisions file if the sheet has touched it."""
import csv, json, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = f"{R}/design/RimMandrake/mineral_abundance_registry_2026-10-03.csv"
TPL = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")
OUT = f"{R}/Transient/mineral_numbers_review_2026-10-03.html"
DEC = f"{R}/Transient/mineral_numbers_review_2026-10-03.decisions.json"

# units per deposit + the stated assumption, per material (row in the CSV). CSV units_per_cell_or_find x cells.
# vein (F1/F2) = 30 cells (design section 4: mean of 20-40). Everything else is an AGENT ASSUMPTION.
VEIN, NOD, CRY, SEAM = 30, 10, 6, 20
DEP = {  # material: (cells_or_per_source, basis text)
 "steel": (VEIN, "vein lump, 30 cells x 40/cell (design section 4)"),
 "chimney iron": (NOD, "nodule cluster, 10 cells x 30/cell (assumed)"),
 "gold": (NOD, "nodule cluster, 10 cells x 40/cell (assumed)"),
 "silver": (NOD, "nodule cluster, 10 cells x 40/cell (assumed)"),
 "uranium": (NOD, "nodule cluster, 10 cells x 40/cell (assumed)"),
 "uraninite": (CRY, "crystal cluster, 6 cells x 5/cell (assumed)"),
 "magnetite": (CRY, "crystal cluster, 6 cells x 5/cell (assumed)"),
 "jade": (VEIN, "vein lump, 30 cells x 40/cell (design section 4)"),
 "obsidian": (VEIN, "vein lump, 30 cells x 40/cell (design section 4)"),
 "diamond": (CRY, "crystal cluster, 6 cells x 20/cell (assumed)"),
 "ruby": (CRY, "crystal cluster, 6 cells x 20/cell (assumed)"),
 "sapphire": (CRY, "crystal cluster, 6 cells x 20/cell (assumed)"),
 "rough gem (Minerals Sparkle)": (CRY, "crystal cluster, 6 cells x 1/cell (assumed)"),
 "pyrinth": (VEIN, "vein lump, 30 cells x 10/cell (design section 4)"),
 "kyber": (CRY, "formation, 6 cells x 1/cell (assumed)"),
 "glowstone": (CRY, "cluster, 6 cells x 3/cell (assumed)"),
 "lanternstone": (VEIN, "rock-wall lump, 30 cells x 1/cell (assumed; it is a rock type, so many deposits)"),
 "dead smartsteel": (10, "salvage seam, 10 cells x 20/cell (assumed)"),
 "amber": (SEAM, "stratum seam, 20 cells x 20/cell (assumed)"),
 "fossils": (SEAM, "stratum seam, 20 cells x 20/cell (assumed)"),
 "coarse and crystal salts": (CRY, "great crystal, 6 cells x 20/cell (assumed)"),
 "cooking salt (VCE)": (40, "basin crust, 40 cells x 5/cell (assumed)"),
 "brine plate, drazz, tekk": (10, "colony bed, 10 cells x 10/cell (assumed)"),
 "bezoars": (1, "one carcass seam = 1 find x 5 (assumed)"),
 "mindstone": (10, "custom-location cache, 10 x 5 (assumed)"),
 "Rakatan hull shard": (20, "one wreck holds ~20 shards (assumed)"),
}
SRC_YR = 10  # regrowing sources: each vent/crust/colony yields 10 units/yr (assumed)
YR = {"seep-salt","delta salt","fulgurite","rime nodules (propane)","gallium","vexxith","Mother-of-Scaldpearl"}
# presence promised by a biome doc / built / ruled (the NUMBER is still a guess everywhere)
INTENT = {
 ("RM_SeabedFloor_TheScald",m) for m in ["chimney iron","gold","silver","uranium","uraninite","magnetite","pyrinth","seep-salt","Mother-of-Scaldpearl","Rakatan hull shard"]}
INTENT |= {("RM_TheForge","obsidian"),("RM_Pyrelands","fulgurite"),("RM_Stillsand","fulgurite"),("RM_LanternDeeps","pyrinth"),
 ("RM_LanternDeeps","kyber"),("RM_LanternDeeps","lanternstone"),("RM_LanternDeeps","mindstone"),("RM_RustCathedral","dead smartsteel"),
 ("RM_GreySea","coarse and crystal salts"),("RM_SeabedFloor_GreySea","coarse and crystal salts"),("RM_WeepingStones","seep-salt"),
 ("RM_Miasma","delta salt"),("RM_Wasteland","cooking salt (VCE)"),("RM_Wasteland","brine plate, drazz, tekk"),("RM_Wasteland","bezoars"),
 ("RM_TheChill","rime nodules (propane)"),("RM_Contagion","gallium"),("RM_Cauldron","vexxith"),("RM_FloodedCanyon","fossils")}
PLACER = {"gold","silver","rough gem (Minerals Sparkle)","jade","diamond","ruby","sapphire","magnetite","uraninite","uranium"}

rows = list(csv.DictReader(open(CSV)))
cols = list(rows[0].keys())
biomes = [c for c in cols if c.startswith(("RM_","RUT_"))]
mats = [r for r in rows if r["unit"] in ("EPM","EPM/yr") and r["material"] in DEP or r["material"] in YR]
def unit_size(r):
    m=r["material"]
    if m in YR: return SRC_YR, f"regrowing source, {SRC_YR} units/yr each (assumed)"
    ppc=float(r["units_per_cell_or_find"]); cells,basis=DEP[m]
    return ppc*cells, basis
def dep(v, size): return round(v/size, 2 if v/size<10 else 1)

items=[]; decs={}
ctx_other = [r for r in rows if r["unit"] not in ("EPM","EPM/yr")]
for b in biomes:
    cells=[]
    for r in mats:
        m=r["material"]; raw=r[b]; size,basis=unit_size(r)
        if raw in ("","0"): v=0.0; prov="zero"
        elif raw=="unbounded": cells.append(dict(m=m,unb=True)); continue
        else: v=dep(float(raw),size); prov="intent" if (b,m) in INTENT else "guess"
        if m=="steel" and v==0: prov="owner-intent-zero"
        # rivers carry
        riv=0.0
        if m in PLACER and v>0 and "SeabedFloor" not in b:
            riv=round(max(0.1, v*0.5),1) if v>=1 else round(v*0.5,2)
        cells.append(dict(m=m,v=v,rv=riv,prov=prov,size=size,basis=basis,raw=float(raw or 0),yr=m in YR))
    nz=[c for c in cells if c.get("v")]
    steel=next((c for c in cells if c["m"]=="steel"),None)
    bare = len(nz)<=(1 if steel and steel["v"] else 0)
    grp = "Sea floors" if "SeabedFloor" in b else ("RUT-only biomes (campaign layer)" if b.startswith("RUT_") else "RM biomes")
    eff = (f"{len(nz)} of {len(cells)} materials present. " +
           ("Bare biome: local rock only"+(" (steel "+str(steel['v'])+" deposits)" if steel and steel['v'] else ", no iron")+"." if bare else
            "Carries: "+", ".join(f"{c['m']} {c['v']}" for c in nz[:6])+("..." if len(nz)>6 else "")+"."))
    items.append(dict(id=b,prefill="pending",label=b.replace("_"," "),group=grp,effect=eff,cells=cells,bare=bare,
                      contested=bool(any(c.get("prov")=="intent" for c in cells)) and False))
    vals={c["m"]:c["v"] for c in cells if "v" in c}; rv={c["m"]:c["rv"] for c in cells if "v" in c}
# prefill decisions file: NO approvals, only the proposed values for reference (rows absent => nothing ruled)
mat_info=[dict(m=r["material"],form=r["form"],unit=r["unit"],size=unit_size(r)[0],basis=unit_size(r)[1]) for r in mats]
other=[dict(m=r["material"],form=r["form"],note="off-map / not a per-map deposit (salvage, trade, deep share) - not on this sheet") for r in ctx_other if r["material"]!="donor oddities"]
cfg=dict(sheetId="mineral_numbers_review_2026-10-03",title="Mineral abundance - deposits per map",
 subtitle="item MINERALS_WHERE_THEY_BELONG_1",
 criterion="Rows are biomes; every number is an agent GUESS converted from the draft registry's units-per-map. Ordered by biome group, then CSV order. This ranks nothing for worth - you judge whether a biome should bear a thing at all, and how often.",
 invented=[
  "Deposit sizes (cells per deposit, and units per cell) for every material except the plain veins are MY ASSUMPTIONS - the design only states vein = ~30 cells. Change a size and every number for that material scales; tell me in a note.",
  "Regrowing sources (salts, fulgurite, gallium...) are converted at 10 units per year per source - invented, so 'deposits' there means vents/crusts/colonies.",
  "Rivers-carry = half the biome's own deposit count of each hard-wearing mineral (gold, silver, gems, jade, magnetite, uranium...), min 0.1, none on sea floors. Pure heuristic; unit is PLACER BARS per map (gravel bars to pan or sluice).",
  "Provenance 'intent' means a biome doc / built def / ruling says the biome HAS the material; the NUMBER is still a guess. 'guess' means even the presence is mine."],
 posture=dict(mode="whitelist",explain="Default is NOT APPROVED (the pre-filled state, no human ruling). A row is approved only when you tick Approve row; unapproved rows ship nothing. Your edited numbers are saved with the row either way."),
 options=[dict(key="pending",label="Not approved",hotkey="0",color="#98a2b3",counts="out"),dict(key="approve",label="Approve row",hotkey="1",color="#5ac37f",counts="in"),
          dict(key="discuss",label="Discuss",hotkey="2",color="#e8b64c",counts="out")],
 groupLabel="biome group",media=False,decisionsFile=os.path.basename(DEC),decisionsPath="",sheetPath="",
 briefHtml="""<p><b>What this is.</b> The settings unit is <b>deposits per map</b>. Each biome row lists every material with a proposed number you can edit, and a separate <b>rivers carry</b> number (placer bars for panning and sluicing). Nothing is pre-approved: every row starts as 'Not approved' (the gate needs a neutral default; it is not a ruling).</p>
<p><b>Rulings already in:</b> unknown-mod ores behave as their mod intends (no row needed) - bare biomes give local rock only - deep drill gives iron plus home-biome deposits - quarries yield only local materials. Salvage, trade and deep-share channels are not on this sheet.</p>
<p><b>How to use:</b> change any number, type why in the notes box, tick <b>Approve row</b>. Cells shaded amber are values you changed. Zero cells are tucked under 'zero materials'. Hover a number for units per deposit and its basis. Off-map materials not shown: """ + "; ".join(o["m"] for o in other) + """.</p>
<p>Deposit size per material: see the table at the foot of this brief panel (scroll) - <span id="sizetab"></span></p>""")
cfg["materials"]=mat_info
html=open(TPL).read()
html=re.sub(r'(<script id="CONFIG" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+json.dumps(cfg,ensure_ascii=False).replace("</","<\\/")+"\n"+m.group(2),html,count=1,flags=re.S)
html=re.sub(r'(<script id="ITEMS" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+json.dumps(items,ensure_ascii=False).replace("</","<\\/")+"\n"+m.group(2),html,count=1,flags=re.S)
html=html.replace("<title>Review sheet</title>","<title>Mineral numbers review</title>")
render=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"mineral_numbers_render.js")).read()
i=html.rindex("</body>")
html=html[:i]+'<script id="RENDER2">\n'+render+'\n</script>\n'+html[i:]
open(OUT+".tmp","w").write(html); 
print("items",len(items),"mats",len(mats))
os.replace(OUT+".tmp",OUT)
if os.path.exists(DEC) and json.load(open(DEC)).get("savedBy"):
    print("decisions file touched by sheet - NOT rewritten")
else:
    json.dump(dict(sheetId=cfg["sheetId"],posture="whitelist",criterion=cfg["criterion"],
        reviewStatus=dict(state="prefill",by=None,at=None,evidence="agent-generated proposal; no human has ruled"),
        proposed={it["id"]:{c["m"]:{"deposits":c.get("v"),"rivers":c.get("rv"),"prov":c.get("prov")} for c in it["cells"] if "v" in c} for it in items},
        decisions={it["id"]:{"decision":"pending","prefill":"pending","note":""} for it in items}),open(DEC,"w"),indent=1)
