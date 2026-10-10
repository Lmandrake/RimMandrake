import json,glob,hashlib,sys,io,os,subprocess
from pathlib import Path
sys.path.insert(0,"src/RimMandrake/Utils/art")
import artledger as L
from PIL import Image
import numpy as np
A="/mnt/d/Luke/dev/_artpipe/"
GAME="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/"
d=json.load(open("Transient/biome_ffar/therot_sheet_2026-10-05.decisions.json"))["decisions"]
S=json.load(open("infrastructure/state/art/sheets/therot_sheet_2026-10-05.snapshot.json"))["rows"]
ruled=sorted(r for r,v in d.items() if v.get("at"))
ev=L.read_events()
locs={}
for e in ev:
  if e.get("sha") and e.get("loc"): locs.setdefault(e["sha"],[]).append(e["loc"])
idx=L.Index()
live_shas={e["sha"] for e in idx.live.values()}
retired_prev={e["prev"] for e in ev if e.get("type")=="live" and e.get("sha") is None and e.get("prev")}
allpurged=set(idx.purged)
_img={}
def img_of(sha):
  if sha in _img: return _img[sha]
  im=None
  p=L.store_path(sha)
  srcs=[str(p)] if p.is_file() else []
  for loc in locs.get(sha,[]):
    if loc.startswith("git:"): srcs.append(loc)
    else: srcs.append(A+loc)
  for s_ in srcs:
    try:
      if s_.startswith("git:"):
        _,rev,path=s_.split(":",2); b=subprocess.run(["git","show",f"{rev}:{path}"],capture_output=True).stdout
      else: b=open(s_,"rb").read()
      im=Image.open(io.BytesIO(b)).convert("RGBA"); break
    except Exception: continue
  _img[sha]=im; return im
def diff(a,b):
  x=np.asarray(a,dtype=np.int16); y=np.asarray(b.resize(a.size,Image.LANCZOS),dtype=np.int16)
  return float(np.abs(x-y).mean())
def files_for(res, roots):
  out=[]
  for root in roots:
    for base in glob.glob(root):
      p=os.path.join(base,res)
      if os.path.isdir(p): out+= [f for f in glob.glob(p+"/**/*.png",recursive=True)]
      else: out+= glob.glob(p+"_*.png")+glob.glob(p+".png")
  return [f for f in out if not f.endswith("m.png") or f.endswith("_m.png")==False and not f[:-4].endswith(("southm","eastm","northm","westm"))]
SRCROOTS=["src/*/*/Textures"]
GAMEROOTS=[GAME+"RimMandrake.Biomes/Biomes/*/Textures",GAME+"UtinniPatches/Textures",GAME+"SWBestiary/Textures",GAME+"*/Textures"]
EXTRA={"AA_Agaripod":"Things/Pawn/Animal/RM_Agaripod"}
rows=[];summary={"PASS":0,"FAIL":0}
for r in ruled:
  v=d[r]; snap=S[r]; fails=[];notes=[]
  res=[snap["res"]]+([EXTRA[r]] if r in EXTRA else [])
  sf=sorted(set(sum((files_for(x,SRCROOTS) for x in res),[])))
  gf=sorted(set(sum((files_for(x,GAMEROOTS) for x in res),[])))
  sim={f:Image.open(f).convert("RGBA") for f in sf}
  gim={}
  for f in gf:
    try: gim[f]=Image.open(f).convert("RGBA")
    except Exception: pass
  # ✕'d pictures absent
  for sha in v.get("purge",[]):
    im=img_of(sha)
    if im is None: notes.append(f"✕{sha[:8]} no pixels to compare"); continue
    for f,fi in list(sim.items())+list(gim.items()):
      if diff(fi,im)<2: fails.append(f"✕ {sha[:8]} live as {f.split('/Textures/')[-1]}")
  # pick live
  letter=v.get("decision")
  col=snap["columns"].get(letter) if letter else None
  colsh=[x for x in (col or {}).values()] if col else []
  if colsh and not any(s in v.get("purge",[]) for s in colsh):
    for sha in colsh:
      im=img_of(sha)
      if im is None: notes.append(f"pick {letter} {sha[:8]} no pixels"); continue
      ins=[f for f,fi in sim.items() if diff(fi,im)<2]; ing=[f for f,fi in gim.items() if diff(fi,im)<2]
      donor="IN GAME" in snap["labels"].get(letter,"") and not sf
      if not ing: (notes if donor else fails).append(f"pick {letter} {sha[:8]} not in game copy")
      if sf and not ins: notes.append(f"pick {letter} {sha[:8]} not in src folder (texPath may be redirected)")
  # duplicates in src
  ks=list(sim)
  for i in range(len(ks)):
    for j in range(i+1,len(ks)):
      if diff(sim[ks[i]],sim[ks[j]])<2: fails.append(f"dup {Path(ks[i]).name}={Path(ks[j]).name}")
  # unshown pictures
  colimgs=[img_of(s) for c in snap["columns"].values() for s in c.values()]
  colimgs=[c for c in colimgs if c is not None]
  unshown=[Path(f).name for f,fi in sim.items() if not any(diff(fi,c)<2 for c in colimgs)]
  if unshown:
    (fails if r in ("RM_Pusmelon","RM_Sagecrust") else notes).append("unshown: "+",".join(unshown))
  # jobs
  for st in ("pending","active","done"):
    for jp in glob.glob(A+st+"/*.json"):
      if jp.endswith(".manifest.json"): continue
      try: j=json.load(open(jp))
      except Exception: continue
      if j.get("target_def")!=r: continue
      for ref in j.get("canon_reference") or []:
        rs=Path(ref).stem
        if len(rs)==64 and (rs in allpurged or (rs in retired_prev and rs not in live_shas)):
          fails.append(f"job {j['id']} ({st}) refs {'purged' if rs in allpurged else 'retired'} {rs[:8]}")
  if r=="RM_ThozzikSpawned":
    hits=subprocess.run(["grep","-rl","RM_ThozzikSpawned","src/RimMandrake/TheRot/Defs"],capture_output=True,text=True).stdout.strip()
    if hits: fails.append("ThozzikSpawned still defined")
    notes.append("deleted (owner card)")
  st="FAIL" if fails else "PASS"; summary[st]+=1
  rows.append((r,st,fails,notes))
for r,st,f,n in rows: print(f"{st} {r} | {'; '.join(f)} | {'; '.join(n)}")
print(summary)
