"""Render ONE design as a large standalone sheet with big, readable text
(fonts ~3x the comparison grid, larger tiles). Usage: python3 render_single.py <name>
Defaults to 9_derelict_halo."""
import sys, numpy as np, json, math
from PIL import Image, ImageDraw, ImageFont
from ship_designs import COL, R_ENG, R_EXT, CAP, N_EXT

name = sys.argv[1] if len(sys.argv)>1 else '9_derelict_halo'
TITLES={'9_derelict_halo':'9 · Derelict Halo — pods on curved tethers, dangling perimeter walks, a shrine at the dead centre',
 '10_spinal_reliquary':'10 · Spinal Reliquary — one straight keel, wings hung on catwalks, grav-shrine amidships',
 '11_ladder_halo':'11 · Ladder Halo — twin rails, hollow void between, pods hung outboard, shrine in the void',
 '12_cross_nave':'12 · Cross-Nave Cathedral — cruciform hull, shrine at the crossing, pods off all four arms',
 '13_broken_keel_halo':'13 · Broken Keel Halo — keel snapped in three, dog-leg catwalk bridges, shrine in the middle'}
title = TITLES.get(name, name)

def font(sz,bold=True):
    base="/usr/share/fonts/truetype/dejavu/DejaVuSans"
    for p in ([base+"-Bold.ttf"] if bold else [])+[base+".ttf"]:
        try:return ImageFont.truetype(p,sz)
        except:pass
    return ImageFont.load_default()
# ~3x the comparison-grid sizes (which were 32/19/14/16)
fTit=font(46); fStat=font(38,False); fLeg=font(36,False); fSub=font(32,False)

TS=16   # tile pixel size (was 6 in the grid)
g=np.load(f'design_{name}.npy'); h,w=g.shape
place=json.load(open(f'design_{name}_place.json'))
report=json.load(open('designs_report.json'))[name]
W,H=w*TS,h*TS
panel=Image.new('RGBA',(W,H),(0,0,0,255))
# coverage halos
ov=Image.new('RGBA',(W,H),(0,0,0,0)); do=ImageDraw.Draw(ov)
for typ,x,y,r in place:
    X,Y,R=x*TS+TS//2,y*TS+TS//2,r*TS
    fillc=(255,235,60,30) if typ=='ENGINE' else (60,200,255,22)
    do.ellipse([X-R,Y-R,X+R,Y+R],fill=fillc)
panel=Image.alpha_composite(panel,ov)
d=ImageDraw.Draw(panel)
for y in range(h):
    for x in range(w):
        c=g[y,x]
        if c=='':continue
        X,Y=x*TS,y*TS
        d.rectangle([X,Y,X+TS,Y+TS],fill=COL[c],outline=(90,90,98),width=1)
for typ,x,y,r in place:
    X,Y=x*TS+TS//2,y*TS+TS//2
    if typ=='ENGINE':
        d.ellipse([X-14,Y-14,X+14,Y+14],fill=(255,235,60),outline=(0,0,0),width=3)
    else:
        d.ellipse([X-11,Y-11,X+11,Y+11],fill=(60,200,255),outline=(0,0,0),width=3)
panel=panel.convert('RGB')

# ---- compose sheet: title on top, panel centred, legend + stats on the right
pad=40; titleH=100; legendW=680
sheetW=pad+W+40+legendW+pad
# ensure the (long) title fits the sheet width
tmp=ImageDraw.Draw(Image.new('RGB',(10,10)))
titleW=tmp.textlength(title,font=fTit)
sheetW=max(sheetW,int(titleW)+2*pad)
sheetH=titleH+H+pad
sheet=Image.new('RGB',(sheetW,sheetH),(0,0,0))
dc=ImageDraw.Draw(sheet)
dc.text((pad,28),title,font=fTit,fill=(238,238,242))
sheet.paste(panel,(pad,titleH))
dc.rectangle([pad-1,titleH-1,pad+W,titleH+H],outline=(110,110,118),width=2)

# legend + stats column
lx=pad+W+40; ly=titleH
order=[('M','Command / control'),('K','Keel / spine'),('.','Corridor / causeway'),
 ('G','Cargo hold'),('F','Precision factory'),('E','Adv. materials (HOT)'),
 ('B','Bulk / dirty (HOT)'),('C','Food'),('D','Textile / ammo'),('A','Raw extraction'),
 ('R','Habitat'),('W','Water tanks'),('U','Fuel tanks'),('S','Thrusters + power'),
 ('T','Carbonite / scrap shrine'),('H','Shuttle bay')]
yy=ly
for c,nm in order:
    dc.rectangle([lx,yy,lx+40,yy+34],fill=COL[c],outline=(150,150,158),width=1)
    dc.text((lx+54,yy+2),nm,font=fLeg,fill=(226,226,230))
    yy+=46
yy+=24
dc.ellipse([lx,yy,lx+34,yy+34],fill=(255,235,60),outline=(0,0,0),width=3)
dc.text((lx+54,yy),f"Grav engine (r{R_ENG})",font=fLeg,fill=(226,226,230)); yy+=52
dc.ellipse([lx,yy,lx+34,yy+34],fill=(60,200,255),outline=(0,0,0),width=3)
dc.text((lx+54,yy),f"Field extender (r{R_EXT})",font=fLeg,fill=(226,226,230)); yy+=52
dc.text((lx,yy),"pale halo = connection reach",font=fSub,fill=(170,164,150)); yy+=64

rep=report
stats=[f"tiles {rep['tiles']} / {CAP}  (headroom {rep['headroom']})",
       f"extenders {rep['n_ext_used']} / {N_EXT}",
       f"engine r{R_ENG} · ext r{R_EXT}",
       f"coverage {rep['cover_pct']}%  ·  farthest {rep['max_dist']}",
       f"cargo {rep['zones'].get('G',0)} tiles",
       "LIFTABLE  ✓" if rep['liftable'] else "NOT liftable"]
for ln in stats:
    col=(90,220,120) if ln.startswith("LIFTABLE") else (200,200,206)
    dc.text((lx,yy),ln,font=fStat,fill=col); yy+=50

out=f'design_{name}_large.png'
sheet.save(out); print("saved",out,sheet.size)
