"""Flatten the placeholder biome world textures toward a colour field, keeping each mean.
WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES. out = mean + (px - mean) * (TARGET / std_L) per
file whose luminance std > THRESH; shrinking toward the mean never clips, so the mean colour
is kept exactly (up to uint8 rounding). A fine seamless grain (per-pixel, zero-mean, std GRAIN)
replaces the removed structure: it averages out at planet zoom (no relief) and keeps the field a
texture, not a flat rectangle (the art ledger refuses geometric placeholders, owner 2026-10-07). Reference: the pre-placeholder near-flat RM textures
(FeverWood 0.0, TheRot 0.0, Pyrelands 2.8). usage: flatten.py <stage_dir>"""
import json,os,sys,numpy as np
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,'src/RimMandrake/Utils/art'); import measure
THRESH,TARGET,GRAIN=6.0,3.0,4.0
stage=sys.argv[1]; os.makedirs(stage,exist_ok=True); plan=[]
fl=measure.files()
fl["src/RimMandrake/CrackedLands/Textures/World/Biomes/RM_CrackedLands.png"]=fl.pop("src/RimMandrake/FloodedCanyon/Textures/World/Biomes/RM_CrackedLands.png")
for p,dns in fl.items():
    s,ss,m=measure.stats(p)
    if s<=THRESH: plan.append(dict(src=p,defs=dns,std=s,std32=ss,mean=m,action="keep")); continue
    a=np.asarray(Image.open(p).convert("RGB"),float); mu=a.reshape(-1,3).mean(0)
    o=mu+(a-mu)*(TARGET/s)
    r=np.random.default_rng(sum(map(ord,os.path.basename(p))))      # deterministic per file
    g=r.standard_normal(a.shape[:2]+(1,))+0.35*r.standard_normal(a.shape)  # mostly luminance grain
    g=(g-g.mean())/g.mean(-1).std()*GRAIN
    o=o+g; o=o-o.reshape(-1,3).mean(0)+mu; im=Image.fromarray(np.clip(np.rint(o),0,255).astype(np.uint8),"RGB")
    mod=p.split("/Textures/")[0][4:]; out=os.path.join(stage,mod.replace("/","__")+"__"+os.path.basename(p)); im.save(out)
    s2,ss2,m2=measure.stats(out)
    import placeholder_detect as PD; ph=PD.placeholder_reason(out)
    plan.append(dict(src=p,defs=dns,mod=mod,rel="World/Biomes/"+os.path.basename(p),stage=out,std=s,std32=ss,mean=m,std_after=s2,std32_after=ss2,mean_after=m2,placeholder=ph,action="flatten"))
json.dump(plan,open(os.path.join(stage,"..","plan.json"),"w"),indent=1)
for r in sorted(plan,key=lambda r:-r["std"]):
    print(f'{os.path.basename(r["src"]):24s} {r["action"]:7s} std {r["std"]:5.1f}->{r.get("std_after","-")}  32px {r["std32"]:4.1f}->{r.get("std32_after","-")}  mean {r["mean"]}->{r.get("mean_after","=")} {r.get("placeholder") or ""}')
