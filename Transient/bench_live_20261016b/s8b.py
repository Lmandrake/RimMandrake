from afk_lib import *
S="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
cells=[(206,234),(207,234),(206,235),(207,235)]
def terr(c): return (B.call("rimworld/get_cell_info",x=c[0],z=c[1]).get("cell") or {}).get("terrainDefName","?").replace("RM_","")
def mu(): return [(p["id"],p["x"],p["z"]) for p in B.call("jawa/list_pawns").get("pawns") if p["kind"]=="Muffalo"]
m=mu()[0]; mid=int(m[0].replace("Muffalo",""))
print("old mult",B.call("jawa/mod_settings_field",typeName=S,action="get",field="refillRateMultiplier").get("value"))
print(B.call("jawa/mod_settings_field",typeName=S,action="set",field="refillRateMultiplier",value="500").get("success"))
print("readback",B.call("jawa/mod_settings_field",typeName=S,action="get",field="refillRateMultiplier").get("value"))
print("tp",B.hp("pawn:%d=tp:206,234"%mid).get("success"), mu())
t0=tick()
for i in range(12):
    B.hp("pawn:%d=tp:206,234"%mid)
    step(50)
    print("dt",tick()-t0,[terr(c) for c in cells],mu(),flush=True)
print("-- muffalo released")
for i in range(8):
    step(250)
    print("dt",tick()-t0,[terr(c) for c in cells],mu(),flush=True)
