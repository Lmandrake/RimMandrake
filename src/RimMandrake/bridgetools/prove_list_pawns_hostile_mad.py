"""prove_list_pawns_hostile_mad.py - live test of RIMMANDRAKE_WIDEN_LIST_PAWNS_HOSTILE_TO_MAD_ANIMALS_ZERO_WHILE_BITING.

On the loaded (throwaway) map, paused: spawn ONE wild Muffalo (no faction), then
  1. calibration: jawa/list_pawns reads it hostile=false with no mental state (a wild calm animal is not hostile);
  2. jawa/pawn_mental action=start state=Manhunter must report started=true;
  3. jawa/list_pawns must read it hostile=true, mentalState=Manhunter, factionHostile=false,
     and the faction='hostile' filter must keep it.
The muffalo is vanished at the end. Kind A (deterministic): one valid run decides.
Exit 0 green, 1 red (the read is wrong), 2 the stage could not be set (no map, spawn or break refused).
Run with Windows python from the repo root, the game picked by RM_GAME_INSTANCE:
  python.exe src\\RimMandrake\\bridgetools\\prove_list_pawns_hostile_mad.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

KIND = "Muffalo"
h, p, t = rb.resolve_endpoint()
S = rb.RimBridge(host=h, port=p, token=t, timeout=120.0)
S.connect()


def call(tool, **kw):
    try:
        return S.call(tool, kw) or {}
    except rb.RimBridgeError as e:      # a refusal may arrive as a tool error
        return {"success": False, "error": str(e)}


def row_of(pid, **filt):
    """The list_pawns row of pid; None when it is not listed; raises SystemExit(2) when the read failed."""
    r = call("jawa/list_pawns", limit=5000, **filt)
    if r.get("success") is False or not isinstance(r.get("pawns"), list):
        print("STAGE list_pawns read failed: %s" % str(r)[:300])
        sys.exit(2)
    return next((q for q in r["pawns"] if q.get("id") == pid), None)


mi = call("jawa/map_info")
if not mi.get("sizeX"):
    print("STAGE no current map: %s" % str(mi)[:200])
    sys.exit(2)
call("jawa/set_game_speed", speed=0)
x, z = mi["sizeX"] // 2, mi["sizeZ"] // 2
sp = call("jawa/spawn_pawn", kindDef=KIND, x=x, z=z, faction="none", count=1)
pw = (sp.get("pawns") or [{}])[0]
pid = pw.get("id")
if not pid or sp.get("success") is not True or pw.get("ok") is False:
    print("STAGE spawn_pawn %s did not stage one wild animal: %s" % (KIND, str(sp)[:300]))
    sys.exit(2)

ok = True


def check(name, good, detail):
    global ok
    ok &= bool(good)
    print("%-4s %-44s %s" % ("PASS" if good else "FAIL", name, detail))


try:
    before = row_of(pid)
    if before is None:
        print("STAGE the spawned %s %s is not listed" % (KIND, pid))
        sys.exit(2)
    check("calm wild animal reads hostile=false", before.get("hostile") is False,
          "hostile=%r mentalState=%r" % (before.get("hostile"), before.get("mentalState")))

    ms = call("jawa/pawn_mental", pawn=pid, action="start", state="Manhunter")
    if ms.get("started") is not True:
        print("STAGE pawn_mental start Manhunter did not start: %s" % str(ms)[:300])
        sys.exit(2)

    after = row_of(pid)
    check("manhunter reads hostile=true", after is not None and after.get("hostile") is True,
          "hostile=%r hostileError=%r" % ((after or {}).get("hostile"), (after or {}).get("hostileError")))
    check("mentalState names Manhunter", (after or {}).get("mentalState") == "Manhunter",
          "mentalState=%r" % (after or {}).get("mentalState"))
    check("factionHostile stays false (no faction)", (after or {}).get("factionHostile") is False,
          "factionHostile=%r" % (after or {}).get("factionHostile"))
    check("faction='hostile' filter keeps it", row_of(pid, faction="hostile") is not None, "")
finally:
    call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")

print("GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
