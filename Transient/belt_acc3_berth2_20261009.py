import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
mid=S.biome_map(114503,"RM_SeabedFloor_TheScald",layer="RM_SeabedLayer",surface_biome="RM_TheScald",parent="RM_SeabedSite")
sc=[]
try:
    pair=S.Scene("pair",10,30,11,6); sepA=S.Scene("sepA",10,10,6,6); sepB=S.Scene("sepB",20,10,6,6)
    for s in (pair,sepA,sepB): s.__enter__(); sc.append(s); s.room(roof=True)
    for dz in range(1,5): pair.put("Wall",5,dz,stuff="BlocksGranite")
    S.call("jawa/map_commit",full=True)
    snap=lambda:{"pairL":pair.temp(3,3),"pairR":pair.temp(7,3),"sepA":sepA.temp(3,3),"sepB":sepB.temp(3,3)}
    print("t0",snap())
    for i in range(4):
        S.run(1500); print("t",S.ticks(),snap())
finally:
    for s in sc: s.teardown()
    S.drop_map(mid,114503,back=0)
