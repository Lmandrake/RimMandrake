#!/usr/bin/env python3
"""Mutation proof for the RaidRedesigner fuzz: plants each defect in the roster kernel (RM_RosterKernel.cs), demands the fuzz FAILS,
restores the file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_raidredesigner_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/RaidRedesigner/Source/Kernel/RM_RosterKernel.cs"
MUTATIONS = [
    ("grudge upper clamp 101", "public const int GrudgeMin = -100, GrudgeMax = 100,", "public const int GrudgeMin = -100, GrudgeMax = 101,"),
    ("notability floor -1", "NotabilityMin = 0, NotabilityMax = 100;", "NotabilityMin = -1, NotabilityMax = 100;"),
    ("clamp ignores the lower bound", "if (value < min) return min;\n            if (value > max) return max;", "if (value > max) return max;"),
    ("clamp ignores the upper bound", "if (value < min) return min;\n            if (value > max) return max;", "if (value < min) return min;"),
    ("delta rounds instead of truncating", "return (int)(delta * multiplier);", "return (int)Math.Round(delta * multiplier);"),
    ("delta ignores the multiplier", "return (int)(delta * multiplier);", "return delta;"),
    ("grudge uses the notability bounds", "return Clamp(grudge + ScaledDelta(delta, multiplier), GrudgeMin, GrudgeMax);", "return Clamp(grudge + ScaledDelta(delta, multiplier), NotabilityMin, NotabilityMax);"),
    ("notability replaces instead of adds", "return Clamp(notability + ScaledDelta(delta, multiplier), NotabilityMin, NotabilityMax);", "return Clamp(ScaledDelta(delta, multiplier), NotabilityMin, NotabilityMax);"),
    ("prune counts dead entries", "var living = entries.Where(e => e != null && !e.Dead).ToList();", "var living = entries.Where(e => e != null).ToList();"),
    ("prune keeps the lowest notability", "living.OrderBy(e => e.Notability).ThenBy(e => e.LastSeenTick)", "living.OrderByDescending(e => e.Notability).ThenBy(e => e.LastSeenTick)"),
    ("tie keeps the stalest", "OrderBy(e => e.Notability).ThenBy(e => e.LastSeenTick).Take(overflow)", "OrderBy(e => e.Notability).ThenByDescending(e => e.LastSeenTick).Take(overflow)"),
    ("prune one too few", "int overflow = living.Count - cap;", "int overflow = living.Count - cap - 1;"),
    ("prune one too many", "int overflow = living.Count - cap;", "int overflow = living.Count - cap + 1;"),
    ("find matches dead entries", "entries.Find(e => !e.Dead && isThePawn(e));", "entries.Find(e => isThePawn(e));"),
    ("role downgraded by any later tag", "else if (role == RoleTag.Captain)\n            {\n                entry.Role = RoleTag.Captain;", "else\n            {\n                entry.Role = role;"),
    ("role never upgrades", "else if (role == RoleTag.Captain)", "else if (false)"),
    ("encounter not recorded", "entry.NoteEncounter(tick, role, summary);", ""),
    ("grudge not applied", "entry.Grudge = NextGrudge(entry.Grudge, grudgeDelta, multiplier);", ""),
    ("notability uses the grudge delta", "NextNotability(entry.Notability, notabilityDelta, multiplier)", "NextNotability(entry.Notability, grudgeDelta, multiplier)"),
    ("cap enforced on every record", "            if (outcome.IsNew)\n            {\n                outcome.Victims", "            if (true)\n            {\n                outcome.Victims"),
    ("cap enforced before the deltas", "entry.NoteEncounter(tick, role, summary);\n            entry.Grudge", "if (outcome.IsNew) { foreach (T v in SelectPruneVictims(entries, cap)) entries.Remove(v); }\n            entry.NoteEncounter(tick, role, summary);\n            entry.Grudge"),
    ("victims not removed", "                    entries.Remove(victim);\n", ""),
    ("self eviction not reported", "if (ReferenceEquals(victim, entry)) outcome.EvictedSelf = true;", ""),
    ("self eviction always reported", "if (ReferenceEquals(victim, entry)) outcome.EvictedSelf = true;", "outcome.EvictedSelf = true;"),
    ("dead pawn not collapsed", "return pawnDead ? SweepVerdict.Died : SweepVerdict.Alive;", "return SweepVerdict.Alive;"),
    ("lost pawn stays alive", "if (pawnIsNull) return SweepVerdict.Lost;", ""),
    ("dead entry swept again", "if (entryDead) return SweepVerdict.Alive;", ""),
    ("summary drops the cause", '+ ") — " + cause;', '+ ")";'),
    ("a pin someone else placed is claimed", "return alreadyOurs || (!keptBeforeThisCall && keptAfterThisCall);", "return alreadyOurs || keptAfterThisCall;"),
    ("a pin we placed is forgotten", "return alreadyOurs || (!keptBeforeThisCall && keptAfterThisCall);", "return !keptBeforeThisCall && keptAfterThisCall;"),
    ("a faction leader is unpinned", "return pinnedByUs && !leadsAFaction;", "return pinnedByUs;"),
    ("a foreign pin is released", "return pinnedByUs && !leadsAFaction;", "return !leadsAFaction;"),
    ("summary drops the grudge", '", grudge " + grudge + ", notability "', '", notability "'),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_raidredesigner_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
