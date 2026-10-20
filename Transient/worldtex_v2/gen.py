"""WORLDMAP_BIOME_APPEARANCE_1 step 1: one planet-scale world texture per biome on the dev world.
Seamless 512x512 opaque RGB colour fields, tuned to vanilla's measured register (mean RGB mid-tones,
luminance std 1.6-4.8 on the 13 vanilla World/Biomes textures): base colour + soft low-frequency
mottle toward a second colour + fine grain + an optional faint biome motif. Colours from the palette
brief (design/Jawa/worldbuilding/biomes/*.md 'Palette:' lines + ground terrain means), adjusted for
neighbour contrast. usage: python3 gen.py  -> tex/<defName>.png, stats.json, sheet.png"""
import numpy as np, json, os
from PIL import Image, ImageDraw, ImageFont
N=512; OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"tex")
def H(c): c=c.lstrip('#'); return np.array([int(c[i:i+2],16) for i in (0,2,4)],float)
def noise(scale,seed,aniso=(1,1)):
    r=np.random.default_rng(seed).standard_normal((N,N)); f=np.fft.fft2(r)
    fy=np.fft.fftfreq(N)[:,None]*N*aniso[1]; fx=np.fft.fftfreq(N)[None,:]*N*aniso[0]
    k=np.sqrt(fx**2+fy**2); filt=np.exp(-(k/scale)**2); filt[0,0]=0
    o=np.real(np.fft.ifft2(f*filt)); o=(o-o.mean())/(o.std()+1e-9); return o   # zero-mean, unit std
def fbm(scale,seed,aniso=(1,1)): return (0.65*noise(scale,seed,aniso)+0.3*noise(scale*2.5,seed+7,aniso)+0.05*noise(scale*7,seed+13,aniso))
# defName: (base, mottle, mottle_amount 0..1, motif, seed)
P={
 "RM_Stillsand":     ("#b8a174","#d2c6aa",0.35,"dunes",1),
 "RUT_Umbra":        ("#76818f","#7d9488",0.30,"aurora",2),
 "RM_LongShade":     ("#9a7650","#6e6c78",0.30,"none",3),
 "RM_TheRot":        ("#928aa0","#b9b0a8",0.35,"none",4),
 "RM_Wasteland":     ("#8b8780","#b4b0a4",0.30,"salt",5),
 "RM_NightsideIce":  ("#a8abae","#8a8f96",0.30,"none",6),
 "RM_Abyss":         ("#41465a","#5d7585",0.30,"none",7),
 "RM_BlueDesert":    ("#8fa6c2","#b5c4d6",0.30,"dunes",8),
 "RM_FloodedCanyon": ("#a68a78","#8e6652",0.35,"none",9),
 "RM_LeaningScrub":  ("#8b9476","#b09c62",0.30,"none",10),
 "RM_TwilightSea":   ("#3f6a68","#8a7a4a",0.20,"none",11),
 "RM_Cauldron":      ("#544652","#5e4a58",0.30,"none",12),
 "RM_GreySea":       ("#66746f","#9a9d94",0.25,"none",13),
 "RM_TheScald":      ("#5fa0a8","#c8d6d2",0.25,"none",14),
 "RM_RustCathedral": ("#7a5444","#a58257",0.30,"none",15),
 "RM_Greentide":     ("#587a3a","#7f9a52",0.30,"none",16),
 "RM_WeepingStones": ("#b9b5a8","#5e6a52",0.18,"none",17),
 "RM_Pyrelands":     ("#b08d4c","#5c5349",0.30,"bands",18),
 "RM_Contagion":     ("#8f4f45","#a97d70",0.30,"none",19),
 "RM_Webwork":       ("#4c6240","#c4c2b0",0.15,"none",20),
 "RM_GelatinousSlime":("#8fa860","#c58f6a",0.22,"none",21),
 "RM_Miasma":        ("#6b6840","#b9b293",0.20,"none",22),
 "RM_Warscar":       ("#5f5851","#8a5b44",0.30,"none",23),
 "RM_TheChill":      ("#3c4a5c","#a9b8c4",0.18,"none",24),
 "RM_TheForge":      ("#4d4846","#8a4a34",0.28,"none",25),
 "RM_FeverWood":     ("#5f5a35","#7a6030",0.35,"none",26),
 "RM_TheSump":       ("#474b47","#85795a",0.25,"none",27),
}
GRAIN=2.6   # fine-grain luminance std (8-bit), vanilla 1.6-4.8
def make(base,mott,amt,motif,seed):
    b=H(base); m=H(mott)
    low=fbm(5,seed*101)                       # 5 cycles per texture: soft patches
    w=np.clip(0.5+0.5*low/2.0,0,1)*amt*1.6    # 0..~amt*1.6, mean ~amt*0.8
    w=np.clip(w-amt*0.3,0,1)
    img=b[None,None,:]*(1-w[...,None])+m[None,None,:]*w[...,None]
    if motif=="dunes":   # faint long-wave streaks, very low amplitude
        img+= (noise(18,seed*7,aniso=(0.25,1.6))*2.2)[...,None]
    elif motif=="bands": # Pyrelands: migrating ash bands, soft
        band=np.clip(noise(4,seed*9,aniso=(0.5,1.5)),0,None); img=img*(1-0.06*band[...,None])+H("#3a3530")[None,None,:]*0.06*band[...,None]
    elif motif=="salt":
        s=np.clip(noise(30,seed*5)-1.6,0,None); img+= (s*10)[...,None]
    elif motif=="aurora":
        a=np.clip(noise(3,seed*3),0,None); img=img+(H("#6f5f8a")-b)[None,None,:]*0.08*a[...,None]
    img+= (noise(120,seed*11)*GRAIN)[...,None]
    return np.clip(img,0,255).astype(np.uint8)
if __name__=="__main__":
    os.makedirs(OUT,exist_ok=True); stats={}
    for dn,(b,m,a,mo,s) in P.items():
        arr=make(b,m,a,mo,s); Image.fromarray(arr,"RGB").save(os.path.join(OUT,dn+".png"),optimize=True)
        L=0.299*arr[...,0]+0.587*arr[...,1]+0.114*arr[...,2]
        stats[dn]={"mean":[round(float(x)) for x in arr.reshape(-1,3).mean(0)],"Lstd":round(float(L.std()),2)}
    json.dump(stats,open(os.path.join(os.path.dirname(OUT),"stats.json"),"w"),indent=1)
    # sheet: each texture tiled 2x2 at 128px + its mean as a flat swatch
    keys=list(P); cols=7; cw,ch=200,236; sh=Image.new("RGB",(cols*cw,((len(keys)+cols-1)//cols)*ch),(24,24,28)); d=ImageDraw.Draw(sh)
    for i,k in enumerate(keys):
        t=Image.open(os.path.join(OUT,k+".png")).resize((96,96)); x,y=(i%cols)*cw+4,(i//cols)*ch+4
        for ox in (0,96):
            for oy in (0,96): sh.paste(t,(x+ox,y+18+oy))
        d.text((x,y),k[3:] if k.startswith("RM_") else k,fill=(230,230,230))
    sh.save(os.path.join(os.path.dirname(OUT),"sheet.png")); print(json.dumps(stats))
