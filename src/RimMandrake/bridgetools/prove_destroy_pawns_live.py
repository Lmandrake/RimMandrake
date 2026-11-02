"""prove_destroy_pawns_live.py - A3 of JAWABENCH_DESTROY_PAWNS_1, on the running companion DLL.

On the loaded (throwaway quicktest) map, paused: spawn ONE hostile Megascarab near the centre, then
  1. jawa/destroy_batch categories=Pawn over its cell must be REFUSED (success false), and the pawn still stands;
  2. jawa/destroy_batch categories=All over its cell must leave it standing (pawns are never destroy_batch's);
  3. jawa/pawn_force_incapacitate action=vanish by id must answer destroyedAfter=true, and jawa/list_pawns over
     the cell must no longer list it (the instrument is calibrated by step 1-2, where the same read DID list it).
categories=All clears every non-pawn thing in the 9x9 round the spawn: a throwaway map only.
Exit 0 when all hold, 1 otherwise, 2 when the stage could not be set (no map / spawn failed).
Run with Windows python from the repo root: python.exe src\\RimMandrake\\bridgetools\\prove_destroy_pawns_live.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

KIND = "Megascarab"
h, p, t = rb.resolve_endpoint()
S = rb.RimBridge(host=h, port=p, token=t, timeout=120.0)
S.connect()


def call(tool, **kw):
    try:
        return S.call(tool, kw) or {}
    except rb.RimBridgeError as e:      # a refusal may arrive as a tool error
        return {"success": False, "error": str(e)}


def listed(pid, whole_map=False, alive=True):
    """True / False from a list_pawns read that worked (corpses included); None when the read itself failed (never
    'absent'). alive=False: any row with the id counts, so a vanish that left a corpse is NOT 'gone'."""
    kw = {} if whole_map else {"rect": RECT}
    r = call("jawa/list_pawns", limit=5000, includeCorpses=True, **kw)
    if r.get("success") is False or not isinstance(r.get("pawns"), list) or (r.get("truncated") or 0) > 0:
        return None
    return any(q.get("id") == pid and (not alive or not (q.get("dead") or q.get("downed"))) for q in r["pawns"])


mi = call("jawa/map_info")
if not mi.get("sizeX"):
    print("STAGE no current map: %s" % str(mi)[:200])
    sys.exit(2)
x, z = mi["sizeX"] // 2, mi["sizeZ"] // 2
call("jawa/set_game_speed", speed=0)                # paused: the pawn cannot walk out of RECT between calls
sp = call("jawa/spawn_pawn", kindDef=KIND, x=x, z=z, faction="hostile", count=1)
pw = (sp.get("pawns") or [{}])[0]
pid = pw.get("id")
if not pid or sp.get("success") is not True or pw.get("ok") is False or pw.get("hostile") is not True:
    print("STAGE spawn_pawn %s did not stage one hostile pawn: %s" % (KIND, str(sp)[:300]))
    sys.exit(2)
x, z = pw.get("x", x), pw.get("z", z)
RECT = "%d,%d,9,9" % (x - 4, z - 4)                  # destroy_batch and the presence reads cover the SAME cells
ok = True


def row(name, good, detail):
    global ok
    ok &= bool(good)
    print(("PASS " if good else "FAIL ") + name + "  " + str(detail)[:300])


r = call("jawa/destroy_batch", rects=RECT, categories="Pawn")
# the refusal's own words (JawaBenchTerrainTools.cs DestroyBatch Fail): a transport error is not a refusal
row("A3 destroy_batch categories=Pawn is refused", r.get("success") is False and not r.get("error")
    and "never removes pawns" in str(r.get("message") or ""), r)
row("A3 ... and the hostile still stands (list_pawns sees it)", listed(pid) is True, pid)
r = call("jawa/destroy_batch", rects=RECT, categories="All")
row("A3 destroy_batch categories=All succeeds, counts the pawn skipped, leaves it standing",
    r.get("success") is True and (r.get("pawnsSkipped") or 0) >= 1 and listed(pid) is True, r.get("message") or r)
v = call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
row("A3 vanish by id answers destroyedAfter=true", v.get("destroyedAfter") is True, v)
row("A3 the hostile is gone from the whole map's list_pawns, no corpse either (a read that worked)",
    listed(pid, whole_map=True, alive=False) is False, pid)
sys.exit(0 if ok else 1)
