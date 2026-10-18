import sys, os, json, re, hashlib
sys.path.insert(0,"/home/mandrake/rm/bench/src/RimMandrake/Utils/art")
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw
import scale_panel as sp
SP="/home/mandrake/.seat-tmp/BENCH/claude-1000/-home-mandrake-rm-bench/15edd687-1a6e-4658-b099-5732edf1617f/scratchpad/"
R="/home/mandrake/rm/bench/src/"
OUT="/home/mandrake/rm/bench/Transient/walk_precheck_2026-10-18/"
def modroot(f):
    d=os.path.dirname(R+f)
    while len(d)>len(R):
        if os.path.isdir(d+"/About"): return d
        d=os.path.dirname(d)
def defsize(f,dn):
    try: t=ET.parse(R+f)
    except: return (1,1)
    for e in t.iter():
        if e.find("defName") is not None and e.find("defName").text==dn:
            s=e.find("size")
            if s is not None and s.text:
                a=re.findall(r"[\d.]+",s.text); return (float(a[0]),float(a[1]))
    return (1,1)
def checks(path):
    im=Image.open(path).convert("RGBA"); a=np.array(im)[:,:,3]; w,h=im.size
    vis=a>16; c={}
    c["size"]=f"{w}x{h}"
    c["alpha_min"]=int(a.min()); c["vis"]=round(float(vis.mean()),3)
    if vis.any():
        ys,xs=np.where(vis); c["bbox"]=(int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
        c["bw"]=int(xs.max()-xs.min()+1); c["bh"]=int(ys.max()-ys.min()+1)
        c["edge_touch"]=[n for n,v in(("L",xs.min()==0),("R",xs.max()==w-1),("T",ys.min()==0),("B",ys.max()==h-1)) if v]
        sub=vis[:, :w//2]; flip=vis[:, ::-1][:, :w//2]
        # mirror symmetry of visible silhouette
        f=vis[:, ::-1]; inter=(vis&f).sum(); uni=(vis|f).sum(); c["sym"]=round(float(inter/uni),2) if uni else 0
    else: c["bbox"]=None
    rgb=np.array(im)[:,:,:3].astype(int)
    # opaque box: >=97% opaque
    c["opaque_box"]= bool(vis.mean()>0.97)
    # checkerboard: corner block with opaque and two alternating greys
    blk=rgb[:16,:16]; ab=a[:16,:16]
    c["checker"]= bool(ab.min()>200 and len(np.unique(blk.reshape(-1,3),axis=0))<=3 and np.abs(blk[0,0]-blk[0,8]).sum()>20) if min(w,h)>=16 else False
    c["sha"]=hashlib.sha256(open(path,'rb').read()).hexdigest()[:8]
    return c
def label(d,text,xy,fill=(235,225,200)):
    d.text(xy,text,fill=fill)
def draw_group(name, entries, ppc=40, maxw=1900):
    """entries: dict(label, files:[abs path], cells:(w,h), human:bool, kind)"""
    rowsimgs=[]
    hum,m,hoff=sp.human_sprite(ppc)
    for e in entries:
        cw,ch=e["cells"]
        panels=[]
        for f in e["files"]:
            im=Image.open(f).convert("RGBA")
            sw,sh=max(1,round(cw*ppc)),max(1,round(ch*ppc))
            if e.get("keep_aspect"):
                sc=max(cw,ch)*ppc/max(im.size); sw,sh=max(1,round(im.size[0]*sc)),max(1,round(im.size[1]*sc))
            panels.append((os.path.basename(f),sp._premul_resize(im,sw,sh)))
        H=max([p[1].size[1] for p in panels]+[hum.size[1]])+34
        W=hum.size[0]+14+sum(p[1].size[0]+12 for p in panels)+10
        row=Image.new("RGBA",(max(W,420),H+16),(30,27,22,255)); d=ImageDraw.Draw(row)
        # checker under art
        x=hum.size[0]+14
        for nm,p in panels:
            for yy in range(0,p.size[1],8):
                for xx in range(0,p.size[0],8):
                    if (xx//8+yy//8)%2==0: d.rectangle([x+xx,16+yy,x+xx+7,16+yy+7],fill=(52,48,40,255))
            # cell ticks
            for k in range(0,int(cw)+1):
                d.line([x+k*ppc,16,x+k*ppc,16+p.size[1]],fill=(90,80,60,255))
            for k in range(0,int(ch)+1):
                d.line([x,16+p.size[1]-k*ppc,x+p.size[0],16+p.size[1]-k*ppc],fill=(90,80,60,255))
            row.alpha_composite(p,(x,16)); label(d,nm.replace(".png","")[-22:],(x,H-14))
            x+=p.size[0]+12
        row.alpha_composite(hum,(2,16+max(p[1].size[1] for p in panels)-hum.size[1]) if max(p[1].size[1] for p in panels)>hum.size[1] else (2,16))
        label(d,e["label"][:150],(4,1))
        rowsimgs.append(row)
    # stack, wrap into columns when too tall
    colw=min(maxw,max(r.size[0] for r in rowsimgs)); 
    sheet_h=sum(r.size[1] for r in rowsimgs)
    img=Image.new("RGBA",(colw,sheet_h),(30,27,22,255)); y=0
    for r in rowsimgs:
        if r.size[0]>colw: r=r.resize((colw,int(r.size[1]*colw/r.size[0])))
        img.alpha_composite(r,(0,y)); y+=r.size[1]
    img.convert("RGB").save(OUT+name+".png"); return OUT+name+".png",img.size
def rows_for(jsonf, pick=None):
    seen=set(); out=[]
    for r in json.load(open(SP+jsonf)):
        if pick and not pick(r): continue
        key=(r["defName"],r["texPath"],r["drawSize"])
        if key in seen or not r["src_files"]: continue
        seen.add(key); out.append(r)
    return out
def entry_from(r, adultonly=False):
    mr=modroot(r["file"]); files=[mr+"/Textures/"+f for f in r["src_files"]]
    order={"south":0,"east":1,"north":2,"west":3}
    def k(f):
        m=re.search(r"_(south|east|north|west)\.png$",f); return order[m.group(1)] if m else 9
    files.sort(key=lambda f:(k(f),f))
    ds=r["drawSize"]
    if ds:
        a=re.findall(r"[\d.]+",ds); cells=(float(a[0]),float(a[-1]))
    else: cells=defsize(r["file"],r["defName"])
    return dict(label=f'{r["defName"]}  {r["graphicClass"] or "(pawn lifestage)"}  drawSize/size {cells}  {r["texPath"].split("/")[-1]}',files=files,cells=cells)
if __name__=="__main__":
    pass
