using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

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
        // Crush damage dealt to a curated-crushable Thing that ISN'T simply
        // destroyed outright (T3 buildings are - see ProcessCell). BENCH-draft
        // tuning, not owner-ruled: enough that a wall dies in a handful of
        // passes at T1/T2, cheap to retune from one place.
        private const float CrushDamageT1 = 20f;
        private const float CrushDamageT2 = 60f;

        // Chance per occupied cell, per step, of leaving a filth-trail mark
        // (tier table: "filth trail" is a T1+ wake behaviour). Not every cell,
        // every step, or the trail would blanket the map on a single pass.
        private const float FilthTrailChancePerCell = 0.35f;

        public static void ProcessFootprint(Pawn titan, TitanicTier tier)
        {
            Map map = titan.Map;
            CellRect rect = titan.OccupiedRect();
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                ProcessCell(c, map, tier, titan);
            }
        }

        private static void ProcessCell(IntVec3 c, Map map, TitanicTier tier, Pawn titan)
        {
            ProcessRoof(c, map, tier);
            ProcessCrushables(c, map, tier, titan);

            if (tier >= TitanicTier.T1 && Rand.Chance(FilthTrailChancePerCell))
            {
                FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_RubbleRock);
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
            if (tier < TitanicTier.T2)
            {
                return;
            }
            RoofDef roof = c.GetRoof(map);
            if (roof != null && !roof.isThickRoof)
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
        private static void ProcessCrushables(IntVec3 c, Map map, TitanicTier tier, Pawn titan)
        {
            List<Thing> cellThings = c.GetThingList(map).ToList(); // copy: destroying below mutates the live list
            for (int i = 0; i < cellThings.Count; i++)
            {
                Thing t = cellThings[i];
                if (t == titan || t is Pawn || t.Destroyed || !t.Spawned)
                {
                    // Never crush pawns here (incl. riders or a second titan) -
                    // combat/collision between creatures is a separate system,
                    // out of scope for the wake.
                    continue;
                }
                if (!CrushTableUtility.IsCrushableAtTier(t, tier))
                {
                    continue;
                }

                if (tier == TitanicTier.T3 && t.def.category == ThingCategory.Building)
                {
                    t.Destroy(DestroyMode.KillFinalize);
                    continue;
                }

                float damage = tier == TitanicTier.T2 ? CrushDamageT2 : CrushDamageT1;
                t.TakeDamage(new DamageInfo(DamageDefOf.Crush, damage, instigator: titan));
            }
        }
    }
}
