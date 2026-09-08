import sys, time, json, os, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
OUT = r"D:\Luke\dev\Rimworld\Transient\ninefold_fire_proof_result.txt"
def log(m):
    print(m, flush=True)
    open(OUT, "a").write(m + "\n")
open(OUT, "w").write("")

rb = RimBridge(*resolve_endpoint()); rb.__enter__()
def call(n, p=None):
    return rb.call(n, p or {})

log("devmode: " + json.dumps(call("jawa/prefs", {"devMode": True}).get("after")))
gi = call("rimworld/get_game_info")
log("state: %s / %s maps=%s ticks=%s" % (gi.get("status"), gi.get("programState"), gi.get("mapCount"), gi.get("ticksGame")))
if not (gi.get("mapCount") and gi.get("status") == "game_loaded"):
    r = call("rimworld/load_game", {"saveName": "Autosave-4", "ignoreModCompatibility": True})
    log("load_game: %s %s" % (r.get("success"), r.get("code")))
    for i in range(60):
        time.sleep(6)
        try: gi = call("rimworld/get_game_info")
        except Exception:
            rb.__exit__(None,None,None); rb=RimBridge(*resolve_endpoint()); rb.__enter__(); continue
        if gi.get("mapCount") and gi.get("status") == "game_loaded":
            break
    log("after load: %s maps=%s ticks=%s" % (gi.get("programState"), gi.get("mapCount"), gi.get("ticksGame")))
if not (gi.get("mapCount") and gi.get("status") == "game_loaded"):
    log("NO MAP — abort"); sys.exit(1)

# a colonist cell as an anchor
cols = call("rimworld/list_colonists", {"currentMapOnly": True})
cl = cols.get("colonists") or cols.get("pawns") or []
pos = None
for c in cl:
    p = c.get("position") or c.get("pos")
    if p: pos = p; break
log("anchor colonist cell: %s (of %d colonists)" % (pos, len(cl)))
if not pos:
    log("no colonist cell — abort"); sys.exit(1)
cx, cz = (pos["x"], pos["z"]) if isinstance(pos, dict) else (pos[0], pos[2] if len(pos) > 2 else pos[1])

def children(path):
    r = call("rimworld/list_debug_action_children", {"path": path})
    return r.get("children", []) if r.get("success", True) else []

# discover the explosion + spawn leaves
expl = None
for c in children(r"Actions\Explosion..."):
    lab = c["path"].split("\\")[-1].lower()
    if "bomb" in lab: expl = c["path"]; break
if not expl:
    ch = children(r"Actions\Explosion...")
    expl = ch[0]["path"] if ch else None
log("explosion leaf: %s" % expl)

OFF = os.path.getsize(LOG)
log("log offset: %d" % OFF)

# fire an explosion at an empty-ish cell near the colony (explosion hook, no deaths needed)
ex, ez = cx + 8, cz + 8
r = call("rimworld/execute_debug_action", {"path": expl, "x": ex, "z": ez})
log("explosion@(%d,%d): success=%s logs=%s" % (ex, ez, r.get("success"), (r.get("effects") or {}).get("logCount")))
call("rimworld/step_game_ticks", {"ticks": 120})

# spawn 2 hostiles far away and bomb them for a real Pawn.Kill (kill/battle hook)
spawnroot = r"Actions\Spawn Pawn..."
kinds = children(spawnroot)
hostile = None
for c in kinds:
    lab = c["path"].split("\\")[-1].lower()
    if any(k in lab for k in ("pirate", "grunt", "mercenary", "raider", "scavenger")):
        hostile = c["path"]; break
if not hostile and kinds:
    hostile = kinds[0]["path"]
log("hostile kind leaf: %s" % hostile)
hx, hz = cx + 20, cz
ids_before = set()
pl = call("jawa/list_pawns").get("pawns", [])
ids_before = set(str(p.get("id") or p.get("pawnId")) for p in pl)
if hostile:
    for k in range(2):
        rr = call("rimworld/execute_debug_action", {"path": hostile, "x": hx + k, "z": hz})
    call("rimworld/step_game_ticks", {"ticks": 30})
    pl2 = call("jawa/list_pawns").get("pawns", [])
    newp = [p for p in pl2 if str(p.get("id") or p.get("pawnId")) not in ids_before]
    log("spawned new pawns: %d at ~(%d,%d)" % (len(newp), hx, hz))
    # big bomb on them
    for _ in range(3):
        call("rimworld/execute_debug_action", {"path": expl, "x": hx, "z": hz})
    call("rimworld/step_game_ticks", {"ticks": 300})

# harvest
time.sleep(2)
data = open(LOG, "rb").read()[OFF:].decode("utf-8", "ignore")
lines = [l.strip() for l in data.splitlines() if "[Ninefold]" in l]
log("=== [Ninefold] LINES SINCE OFFSET: %d ===" % len(lines))
for l in lines[:40]:
    log("  " + l)
rb.__exit__(None, None, None)
log("DONE")
