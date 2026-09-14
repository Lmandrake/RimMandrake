using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef ParentName="BuildingBase">
    //     <defName>RUT_DryAirBlower</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_DryFieldEmitter">
    //         <dryRoomHoldTicks>15000</dryRoomHoldTicks>
    //         <animalRepelRadius>3</animalRepelRadius>
    //         <animalRepelArcDegrees>90</animalRepelArcDegrees>
    //         <aversionHediff>RUT_DryAirAversion</aversionHediff>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_DryFieldEmitter : CompProperties
    {
        // INVENTED (greentide_kit_spec.md M2): "when it runs out of fuel,
        // the green notices within hours" — ~6 in-game hours of grant per
        // active refresh (CompTickRare cadence, 250 ticks, keeps re-granting
        // the full duration while the blower runs, so this only matters
        // once it stops).
        public int dryRoomHoldTicks = 15000;

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
    // blower"). Three pieces per the spec's own numbering; #2 is a
    // documented no-op this pass (see SuppressPlantGrowth below), #1 and #3
    // are built for real.
    //
    // CompTickRare (vanilla's own 250-tick cadence) is used deliberately for
    // both remaining pieces rather than a hand-rolled counter: it matches
    // the spec's own "periodic scan (interval 250 ticks)" for piece 3
    // exactly, and re-granting the room-dry duration at the same cadence
    // (piece 1) is a harmless simplification — more frequent refresh only
    // ever extends the grant, never shortens it.
    public class RM_CompDryFieldEmitter : ThingComp
    {
        public CompProperties_DryFieldEmitter Props => (CompProperties_DryFieldEmitter)props;

        public override void CompTickRare()
        {
            base.CompTickRare();

            if (!RM_EnvironmentalHazardsSettings.dryAirBlowerEnabled)
            {
                return; // mod option: dry-air blower disabled
            }

            if (!IsActive())
            {
                return;
            }

            KeepRoomDry();
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

        // Piece 1: "dries the room ... registers its room (via
        // Thing.GetRoom()) in RM_MapComponent_DryRooms, which M1's
        // condition reads." See RM_MapComponent_DryRooms's own header for
        // why this re-registers every active tick rather than once at spawn.
        private void KeepRoomDry()
        {
            Room room = parent.GetRoom();
            if (room == null)
            {
                return;
            }

            parent.Map?.GetComponent<RM_MapComponent_DryRooms>()?.KeepDry(room, Props.dryRoomHoldTicks);
        }

        // Piece 2: "repels encroachment: writes suppression into the
        // EXPLOSIVE_PLANT_GROWTH_1 engine's suppression grid over a doorway
        // arc." GREENTIDE_MECHANICS_2's own build-pass brief flags this as a
        // known external gap: confirmed by grep before this pass started
        // (`grep -r "PlantSuppression\|ExplosivePlantGrowth" src/`, zero
        // hits) that no such grid exists anywhere in src/ yet — building it
        // here would mean building EXPLOSIVE_PLANT_GROWTH_1's whole job
        // inside this comp, which is a different item's scope, not this
        // one's. Left as a documented no-op rather than skipped silently.
        //
        // TODO(EXPLOSIVE_PLANT_GROWTH_1): once that engine exists, call its
        // suppression-grid write here for the same arc RepelAnimals already
        // computes (radius/arc INVENTED values on CompProperties_DryFieldEmitter
        // above) — do not build a new grid in this method when that day comes,
        // call into the real one.
        private void SuppressPlantGrowth()
        {
        }

        // Piece 3: "repels animals ... a periodic scan (interval 250 ticks)
        // applying a short RUT_DryAirAversion hediff (flee-inducing mental
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
                MentalStateDefOf.PanicFlee, "dry, bone-scouring heat", forced: true, forceWake: true);
        }
    }
}
