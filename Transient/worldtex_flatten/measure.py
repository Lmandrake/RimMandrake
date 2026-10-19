"""Contrast census of the installed biome world textures. usage: measure.py [root]"""
import json,os,sys,numpy as np
from PIL import Image
R=json.load(open("Transient/biome_worldtex_2026-10-18/apply_result.json"))
def files():
    seen={}
    for dn,key,mod,newname,*_ in R: seen.setdefault(f"src/{mod}/Textures/World/Biomes/{newname}.png",[]).append(dn)
    fc="src/RimMandrake/FloodedCanyon/Textures/World/Biomes/RM_CrackedLands.png"
    if fc in seen: seen["src/RimMandrake/CrackedLands/Textures/World/Biomes/RM_CrackedLands.png"]=seen.pop(fc)  # moved at 20f2c5c98d
    return seen
def stats(p):
    a=np.asarray(Image.open(p).convert("RGB"),float); L=a@[0.2126,0.7152,0.0722]
    small=np.asarray(Image.fromarray(np.clip(L,0,255).astype(np.uint8)).resize((32,32),Image.BOX),float)
    return round(L.std(),1), round(small.std(),1), [round(x) for x in a.reshape(-1,3).mean(0)]
if __name__=="__main__":
    out=[]
    for p,dns in files().items():
        if not os.path.exists(p): print("MISSING",p); continue
        out.append((*stats(p),p,dns))
    for s,ss,m,p,dns in sorted(out,key=lambda t:-t[0]):
        print(f"{s:6.1f} {ss:5.1f} {os.path.basename(p):26s} mean={m} {','.join(dns)}")
    print(len(out),"files /",sum(len(d) for d in files().values()),"defs")
