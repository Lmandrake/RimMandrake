import sys
exec(open("contact.py").read().split('if __name__')[0])
def vsr(f,dn):
    t=ET.parse(R+f)
    for e in t.iter():
        if e.find("defName") is not None and e.find("defName").text==dn:
            p=e.find("plant"); 
            if p is not None and p.find("visualSizeRange") is not None:
                a=re.findall(r"[\d.]+",p.find("visualSizeRange").text); return float(a[0]),float(a[-1])
            v=e.find("visualSizeRange")
            if v is not None: a=re.findall(r"[\d.]+",v.text); return float(a[0]),float(a[-1])
    return None
def plant_entries(jf, pick=None):
    es=[]
    for r in rows_for(jf,pick):
        e=entry_from(r); v=vsr(r["file"],r["defName"])
        q=(v[1] if v else 1.0)
        e["cells"]=(q,q); e["label"]=f'{r["defName"]} {r["graphicClass"]}  visualSize {v}  pool={len(e["files"])}  drawn at {q} cells'
        es.append(e)
    return es
g={}
# brine
g["01_brine_tank_and_grub"]=[entry_from(r) for r in rows_for("out_brine_sprinkler.json",lambda r:r["subj"]=="brine" and r["src_files"])]
# flowworks
fw=[entry_from(r) for r in rows_for("out_brine_sprinkler.json",lambda r:r["subj"]=="sprinkler" and r["tag"]=="texPath")]
fw+=[entry_from(r) for r in rows_for("out_river.json",lambda r:r["tag"]=="texPath")]
g["02_flowworks_sprinkler_weir_river_hose"]=fw
g["03_venomvine"]=plant_entries("out_venomvine.json",lambda r:r["src_files"])
ti=[entry_from(r) for r in rows_for("out_titan.json",lambda r:r["defName"] in("RM_Titanoslime","RM_Gelatid","RM_Oomb","RM_Wuum") and r["src_files"])]
g["04_titanoslime_gelatinous"]=ti
for k in g:
    for e in g[k]: e["files"]=sorted(set(e["files"]),key=lambda f:f)
dr=[entry_from(r) for r in rows_for("out_dragon.json",lambda r:r["src_files"])]
g["05_dragonsnake"]=dr
import pprint
for k,v in g.items():
    p,s=draw_group(k,v,ppc=int(sys.argv[1]) if len(sys.argv)>1 else 40)
    print(k,s,len(v))
t=plant_entries("out_trees.json")
p,s=draw_group("06_trees_pools",t,ppc=24); print("trees",s,len(t))
