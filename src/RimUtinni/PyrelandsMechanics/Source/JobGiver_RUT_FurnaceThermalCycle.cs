using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// FURNACEBEAST_THERMAL_CYCLE_1, part 3 — the LOCAL half of the cycle, and
    /// part 4, the thornvine diet.
    ///
    /// 🔴 SCOPE, STATED HONESTLY. The owner's cycle has a world leg and a map
    /// leg:
    ///
    ///   WORLD LEG (Deep Desert -> Pyrelands -> near terminator -> back). NOT
    ///   BUILT HERE, and not because it was forgotten. A herd that walks between
    ///   biomes over weeks is a world-pawn behaviour: it needs the herd to exist
    ///   on the planet while no map holds it, a route across WorldGrid tiles, a
    ///   tick that runs without a Map, and an arrival rule that spawns it into
    ///   whichever map it reaches. That is Caravan/WorldObject machinery, not
    ///   ThinkTree machinery, and it is its own build. Filed as
    ///   FURNACEBEAST_WORLD_MIGRATION_1.
    ///
    ///   MAP LEG (this file). Everything the cycle means once a beast is ON a
    ///   map, which is the only place a player ever sees it:
    ///     - under-charged: walk toward the burn. This is the owner's
    ///       "intentionally coming into the Pyrelands to help it burn and absorb
    ///       yet more heat", expressed at the scale a map can express it.
    ///     - fully charged: walk away from the burn. The capacitor is full; more
    ///       fire is no longer worth standing in.
    ///     - hungry: strip a thornvine patch. "One of the only things that will
    ///       eat the terrible Thornvine patches."
    ///
    /// 🔑 WHY THE BEAST CAN EAT THORNVINE AND NOTHING ELSE CAN, mechanically.
    /// VERIFIED against the engine: thornvine ships
    /// &lt;preferability&gt;NeverForNutrition&lt;/preferability&gt; (vanilla
    /// Plant_Thornvine, Odyssey), and FoodUtility.BestFoodSourceOnMap's animal
    /// path rejects anything at preferability &lt;= 2 on its main pass — so no
    /// ordinary grazer ever routes to it. This job-giver bypasses that search
    /// entirely and points the beast at the plant directly, which is exactly the
    /// species-specific exception the lore describes. Raising thornvine's
    /// preferability in XML would have fed it to every herbivore in the stack and
    /// destroyed the line.
    ///
    /// ⚠️ The nutrition itself is XML (Patches/RUT_Thornvine_Edible.xml), not
    /// here: JobDriver_Ingest refuses any def whose IsNutritionGivingIngestible
    /// is false, and that is computed from a cached stat that must be right at
    /// def-load time, not patched at startup.
    ///
    /// Wired at Animal_PreWander, the same supported Core insertion tag the
    /// fire-hawk uses. The species gate is the comp, checked here in C#, for the
    /// reason JobGiver_RUT_FireHawkCarryEmber's header gives.
    /// </summary>
    public class JobGiver_RUT_FurnaceThermalCycle : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned || pawn.Downed || !pawn.Awake())
            {
                return null;
            }

            CompFurnaceThermalCharge charge = pawn.TryGetComp<CompFurnaceThermalCharge>();
            if (charge == null)
            {
                return null;   // not a furnace-beast
            }

            // Hunger first: a starving beast that walks into a fire instead of
            // eating is a bug, not a thermal cycle.
            Job graze = TryGrazeThornvine(pawn);
            if (graze != null)
            {
                return graze;
            }

            return TryWorkTheBurn(pawn, charge);
        }

        // ---------------------------------------------------------------
        // Part 4 — the thornvine diet.
        // ---------------------------------------------------------------

        private static Job TryGrazeThornvine(Pawn pawn)
        {
            if (!PyrelandsMechanicsSettings.furnaceThornvineDietEnabled)
            {
                return null;
            }
            if (pawn.needs?.food == null
                || pawn.needs.food.CurCategory < HungerCategory.Hungry)
            {
                return null;
            }

            Thing vine = GenClosest.ClosestThingReachable(
                pawn.Position, pawn.Map,
                ThingRequest.ForGroup(ThingRequestGroup.Plant),
                PathEndMode.Touch,
                TraverseParms.For(pawn, Danger.Deadly),
                PyrelandsTuning.FurnaceThornvineScanRadius,
                (Thing t) => ThornvineDefs.IsThornvine(t.def)
                          && t.def.IsNutritionGivingIngestible
                          && t.IngestibleNow
                          && !t.IsForbidden(pawn)
                          && pawn.CanReserve(t));

            if (vine == null)
            {
                return null;
            }

            Job job = JobMaker.MakeJob(JobDefOf.Ingest, vine);
            job.count = 1;
            return job;
        }

        // ---------------------------------------------------------------
        // Part 3 — the map leg of the capacitor cycle.
        // ---------------------------------------------------------------

        private static Job TryWorkTheBurn(Pawn pawn, CompFurnaceThermalCharge charge)
        {
            if (!PyrelandsMechanicsSettings.furnaceFireSeekingEnabled)
            {
                return null;
            }

            MapComponent_BurnLine burn = MapComponent_BurnLine.For(pawn.Map);
            if (burn == null || !burn.AnyBurn)
            {
                return null;
            }

            IntVec3 centre = burn.BurnCenter;
            float distSq = (centre - pawn.Position).LengthHorizontalSquared;

            if (charge.WantsHeat)
            {
                // Already standing in it — the comp is charging, nothing to do.
                if (distSq <= PyrelandsTuning.FurnaceBurnCloseEnough * PyrelandsTuning.FurnaceBurnCloseEnough)
                {
                    return null;
                }
                if (distSq > PyrelandsTuning.FurnaceBurnSeekRadius * PyrelandsTuning.FurnaceBurnSeekRadius)
                {
                    // Out of map-scale range. Walking there is the WORLD leg's
                    // job, not this one — see the header. No job, no pretending.
                    return null;
                }
                return GotoNear(pawn, centre);
            }

            if (charge.IsFullyCharged
                && distSq <= PyrelandsTuning.FurnaceBurnCloseEnough * PyrelandsTuning.FurnaceBurnCloseEnough)
            {
                // Full. Step off the burn — the beast is done charging and the
                // rest of the cycle is spent somewhere cold.
                Vector3 away = (pawn.Position - centre).ToVector3();
                if (away.sqrMagnitude < 0.01f)
                {
                    away = Rand.InsideUnitCircleVec3;
                }
                IntVec3 target = pawn.Position
                    + (away.normalized * PyrelandsTuning.FurnaceBurnBackOffCells).ToIntVec3();
                return GotoNear(pawn, target);
            }

            return null;
        }

        private static Job GotoNear(Pawn pawn, IntVec3 target)
        {
            IntVec3 cell = CellFinder.RandomClosewalkCellNear(target, pawn.Map, 4, null);
            if (!cell.IsValid || !pawn.CanReach(cell, PathEndMode.OnCell, Danger.Deadly))
            {
                return null;
            }
            return JobMaker.MakeJob(JobDefOf.Goto, cell);
        }
    }

    /// <summary>
    /// Which plants count as thornvine, resolved once.
    ///
    /// 🔑 FAMILY BY NAME, NOT A DEF REFERENCE, and that is the correct call here
    /// rather than laziness. The family spans mods that come and go: vanilla
    /// Odyssey's Plant_Thornvine, and the GRiNDTerra Biomes donor's
    /// GRimThornvine / GRim1Thornvine / GRim2Thornvine. A DefOf would hard-fail
    /// when a donor is absent; a MayRequire list would need editing every time
    /// the stack changes. Matching on the name and requiring the def to actually
    /// be an ingestible plant degrades to "no thornvine on this map" with no
    /// error when none of them are loaded.
    ///
    /// ⚠️ MEASURED 2026-09-16: GRiNDTerra Biomes (grimterra.biomesmod) is NOT on
    /// disk in the current install — neither Mods\ nor workshop\294100 holds a
    /// file naming GRimThornvine. The GRim* names below are therefore carried
    /// forward from design/Jawa/worldbuilding/review/plant_register_rows.json,
    /// not read from a live def, and they cost nothing while the donor is away.
    /// </summary>
    internal static class ThornvineDefs
    {
        internal static bool IsThornvine(ThingDef def)
        {
            return def != null
                && def.plant != null
                && def.ingestible != null
                && def.defName.IndexOf("Thornvine", System.StringComparison.OrdinalIgnoreCase) >= 0;
        }
    }
}
