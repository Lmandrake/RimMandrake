#!/usr/bin/env python3
"""Mutation proof for the SeaShores fuzz: plants each defect in the kernel (RM_SeaKernel.cs), demands the fuzz FAILS, restores the file
byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_seashores_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/SeaShores/Source/Kernel/RM_SeaKernel.cs"
MUTATIONS = [
    ("resolution skips the ocean pair", "return extension ?? oceanPair ?? waterPair ?? vanilla();", "return extension ?? waterPair ?? vanilla();"),
    ("resolution prefers the sea over the extension", "return extension ?? oceanPair ?? waterPair ?? vanilla();", "return oceanPair ?? extension ?? waterPair ?? vanilla();"),
    ("vanilla rung evaluated eagerly", "return extension ?? oceanPair ?? waterPair ?? vanilla();", "T v = vanilla(); return extension ?? oceanPair ?? waterPair ?? v;"),
    ("shallow terrain never registered", "Register(terrainToSea, s.Shallow, s.Sea, ambiguous);", ""),
    ("deep terrain never registered", "Register(terrainToSea, s.Deep, s.Sea, ambiguous);", ""),
    ("shared terrain stays keyed to the first sea", "                ambiguous.Add(terrain);\n                return;", "                return;"),
    ("shared terrain keyed to the last sea", "if (map.TryGetValue(terrain, out existing) && existing != sea)", "if (false)"),
    ("ambiguous seeds ignored", "var ambiguous = new HashSet<TTerrain>(initiallyAmbiguous);", "var ambiguous = new HashSet<TTerrain>();"),
    ("ambiguous terrain not removed", "foreach (TTerrain t in ambiguous) terrainToSea.Remove(t);", ""),
    ("one sea's two terrains count as ambiguous", "existing != sea)", "true)"),
    ("faced sea ignores the neighbour count", "if (count > bestCount ||", "if (bestCount == 0 ||"),
    ("faced sea takes the highest name on a tie", "string.CompareOrdinal(nameOf(biome), nameOf(best)) < 0", "string.CompareOrdinal(nameOf(biome), nameOf(best)) > 0"),
    ("faced sea ignores the name on a tie", "(count == bestCount && best != null && string.CompareOrdinal(nameOf(biome), nameOf(best)) < 0)", "false"),
    ("faced sea counts non-sea neighbours", "if (biome == null) continue;\n                int count", "int count"),
    ("faced sea compares culture-sensitively", "string.CompareOrdinal(nameOf(biome), nameOf(best)) < 0", "string.Compare(nameOf(biome), nameOf(best), StringComparison.OrdinalIgnoreCase) < 0"),
    ("cell trusts the terrain key only on a hit of null", "if (terrainKnown && keyed != null) return keyed;", ""),
    ("cell ignores an unknown terrain", "if (facedSea == null || !terrainKnown) return null;", "if (facedSea == null) return null;"),
    ("a pond on a coastal map is the sea", "return (terrainIsFacedDeep || terrainIsFacedShallow) ? facedSea : null;", "return facedSea;"),
    ("only deep water is the faced sea", "(terrainIsFacedDeep || terrainIsFacedShallow)", "terrainIsFacedDeep"),
    ("only shallow water is the faced sea", "(terrainIsFacedDeep || terrainIsFacedShallow)", "terrainIsFacedShallow"),
    ("empty band answers itself", "if (preferred != null && preferred.Count > 0) return preferred;", "if (preferred != null) return preferred;"),
    ("fallback ignored", "return fallback ?? empty;", "return empty;"),
    ("fallback null returns null", "return fallback ?? empty;", "return fallback;"),
    ("catch table ignores the setting", "return settingOn && hasMap && seaFound && seaHasFishTypes && providesCatch;", "return hasMap && seaFound && seaHasFishTypes && providesCatch;"),
    ("catch table ignores providesCatch", "&& seaHasFishTypes && providesCatch;", "&& seaHasFishTypes;"),
    ("catch table ignores a missing fish table", "&& seaFound && seaHasFishTypes && providesCatch;", "&& seaFound && providesCatch;"),
    ("fish roll inverted", "return !landBiomeHasFishTypes;", "return landBiomeHasFishTypes;"),
    ("master switch off does not suppress", "if (!generateSeaShoresSetting) return true;", ""),
    ("unknown sea suppressed", "return seaKnown && !seaGeneratesShore;", "return !seaGeneratesShore;"),
    ("sea that opts out is not suppressed", "return seaKnown && !seaGeneratesShore;", "return false;"),
    ("heal touches non-buildable land", "if (!buildableLand || !facesSea) return HealAction.Skip;", "if (!facesSea) return HealAction.Skip;"),
    ("heal touches land that faces no sea", "if (!buildableLand || !facesSea) return HealAction.Skip;", "if (!buildableLand) return HealAction.Skip;"),
    ("stale needs no ocean check", "bool stale = hasVanillaCoastMutator && !hasVanillaOceanNeighbour;", "bool stale = hasVanillaCoastMutator;"),
    ("stale vanilla coast kept as already coastal", "if (hasAnyCoastCategoryMutator && !stale) return HealAction.Already;", "if (hasAnyCoastCategoryMutator) return HealAction.Already;"),
    ("coastal tile healed again", "if (hasAnyCoastCategoryMutator && !stale) return HealAction.Already;", ""),
    ("stale reported as heal", "return stale ? HealAction.Replace : HealAction.Heal;", "return HealAction.Heal;"),
    ("coast directions keep duplicates", "if (!dirs.Contains(directions[i])) dirs.Add(directions[i]);", "dirs.Add(directions[i]);"),
    ("coast directions ignore countsAsCoast", "if (!countsAsCoast[i]) continue;", ""),
    ("coast directions out of order", "if (!dirs.Contains(directions[i])) dirs.Add(directions[i]);", "if (!dirs.Contains(directions[i])) dirs.Insert(0, directions[i]);"),
]

if __name__ == "__main__":
    sys.exit(run_mutations(KERNEL, "selftest_seashores_fuzz.py", MUTATIONS, sys.argv[1] if len(sys.argv) > 1 else None))
