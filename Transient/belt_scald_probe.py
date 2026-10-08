import sys, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation", None)
    return r
if __name__ == "__main__":
    print(str(call("rimworld/get_ui_state"))[:400])
    print(str(call("jawa/map_info"))[:600])
    for d in ("StatDef/ArmorRating_Heat","HediffDef/RUT_ScaldExposure","DamageDef/RUT_Scald","DamageArmorCategoryDef/RM_ScaldArmor"):
        r=call("jawa/get_defs", defs=d); print(d, r.get("success"), r.get("foundCount"), r.get("notFound"))
