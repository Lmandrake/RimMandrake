#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""localmap.py - a close-up hex map of ONE PLACE on Ash'karr.

worldview.py draws the whole planet; at 20 deg of arc a tile is 11 px and you cannot see a
coastline. This projects the tiles around a point (azimuthal equidistant, north up) and draws
one disc per tile, so an island, a strait or a peninsula is legible.

    STEM=world/ASHKARR_VIVIFIED_2026-08-24 python3 src/RimMandrake/Utils/localmap.py \\
        <lat> <lon> <radius_deg> <out.png> 'lat,lon,LABEL;lat,lon,LABEL'

STEM defaults to the vivified bundle. Reads only the _tiles.csv.
"""
import csv, math, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
STEM=__import__('os').environ.get('STEM','world/ASHKARR_VIVIFIED_2026-08-24')
rows=list(csv.DictReader(open(STEM+'_tiles.csv')))
N=len(rows)
biome=np.array([r['biome'] for r in rows]); lat=np.array([float(r['lat']) for r in rows])
lon=np.array([float(r['lon']) for r in rows]); region=np.array([r['region'] for r in rows])
rp=np.deg2rad(lat); rl=np.deg2rad(lon)
V=np.stack([np.cos(rp)*np.cos(rl),np.cos(rp)*np.sin(rl),np.sin(rp)],1)
COL={'Ocean':(24,52,104),'Lake':(40,110,190),'SeaIce':(226,238,248),
     'AB_RockyCrags':(78,84,100),'AB_MycoticJungle':(168,64,196),'AridShrubland':(196,178,110),
     'Desert':(214,190,132),'ExtremeDesert':(238,226,186),'ZBiome_Badlands':(176,96,60),
     'PoisonForest':(96,132,52),'BMT_FungalForest':(120,80,170),'Wasteland':(140,140,140),
     'HorrorWastes':(140,26,54),'BMT_CrystalCaverns':(150,206,238)}
CENTRE=(float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv)>2 else (8.77,-110.31)
RAD=float(sys.argv[3]) if len(sys.argv)>3 else 22.0     # degrees of arc shown
OUT=sys.argv[4] if len(sys.argv)>4 else 'world/view/local_twilight_crags.png'
LABELS=sys.argv[5] if len(sys.argv)>5 else ''
c=np.array([math.cos(math.radians(CENTRE[0]))*math.cos(math.radians(CENTRE[1])),
            math.cos(math.radians(CENTRE[0]))*math.sin(math.radians(CENTRE[1])),
            math.sin(math.radians(CENTRE[0]))])
north=np.array([0,0,1.0]); east=np.cross(north,c); east/=np.linalg.norm(east); up=np.cross(c,east)
ang=np.degrees(np.arccos(np.clip(V@c,-1,1)))
sel=np.where(ang<=RAD)[0]
S=1400; img=Image.new('RGB',(S,S+70),(12,12,16)); dr=ImageDraw.Draw(img)
def px(i):
    x=float(V[i]@east); y=float(V[i]@up); a=math.radians(ang[i])
    n=math.hypot(x,y) or 1e-9
    r=(a/math.radians(RAD))*(S/2-20)
    return (S/2+r*x/n, S/2-r*y/n)
rad=max(3,int((S/2-20)*(2.5756/2.0)/RAD))
for i in sel:
    xx,yy=px(i); col=COL.get(biome[i],(90,90,90))
    dr.ellipse([xx-rad,yy-rad,xx+rad,yy+rad], fill=col, outline=(0,0,0), width=1)
try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
except Exception: font=ImageFont.load_default()
seen=set()
for i in sel:
    r=region[i]
    if r and r not in seen and ang[i]<RAD*0.85:
        seen.add(r); xx,yy=px(i)
        dr.text((xx,yy), r, fill=(255,255,255), font=font, anchor="mm",
                stroke_width=3, stroke_fill=(0,0,0))
for spec in [s for s in LABELS.split(';') if s]:
    la,lo,txt = spec.split(',',2)
    i=int(np.argmin((lat-float(la))**2+(lon-float(lo))**2)); xx,yy=px(i)
    dr.ellipse([xx-rad*2,yy-rad*2,xx+rad*2,yy+rad*2], outline=(255,80,80), width=4)
    dr.text((xx,yy-rad*3), txt, fill=(255,140,140), font=font, anchor="mm", stroke_width=3, stroke_fill=(0,0,0))
dr.text((16,S+10), "centre lat %.2f lon %.2f  |  %.0f deg radius  |  %d tiles  |  north is up"
        % (CENTRE[0],CENTRE[1],RAD,len(sel)), fill=(220,220,220), font=font)
img.save(OUT); print("wrote", OUT, img.size)
