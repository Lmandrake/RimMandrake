using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 Part 4 — the Sunbeam's UV.
    // "Low damage vs people + nasty sunburn scar hediffs; large multiplier vs
    // Contagion natives and the goo" (item §4). The base damage (low) and the
    // scar-prone hediff (RM_UVSunburn) live in the DamageDef/projectile XML;
    // this worker only multiplies the hit when the victim is a Contagion
    // native (RM_ContagionSky.IsNative: any race rostered on a biome carrying
    // RM_ContagionSkyExtension, plus that extension's extraNatives — the
    // Bloody Mess, "the goo", is rostered, so it is covered).
    public class DamageWorker_RM_UV : DamageWorker_AddInjury
    {
        public override DamageResult Apply(DamageInfo dinfo, Thing thing)
        {
            float factor = RM_ContagionSettings.sunbeamNativeFactor;
            if (factor > 1f && RM_ContagionSky.IsNative(thing))
            {
                dinfo.SetAmount(dinfo.Amount * factor);
            }
            return base.Apply(dinfo, thing);
        }
    }
}
