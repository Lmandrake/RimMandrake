import sys, os, re, glob, json, hashlib
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
R="/home/mandrake/rm/bench/src/"
DEP="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/"
depmods=sorted(os.listdir(DEP))
BIO=DEP+"RimMandrake.Biomes/Biomes/"
extra=["RimMandrake.Biomes/Biomes/"+m for m in sorted(os.listdir(BIO))] if os.path.isdir(BIO) else []
extra+=["RimMandrake.Biomes/Biomes/_Kits/"+m for m in sorted(os.listdir(BIO+"_Kits"))] if os.path.isdir(BIO+"_Kits") else []
depmods+=extra
TAGS={"texPath","swimmingTexPath","uiIconPath","iconPath","texture","flyingAnimationFramePathPrefix","texPathFemale","texPathMale","fallbackTexPath"}
SUBJ={
 "brine":[("RimStarWars/SWBestiary/Defs/TaozinBrineTank/*.xml",None),("RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_TaozinGrub.xml",None),("RimStarWars/Cuisine/Defs/RSW_TaozinBrine.xml",None)],
 "sprinkler":[("RimMandrake/FlowWorks/Defs/Sprinklers/*.xml",None)],
 "river":[("RimMandrake/FlowWorks/Defs/Rivers/*.xml",None),("RimMandrake/FlowWorks/Defs/Hose/*.xml",None)],
 "venomvine":[("RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Plants/RM_Venomvine.xml",None),("RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_Venomvine*.xml",None),("RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_VenomvineFourFormsSupport.xml",None)],
 "titan":[("RimMandrake/GelatinousSlime/Defs/**/*.xml",None)],
 "dragon":[("RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Dragonsnake.xml",None)],
 "trees":[("RimMandrake/*/Defs/ThingDefs_Plants/*.xml",r"(Thulvane|CorriskTree|Ghemmel|Mourvel|Tumbel|Veluthar|Vurmeloth|Zhorrel|Ollamane|VaultRoot|Rockfinger)")],
 "biome":[("Rim*/*/Defs/BiomeDefs/*.xml",None),("Rim*/*/Defs/**/*Biome*.xml",None)],
}
def modroot(p):
    d=os.path.dirname(p)
    while d.startswith(R.rstrip('/')) and d!=R.rstrip('/'):
        if os.path.isdir(d+"/About"): return d
        d=os.path.dirname(d)
def rows(subj):
    out=[]; seen=set()
    for pat,rx in SUBJ[subj]:
        for f in sorted(glob.glob(R+pat,recursive=True)):
            if f in seen: continue
            seen.add(f)
            try: t=ET.parse(f)
            except Exception as e: continue
            par={c:p for p in t.iter() for c in p}
            for e in t.iter():
                if e.tag in TAGS and e.text and e.text.strip():
                    tp=e.text.strip()
                    if subj=="biome" and e.tag!="texture": continue
                    if rx and not re.search(rx,tp): continue
                    # find def
                    n=e; dn=None; gc=None; ds=None
                    while n in par:
                        n=par[n]
                        if n.find("defName") is not None and dn is None: dn=n.find("defName").text
                    p=par.get(e)
                    if p is not None:
                        g=p.find("graphicClass"); gc=g.text if g is not None else None
                        d=p.find("drawSize"); ds=d.text if d is not None else None
                    out.append(dict(subj=subj,file=f[len(R):],tag=e.tag,defName=dn,texPath=tp,graphicClass=gc,drawSize=ds))
    return out
def cands(tp):
    return [tp+".png"]+[f"{tp}_{s}.png" for s in("south","east","north","west")]
def findpng(root,tp):
    base=root+"/Textures/"+tp
    res=[]
    for c in cands(tp):
        if os.path.isfile(root+"/Textures/"+c): res.append(c)
    if os.path.isdir(base): res+= [tp+"/"+x for x in sorted(os.listdir(base)) if x.endswith(".png")]
    # letter forms
    d=os.path.dirname(base); b=os.path.basename(base)
    if os.path.isdir(d):
        for x in sorted(os.listdir(d)):
            if x.endswith(".png") and re.match(re.escape(b)+r"_?[a-z]$",x[:-4],re.I) : res.append(os.path.dirname(tp)+"/"+x if os.path.dirname(tp) else x)
    return res
def stats(path):
    im=Image.open(path); w,h=im.size; m=im.mode
    if m!="RGBA": 
        im2=im.convert("RGBA"); a=np.array(im2)[:,:,3]
    else: a=np.array(im)[:,:,3]
    vis=a>16
    bb=None
    if vis.any():
        ys,xs=np.where(vis); bb=(int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
    cs=[int(a[0,0]),int(a[0,-1]),int(a[-1,0]),int(a[-1,-1])]
    return dict(size=(w,h),mode=m,visfrac=round(float(vis.mean()),3),bbox=bb,corners=cs,has_alpha=(m in("RGBA","LA","P")) and a.min()<255)
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()[:10]
if __name__=="__main__":
    allrows=[]
    for s in sys.argv[1:]:
        for r in rows(s):
            mr=modroot(R+r["file"]); r["mod"]=os.path.basename(mr) if mr else None
            files=findpng(mr,r["texPath"]) if mr else []
            r["src_files"]=files
            r["src_stats"]={f:stats(mr+"/Textures/"+f) for f in files}
            # deployed: own mod name first then anywhere
            dep={}
            for dm in ([r["mod"]] if r["mod"] in depmods else [])+["RimMandrake.Biomes/Biomes/"+r["mod"]]+[m for m in depmods if m!=r["mod"]]:
                dr=DEP+dm
                fs=findpng(dr,r["texPath"]) if os.path.isdir(dr+"/Textures") else []
                if fs: dep[dm]=fs; 
                if fs and dm==r["mod"]: break
            r["dep"]=dep
            r["sha_match"]=None
            if mr and dep:
                dm=list(dep)[0]; 
                r["sha_match"]=[ (f, sha(mr+"/Textures/"+f)==sha(DEP+dm+"/Textures/"+f) if os.path.isfile(DEP+dm+"/Textures/"+f) else None) for f in files]
            allrows.append(r)
    json.dump(allrows,open(sys.argv[0].replace("scan.py","out_"+"_".join(sys.argv[1:])+".json"),"w"),indent=1,default=str)
    for r in allrows:
        dm=list(r["dep"])[0] if r["dep"] else None
        nm=sum(1 for x in (r["sha_match"] or []) if x[1] is False); nn=sum(1 for x in (r["sha_match"] or []) if x[1] is None)
        print(f'{r["subj"]}|{r["defName"]}|{r["tag"]}|{r["graphicClass"]}|{r["drawSize"]}|{r["texPath"]}|src={len(r["src_files"])} dep={dm}:{len(r["dep"].get(dm,[])) if dm else 0} diff={nm} missing_in_dep={nn}')
