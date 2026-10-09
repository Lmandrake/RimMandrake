import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
def lst(sc,names):
    return [(t.get("def"),t.get("x"),t.get("z"),t.get("hitPoints")) for t in (sc.things().get("things") or []) if t.get("def") in names]
d=S.call("jawa/get_defs",defs="StructureLayoutDef/RUT_VaultType2_FleshWeaponLoose_Sealed",fields="defName")
out["layout"]=[d.get("foundCount"),d.get("notFound")]
d=S.call("jawa/get_defs",defs="ThingDef/RM_TitanoslimeChunk",fields="defName"); out["chunk"]=[d.get("foundCount"),d.get("notFound")]
with S.Scene("seal",40,40,14,8) as sc:
    try:
        sc.put("RUT_VaultFleshSeal",2,3); sc.put("RUT_VaultFleshSeal",10,3)
        s=sc.find("RUT_VaultFleshSeal"); out["seal0"]=lst(sc,["RUT_VaultFleshSeal"])
        for tid in [t["id"] for t in sc.things().get("things") if t.get("def")=="RUT_VaultFleshSeal"][:1]:
            out["dmg"]=str(S.call("jawa/damage",damageDef="Bomb",amount=500,thingId=tid,allowColonists=True))[:160]
        S.run(150)
        out["seal_after_damage"]=lst(sc,["RUT_VaultFleshSeal"])
        sc.put("RM_TitanoslimeChunk",9,3)
        S.run(150)
        out["seal_after_chunk"]=lst(sc,["RUT_VaultFleshSeal","RM_TitanoslimeChunk","Filth_Slime"])
    except Exception as e: out["ERR_seal"]=str(e)[:300]
print(json.dumps(out,default=str))
