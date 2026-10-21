"""Tree shade estimate for design/RimMandrake/tree_shade_model_2026-10-19.md section 2.2.

An ESTIMATE of two shade models, not a measurement of any map. Reads the live def dump
(capture 2026-10-19T11:23:54Z) for each BiomeDef plantDensity and wildPlants (after patches)
and each plant visualSizeRange. Places plants at random on a 200x200 grid (no fertility, rock
or water), keeps casters (visualSizeRange.max >= 1.5), and rasterises:
  strip  - today RM_MapComponent_ShadeGrid: height = vmax*0.5, one-cell strip down-sun,
           length height*cot(E) capped at 16, caster cell unshaded
  crown  - the proposed projected crown: disc radius 0.4*drawn size (growth uniform 0.3-1),
           offset down-sun by 0.5*drawn size*cot(E), capped at 16, full shade
E is the median sun elevation from each biome sheet. Seeded; runs ~15 min (pure Python loops).
"""
import json,sqlite3,math,random
import numpy as np
import sys; sys.path.insert(0,"/home/mandrake/rm/foundry/src/RimMandrake/Utils"); import game_paths
D=game_paths.DUMP_ROOT.rstrip("/\\")+"/"
bd={b['defName']:b for b in json.load(open(D+"captures/2026-10-19T11-23-54Z/defs/BiomeDef.json"))['defs']}
c=sqlite3.connect(D+"defs.sqlite")
def vs(n):
    r=c.execute("select json from defs where def_name=? and def_type like '%ThingDef'",(n,)).fetchone()
    p=json.loads(r[0])['fields'].get('plant') or {}; v=p.get('visualSizeRange') or {}
    return v.get('min',0),v.get('max',0)
# E: sun elevation from the biome sheets (median); None = nightside/terminator
BIO={'RM_Greentide':45,'RUT_Greentide':45,'RM_FeverWood':43,'RUT_FeverWood':43,'RM_Webwork':51,'RUT_Webwork':51,
     'RM_Miasma':39,'RUT_Miasma':39,'RM_Contagion':31,'RUT_Contagion':31,'RM_TheForge':57,'RM_FloodedCanyon':21,
     'RM_WeepingStones':31,'RM_Wasteland':3,'RM_LongShade':14,'RM_Stillsand':47}
N=200; rng=np.random.default_rng(1)
def sim(name,E,model):
    b=bd[name]['fields']; pd=min(1,b['plantDensity']); wp=b['wildPlants']; tot=sum(w['commonality'] for w in wp)
    cot=1/math.tan(math.radians(max(E,0.5)))
    shade=np.zeros((N,N)); trees=0
    for x in range(N):
        for z in range(N):
            if rng.random()>pd: continue
            r=rng.random()*tot; acc=0
            for w in wp:
                acc+=w['commonality']
                if r<=acc: pn=w['plant']; break
            lo,hi=VS.setdefault(pn,vs(pn))
            if hi<1.5: continue
            g=rng.uniform(0.3,1.0); s=lo+(hi-lo)*g   # drawn size at a random growth
            trees+=1
            if model=='strip':   # today's code: height=vmax*0.5, strip down-sun, own cell unshaded
                L=min(16,hi*0.5*cot)
                for k in range(1,int(math.ceil(L*2))+1):
                    t=k*0.5; xx=round(x+t*0.0); zz=round(z-t)  # sun from north: shadow to south
                    if (xx,zz)==(x,z): continue
                    if 0<=zz<N: shade[xx,zz]=max(shade[xx,zz], 1 if t<L-1 else 0.6)
            else:                # crown: disk radius 0.4*s, centred crownH*cot down-sun, full shade
                rad=0.4*s; off=min(16,0.5*s*cot)  # crown base at ~half the drawn size
                cz=z-off
                for xx in range(int(x-rad)-1,int(x+rad)+2):
                    for zz in range(int(cz-rad)-1,int(cz+rad)+2):
                        if 0<=xx<N and 0<=zz<N and (xx-x)**2+(zz-cz)**2<=rad*rad: shade[xx,zz]=1
    return trees/(N*N), (shade>=0.99).mean(), shade.mean()
VS={}
for n,E in BIO.items():
    t,s1,m1=sim(n,E,'strip'); _,s2,m2=sim(n,E,'crown')
    print(f"{n:18s} E={E:>3} casterCells={t:.3f}  today-strip: fullShade={s1:.2f} meanShade={m1:.2f}   crown: covered={s2:.2f}")
