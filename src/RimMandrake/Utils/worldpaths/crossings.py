"""Which biomes do road/river links touch on the dev save, and each face's colour stats."""
import subprocess as _sp, os as _os
def _out():
    """Scratch under the machine's agent storage root (never ~/dev); fails by name if unset."""
    r=_sp.run(['python3',_os.path.expanduser('~/dev/Lodestar/bin/lib/agent_storage.py')],capture_output=True,text=True,check=True).stdout.strip()
    p=_os.path.join(r,'rimmandrake','scratch','riverroad'); _os.makedirs(p,exist_ok=True); return p
OUT=_out()
import sys,os,json,glob
from collections import Counter,defaultdict
REPO=_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))))
sys.path.insert(0,REPO+'/src/RimMandrake/Utils')
import numpy as np
from PIL import Image
import worldview as WV
save=sys.argv[1]
pv=WV.PlanetView(save)
print('unresolved',pv.unresolved,pv.roads_unresolved,pv.rivers_unresolved,file=sys.stderr)
cross={'road':defaultdict(Counter),'river':defaultdict(Counter)}
for kind,links in (('road',pv.roads),('river',pv.rivers)):
    for a,b,d,_ in links:
        for t in (a,b): cross[kind][d][pv.biome[t]]+=1
# biome -> texture
dump=json.load(open(os.path.join(WV.DEFAULT_DUMP,'BiomeDef.json')))
tex={x['defName']:x['fields'].get('texture') for x in dump['defs']}
files={}
for p in glob.glob(REPO+'/src/*/*/Textures/**/*.png',recursive=True):
    rel=p.split('/Textures/',1)[1][:-4]; files.setdefault(rel,p)
def lum(rgb):
    c=rgb/255.0; c=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4); return c@np.array([0.2126,0.7152,0.0722])
stats={}
biomes=set(); [biomes.update(c) for k in cross.values() for c in k.values()]
for b in sorted(biomes):
    t=tex.get(b); p=files.get(t) if t else None
    if not p: stats[b]={'texture':t,'file':None}; continue
    a=np.asarray(Image.open(p).convert('RGB').resize((128,128))).reshape(-1,3).astype(float)
    L=lum(a)
    stats[b]={'texture':t,'file':p.replace(REPO+'/',''),'mean':a.mean(0).round().tolist(),
      'p10':a[L<=np.percentile(L,10)].mean(0).round().tolist(),'p90':a[L>=np.percentile(L,90)].mean(0).round().tolist(),
      'L10':float(np.percentile(L,10)),'L50':float(np.percentile(L,50)),'L90':float(np.percentile(L,90))}
out={'save':save,'cross':{k:{d:dict(c) for d,c in v.items()} for k,v in cross.items()},'faces':stats,
     'n_roads':len(pv.roads),'n_rivers':len(pv.rivers)}
json.dump(out,open(OUT+'/crossings.json','w'),indent=1)
print('roads',len(pv.roads),'rivers',len(pv.rivers),'biomes',len(biomes),'nofile',[b for b in stats if not stats[b].get('file')])
for k,v in cross.items():
    for d,c in v.items(): print(k,d,sum(c.values()),c.most_common(6))
