#!/usr/bin/env python3
"""Mutation proof for the JawaRules fuzz: plants each defect in the kernel (RSW_JawaRulesKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_jawarules_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimStarWars/JawaRules/Source/Kernel/RSW_JawaRulesKernel.cs"
MUTATIONS = [
    ("hood: swim rule ignores the setting", "return enabled && swimming && !portrait;", "return swimming && !portrait;"),
    ("hood: swim rule outside the water", "return enabled && swimming && !portrait;", "return enabled && !portrait;"),
    ("hood: swim rule on portraits", "return enabled && swimming && !portrait;", "return enabled && swimming;"),
    ("hood: only headgear put back", "public const int Headgear = 0x20, Clothes = 0x40, ApparelFlags = Headgear | Clothes;", "public const int Headgear = 0x20, Clothes = 0x40, ApparelFlags = Headgear;"),
    ("hood: flags put back always", "return applies ? flags | ApparelFlags : flags;", "return flags | ApparelFlags;"),
    ("hood: flags replaced not added", "return applies ? flags | ApparelFlags : flags;", "return applies ? ApparelFlags : flags;"),
    ("hood: wrong clothes bit", "public const int Headgear = 0x20, Clothes = 0x40,", "public const int Headgear = 0x20, Clothes = 0x10,"),
    ("hood: re-asks after vanilla said yes", "if (vanillaResult || reentry) return vanillaResult;", "if (reentry) return vanillaResult;"),
    ("hood: re-asks inside its own re-ask", "if (vanillaResult || reentry) return vanillaResult;", "if (vanillaResult) return vanillaResult;"),
    ("hood: re-asks outside the swim rule", "if (!applies || !keptHood) return vanillaResult;", "if (!keptHood) return vanillaResult;"),
    ("hood: re-asks every hat", "if (!applies || !keptHood) return vanillaResult;", "if (!applies) return vanillaResult;"),
    ("hood: re-asks with the old flags", "return askAgain(EffectiveFlags(flags, applies));", "return askAgain(flags);"),
    ("hood: keeps the hood without asking", "return askAgain(EffectiveFlags(flags, applies));", "return true;"),
    ("hood: ignores the answer", "return askAgain(EffectiveFlags(flags, applies));", "askAgain(EffectiveFlags(flags, applies)); return false;"),
    ("hood: real hood ignores visibility", "if (!headgearVisible(EffectiveFlags(flags, applies))) return false;", ""),
    ("hood: visibility on the raw flags", "if (!headgearVisible(EffectiveFlags(flags, applies))) return false;", "if (!headgearVisible(flags)) return false;"),
    ("hood: not worn still counts", "return wearsHood();", "return true;"),
    ("hood: no tracker still counts", "if (!hasApparelTracker) return false;", ""),
    ("hood: unresolved def still counts", "if (!hoodDefResolved) return false;", ""),
    ("hood: fallback ignores its base gates", "if (!baseCanDraw) return false;", ""),
    ("hood: fallback and hood both draw", "try { return !realHoodDrawing(); }", "try { return true; }"),
    ("hood: fallback never draws", "try { return !realHoodDrawing(); }", "try { return false; }"),
    ("hood: fallback fails closed", "catch (Exception) { return true; }", "catch (Exception) { return false; }"),
    ("hood: fallback lets the guard throw", "try { return !realHoodDrawing(); }\n            catch (Exception) { return true; }", "return !realHoodDrawing();"),
    ("rules: Jawa match is case-insensitive", "return hasGenes && hasXenotype && xenotypeDefName == jawaXenotype;", "return hasGenes && hasXenotype && string.Equals(xenotypeDefName, jawaXenotype, StringComparison.OrdinalIgnoreCase);"),
    ("rules: Jawa match needs no genes", "return hasGenes && hasXenotype && xenotypeDefName == jawaXenotype;", "return hasXenotype && xenotypeDefName == jawaXenotype;"),
    ("rules: Jawa match by prefix", "return hasGenes && hasXenotype && xenotypeDefName == jawaXenotype;", "return hasGenes && hasXenotype && xenotypeDefName != null && xenotypeDefName.StartsWith(\"RSW_\");"),
    ("rules: sow ban ignores the setting", "return enabled && vanillaResult && isJawa() ? false : vanillaResult;", "return vanillaResult && isJawa() ? false : vanillaResult;"),
    ("rules: sow ban for everyone", "return enabled && vanillaResult && isJawa() ? false : vanillaResult;", "return enabled ? false : vanillaResult;"),
    ("rules: sow ban reads the xenotype eagerly", "return enabled && vanillaResult && isJawa() ? false : vanillaResult;", "return enabled && isJawa() && vanillaResult ? false : vanillaResult;"),
    ("rules: sow ban grants sowing", "return enabled && vanillaResult && isJawa() ? false : vanillaResult;", "return enabled && isJawa() ? !vanillaResult : vanillaResult;"),
    ("rules: tracker for animals", "return enabled && hasRaceProps && humanlike && !hasTracker;", "return enabled && hasRaceProps && !hasTracker;"),
    ("rules: tracker replaces an existing one", "return enabled && hasRaceProps && humanlike && !hasTracker;", "return enabled && hasRaceProps && humanlike;"),
    ("rules: tracker ignores the setting", "return enabled && hasRaceProps && humanlike && !hasTracker;", "return hasRaceProps && humanlike && !hasTracker;"),
    ("rules: names everything", "if (!enabled || !hasRaceProps || !animal) return false;", "if (!enabled || !hasRaceProps) return false;"),
    ("rules: names wild animals", "if (!hasFaction || !playerFaction) return false;", "if (!playerFaction) return false;"),
    ("rules: names other factions' animals", "if (!hasFaction || !playerFaction) return false;", "if (!hasFaction) return false;"),
    ("rules: renames a chosen name", "if (hasName && !nameNumerical) return false;", ""),
    ("rules: leaves placeholder names", "if (hasName && !nameNumerical) return false;", "if (hasName) return false;"),
    ("rules: pet names ignore the setting", "if (!enabled || !hasRaceProps || !animal) return false;", "if (!hasRaceProps || !animal) return false;"),
    ("rules: re-kinds a matching pawn", "return enabled && hasPawn && hasRequestKind && kindDiffers;", "return enabled && hasPawn && hasRequestKind;"),
    ("rules: re-kinds with no request", "return enabled && hasPawn && hasRequestKind && kindDiffers;", "return enabled && hasPawn && kindDiffers;"),
    ("rules: re-kind ignores the setting", "return enabled && hasPawn && hasRequestKind && kindDiffers;", "return hasPawn && hasRequestKind && kindDiffers;"),
    ("rules: xenotype without Biotech", "return biotech && hasGenes && usesFactionXenotypes && wantedExists && differs;", "return hasGenes && usesFactionXenotypes && wantedExists && differs;"),
    ("rules: xenotype to nothing", "return biotech && hasGenes && usesFactionXenotypes && wantedExists && differs;", "return biotech && hasGenes && usesFactionXenotypes && differs;"),
    ("rules: xenotype for kinds that do not use factions", "return biotech && hasGenes && usesFactionXenotypes && wantedExists && differs;", "return biotech && hasGenes && wantedExists && differs;"),
    ("rules: xenotype re-set when equal", "return biotech && hasGenes && usesFactionXenotypes && wantedExists && differs;", "return biotech && hasGenes && usesFactionXenotypes && wantedExists;"),
    ("rules: world label value inverted", "return boostEnabled ? wanted : vanilla;", "return boostEnabled ? vanilla : wanted;"),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(run_mutations(KERNEL, "selftest_jawarules_fuzz.py", MUTATIONS, only))
