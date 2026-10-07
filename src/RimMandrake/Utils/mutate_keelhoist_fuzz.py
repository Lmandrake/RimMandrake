#!/usr/bin/env python3
"""Mutation proof for the KeelHoist fuzz: plants each defect in the kernel (RM_HoistKernel.cs), demands the fuzz FAILS, restores the
file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_keelhoist_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/KeelHoist/Source/Kernel/RM_HoistKernel.cs"
MUTATIONS = [
    ("due test >= instead of >", "return !(i < arriveAt.Count && arriveAt[i] > now);", "return !(i < arriveAt.Count && arriveAt[i] >= now);"),
    ("tick loop skips index 0", "for (int i = sink.TransitCount - 1; i >= 0; i--)\n            {\n                if (!IsDue", "for (int i = sink.TransitCount - 1; i > 0; i--)\n            {\n                if (!IsDue"),
    ("RemoveAt forgets the origin label", "            goingUp.RemoveAt(i);\n            fromLabel.RemoveAt(i);\n        }\n\n        /// <summary>Could not land", "            goingUp.RemoveAt(i);\n        }\n\n        /// <summary>Could not land"),
    ("Defer does nothing", "if (i < arriveAt.Count) arriveAt[i] = until;", ""),
    ("PadTo pads direction with true", "while (goingUp.Count < ownerCount) goingUp.Add(false);", "while (goingUp.Count < ownerCount) goingUp.Add(true);"),
    ("Soonest returns the latest", "if (arriveAt[i] < m) m = arriveAt[i];", "if (arriveAt[i] > m) m = arriveAt[i];"),
    ("ArriveAllNow skips the last", "if (i < sink.TransitCount) sink.ArriveAt(i);", "if (i < sink.TransitCount - 1) sink.ArriveAt(i);"),
    ("cycle floor gone", "return Math.Max(MinCycleTicks, (int)Math.Round(", "return Math.Max(0, (int)Math.Round("),
    ("cycle mass divisor 100", "(1f + mass / 50f)", "(1f + mass / 100f)"),
    ("cycle rounds up", "(int)Math.Round(BaseCycleTicks * cycleTimeMultiplier", "(int)Math.Ceiling(BaseCycleTicks * cycleTimeMultiplier"),
    ("chute keeps what rides UP", "if (!up && handlesBelow) return ArrivalPlan.HandledBelow;", "if (handlesBelow) return ArrivalPlan.HandledBelow;"),
    ("awake colonist lowered into a holder", "return !up && holderSpawned && isPawn && !(isColonist && !downed);", "return !up && holderSpawned && isPawn;"),
    ("manifest cap off by one", "if (list.Count > cap) list.RemoveAt(0);", "if (list.Count >= cap) list.RemoveAt(0);"),
    ("enter refusal order", "if (!masterEnabled) return \"off\";\n            if (!cableDown) return \"cable\";", "if (!cableDown) return \"cable\";\n            if (!masterEnabled) return \"off\";"),
    ("prisoner of ours captured again", "if (prisonerOrSlave || !hasGuest) return CaptureKind.None;", "if (!hasGuest) return CaptureKind.None;"),
    ("owned animal bound", "if (animal && factionless) return CaptureKind.Bound;", "if (animal) return CaptureKind.Bound;"),
    ("cradle lifts any awake stranger", "bool capturable = downed && downedStrangersAndBeasts;", "bool capturable = downedStrangersAndBeasts;"),
    ("dialog lists free colonists at a pit", "if (buyerOrChute && isColonist && !isSlave) return true;", "if (buyerOrChute && isColonist && isSlave) return true;"),
    ("holder accepts a free colonist", "if (isColonist && !isSlave) return \"own\";", "if (isColonist && isSlave) return \"own\";"),
    ("gate inverted", "return !keepersLeft;", "return keepersLeft;"),
    ("pit buys with the gate open", "return hasBuyer && pitSales && factionOther && !hostile && !gateOpen;", "return hasBuyer && pitSales && factionOther && !hostile;"),
    ("fighter bonus without an arena week", "if (fighter && arenaWants) price *= fighterBonus;", "if (fighter || arenaWants) price *= fighterBonus;"),
    ("price floor gone", "return Math.Max(1, (int)Math.Round(price));", "return (int)Math.Round(price);"),
    ("silver stack ignores the amount", "int n = Math.Min(amount, stackLimit);", "int n = stackLimit;"),
    ("a later stake restarts the clock", "return rollAt < 0 ? now + chuteTicks : rollAt;", "return now + chuteTicks;"),
    ("roll due one tick late", "return rollAt >= 0 && now >= rollAt;", "return rollAt >= 0 && now > rollAt;"),
    ("jackpot edge inclusive", "if (r < jackpotChance) return 3f;", "if (r <= jackpotChance) return 3f;"),
    ("bust band ignores the jackpot offset", "if (r < jackpotChance + bustChance) return 0.3f;", "if (r < bustChance) return 0.3f;"),
    ("house takes no cut", "return stake * (1f - houseCut) * multiplier;", "return stake * multiplier;"),
    ("crate silver rounds up", "return (int)Math.Floor(value - gotFromSet);", "return (int)Math.Ceiling(value - gotFromSet);"),
    ("item set threshold exclusive", "return value >= CrateItemSetThreshold;", "return value > CrateItemSetThreshold;"),
    ("open line falls below zero", "return open ? level + OpenLineRisePerHour : Math.Max(0f, level - OpenLineFallPerHour);", "return open ? level + OpenLineRisePerHour : level - OpenLineFallPerHour;"),
    ("open line minute", "public const int OpenLineMinute = 137;", "public const int OpenLineMinute = 0;"),
    ("lowerable: owned animal", "return animal && factionless;\n        }\n\n        /// <summary>Which awake", "return animal;\n        }\n\n        /// <summary>Which awake"),
    ("week is six days", "return ticksGame / (TicksPerDay * 7);", "return ticksGame / (TicksPerDay * 6);"),
    ("fighter skill 9", "return humanlike ? meleeLevel >= MeleeFighterSkill : combatPower >= BeastFighterCombatPower;", "return humanlike ? meleeLevel > MeleeFighterSkill : combatPower >= BeastFighterCombatPower;"),
    ("tether blocks a refused launch", "return accepted && tetherLock && hasMap && defKnown && cableDownOnSubstructure;", "return tetherLock && hasMap && defKnown && cableDownOnSubstructure;"),
    ("reach edge exclusive", "return !(distance > range + portalSizeX);", "return distance < range + portalSizeX;"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_keelhoist_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
