#!/usr/bin/env python3
"""T_BURROW_BEATS_DASH: an ashwallow beside a fire dives, whatever else would move it first (bar ashwallow_dives_unharmed).

Why it exists (RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE, visit 2, 2026-11-20): a wild ashwallow 3 cells
from a fresh fire took RM_ShadeDash (noon) or a shade-patch Wait (night), left its 6-cell dive radius, and never dived.
Three causes, each read here from the SHIPPED artifacts, never from a copy:
  1. order    the burrow giver sat at Animal_PreWander 56. CreatureBehaviors' sun escape (Animal_PreMain 10) and FlowWorks'
              animal drink (Animal_PreMain 100) are asked before it, so a pawn in the sun, or thirsty, walked off first.
  2. lag      WouldDive gated on MapComponent_BurnLine.AnyBurn, which is measured every BurnWatchIntervalTicks (60). On a
              map's first fire the first think pass saw no burn, gave a move (a shade hop to its rim), and the pawn was
              out of range before the flag turned on.
  3. nudge    the burn line's dive nudge re-asks idling burrowers and starts the dive outright over grazing and sleep. A
              burrower mid RM_ShadeDash (or walking to drink) was left alone and finished its move out of range.

The range of situations (what the game varies for this bar, all enumerated, 2 x 3 x 2 x 9 = 108 cases):
  burn      cold (the map's first fire: the burn line has not measured it yet) | warm (a burn already measured)
  light     sun (the pawn in open sun) | shade (in a shade patch, by day) | night
  thirst    thirsty (FlowWorks drink giver fires) | not
  onset     what the pawn is doing when the fire comes inside its radius: a fresh think pass (no job), GotoWander, Wait,
            Wait_Wander, Ingest, LayDown, RM_ShadeDash, RM_DrinkFromTerrain, Wait_MaintainPosture
Left out, and why: Flee from fire (RM_BurrowHeatReaction answers it; its own table is in PyrelandsFuzz), mental states,
roped or tamed pawns (vanilla nodes above Animal_PreMain own them), settings off (the bar is the shipped default; the
settings sweep owns the off cases), the burrow timeout cooldown (BurrowMayStart, fuzzed in PyrelandsFuzz).
The control: with no fire near, the sun escape still wins in the sun (criterion 2: the sun mechanic is not lost).

The model of one case: the first think pass (at onset with no job, or when the nudge re-asks the tree) gives the job of
the first giver in tree order whose condition holds; the burrow giver's condition is "fire near" when warm, and when cold
only if its gate reads the live fire list. A job the nudge dives over outright dives at the next watch interval; a job it
re-asks resolves as a warm think pass; any other job is a move the pawn finishes out of range: no dive.
What this proves and what it does not: it reads the think order, the dive gate and the nudge's job sets that ship, and
runs them through that model. It does not run the game: the nudge's 60-tick cadence (a dash or walk already under way when
a map's first fire lights runs up to one watch interval before the dive) and the pawn's real path are Stage 6's live row
(sc_ashwallow, chain burrowers). Two wiring rows make the model honest: the dive stays scoped to a Pyrelands map (the old
AnyBurn gate also did that: the burn line never measures another biome), and the burn line's nudge calls the kernel sets.
The worst row prints the failing cases; --old <git-ref> runs the same table on an older build (the planted fault).

    python3 src/RimMandrake/Pyrelands/selftest_pyrelands_burrow_beats_dash.py [--old <git-ref>]
"""
import argparse
import glob
import itertools
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(SRC))
GIVER = "src/RimMandrake/Pyrelands/Source/RM_JobGiver_BurrowOnFire.cs"
KERNEL = "src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs"
BURNLINE = "src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs"

# Vanilla Animal ThinkTreeDef (RimSage get_def_details Animal, raw, read 2026-11-21): the Animal_PreMain splice comes
# after LordDuty and before SatisfyBasicNeeds; Animal_PreWander comes after SatisfyBasicNeeds. ThinkNode_SubtreesByTag
# orders the trees of one tag by insertPriority, highest first (RimSage read_csharp_symbol ThinkNode_SubtreesByTag).
TAG_ORDER = ["Animal_PreMain", "Animal_PreWander"]
BURROW = "RimMandrake.Pyrelands.RM_JobGiver_BurrowOnFire"
# The givers that hand a wild Pyrelands animal a move with no regard for fire, and when each fires in this model.
RIVALS = {
    "RimMandrake.CreatureBehaviors.RM_JobGiver_SunEscape": ("sun", "RM_ShadeDash"),
    "RimMandrake.FlowWorks.Thirst.JobGiver_RM_AnimalDrink": ("thirsty", "RM_DrinkFromTerrain"),
    "RimMandrake.CreatureBehaviors.RM_JobGiver_ShadeHop": ("shade_or_night", "RM_ShadeDash"),
}
ONSETS = [None, "GotoWander", "Wait", "Wait_Wander", "Ingest", "LayDown", "RM_ShadeDash", "RM_DrinkFromTerrain",
          "Wait_MaintainPosture"]

rows = []


def row(name, ok, worst, limit, sampled):
    rows.append(ok)
    print("%-4s %-30s worst %-44s must %-40s | %s" % ("ok" if ok else "FAIL", name, worst, limit, sampled))


class Tree:
    """The repo's files at the working tree, or at a git ref (--old)."""

    def __init__(self, ref=None):
        self.ref = ref

    def read(self, rel):
        if self.ref is None:
            p = os.path.join(REPO, rel)
            return open(p, encoding="utf-8").read() if os.path.exists(p) else None
        r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (self.ref, rel)], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None

    def defs_files(self):
        if self.ref is None:
            return sorted(os.path.relpath(p, REPO) for p in glob.glob(os.path.join(SRC, "*", "Defs", "**", "*.xml"),
                                                                         recursive=True))
        r = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", self.ref, "src/RimMandrake/"],
                           capture_output=True, text=True, check=True)
        return sorted(p for p in r.stdout.split() if re.match(r"src/RimMandrake/[^/]+/Defs/.*\.xml$", p))


def think_order(tree):
    """[(tag index, -priority, defName, [giver classes])] for every Animal_PreMain/PreWander insert in the repo's mods."""
    out = []
    for rel in tree.defs_files():
        text = tree.read(rel)
        if not text or "insertTag" not in text:
            continue
        try:
            root = ET.fromstring(text.encode("utf-8"))
        except ET.ParseError:
            continue
        for td in root.iter("ThinkTreeDef"):
            tag = (td.findtext("insertTag") or "").strip()
            if tag not in TAG_ORDER:
                continue
            prio = float((td.findtext("insertPriority") or "0").strip())
            givers = [li.get("Class") for li in td.iter() if li.get("Class")]
            out.append((TAG_ORDER.index(tag), -prio, (td.findtext("defName") or "").strip(), givers, rel))
    return sorted(out, key=lambda e: (e[0], e[1]))


def position(order, cls):
    for i, e in enumerate(order):
        if cls in e[3]:
            return i, e
    return None, None


def method_body(text, name):
    m = re.search(r"\b%s\s*\([^)]*\)\s*\{" % re.escape(name), text or "")
    if not m:
        return None
    depth, i = 1, m.end()
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[m.end():i - 1]


def nudge_sets(tree):
    """(re-ask set, dive-outright set) the burn line's nudge uses: the kernel's named lists, else the old JobDefOf tests."""
    kern = method_body(tree.read(KERNEL), "BurrowerNudgeKind")
    if kern is not None:
        reask = method_body(tree.read(KERNEL), "BurrowerReasksOver")
        dive = method_body(tree.read(KERNEL), "BurrowerDivesOver")
        return (set(re.findall(r'"(\w+)"', reask or "")), set(re.findall(r'"(\w+)"', dive or "")))
    bl = tree.read(BURNLINE) or ""
    return (set(re.findall(r"JobDefOf\.(\w+)", method_body(bl, "IsIdleJob") or "")),
            set(re.findall(r"JobDefOf\.(\w+)", method_body(bl, "YieldsToFire") or "")))


def gate_is_live(tree):
    """WouldDive's fire precondition reads the live fire list, not the burn line's interval-measured AnyBurn."""
    body = method_body(tree.read(GIVER), "WouldDive")
    if body is None:
        return None
    code = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", body, flags=re.S))   # code only: a comment may name the flag
    return not re.search(r"\bAnyBurn\b", code)


def think(order, case, fire_seen):
    """The job the first firing giver hands out, or 'RM_Burrow'; None when only vanilla wander is left."""
    burn, light, thirsty = case
    for _, _, _, givers, _ in order:
        for g in givers:
            if g == BURROW and fire_seen:
                return "RM_Burrow"
            if g in RIVALS:
                cond, job = RIVALS[g]
                if (cond == "sun" and light == "sun") or (cond == "thirsty" and thirsty) or \
                        (cond == "shade_or_night" and light != "sun"):
                    return job
    return "GotoWander"   # vanilla wander after Animal_PreWander


def outcome(order, live_gate, reask, dive, case, onset):
    burn = case[0]
    job = onset if onset is not None else think(order, case, fire_seen=(burn == "warm" or live_gate))
    for _ in range(2):   # the nudge acts at the next watch interval; a re-ask is one more (warm) think pass
        if job == "RM_Burrow" or job in dive:
            return "dive"
        if job in reask:
            job = think(order, case, fire_seen=True)
            continue
        return "moved off as %s" % job
    return "dive" if job == "RM_Burrow" or job in dive else "moved off as %s" % job


def run(tree, label):
    order = think_order(tree)
    pb, eb = position(order, BURROW)
    if pb is None:
        row("order " + label, False, "no ThinkTreeDef holds %s" % BURROW, "an Animal_PreMain/PreWander insert", "")
        return False
    worst, rivals_read = None, 0
    for cls in RIVALS:
        pr, er = position(order, cls)
        if pr is None:
            continue
        rivals_read += 1
        tie = er[0] == eb[0] and er[1] == eb[1]
        if pr < pb or tie:
            worst = "%s %s %g before %s %s %g%s" % (er[2], TAG_ORDER[er[0]], -er[1], eb[2], TAG_ORDER[eb[0]], -eb[1],
                                                     " (tie)" if tie else "")
    row("order " + label, worst is None and rivals_read == len(RIVALS),
        worst or "%s at %s %g, first of %d rivals" % (eb[2], TAG_ORDER[eb[0]], -eb[1], rivals_read),
        "burrow giver asked before every rival", "%d inserts read, %d of %d rivals found" % (len(order), rivals_read, len(RIVALS)))

    live = gate_is_live(tree)
    row("gate " + label, live is True, "WouldDive reads %s" % ("the live fire list" if live else "AnyBurn (60-tick measure)"
                                                              if live is False else "nothing: method not found"),
        "no interval-measured flag in the dive gate", GIVER)

    gbody = method_body(tree.read(GIVER), "WouldDive") or ""
    gcode = re.sub(r"//[^\n]*", "", gbody)
    scoped = bool(re.search(r"\bIsPyrelandsMap\b|\bAnyBurn\b", gcode))
    row("scope " + label, scoped, "WouldDive %s" % ("asks for a Pyrelands map" if scoped else "dives on any biome's map"),
        "biome mechanics only inside our own biomes", GIVER)
    bl = tree.read(BURNLINE) or ""
    wired = [m for m in ("YieldsToFire", "IsIdleJob") if "BurrowerNudgeKind" in (method_body(bl, m) or "")]
    row("nudge wiring " + label, len(wired) == 2, "%d of 2 burn-line job tests call the kernel sets" % len(wired),
        "YieldsToFire and IsIdleJob read BurrowerNudgeKind", BURNLINE)

    reask, dive = nudge_sets(tree)
    fails, n = [], 0
    for burn, light, thirsty, onset in itertools.product(("cold", "warm"), ("sun", "shade", "night"), (False, True), ONSETS):
        n += 1
        o = outcome(order, bool(live), reask, dive, (burn, light, thirsty), onset)
        if o != "dive":
            fails.append("%s/%s/%s/%s: %s" % (burn, light, "thirsty" if thirsty else "-", onset or "think", o))
    row("regimes " + label, not fails, "%d of %d cases do not dive%s" % (len(fails), n, (": " + fails[0]) if fails else ""),
        "0 cases that do not dive", "%d cases; nudge re-asks %d jobs, dives over %d" % (n, len(reask), len(dive)))
    for f in fails[1:6]:
        print("       also: " + f)

    # Control (criterion 2): no fire near, the ashwallow in the sun still takes the sun escape's dash.
    ctrl = think(order, ("warm", "sun", False), fire_seen=False)
    row("no-fire control " + label, ctrl == "RM_ShadeDash", "in sun, no fire: %s" % ctrl, "RM_ShadeDash", "1 case")
    return all(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", help="git ref of a build known bad: the table must go red on it")
    a = ap.parse_args()
    if a.old:
        run(Tree(a.old), "@" + a.old)
        ok = all(rows)
        print("%s: the table on %s reads %s" % ("RED (as a known-bad build must)" if not ok else "GREEN", a.old,
                                                 "FAIL" if not ok else "PASS"))
        return 0 if not ok else 1
    run(Tree(), "@worktree")
    ok = all(rows)
    print("T_BURROW_BEATS_DASH %s (%d rows)" % ("PASS" if ok else "FAIL", len(rows)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
