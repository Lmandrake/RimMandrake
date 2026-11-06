#!/usr/bin/env python3
"""Selftest: prove_hover_tooltip.py never hides the HUD it is trying to hover.
(GAMEENV_FIX_PROOFSITE_E94045E9_ITEMS_WAIT)

The 2026-11-06 live A1 run ended NO VERDICT: get_ui_layout held only the Inspect surface, 0 elements, tabCount 0. The
probe's own jawa/clear_ui call took clear_ui's default hideHud=true, a 20 s vanilla screenshot-mode lease, and in
screenshot mode RimWorld draws no gizmo grid, no inspect tabs and no tooltips. A fake bridge models that rule (a
hidden HUD empties every surface but Inspect); the probe is driven through ensure_map and all three clauses with
the frame pair stubbed. Cases:
  1. the instance: clear_ui called the old way (no hideHud) reproduces 'no gizmo element in get_ui_layout';
  2. A1, A2, A3: every jawa/clear_ui call carries hideHud=false and A1 finds the GizmoGridDrawer's elements;
  3. a lease someone else took that ends after a few polls is waited out;
  4. a lease that never ends gives NO VERDICT naming the hidden HUD, not a false 'no gizmo'.
Exit 0 = all pass.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prove_hover_tooltip as ph  # noqa: E402


class FakeBridge:
    def __init__(self, foreign_lease_polls=0):
        self.hud_hidden = foreign_lease_polls != 0
        self.lease_polls = foreign_lease_polls     # <0 = never ends
        self.calls = []

    def call(self, tool, params, check=False):
        self.calls.append((tool, dict(params)))
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 250, "sizeZ": 250}
        if tool == "jawa/clear_ui":
            if params.get("hideHud", True):
                self.hud_hidden = True
            elif self.hud_hidden and self.lease_polls > 0:
                self.lease_polls -= 1
                if self.lease_polls == 0:
                    self.hud_hidden = False
            return {"success": True, "hudHidden": self.hud_hidden}
        if tool == "rimworld/list_colonists":
            return {"success": True, "colonists": [{"pawnId": "Thing_Human1"}]}
        if tool == "jawa/build_batch":   # the real read-back carries no ThingID (JawaBenchMapTools.cs BuildBatch)
            return {"success": True, "placed": 1, "survived": 1, "things": [{"def": "ButcherSpot", "x": 125, "z": 125}]}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"id": "Thing_ButcherSpot9", "def": "ButcherSpot"}]}
        if tool == "rimworld/open_inspect_tab":
            return {"success": not self.hud_hidden}
        if tool == "rimworld/get_ui_layout":
            inspect = {"type": "RimWorld.MainTabWindow_Inspect", "surfaceTargetId": "main-tab:Inspect",
                       "elements": []}
            if self.hud_hidden:
                return {"success": True, "surfaces": [inspect]}
            inspect["elements"] = [{"targetId": "ui-element:1:1:%d" % i} for i in (1, 2)]
            gizmos = {"type": "Verse.GizmoGridDrawer", "surfaceTargetId": "selection-gizmos",
                      "elements": [{"targetId": "ui-element:1:2:%d" % i} for i in (1, 2, 3)]}
            bills = {"type": "RimWorld.ITab_Bills", "surfaceTargetId": "itab:bills",
                     "elements": [{"targetId": "ui-element:1:3:1"}]}
            return {"success": True, "surfaces": [inspect, gizmos, bills]}
        return {"success": True}


def stub_pair(self, tag, hover_params):
    self.c.calls.append(("PAIR", {"tag": tag, "hudHidden": self.c.hud_hidden}))
    return {"tag": tag, "hover": hover_params, "tooltip": {"drawn": False, "box": None}, "readout": {"changed": False}}


ph.Probe.pair = stub_pair
ph.time.sleep = lambda s: None
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s%s" % ("PASS" if cond else "FAIL", name, ("  " + detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def run(clause, fake):
    p = ph.Probe(fake, "/nonexistent")
    sx, sz = ph.ensure_map(p)
    if clause == "A1":
        return ph.clause_gizmo(p)
    if clause == "A2":
        return ph.clause_bill(p, sx, sz)
    return ph.clause_mapthing(p, sx, sz)


def clear_calls(fake):
    return [prm for t, prm in fake.calls if t == "jawa/clear_ui"]


def main():
    # 1. the instance: the old call shape hides the HUD and A1 finds no gizmo
    fixed = ph.clear_ui
    ph.clear_ui = lambda p, **kw: p.call("jawa/clear_ui", kw)
    fake = FakeBridge()
    try:
        run("A1", fake)
        check("instance reproduces: old clear_ui call -> no gizmo element", False, "probe proceeded")
    except ph.NoVerdict as e:
        check("instance reproduces: old clear_ui call -> no gizmo element", "no gizmo element" in str(e), str(e))
    ph.clear_ui = fixed

    # 2. the fix, every clause
    for clause in ("A1", "A2", "A3"):
        fake = FakeBridge()
        try:
            rows = run(clause, fake)
        except ph.NoVerdict as e:
            check("%s runs with the HUD shown" % clause, False, str(e))
            continue
        cc = clear_calls(fake)
        check("%s: every clear_ui passes hideHud=false" % clause,
              cc and all(prm.get("hideHud") is False for prm in cc), str(cc))
        pairs = [prm for t, prm in fake.calls if t == "PAIR"]
        check("%s: hovers only with the HUD drawn" % clause,
              pairs and not any(prm["hudHidden"] for prm in pairs), str(pairs))
        if clause == "A1":
            check("A1: hovers the GizmoGridDrawer elements", [r["hover"]["targetId"] for r in rows][:3] ==
                  ["ui-element:1:2:%d" % i for i in (1, 2, 3)], str(rows))

    # 3. a foreign lease that ends is waited out
    fake = FakeBridge(foreign_lease_polls=3)
    try:
        rows = run("A1", fake)
        check("foreign lease waited out", bool(rows) and not fake.hud_hidden)
    except ph.NoVerdict as e:
        check("foreign lease waited out", False, str(e))

    # 4. a lease that never ends: NO VERDICT about the HUD, quickly
    ph.HUD_WAIT_S = 0.2
    fake = FakeBridge(foreign_lease_polls=-1)
    try:
        run("A1", fake)
        check("endless lease -> NO VERDICT naming the HUD", False, "probe proceeded")
    except ph.NoVerdict as e:
        check("endless lease -> NO VERDICT naming the HUD", "HUD still hidden" in str(e), str(e))

    print("selftest_hover_probe_hud: %s" % ("FAIL %s" % FAILS if FAILS else "ALL PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
