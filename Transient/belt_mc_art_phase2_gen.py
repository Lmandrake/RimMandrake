import json
IT="MESSY_CONDUIT_MOD_1"
BASE="painterly RimWorld game sprite, matte low-shine surface, top-lit cylinder form with soft dark keyline, value over detail, transparent background, "
FAM={
"Cybertek":"top-down "+BASE+"ultra-sleek futuristic cybertek look, smooth brushed grey metallic sheathed cable, cool light-grey and gunmetal tones with a thin teal accent line, clean precision-machined fittings, tidy and modern",
"ExtCord":"top-down "+BASE+"cheap modern household extension cord look, glossy-matte coloured PVC insulation, mismatched ugly plastic joiners and power strips, slightly grubby, truck-drivers-in-space repaired feel, warm 70s palette",
"StarWars":"top-down "+BASE+"Star Wars used-future industrial look, dark worn greasy rubber and steel, soot grey, matte black, dark brown, rust, scuffed and repaired, all colours dark, no white or pale tones anywhere in the piece",
"Aerial":"painterly RimWorld game sprite, matte low-shine surface, value over detail, transparent background, weathered utility infrastructure, warm 70s-brown palette, dark weathered wood, grey porcelain and black wire, truck-drivers-in-space jury-rigged look",
"Hose":"top-down painterly RimWorld game sprite, matte low-shine surface, top-lit form with soft dark keyline, value over detail, transparent background, firefighter hose look, flat-woven canvas jacket in pale grey-tan, tarnished brass fittings, warm 70s-brown palette, grubby and used",
}
jobs=[]
def J(fam,name,w,h,prompt,notes=None,pri=62):
    jobs.append(dict(id=f"RM_MessyConduit_{fam}_{name}",rimflow_item_id=IT,prompt=prompt,canvas_w=w,canvas_h=h,style_notes=notes or FAM[fam],priority=pri,background="transparent"))
def strip(fam,name,desc,body=18):
    J(fam,name,128,32,f"Seamless horizontally tileable straight strip of {desc} seen from directly above, running edge to edge left to right, centred vertically with transparent margin above and below, the cable body about {body} px tall, left and right ends meet at identical height and shading so copies join invisibly.")
def set_(fam,cable,T,X,plug,wall,rock,dead):
    J(fam,"Node_T",128,128,"T junction node: "+T+" Three cable ends of "+cable+" leave it to the left, right and bottom edges at the vertical centre and horizontal centre, node about 50 px across at the centre.")
    J(fam,"Node_X",128,128,"X junction node: "+X+" Four cable ends of "+cable+" enter it at the left, right, top and bottom edge midpoints, node about 64 px across at the centre.")
    J(fam,"Plug_Casing",128,128,f"{cable} entering from the left edge at the vertical centre ending in "+plug+", seen from above, plug about 40 px long, pushed into a small casing socket on the right, transparent elsewhere.")
    J(fam,"Stub_Wall",128,128,"Wall stub plate: "+wall+f" A square plate about 72 px across centred on the canvas with a round hole in its centre where {cable} disappears into the wall, a short length of cable emerging toward the left edge.")
    J(fam,"Stub_Rock",128,128,"Rock cable hole: a rough round hole drilled into stone, about 56 px across centred on the canvas, chipped grey rim of broken rock, deep dark interior, "+f"{cable} emerging from the hole toward the left edge, "+rock)
    J(fam,"Decal_FrayedEndDead",64,64,f"Dead frayed cable end decal: {cable} coming in from the left edge at the vertical centre ending in a ragged cut with splayed dull copper wire strands, the copper dull tarnished and limp, "+dead+", transparent elsewhere.")
# Cybertek
strip("Cybertek","Strand","one slim smooth brushed grey metallic sheathed cable with a thin teal accent line along the top third",16)
set_("Cybertek","a slim brushed grey metallic cable","a sleek hexagonal gunmetal hub with a small teal glowing dot at its centre.","a sleek hexagonal gunmetal hub with a teal dot at its centre and four machined collars.","a slim machined gunmetal connector with a teal ring","a brushed steel square plate with four tiny hex bolts and a clean round grommet.","a neat machined collar where it enters,","a clean tidy cut and a faint grey smudge at the tip")
# ExtCord
cols={"Orange":"bright orange","Green":"bright green","Brown":"muddy brown","Yellow":"mustard yellow","Blue":"cobalt blue"}
for k,v in cols.items():
    strip("ExtCord","Strand_"+k,f"one thick glossy-matte {v} PVC extension cord with a faint stripe of lighter shade along the top third",18)
set_("ExtCord","a thick orange extension cord","an ugly mismatched plastic cube joiner in dirty beige-grey, three cord sockets, one cracked corner, a strip of electrical tape.","a dirty off-white power strip body lying across the node with five sockets, small red switch, and four cords plugged in from four sides, scuffed and cluttered.","a chunky mismatched orange-brown plastic three-prong plug","a dull scuffed beige plastic wall socket plate with two screws and a round hole, grime around it.","a loop of grubby electrical tape where it enters,","a smear of soot at the tip")
# StarWars
strip("StarWars","Strand_BlackRubber","one very thick smooth matte black rubber cable, broad faint sheen, no specular line",22)
strip("StarWars","Strand_CorrugatedSteel","one dark corrugated steel flexible hose with fine ribbing across its width, dark gunmetal with rust at the grooves",22)
strip("StarWars","Strand_CoiledBlack","one coiled black cable wound as a tight helix of matte black rubber loops, each loop visible, about 20 px tall",20)
set_("StarWars","a thick matte black rubber cable","a clamped dark steel junction clamp with two bolts, hose clamp band and oil stains.","a heavy dark scuffed steel junction box with bolted corners, a small amber lamp and grease smears.","a heavy dark grey industrial plug with a locking ring","a dark scuffed steel bulkhead plate with four rivets and a thick rubber grommet, rust and grease stains.","grease and grit around the rim,","a smudge of soot at the tip")
# Shared
J("Shared","SparkGlow",64,64,"Spark burst decal: a small cluster of bright yellow-white electric sparks and short orange streaks radiating from the centre with a soft warm orange glow halo fading to transparent, painterly, centred on the canvas.","painterly RimWorld game sprite, soft additive-style glow, transparent background, warm colours")
J("Aerial","Strand_Wire",128,32,"Seamless horizontally tileable straight strip of one thin dark weathered overhead power wire seen from the side, running edge to edge left to right, centred vertically, wire only about 6 px tall with a faint soft sheen on top, transparent margin above and below, left and right ends meet at identical height and shading so copies join invisibly, usable as a drooping catenary when bent.")
J("Aerial","Strand_WireShadow",128,32,"Seamless horizontally tileable soft drop-shadow strip for a thin wire: a blurred dark brown-black translucent band running edge to edge, centred vertically, about 10 px tall with feathered edges, uniform along its length, shadow only.")
J("Aerial","Pole_Top",128,128,"Utility pole seen from directly above: a round dark weathered wooden pole end about 36 px across at the centre, a long wooden crossarm about 110 px long running left to right through it, an insulator on each end of the arm, bolts and iron straps, rope tie marks, centred on the canvas.")
J("Aerial","Pole_Side",128,256,"Tall weathered wooden utility pole seen from the side, standing vertical and centred, base at the bottom edge with a small mound of packed earth, a wooden crossarm near the top with three grey porcelain insulators and short wire stubs leaving sideways, iron bolts, patched with tape, slight lean, leaving transparent space at the sides.")
J("Aerial","Insulator",64,64,"Grey porcelain pin insulator on a short wooden crossarm piece, a black wire wrapped around its groove, seen from slightly above, chipped, centred.")
J("Aerial","Hanger_Bracket",64,64,"Small rusty iron wall hanger bracket with a ceramic knob insulator and a black wire looped through it, seen from slightly above, centred.")
# Hose
J("Hose","Strand_Flat",256,64,"Seamless horizontally tileable straight strip of a collapsed empty fire hose lying flat on the ground, a limp wide woven canvas ribbon about 34 px tall, pale grey-tan flat-woven fabric with fine weave lines, two parallel stitched seams along its length, slightly wrinkled and soft, edge to edge left to right, centred vertically with transparent margin, left and right ends meet at identical height and shading so copies join invisibly.")
J("Hose","Strand_Plump",256,64,"Seamless horizontally tileable straight strip of a fully pressurised fire hose seen from above, a round swollen taut cylinder about 42 px tall, pale grey-tan woven canvas jacket with fine weave lines and one visible lengthwise seam, soft highlight along the top third with slight sheen, rounded smooth shading, edge to edge left to right, centred vertically with transparent margin, left and right ends meet at identical height and shading so copies join invisibly.")
J("Hose","Strand_Shadow",256,64,"Seamless horizontally tileable soft drop-shadow strip for a thick hose: a blurred dark brown-black translucent band running edge to edge left to right, centred vertically, about 46 px tall with feathered soft edges fading to transparency, uniform along its length, shadow only.")
J("Hose","Coupling_Brass",128,128,"Brass fire hose coupling: a threaded tarnished brass cylindrical end fitting with two lugs and ribbed grip, about 56 px long, a pale grey-tan canvas hose entering from the left edge at the vertical centre and joined into it, the threaded end on the right.")
J("Hose","Nozzle",128,128,"Fire hose nozzle: a tarnished brass and dark steel hand nozzle with a pistol-grip valve lever and tapered tip pointing right, a pale grey-tan canvas hose entering from the left edge at the vertical centre, about 90 px long overall.")
J("Hose","Reel_PumpHookup",128,128,"Hose reel and pump hookup: a squat dark red-brown steel pump housing about 70 px across with a round brass inlet valve wheel, a brass outlet coupling on the left edge at the vertical centre, a few coils of pale grey-tan canvas hose wound on a small reel, grease stains.")
J("Hose","EndCap",128,128,"Hose end cap: a threaded brass blanking cap screwed onto the end of a pale grey-tan canvas hose entering from the left edge at the vertical centre, a short chain tying the cap to the hose, tarnished and dented, about 44 px long.")
for j in jobs:
    if j["id"].startswith("RM_MessyConduit_Shared"): j["id"]=j["id"].replace("Shared_","Shared_")
json.dump(jobs,open("/home/mandrake/rm/foundry/Transient/belt_mc_art_phase2_jobs.json","w"),indent=1)
print(len(jobs))
