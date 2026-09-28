using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_DEDICATED_GRAZER_1 — "detect an approaching fire front, path
    /// underground/into a burrow state, then re-emerge once the burn has
    /// passed" (the_pyrelands.md §4).
    ///
    /// Hooks the biome's EXISTING fire-tracking rather than re-deriving it:
    /// MapComponent_BurnLine already re-measures every free-standing Fire on
    /// the map each watch interval (PyrelandsFireFront.cs's clock feeds it),
    /// and AnyBurn is a free early-out for the ~every-other-biome case — only
    /// a map that is ACTUALLY burning pays for the per-pawn distance scan
    /// below.
    ///
    /// Same insertion shape as CreatureBehaviors' RM_JobGiver_FollowShadowCaster
    /// (built for DESERT_GLITTER_BIRDS_COMMENSALS_1, checked before writing
    /// this): a null modExtension check makes it safe to insert at
    /// Animal_PreWander for every animal in the game, not only Pyrelands
    /// fauna, so no per-species XML gate is needed at the splice point. The
    /// MECHANISM itself is new and unrelated (that job-giver steers a pawn
    /// toward a moving host's shadow; this one detects a map-wide hazard and
    /// holds the pawn still) — only the "opt-in DefModExtension + global
    /// ThinkTree insert" shape is reused, per this item's own step 2.
    /// </summary>
    public class RM_JobGiver_BurrowOnFire : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            Map map = pawn?.Map;
            if (map == null || pawn.Dead || !pawn.Spawned)
            {
                return null;
            }

            RM_BurrowOnFireExtension ext = pawn.def.GetModExtension<RM_BurrowOnFireExtension>();
            if (ext == null)
            {
                return null;
            }

            if (!RM_PyrelandsSettings.pyrelandsEnabled || !RM_PyrelandsSettings.burrowOnFireEnabled)
            {
                return null;
            }

            // The JobDriver owns the burrowed state from here — it is the one
            // that removes the hediff on safe emergence or timeout — so a
            // pawn already carrying it is left alone rather than re-issued a
            // second burrow job on top of the first.
            if (pawn.health?.hediffSet == null
                || pawn.health.hediffSet.HasHediff(PyrelandsMechanicsDefOf.RM_Burrowed))
            {
                return null;
            }

            MapComponent_BurnLine burnLine = MapComponent_BurnLine.For(map);
            if (burnLine == null || !burnLine.AnyBurn)
            {
                return null;
            }

            if (!FireIsNear(pawn, map, ext.detectionRadius))
            {
                return null;
            }

            return JobMaker.MakeJob(PyrelandsMechanicsDefOf.RM_Burrow);
        }

        /// <summary>
        /// Nearest free-standing ground fire within range. Uses the same
        /// "Fire.parent == null" test MapComponent_BurnLine.Measure() uses to
        /// tell a real ground burn from a pawn or a wall on fire, so a
        /// burning colonist standing next to a grazer does not trigger a
        /// burrow. Shared with RM_JobDriver_Burrow so "is it safe to come
        /// back up" asks the identical question "is it time to go down" did.
        /// </summary>
        internal static bool FireIsNear(Pawn pawn, Map map, float radius)
        {
            float radiusSq = radius * radius;
            List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < fires.Count; i++)
            {
                if (fires[i] is Fire { parent: null } fire && fire.Spawned
                    && (fire.Position - pawn.Position).LengthHorizontalSquared <= radiusSq)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
