#!/usr/bin/env python3
"""T_ROOF_WITHER_OFFLINE: Pyrelands grass under a roof declines visibly and leaves dead grass (bar roofed_grass_declines_visibly).

Owner, 2026-11-26 (vision.md 0.2.0): "the grass just suddenly all dies at the same time ... it doesn't turn into dead grass,
just... barren nothing". The wither rule is the SHIPPED C# kernel Source/Kernel/RM_RoofWitherKernel.cs (CompWithersUnderRoof.cs
calls it); this test builds it into Source/SelfTest/RoofWither (net8, no RimWorld) through winbuild.stage_build, feeds it
generated patches on stdin and reads every long tick of every plant back.

    python3 src/RimMandrake/Pyrelands/selftest_pyrelands_roof_wither.py [--seeds N]

The range it reads (what the game can vary for this bar):
  * the plant: each def that carries CompProperties_WithersUnderRoof (read from Defs/, today ember grass 28 HP and quickgrass
    32 HP), its witherTicks (the def's, else the class default read from the .cs) and its hit points when the roof arrives
    (full, damaged, 1 HP);
  * the patch: 200 plants, as a rectangle, a one-cell line and a scatter over a 250x250 map, with consecutive thing ids
    (a patch spawned together) or strided ids (spawned over time), over SEEDS random origins and id bases;
  * the roof: always roofed, never roofed, roofed then unroofed;
  * the gate: Pyrelands mechanics on or off;
  * time: every long tick until 1.6 x witherTicks (past the last death, 1.4 x).
Left out: fire on the patch (bar fire_catches; the scene's contract excludes it), the drawing and the cut job (live only: the scene
sc_roofed_grass_declines), witherTicks below WITHER_FLOOR_TICKS (no def ships one; the floor row says where spread can hold).

Rows (each prints its worst value, its limit and how many cases it read):
  rising          a continuously roofed plant's stage never falls, and passes wilting (1) and withered (2) before dead (3)
  spread_share    no single long tick kills more than SHARE_MAX of one patch (0.1.0 killed 100% on one long tick)
  spread_window   the 5th..95th percentile of a patch's death times spans at least WINDOW_MIN_TICKS
  all_die         every continuously roofed plant is dead by 1.4 x witherTicks + one long tick
  one_hp          a 1-HP plant on a roofed cell dies on its first roofed long tick (the scene's probe)
  unroofed        a never-roofed plant: stage 0 and 0 damage on every long tick
  unroof_stops    roofed then unroofed: 0 damage after the roof goes
  gate_off        gate off: stage 0 and 0 damage on every long tick
  remains         each def with the comp names a remainsDef that is a real ThingDef of ours, a dead plant labelled dead grass;
                  each simulated death therefore names it
  crumble         dead grass is gone by 1.4 x crumbleTicks, and no long tick crumbles more than SHARE_MAX of a patch
  floor           the shipped witherTicks is at or above WITHER_FLOOR_TICKS
  no_kill_in_tick CompTickLong never kills or destroys (vanilla Plant.TickLong reads base.Map after the comps tick, so a kill
                  there is 'Exception ticking RM_FE_Plant_EmberGrass'); its lethal step goes to the map component's queue,
                  whose MapComponentTick kills and spawns Props.remainsDef
"""
import os
import random
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import winbuild  # noqa: E402

PYR = os.path.join(HERE, "Source")
KERNEL = os.path.join(PYR, "Kernel", "RM_RoofWitherKernel.cs")
COMP = os.path.join(PYR, "CompWithersUnderRoof.cs")
SELFTEST = os.path.join(PYR, "SelfTest", "RoofWither")
CSPROJ = os.path.join(SELFTEST, "RimMandrakePyrelands.RoofWither.csproj")
DEFS = os.path.join(HERE, "Defs")
COMP_CLASS = "RimMandrake.Pyrelands.CompProperties_WithersUnderRoof"

LONG = 2000            # GenTicks.TickLongInterval (vanilla 1.6 decompile)
PATCH = 200            # the brief's patch size
SHARE_MAX = 0.15       # our reading of the bar ("all dies at the same time"): no long tick (2000 ticks, ~33 s at speed 1) takes
                       # more than about one plant in seven of a patch
WINDOW_MIN_TICKS = 30000  # our reading of the bar: a patch's deaths (5th..95th percentile) spread over at least half a day
WITHER_FLOOR_TICKS = 40000  # measured by this test's own sweep (printed): below it 200 deaths share too few long ticks for SHARE_MAX
UNROOF_AT = 6          # unroof_stops: the roof goes after 6 long ticks (any point before the first death, 0.6 x witherTicks)
MAP = 250              # largest vanilla map side


def row(name, ok, worst, limit, cases):
    print("%-16s %s  worst %s  limit %s  cases %d" % (name, "ok  " if ok else "FAIL", worst, limit, cases))
    return ok


# ---------- defs ----------

def load_defs():
    """Every ThingDef in Pyrelands Defs/ by defName -> element (abstract parents by Name too)."""
    by_name, by_parent_name = {}, {}
    for root, _, files in os.walk(DEFS):
        for f in files:
            if not f.endswith(".xml"):
                continue
            try:
                tree = ET.parse(os.path.join(root, f))
            except ET.ParseError:
                continue
            for el in tree.getroot():
                if el.tag != "ThingDef":
                    continue
                dn = el.findtext("defName")
                if dn:
                    by_name[dn.strip()] = el
                if el.get("Name"):
                    by_parent_name[el.get("Name")] = el
    return by_name, by_parent_name


def resolved(el, parents, path):
    """A field through the def's ParentName chain."""
    seen = 0
    while el is not None and seen < 20:
        v = el.findtext(path)
        if v is not None:
            return v.strip()
        el = parents.get(el.get("ParentName") or "")
        seen += 1
    return None


def class_default(cs_text, cls, field):
    m = re.search(r"class\s+%s\b.*?public\s+int\s+%s\s*=\s*(\d+)" % (cls, field), cs_text, re.S)
    return int(m.group(1)) if m else None


def wither_plants(by_name, parents, cs_text):
    """[(defName, maxHp, witherTicks, remainsDef)] for each def whose comps carry the wither comp."""
    out = []
    for dn, el in sorted(by_name.items()):
        for li in el.findall("comps/li"):
            if li.get("Class") == COMP_CLASS:
                wt = li.findtext("witherTicks")
                wt = int(wt) if wt else class_default(cs_text, "CompProperties_WithersUnderRoof", "witherTicks")
                hp = resolved(el, parents, "statBases/MaxHitPoints")
                rem = li.findtext("remainsDef")
                out.append((dn, int(float(hp)) if hp else None, wt, rem.strip() if rem else None))
    return out


def dead_grass_numbers(by_name, parents, cs, plants):
    """(crumbleTicks, MaxHitPoints) of the remains def the first plant names: crumbleTicks from its RM_DeadGrassExtension,
    else the extension class's default in the .cs; (None, None) when there are no remains to read."""
    rem = next((p[3] for p in plants if p[3]), None)
    el = by_name.get(rem) if rem else None
    if el is None:
        return None, None
    ct = None
    for li in el.findall("modExtensions/li"):
        if (li.get("Class") or "").endswith("RM_DeadGrassExtension") and li.findtext("crumbleTicks"):
            ct = int(li.findtext("crumbleTicks"))
    if ct is None:
        ct = class_default(cs, "RM_DeadGrassExtension", "crumbleTicks")
    hp = resolved(el, parents, "statBases/MaxHitPoints")
    return ct, int(float(hp)) if hp else None


# ---------- the shipped kernel ----------

def build():
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="PyrelandsRoofWitherSelfTest", extra_dirs=[os.path.join(PYR, "Kernel")])
    if rc:
        return None
    return winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakePyrelands.RoofWither.dll"


def run_kernel(dll, lines):
    """lines -> [trace per input line], trace = [(k, stage, damage, lethal, hp)], from the shipped kernel."""
    res = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], cwd="/mnt/d/Luke/dev", input="\n".join(lines) + "\n",
                                        capture_output=True, text=True, timeout=300)
    if res.returncode != 0:
        raise SystemExit("kernel driver failed rc %s: %s" % (res.returncode, (res.stderr or "")[-400:]))
    out, end = [[] for _ in lines], None
    for ln in res.stdout.splitlines():
        f = ln.split()
        if not f:
            continue
        if f[0] == "END":
            end = int(f[1])
            continue
        idx, k, st, dmg, leth, hp = (int(v) for v in f)
        out[idx].append((k, st, dmg, leth, hp))
    if end != len(lines):
        raise SystemExit("kernel driver read %s plants of %d" % (end, len(lines)))
    return out


# ---------- patches ----------

def patch_cells(rng, shape):
    if shape == "rect":
        x0, z0 = rng.randrange(0, MAP - 20), rng.randrange(0, MAP - 10)
        return [(x0 + i % 20, z0 + i // 20) for i in range(PATCH)]
    if shape == "line":
        z0 = rng.randrange(0, MAP)
        x0 = rng.randrange(0, MAP - PATCH) if MAP > PATCH else 0
        return [(x0 + i, z0) for i in range(PATCH)]
    cells = set()
    while len(cells) < PATCH:
        cells.add((rng.randrange(MAP), rng.randrange(MAP)))
    return sorted(cells)


def patch_ids(rng, ids):
    base = rng.randrange(1000, 2000000)
    if ids == "consecutive":
        return [base + i for i in range(PATCH)]
    stride = rng.randrange(2, 400)
    return [base + i * stride for i in range(PATCH)]


def patches(seeds):
    for seed in range(seeds):
        for shape in ("rect", "line", "scatter"):
            for ids in ("consecutive", "strided"):
                rng = random.Random("%d-%s-%s" % (seed, shape, ids))
                yield (seed, shape, ids), list(zip(patch_ids(rng, ids), patch_cells(rng, shape)))


def death_ticks(trace):
    """Roofed ticks at the lethal step, or None."""
    for k, st, dmg, leth, hp in trace:
        if leth:
            return (k + 1) * LONG
    return None


def share_and_window(deaths):
    from collections import Counter
    c = Counter(deaths)
    share = max(c.values()) / float(len(deaths))
    s = sorted(deaths)
    lo, hi = s[int(0.05 * (len(s) - 1))], s[int(0.95 * (len(s) - 1))]
    return share, hi - lo


def main(argv):
    seeds = 40
    if "--seeds" in argv:
        seeds = int(argv[argv.index("--seeds") + 1])
    with open(COMP, encoding="utf-8") as f:
        cs = f.read()
    by_name, parents = load_defs()
    plants = wither_plants(by_name, parents, cs)
    ok = row("plants", len(plants) >= 2 and all(p[1] and p[2] for p in plants), "%d defs: %s" % (len(plants), ", ".join(
        "%s %sHP %st" % (p[0], p[1], p[2]) for p in plants)), ">=2 with HP and witherTicks", len(plants))
    if not ok:
        print("FAIL (no plants read)")
        return 1
    crumble_ticks, dead_hp = dead_grass_numbers(by_name, parents, cs, plants)
    dll = build()
    if not dll:
        print("selftest build FAILED")
        return 1

    # ---- one batch of every case: (case key, driver line) ----
    work = []
    for dn, hp, wt, rem in plants:
        steps = int(1.6 * wt / LONG) + 2
        for pkey, pl in patches(seeds):
            for pid, (x, z) in pl:
                work.append((("roofed", dn, pkey), "W %d %d %d %d %d %d 1 0 %d %d" % (pid, x, z, hp, hp, wt, steps, steps)))
        for kind, gate, frm, until, hp0 in (("unroofed", 1, 0, 0, hp), ("gate_off", 0, 0, steps, hp),
                                            ("unroof_stops", 1, 0, UNROOF_AT, hp), ("one_hp", 1, 0, steps, 1)):
            for pkey, pl in patches(max(1, seeds // 8)):
                for pid, (x, z) in pl:
                    work.append(((kind, dn, pkey), "W %d %d %d %d %d %d %d %d %d %d" % (pid, x, z, hp, hp0, wt, gate, frm, until, steps)))
    if crumble_ticks and dead_hp:
        csteps = int(1.6 * crumble_ticks / LONG) + 2
        for pkey, pl in patches(max(1, seeds // 4)):
            for pid, (x, z) in pl:
                work.append((("crumble", "dead", pkey), "C %d %d %d %d %d %d %d" % (pid, x, z, dead_hp, dead_hp, crumble_ticks, csteps)))
    # the floor sweep: witherTicks below and above the shipped one, ember-grass HP, 4 seeds
    sweep = (10000, 20000, 30000, 40000, 50000, 60000, 120000, 600000)
    for wt in sweep:
        steps = int(1.6 * wt / LONG) + 2
        for pkey, pl in patches(4):
            for pid, (x, z) in pl:
                work.append((("sweep", wt, pkey), "W %d %d %d %d %d %d 1 0 %d %d" % (pid, x, z, plants[0][1], plants[0][1], wt, steps, steps)))
    traces = run_kernel(dll, [ln for _, ln in work])
    by_case = {}
    for (key, _), tr in zip(work, traces):
        by_case.setdefault(key, []).append(tr)
    return report(by_case, plants, crumble_ticks, cs, by_name, parents, sweep)


def body_of(cs, signature):
    """The brace-matched body of the first method whose header matches signature (a regex), or None."""
    m = re.search(signature, cs)
    if not m:
        return None
    i = cs.index("{", m.end())
    depth = 0
    for j in range(i, len(cs)):
        if cs[j] == "{":
            depth += 1
        elif cs[j] == "}":
            depth -= 1
            if depth == 0:
                return cs[i:j + 1]
    return None


def report(by_case, plants, crumble_ticks, cs, by_name, parents, sweep):
    ok = True
    kinds = {}
    for key, trs in by_case.items():
        kinds.setdefault(key[0], []).append((key, trs))

    # rising
    bad, n = 0, 0
    for key, trs in kinds.get("roofed", []):
        for tr in trs:
            n += 1
            st = [t[1] for t in tr]
            if any(b < a for a, b in zip(st, st[1:])) or not ({1, 2} <= set(st)) or not st or st[-1] != 3:
                bad += 1
    ok &= row("rising", n and bad == 0, "%d plants fall, skip a stage or never die" % bad, 0, n)

    # spread per patch, per def
    worst_share, worst_window, worst_key, n = 0.0, None, None, 0
    late, nd = 0, 0
    for key, trs in kinds.get("roofed", []):
        dn = key[1]
        wt = [p[2] for p in plants if p[0] == dn][0]
        deaths = [death_ticks(tr) for tr in trs]
        nd += len(deaths)
        late += sum(1 for d in deaths if d is None or d > 1.4 * wt + LONG)
        deaths = [d for d in deaths if d is not None]
        if not deaths:
            worst_share, worst_window, worst_key = 1.0, 0, key
            continue
        share, window = share_and_window(deaths)
        n += 1
        if share > worst_share:
            worst_share, worst_key = share, key
        if worst_window is None or window < worst_window:
            worst_window = window
    ok &= row("spread_share", n and worst_share <= SHARE_MAX, "%.3f (%s)" % (worst_share, worst_key), SHARE_MAX, n)
    ok &= row("spread_window", n and worst_window is not None and worst_window >= WINDOW_MIN_TICKS, "%s ticks" % worst_window,
              ">= %d" % WINDOW_MIN_TICKS, n)
    ok &= row("all_die", nd and late == 0, "%d plants alive or late past 1.4 x witherTicks + %d" % (late, LONG), 0, nd)

    # one hp
    bad, n = 0, 0
    for key, trs in kinds.get("one_hp", []):
        for tr in trs:
            n += 1
            if not tr or tr[0][3] != 1:
                bad += 1
    ok &= row("one_hp", n and bad == 0, "%d 1-HP plants alive after their first roofed long tick" % bad, 0, n)

    for kind, after in (("unroofed", 0), ("gate_off", 0), ("unroof_stops", UNROOF_AT)):
        worst_st, worst_dmg, n = 0, 0, 0
        for key, trs in kinds.get(kind, []):
            for tr in trs:
                n += 1
                tail = [t for t in tr if t[0] >= after]
                if kind != "unroof_stops":
                    worst_st = max([worst_st] + [t[1] for t in tail])
                worst_dmg = max([worst_dmg] + [t[2] for t in tail] + [99 for t in tail if t[3]])
        ok &= row(kind, n and worst_st == 0 and worst_dmg == 0, "stage %d, damage %d%s" % (
            worst_st, worst_dmg, " after long tick %d" % after if after else ""), "0, 0", n)

    # remains
    problems, n = [], 0
    for dn, hp, wt, rem in plants:
        n += 1
        el = by_name.get(rem) if rem else None
        if el is None:
            problems.append("%s: remainsDef %r is no ThingDef of ours" % (dn, rem))
            continue
        tc = resolved(el, parents, "thingClass") or ""
        label = (resolved(el, parents, "label") or "").lower()
        if tc not in ("DeadPlant", "RimWorld.DeadPlant") and not re.search(r"class\s+%s\s*:\s*DeadPlant\b" % re.escape(tc.split(".")[-1]), cs):
            problems.append("%s: %s thingClass %r is no DeadPlant" % (dn, rem, tc))
        if "dead" not in label or "grass" not in label:
            problems.append("%s: %s label %r does not read dead grass" % (dn, rem, label))
    deaths = sum(1 for key, trs in kinds.get("roofed", []) for tr in trs if death_ticks(tr) is not None)
    ok &= row("remains", n and not problems, "; ".join(problems) or "%d deaths, each names %s" % (
        deaths, sorted({p[3] for p in plants})), "every def names a dead-grass DeadPlant", n)

    # crumble
    if crumble_ticks:
        worst_share, late, n, nd = 0.0, 0, 0, 0
        for key, trs in kinds.get("crumble", []):
            deaths = [death_ticks(tr) for tr in trs]
            nd += len(deaths)
            late += sum(1 for d in deaths if d is None or d > 1.4 * crumble_ticks + LONG)
            deaths = [d for d in deaths if d is not None]
            n += 1
            if deaths:
                worst_share = max(worst_share, share_and_window(deaths)[0])
        ok &= row("crumble", nd and late == 0 and worst_share <= SHARE_MAX, "share %.3f, %d late (crumbleTicks %d)" % (
            worst_share, late, crumble_ticks), "share <= %s, 0 late" % SHARE_MAX, nd)
    else:
        ok &= row("crumble", False, "no crumbleTicks default found in CompWithersUnderRoof.cs", "a dead-grass crumble clock", 0)

    # floor: the sweep map, then the shipped witherTicks against the floor
    print("sweep (witherTicks -> worst share over 4 seeds x 6 patch kinds; informs WITHER_FLOOR_TICKS):")
    for wt in sweep:
        worst = 0.0
        for key, trs in kinds.get("sweep", []):
            if key[1] != wt:
                continue
            deaths = [d for d in (death_ticks(tr) for tr in trs) if d is not None]
            worst = max(worst, share_and_window(deaths)[0] if deaths else 1.0)
        print("  %7d  %.3f  %s" % (wt, worst, "holds" if worst <= SHARE_MAX else "breaks"))
    low = min(p[2] for p in plants)
    ok &= row("floor", low >= WITHER_FLOOR_TICKS, "shipped witherTicks min %d" % low, ">= %d" % WITHER_FLOOR_TICKS, len(plants))

    # no kill in the plant's tick
    problems = []
    tick = body_of(cs, r"override\s+void\s+CompTickLong\s*\(")
    if tick is None:
        problems.append("no CompTickLong")
    else:
        if "RM_RoofWitherKernel.Advance" not in tick:
            problems.append("CompTickLong does not call RM_RoofWitherKernel.Advance")
        for bad in (".Kill(", ".Destroy(", "GenSpawn.Spawn("):
            if bad in tick:
                problems.append("CompTickLong calls %s" % bad)
        if "Lethal" not in tick or ".Queue(" not in tick:
            problems.append("CompTickLong does not queue its lethal step")
    mtick = body_of(cs, r"override\s+void\s+MapComponentTick\s*\(")
    if mtick is None:
        problems.append("no MapComponentTick")
    else:
        if ".Kill(" not in mtick and "KillAndLeaveRemains(" not in mtick:
            problems.append("MapComponentTick kills nothing")
    kr = body_of(cs, r"void\s+KillAndLeaveRemains\s*\(")
    if kr is None or ".Kill(" not in kr or "GenSpawn.Spawn(" not in kr or "remains" not in kr:
        problems.append("KillAndLeaveRemains does not kill and spawn the remains")
    ok &= row("no_kill_in_tick", not problems, "; ".join(problems) or "tick queues, map component kills and spawns", 0, 3)

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
