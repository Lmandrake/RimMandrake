import json,glob,os
from PIL import Image,ImageDraw
import numpy as np
A='/mnt/d/Luke/dev/_artpipe/_artsrc'
idx={}
for p in glob.glob('src/**/Textures/**/*.png',recursive=True):
    k=p.split('/Textures/',1)[1][:-4]; idx.setdefault(k,p)
def metr(im):
    a=np.array(im.convert('RGBA')).astype(int); op=a[...,3]>128; p=np.pad(op,1)
    edge=op&~(p[:-2,1:-1]&p[2:,1:-1]&p[1:-1,:-2]&p[1:-1,2:])
    # interior: pixels >=3 px inside
    q=op.copy()
    for _ in range(3):
        pp=np.pad(q,1); q=q&pp[:-2,1:-1]&pp[2:,1:-1]&pp[1:-1,:-2]&pp[1:-1,2:]
    lum=0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
    e=(edge&(lum<45)).sum()/max(edge.sum(),1); i=(q&(lum<45)).sum()/max(q.sum(),1)
    return e,i,op.mean()
def oldp(t):
    for k in (t,t+'_a',t+'_south',t+'_north',t+'_east'):
        if k in idx: return idx[k]
    base=os.path.basename(t)
    c=[k for k in idx if k.endswith('/'+base) or k.endswith('/'+base+'_a')]
    return idx[c[0]] if c else None
b=json.load(open('Transient/icon_outline_jobs_batch3_20261010.json'))
S=160;W=2*S+260;rows=[]
for j in b:
    f=f"{A}/{j['id']}/{j['id']}.png"
    new=Image.open(f).convert('RGBA'); e,i,cov=metr(new)
    op=oldp(j['target_texpath']); old=Image.open(op).convert('RGBA') if op else None
    verdict='OUTLINE?' if (e>=.1 and e-i>.25) else 'ok'
    print(j['id'],f"edge{e:.2f} int{i:.2f} cov{cov:.2f}",verdict,new.size,bool(old))
    rows.append((j['id'],e,i,verdict,old,new))
h=(len(rows)+1)//2
sh=Image.new('RGBA',(W*2,S*h),(110,100,90,255));d=ImageDraw.Draw(sh)
for n,(id_,e,i,v,old,new) in enumerate(rows):
    x=(n%2)*W;y=(n//2)*S
    if old: sh.alpha_composite(old.resize((S,S)),(x,y))
    else: d.text((x+10,y+70),'no old texture',fill=(255,200,200,255))
    sh.alpha_composite(new.resize((S,S)),(x+S,y))
    d.text((x+2*S+5,y+10),f"{id_}\nedge {e:.2f} int {i:.2f}\n{v}",fill=(255,255,255,255))
sh.convert('RGB').save('Transient/icon_renders_contact_batch3_20261010.png')
