import json,glob,os
from PIL import Image,ImageDraw
import numpy as np
A='/mnt/d/Luke/dev/_artpipe/_artsrc'
jobs=json.load(open('Transient/icon_outline_jobs_20261010.json'))
def share(im):
    a=np.array(im.convert('RGBA')).astype(int)
    op=a[...,3]>128
    p=np.pad(op,1)
    edge=op&~(p[:-2,1:-1]&p[2:,1:-1]&p[1:-1,:-2]&p[1:-1,2:])
    lum=0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
    n=edge.sum()
    return (edge&(lum<45)).sum()/n if n else -1, op.mean()
def oldpath(t):
    c=glob.glob(f'src/**/Textures/**/{t}.png',recursive=True)+glob.glob(f'src/**/Textures/**/{t}_[aA].png',recursive=True)
    c=[x for x in c if '/Item' in x]
    return c[0] if c else None
rows=[];res=[]
for j in jobs:
    new=Image.open(f"{A}/{j['id']}/{j['id']}.png").convert('RGBA')
    s,cov=share(new)
    op=oldpath(j['target_def']); old=Image.open(op).convert('RGBA') if op else None
    res.append((j['id'],round(s,3),round(cov,2),op))
    rows.append((j['id'],s,old,new))
S=160;W=2*S+250
sheet=Image.new('RGBA',(W*2,S*12+0),(110,100,90,255));d=ImageDraw.Draw(sheet)
for i,(id_,s,old,new) in enumerate(rows):
    x=(i%2)*W;y=(i//2)*S
    if old: sheet.alpha_composite(old.resize((S,S)),(x,y))
    sheet.alpha_composite(new.resize((S,S)),(x+S,y))
    d.text((x+2*S+5,y+10),f"{id_}\nnew edge-black {s:.2f}\n{'OUTLINED' if s>=.1 else 'ok'}",fill=(255,255,255,255))
sheet.convert('RGB').save('Transient/icon_renders_contact_20261010.png')
json.dump(res,open('/tmp/x.json','w'))
for r in res:print(r[:3])
