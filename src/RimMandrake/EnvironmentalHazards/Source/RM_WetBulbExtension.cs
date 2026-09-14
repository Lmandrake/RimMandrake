using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M1 build (greentide_kit_spec.md "M1. Wet-bulb
    // overwhelm + the gear tree"). The data side of RM_GameCondition_WetBulb.
    //
    // Deliberately NOT EnvironmentalWeatherExtension (the ruled
    // GameCondition_EnvironmentalWeather's own config): the spec is explicit
    // this mechanic "shares no field semantics with the ruled one" — it is a
    // severity ramp (not damage), gated by a summed-from-apparel StatDef and
    // by a dried-room lookup, neither of which the ruled extension has any
    // field for.
    //
    //   <GameConditionDef MayRequire="mandrake.rm.environmentalhazards">
    //     <defName>RUT_GreentideWetBulbLock</defName>
    //     <conditionClass>RimMandrake.EnvironmentalHazards.RM_GameCondition_WetBulb</conditionClass>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_WetBulbExtension">
    //         <hediffDef>RUT_WetBulbOverwhelm</hediffDef>
    //         <protectionStat>RM_WetBulbProtection</protectionStat>
    //         <intervalTicks>600</intervalTicks>
    //         <severityPerInterval>0.00667</severityPerInterval>
    //         <protectionHoldThreshold>0.8</protectionHoldThreshold>
    //       </li>
    //     </modExtensions>
    //   </GameConditionDef>
    public class RM_WetBulbExtension : DefModExtension
    {
        // The hediff RM_GameCondition_WetBulb ramps every interval.
        public HediffDef hediffDef;

        // Summed across every worn apparel item (RM_GameCondition_WetBulb
        // does the summing itself — an "Apparel"-category StatDef has no
        // vanilla auto-aggregation onto a pawn stat; ArmorUtility is the
        // only vanilla consumer of that category and reads per-apparel, not
        // per-pawn). Clamped to 0..1 after summing.
        public StatDef protectionStat;

        public int intervalTicks = 600;

        // INVENTED (kit spec's own tuning license): unprotected, this
        // reaches lethalSeverity (1.0) in ~150 intervals at 600 ticks each —
        // 90000 ticks, ~1.5 in-game days, matching the spec's named target.
        public float severityPerInterval = 0.00667f;

        // INVENTED tuning knob realizing the spec's other named anchor,
        // "indefinite hold at protection >= 0.8": the applied gain is scaled
        // by max(0, 1 - protection/protectionHoldThreshold), which is 1 at
        // protection 0 (full rate) and 0 at protection ==
        // protectionHoldThreshold (gain stops entirely, not just slows) —
        // the honest way to hit both named tuning points from the spec with
        // one formula rather than picking a rate that only approximates the
        // second one. Set <= 0 to disable the hold (pure linear (1-protection)
        // gate) if a future biome wants that instead.
        public float protectionHoldThreshold = 0.8f;

        // Species/immunity gate (gate 3, "elevated-thirst races and native
        // fauna are immune") — reuses the kit's own shared HazardTargeting
        // rather than re-deriving a fourth exemption-list shape.
        public PawnTargetKind affects = PawnTargetKind.Flesh;
        public List<ThingDef> immuneThingDefs;
        public List<PawnKindDef> immunePawnKinds;

        // GREENTIDE_MECHANICS_2 M5 build ("M1's condition reads Breaklight's
        // presence and idles — dry air, the multiplier switches off, exactly
        // the sheet's physics"). Gate 4: while ANY GameConditionDef named
        // here is active on the same map, RampMap idles the whole ramp for
        // that map that tick — not merely a reduced driveFactor, an outright
        // skip, matching "the wet-bulb clock pauses" verbatim. Left empty by
        // default so this stays a no-op on every other biome; Greentide's
        // own RUT_GreentideWetBulbLock.xml is the only config that names
        // RUT_BreaklightCondition here. Data-driven rather than a hardcoded
        // defName so this class stays kit-agnostic — the specific pairing
        // lives in XML, not in RM_GameCondition_WetBulb.cs.
        public List<GameConditionDef> pausedByConditions;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (hediffDef == null)
            {
                yield return "RM_WetBulbExtension has no hediffDef set.";
            }

            if (intervalTicks < 1)
            {
                yield return "RM_WetBulbExtension intervalTicks must be >= 1.";
            }

            if (severityPerInterval <= 0f)
            {
                yield return "RM_WetBulbExtension severityPerInterval must be > 0 — 0 or less means the condition never does anything.";
            }
        }
    }
}
