"""Road/river world-map style: vanilla vs proposed, and contrast against every face each tier crosses.
Screen model (fitted 2026-10-20 on worldlook3 H/J shots, day side, within ~5%): screen = 1-(1-c)^2.5 per channel,
for both WorldTerrain faces and Custom/Roads paths. Custom/Roads is alpha-blended but draws hard-edged (alpha cut ~0.5)."""
import subprocess as _sp, os as _os
def _out():
    """Scratch under the machine's agent storage root (never ~/dev); fails by name if unset."""
    r=_sp.run(['python3',_os.path.expanduser('~/dev/Lodestar/bin/lib/agent_storage.py')],capture_output=True,text=True,check=True).stdout.strip()
    p=_os.path.join(r,'rimmandrake','scratch','riverroad'); _os.makedirs(p,exist_ok=True); return p
OUT=_out()
import json,sys,math
import numpy as np
P=2.5
def T(c): c=np.clip(np.asarray(c,float),0,1); return 1-(1-c)**P
def lin(s): s=np.asarray(s,float); return np.where(s<=0.04045,s/12.92,((s+0.055)/1.055)**2.4)
def Y(s): return float(lin(s)@[0.2126,0.7152,0.0722])
def wcag(a,b): ya,yb=sorted((Y(a),Y(b))); return (yb+0.05)/(ya+0.05)
def lab(s):
    l=lin(s); M=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]]); x=M@l/np.array([0.95047,1,1.08883])
    f=np.where(x>0.008856,np.cbrt(x),7.787*x+16/116); return np.array([116*f[1]-16,500*(f[0]-f[1]),200*(f[1]-f[2])])
def dE(a,b): return float(np.linalg.norm(lab(a)-lab(b)))
def hue(s): L=lab(s); return math.degrees(math.atan2(L[2],L[1]))%360
VANILLA={'layers':{'Outline':(0.1,0.1,0.1),'Dirt':(0.5,0.4,0.3),'Stone':(0.4,0.4,0.4),'Gravel':(0.5,0.5,0.5),'Asphalt':(0.3,0.3,0.3)},
 'roads':{'DirtPath':[('Outline',0.35),('Dirt',0.2)],'DirtRoad':[('Outline',0.55),('Dirt',0.4)],'StoneRoad':[('Outline',0.55),('Stone',0.4)],
          'AncientAsphaltRoad':[('Outline',0.65),('Gravel',0.5),('Asphalt',0.25)],'AncientAsphaltHighway':[('Outline',0.95),('Gravel',0.8),('Asphalt',0.55)]},
 'river_core':(73/255,82/255,100/255),'river_bank':(73/255,82/255,100/255),
 'rivers':{'Creek':0.2,'River':0.4,'LargeRiver':0.6,'HugeRiver':0.8}}
NEW={'layers':{'Outline':(0.05,0.04,0.035),'Dirt':(0.30,0.16,0.07),'Stone':(0.18,0.15,0.12),'Gravel':(0.80,0.50,0.00),'Asphalt':(0.10,0.07,0.05)},
 'roads':{'DirtPath':[('Outline',0.46),('Dirt',0.26)],'DirtRoad':[('Outline',0.62),('Dirt',0.42)],'StoneRoad':[('Outline',0.64),('Stone',0.44)],
          'AncientAsphaltRoad':[('Outline',0.78),('Gravel',0.58),('Asphalt',0.10)],'AncientAsphaltHighway':[('Outline',1.0),('Gravel',0.80),('Asphalt',0.14)]},
 'river_core':(0.08,0.16,0.30),'river_bank':(0.08*0.22,0.16*0.22,0.30*0.22),
 'rivers':{'Creek':0.32,'River':0.46,'LargeRiver':0.62,'HugeRiver':0.82}}
# What the live game draws today (2026-10-20 deploy): slate stone road, gradient rivers. The 'before' of preview.py.
NOW_LIVE=dict(NEW,layers=dict(NEW['layers'],Stone=(0.15,0.25,0.25)))
def tier_colours(st,kind,d):
    if kind=='river': return T(st['river_core']),T(st['river_bank'])
    steps=st['roads'][d]; fill=[s for s in steps if s[0]!='Outline']
    return T(st['layers'][fill[0][0]]),T(st['layers']['Outline'])   # outermost fill = what you see, outline = casing
def evaluate(st,cross,faces,seas):
    rows=[]
    for kind in ('road','river'):
        for d,biomes in cross[kind].items():
            core,case=tier_colours(st,kind,d); worst=None
            for b,n in biomes.items():
                f=faces.get(b,{})
                cols=[T(np.array(f[k])/255) for k in ('p10','mean','p90')] if f.get('mean') else ([T(np.array(seas[b])/255)] if b in seas else [])
                for F in cols:
                    c1=max(wcag(core,F),wcag(case,F)); e=dE(core,F); sc=min(c1/3.0,e/20.0)
                    r=(sc,b,round(wcag(core,F),2),round(wcag(case,F),2),round(e,1),n)
                    if b not in seas and (worst is None or r<worst): worst=r
            rows.append({'kind':kind,'def':d,'core':[int(x*255) for x in core],'casing':[int(x*255) for x in case],'core_vs_casing':round(wcag(core,case),2),
                         'worst_biome':worst[1],'worst_core_wcag':worst[2],'worst_casing_wcag':worst[3],'worst_core_dE':worst[4],'pass':bool(worst[0]>=1.0)})
    return rows
# FlowWorks River Colours. BEFORE (owner 2026-09-06 gradient by elevation, darkened 2026-10-20 by card): kept to draw
# the "before" side. NOW (RIVER_WATER_BY_BIOME, 2026-10-20, owner: "the river is shown brown and red. Odd colors"):
# blue-grey water, tinted only inside the biomes whose sheet says the water is not clean (RM_RiverColorsSettings).
GRADIENT=[(0xE0/255,0x31/255,0x1C/255),(0x2E/255,0x2E/255,0x00/255),(0x00/255,0x29/255,0x3D/255)]
WATER=(0.08,0.16,0.30)
BIOME_WATER={'RM_Contagion':(0.36,0.03,0.04),'RM_Miasma':(0.16,0.14,0.04),'RM_Wasteland':(0.14,0.24,0.06),'RM_RustCathedral':(0.04,0.20,0.16)}
BANK_SHADE=0.22
def gradient(t):
    a,b,c=[np.array(x) for x in GRADIENT]
    return a+(b-a)*(t/0.5) if t<=0.5 else b+(c-b)*((t-0.5)/0.5)
def water_for(biome): return np.array(BIOME_WATER.get(biome,WATER))
def eval_water(cross,faces):
    """Each water colour against every face of the biomes it is drawn in (a tint only in its own biome)."""
    crossed=set(); [crossed.update(v) for v in cross['river'].values()]
    rows=[]
    for name,col,bs in [('water',WATER,[b for b in crossed if b not in BIOME_WATER])]+[(b,c,[b]) for b,c in BIOME_WATER.items()]:
        core=T(col); case=T(np.array(col)*BANK_SHADE); worst=None
        for b in bs:
            f=faces.get(b,{})
            if not f.get('mean'): continue
            for k in ('p10','mean','p90'):
                F=T(np.array(f[k])/255); sc=min(max(wcag(core,F),wcag(case,F))/3.0,dE(core,F)/20.0)
                r=(sc,b,round(wcag(core,F),2),round(wcag(case,F),2),round(dE(core,F),1))
                if worst is None or r<worst: worst=r
        rows.append({'water':name,'core':[int(x*255) for x in core],'bank':[int(x*255) for x in case],'worst_biome':worst[1],'worst_core_wcag':worst[2],'worst_bank_wcag':worst[3],'worst_core_dE':worst[4],'pass':bool(worst[0]>=1.0)})
    return rows
if __name__=='__main__':
    X=json.load(open(OUT+'/crossings.json'))
    seas={'RM_GreySea':(60,68,82),'RM_TwilightSea':(40,60,85),'RM_TheScald':(60,68,82)}  # texture-space guess for sea faces (no face file); not gated
    out={}
    for name,st in (('vanilla',VANILLA),('proposed',NEW)):
        rows=evaluate(st,X['cross'],X['faces'],seas); out[name]=rows
        print(name)
        for r in rows: print('  %-6s %-22s core%-15s case%-15s c/c %.1f worst %-17s coreW %.2f caseW %.2f dE %5.1f %s'%(r['kind'],r['def'],r['core'],r['casing'],r['core_vs_casing'],r['worst_biome'],r['worst_core_wcag'],r['worst_casing_wcag'],r['worst_core_dE'],'PASS' if r['pass'] else 'FAIL'))
    # tier distinctness (proposed)
    cores={(k,d):tier_colours(NEW,k,d)[0] for k in ('road','river') for d in X['cross'][k]}
    fills={'Dirt':T(NEW['layers']['Dirt']),'Stone':T(NEW['layers']['Stone']),'Gravel':T(NEW['layers']['Gravel']),'River':T(NEW['river_core']),**{b:T(c) for b,c in BIOME_WATER.items()}}
    ks=list(fills); out['tier_dE']={a+'/'+b:round(dE(fills[a],fills[b]),1) for i,a in enumerate(ks) for b in ks[i+1:]}
    print('tier dE',out['tier_dE'])
    out['water_by_biome']=eval_water(X['cross'],X['faces']); print('water by biome')
    for r in out['water_by_biome']: print('   %-17s core%s bank%s worst %s coreW %.2f bankW %.2f dE %.1f %s'%(r['water'],r['core'],r['bank'],r['worst_biome'],r['worst_core_wcag'],r['worst_bank_wcag'],r['worst_core_dE'],'PASS' if r['pass'] else 'FAIL'))
    json.dump(out,open(OUT+'/contrast.json','w'),indent=1)
