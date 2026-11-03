#!/bin/bash
# Mutant sweep for selftest_cauldron_trunk_deposits.py (item CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS).
# Usage: bash src/RimMandrake/Cauldron/mutants_cauldron_trunk_deposits.sh "$PWD"   (repo root). Every mutant must print RED; baseline rc=0.
R=$1; T=$(mktemp -d)
mk(){ rm -rf $T/w; mkdir -p $T/w/src/RimMandrake $T/w/design/Jawa/worldbuilding $T/w/skills $T/w/infrastructure/state/items
 rsync -a --include="*/" --include="*.cs" --exclude="*" $R/src/ $T/w/src/; cp -r $R/src/RimMandrake/Cauldron $T/w/src/RimMandrake/; cp -r $R/design/Jawa/worldbuilding/biomes $T/w/design/Jawa/worldbuilding/
 cp -r $R/skills/rimworld-art-evaluation $R/skills/editing-images $T/w/skills/
 for i in CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS CAULDRON_TRUNK_DEPOSITS_BUILD_SWEAT_SHOWS CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR; do cp $R/infrastructure/state/items/$i.md $T/w/infrastructure/state/items/ 2>/dev/null || true; done; }
run(){ python3 $T/w/src/RimMandrake/Cauldron/selftest_cauldron_trunk_deposits.py > $T/out 2>&1; echo $?; }
C=$T/w/src/RimMandrake/Cauldron; B=$T/w/design/Jawa/worldbuilding/biomes; D=$B/cauldron_trunk_deposits_design_2026-11-02.md
mk; echo "baseline rc=$(run) (want 0)"
declare -A M=(
 [fexxil_renamed]="sed -i 's/<defName>RM_Fexxil</<defName>RM_FexxilX</' \$C/Defs/ThingDefs_Plants/RM_CauldronFloraExpansion.xml"
 [crystalflower_renamed]="sed -i 's/<defName>RM_CrystalFlower</<defName>RM_CrystalFlowerX</' \$C/Defs/ThingDefs_Plants/RM_CauldronFlora.xml"
 [compmetalyield_class_renamed]="sed -i 's/class RM_CompMetalYield\b/class RM_CompMetalYieldX/' \$C/Source/RM_CompMetalYield.cs"
 [gradefraction_removed]="sed -i 's/ GradeFraction(/ GradeFractionX(/' \$C/Source/RM_CompMetalYield.cs"
 [overlayyoffset_renamed]="sed -i 's/OverlayYOffset/OverlayYOffsetX/g' \$C/Source/RM_CauldronDewfallVisuals.cs"
 [fleckband_renamed]="sed -i 's/ FleckBand(/ FleckBandX(/' \$C/Source/Kernel/RM_YieldKernel.cs"
 [enrichment_spec_deleted]="rm \$B/cauldron_enrichment_audio_visuals_spec_2026-10-02.md"
 [cauldron_md_deleted]="rm \$B/cauldron.md"
 [roster_deleted]="rm \$B/rosters/cauldron.json"
 [roster_keep_dropped]="sed -i 's/owner favourite, keep; no leaf-crown/no leaf-crown/' \$B/rosters/cauldron.json"
 [treemartyr_uncut]="sed -i 's#</Defs>#<ThingDef><defName>RM_TreeMartyr</defName></ThingDef></Defs>#' \$C/Defs/ThingDefs_Plants/RM_CauldronFlora.xml"
 [skill_missing]="rm -r \$T/w/skills/editing-images"
 [followon_item_missing]="rm \$T/w/infrastructure/state/items/CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR.md"
 [engine_api_unused]="sed -i s/Rand.Seed/Rand.SeedX/ \$(grep -rlF Rand.Seed \$T/w/src --include=*.cs)"
 [new_unclassified_cite]="echo 'See \`RM_SomethingInvented\`.' >> \$D"
 [flecks_texture_deleted]="rm \$C/Textures/Things/Plant/RM_AssayFlecks/Flecks_Heavy.png"
)
for k in $(printf '%s\n' "${!M[@]}" | sort); do mk; eval "${M[$k]}"; rc=$(run); [ "$rc" != 0 ] && v=RED || v="GREEN(BAD)"; echo "$k rc=$rc $v :: $(grep -m1 ^FAIL $T/out | cut -c1-110)"; done
rm -rf $T
