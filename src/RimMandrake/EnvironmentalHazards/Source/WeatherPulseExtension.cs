using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F1 build pass (forge_kit_spec.md "F1. The closed
    // boiling rain"). The data side of RM_GameCondition_WeatherPulse — a
    // DefModExtension on the GameConditionDef, the same shape
    // EnvironmentalWeatherExtension already uses (GameConditionDef has no
    // per-def props object; a DefModExtension is the only per-def hook).
    //
    // Generic, not Forge-specific: any biome that wants "calm weather, then
    // an occasional violent burst of a second weather with scald-style
    // damage while the burst runs" attaches this to its own GameConditionDef
    // via BiomeDef.biomeMapConditions. The Forge's own tuning
    // (RUT_ForgeStill / RUT_BoilingRain / RUT_Scald, MTB 10h, burst
    // 20-40min, ~4 dmg/60 ticks) lives in RUT_ForgePulse's own XML, not here.
    //
    //   <GameConditionDef>
    //     <defName>RUT_ForgePulse</defName>
    //     <conditionClass>RimMandrake.EnvironmentalHazards.RM_GameCondition_WeatherPulse</conditionClass>
    //     <canBePermanent>true</canBePermanent>
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.WeatherPulseExtension">
    //         <baseWeather>RUT_ForgeStill</baseWeather>
    //         <burstWeather>RUT_BoilingRain</burstWeather>
    //         <burstMtbHours>10</burstMtbHours>
    //         <burstDurationMinutesRange>20~40</burstDurationMinutesRange>
    //         <flashWindowHoursAfterBurstStart>2</flashWindowHoursAfterBurstStart>
    //         <scaldDamageDef>RUT_Scald</scaldDamageDef>
    //         <scaldDamageAmount>4</scaldDamageAmount>
    //         <scaldDamageIntervalTicks>60</scaldDamageIntervalTicks>
    //       </li>
    //     </modExtensions>
    //   </GameConditionDef>
    public class WeatherPulseExtension : DefModExtension
    {
        // --- the lock -------------------------------------------------
        // Forced whenever no burst is in progress. The condition itself is
        // made permanent by the engine (BiomeConditionMapComponent.
        // MapGenerated calls GameConditionMaker.MakeConditionPermanent on
        // every entry in BiomeDef.biomeMapConditions, verified
        // Source/RimWorld/BiomeConditionMapComponent.cs) — this condition
        // IS the biome's whole weather rotation for as long as it runs,
        // which is how "no ordinary rain reachable" (forge_kit_spec.md
        // ban #6) is structurally enforced: nothing else ever gets a turn
        // to force weather on this map.
        public WeatherDef baseWeather;

        // --- the burst --------------------------------------------------
        public WeatherDef burstWeather;

        // Mean in-game hours between burst starts, rolled once per tick via
        // Rand.MTBEventOccurs while no burst is running (never scheduled).
        // INVENTED, F1 spec: mean 10.
        public float burstMtbHours = 10f;

        // How long the burst's own forced weather lasts once triggered.
        // INVENTED, F1 spec: 20-40 in-game minutes.
        public IntRange burstDurationMinutesRange = new IntRange(20, 40);

        // --- the flash --------------------------------------------------
        // RM_MapComponent_FlashCycle's own window runs from burst start
        // until this many in-game hours later — deliberately independent
        // of the burst weather's own (shorter) duration above, per the F1
        // spec's own "flash-interval growth... until 2 in-game hours
        // after [burst start]" line: the window outlasts the rain itself.
        // INVENTED, F1 spec: 2.
        public float flashWindowHoursAfterBurstStart = 2f;

        // --- the scald ----------------------------------------------------
        // Reparameterizes GameCondition_EnvironmentalWeather.DoPawnEffects'
        // own damage shape (HazardTargeting.Affects gate, onlyUnroofed
        // check, settings-driven global multiplier) rather than reusing
        // that class directly, because EnvironmentalWeather forces one
        // weather and damages continuously, while this condition must gate
        // the identical shape to "currently in a burst" only — see
        // RM_GameCondition_WeatherPulse.DoScaldDamageOnMap's own header.
        public DamageDef scaldDamageDef;
        public float scaldDamageAmount = 4f;
        public float armorPenetration;
        public int scaldDamageIntervalTicks = 60;
        public bool onlyUnroofed = true;
        public PawnTargetKind affects = PawnTargetKind.Flesh;
        public List<ThingDef> immuneThingDefs;
        public List<PawnKindDef> immunePawnKinds;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (baseWeather == null)
            {
                yield return "WeatherPulseExtension needs a baseWeather - the condition has nothing to force between bursts.";
            }

            if (burstWeather == null)
            {
                yield return "WeatherPulseExtension needs a burstWeather.";
            }

            if (burstMtbHours <= 0f)
            {
                yield return "WeatherPulseExtension burstMtbHours must be > 0.";
            }

            if (burstDurationMinutesRange.min <= 0 || burstDurationMinutesRange.max < burstDurationMinutesRange.min)
            {
                yield return "WeatherPulseExtension burstDurationMinutesRange is invalid.";
            }

            if (flashWindowHoursAfterBurstStart <= 0f)
            {
                yield return "WeatherPulseExtension flashWindowHoursAfterBurstStart must be > 0.";
            }

            if (scaldDamageIntervalTicks < 1)
            {
                yield return "WeatherPulseExtension scaldDamageIntervalTicks must be >= 1.";
            }
        }
    }
}
