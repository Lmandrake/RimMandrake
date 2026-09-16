using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// FURNACEBEAST_THERMAL_CYCLE_1, part 1 — TRUE fire and heat immunity.
    ///
    /// 🔑 OWNER, 2026-09-14, verbatim: "totally resistant to fire and heat based
    /// attacks". The XML half shipped first and is NOT enough on its own:
    /// ArmorRating_Heat 2.0 is a very good roll, not a guarantee, and armour is
    /// rolled per-hit against the attack's armour penetration. "Totally" needs a
    /// gate that does not roll dice.
    ///
    /// 🔴 WHAT IS ALREADY TRUE IN XML AND MUST NOT BE RE-IMPLEMENTED HERE:
    ///
    ///   - NEVER IGNITES. VERIFIED against the engine, not assumed:
    ///     FireUtility.CanEverAttachFire (RimWorld/FireUtility.cs:19) returns
    ///     false the moment !t.FlammableNow, and FlammableNow reads the
    ///     Flammability stat, which RUT_FurnaceBeast sets to 0 in statBases.
    ///     Every ignition route in the game funnels through TryAttachFire ->
    ///     CanEverAttachFire (DamageWorker_Flame, FlameThrower, Verb_ShootBeam,
    ///     Fire.TrySpread, HediffGiver_Terrain). So the beast cannot catch fire
    ///     and no C# is owed for it. Do not add a second guard.
    ///   - NEVER OVERHEATS. ComfyTemperatureMax 1000 clears any temperature the
    ///     map can reach, burning grass cell included.
    ///
    /// WHAT THIS PATCH ADDS, and only this: zero damage from heat-category
    /// attacks. The gate is DATA-DRIVEN — DamageDef.armorCategory == Heat —
    /// rather than a hand-written list of defNames, so it covers Flame, Burn,
    /// Vaporize and Beam (VERIFIED: the four Core DamageDefs carrying
    /// &lt;armorCategory&gt;Heat&lt;/armorCategory&gt;) AND every modded
    /// flamethrower, incendiary and plasma weapon in the stack without this file
    /// ever being edited again. A defName list would have covered four and
    /// silently missed the rest.
    ///
    /// ⚠️ Prefix, not postfix, and it returns false: absorbed damage must never
    /// reach Pawn_HealthTracker.PreApplyDamage at all, or the beast still takes
    /// the hediff and the job interruption while taking no injury.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class Patch_FurnaceBeastHeatImmunity
    {
        /// <summary>Resolved once at startup. Null-checked at every call site:
        /// an absent Heat armour category means the patch declines to absorb,
        /// which degrades to the XML armour rating rather than to a crash.</summary>
        internal static DamageArmorCategoryDef HeatCategory;

        /// <summary>The beast itself. A ThingDef reference rather than a string
        /// compare in a damage path, and a null one (this mod loaded without the
        /// igniter mod) makes the whole patch a no-op.</summary>
        internal static ThingDef FurnaceBeastDef;

        static Patch_FurnaceBeastHeatImmunity()
        {
            HeatCategory = DefDatabase<DamageArmorCategoryDef>.GetNamedSilentFail("Heat");
            FurnaceBeastDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_FurnaceBeast");

            if (FurnaceBeastDef == null)
            {
                // The igniter mod is not loaded. Nothing to protect; say so once
                // rather than patching a hot path for nobody.
                return;
            }
            if (HeatCategory == null)
            {
                Log.Error("[RimMandrake.Utinni.PyrelandsMechanics] furnace-beast heat immunity: "
                        + "no DamageArmorCategoryDef named 'Heat' — the rule is NOT in effect and "
                        + "the beast falls back to its XML ArmorRating_Heat. A game update renamed it.");
                return;
            }

            try
            {
                new Harmony("mandrake.rut.pyrelandsmechanics").Patch(
                    AccessTools.Method(typeof(Pawn), nameof(Pawn.PreApplyDamage)),
                    prefix: new HarmonyMethod(typeof(Patch_FurnaceBeastHeatImmunity), nameof(Prefix)));
                Log.Message("[RimMandrake.Utinni.PyrelandsMechanics] furnace-beast heat immunity: armed; "
                          + "RUT_FurnaceBeast absorbs all Heat-category damage.");
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Utinni.PyrelandsMechanics] furnace-beast heat immunity: patch "
                        + "FAILED, rule NOT in effect — " + e.Message);
            }
        }

        /// <summary>
        /// Returns false (skip the original) only for the one species and the one
        /// damage category. Everything else in the game reaches this method and
        /// leaves it untouched on the very first comparison.
        /// </summary>
        public static bool Prefix(Pawn __instance, ref DamageInfo dinfo, ref bool absorbed)
        {
            try
            {
                if (!PyrelandsMechanicsSettings.furnaceHeatImmunityEnabled)
                {
                    return true;
                }
                if (FurnaceBeastDef == null || __instance == null || __instance.def != FurnaceBeastDef)
                {
                    return true;
                }
                if (dinfo.Def == null || HeatCategory == null || dinfo.Def.armorCategory != HeatCategory)
                {
                    return true;
                }

                absorbed = true;
                return false;
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Utinni.PyrelandsMechanics] furnace-beast heat immunity: "
                              + e.Message, 0x46E11);
                return true;
            }
        }
    }
}
