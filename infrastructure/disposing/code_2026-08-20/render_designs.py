"""Render the candidate designs as one comparison sheet.
Each panel: tile grid + engine (R_ENG) / extender (R_EXT) coverage halos + stats.
Expanded (Bigger Gravships) limits; 8 designs in a 2x4 grid."""
import numpy as np, json, math
from PIL import Image, ImageDraw, ImageFont
from ship_designs import COL, LABEL, R_ENG, R_EXT, CAP, N_EXT

NAMES=['1_spinal_freighter','2_nebulon_b','3_corellian_corvette',
       '4_catamaran_courtyard','5_ring_station','6_salvage_hulk','7_nodal_station',
       '8_ring_spur']
TITLES={'1_spinal_freighter':'1 · Spinal Freighter',
        '2_nebulon_b':'2 · Nebulon-B (fore hull · neck · aft hull)',
        '3_corellian_corvette':'3 · Corellian Corvette (hammerhead)',
        '4_catamaran_courtyard':'4 · Catamaran (twin hull + courts)',
        '5_ring_station':'5 · Ring Station (central hangar)',
        '6_salvage_hulk':'6 · Salvage Hulk (asymmetric wreck)',
        '7_nodal_station':'7 · Nodal Station (twin-nucleus spokes)',
        '8_ring_spur':'8 · Ring-and-Spur (ring + circular pods)'}
report=json.load(open('designs_report.json'))

def font(sz,bold=True):
    base="/usr/share/fonts/truetype/dejavu/DejaVuSans"
    for p in ([base+"-Bold.ttf"] if bold else [])+[base+".ttf"]:
        try:return ImageFont.truetype(p,sz)
        except:pass
    return ImageFont.load_default()
fTit=font(32); fPan=font(19); fStat=font(14,False); fLeg=font(16,False); fSub=font(14,False)

TS=6   # tile pixel size in panels
def render_panel(name):
    g=np.load(f'design_{name}.npy'); h,w=g.shape
    place=json.load(open(f'design_{name}_place.json'))
    W,H=w*TS,h*TS
    img=Image.new('RGBA',(W,H),(0,0,0,255))          # black panel background
    # coverage halos first (brighter so they read on black)
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); do=ImageDraw.Draw(ov)
    for typ,x,y,r in place:
        X,Y,R=x*TS+TS//2,y*TS+TS//2,r*TS
        fillc=(255,235,60,32) if typ=='ENGINE' else (60,200,255,24)
        do.ellipse([X-R,Y-R,X+R,Y+R],fill=fillc)
    img=Image.alpha_composite(img,ov)
    d=ImageDraw.Draw(img)
    for y in range(h):
        for x in range(w):
            c=g[y,x]
            if c=='':continue
            X,Y=x*TS,y*TS
            d.rectangle([X,Y,X+TS,Y+TS],fill=COL[c],outline=(110,110,118),width=1)
    for typ,x,y,r in place:
        X,Y=x*TS+TS//2,y*TS+TS//2
        if typ=='ENGINE':
            d.ellipse([X-6,Y-6,X+6,Y+6],fill=(255,235,60),outline=(0,0,0),width=2)
        else:
            d.ellipse([X-5,Y-5,X+5,Y+5],fill=(60,200,255),outline=(0,0,0),width=2)
    return img.convert('RGB')

panels=[render_panel(n) for n in NAMES]
pmax_w=max(p.width for p in panels); pmax_h=max(p.height for p in panels)

# layout: 8 panels in a 4-wide x 2-tall grid, stats caption under each; legend on top
pad=26; capH=110; titleH=60
cols=4; rows=2
cellW=pmax_w+pad; cellH=pmax_h+capH+34
legendH=176
Wt=cols*cellW+pad
Ht=titleH+legendH+rows*cellH+pad
canvas=Image.new('RGB',(Wt,Ht),(0,0,0))          # black sheet background
dc=ImageDraw.Draw(canvas)
dc.text((20,12),f"Gravship topologies — expanded (Bigger Gravships) limits  ·  all liftable: 100% substructure coverage, chain rule OK, <= {CAP} tiles",
        font=fTit,fill=(238,238,242))

# legend strip
lx,ly=20,titleH+6
dc.rectangle([lx,ly,Wt-20,ly+legendH-16],fill=(24,24,28),outline=(120,120,128),width=2)
order=[('M','Command / control'),('K','Keel / spine (backbone)'),('.','Corridor / cross-deck'),
 ('G','Cargo hold'),('F','Precision factory'),('E','Adv. materials (HOT)'),
 ('B','Bulk / dirty (HOT)'),('C','Food'),('D','Textile / ammo'),('A','Raw extraction'),
 ('R','Habitat'),('W','Water tanks'),('U','Fuel tanks'),('S','Thrusters + power'),
 ('T','Carbonite'),('H','Shuttle bay')]
perrow=5
for i,(c,nm) in enumerate(order):
    r,cc=divmod(i,perrow)
    xx=lx+16+cc*300; yy=ly+12+r*30
    dc.rectangle([xx,yy,xx+22,yy+20],fill=COL[c],outline=(150,150,158),width=1)
    dc.text((xx+30,yy+2),nm,font=fLeg,fill=(226,226,230))
# node glyph key at far right of legend
dc.ellipse([Wt-380,ly+12,Wt-364,ly+28],fill=(255,235,60),outline=(0,0,0),width=2)
dc.text((Wt-356,ly+12),f"Grav engine (r{R_ENG})",font=fLeg,fill=(226,226,230))
dc.ellipse([Wt-380,ly+42,Wt-366,ly+56],fill=(60,200,255),outline=(0,0,0),width=2)
dc.text((Wt-356,ly+42),f"Field extender (r{R_EXT}, <= {N_EXT})",font=fLeg,fill=(226,226,230))
dc.text((Wt-380,ly+74),"pale halo = connection",font=fSub,fill=(170,164,150))
dc.text((Wt-380,ly+92),"radius reach",font=fSub,fill=(170,164,150))

# panels grid
py0=titleH+legendH+4
for i,(name,p) in enumerate(zip(NAMES,panels)):
    r,cc=divmod(i,cols)
    cellx=pad+cc*cellW
    py=py0+r*cellH
    px=cellx+(pmax_w-p.width)//2
    dc.text((cellx,py),TITLES[name],font=fPan,fill=(236,236,240))
    canvas.paste(p,(px,py+28))
    dc.rectangle([px-1,py+27,px+p.width,py+28+p.height],outline=(110,110,118),width=1)
    rep=report[name]
    cy=py+32+pmax_h
    lines=[f"tiles {rep['tiles']} / {CAP}  (headroom {rep['headroom']})",
           f"extenders used {rep['n_ext_used']} / {N_EXT}  ·  engine r{R_ENG}, ext r{R_EXT}",
           f"coverage {rep['cover_pct']}%  ·  farthest {rep['max_dist']}",
           f"cargo {rep['zones'].get('G',0)} tiles",
           "LIFTABLE ✓" if rep['liftable'] else "NOT liftable"]
    for j,ln in enumerate(lines):
        col=(90,220,120) if ln.startswith("LIFTABLE") else (200,200,206)
        dc.text((cellx,cy+j*18),ln,font=fStat,fill=col)

canvas.save('ship_designs_comparison.png')
print("saved",canvas.size)
