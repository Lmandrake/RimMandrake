using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M3 build (miasma_kit_spec.md M3: "stranding pools
    // and the stranded"). Generic on purpose, same reasoning as M1/M2's own
    // extensions — attached to the SAME BiomeDef (RUT_Miasma today; any
    // future biome with a two-water axis and a recede could adopt this
    // unchanged). Parameterizes RM_MapComponent_StrandingPools end to end:
    // what spawns into a freshly-detected pool, how the weighted roll is
    // sized, how fast a pool dries, what it dries INTO, and the size
    // threshold that arms the return-to-water JobGiver.
    //
    //   <li MayRequire="mandrake.rm.environmentalhazards" Class="RimMandrake.EnvironmentalHazards.RM_StrandingPoolsExtension">
    //     <strandedSpawnList>
    //       <li MayRequire="mlie.starwarsanimalcollection">Yobshrimp</li> <!-- PLACEHOLDER, see header -->
    //     </strandedSpawnList>
    //     <emptyWeight>40</emptyWeight>
    //     <smallWeight>50</smallWeight>
    //     <bigWeight>10</bigWeight>
    //     <strandedCountSmall>1~2</strandedCountSmall>
    //     <strandedCountBig>3~5</strandedCountBig>
    //     <decayDaysRange>3~8</decayDaysRange>
    //     <poolSizeThreshold>4</poolSizeThreshold>
    //     <searchRadius>60</searchRadius>
    //     <dryTerrain>RUT_Jawa_SaltCrust</dryTerrain>
    //   </li>
    //
    // strandedSpawnList: the kit spec's own explicit scope line — "the
    // transitional endemics are roster content; this kit ships only the
    // spawner and the pool lifecycle" — means the REAL RUT_StrandedSpawnList
    // roster (the sheet's actual gill-going-leathery, fin-splaying-to-feet
    // creatures) is not authored here. This field is a generic
    // List<PawnKindDef> so the roster pass can point it at real content
    // later without touching a line of C#; RUT_Miasma.xml wires exactly ONE
    // existing shipped PawnKindDef into it as a loudly-commented PLACEHOLDER
    // so the spawner/lifecycle below compiles and could run end-to-end
    // today, not a real roster decision.
    //
    // "Something bigger" (10% tier, spec's own words) is read here as MORE
    // individuals from the same generic list (strandedCountBig, INVENTED
    // 3-5) rather than a differently-tiered creature, since a second,
    // "bigger" PawnKindDef list would itself be roster content this kit is
    // explicitly not scoped to invent. The roster pass can still express a
    // genuinely bigger single creature later by pointing bigWeight's own
    // draws at a list containing only large kinds, if it wants to — nothing
    // here forces "more of the same," it only doesn't invent a second list.
    public class RM_StrandingPoolsExtension : DefModExtension
    {
        public List<PawnKindDef> strandedSpawnList = new List<PawnKindDef>();

        // Weighted roll (INVENTED, spec: "40% empty, 50% 1-2 stranded, 10%
        // something bigger"). Not required to sum to 100 — normalized at
        // roll time against whatever total the three add up to.
        public float emptyWeight = 40f;
        public float smallWeight = 50f;
        public float bigWeight = 10f;

        public IntRange strandedCountSmall = new IntRange(1, 2);

        // INVENTED-BUILD figure — the spec names the 10% tier only as
        // "something bigger," this pass picked a count range for it (see
        // header note on why it's a count, not a size, tier).
        public IntRange strandedCountBig = new IntRange(3, 5);

        // Days to fully dry (INVENTED, spec: "3-8 days").
        public FloatRange decayDaysRange = new FloatRange(3f, 8f);

        // Cell count at/below which RM_JobGiver_ReturnToWater starts sending
        // this pool's occupants toward the nearest channel (INVENTED — no
        // figure named by the spec at all, picked and recorded here).
        public int poolSizeThreshold = 4;

        // Search radius (map cells) RM_MapComponent_StrandingPools.
        // TryFindNearestChannelCell scans for a reachable non-pool water
        // cell (INVENTED-BUILD, same order of magnitude as this mod's own
        // RM_SeekTargetExtension-style search radii elsewhere).
        public float searchRadius = 60f;

        // What a decaying pool's cells repaint to once dry (via
        // RM_GradientAxisRepaint.SetTerrainFloorSafe — the same
        // floor-exclusion write M2 built, reused rather than forked, per
        // this item's own assignment). A dedicated field rather than
        // reading M1's RM_GradientAxisExtension.landTerrain: that field is
        // gated on landRepaintSource/landRepaintMinSalinity for a different
        // purpose (muck salt-crusting) and doesn't apply to former WATER
        // cells drying out, so this mechanism carries its own, simpler
        // target terrain instead of depending on M1's unrelated gating.
        public TerrainDef dryTerrain;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (emptyWeight < 0f || smallWeight < 0f || bigWeight < 0f)
            {
                yield return "RM_StrandingPoolsExtension has a negative weight — emptyWeight/smallWeight/bigWeight must all be >= 0.";
            }

            if (emptyWeight + smallWeight + bigWeight <= 0f)
            {
                yield return "RM_StrandingPoolsExtension's three weights sum to 0 — the stranding roll could never resolve.";
            }

            if (poolSizeThreshold < 0)
            {
                yield return "RM_StrandingPoolsExtension.poolSizeThreshold must be >= 0.";
            }

            if (decayDaysRange.min <= 0f || decayDaysRange.max < decayDaysRange.min)
            {
                yield return "RM_StrandingPoolsExtension.decayDaysRange is invalid.";
            }

            if (searchRadius <= 0f)
            {
                yield return "RM_StrandingPoolsExtension.searchRadius must be > 0.";
            }
        }
    }
}
