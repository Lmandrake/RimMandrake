using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef ParentName="BuildingBase">
    //     <defName>RM_DryAirBlower</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_DryFieldEmitter">
    //         <animalRepelRadius>3</animalRepelRadius>
    //         <animalRepelArcDegrees>90</animalRepelArcDegrees>
    //         <aversionHediff>RM_DryAirAversion</aversionHediff>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_DryFieldEmitter : CompProperties
    {
        // INVENTED (greentide_kit_spec.md M2): "when it runs out of fuel,
        // the green notices within hours" — ~6 in-game hours of plant
        // suppression per active refresh (every 250 ticks while the blower
        // runs, so this only matters once it stops).
        public int suppressHoldTicks = 15000;

        // INVENTED (kit spec, piece 2's own named values, reused for piece 3
        // — the animal-repel arc — since the spec ties both to "a doorway
        // arc" of the same shape): radius 3, 90 degree arc facing outward.
        public float animalRepelRadius = 3f;
        public float animalRepelArcDegrees = 90f;

        // The short marker/cooldown hediff applied to a repelled animal —
        // also what actually triggers the flee (see RM_CompDryFieldEmitter.TryRepel).
        public HediffDef aversionHediff;

        public List<ThingDef> immuneThingDefs;
        public List<PawnKindDef> immunePawnKinds;

        public CompProperties_DryFieldEmitter()
        {
            compClass = typeof(RM_CompDryFieldEmitter);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (aversionHediff == null)
            {
                yield return "CompProperties_DryFieldEmitter on " + parentDef.defName + " has no aversionHediff set.";
            }

            if (animalRepelRadius <= 0f)
            {
                yield return "CompProperties_DryFieldEmitter animalRepelRadius must be > 0.";
            }
        }
    }

    // GREENTIDE_MECHANICS_2 M2 build (greentide_kit_spec.md "M2. The dry-air
    // blower"). Two pieces: plant-growth suppression over the doorway arc
    // (SuppressPlantGrowth) and the wild-animal repel (RepelAnimals). Its old
    // first piece, drying the room to stop the wet-bulb clock, was deleted
    // with that clock (WETBULB_FOLD_INTO_HEAT_1): Greentide heat is vanilla
    // heat, and an enclosed room already takes no felt-heat offset.
    //
    // Runs every 250 ticks (the spec's own "periodic scan (interval 250
    // ticks)") from CompTick, because the blower is a Normal-ticker building.
    public class RM_CompDryFieldEmitter : ThingComp
    {
        public CompProperties_DryFieldEmitter Props => (CompProperties_DryFieldEmitter)props;

        // The blower is tickerType Normal (power, fuel and heat pusher need it), and a Normal building
        // never calls CompTickRare, so this runs from CompTick on the rare cadence (TICKER_NEVER_FIRES_FIX_1).
        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(GenTicks.TickRareInterval))
            {
                return;
            }

            if (!RM_EnvironmentalHazardsSettings.dryAirBlowerEnabled)
            {
                return; // mod option: dry-air blower disabled
            }

            if (!IsActive())
            {
                return;
            }

            SuppressPlantGrowth();
            RepelAnimals();
        }

        private bool IsActive()
        {
            if (!parent.Spawned)
            {
                return false;
            }

            CompPowerTrader power = parent.GetComp<CompPowerTrader>();
            if (power != null && !power.PowerOn)
            {
                return false;
            }

            CompRefuelable fuel = parent.GetComp<CompRefuelable>();
            if (fuel != null && !fuel.HasFuel)
            {
                return false;
            }

            CompFlickable flick = parent.GetComp<CompFlickable>();
            if (flick != null && !flick.SwitchIsOn)
            {
                return false;
            }

            return true;
        }

        // Piece 2: "repels encroachment: writes suppression into the
        // EXPLOSIVE_PLANT_GROWTH_1 engine's suppression grid over a doorway
        // arc." WIRED 2026-09-26: that grid now exists
        // (mandrake.rm.explosivegrowth); the write goes through
        // RM_ExplosiveGrowthSuppressionBridge by reflection, so without that
        // mod this is still a no-op. Same arc as RepelAnimals (the spec ties
        // both to one doorway arc), each cell suppressed for suppressHoldTicks
        // and re-granted every active rare tick — so when the blower stops,
        // "the green notices within hours".
        private void SuppressPlantGrowth()
        {
            Map map = parent.Map;
            if (map == null || !RM_ExplosiveGrowthSuppressionBridge.Available)
            {
                return;
            }

            Vector2 facing = parent.Rotation.AsVector2;
            float arcCos = Mathf.Cos(Props.animalRepelArcDegrees * 0.5f * Mathf.Deg2Rad);
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(parent.Position, Props.animalRepelRadius, useCenter: true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }
                Vector2 offset = new Vector2(cell.x - parent.Position.x, cell.z - parent.Position.z);
                if (offset.sqrMagnitude > 0.0001f && Vector2.Dot(offset.normalized, facing) < arcCos)
                {
                    continue;
                }
                RM_ExplosiveGrowthSuppressionBridge.Suppress(map, cell, 0, Props.suppressHoldTicks);
            }
        }

        // Piece 3: "repels animals ... a periodic scan (interval 250 ticks)
        // applying a short RM_DryAirAversion hediff (flee-inducing mental
        // state) to non-immune wild animals in the arc." RESOLVED by the
        // GREENTIDE_MECHANICS_2 spike pass: Verse.AI/AvoidGrid.cs is
        // colonist-pathing/combat-danger only, so this scan-and-flee route
        // is the only one — built for real here, not re-investigated.
        private void RepelAnimals()
        {
            HediffDef aversion = Props.aversionHediff;
            if (aversion == null)
            {
                return;
            }

            Map map = parent.Map;
            if (map == null)
            {
                return;
            }

            Vector2 facing = parent.Rotation.AsVector2;
            float arcCos = Mathf.Cos(Props.animalRepelArcDegrees * 0.5f * Mathf.Deg2Rad);

            foreach (IntVec3 cell in GenRadial.RadialCellsAround(parent.Position, Props.animalRepelRadius, useCenter: false))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                Vector2 offset = new Vector2(cell.x - parent.Position.x, cell.z - parent.Position.z);
                if (offset.sqrMagnitude < 0.0001f)
                {
                    continue;
                }

                if (Vector2.Dot(offset.normalized, facing) < arcCos)
                {
                    continue; // outside the doorway-facing arc
                }

                List<Thing> things = cell.GetThingList(map);
                for (int i = things.Count - 1; i >= 0; i--)
                {
                    if (things[i] is Pawn animal)
                    {
                        TryRepel(animal, aversion);
                    }
                }
            }
        }

        private void TryRepel(Pawn animal, HediffDef aversion)
        {
            if (animal == null || animal.Dead || !animal.Spawned)
            {
                return;
            }

            if (animal.RaceProps == null || !animal.RaceProps.Animal)
            {
                return; // wild ANIMALS only, per the spec's own wording
            }

            if (animal.Faction != null)
            {
                return; // tame/player-owned — not "shying off", a colonist's animal stays put
            }

            if (Props.immuneThingDefs != null && Props.immuneThingDefs.Contains(animal.def))
            {
                return;
            }

            if (Props.immunePawnKinds != null && animal.kindDef != null && Props.immunePawnKinds.Contains(animal.kindDef))
            {
                return;
            }

            if (animal.health?.hediffSet?.GetFirstHediffOfDef(aversion) != null)
            {
                return; // already averted this cycle — the hediff IS the cooldown
            }

            Hediff hediff = HediffMaker.MakeHediff(aversion, animal);
            animal.health.AddHediff(hediff);

            animal.mindState?.mentalStateHandler?.TryStartMentalState(
                MentalStateDefOf.PanicFlee, "a blast of bone-dry air", forced: true, forceWake: true);
        }
    }
}
