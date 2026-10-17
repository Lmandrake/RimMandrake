from PIL import Image, ImageDraw
D='/home/mandrake/rm/bench/Transient/river_hose_art_review_2026-10-16/'
rows=[
 ('weir_scene_3x.png',None,'WEIR (offline)','Reads as a fish trap / collapsed walkway, not a dam. No crest, no spill, no pool; baked 3/4 perspective breaks under rotation; 2 cells cannot span a river. Redraw as a low blunt sill + spill/foam overlay.'),
 ('river_works_textures_zoom.png',(394,0,780,402),'BANK STAKE','Reads as a lamp post (good) but not as a levee: separate posts hold nothing. Add connected ridge/wall between stakes.'),
 ('river_works_textures_zoom.png',(788,0,1170,402),'SILT TRAP','Reads as a plain timber fence. Needs water contact, a sheltered pocket and a visible silt wedge.'),
 ('river_works_textures_zoom.png',(1182,0,1566,402),'FERRY POST + ROPE','Post reads as a winch/bollard; a ferry needs the rope visibly running across to a far post/raft.'),
 ('ford_composite.png',None,'FORD STONES (offline, my read)','Tiles into a continuous paved strip (reads as a bridge); the def does not even use this file (vanilla Flagstone tint). Needs gaps with water between stones.'),
 ('live_pump_reel_hose_crop.png',None,'PUMP + HOSE (LIVE)','Pump is a tiny fitting; the hose coupling is wider than the pump. Joins: nothing physically roots into the machine.'),
 ('reel_pump_tank_adjacent_Industrial.png',None,'REEL | PUMP | TANK (offline)','Reel dwarfs tank and hides the pump; no facing ports, no direction cue, hose does not leave the drum tangentially. Disconnected at a glance.'),
 ('live_pipe_tank_crop.png',None,'PIPE -> TANK (LIVE)','Pipe vanishes behind the tank foot; reads as passing behind, not entering. Needs an exposed nozzle + flange.'),
]
W=1500; th=190; out=Image.new('RGB',(W,len(rows)*(th+10)+50),(24,24,24)); d=ImageDraw.Draw(out)
d.text((10,8),'River works + hose joins: current art and the Codex critique verdict (2026-10-16). Art is NOT changed. See REVIEW.md.',fill=(255,255,255))
y=40
for f,box,t,v in rows:
    im=Image.open(D+f).convert('RGB')
    if box: im=im.crop(box)
    im.thumbnail((420,th)); out.paste(im,(10,y))
    d.text((450,y+4),t,fill=(255,210,90))
    import textwrap
    for i,l in enumerate(textwrap.wrap(v,105)): d.text((450,y+26+i*15),l,fill=(230,230,230))
    y+=th+10
out.save(D+'overview.png')
