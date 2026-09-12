using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 4. See EnvironmentalWeatherExtension for
    // the XML surface.
    //
    // Structure follows vanilla's own GameCondition_ToxicFallout rather than
    // the donor's acid-rain class: pawn damage on an interval from
    // GameConditionTick, item rot and plant kill from DoCellSteadyEffects
    // (which the engine already sweeps at its own throttled rate), density
    // and temperature through the virtuals the base class already exposes.
    // The donor's forced-weather re-set loop is not reproduced because
    // GameCondition.ForcedWeather() is a vanilla override that does the same
    // job correctly and for free.
    public class GameCondition_EnvironmentalWeather : GameCondition
    {
        private int ticksUntilDamage;

        private EnvironmentalWeatherExtension ExtensionInt
        {
            get { return def != null ? def.GetModExtension<EnvironmentalWeatherExtension>() : null; }
        }

        public override int TransitionTicks
        {
            get
            {
                EnvironmentalWeatherExtension ext = ExtensionInt;
                return ext != null ? Mathf.Max(1, ext.temperatureTransitionTicks) : base.TransitionTicks;
            }
        }

        public override void Init()
        {
            base.Init();

            EnvironmentalWeatherExtension ext = ExtensionInt;
            if (ext == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] GameConditionDef " + (def != null ? def.defName : "(null)")
                    + " uses GameCondition_EnvironmentalWeather but carries no EnvironmentalWeatherExtension; it will run with no effects.",
                    def != null ? def.shortHash ^ 0x5A13 : 0x5A13);
                return;
            }

            ticksUntilDamage = ext.damageIntervalTicks;
        }

        public override void GameConditionTick()
        {
            base.GameConditionTick();

            EnvironmentalWeatherExtension ext = ExtensionInt;
            if (ext == null)
            {
                return;
            }

            if (ext.damageDef == null && ext.hediffToApply == null)
            {
                return;
            }

            if (--ticksUntilDamage > 0)
            {
                return;
            }

            ticksUntilDamage = ext.damageIntervalTicks;

            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++)
            {
                DoPawnEffects(maps[i], ext);
            }
        }

        // Public so a quicktest can force one deterministic application
        // without waiting out damageIntervalTicks.
        public void DoPawnEffects(Map map, EnvironmentalWeatherExtension ext)
        {
            if (!RM_EnvironmentalHazardsSettings.environmentalDamageEnabled)
            {
                return; // mod option: environmental weather damage disabled
            }
            if (map == null || ext == null)
            {
                return;
            }

            // Snapshot: damage can kill, and a kill mutates AllPawnsSpawned.
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);

            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];

                if (!HazardTargeting.Affects(pawn, ext.affects, ext.immuneThingDefs, ext.immunePawnKinds))
                {
                    continue;
                }

                if (ext.onlyUnroofed && pawn.Position.Roofed(map))
                {
                    continue;
                }

                float mult = Mathf.Max(0f, RM_EnvironmentalHazardsSettings.hazardDamageMultiplier);

                if (ext.damageDef != null && ext.damageAmount > 0f)
                {
                    pawn.TakeDamage(new DamageInfo(ext.damageDef, ext.damageAmount * mult, ext.armorPenetration, -1f));
                }

                if (ext.hediffToApply != null && ext.hediffSeverityPerInterval != 0f && !pawn.Dead)
                {
                    HealthUtility.AdjustSeverity(pawn, ext.hediffToApply, ext.hediffSeverityPerInterval * mult);
                }
            }
        }

        public override void DoCellSteadyEffects(IntVec3 c, Map map)
        {
            base.DoCellSteadyEffects(c, map);

            if (!RM_EnvironmentalHazardsSettings.environmentalDamageEnabled)
            {
                return; // mod option: environmental weather damage disabled
            }

            EnvironmentalWeatherExtension ext = ExtensionInt;
            if (ext == null)
            {
                return;
            }

            if (ext.itemRotProgressPerCellEffect <= 0f && ext.plantKillChancePerCellEffect <= 0f)
            {
                return;
            }

            if (ext.onlyUnroofed && c.Roofed(map))
            {
                return;
            }

            List<Thing> things = c.GetThingList(map);
            for (int i = things.Count - 1; i >= 0; i--)
            {
                Thing thing = things[i];
                if (thing == null || thing.Destroyed)
                {
                    continue;
                }

                if (thing is Plant plant)
                {
                    if (ext.plantKillChancePerCellEffect <= 0f)
                    {
                        continue;
                    }

                    if (ext.respectPlantToxicSensitivity
                        && (plant.def.plant == null || !plant.def.plant.dieFromToxicFallout))
                    {
                        continue;
                    }

                    if (!HazardTargeting.PlantAffected(plant, ext.immuneThingDefs))
                    {
                        continue;
                    }

                    if (Rand.Value < ext.plantKillChancePerCellEffect)
                    {
                        plant.Kill();
                    }

                    continue;
                }

                if (ext.itemRotProgressPerCellEffect > 0f && thing.def.category == ThingCategory.Item)
                {
                    CompRottable rot = thing.TryGetComp<CompRottable>();
                    if (rot != null && (int)rot.Stage < (int)RotStage.Dessicated)
                    {
                        rot.RotProgress += ext.itemRotProgressPerCellEffect;
                    }
                }
            }
        }

        public override WeatherDef ForcedWeather()
        {
            EnvironmentalWeatherExtension ext = ExtensionInt;
            return ext != null ? ext.forcedWeather : null;
        }

        public override float TemperatureOffset()
        {
            EnvironmentalWeatherExtension ext = ExtensionInt;
            if (ext == null)
            {
                return 0f;
            }

            float target;

            if (ext.dayTempOffset != 0f || ext.nightTempOffset != 0f)
            {
                // Day/night swing. SingleMap can be null for a world-level
                // condition, in which case the flat offset is the honest
                // answer rather than an arbitrary half-way value.
                Map map = SingleMap;
                if (map == null)
                {
                    target = ext.tempOffset;
                }
                else
                {
                    target = GenCelestial.IsDaytime(GenCelestial.CurCelestialSunGlow(map))
                        ? ext.dayTempOffset
                        : ext.nightTempOffset;
                }
            }
            else
            {
                target = ext.tempOffset;
            }

            if (target == 0f)
            {
                return 0f;
            }

            // Fade the offset in and out rather than snapping the map's
            // temperature by ±30C on one tick — vanilla's own route for
            // exactly this (GameConditionUtility.LerpInOutValue).
            return GameConditionUtility.LerpInOutValue(this, TransitionTicks, target);
        }

        public override float AnimalDensityFactor(Map map)
        {
            EnvironmentalWeatherExtension ext = ExtensionInt;
            return ext != null ? ext.animalDensityFactor : 1f;
        }

        public override float PlantDensityFactor(Map map)
        {
            EnvironmentalWeatherExtension ext = ExtensionInt;
            return ext != null ? ext.plantDensityFactor : 1f;
        }

        public override bool AllowEnjoyableOutsideNow(Map map)
        {
            EnvironmentalWeatherExtension ext = ExtensionInt;
            return ext == null || ext.allowEnjoyableOutside;
        }

        public override bool ElectricityDisabled
        {
            get
            {
                EnvironmentalWeatherExtension ext = ExtensionInt;
                return ext != null && ext.electricityDisabled;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksUntilDamage, "ticksUntilDamage", 0);
        }
    }
}
