# Offline composites for the river-works / hose art review. Water is SYNTHETIC (no vanilla water texture offline).
import numpy as np, os
from PIL import Image, ImageDraw
R='/home/mandrake/rm/bench/src/RimMandrake/FlowWorks/Textures/'
O='/home/mandrake/rm/bench/Transient/river_hose_art_review_2026-10-16/'
C=64
rng=np.random.default_rng(3)
def ground(w,h):
    a=np.zeros((h,w,3),np.uint8); a[:]=(112,88,66); a=a+rng.integers(-8,8,(h,w,1)); 
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA')
def water_band(img,x0,x1):
    d=ImageDraw.Draw(img); h=img.height
    for x in range(x0,x1):
        t=abs((x-(x0+x1)/2)/((x1-x0)/2)); c=(int(60-20*(1-t)),int(95-25*(1-t)),int(120-25*(1-t)))
        d.line([(x,0),(x,h)],fill=c+(255,))
    for _ in range(90):
        y=rng.integers(0,h); x=rng.integers(x0+6,x1-6); d.line([(x,y),(x,y+rng.integers(8,26))],fill=(150,185,200,120),width=1)
def paste(base,tex,cx,cy,sz,rot=0):
    t=Image.open(tex).convert('RGBA'); t=t.resize((int(sz*C),int(sz*C)),Image.LANCZOS)
    if rot: t=t.rotate(rot,expand=True)
    base.alpha_composite(t,(int(cx-t.width/2),int(cy-t.height/2)))
def up(img,k): return img.resize((img.width*k,img.height*k),Image.NEAREST)
def lab(img,text):
    out=Image.new('RGBA',(img.width,img.height+18),(20,20,20,255)); out.paste(img,(0,18)); ImageDraw.Draw(out).text((4,3),text,fill=(255,255,255,255)); return out
RV=R+'Things/Building/FlowWorks/Rivers/'
# 1 weir scene at true scale, 6x5 cells, river 2.5 cells wide running N-S, weir spanning from east bank in (rot 90 so it runs E-W)
W,H=8*C,5*C
s=ground(W,H); water_band(s,int(2.5*C),int(5.5*C))
paste(s,RV+'RM_BankWeir.png',int(4.9*C),int(2.5*C),2.2,90)   # 1x2 footprint, bank end east
paste(s,RV+'RM_BankStake.png',int(6.5*C),int(1.5*C),0.6); paste(s,RV+'RM_BankStake.png',int(6.5*C),int(2.5*C),0.6); paste(s,RV+'RM_BankStake.png',int(6.5*C),int(3.5*C),0.6)
paste(s,RV+'RM_SiltTrap.png',int(7*C),int(0.8*C),1.2)
s1=lab(s,'OFFLINE composite, true 64px/cell: weir (rot 90, drawSize 2.2) + stake line + silt trap on synthetic water')
tex=lambda n: Image.open(RV+n).convert('RGBA')
def pane(n,k=2,bg=(112,88,66)):
    t=tex(n); b=Image.new('RGBA',t.size,bg+(255,)); b.alpha_composite(t); return up(b.resize((t.width//2,t.height//2),Image.LANCZOS),k) if t.width>256 else up(b,k//2 if k>1 else 1)
tiles=[]
for n in ['RM_BankWeir','RM_BankStake','RM_SiltTrap','RM_FerryPost','RM_FerryRope','RM_SluiceBox','RM_PanningSpot']:
    t=tex(n+'.png'); b=Image.new('RGBA',t.size,(112,88,66,255)); b.alpha_composite(t)
    sc=384/max(t.size); b=b.resize((int(t.width*sc),int(t.height*sc)),Image.LANCZOS); tiles.append(lab(b,n+' raw %dx%d'%t.size))
wd=sum(t.width for t in tiles[:4])+30; sheet=Image.new('RGBA',(max(wd,sum(t.width for t in tiles[4:])+20),2*(384+18)+10),(20,20,20,255))
x=0
for t in tiles[:4]: sheet.paste(t,(x,0)); x+=t.width+10
x=0
for t in tiles[4:]: sheet.paste(t,(x,402)); x+=t.width+10
sheet.convert('RGB').save(O+'river_works_textures_zoom.png')
# ford: terrain def uses vanilla Flagstone tinted (128,124,112); also the unused RM_FordStones.png
fs=Image.open(R+'Terrain/Surfaces/RM_FordStones.png').convert('RGBA')
fw=ground(6*C,4*C); water_band(fw,int(1.5*C),int(4.5*C))
tile=fs.resize((C*2,C*2),Image.LANCZOS)
for cx in range(2,5):
    fw.alpha_composite(fs.crop((0,0,512,512)).resize((C,C),Image.LANCZOS),(cx*C-C//2+C//2,int(1.5*C)))
lab(fw,'OFFLINE: RM_FordStones.png tile (top-left 512) across synthetic water -- NOTE def uses vanilla Flagstone, not this file').convert('RGB').save(O+'ford_composite.png')
fs.convert('RGBA').resize((512,512)).save(O+'ford_png_512.png')
lab(s,'x').convert('RGB')  # noqa
s1.convert('RGB').save(O+'weir_scene_true_scale.png')
up(s.crop((int(2*C),int(1*C),int(7.5*C),int(4*C))),3).convert('RGB').save(O+'weir_scene_3x.png')
print('ok')
