"""python.exe: visit 8. Read Pyrelands' master, roster toggle, gate and wind probe on the running game; SET=1 puts the master and roster on."""
import json, os, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
T = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    def show(w):
        for f in ("pyrelandsEnabled", "burnLineEnabled", "windCarriesFireEnabled", "fireHawkSpreadEnabled", "fireClockEnabled", "furnaceThermalEnabled"):
            print(w, f, c("jawa/mod_settings_field", typeName=T, action="get", field=f).get("value"))
        print(w, "gate", c("jawa/static_call", type="RimMandrake.Pyrelands.PyrelandsMechanicsGate", method="get_On").get("result"),
              "shell", c("jawa/static_call", type="RimMandrake.Pyrelands.PyrelandsMechanicsGate", method="get_ShellOn").get("result"),
              c("jawa/static_call", type="RimMandrake.Pyrelands.MapComponent_BurnLine", method="ProbeWind").get("result"))
    show("now")
    if os.environ.get("SET") == "1":
        print(c("jawa/mod_settings_field", typeName=T, action="set", field="pyrelandsEnabled", value="True").get("valueAfter"))
        print(json.dumps(c("jawa/mod_settings_field", typeName="RimMandrake.Biomes.RM_BiomesSettings", action="set", field="enabled", key="Pyrelands", value="True"))[:300])
        show("after")
