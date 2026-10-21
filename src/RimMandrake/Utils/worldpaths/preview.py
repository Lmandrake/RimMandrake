"""Offline preview: dev-world faces + roads/rivers drawn with the engine's path geometry (no Perlin wiggle),
vanilla values (left) vs proposed (right). Screen transfer T() from design.py."""
import subprocess as _sp, os as _os
def _out():
    """Scratch under the machine's agent storage root (never ~/dev); fails by name if unset."""
    r=_sp.run(['python3',_os.path.expanduser('~/dev/Lodestar/bin/lib/agent_storage.py')],capture_output=True,text=True,check=True).stdout.strip()
    p=_os.path.join(r,'rimmandrake','scratch','riverroad'); _os.makedirs(p,exist_ok=True); return p
OUT=_out()
import sys,os,json,math,glob
import numpy as np
from PIL import Image,ImageDraw,ImageFont
REPO=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))))
sys.path.insert(0,REPO+'/src/RimMandrake/Utils'); sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
import worldview as WV, design as D
SAVE=sys.argv[1]; MODE=sys.argv[2]   # desert|coast
pv=WV.PlanetView(SAVE); g=pv.geom
X=json.load(open(OUT+'/crossings.json'))
dump=json.load(open(os.path.join(WV.DEFAULT_DUMP,'BiomeDef.json'))); tex={x['defName']:x['fields'].get('texture') for x in dump['defs']}
files={}
for p in glob.glob(REPO+'/src/*/*/Textures/**/*.png',recursive=True): files.setdefault(p.split('/Textures/',1)[1][:-4],p)
SEA_SCREEN={'RM_GreySea':(92,106,129),'RM_TwilightSea':(60,95,130),'RM_TheScald':(92,106,129),'Ocean':(60,80,120),'Lake':(60,80,120)}
# --- pick a centre
roads_at={};
for a,b,d,_ in pv.roads: roads_at.setdefault(a,[]).append(d); roads_at.setdefault(b,[]).append(d)
riv_at={}
for a,b,d,_ in pv.rivers: riv_at.setdefault(a,[]).append(d); riv_at.setdefault(b,[]).append(d)
def score(t,rad=0.25):
    v=g.vec[t]; near=np.where(g.vec@v>math.cos(rad))[0]
    if MODE=='desert':
        return sum(pv.biome[u] in ('RM_Stillsand','RM_LongShade') for u in near)*0.2+sum(len(roads_at.get(u,[])) for u in near)+5*sum('AncientAsphaltHighway' in roads_at.get(u,[]) for u in near)
    return sum(len(riv_at.get(u,[])) for u in near)*2+sum(len(roads_at.get(u,[])) for u in near)+30*min(sum(bool(pv.is_water[u]) for u in near),15)/15
cands=sorted(set(list(roads_at)+list(riv_at)))[::3]
if MODE=='desert': cands=[t for t in cands if pv.biome[t] in ('RM_Stillsand','RM_LongShade')]
else: cands=[t for t in cands if t in riv_at and any(pv.is_water[u] for u in g.neighbours(t))]
C=max(cands,key=score); lat,lon=g.latlon_of(g.vec[C])
print(MODE,'centre tile',C,pv.biome[C],round(lat,1),round(lon,1),file=sys.stderr)
SS=2; PW=900*SS; SPAN=float(os.environ.get('SPAN','0.30'))   # radians half-width
ax=g.vec[C]; north=np.array([0,1.0,0]); east=np.cross(north,ax); east/=np.linalg.norm(east); nn=np.cross(ax,east)
sc=PW/2/SPAN
def proj(v): return (PW/2+sc*(v@east), PW/2-sc*(v@nn))
vis=np.where(g.vec@ax>math.cos(SPAN*1.6))[0]
corners={t:g.corners(t) for t in vis}
def face_layer():
    im=Image.new('RGB',(PW,PW),(0,0,0)); 
    byb={}
    for t in vis: byb.setdefault(pv.biome[t],[]).append(t)
    tile_px=None
    for b,ts in byb.items():
        mask=Image.new('L',(PW,PW),0); dm=ImageDraw.Draw(mask)
        for t in ts: dm.polygon([proj(c) for c in corners[t]],fill=255)
        f=files.get(tex.get(b)) if tex.get(b) else None
        if b in SEA_SCREEN or pv.is_water[ts[0]] or not f:
            col=SEA_SCREEN.get(b,(92,106,129)); src=Image.new('RGB',(PW,PW),col)
        else:
            if tile_px is None:
                t0=ts[0]; c0=corners[t0]; tile_px=np.linalg.norm(np.subtract(proj(c0[0]),proj(c0[3])))
            S=int(tile_px*3.0); tx=Image.open(f).convert('RGB').resize((S,S))
            a=np.asarray(tx).astype(float)/255; a=(D.T(a)*255).astype(np.uint8); tx=Image.fromarray(a)
            src=Image.new('RGB',(PW,PW))
            for x in range(0,PW,S):
                for y in range(0,PW,S): src.paste(tx,(x,y))
        im.paste(src,(0,0),mask)
    # hard hex edges are what the game shows; no outline drawn
    return im
def nbi(t,u): return g.neighbours(t).index(u)
def endpoint(t,k):
    c=corners[t]; n=len(c); a=c[(k-1)%n]; b=c[k]
    m=(a+b)/2; return np.array(proj(m)), np.subtract(proj(b),proj(a))
def draw_paths(dr,t,nodes,col,pointy,smooth):
    """nodes=[(neighbour, width)] - the vanilla GeneratePaths shape, alpha>0.5 region."""
    ctr=np.array(proj(g.vec[t])); col=tuple(int(x) for x in col)
    def band(p,q,w):
        d=np.subtract(q,p); L=np.hypot(*d)
        if L<1e-6 or w<=0: return
        nrm=np.array([-d[1],d[0]])/L*w/2
        dr.polygon([tuple(p+nrm),tuple(q+nrm),tuple(q-nrm),tuple(p-nrm)],fill=col)
        r=w/2; dr.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=col)
    eps=[]
    for u,w in nodes:
        k=nbi(t,u); m,e=endpoint(t,k); eps.append((k,m,np.hypot(*e)*w))
    if len(nodes)==1 and pointy:
        k,m,w=eps[0]; d=ctr-m; L=np.hypot(*d); 
        if L>0:
            nrm=np.array([-d[1],d[0]])/L*w/2; dr.polygon([tuple(m+nrm),tuple(m-nrm),tuple(m+0.5*d)],fill=col)
        return
    n=len(corners[t])
    if len(nodes)==2 and smooth:
        i,j=eps[0][0],eps[1][0]
        if abs(i-j)>1 and ((i-j+n)%n)>1:
            band(eps[0][1],eps[1][1],min(eps[0][2],eps[1][2])); return
    mw=max(w for _,w in nodes)
    if mw>0:
        dr.polygon([tuple(ctr+(np.array(proj(c))-ctr)*0.5*mw) for c in corners[t]],fill=col)
    for k,m,w in eps:
        if w>0: band(m,ctr,w)
# FlowWorks River Colours, as RM_RiverColors.BuildTilePositions does it: per connected river network,
# t = (hi - elev)/(hi - lo); its biome anchors (AB_OcularForest, AB_FeraliskInfestedJungle, Wasteland) match no tile here.
par={}
def fnd(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for a,b,d,_ in pv.rivers:
    par.setdefault(a,a); par.setdefault(b,b); ra,rb=fnd(a),fnd(b)
    if ra!=rb: par[ra]=rb
nets={}
for t in list(par): nets.setdefault(fnd(t),[]).append(t)
river_t={}
for net in nets.values():
    e=[pv.elev[t] for t in net]; hi,lo=max(e),min(e); sp=(hi-lo) if hi-lo>0.01 else 1.0
    for t in net: river_t[t]=min(1,max(0,(hi-pv.elev[t])/sp))
def render(st):
    im=face_layer(); dr=ImageDraw.Draw(im)
    rv={}
    for a,b,d,_ in pv.rivers:
        if a in corners or b in corners:
            rv.setdefault(a,[]).append((b,d)); rv.setdefault(b,[]).append((a,d))
    for which in ('bank','core'):
        for t,L in rv.items():
            if t not in corners: continue
            water=D.gradient(river_t.get(t,0.5))
            v=water*st['bank_shade'] if (which=='bank' and st.get('bank_shade')) else water
            nodes=[(u,st['rivers'][d]-(0.2 if which=='core' else 0)) for u,d in L]
            draw_paths(dr,t,nodes,D.T(v)*255,True,True)
    rd={}
    for a,b,d,_ in pv.roads:
        rd.setdefault(a,[]).append((b,d)); rd.setdefault(b,[]).append((a,d))
    order=['Outline','Dirt','Stone','Gravel','Asphalt']
    grp={'DirtPath':'Dirt','DirtRoad':'Dirt','StoneRoad':'Stone','AncientAsphaltRoad':'Asphalt','AncientAsphaltHighway':'Asphalt'}
    for lay in order:
        colr=D.T(st['layers'][lay])*255
        for t,L in rd.items():
            if t not in corners or pv.is_water[t]: continue
            ws=[(u,dict(st['roads'][d]).get(lay,0.0)) for u,d in L]
            if not any(w>0 for _,w in ws): continue
            smooth=len(set(grp[d] for _,d in L))==1
            draw_paths(dr,t,ws,colr,False,smooth)
    return im.resize((PW//SS,PW//SS),Image.LANCZOS)
A=render(dict(D.VANILLA,bank_shade=None)); B=render(dict(D.NEW,bank_shade=D.BANK_SHADE))
W=PW//SS; canvas=Image.new('RGB',(2*W+12,W+150),(24,22,20)); canvas.paste(A,(0,60)); canvas.paste(B,(W+12,60))
dr=ImageDraw.Draw(canvas)
try: fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30); fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
except Exception: fnt=fs=ImageFont.load_default()
dr.text((16,14),'NOW (vanilla roads, FlowWorks river colours)',fill=(235,225,205),font=fnt); dr.text((W+28,14),'PROPOSED',fill=(235,225,205),font=fnt)
leg=[('dirt path/road',D.NEW['layers']['Dirt']),('stone road',D.NEW['layers']['Stone']),('ancient highway',D.NEW['layers']['Gravel']),('river',D.GRADIENT[1])]
x=W+28
for name,c in leg:
    cc=tuple(int(v) for v in D.T(c)*255); dr.rectangle((x,W+80,x+44,W+100),fill=cc,outline=(30,24,21),width=4); dr.text((x+54,W+76),name,fill=(235,225,205),font=fs); x+=54+int(dr.textlength(name,font=fs))+26
dr.text((16,W+76),'%s: tile %d (%s), %.0f°N %.0f°E. Day-side colour model; no Perlin wiggle.'%(MODE,C,pv.biome[C].replace('RM_',''),lat,lon),fill=(190,180,160),font=fs)
dr.text((16,W+112),'Offline approximation of the in-game world map; the live check decides.',fill=(150,140,125),font=fs)
p=OUT+'/preview_%s.png'%MODE; canvas.save(p); print(p)
