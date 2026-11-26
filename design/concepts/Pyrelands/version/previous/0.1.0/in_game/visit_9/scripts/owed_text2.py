"""python.exe (ArchSmall): the full fire-front letter text as the game translates it, and the settings window at each scroll."""
import sys, time; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t=resolve_endpoint()
with RimBridge(h,p,t) as rb:
    c=lambda tool,**k: rb.call(tool,k)
    r=c("jawa/static_call",type="Verse.Translator",method="Translate",args="RM_FireFrontLetterTextWind")
    print("LEN",len(str(r.get("result")))); print(repr(r.get("result")))
    o=c("rimworld/open_mod_settings",modId="RM_PyrelandsMod",replaceExisting=True); print(o.get("success"))
    print(c("jawa/window_list_close",typeName="Dialog_ModSettings").get("success"))
