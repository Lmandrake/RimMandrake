"""SUPERDEEP_TARGET_VALIDATOR_1 A1 (L2): a ranged hostile with one enemy in a superdeep pit (closer) and another on open
ground (farther) picks the open-ground enemy instead of idling. Read through jawa/attack_target_probe: the game's own
AttackTargetFinder.BestAttackTarget with JobGiver_AIFightEnemy's flags, so FlowWorks' validator prefix runs.
Controls: the rule OFF picks the nearer pit enemy (proves the scene can tell), and with only the pit enemy left the
rule ON picks nothing. python.exe, bridge held, any quicktest map. Exit 0 = PASS."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=180.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
X, Z = (int(v) for v in (sys.argv[1] if len(sys.argv) > 1 else "60,200").split(","))
site = (X - 2, Z - 4, 30, 9)
PIT, OPEN, HOST = (X + 2, Z), (X + 20, Z), (X + 8, Z)
RULE = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % site)
call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % site)
call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % site)
dig = call("jawa/flowworks_excavation_drive", x=PIT[0], z=PIT[1], deepenLevels=4, setFill=-1)
def spawn(kind, c, fac):
    before = {q.get("id") for q in call("jawa/list_pawns", rect="%d,%d,%d,%d" % site).get("pawns") or []}
    call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=fac, count=1)
    now = call("jawa/list_pawns", rect="%d,%d,%d,%d" % site).get("pawns") or []
    return next((q for q in now if q.get("id") not in before), {})
a = spawn("Colonist", PIT, "player"); b = spawn("Colonist", OPEN, "player"); hst = spawn("Mercenary_Gunner", HOST, "hostile")
gear = S.call("jawa/pawn_gear", {"pawn": str(hst.get("id")), "action": "equip", "def": "Gun_AssaultRifle"})
for pid in (a.get("id"), b.get("id")):
    call("jawa/set_draft", pawnId=str(pid), drafted=True, fireAtWill=False)
def probe():
    return call("jawa/attack_target_probe", pawn=str(hst.get("id")), maxDist=40)
def picked_id(r):
    return ((r.get("picked") or {}).get("id") or "").replace("Thing_", "")
ids = {k: str(v.get("id") or "").replace("Thing_", "") for k, v in (("pit", a), ("open", b))}
rows, fails = {}, []
rows["depth"] = dig.get("depth")
rows["on"] = probe()
call("jawa/mod_settings_field", typeName=RULE, action="set", field="superdeepShootingRuleEnabled", value="False")
rows["off"] = probe()
call("jawa/mod_settings_field", typeName=RULE, action="set", field="superdeepShootingRuleEnabled", value="True")
call("jawa/clear_area", rect="%d,%d,1,1" % OPEN, dryRun=False)
rows["onlyPit"] = probe()
for k in ("on", "off", "onlyPit"):
    r = rows[k]
    print(k, json.dumps({x: r.get(x) for x in ("success", "picked", "primary", "primaryVerbRanged", "curJob", "enemyTarget", "error")}))
print("ids", ids, "depth", rows["depth"])
if not rows["on"].get("primaryVerbRanged"):
    fails.append("UNMEASURED: hostile has no ranged verb (%s)" % rows["on"].get("primary"))
if rows["depth"] != 4:
    fails.append("UNMEASURED: pit depth %s, not superdeep" % rows["depth"])
if picked_id(rows["on"]) != ids["open"]:
    fails.append("rule ON picked %s, want the open-ground enemy %s" % (picked_id(rows["on"]) or None, ids["open"]))
if picked_id(rows["off"]) != ids["pit"]:
    fails.append("control: rule OFF picked %s, want the nearer pit enemy %s (scene cannot tell)" % (picked_id(rows["off"]) or None, ids["pit"]))
if picked_id(rows["onlyPit"]):
    fails.append("rule ON with only the pit enemy left picked %s, want none" % picked_id(rows["onlyPit"]))
call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
print("PASS" if not fails else "FAIL: " + "; ".join(fails))
sys.exit(1 if fails else 0)
