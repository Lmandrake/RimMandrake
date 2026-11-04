#!/usr/bin/env python3
"""Live proof of BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE (clause A1): a debug action's FloatMenu is readable and
pickable through the bridge, and picking a liquid in 'Tanks: fill ALL on map to max (pick liquid)' fills every tank.

    python.exe src/RimMandrake/bridgetools/prove_debug_action_menu.py < /dev/null

Needs a quicktest (or any throwaway) map on a list holding FlowWorks and the companion built at or after this item.
Steps, all through jawa/debug_action_menu (the companion tool that runs the action and reads/picks its menu in one
main-thread call, because rimworld/execute_debug_action's menu is gone before the next call):
  1. place three RM_LiquidTank on clear ground near the map centre (jawa/build_batch, player faction);
  2. run 'Tanks: empty ALL on map' (a plain action, no menu) so a fill cannot be confused with what was there;
  3. run the fill-ALL action with NO pick: the reply must list >= 2 liquid options, the first marked '(default)';
  4. run it again picking the SECOND option (a non-default liquid, so a default-only route cannot pass);
  5. read every RM tank's inspect string (jawa/inspect_string): each must read 'Holding: <picked label> (N / N)'.
  The three tanks are destroyed afterwards. Exit 0 = every clause held, 1 = a clause failed, 2 = no verdict
  (no bridge, no map, tool absent, nowhere to place a tank).
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

FILL_ALL = "Actions\\Tanks: fill ALL on map to max (pick liquid)"
EMPTY_ALL = "Actions\\Tanks: empty ALL on map"
TANK = "RM_LiquidTank"
HOLD = re.compile(r"Holding:\s*(.+?)\s*\(([^/()]+?)\s*/\s*([^/()]+?)\)")


def holding(lines):
    """('label', 'have', 'cap') from a tank's inspect lines, or None when it reads Empty / nothing."""
    for ln in lines or []:
        m = HOLD.search(str(ln))
        if m:
            return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    return None


def first_menu_options(reply):
    menus = (reply or {}).get("menus") or []
    return (menus[0].get("options") or []) if menus else []


def main():
    h, p, t = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
    c.connect()
    mi = c.call("jawa/map_info", {}, check=False)
    mi = mi if isinstance(mi, dict) else {}
    sx, sz = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or mi.get("sizeY") or 0)
    if sx <= 20 or sz <= 20:
        print("NO VERDICT: map_info gave no map: %s" % str(mi)[:200])
        return 2
    cx, cz = sx // 2, sz // 2
    rect = "%d,%d,12,4" % (cx - 6, cz - 2)
    c.call("jawa/destroy_batch", {"rects": rect, "categories": "Plant,Item,Filth,Building"}, check=False)
    ops = ";".join("%s:%d,%d" % (TANK, cx - 4 + 4 * i, cz) for i in range(3))
    b = c.call("jawa/build_batch", {"ops": ops, "faction": "player", "readBack": 3}, check=False)
    b = b if isinstance(b, dict) else {}
    if int(b.get("survived") or 0) < 3:
        print("NO VERDICT: could not place three tanks: %s" % str(b)[:300])
        return 2
    fails = []
    try:
        e = c.call("jawa/debug_action_menu", {"path": EMPTY_ALL}, check=False)
        if not (isinstance(e, dict) and e.get("success")):
            if "debug_action_menu" in str(e) and ("unknown" in str(e).lower() or "not found" in str(e).lower()):
                print("NO VERDICT: jawa/debug_action_menu absent from the live companion: %s" % str(e)[:300])
                return 2
            fails.append("empty-all did not run: %s" % str(e)[:300])
        lst = c.call("jawa/debug_action_menu", {"path": FILL_ALL}, check=False)
        opts = first_menu_options(lst if isinstance(lst, dict) else {})
        labels = [o.get("label", "") for o in opts]
        print("options read: %d %s" % (len(labels), labels[:8]))
        if not (isinstance(lst, dict) and lst.get("success")):
            fails.append("listing call failed: %s" % str(lst)[:300])
        if len(labels) < 2:
            fails.append("the fill-ALL menu listed %d options (want >= 2 liquids)" % len(labels))
        elif "(default)" not in labels[0]:
            fails.append("first option is not the '(default)' liquid: %r" % labels[0])
        if len(labels) >= 2:
            pk = c.call("jawa/debug_action_menu", {"path": FILL_ALL, "pickIndex": 1}, check=False)
            picked = (pk or {}).get("picked") if isinstance(pk, dict) else None
            print("picked: %s" % picked)
            if not (isinstance(pk, dict) and pk.get("success") and picked):
                fails.append("pick call failed: %s" % str(pk)[:300])
            want = labels[1]
            ins = c.call("jawa/inspect_string", {"defName": TANK, "limit": 200}, check=False)
            rows = ins.get("things") if isinstance(ins, dict) else None
            if rows is None and isinstance(ins, dict):
                rows = next((v for v in ins.values() if isinstance(v, list)), None)
            rows = rows or []
            if not rows:
                fails.append("inspect_string read no %s: %s" % (TANK, str(ins)[:300]))
            for r in rows:
                hv = holding(r.get("inspect"))
                tid = r.get("id") or r.get("thingId")
                if hv is None:
                    fails.append("%s holds nothing after the pick: %s" % (tid, r.get("inspect")))
                elif hv[0] != want or hv[1] != hv[2]:
                    fails.append("%s reads %r, want %r full" % (tid, hv, want))
            print("tanks read: %d" % len(rows))
        # a menu left from the listing call is pinned open; close it so the map is left as found
        c.call("jawa/window_list_close", {"action": "close", "typeName": "FloatMenu", "closeAll": True, "doCloseSound": False}, check=False)
    finally:
        c.call("jawa/destroy_batch", {"rects": rect, "categories": "Building"}, check=False)
    if fails:
        print("FAIL A1:\n  " + "\n  ".join(fails))
        return 1
    print("PASS A1: the fill-ALL picker listed %d liquids through the bridge; picking %r filled every tank" % (len(labels), labels[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
