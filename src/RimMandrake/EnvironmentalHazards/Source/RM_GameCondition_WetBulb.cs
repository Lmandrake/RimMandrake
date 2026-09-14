using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M1 build (greentide_kit_spec.md "M1. Wet-bulb
    // overwhelm + the gear tree"). Attached via a biome's <biomeMapConditions>
    // (BiomeDef.biomeMapConditions, verified in ALPHA_MECHANICS_KIT_1's own
    // spec pass) — every map of that biome runs it permanently.
    //
    // Shape cribbed from vanilla HediffGiver_Heat.OnIntervalPassed (severity
    // driven by HealthUtility.AdjustSeverity against an ambient-vs-safe
    // comparison) per the kit spec's own citation, but this is a
    // GameCondition (map-wide, interval-batched) rather than a per-pawn
    // HediffGiver, and it adds the three gates HediffGiver_Heat has no
    // field for: apparel-summed protection, a dried-room zero, and a
    // species exemption list (the third reuses HazardTargeting.Affects,
    // the same gate GameCondition_EnvironmentalWeather already uses).
    //
    // Deliberately does NOT read ambient temperature at all, unlike
    // HediffGiver_Heat: the sheet's whole point is that wet-bulb heat
    // overwhelms regardless of shade/roof — this condition ramps
    // unconditionally (subject to its own three gates) rather than
    // comparing against SafeTemperatureRange, which is the desert's kit,
    // not this biome's.
    public class RM_GameCondition_WetBulb : GameCondition
    {
        private int ticksUntilRamp;

        private RM_WetBulbExtension ExtensionInt
        {
            get { return def != null ? def.GetModExtension<RM_WetBulbExtension>() : null; }
        }

        public override void Init()
        {
            base.Init();

            RM_WetBulbExtension ext = ExtensionInt;
            if (ext == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] GameConditionDef " + (def != null ? def.defName : "(null)")
                    + " uses RM_GameCondition_WetBulb but carries no RM_WetBulbExtension; it will run with no effects.",
                    def != null ? def.shortHash ^ 0x5713 : 0x5713);
                return;
            }

            ticksUntilRamp = ext.intervalTicks;
        }

        public override void GameConditionTick()
        {
            base.GameConditionTick();

            if (!RM_EnvironmentalHazardsSettings.wetBulbOverwhelmEnabled)
            {
                return; // mod option: wet-bulb overwhelm disabled
            }

            RM_WetBulbExtension ext = ExtensionInt;
            if (ext == null || ext.hediffDef == null)
            {
                return;
            }

            if (--ticksUntilRamp > 0)
            {
                return;
            }

            ticksUntilRamp = ext.intervalTicks;

            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++)
            {
                RampMap(maps[i], ext);
            }
        }

        private void RampMap(Map map, RM_WetBulbExtension ext)
        {
            if (map == null)
            {
                return;
            }

            // M2's dried-room gate: RM_CompDryFieldEmitter keeps this
            // registry fresh while its blower runs. Absent mod/no blower on
            // this map at all is the common case and must not throw.
            RM_MapComponent_DryRooms dryRooms = map.GetComponent<RM_MapComponent_DryRooms>();

            // Snapshot: AdjustSeverity can, in principle, trigger death and
            // mutate AllPawnsSpawned — same caution GameCondition_EnvironmentalWeather
            // already takes.
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);

            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];

                if (!HazardTargeting.Affects(pawn, ext.affects, ext.immuneThingDefs, ext.immunePawnKinds))
                {
                    continue; // gate 3: species exemption
                }

                if (dryRooms != null && dryRooms.IsDry(pawn.GetRoom()))
                {
                    continue; // gate 2: a dried room stops the clock entirely
                }

                float protection = SumApparelProtection(pawn, ext.protectionStat);

                // gate 1: severity gain x (1 - protection), realized as a
                // hold-threshold curve — see RM_WetBulbExtension.protectionHoldThreshold.
                float driveFactor = ext.protectionHoldThreshold > 0f
                    ? Mathf.Max(0f, 1f - protection / ext.protectionHoldThreshold)
                    : Mathf.Max(0f, 1f - protection);

                if (driveFactor <= 0f)
                {
                    continue; // gear alone holds the clock — nothing to apply
                }

                float mult = Mathf.Max(0f, RM_EnvironmentalHazardsSettings.hazardDamageMultiplier);
                float gain = ext.severityPerInterval * driveFactor * mult;
                if (gain <= 0f || pawn.Dead)
                {
                    continue;
                }

                HealthUtility.AdjustSeverity(pawn, ext.hediffDef, gain);
            }
        }

        // "New StatDef summed from apparel" (kit spec, M1) — an
        // "Apparel"-category StatDef has no vanilla auto-aggregation onto a
        // pawn stat (ArmorUtility is the only vanilla consumer of that
        // category, and it reads per-apparel-item, not per-pawn), so this
        // condition does the summing itself.
        private static float SumApparelProtection(Pawn pawn, StatDef stat)
        {
            if (stat == null || pawn?.apparel == null)
            {
                return 0f;
            }

            List<Apparel> worn = pawn.apparel.WornApparel;
            float total = 0f;
            for (int i = 0; i < worn.Count; i++)
            {
                total += worn[i].GetStatValue(stat);
            }

            return Mathf.Clamp01(total);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksUntilRamp, "ticksUntilRamp", 0);
        }
    }
}
