using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// The destruction wake itself (item ruling #1). Fires once per cell a
    /// tiered pawn enters (see Patch_Thing_Position_Wake / CompTitanicWake) -
    /// never a per-tick scan.
    ///
    /// Footprint is read via the vanilla GenAdj.OccupiedRect(Thing) extension
    /// with NO reference to Large Pawns: that mod Prefix-patches exactly this
    /// method to return the true multi-cell square when present (confirmed by
    /// decompile), so this degrades to a correct 1x1 wake automatically if
    /// Large Pawns is absent or removed.
    /// </summary>
    public static class TitanicWakeProcessor
    {
        // Crush damage numbers live in RM_TitanicKernel (CrushDamageLight/Heavy, PROVISIONAL BENCH-draft tuning).

        public static void ProcessFootprint(Pawn titan, TitanicTier tier)
        {
            // MOD_OPTIONS_RETROFIT_1: master switch for the whole wake.
            if (!RM_HugeThingsSettings.WakeActive) return;

            if (titan.Flying) return; // TITAN_WAKE_FIXES_1 (B3.8): no ground wake while airborne
            Map map = titan.Map;
            CellRect rect = titan.OccupiedRect();
            // TITAN_WAKE_FIXES_1 (B3.6): 1.6 ThingGrid registers a multi-cell thing in every cell it covers, so crushables are gathered
            // across the whole footprint first and each is struck once per step (a 2x2 under a 4x4 step took four blows before).
            var cells = new List<List<Thing>>();
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                ProcessRoof(c, map, tier);
                if (RM_TitanicKernel.LeavesFilth((int)tier, Rand.Chance(RM_HugeThingsSettings.wakeFilthTrailChance)))
                {
                    FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_RubbleRock);
                }
                cells.Add(c.GetThingList(map).ToList()); // copy: destroying below mutates the live lists
            }
            foreach (Thing t in RM_TitanicKernel.UniqueInOrder<Thing>(cells))
            {
                ProcessCrushable(t, tier, titan);
            }
            SmashGiantPlants(rect, map, tier, titan);
        }

        /// <summary>
        /// Owner ruling 2026-10-07 (decision taken by question card): the biggest titans smash through giant plants and damage
        /// them; smaller titans path around giant trunks as walls. A trunk is impassable, so a smasher meets it beside its
        /// footprint, never inside it: every giant with a solid cell in the footprint or the ring around it takes one heavy crush
        /// blow per step, through the plant's own damage route (Building_TrunkBlocker.ForwardToPlant, deduplicated per tick,
        /// titan and plant), until it falls and its trunk goes with it. Which tier smashes is a Mod Setting (T3 by default).
        /// </summary>
        private static void SmashGiantPlants(CellRect rect, Map map, TitanicTier tier, Pawn titan)
        {
            int minTier = RM_HugeThingsSettings.giantPlantSmashMinTier;
            bool active = RM_HugeThingsSettings.GiantPlantSmashActive;
            if (!GiantSmash.Smashes((int)tier, minTier, active)) return;
            MapComponent_HugeFootprints mc = map.GetComponent<MapComponent_HugeFootprints>();
            if (mc == null || mc.Count == 0) return;
            Dictionary<int, Plant> plants = new Dictionary<int, Plant>();
            List<SolidCell> solid = mc.SolidCellsIn(rect.ExpandedBy(GiantSmash.Reach), plants);
            float damage = GiantSmash.Damage(RM_TitanicKernel.CrushDamageHeavy, RM_HugeThingsSettings.wakeCrushDamageMultiplier);
            foreach (int id in GiantSmash.Owners((int)tier, minTier, active, rect.minX, rect.minZ, rect.maxX, rect.maxZ, solid))
            {
                Building_TrunkBlocker.ForwardToPlant(plants[id], new DamageInfo(DamageDefOf.Crush, damage, instigator: titan));
            }
        }

        /// <summary>
        /// Card #1: "Thin (constructed) roofs are DESTROYED as the titan
        /// passes; thick roofs (overhead mountain) are AVOIDED." The
        /// distinction is RoofDef.isThickRoof (Verse/RoofDef.cs) -
        /// RoofRockThick (overhead mountain) is the only shipped RoofDef with
        /// isThickRoof=true; RoofRockThin and RoofConstructed are both false
        /// (confirmed by reading the three defs). Avoidance itself is a
        /// pathing-cost matter, handled separately by
        /// Patch_ThickRoofAvoidance - this method only ever REMOVES a roof, and
        /// only ever a thin one; a thick roof overhead is never touched here
        /// even as a fallback, on purpose (never destroy natural rock).
        /// Gated to T2+ per the tier table ("T2 colossal: thin roofs holed";
        /// T1 does not hole roofs).
        /// </summary>
        private static void ProcessRoof(IntVec3 c, Map map, TitanicTier tier)
        {
            if (!RM_HugeThingsSettings.RoofHolingActive) return;
            RoofDef roof = c.GetRoof(map);
            if (RM_TitanicKernel.HolesRoof((int)tier, roof != null, roof != null && roof.isThickRoof))
            {
                map.roofGrid.SetRoof(c, null);
            }
        }

        /// <summary>
        /// Card #3: crush only what the curated table names, never
        /// "everything in radius". T3 outright-destroys a crushable Building
        /// (tier table: "structures destroyed outright"); every other
        /// crushable hit, at any tier, takes Crush damage instead of an
        /// instant kill, so a wall takes a few passes rather than vanishing on
        /// first contact.
        /// </summary>
        private static void ProcessCrushable(Thing t, TitanicTier tier, Pawn titan)
        {
            if (t == titan || t is Pawn || t.Destroyed || !t.Spawned)
            {
                // Never crush pawns here (incl. riders or a second titan) - combat/collision between creatures is a separate system,
                // out of scope for the wake.
                return;
            }
            // A giant plant and its trunk are never on the crush table while giant plants are on: smashers reach them through
            // SmashGiantPlants (one blow per step), and smaller titans leave them standing.
            bool giant = t is Building_TrunkBlocker || (t is Plant && t.TryGetComp<CompHugeFootprint>() != null);
            if (!GiantSmash.WakeMayCrush(HugeGates.IsGiantForWake(RM_HugeThingsSettings.giantPlantsEnabled, giant)))
            {
                return;
            }
            if (!CrushTableUtility.IsCrushableAtTier(t, tier))
            {
                return;
            }

            if (RM_TitanicKernel.DestroysOutright((int)tier, t.def.category == ThingCategory.Building))
            {
                t.Destroy(DestroyMode.KillFinalize);
                return;
            }

            float damage = RM_TitanicKernel.CrushDamage((int)tier, RM_HugeThingsSettings.wakeCrushDamageMultiplier);
            t.TakeDamage(new DamageInfo(DamageDefOf.Crush, damage, instigator: titan));
        }
    }
}
