"""Live bridge test for the owner's 2026-11-14 pit look fixes (RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE).

    python.exe pit_look_1114_live.py [section ...]     sections: pour_labels pit_walk hot_tub (default: all)

Read-only against the loaded save SITTING_20261114_PIT_FIXES (or any map with the same stations); each section prints
PASS/FAIL/UNMEASURED rows. Status: UNRUN (written 2026-11-14 offline while the owner was in the game; run it with the bridge
held, after FlowWorks is deployed and the game restarted on the new DLL).
"""
import sys

sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")
import validation_core as V  # noqa: E402

B = V.Bridge()
ROWS = []


def row(name, ok, detail):
    ROWS.append((name, ok, detail))
    print("%-10s %-48s %s" % ("PASS" if ok is True else "FAIL" if ok is False else "UNMEASURED", name, str(detail)[:300]))


def static(type_, method, args=""):
    r = B.call("jawa/static_call", type=type_, method=method, args=args) or {}
    return r.get("result") if isinstance(r, dict) and "result" in r else r


def pour_labels():
    """His 9: every pour/drain amount shows metres on one tile; no Fill N wording."""
    for litres, want in (("100", "100 L (one tile 0.05 m deep)"), ("1000", "1 kL (one tile 0.5 m deep)"),
                         ("2048000", "2048 kL (one tile 1024 m deep)")):
        got = static("RimMandrake.FlowWorks.RM_GodLiquidMath", "StepLabel", litres)
        row("pour_label_" + litres, got == want if isinstance(got, str) else None, got)


def pit_walk():
    """His 1: a dry pit floor reads full speed (station A1, 4 m dry pit at 154,200; station C 0.5-4 m pits); B1 (2 m water)
    reads the swim/wading cost, never 4.2%. The walked step: CalculatedCostAt with prevCell on the same floor."""
    for cell in ("154,200", "167,199", "187,199", "180,188"):
        line = static("RimMandrake.FlowWorks.RM_Patch_MouseoverDepth", "ProofPitLabel", cell)
        ok = isinstance(line, str) and line.startswith("line=Pit") and "4.2%" not in line
        if cell != "180,188":
            ok = ok and "100%" in line
        row("pit_walk_readout_" + cell, ok if isinstance(line, str) else None, line)


def hot_tub():
    """His second 8: the geyser pit south of the B2 sign, filled with water: its vent and heated water say Hot tub. The
    geyser cell is read from the map (first sunk SteamGeyser); its pool state from RM_GeyserPit's proof reader."""
    r = B.call("jawa/list_things", defName="SteamGeyser") or {}
    things = r.get("things") or []
    if not things:
        row("hot_tub_geyser_found", None, "no SteamGeyser listed: " + str(r)[:200])
        return
    for t in things[:6]:
        cell = "%s,%s" % (t.get("x"), t.get("z"))
        line = static("RimMandrake.FlowWorks.RM_Patch_MouseoverDepth", "ProofPitLabel", cell)
        if isinstance(line, str) and line.startswith("line=Pit"):
            row("hot_tub_readout_" + cell, "Hot tub" in line or "hot tub" in line, line)


SECTIONS = {"pour_labels": pour_labels, "pit_walk": pit_walk, "hot_tub": hot_tub}

if __name__ == "__main__":
    for name in (sys.argv[1:] or list(SECTIONS)):
        SECTIONS[name]()
    bad = [r for r in ROWS if r[1] is not True]
    print("%d/%d PASS" % (len(ROWS) - len(bad), len(ROWS)))
    sys.exit(1 if bad else 0)
