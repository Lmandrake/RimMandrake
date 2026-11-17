#!/usr/bin/env python3
"""Offline clump-plan selftest for Explosive Knockback (bars gas_goes_clump_by_clump / inv_gas_chain, test T_GAS_CLUMP_ORDER).

The clump plan of a lit cloud as pure logic. The ORDER of bursts is the Cauldron's burn scan (RM_VentGas.cs BurnScan:
every BurnScanIntervalTicks each Fire tries its own cell and its 8 neighbours; a cell at least IgniteMin thick burns and
gets a new Fire, which joins at the next scan); Explosive Knockback adds one burst per burned cell (the Ignite postfix).
This test (1) reads the constants and the rule's shape from the C# so a changed rule goes red, (2) runs that rule as a
model over a 40-cell cloud and checks: one burst per clump cell, ordered by distance from the lit edge, on many ticks;
a fire not touching the cloud lights nothing; goods within gasBurstRadius of a burst are queued, at most
gasBurstGoodsCells; a person is shoved 1 cell with no impact, at most once per gasPawnCooldownTicks. Planted faults
are run on copies of the source text and must go red.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_clumps.py
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
FILES = {
    "kernel": os.path.join(SRC, "Cauldron", "Source", "Kernel", "RM_VentGasKernel.cs"),
    "vent": os.path.join(SRC, "Cauldron", "Source", "RM_VentGas.cs"),
    "comp": os.path.join(HERE, "Source", "RM_MapComponent_Knockback.cs"),
    "plan": os.path.join(HERE, "Source", "RM_KnockbackPlan.cs"),
    "compat": os.path.join(HERE, "Source", "RM_KnockbackCompat.cs"),
    "mod": os.path.join(HERE, "Source", "RM_KnockbackMod.cs"),
}


def num(text, pat, what):
    m = re.search(pat, text)
    if not m:
        raise ValueError("cannot read " + what)
    return float(m.group(1))


def read_rule(t):
    """The rule as the C# states it; raises ValueError naming what it could not read (a reshaped rule)."""
    r = dict(
        ignite_min=num(t["kernel"], r"const int IgniteMin\s*=\s*(\d+)", "IgniteMin"),
        interval=num(t["kernel"], r"const int BurnScanIntervalTicks\s*=\s*(\d+)", "BurnScanIntervalTicks"),
        max_per_scan=num(t["kernel"], r"const int MaxIgnitionsPerScan\s*=\s*(\d+)", "MaxIgnitionsPerScan"),
        radius=num(t["mod"], r"public static float gasBurstRadius\s*=\s*([\d.]+)f", "gasBurstRadius"),
        goods_cells=num(t["mod"], r"public static int gasBurstGoodsCells\s*=\s*(\d+)", "gasBurstGoodsCells"),
        cooldown=num(t["mod"], r"public static int gasPawnCooldownTicks\s*=\s*(\d+)", "gasPawnCooldownTicks"),
    )
    if not re.search(r"for \(int n = -1; n < 8[^)]*\)\s*\{\s*IntVec3 c = n < 0 \? at : at \+ GenAdj\.AdjacentCells\[n\];", t["vent"]):
        raise ValueError("BurnScan no longer tries the fire's own cell and its 8 neighbours")
    # the scan walks a snapshot of the fires: a fire set this scan joins at the next one (that is what makes clumps)
    r["snapshot"] = bool(re.search(r"for \(int k = 0; k < firesTmp\.Count", t["vent"]))
    if not re.search(r"density >= IgniteMin", t["kernel"]):
        raise ValueError("Ignites is no longer density >= IgniteMin")
    if not re.search(r"if \(__result && VentGasRegistered[^)]*\)\s*\{\s*RM_MapComponent_Knockback\.GasBurst\(", t["compat"]):
        raise ValueError("the Ignite postfix no longer bursts once per burned cell")
    g = t["comp"][t["comp"].index("public static void GasBurst("):]
    g = g[:g.index("private bool ThrowPawn")]
    r["impact_factor"] = num(g, r"impactFactor\s*=\s*([\d.]+)f", "GasBurst impactFactor")
    if "shield = null" not in g or "gas = true" not in g:
        raise ValueError("GasBurst requests are no longer shield-free gas requests")
    if not re.search(r"Mathf\.Max\(0\.9f, RimMandrakeExplosiveKnockbackSettings\.gasBurstRadius\)", g):
        raise ValueError("GasBurst radius is no longer the gasBurstRadius setting")
    if not re.search(r"ownCap = Math\.Max\(1, RimMandrakeExplosiveKnockbackSettings\.gasBurstGoodsCells\)", g):
        raise ValueError("GasBurst goods cap is no longer gasBurstGoodsCells")
    # RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES (live 2026-11-16): gas drifting back into a burned cell was
    # relit by the fire still on it and burst again 30-60 ticks later; a cell bursts once per GasCellOnceTicks
    r["cell_once"] = num(t["comp"], r"const int GasCellOnceTicks\s*=\s*(\d+)", "GasCellOnceTicks")
    if not re.search(r"gasCellBurstTick\.TryGetValue\(c, out int was\) && now - was < GasCellOnceTicks\)\s*\{\s*"
                     r"RM_KnockbackJournal\.Add\(\"gas_reburst_skip\"[^;]*;\s*return;", g):
        raise ValueError("GasBurst no longer refuses a second burst on a cell inside GasCellOnceTicks")
    # the shove rule lives in the Verse-free plan since 2026-11-17 (RM_KnockbackPlan.cs, run by the SelfTest); the map component
    # hands it the ticks since the pawn's last shove and Rules() the cooldown setting
    p = t["plan"]
    if not re.search(r"pawn && b\.gas\)\s*\{[^}]*f\.gasShovedAgo < q\.gasPawnCooldownTicks[^}]*\}\s*s\.maxCells = Math\.Min\(s\.maxCells, 1\);", p, re.S) \
            or "f.gasShovedAgo = Find.TickManager.TicksGame - lastGasShove;" not in t["comp"] \
            or "gasPawnCooldownTicks = gasPawnCooldownTicks" not in t["mod"]:
        raise ValueError("a gas shove is no longer 1 cell at most once per gasPawnCooldownTicks")
    # the game path hands the plan the live rules and the request's gas flag (the old check read both in the map component)
    ex = t["comp"][t["comp"].index("private bool Execute(KnockbackRequest r)"):]
    ex = ex[:ex.index("private static KbBlast BlastOf(")]
    if "KbPlanner.Decide(f, BlastOf(r), RimMandrakeExplosiveKnockbackSettings.Rules()," not in ex \
            or not re.search(r"KbBlast BlastOf\(KnockbackRequest r\)\s*\{[^}]*\bgas = r\.gas\b", t["comp"]):
        raise ValueError("the map component no longer hands the plan the live rules and the request's gas flag")
    return r


def burn(cloud, fire, rule, drift=False):
    """Model of BurnScan: {cell: density}, the first Fire's cell -> [(tick, cell)] bursts in order. drift: gas from an
    unburned neighbour drifts back into a burned cell, whose Fire is still burning, so it is relit (live 2026-11-16);
    Explosive Knockback's GasBurst then bursts a cell at most once per GasCellOnceTicks."""
    dens, fires, out, tick = dict(cloud), [fire], [], 0
    burst_at = {}
    for _ in range(200):
        tick += int(rule["interval"])
        lit, new = 0, []
        for (fx, fz) in (list(fires) if rule["snapshot"] else fires):
            for dx, dz in [(0, 0)] + [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]:
                if lit >= rule["max_per_scan"]:
                    break
                c = (fx + dx, fz + dz)
                if dens.get(c, 0) >= rule["ignite_min"]:
                    dens[c] = 0
                    if c not in burst_at or tick - burst_at[c] >= rule.get("cell_once", 0):
                        out.append((tick, c))
                        burst_at[c] = tick
                    new.append(c)
                    if not rule["snapshot"]:
                        fires.append(c)
                    lit += 1
        if rule["snapshot"]:
            fires += [c for c in new if c not in fires]
        if drift:
            for c in [c for c in cloud if dens.get(c, 0) == 0]:
                if any(dens.get((c[0] + a, c[1] + b), 0) >= rule["ignite_min"] for a in (-1, 0, 1) for b in (-1, 0, 1)):
                    dens[c] = rule["ignite_min"]
        if not new and tick > 600:
            break
    return out


def check(rule):
    faults = []
    cloud = {(x, z): 60 for x in range(8) for z in range(5)}          # a 40-cell cloud
    bursts = burn(cloud, (-1, 2), rule)                               # a Fire on the cell beside the west edge
    cells = [c for _, c in bursts]
    if sorted(cells) != sorted(cloud):
        faults.append("not one burst per clump cell: %d bursts for %d cells" % (len(cells), len(cloud)))
    d = [max(abs(c[0] + 1), abs(c[1] - 2)) for _, c in bursts]
    if d != sorted(d):
        faults.append("bursts not ordered by distance from the lit edge")
    if len(set(t for t, _ in bursts)) < 4:
        faults.append("the cloud went off on %d ticks, not clump by clump" % len(set(t for t, _ in bursts)))
    if burn(cloud, (-3, 2), rule):
        faults.append("a fire two cells off the cloud lit it")
    drifted = [c for _, c in burn(cloud, (-1, 2), rule, drift=True)]
    if sorted(drifted) != sorted(cloud):
        faults.append("with gas drifting back under the fires: %d bursts for %d cells (a cell burst twice)" % (
            len(drifted), len(cloud)))
    if rule["radius"] < 1.9 - 1e-6 or rule["radius"] > 2.0:
        faults.append("burst radius %.2f, the bar says about 1.9 cells" % rule["radius"])
    # goods: a good 1.9 cells from a burst cell (outside the cloud) is reached, one 2.5 cells away is not
    reach = lambda g, b: math.hypot(g[0] - b[0], g[1] - b[1]) <= rule["radius"]
    if not reach((-1, 4), (0, 3)) or any(reach((-3, 2), c) for c in cloud):
        faults.append("goods reach wrong: within the radius must be queued, beyond must not")
    if rule["goods_cells"] != 2:
        faults.append("goods fly at most %d cells, the bar says 2" % rule["goods_cells"])
    if rule["impact_factor"] != 0:
        faults.append("a gas shove carries impact %.2f: people would be hurt" % rule["impact_factor"])
    # a person reached by two bursts 30 ticks apart is shoved once in that window
    shoves, last = 0, None
    for t, c in bursts:
        if reach((3, 2), c) and (last is None or t - last >= rule["cooldown"]):
            shoves, last = shoves + 1, t
    first = [t for t, c in bursts if reach((3, 2), c)]
    in_window = sum(1 for t in first if t - first[0] < rule["cooldown"])
    if not (in_window >= 2 and rule["cooldown"] >= 120):
        faults.append("cooldown %d ticks: a person reached twice inside 2 seconds would be shoved twice" % rule["cooldown"])
    return faults


def main():
    texts = {k: open(f, encoding="utf-8", errors="replace").read() for k, f in FILES.items()}
    try:
        faults = check(read_rule(texts))
    except ValueError as e:
        faults = ["rule unreadable: %s" % e]
    for f in faults:
        print("FAIL", f)
    mutants = {
        "fires reach two cells": ("vent", "GenAdj.AdjacentCells[n]", "GenAdj.AdjacentCells[n] + GenAdj.AdjacentCells[n]"),
        "gas shoves hurt": ("comp", "impactFactor = 0f, source = \"gas\"", "impactFactor = 1f, source = \"gas\""),
        "no cooldown": ("mod", "gasPawnCooldownTicks = 120", "gasPawnCooldownTicks = 0"),
        "the cooldown never reaches the plan": ("mod", "gasPawnCooldownTicks = gasPawnCooldownTicks,", ""),
        "a gas shove keeps the full throw": ("plan", "s.maxCells = Math.Min(s.maxCells, 1);", ""),
        "the game path hands the plan default rules": ("comp", "KbPlanner.Decide(f, BlastOf(r), RimMandrakeExplosiveKnockbackSettings.Rules(), s, new RM_MapKbWorld(map, t))",
                                                        "KbPlanner.Decide(f, BlastOf(r), new KbRules(), s, new RM_MapKbWorld(map, t))"),
        "a gas burst reaches the plan as a plain blast": ("comp", ", gas = r.gas };", " };"),
        "a cell bursts again under its fire": ("comp", "const int GasCellOnceTicks = 600", "const int GasCellOnceTicks = 0"),
        "goods fly 6": ("mod", "gasBurstGoodsCells = 2", "gasBurstGoodsCells = 6"),
        "postfix bursts on every Ignite call": ("compat", "if (__result && VentGasRegistered", "if (VentGasRegistered"),
        "new fires burn in the same scan": ("vent", "for (int k = 0; k < firesTmp.Count", "for (int k = 0; k < fires.Count"),
    }
    missed = 0
    for label, (k, old, new) in mutants.items():
        if old not in texts[k]:
            print("FAIL planted fault '%s' could not be planted (anchor gone)" % label)
            missed += 1
            continue
        m = dict(texts, **{k: texts[k].replace(old, new, 1)})
        try:
            caught = bool(check(read_rule(m)))
        except ValueError:
            caught = True
        if not caught:
            print("FAIL planted fault NOT CAUGHT:", label)
            missed += 1
    ok = not faults and not missed
    print("explosive knockback gas clumps: %s (%d faults, %d/%d planted faults caught)"
          % ("PASS" if ok else "FAIL", len(faults), len(mutants) - missed, len(mutants)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
