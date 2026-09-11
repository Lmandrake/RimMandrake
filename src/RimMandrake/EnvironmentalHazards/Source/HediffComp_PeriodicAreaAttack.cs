using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 2. See
    // HediffCompProperties_PeriodicAreaAttack for the XML surface.
    //
    // An active area-damage field carried by whatever holds the hediff. The
    // source review's point about why this is a HediffComp and not a Hediff
    // subclass: a comp stacks onto ANY existing HediffDef from XML, so the
    // same mechanism serves a walking hazard creature, a guardian plant and
    // a hazardous building without a class per use.
    public class HediffComp_PeriodicAreaAttack : HediffComp
    {
        private int ticksUntilBurst;
        private Sustainer sustainer;

        public HediffCompProperties_PeriodicAreaAttack Props => (HediffCompProperties_PeriodicAreaAttack)props;

        public override void CompPostMake()
        {
            base.CompPostMake();
            // Stagger so a pack of carriers does not burst in lockstep.
            ticksUntilBurst = Rand.RangeInclusive(1, Mathf.Max(1, Props.tickIntervalTicks));
        }

        // 1.6's batched tick hook. CompPostTick is the legacy per-tick one;
        // overriding the interval form means the comp stays correct when the
        // engine coalesces ticks (which it does for unloaded/background maps).
        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            if (!Active())
            {
                EndSustainer();
                return;
            }

            MaintainSustainer();

            ticksUntilBurst -= delta;
            if (ticksUntilBurst > 0)
            {
                return;
            }

            ticksUntilBurst = Props.tickIntervalTicks;
            Burst();
        }

        private bool Active()
        {
            Pawn pawn = Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Map == null)
            {
                return false;
            }

            if (parent.Severity < Props.minSeverity)
            {
                return false;
            }

            if (Props.requiresAwake && pawn.Awake() == false)
            {
                return false;
            }

            return true;
        }

        // Public so a quicktest can drive one deterministic burst without
        // stepping ticks.
        public void Burst()
        {
            Pawn carrier = Pawn;
            if (carrier == null || !carrier.Spawned || Props.damageDef == null)
            {
                return;
            }

            Map map = carrier.Map;
            if (map == null)
            {
                return;
            }

            IntVec3 origin = carrier.Position;
            List<IntVec3> affectedCells = new List<IntVec3>();

            foreach (IntVec3 cell in GenRadial.RadialCellsAround(origin, Props.radius, useCenter: true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                if (Props.sparedUnderThickRoof && UnderThickRoof(cell, map))
                {
                    continue;
                }

                bool touched = DamageCell(cell, map, origin, carrier);
                if (touched)
                {
                    affectedCells.Add(cell);
                }
            }

            TrySpawnFilth(map, affectedCells, origin);
        }

        private static bool UnderThickRoof(IntVec3 cell, Map map)
        {
            RoofDef roof = map.roofGrid.RoofAt(cell);
            return roof != null && roof.isThickRoof;
        }

        private bool DamageCell(IntVec3 cell, Map map, IntVec3 origin, Pawn carrier)
        {
            // Snapshot: damage destroys things and mutates the live list.
            List<Thing> things = new List<Thing>(cell.GetThingList(map));
            bool touchedAnything = false;

            float distance = (cell - origin).LengthHorizontal;
            float falloff = Props.falloffCurve != null ? Props.falloffCurve.Evaluate(distance) : 1f;

            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t == null || t.Destroyed)
                {
                    continue;
                }

                if (Props.sparesCarrier && t == carrier)
                {
                    continue;
                }

                if (Props.immuneThingDefs != null && Props.immuneThingDefs.Contains(t.def))
                {
                    continue;
                }

                float multiplier = CategoryMultiplier(t, carrier);
                if (multiplier <= 0f)
                {
                    continue;
                }

                float amount = Props.damageAmount * falloff * multiplier;
                if (amount <= 0f)
                {
                    continue;
                }

                t.TakeDamage(new DamageInfo(Props.damageDef, amount, Props.armorPenetration, -1f, carrier));
                touchedAnything = true;
            }

            return touchedAnything;
        }

        // Returns 0 for "this hazard does not touch that at all".
        private float CategoryMultiplier(Thing t, Pawn carrier)
        {
            if (t is Pawn pawn)
            {
                if (!HazardTargeting.Affects(pawn, Props.affects, Props.immuneThingDefs, Props.immunePawnKinds))
                {
                    return 0f;
                }

                if (Props.sparesSameFaction && carrier.Faction != null && pawn.Faction == carrier.Faction)
                {
                    return 0f;
                }

                float m = Props.pawnMultiplier;
                if (pawn.RaceProps != null && pawn.RaceProps.Animal)
                {
                    m *= Props.animalMultiplier;
                }
                if (pawn.Downed)
                {
                    m *= Props.downedPawnMultiplier;
                }
                return m;
            }

            if (t is Plant)
            {
                return Props.plantMultiplier;
            }

            if (t.def.category == ThingCategory.Building)
            {
                // Natural rock is the map's own bedrock. Chewing through it
                // turns any long-lived area hazard into a map-wide excavator,
                // so it is spared unless a def explicitly asks otherwise.
                if (Props.sparedNaturalRock && t.def.building != null && t.def.building.isNaturalRock)
                {
                    return 0f;
                }
                return Props.buildingMultiplier;
            }

            if (t.def.category == ThingCategory.Item)
            {
                return Props.itemMultiplier;
            }

            return 0f;
        }

        private void TrySpawnFilth(Map map, List<IntVec3> affectedCells, IntVec3 origin)
        {
            if (Props.filthDef == null || Props.filthChancePerBurst <= 0f)
            {
                return;
            }

            if (!Rand.Chance(Props.filthChancePerBurst))
            {
                return;
            }

            IntVec3 cell = affectedCells.Count > 0 ? affectedCells.RandomElement() : origin;
            if (cell.InBounds(map))
            {
                FilthMaker.TryMakeFilth(cell, map, Props.filthDef);
            }
        }

        private void MaintainSustainer()
        {
            if (Props.sustainerSound == null)
            {
                return;
            }

            Pawn pawn = Pawn;
            if (pawn == null || !pawn.Spawned)
            {
                EndSustainer();
                return;
            }

            if (sustainer == null || sustainer.Ended)
            {
                sustainer = Props.sustainerSound.TrySpawnSustainer(
                    SoundInfo.InMap(new TargetInfo(pawn), MaintenanceType.PerTick));
            }

            sustainer?.Maintain();
        }

        private void EndSustainer()
        {
            if (sustainer != null)
            {
                if (!sustainer.Ended)
                {
                    sustainer.End();
                }
                sustainer = null;
            }
        }

        public override void CompPostPostRemoved()
        {
            base.CompPostPostRemoved();
            EndSustainer();
        }

        public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
        {
            base.Notify_PawnDied(dinfo, culprit);
            EndSustainer();
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref ticksUntilBurst, "ticksUntilBurst", 0);
        }

        public override string CompDebugString()
        {
            return "ticksUntilBurst: " + ticksUntilBurst;
        }
    }
}
