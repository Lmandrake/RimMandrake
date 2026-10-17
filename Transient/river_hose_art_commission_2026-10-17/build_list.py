import json
FW="src/RimMandrake/FlowWorks/Textures/"
ITEM="RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS"
OWN="judged in game (owner card 2026-10-17: commission all seven unruled river/hose art fixes)"
FAM=("SIZE FAMILY (chosen, pass A): hose strand 10-12 px wide, rigid pipe 10 px, coupling/union 16-20 px, port stub 8x8, flange collar 3x14, "
     "all at 64 px per cell native; nothing wider than the cell it sits in. Pass B's 6 px hose rejected: it vanishes at game zoom and reads as a cable.")
LOOKS={"Scrapper":"salvaged rust, mismatched plates, rope lashings","Industrial":"gunmetal steel, hazard yellow, hex bolts",
 "Modern":"glossy red paint, chrome, clean sawn timber","Futuristic":"white composite, pale grey seams, glowing cyan strip"}
rows=[]
def add(id_,item,target,texpath,w,h,ref,prompt,look=None,facings=""):
    notes=f"REVIEW item {item} (Transient/river_hose_art_review_2026-10-16/REVIEW.md). {FAM} Look: {look}={LOOKS[look]}. " if look else f"REVIEW item {item}. {FAM} "
    rows.append(dict(id=id_,rimflow_item_id=ITEM,prompt=prompt,canvas_w=w,canvas_h=h,canon_reference=ref,facings=facings,
      style_notes=notes+"Same camera, palette and material as the attached existing sprite; change only what the prompt names. Real alpha, no ground, no water, no cast shadow.",
      owner_note=OWN,target_def=target,target_texpath=texpath,biome_neutral=True,priority=20))
for L in LOOKS:
    tank=f"{FW}RimMandrake/FlowWorks/Tank/{L}/RM_LiquidTank.png"
    add(f"RM_LiquidTank_ports_{L}",3,"RM_LiquidTank",f"RimMandrake/FlowWorks/Tank/{L}/RM_LiquidTank",512,512,tank,
     "Redraw this liquid tank with visible facing PORTS: an explicit nozzle neck (8x8 px stub at 64 px/cell scale) rooted on the body on each cell-edge lane (32 or 96 px along a 2-cell edge, not the midpoint), a flange collar (3x14), and an exposed 8-12 px bridge of short spool so a pipe or hose visibly enters a socket and never vanishes behind the foot. Unused ports show a blanking cap (3x10). Keep body, silhouette and footprint.",L)
    reel=f"{FW}RimMandrake/FlowWorks/Hose/Styles/{L}/Reel_PumpHookup.png" if L!="Scrapper" else f"{FW}RimMandrake/FlowWorks/Hose/Reel_PumpHookup.png"
    rdep=reel.replace("PumpHookup","Deployed")
    rp=("Redraw this hose reel SMALLER: about 120 px wide overall against today's about 170 (same 2x2 cell centre), drum clearly visible, "
        "a visible supply swivel on the pump-facing side with a flexible whip + union (8x12) into it, and a tangential payout GUIDE (fairlead about 16x10 px) with the hose leaving the drum's lower tangent through it, "
        "traceable 12-18 px before first bend, ending under the coupling lip; the reel's valve housing must not look like it pumps. ")
    add(f"RM_HoseReel_smaller_fairlead_{L}_PumpHookup",6,"RM_HoseReel",f"RimMandrake/FlowWorks/Hose/{'Styles/'+L+'/' if L!='Scrapper' else ''}Reel_PumpHookup",256,256,reel,rp+"State: hose reeled in, parked end in a cradle.",L)
    add(f"RM_HoseReel_smaller_fairlead_{L}_Deployed",6,"RM_HoseReel",f"RimMandrake/FlowWorks/Hose/{'Styles/'+L+'/' if L!='Scrapper' else ''}Reel_Deployed",256,256,rdep,rp+"State: deployed, empty drum with its hose inlet at the fairlead; must match the PumpHookup render's scale and drum exactly.",L)
    pump=f"{FW}Things/Building/FlowWorks/Machinery/RM_LiquidPump.png"
    add(f"RM_LiquidPump_ports_arrow_{L}",'3+7',"RM_LiquidPump","Things/Building/FlowWorks/Machinery/RM_LiquidPump",512,256,pump,
     "Redraw as a heftier 2x1 pump skid (body about 108-116 x 46-54 px at 64 px/cell, raised camera, not a side elevation): opposed ports on cell-edge lanes - axial suction port on one end, a distinct radial elbowed discharge outlet on the other, each with nozzle neck 8x8, flange collar 3x14 and an exposed 8-12 px bridge of spool; fewer striped collars; plus a FLOW ARROW about 10x6 px on the pump top showing suction-to-discharge direction. Nothing wider than the 2x1 footprint.",L)
    for part,w,h,txt in (("Coupling_Bare",128,128,"Redraw the hose coupling/union as a 16-20 px-wide fitting at 64 px/cell (today about 70 px, wider than the pump cell), centred, same look and material."),("Strand_Plump",256,64,"Redraw the hose strand as a 10-12 px-wide tile (at 64 px/cell), centred vertically, ends flush left and right, tiles seamlessly, same material.")):
        d=f"{FW}RimMandrake/FlowWorks/Hose/"+("" if L=="Scrapper" else f"Styles/{L}/")
        add(f"RM_Hose_{part}_gauge_{L}",4,"RM_HoseReel",d.split("Textures/")[1]+part,w,h,d+part+".png",txt,L)
# look-free river pieces (single art today)
R=f"{FW}Things/Building/FlowWorks/Rivers/"
add("RM_BankStake_ridge","8","RM_BankStake","Things/Building/FlowWorks/Rivers/RM_BankStake",256,256,R+"RM_BankStake.png",
 "Add a connected earth ridge / crib-timber levee segment running left to right through the stake and continuing flush off both side edges, so adjacent stakes in a line read as one levee; 3-4 px crest highlight, damp strip on the water side, the stake lamp kept as a secondary marker and shrunk in dominance. Keep the lamp.")
add("RM_FerryPost_rope","9","RM_FerryPost","Things/Building/FlowWorks/Rivers/RM_FerryPost",256,256,R+"RM_FerryPost.png",
 "Keep the post (do not redraw it first); add a rope spool/tie-off at its top and a taut rope leaving tangentially toward the right edge, running to the canvas edge as a visible line so the existing 256x64 RM_FerryRope strip lines up post to post (rope centre at the canvas vertical middle at the edge). Reads as a rope anchor, not a winch or bollard.")
add("RM_FerryRope_strip","9","RM_FerryRope","Things/Building/FlowWorks/Rivers/RM_FerryRope",256,64,R+"RM_FerryRope.png",
 "Redraw the rope strip as a clearly visible taut rope, 6-8 px thick with twist highlights and a darker lower edge, centred vertically, both ends flush at the left and right edges, high enough contrast to show at game zoom.")
add("RM_SiltTrap_wedge","10","RM_SiltTrap","Things/Building/FlowWorks/Rivers/RM_SiltTrap",256,256,R+"RM_SiltTrap.png",
 "Show the baffle entering water: a wet dark band at its foot, a ripple at the tip, and a sediment wedge (about 24x40 px at 64 px/cell scale, silt-brown, asymmetric) piled against the upstream face with small water passages. Keep the fence timbers and footprint.")
json.dump(rows,open("art_list.json","w"),indent=1)
print(len(rows))
