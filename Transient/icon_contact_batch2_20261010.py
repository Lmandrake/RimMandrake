import json,glob,os,sys
from PIL import Image,ImageDraw
import numpy as np
A='/mnt/d/Luke/dev/_artpipe/_artsrc'
idx={}
for p in glob.glob('src/**/Textures/**/*.png',recursive=True):
    k=p.split('/Textures/',1)[1][:-4]; idx.setdefault(k,p)
def share(im):
    a=np.array(im.convert('RGBA')).astype(int); op=a[...,3]>128; p=np.pad(op,1)
    edge=op&~(p[:-2,1:-1]&p[2:,1:-1]&p[1:-1,:-2]&p[1:-1,2:])
    lum=0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]; n=edge.sum()
    return ((edge&(lum<45)).sum()/n if n else -1), op.mean()
def oldp(t):
    if not t: return None
    for k in (t,t+'_a',t+'_A',t+'_south',t+'_north',t+'_east'):
        if k in idx: return idx[k]
    base=os.path.basename(t)
    c=[k for k in idx if k.endswith('/'+base) or k.endswith('/'+base+'_a')]
    return idx[c[0]] if c else None
def sheet(jobs,out,newpath):
    S=160;W=2*S+250;rows=[];res=[]
    for j in jobs:
        np_=newpath(j)
        if not np_ or not os.path.exists(np_): continue
        new=Image.open(np_).convert('RGBA'); s,cov=share(new)
        op=oldp(j.get('target_texpath')); old=Image.open(op).convert('RGBA') if op else None
        res.append((j['id'],round(s,3),round(cov,2),op)); rows.append((j['id'],s,old,new))
    h=(len(rows)+1)//2
    sh=Image.new('RGBA',(W*2,S*h),(110,100,90,255));d=ImageDraw.Draw(sh)
    for i,(id_,s,old,new) in enumerate(rows):
        x=(i%2)*W;y=(i//2)*S
        if old: sh.alpha_composite(old.resize((S,S)),(x,y))
        else: d.text((x+10,y+70),'no old\ntexture',fill=(255,200,200,255))
        sh.alpha_composite(new.resize((S,S)),(x+S,y))
        d.text((x+2*S+5,y+10),f"{id_}\nnew edge-black {s:.2f}\n{'OUTLINED' if s>=.1 else 'ok'}",fill=(255,255,255,255))
    sh.convert('RGB').save(out); return res
b=json.load(open('Transient/icon_outline_jobs_batch2_20261010.json'))
r=sheet(b,'Transient/icon_renders_contact_batch2_20261010.png',lambda j:f"{A}/{j['id']}/{j['id']}.png")
for x in r:print(*x)
g=json.load(open('Transient/gap_art_jobs_20261010.json'))
def gp(j):
    for c in glob.glob(f"{A}/{j['id']}*/*.png"):
        if 'mask' not in c.lower(): return c
print('GAP')
for x in sheet(g,'Transient/gap_art_contact_20261010.png',gp):print(*x)
