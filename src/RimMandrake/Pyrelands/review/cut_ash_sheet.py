"""Cut a 2x2 ash sheet into trimmed, square, 256 px sprites with premultiplied resampling. cut_ash.py SHEET OUTDIR PREFIX KEEP(e.g. 0,1,3)"""
import sys,os
from PIL import Image
sheet,out,pre,keep=sys.argv[1],sys.argv[2],sys.argv[3],[int(k) for k in sys.argv[4].split(",")]
im=Image.open(sheet).convert("RGBA"); W,H=im.size; os.makedirs(out,exist_ok=True)
for q in keep:
    x0,y0=(q%2)*W//2,(q//2)*H//2
    t=im.crop((x0,y0,x0+W//2,y0+H//2))
    a=t.getchannel("A").point(lambda v:0 if v<24 else v)   # drop faint fringe
    t.putalpha(a); bb=a.getbbox(); t=t.crop(bb)
    side=int(max(t.size)*1.08); c=Image.new("RGBA",(side,side),(0,0,0,0)); c.paste(t,((side-t.size[0])//2,(side-t.size[1])//2))
    r=c.convert("RGBa").resize((256,256),Image.LANCZOS).convert("RGBA")
    al=r.getchannel("A").point(lambda v:0 if v<12 else v); r.putalpha(al)
    p=os.path.join(out,"%s%d.png"%(pre,q)); r.save(p); print(p,bb,side)
