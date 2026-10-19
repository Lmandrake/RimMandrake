"""Before/after sheet: each flattened picture, before (git HEAD) vs after (src), at planet zoom
(texture tiled 3x3 then box-downscaled 1536->144 px, roughly how it reads zoomed out on the
world map) and at close zoom (a 1:1 160 px crop). usage: sheet.py <out.png>"""
import io,json,subprocess,sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
P=[r for r in json.load(open("Transient/worldtex_flatten/plan.json")) if r["action"]=="flatten"]
seen=set(); rows=[]
for r in P:
    k=tuple(r["mean"])+(round(r["std"],1),)
    if k in seen: continue
    seen.add(k); rows.append(r)
def before(p): return Image.open(io.BytesIO(subprocess.run(["git","show","HEAD:"+p],capture_output=True).stdout)).convert("RGB")
def far(im): t=Image.new("RGB",(im.width*3,im.height*3)); [t.paste(im,(x*im.width,y*im.height)) for x in range(3) for y in range(3)]; return t.resize((144,144),Image.BOX)
def near(im): return im.crop((0,0,160,160))
W=40+260+2*(144+160+24); H=60+len(rows)*170
sh=Image.new("RGB",(W,H),(34,30,26)); d=ImageDraw.Draw(sh)
try: F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",14)
except Exception: F=ImageFont.load_default()
d.text((20,15),"BEFORE: planet zoom | close        AFTER: planet zoom | close      (luminance std full-res -> after)",fill=(230,220,200),font=F)
for i,r in enumerate(sorted(rows,key=lambda r:-r["std"])):
    y=50+i*170; b=before(r["src"]); a=Image.open(r["src"]).convert("RGB")
    name=r["src"].split("/")[-1][:-4].split("_",1)[1]
    d.text((20,y+40),name,fill=(240,230,210),font=F); d.text((20,y+62),f'std {r["std"]} -> {r["std_after"]}',fill=(200,190,170),font=F)
    d.text((20,y+84),"32px "+f'{r["std32"]} -> {r["std32_after"]}',fill=(200,190,170),font=F); d.text((20,y+106),"mean "+str(r["mean"]),fill=(200,190,170),font=F)
    x=300
    for im in (far(b),near(b),far(a),near(a)):
        sh.paste(im,(x,y)); x+=im.width+(24 if im.width==160 else 8)
sh.save(sys.argv[1]); print(sys.argv[1],sh.size,len(rows),"pictures")
