"""python.exe, bridge held: visit 9's owed text cases, shown in the game. Opens the Pyrelands settings window (captures),
reads the fire-front letter's key as the game translates it, and presses "Reset all" (its own method) on three changed fields."""
import json, os, sys, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
T = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    for key in ("RM_FireFrontLetterLabel", "RM_FireFrontLetterTextWind"):
        print("KEY", key, "=", c("jawa/static_call", type="Verse.Translator", method="Translate", args=key).get("result"))
    fields = {"burnLineEnabled": "False", "freshBurnDays": "2", "crossBiomeBiomeList": "Desert", "windCarriesFireEnabled": "False"}
    get = lambda f: c("jawa/mod_settings_field", typeName=T, action="get", field=f).get("value")  # noqa: E731
    before = {f: get(f) for f in fields}
    for f, v in fields.items():
        c("jawa/mod_settings_field", typeName=T, action="set", field=f, value=v)
    changed = {f: get(f) for f in fields}
    r = c("jawa/static_call", type=T, method="ResetAllFields")
    after = {f: get(f) for f in fields}
    print("RESET before", before, "changed", changed, "call", r.get("success"), "after", after, "OK" if after == before and changed != before else "NOT RESET")
    o = c("rimworld/open_mod_settings", modId="RM_PyrelandsMod", replaceExisting=True)
    print("OPEN", str(o)[:300])
    time.sleep(1)
    s = c("rimworld/take_screenshot", fileName="pv9_settings")
    print("SHOT settings (0) ", s.get("path"))
    for t in ("rimworld/get_ui_layout",):
        try:
            lay = c(t)
            open(r"Transient\pv9\ui_layout.json", "w").write(json.dumps(lay, indent=1))
            print("LAYOUT", len(json.dumps(lay)))
        except Exception as e:  # noqa: BLE001
            print("LAYOUT failed", str(e)[:200])
    print("CLOSE", str(c("jawa/clear_ui"))[:200])
