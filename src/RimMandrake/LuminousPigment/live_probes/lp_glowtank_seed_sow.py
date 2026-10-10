"""GLOW_TANK_SEED_LIVE_SOW_1 (L2): a SEEDED, powered GlowTank gets its crop sown, spends the seed culture on the first
sow (fuel 1 -> 0), sets `established`, and glows; an UNSEEDED twin with a crop forced into it never establishes
(control: TryEstablish needs the seed). The seed goes in through jawa/thing_refuel (CompRefuelable.Refuel, no hauler).
The sow is tried the real way first (a colonist with Plants 12 and Growing on, the sow research finished,
defaultPlantToGrow) and, if no colonist sows within the budget, the
crop is placed with spawn_batch and the result says route=spawned. python.exe, bridge held, any quicktest map.
argv: "X,Z" site origin (default 90,130). Exit 0 = PASS."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=180.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
X, Z = (int(v) for v in (sys.argv[1] if len(sys.argv) > 1 else "90,130").split(","))
R = lambda x, z, w, h: "%d,%d,%d,%d" % (x, z, w, h)
call("jawa/clear_area", rect=R(X - 2, Z - 2, 22, 12), dryRun=False)
call("jawa/set_fog", action="unfog", rect=R(X - 2, Z - 2, 22, 12))
for ox in (0, 10):
    call("jawa/make_empty_room", rect=R(X - 1 + ox, Z - 1, 8, 8), wallDef="Wall", stuffDef="WoodLog", floorDef="WoodPlankFloor")
call("jawa/spawn_batch", ops="RM_GlowTank:%d,%d;RM_GlowTank:%d,%d" % (X + 2, Z + 2, X + 12, Z + 2))
tanks = sorted((call("jawa/list_things", defName="RM_GlowTank", rect=R(X - 2, Z - 2, 22, 12)).get("things") or []),
               key=lambda r: (r.get("position") or {}).get("x", r.get("x", 0)))
if len(tanks) != 2:
    print("FAIL: UNMEASURED: %d tanks spawned" % len(tanks)); sys.exit(1)
seeded, bare = tanks[0]["id"], tanks[1]["id"]
for tid in (seeded, bare):
    call("jawa/power_net", thing=tid, forcePowerOn=True)
def state(tid):
    f = call("jawa/thing_refuel", thingId=tid, amount=0, fields="established")
    g = call("jawa/comp_read", thing=tid, comp="CompGlower", members="glowOnInt")
    plants = call("jawa/list_things", defName="RM_CrowncarpetCultured", rect=R(X - 2, Z - 2, 22, 12)).get("things") or []
    return dict(fuel=f.get("fuelAfter"), established=(f.get("fields") or {}).get("established"), missing=f.get("missing"),
                glow=(g.get("values") or {}).get("glowOnInt"), plants=len(plants), ok=f.get("success"), err=f.get("error"))
rows = {"start": state(seeded)}
rows["refuel"] = call("jawa/thing_refuel", thingId=seeded, amount=1)
rows["seeded"] = state(seeded)
route = "colonist"
# the real sow needs what the game asks of it: the sow research (RM_DeepfireRefining), Growing >= sowMinSkill 6, Growing on
rows["research"] = call("jawa/research_finish_project", project="RM_DeepfireRefining", doCompletionDialog=False, doCompletionLetter=False).get("success")
before = {q.get("id") for q in call("jawa/list_pawns", rect=R(X, Z, 6, 6)).get("pawns") or []}
call("jawa/spawn_pawn", kindDef="Colonist", x=X + 1, z=Z + 1, faction="player", count=1)
grower = next((q.get("id") for q in call("jawa/list_pawns", rect=R(X, Z, 6, 6)).get("pawns") or [] if q.get("id") not in before), None)
if grower:
    call("jawa/set_pawn_skill", pawn=str(grower), skill="Plants", level=12)
    call("jawa/set_work_priority", pawnId=str(grower), workType="Growing", priority=1)
rows["grower"] = grower
sown = False
for _ in range(12):
    call("rimworld/step_game_ticks", ticks=500, pauseFirst=True, timeoutMs=120000)
    pl = call("jawa/list_things", defName="RM_CrowncarpetCultured", rect=R(X, Z, 6, 6)).get("things") or []
    if pl:
        sown = True
        break
if not sown:
    route = "spawned"
    call("jawa/spawn_batch", ops="RM_CrowncarpetCultured:%d,%d" % (X + 2, Z + 2))
call("jawa/spawn_batch", ops="RM_CrowncarpetCultured:%d,%d" % (X + 12, Z + 2))   # the unseeded control's crop
call("rimworld/step_game_ticks", ticks=600, pauseFirst=True, timeoutMs=120000)
rows["after"] = state(seeded)
rows["control"] = state(bare)
for k in ("start", "seeded", "after", "control"):
    print(k, rows[k])
print("refuel", {k: rows["refuel"].get(k) for k in ("success", "fuelBefore", "fuelAfter", "capacity", "error")}, "route", route,
      "research", rows.get("research"), "grower", rows.get("grower"))
fails = []
a, c = rows["after"], rows["control"]
if not rows["seeded"].get("ok") or rows["seeded"]["fuel"] != 1:
    fails.append("UNMEASURED: could not seed the tank (%s)" % rows["seeded"])
if a["fuel"] != 0:
    fails.append("seed culture not spent on the first sow (fuel %s)" % a["fuel"])
if a["established"] != "True":
    fails.append("established flag not set (%s)" % a["established"])
if a["glow"] != "True":
    fails.append("seeded, established tank does not glow (glowOnInt %s)" % a["glow"])
if c["established"] != "False":
    fails.append("control: the UNSEEDED tank established anyway (%s)" % c["established"])
call("jawa/clear_area", rect=R(X - 2, Z - 2, 22, 12), dryRun=False)
print("route=%s" % route, "PASS" if not fails else "FAIL: " + "; ".join(fails))
sys.exit(1 if fails else 0)
