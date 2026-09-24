using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_GASLIGHT_1 (item spec §2, the founding owner ruling verbatim:
    // "a dancing, pulsing, beautifully warm light that warbles between
    // adjacent colors"). Checked first per the item's own instruction:
    // BiomeGlowMultiplierExtension/BiomeGlowPatches (this same assembly) is
    // a Harmony patch on GenCelestial.CurCelestialSunGlow — a whole-map
    // darkness multiplier, not a per-Thing animated light, so it is not
    // reusable here. The only other glower content in this repo
    // (RUT_LanternstoneItems.xml etc.) is a plain, static
    // RimWorld.CompProperties_Glower with no animation hook at all — vanilla
    // CompGlower itself (Verse/CompGlower.cs, read in full this pass) has no
    // built-in animation either, just a settable GlowColor/GlowRadius the
    // game re-registers with the map's GlowGrid whenever they change
    // (GlowColor's setter does this itself; GlowRadius's setter does not,
    // confirmed against Verse/GlowGrid.cs's GlowLight struct, which snapshots
    // both color AND radius at REGISTER time — so a radius change needs an
    // explicit CompGlower.ForceRegister(map) call, which RM_Comp_WarblingGlow
    // makes).
    //
    // A sibling comp, not a CompGlower subclass: the lamp and the statue
    // both already need a plain vanilla CompProperties_Glower for their base
    // glow (colorPickerEnabled/darklightToggle etc. all stay available
    // untouched), and this rides alongside it via ThingComp.parent.GetComp,
    // the same "generic sibling mechanism" shape RM_HediffComp_
    // CarriedFilthExposure already uses elsewhere in this kit.
    public class RM_CompProperties_WarblingGlow : CompProperties
    {
        public RM_CompProperties_WarblingGlow()
        {
            compClass = typeof(RM_Comp_WarblingGlow);
        }

        // How far the hue wanders each way from the sibling CompGlower's own
        // base glowColor, in degrees around the 360-degree hue wheel — "warbles
        // BETWEEN ADJACENT colors" (the owner's own word), so this stays small
        // (a shipped default of 18 degrees) rather than cycling the full wheel.
        public float hueRangeDegrees = 18f;

        // How far brightness (HSV value) pulses each way from the base color's
        // own value — the "pulsing" half of "dancing, pulsing."
        public float valuePulseFraction = 0.15f;

        // How far the glow radius pulses each way from the sibling CompGlower's
        // own base glowRadius — the "dancing" half, read together with the
        // value pulse so the light visibly breathes, not just recolors.
        public float radiusPulseFraction = 0.12f;

        // Two independent sine periods (in ticks) summed together so the
        // result never repeats on a short, noticeably-looping cycle — a
        // single sine would read as a metronome, not a dancing flame. Left
        // deliberately un-synchronized (no shared factor) by their shipped
        // defaults (211 and 137 ticks).
        public int primaryPeriodTicks = 211;
        public int secondaryPeriodTicks = 137;

        // How often CompTick actually recomputes and re-registers the
        // glower — every tick would re-run the GlowGrid register/deregister
        // pair for no visible benefit; 12 ticks is 5 updates/second, smooth
        // to the eye and cheap on a handful of lamps per map.
        public int updateIntervalTicks = 12;

        // When true and the parent also carries a CompQuality (the statue's
        // case, not the lamp's), both pulse fractions are scaled by a
        // quality-derived factor — "flame display scales with art quality"
        // (item spec §4) — computed once per Apply() rather than baked into
        // the comp's own saved state, so a style/quality change (e.g. a
        // future re-carve) takes effect immediately.
        public bool qualityScalingEnabled;

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (compClass == null || !typeof(RM_Comp_WarblingGlow).IsAssignableFrom(compClass))
            {
                yield return "RM_CompProperties_WarblingGlow.compClass must be (or derive from) RM_Comp_WarblingGlow.";
            }

            if (parentDef.GetCompProperties<CompProperties_Glower>() == null)
            {
                yield return "RM_CompProperties_WarblingGlow requires a sibling CompProperties_Glower on the same ThingDef — nothing to warble.";
            }

            if (hueRangeDegrees < 0f || hueRangeDegrees > 180f)
            {
                yield return "RM_CompProperties_WarblingGlow.hueRangeDegrees should be within 0..180 (it wanders each way around the hue wheel).";
            }

            if (updateIntervalTicks < 1)
            {
                yield return "RM_CompProperties_WarblingGlow.updateIntervalTicks must be at least 1.";
            }
        }
    }
}
