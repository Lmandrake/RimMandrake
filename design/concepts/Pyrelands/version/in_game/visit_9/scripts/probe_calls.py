import sys; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t=resolve_endpoint()
with RimBridge(h,p,t) as rb:
    c=lambda tool,**k: rb.call(tool,k)
    print(str(c("jawa/map_comp_read",comp="MapComponent_BurnLine",members="ticksSinceAnyFire,lastReseedAttemptTick,fireCount"))[:300])
    print(str(c("jawa/map_comp_set",comp="MapComponent_BurnLine",member="ticksSinceAnyFire",value="119880"))[:300])
    print(str(c("jawa/map_comp_set",comp="MapComponent_BurnLine",member="nope",value="1"))[:200])
    print(str(c("jawa/map_comp_set",comp="zzz",member="nope",value="1"))[:120])
    for a in ("current|150,225|20000",):
        print(a, str(c("jawa/static_call",type="RimMandrake.ExplosiveGrowth.ExplosiveGrowthAPI",method="Soak",args=a))[:250])
    print(str(c("jawa/mod_settings_field",typeName="RimMandrake.ExplosiveGrowth.ExplosiveGrowthSettings",action="get",field="chargeHours"))[:200])
