using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 1. One class replacing the "damage gas"
    // duplication the source review found (three near-identical donor
    // classes differing only in DamageDef and interval).
    //
    // Configured entirely by a GasDamageExtension on the gas ThingDef — see
    // that file for the XML. A def with no extension is a plain vanilla Gas
    // and does nothing but expire, which is a legitimate "visual only" state,
    // so that is a one-time warning rather than an error.
    //
    //   <ThingDef ParentName="RM_BaseGas">
    //     <defName>RM_ExampleSporeGas</defName>
    //     <thingClass>RimMandrake.EnvironmentalHazards.Gas_Damaging</thingClass>
    //     ...
    //   </ThingDef>
    public class Gas_Damaging : Gas
    {
        private int ticksUntilScan;

        private GasDamageExtension ExtensionInt
        {
            get { return def.GetModExtension<GasDamageExtension>(); }
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);

            GasDamageExtension ext = ExtensionInt;
            if (ext == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] " + def.defName + " uses Gas_Damaging but carries no GasDamageExtension; it will expire without affecting anything.",
                    def.shortHash ^ 0x5A11);
                return;
            }

            if (!respawningAfterLoad)
            {
                // Stagger: a burst from CompActiveGasEmitter spawns many gas
                // Things in one tick, and they must not all scan together.
                ticksUntilScan = Rand.RangeInclusive(1, ext.tickIntervalTicks);
            }
        }

        // 1.6 replaced Thing.Tick() with TickInterval(int delta): the engine
        // may batch several ticks into one call, so the countdown subtracts
        // delta rather than 1. Verified against Verse/Gas.cs, whose own
        // expiry override has this same signature.
        protected override void TickInterval(int delta)
        {
            base.TickInterval(delta);

            if (Destroyed || !Spawned)
            {
                return;
            }

            GasDamageExtension ext = ExtensionInt;
            if (ext == null)
            {
                return;
            }

            ticksUntilScan -= delta;
            if (ticksUntilScan > 0)
            {
                return;
            }

            ticksUntilScan = ext.tickIntervalTicks;
            ApplyEffects(ext);
        }

        // Public so a quicktest can force one deterministic application
        // without stepping ticks — the RunScan precedent in this codebase.
        public void ApplyEffects(GasDamageExtension ext)
        {
            if (!RM_EnvironmentalHazardsSettings.gasEffectsEnabled)
            {
                return; // mod option: gas effects disabled
            }
            Map map = Map;
            if (map == null || ext == null)
            {
                return;
            }

            IntVec3 cell = Position;

            if (ext.onlyUnroofed && cell.Roofed(map))
            {
                return;
            }

            // Snapshot: TakeDamage can kill a pawn and mutate the live
            // thing list underneath a foreach.
            List<Thing> things = new List<Thing>(cell.GetThingList(map));

            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t == null || t.Destroyed)
                {
                    continue;
                }

                if (t is Pawn pawn)
                {
                    if (HazardTargeting.Affects(pawn, ext.affects, ext.immuneThingDefs, ext.immunePawnKinds))
                    {
                        AffectPawn(pawn, ext);
                    }
                    continue;
                }

                if (ext.plantDamageAmount > 0f && t is Plant
                    && HazardTargeting.PlantAffected(t, ext.immuneThingDefs))
                {
                    DamageDef plantDamage = ext.plantDamageDef ?? DamageDefOf.Deterioration;
                    t.TakeDamage(new DamageInfo(plantDamage, ext.plantDamageAmount, 0f, -1f, this));
                }
            }
        }

        private void AffectPawn(Pawn pawn, GasDamageExtension ext)
        {
            float mult = Mathf.Max(0f, RM_EnvironmentalHazardsSettings.hazardDamageMultiplier);

            if (ext.damageDef != null && ext.damageAmount > 0f)
            {
                pawn.TakeDamage(new DamageInfo(ext.damageDef, ext.damageAmount * mult, ext.armorPenetration, -1f, this));
            }

            if (ext.hediffToApply != null && ext.hediffSeverityPerTick != 0f && !pawn.Dead)
            {
                // AdjustSeverity is vanilla's own additive route: it creates
                // the hediff if the pawn has none, and respects the hediff's
                // own max severity. Immunity to the hediff (a gas mask's
                // ToxicResistance, a gene, an immunity hediff) is therefore
                // handled by the hediff's own def, not re-derived here.
                HealthUtility.AdjustSeverity(pawn, ext.hediffToApply, ext.hediffSeverityPerTick * mult);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksUntilScan, "ticksUntilScan", 0);
        }
    }
}
