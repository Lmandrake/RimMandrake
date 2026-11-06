"""HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK live proofs (selftest_terrain_overlays.py is the offline half).

A1 (any loaded map, all five DLC -- ShallowFloodwater and ThinIce are Odyssey's temporary terrain):
    python.exe src/RimMandrake/bridgetools/prove_terrain_overlays_cleared.py
  Three cells near the map's south-east corner get floodwater, thin ice and a Substructure foundation over Soil. A Soil
  paint WITHOUT clearOverlays must leave all three unread and name the overlay (the control: the run4 defect, and the
  diagnostics that trace it); a Soil paint WITH clearOverlays must read back on all three, and get_terrain_batch must read
  Soil there. The cells' prior terrain is painted back after. Exit 0 holds, 1 does not (a companion built before this item
  ignores clearOverlays), 2 no verdict (no map, a call failed).

A2 (after a proof_hose run):  python3 src/RimMandrake/bridgetools/prove_terrain_overlays_cleared.py --hose-json <json>
  The style_hose and realflow blocks were not stopped by a site that did not read back: no *_site*_ready row is UNMEASURED
  SITE, and each block scored at least one PASS/FAIL row. Exit 0 holds, 1 does not, 2 no verdict (no file, a block absent).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))

OVERLAYS = (("ShallowFloodwater", "top"), ("ThinIce", "top"), ("Substructure", "foundation"))


def judge_pair(control, fixed, readback):
    """(code, why) from the control paint, the clearOverlays paint and the read-back ops string."""
    if not isinstance(control, dict) or not isinstance(fixed, dict):
        return 2, "a set_terrain_batch call failed: %r / %r" % (str(control)[:200], str(fixed)[:200])
    named = {e.get("temp") or e.get("foundation") for e in control.get("errors") or [] if isinstance(e, dict)}
    if control.get("cellsFailedVerify") != 3 or not {"ShallowFloodwater", "ThinIce", "Substructure"} <= named:
        return 1, "control: want 3 unread cells naming the overlays, got %s named %s" % (control.get("cellsFailedVerify"), sorted(map(str, named)))
    if fixed.get("success") is not True or fixed.get("cellsFailedVerify") != 0:
        return 1, "clearOverlays paint did not read back: %s" % str(fixed.get("message") or fixed)[:300]
    if "Soil" not in str(readback) or any(o in str(readback) for o, _ in OVERLAYS):
        return 1, "get_terrain_batch after the fix reads %r" % str(readback)[:200]
    return 0, "flood, thin ice and Substructure read back Soil with clearOverlays; without it all 3 were named unread"


def live():
    import rimbridge_client as rb
    h, p, t = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
    c.connect()
    mi = c.call("jawa/map_info", {}, check=False) or {}
    sx, sz = mi.get("sizeX"), mi.get("sizeZ")
    if not sx or not sz:
        print("NO VERDICT: no map (map_info %r)" % (str(mi)[:200],))
        return 2
    x0, z0 = sx - 8, 4
    rect = "%d,%d,3,1" % (x0, z0)
    before = (c.call("jawa/get_terrain_batch", {"rects": rect}, check=False) or {}).get("ops")
    c.call("jawa/destroy_batch", {"rects": rect, "categories": "All"}, check=False)
    c.call("jawa/set_terrain_batch", {"ops": "Soil:" + rect, "clearOverlays": True}, check=False)
    for i, (d, layer) in enumerate(OVERLAYS):
        c.call("jawa/set_terrain_batch", {"ops": "%s:%d,%d,1,1" % (d, x0 + i, z0), "layer": layer}, check=False)
    control = c.call("jawa/set_terrain_batch", {"ops": "Soil:" + rect}, check=False)
    fixed = c.call("jawa/set_terrain_batch", {"ops": "Soil:" + rect, "clearOverlays": True}, check=False)
    readback = (c.call("jawa/get_terrain_batch", {"rects": rect}, check=False) or {}).get("ops")
    if before:
        c.call("jawa/set_terrain_batch", {"ops": before, "clearOverlays": True}, check=False)
    code, why = judge_pair(control, fixed, readback)
    print(("PASS: " if code == 0 else "FAIL: " if code == 1 else "NO VERDICT: ") + why)
    return code


def judge_hose(res):
    rows = (res or {}).get("rows") or []
    bad = [r["id"] for r in rows if "site" in str(r.get("id")) and str(r.get("id")).endswith("_ready")
           and r.get("status") == "UNMEASURED" and r.get("class") == "SITE" and r.get("block") in ("style_hose", "realflow")]
    if bad:
        return 1, "site not ready: %s -- %s" % (bad, [str(r.get("detail"))[:300] for r in rows if r["id"] in bad])
    scored = {b: sum(1 for r in rows if r.get("block") == b and r.get("status") in ("PASS", "FAIL")) for b in ("style_hose", "realflow")}
    if not all(scored.values()):
        return 2, "a block scored no row: %s" % scored
    return 0, "style_hose and realflow sites ready; rows scored %s" % scored


def main(argv):
    if len(argv) >= 2 and argv[0] == "--hose-json":
        try:
            res = json.load(open(argv[1], encoding="utf-8"))
        except (OSError, ValueError) as ex:
            # GAMEENV_FIX_PROOFSITE_54339AD0_ITEMS_WAIT: proof_hose writes no JSON when its offline gate is red (REFUSED); say
            # so and quote its run log, so the lane reads the cause, not a bare FileNotFoundError
            why = "%s: %r" % (argv[1], ex)
            run = os.path.join(os.path.dirname(argv[1]), "run.txt")
            if os.path.isfile(run):
                tail = [ln.strip() for ln in open(run, encoding="utf-8", errors="replace").read().splitlines() if ln.strip()][-3:]
                why += " -- proof_hose did not write it; %s ends: %s" % (run, " | ".join(tail)[:600])
            print("NO VERDICT: " + why)
            return 2
        code, why = judge_hose(res)
        print(("PASS: " if code == 0 else "FAIL: " if code == 1 else "NO VERDICT: ") + why)
        return code
    return live()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
