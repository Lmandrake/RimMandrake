import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
ST="RimMandrake.Cauldron.RM_CauldronSettings"
S.quiet()
x,z=40,200
out={}
with S.Scene("acid",x-6,z-2,15,9) as sc:
    cells={"vwall":(x-4,z,"Wall","RM_Vexxith"),"vdoor":(x,z,"RM_VexxithDoor","RM_Vexxith"),"swall":(x+4,z,"Wall","Steel"),"vwall2":(x-4,z+4,"Wall","RM_Vexxith")}
    for k,(cx,cz,d,stuff) in cells.items():
        r=S.call("jawa/build_batch",ops="%s:%d,%d"%(d,cx,cz),stuff=stuff,readBack=2)
        out["build_"+k]={"survived":r.get("survived"),"stuff":[w.get("stuff") for w in (r.get("things") or [])]}
    def hit(k):
        cx,cz,d,_=cells[k]
        r=S.call("jawa/damage",damageDef="AcidBurn",amount=20.0,x=cx,z=cz)
        rows=[w for w in (r.get("results") or []) if isinstance(w,dict) and w.get("def")==d]
        return (rows[0].get("hitPointsBefore"),rows[0].get("hitPointsAfter")) if rows else ("noresult",json.dumps(r,default=str)[:200])
    for k in ("vwall","vdoor","swall"): out["hit_"+k]=hit(k)
    # find settings type
    g=S.call("jawa/mod_settings_field",typeName=ST,action="get",field="vexxithAcidImmunityEnabled"); out["get"]=g.get("value"),g.get("success"),g.get("message")
    S.call("jawa/mod_settings_field",typeName=ST,action="set",field="vexxithAcidImmunityEnabled",value="False")
    out["hit_vwall2_off"]=hit("vwall2")
    S.call("jawa/mod_settings_field",typeName=ST,action="set",field="vexxithAcidImmunityEnabled",value="True")
    out["restored"]=S.call("jawa/mod_settings_field",typeName=ST,action="get",field="vexxithAcidImmunityEnabled").get("value")
print(json.dumps(out,default=str))
