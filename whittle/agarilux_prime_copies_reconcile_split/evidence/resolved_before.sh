#!/bin/bash
# The def chain BEFORE the change, read from git at the parent of the landing commit.
cd "$(dirname "$0")/../../.."
C=$(git log -1 --format=%H --grep="AGARILUX_PRIME_COPIES_RECONCILE_SPLIT: TheRot owns"); P=$C^
echo "== def chain BEFORE the change (parent of $C), read from git"
echo "-- base def, src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml:"
git show $P:src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml | grep -n -A14 "<defName>RM_AgariluxPrime</defName>" | grep -E "defName|texPath|graphicClass"
echo "-- TheRot repoint, src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml:"
git show $P:src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml | grep -n -B1 -A5 'RM_AgariluxPrime"\]/graphicData/texPath</xpath>' | head -7
echo "-- PNGs at either path before (git ls-tree):"
git ls-tree -r -l $P -- src | grep -E "Textures/(RotSpecies/AgariluxPrime|Things/Plants/AB_AgariluxPrime)\.png" | awk '{print $4, $5}'
echo
echo "== resolution BEFORE: base Things/Plants/AB_AgariluxPrime -> TheRot repoint (Replace inside a Conditional) -> RotSpecies/AgariluxPrime"
echo "   the live game agreed: the full 317-mod def dump captured 2026-11-02T17:59:18Z reads RM_AgariluxPrime texPath RotSpecies/AgariluxPrime from mandrake.rm.biomes (resolved_texpath_after.txt section 4)"
echo "   so both Things/Plants/AB_AgariluxPrime.png copies sat at that slot (TheRot deployed in mandrake.rm.biomes; UtinniPatches is not in the active mod list), but RM_AgariluxPrime never drew either;"
echo "   AB_AgariluxPrime (the Alpha Biomes donor) is not in the game, so nothing else drew them either."
echo "== owner of def and texture: TheRot (mandrake.rm.biomes) -- the only mod defining RM_AgariluxPrime and the only one shipping the drawn PNG."
