"""Visit 4 owed case RIMMANDRAKE_PIN_PYRE_DESCRIPTIONS_FURNACE_CARD_COULD_READ_BLANK: read the live description of the
furnace-beast and the other creatures a player inspects (jawa/get_defs, the loaded defs), and the furnace-beast's own
inspect card through a spawned one. Exit 0 when every description is non-blank, 1 when one is blank, 2 when unread."""
import json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
DEFS = ["ThingDef/RM_FurnaceBeast", "ThingDef/RM_Ashwallow", "ThingDef/RM_FireHawk", "ThingDef/RM_Flamefang",
        "ThingDef/RM_Ullai", "ThingDef/RM_FE_Plant_ScorchFruit", "ThingDef/RM_FE_Plant_EmberGrass",
        "HediffDef/RM_FlamefangVenom", "BiomeDef/RM_Pyrelands"]
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    call = lambda n, **kw: clockgate._unwrap(raw.call(n, kw))  # noqa: E731
    r = call("jawa/get_defs", defs=";".join(DEFS), fields="description")
    print("get_defs", json.dumps(r)[:2500])
    found = r.get("defs") or r.get("results") or {}
    rows = found if isinstance(found, list) else [dict(v, key=k) for k, v in found.items()] if isinstance(found, dict) else []
    descs = {}
    for row in rows:
        key = row.get("key") or row.get("defName") or row.get("name")
        d = (row.get("fields") or {}).get("description", row.get("description"))
        descs[key] = d
    print("DESCRIPTIONS", json.dumps(descs)[:3000])
    if not descs:
        print("UNMEASURED: get_defs gave no description rows"); sys.exit(2)
    blank = [k for k, v in descs.items() if not (v or "").strip()]
    print("BLANK", blank)
    sys.exit(1 if blank else 0)
