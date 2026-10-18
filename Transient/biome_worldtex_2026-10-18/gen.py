"""Placeholder world-map biome textures, procedural, seamless, 512x512 opaque RGB.
Usage: python3 gen.py <outdir>   -> writes <outdir>/<key>.png and palette.json"""
import numpy as np, json, sys, os
from PIL import Image, ImageDraw
N=512
def H(c): c=c.lstrip('#'); return np.array([int(c[i:i+2],16) for i in (0,2,4)],float)
def rng(s): return np.random.default_rng(s)
def tnoise(scale,seed,beta=2.0):
    r=rng(seed).standard_normal((N,N)); f=np.fft.fft2(r)
    fy=np.fft.fftfreq(N)[:,None]*N; fx=np.fft.fftfreq(N)[None,:]*N
    k=np.sqrt(fx**2+fy**2); k[0,0]=1
    filt=1/(1+(k/scale)**beta)/np.maximum(k,1)**0.0
    filt[0,0]=0
    o=np.real(np.fft.ifft2(f*filt)); o=(o-o.min())/(o.max()-o.min()); return o
def fbm(scale,seed): 
    return 0.6*tnoise(scale,seed)+0.3*tnoise(scale*3,seed+1)+0.1*tnoise(scale*9,seed+2)
yy,xx=np.mgrid[0:N,0:N].astype(float)
def voro(n,seed):
    p=rng(seed).random((n,2))*N
    best=np.full((N,N),1e9); second=best.copy(); idx=np.zeros((N,N),int)
    for i,(px,py) in enumerate(p):
        for ox in (-N,0,N):
            for oy in (-N,0,N):
                d=np.hypot(xx-(px+ox),yy-(py+oy))
                m=d<best; second=np.where(m,best,np.minimum(second,d)); idx=np.where(m,i,idx); best=np.where(m,d,best)
    return best,second,idx
def stamp(fn,count,seed,**kw):
    """draw shapes on a wrapped canvas; fn(draw,x,y,rng,i)"""
    im=Image.new('L',(N,N),0); d=ImageDraw.Draw(im); r=rng(seed)
    for i in range(count):
        x,y=r.random()*N,r.random()*N
        for ox in (-N,0,N):
            for oy in (-N,0,N): fn(d,x+ox,y+oy,r,i)
    return np.array(im)/255.0
def blur(m,s):
    f=np.fft.fft2(m); fy=np.fft.fftfreq(N)[:,None]; fx=np.fft.fftfreq(N)[None,:]
    return np.real(np.fft.ifft2(f*np.exp(-2*(np.pi*s)**2*(fx**2+fy**2))))
def clamp(a): return np.clip(a,0,1)
# ---- pattern masks (0..1) ----
def p_rocks(seed,count=70):  # rocks with long shadow to one side
    def f(d,x,y,r,i):
        s=r.random()*7+3; d.polygon([(x,y),(x+s*4,y+s*1.2),(x+s*4+s,y+s*1.4),(x+s,y+s*.2)],fill=140)
        d.ellipse([x-s,y-s,x+s,y+s],fill=255)
    return clamp(blur(stamp(f,count,seed),0.6))
def p_speckle(seed,count=900,size=1.4):
    def f(d,x,y,r,i): s=size*(0.5+r.random()); d.ellipse([x-s,y-s,x+s,y+s],fill=int(120+135*r.random()))
    return stamp(f,count,seed)
def p_bands(seed,freq=14,warp=0):
    w=(tnoise(60,seed)-.5)*warp
    return .5+.5*np.sin((yy/N*freq+w)*2*np.pi)
def p_dunes(seed,freq=9):
    w=(tnoise(70,seed)-.5)*0.9
    return .5+.5*np.sin(((xx*0.6+yy*0.8)/N*freq+w)*2*np.pi)
def p_corrug(seed,freq=40):
    w=(tnoise(40,seed)-.5)*0.25
    return (.5+.5*np.sin((yy/N*freq+w)*2*np.pi))**2
def p_shards(seed,count=14):
    def f(d,x,y,r,i):
        a=r.random()*np.pi; L=60+r.random()*140; d.line([(x,y),(x+L*np.cos(a),y+L*np.sin(a))],fill=255,width=int(1+r.random()*2))
    return clamp(blur(stamp(f,count,seed),0.4)*1.6)
def p_scabs(seed,count=260):
    def f(d,x,y,r,i): s=2+r.random()*6; d.ellipse([x-s,y-s*.8,x+s,y+s*.8],fill=255)
    return clamp(blur(stamp(f,count,seed),0.8)*1.5)
def p_craters(seed,count=38):
    def f(d,x,y,r,i):
        s=6+r.random()*22; d.ellipse([x-s,y-s,x+s,y+s],fill=255); d.ellipse([x-s*.72,y-s*.72,x+s*.72,y+s*.72],fill=0)
    return clamp(blur(stamp(f,count,seed),0.7))
def p_veins(seed,scale=45,w=0.035):
    n=tnoise(scale,seed,4.0); return clamp(1-np.abs(n-0.5)/w)**1.0
def p_bubbles(seed,count=110):
    def f(d,x,y,r,i): s=3+r.random()*11; d.ellipse([x-s,y-s,x+s,y+s],outline=255,width=2)
    return clamp(blur(stamp(f,count,seed),0.5))
def p_rings(seed,count=14):
    def f(d,x,y,r,i):
        s=30+r.random()*45
        for k in range(4): q=s*(1-k*.22); d.ellipse([x-q,y-q,x+q,y+q],outline=255-k*40,width=3)
    return clamp(blur(stamp(f,count,seed),0.8))
def p_streaks(seed,vertical=False,count=190,diag=0.0):
    def f(d,x,y,r,i):
        L=40+r.random()*160; w=int(1+r.random()*2.5)
        d.line([(x,y),(x+diag*L,y+L)],fill=int(110+145*r.random()),width=w)
    m=stamp(f,count,seed); return clamp(blur(m,0.5)*1.3)
def p_ripple(seed,freq=22):
    a=tnoise(50,seed); b=tnoise(30,seed+5)
    return clamp((.5+.5*np.sin((tnoise(40,seed,4.0)*8+ (xx+yy)/N*3)*2*np.pi))**6*1.5)
def p_grid(seed,cell=64):
    r=rng(seed); m=np.zeros((N,N)); k=N//cell
    for gy in range(k):
        for gx in range(k):
            x0,y0=gx*cell,gy*cell
            if r.random()<.5: m[y0:y0+3,x0:x0+cell]=1
            if r.random()<.5: m[y0:y0+cell,x0:x0+3]=1
            if r.random()<.3: m[y0+cell//3:y0+cell//3+3,x0:x0+cell//2]=1
            if r.random()<.25: m[y0+8:y0+14,x0+8:x0+14]=1
    return m
def p_membrane(seed,scale=28,t=0.5,edge=0.03):
    n=tnoise(scale,seed,4.0); return clamp(1-np.abs(n-t)/edge)
def p_blobs(seed,scale=28,t=0.55,soft=0.05):
    n=tnoise(scale,seed,4.0); return clamp((n-t)/soft+.5)
def p_polys(seed,n=36,w=2.5):
    b,s,_=voro(n,seed); return clamp(1-(s-b)/w)
def p_cells(seed,n=48): 
    return voro(n,seed)
def p_hex(seed,cell=46):
    h=cell*0.866; m=np.zeros((N,N)); k=int(N/cell)
    cx=(xx/ (cell*1.0)); cy=(yy/h)
    row=np.floor(cy); off=(row%2)*0.5
    fx=(cx+off)%1; fy=cy%1
    e=np.minimum(np.minimum(fx,1-fx)*cell, np.minimum(fy,1-fy)*h)
    return clamp(1-e/2.5)
def p_eyes(seed,count=40):
    def f(d,x,y,r,i):
        s=5+r.random()*8; d.ellipse([x-s,y-s*.7,x+s,y+s*.7],fill=255); d.ellipse([x-s*.45,y-s*.45,x+s*.45,y+s*.45],fill=70)
    return clamp(blur(stamp(f,count,seed),0.6))
def p_hatch(seed,angle=None,count=2600):
    def f(d,x,y,r,i):
        a=(angle if angle is not None else r.random()*np.pi); L=5+r.random()*5
        d.line([(x,y),(x+L*np.cos(a),y+L*np.sin(a))],fill=int(100+155*r.random()),width=1)
    return clamp(blur(stamp(f,count,seed),0.4)*1.5)
def p_dots(seed,step=20):
    m=np.zeros((N,N)); 
    for j in range(N//step):
        for i in range(N//step):
            x=i*step+(step//2 if j%2 else 0)+step//2; y=j*step+step//2
            m[(yy-y)**2+(xx-x)**2<9]=1
    return clamp(blur(m,0.6)*1.3)
def p_crystals(seed,count=120):
    def f(d,x,y,r,i):
        s=2+r.random()*6; d.polygon([(x,y-s*2),(x+s,y),(x,y+s*2),(x-s,y)],fill=int(150+105*r.random()))
    return clamp(blur(stamp(f,count,seed),0.5))
def p_leaves(seed,count=520):
    def f(d,x,y,r,i):
        a=r.random()*np.pi*2; L=8+r.random()*14; w=3+r.random()*3
        cx,cy=x+np.cos(a)*L/2,y+np.sin(a)*L/2; d.ellipse([cx-L/2,cy-w/2,cx+L/2,cy+w/2],fill=int(110+145*r.random()))
    return clamp(blur(stamp(f,count,seed),0.5)*1.3)
def p_puddles(seed): return p_blobs(seed,22,0.6,0.02)
def p_folds(seed):
    w=(tnoise(60,seed,4.0)-.5)*5
    return clamp(1-np.abs(np.sin((xx/N*7+w)*np.pi))*3)
def p_glass(seed,n=60):
    b,s,idx=voro(n,seed); return b,s,idx

# key: (dark, mid, accent, pattern-name, pattern-callable, strength)
S={
 'LongShade':   ('#c9a878','#ecd2a4','#3a2c20','rocks+long shadows',   lambda s:p_rocks(s),0.85),
 'Greentide':   ('#0b4a2c','#1f8a4a','#7be08a','leaf litter',          lambda s:p_leaves(s),0.7),
 'Umbra':       ('#05070f','#0d1730','#6dffd0','aurora snow specks',   lambda s:p_speckle(s,1400,1.2),0.9),
 'MineralWater':('#2e4a40','#58806c','#a8c8a0','sediment bands',       lambda s:p_bands(s,10,1.1),0.55),
 'Chill':       ('#1a3a5a','#2a5a82','#d8f4ff','frozen shard lines',   lambda s:p_shards(s,18),0.95),
 'Cauldron':    ('#14160f','#2a3320','#9aa59a','weeping metal scabs',  lambda s:p_scabs(s),0.75),
 'Warscar':     ('#3a332e','#6b5a4c','#ff7a28','crater rings, slag glints',lambda s:p_craters(s),0.8),
 'Webwork':     ('#1d0f2b','#3a2057','#5cff7a','tangled web veins',    lambda s:p_veins(s,38,0.06),0.9),
 'TheRot':      ('#9c86ad','#c9b6d6','#f4f0e6','pale fungal bubbles',  lambda s:p_bubbles(s),0.8),
 'FeverWood':   ('#2a3a1a','#4d5e2c','#8a6a2e','trunk cross-section rings',lambda s:p_rings(s),0.6),
 'SleepingIce': ('#9aa5b0','#d6dde2','#6f7f8d','dirty glacier streaks',lambda s:p_streaks(s,False,160,0.3),0.6),
 'Scald':       ('#0c5a66','#16a0a6','#f2ffff','boiling ripples + foam',lambda s:p_ripple(s),0.85),
 'RustCathedral':('#5a1c0c','#a8461c','#ffb060','circuit-board maze',  lambda s:p_grid(s),0.75),
 'BlueDesert':  ('#a9d4ee','#d4ecfa','#ffffff','wind-scoured ice dunes',lambda s:p_dunes(s),0.6),
 'Slime':       ('#6e9a10','#a9d020','#e8ff70','living-cell membrane', lambda s:p_membrane(s,20,0.5,0.04),0.8),
 'CrackedLands':('#7a3320','#b5583a','#2e140c','clay-pan polygons',    lambda s:p_polys(s,34,3),0.85),
 'TwilightSea': ('#10124a','#2a3aa0','#35e0c0','stained-glass waveglass',None,1),
 'Forge':       ('#120a08','#2c1a14','#ff5a10','molten seam veins',    lambda s:p_veins(s,30,0.06),0.95),
 'Sump':        ('#1a1710','#2e2a18','#050505','black tar puddles',    lambda s:p_puddles(s),0.9),
 'Wasteland':   ('#9a9078','#c8c0a6','#6d6a5e','salt-crust mottling',  lambda s:p_scabs(s,420),0.55),
 'Abyss':       ('#1a0830','#3c1a66','#d04aff','twisted obsidian folds',lambda s:p_folds(s),0.7),
 'GreySea':     ('#5c6a6c','#8c9a9a','#e8efef','salt hex pillars',     lambda s:p_hex(s),0.8),
 'Stillsand':   ('#c8a038','#eacb62','#8a6a14','corrugated ochre ridges',lambda s:p_corrug(s),0.6),
 'Contagion':   ('#4a0a10','#8a1420','#f0e0a0','half-formed eyes',     lambda s:p_eyes(s),0.8),
 'LeaningScrub':('#6a7a6a','#a9bba5','#e6efe4','wind-leaning fuzz',    lambda s:p_hatch(s,0.9,3200),0.6),
 'WeepingStones':('#b8b4a8','#e0ddd2','#16130f','black weeping streaks',lambda s:p_streaks(s,True,150,0.0),0.85),
 'Miasma':      ('#5a5a14','#8d8a24','#d4c34a','stilt-root dots in haze',lambda s:p_dots(s,22),0.7),
 'ChillCrater': ('#02020a','#0a0a18','#5a6a8a','refrozen black glass cracks',lambda s:p_polys(s,70,1.6),0.8),
 'Pyrelands':   ('#4a4218','#8a7c34','#1c1a04','dry grass tufts',     lambda s:p_hatch(s,None,2600),0.55),
 'LanternDeeps':('#06122a','#0e2a5a','#40b0ff','lanternstone crystals',lambda s:p_crystals(s),0.95),
 'SeabedScald': ('#3a0e0a','#7a2a12','#ffb03a','vent bubbles',         lambda s:p_bubbles(s,70),0.7),
 'SeabedGrey':  ('#b88a92','#dcb4b8','#7a4a58','brine-pool membrane',  lambda s:p_membrane(s,24,0.5,0.05),0.6),
 'SeabedTwilight':('#3a1a30','#5a2a48','#ffd34a','glow dots',          lambda s:p_dots(s,34),0.9),
 'SeabedChill': ('#0e3a38','#1a6a5a','#c8fff0','cold garden fronds',   lambda s:p_leaves(s,300),0.55),
 'SeabedBedrock':('#3a3a3e','#5a5a60','#1a1a1c','solid bedrock rubble',lambda s:p_craters(s,70),0.5),
 'SeabedFloor': ('#5a5a46','#8a8a6c','#c8c8a0','seafloor sand ripples',lambda s:p_dunes(s,20),0.5),
}
def render(key,seed):
    dk,md,ac,_,fn,k=S[key]; dk,md,ac=H(dk),H(md),H(ac)
    n=fbm(30,seed)
    base=dk+(md-dk)*n[...,None]
    if key=='TwilightSea':
        b,s,idx=voro(60,seed); pal=[H('#10124a'),H('#2a3aa0'),H('#1f9a9a'),H('#35e0c0'),H('#5a2aa0')]
        col=np.array(pal)[idx%len(pal)]
        edge=clamp(1-(s-b)/2.5)[...,None]
        return clamp((col*(0.7+0.4*n[...,None])*(1-edge*.7)+H('#c8fff0')*edge*.4)/255)
    m=fn(seed)
    m=clamp(m)[...,None]*k
    out=base*(1-m)+ac*m
    out*=(0.94+0.12*tnoise(12,seed+9))[...,None]
    return clamp(out/255)
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True); pal={}
    for i,key in enumerate(S):
        a=render(key,100+i*7); im=Image.fromarray((a*255).astype(np.uint8),'RGB')
        im.save(f'{out}/{key}.png'); pal[key]=[round(float(x)) for x in (a.reshape(-1,3).mean(0)*255)]
    json.dump(pal,open(f'{out}/palette.json','w'),indent=1)
    ks=list(pal); P=np.array([pal[k] for k in ks]); mn=[]
    for i in range(len(ks)):
        d=np.linalg.norm(P-P[i],axis=1); d[i]=1e9; j=d.argmin(); mn.append((round(d[j]),ks[i],ks[j]))
    print(sorted(mn)[:8])
