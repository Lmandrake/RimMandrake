using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F1 build pass (forge_kit_spec.md "F1. The closed
    // boiling rain" / "flash-interval growth"). Plant.GrowthRate is
    // `public virtual` (Source/RimWorld/Plant.cs:289, verified this spec)
    // — the only override point needed. Multiplies the vanilla factors
    // (fertility * temperature * light * noxious-haze * drought, plus the
    // blight/season zero-outs Plant.GrowthRate already applies) rather than
    // replacing them, so a flash-flora plant still responds to terrain,
    // season and toxic fallout normally; the flash window only scales the
    // result.
    //
    // Multiplier and window source are field-configurable (not hardcoded
    // to the Forge's own 8.0/0.05) so a future biome's own flash-growth
    // plant can retune without a new class — same posture as
    // RM_CompScriptedDieOff being explicitly reusable beyond the Forge.
    // Named RUT_ (not RM_) at the owner's own instruction for this build
    // pass even though the class carries no Forge-specific data.
    //
    // No concrete Plant ThingDef is needed for this class to compile — it
    // is a base class a content pass points a real plant's <thingClass> at
    // (this build's own scope; the concrete plant ThingDef and its
    // wildPlants entry are roster/biome-authoring work, not done here).
    public class RUT_Plant_FlashFlora : Plant
    {
        // INVENTED, F1 spec: 8.0.
        protected virtual float FlashWindowGrowthMultiplier => 8f;

        // INVENTED, F1 spec: 0.05.
        protected virtual float OutsideFlashWindowGrowthMultiplier => 0.05f;

        public override float GrowthRate
        {
            get
            {
                float baseRate = base.GrowthRate;
                if (baseRate <= 0f)
                {
                    return baseRate; // blighted / out of season - nothing to scale
                }

                if (!RM_EnvironmentalHazardsSettings.weatherPulseEnabled)
                {
                    // Master switch off: grow at the vanilla rate rather
                    // than being stuck at the "outside window" penalty
                    // forever (with the switch off, RM_GameCondition_
                    // WeatherPulse never starts a burst, so a window would
                    // never arrive to lift it) - MOD_OPTIONS_RETROFIT_1's
                    // all-off-degrades-gracefully rule.
                    return baseRate;
                }

                RM_MapComponent_FlashCycle flashCycle = Spawned ? Map.GetComponent<RM_MapComponent_FlashCycle>() : null;
                bool inWindow = flashCycle != null && flashCycle.InFlashWindow();

                return baseRate * (inWindow ? FlashWindowGrowthMultiplier : OutsideFlashWindowGrowthMultiplier);
            }
        }
    }
}
