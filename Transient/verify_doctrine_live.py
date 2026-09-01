import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CHECKS = [
    ("ThingDef","Bullet_TurretSniper","960 Bullet"),
    ("ThingDef","EWebShot","368 OuterRim_Blaster"),
    ("ThingDef","Bullet_TeslaBlaster","80 EMP"),
    ("ThingDef","Bullet_EMPColumn","40 EMP"),
    ("ThingDef","VFES_Bullet_ChargeRailgunShot","320 Bullet"),
    ("ThingDef","GTbc_Rocket_TheSingularityCannon","72085 r14.9"),
    ("ThingDef","Jawa_TD_Turret_AutoChargeBlaster","107 Bullet"),
    ("ThingDef","Projectile_VaporiserBeam","21 Burn"),
    ("ThingDef","VGE_Bullet_MassDriver","3154 r14.9 (orig, shared - should be UNCHANGED, clone carries it)"),
    ("ThingDef","Jawa_TD_VGE_MassDriver","3154 r14.9"),
    ("ThingDef","VGE_AnticraftCaster","label check only - anticraft landed AFTER this load"),
    ("DamageDef","LaserCannonBeam","3159"),
    ("DamageDef","Jawa_TD_GraserBeam","395"),
    ("ThingDef","Gun_Vaporiser","burst 30"),
    ("ThingDef","Gun_BeamRepeaterTurret","burst 8"),
]
with RimBridge(host, port, token) as rb:
    for dtype, dn, expect in CHECKS:
        try:
            r = rb.call("jawa/get_def", {"defType": dtype, "defName": dn})
        except Exception as e:
            print(dn, "CALL FAILED:", str(e)[:80]); continue
        if not r or r.get("success") is False:
            print(dn, "TOOL REFUSED:", str(r)[:120]); continue
        import json as j
        s = j.dumps(r)
        keep = {}
        for k in ("damageAmountBase","damageDef","explosionRadius","defaultDamage","burstShotCount","label"):
            i = s.find('"'+k+'"')
            if i >= 0: keep[k] = s[i:i+60].split(":",1)[1].split(",")[0].strip(' "}')
        print(f"{dn} | expect [{expect}] | live {keep}")
