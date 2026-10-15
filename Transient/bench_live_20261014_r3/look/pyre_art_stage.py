# Stage the Pyrelands art-install subjects for a look: 5 corpses rotted toward dessication, core + sprayer items.
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint(); out = {"steps": []}
def c(rb, tool, **a):
    r = rb.call(tool, a)
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    out["steps"].append({"tool": tool, "args": a, "ok": (r or {}).get("success"), "msg": str((r or {}).get("message"))[:160]})
    return r or {}
KINDS = ["RM_Emberscythe", "RM_FireWasp", "RM_Flamefang", "RM_Sytheclaw", "RM_Barbslinger"]
X0, Z = 100, 140
with RimBridge(h, p, t, timeout=600.0) as rb:
    if "--shoot-only" not in sys.argv: c(rb, "jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    for i, k in (enumerate(KINDS) if "--shoot-only" not in sys.argv else []):
        x = X0 + 3 * i
        c(rb, "jawa/spawn_pawn", kindDef=k, x=x, z=Z)
        c(rb, "rimworld/execute_debug_action", path="Actions\\T: Kill", x=x, z=Z)
        for _ in range(20):
            c(rb, "rimworld/execute_debug_action", path="Actions\\T: Rot 1 day", x=x, z=Z)
    out["corpses"] = c(rb, "jawa/list_things", rect="%d,%d,15,1" % (X0, Z), limit=20)
    for i, d in (enumerate(["RM_LightningBreakerCore", "RM_FE_FirefoamSprayer"]) if "--shoot-only" not in sys.argv else []):
        c(rb, "rimworld/spawn_thing", defName=d, x=X0 + 3 * i, z=Z + 3)
    c(rb, "jawa/clear_ui")
    c(rb, "rimworld/jump_camera_to_cell", x=X0 + 6, z=Z + 1)
    c(rb, "rimworld/set_camera_zoom", rootSize=8)
    s = c(rb, "rimworld/take_screenshot", fileName="r3_pyre_art_look")
    out["shot"] = s.get("path") or s
json.dump(out, open(os.path.join(os.path.dirname(__file__), "pyre_art_stage.json"), "w"), indent=1, default=str)
bad = [s for s in out["steps"] if s["ok"] is False]
print("steps", len(out["steps"]), "failed", len(bad), [b["tool"] + ":" + b["msg"] for b in bad][:6]); print("shot", out["shot"])
