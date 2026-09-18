using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_LIVE_PREPARATIONS_1, the Mod Settings toggle the ticket names:
    // "viability: strict/lenient". The kit's own settings table is explicit
    // that ban 4 is NEVER fully off — "teas/symbionts keep both comps but
    // min-safe-temp gate relaxed — still expire".
    //
    // WHY A PATCH AND NOT A COMP SUBCLASS. The obvious build was a
    // CompTemperatureRuinable subclass with a lenient threshold, named by
    // the live-prep ThingDefs. That would have put ban 4's whole
    // enforcement behind a cross-mod class reference: RotSporeKit ships in
    // a mod list where mandrake.rm.environmentalhazards is NOT currently
    // active (ENVHAZARDS_NEVER_ACTIVATED_1), the <li> would drop on its own
    // MayRequire, and the teas would quietly become storable — the exact
    // ban the engine is supposed to be enforcing. So the ITEMS carry plain
    // VANILLA CompTemperatureRuinable + CompLifespan, which work with no
    // dependency at all, and the LENIENT option is this optional patch on
    // top. Strict (the shipped default) is therefore also what an install
    // without this assembly gets.
    //
    // Lenient skips temperature ruin entirely for a marked thing rather
    // than moving the threshold to some second invented number: the
    // accessible state (ruinedPercent) is protected and the two-number
    // version buys nothing a player can feel. CompLifespan is untouched
    // either way, so a lenient tea still dies on its own clock.
    //
    // Hot-path note: the prefix's first test is a static bool, so on the
    // shipped default this is one field read per ruinable-thing tick and
    // no dictionary or extension lookup at all.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_Patch_LivePrepViability
    {
        static RM_Patch_LivePrepViability()
        {
            MethodBase target = AccessTools.Method(typeof(CompTemperatureRuinable), nameof(CompTemperatureRuinable.CompTick));
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] live-prep-viability: CompTemperatureRuinable.CompTick "
                    + "not found — rule NOT armed. The engine signature this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target, prefix: new HarmonyMethod(
                    typeof(RM_Patch_LivePrepViability), nameof(CompTick_Prefix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] live-prep-viability: patch failed, rule NOT armed. " + e);
            }
        }

        // false = skip vanilla's temperature-ruin tick for this thing.
        public static bool CompTick_Prefix(CompTemperatureRuinable __instance)
        {
            if (RM_EnvironmentalHazardsSettings.livePrepStrictViability)
            {
                return true; // shipped default: vanilla behaviour, ban 4 at full strength
            }

            ThingDef def = __instance?.parent?.def;
            if (def == null)
            {
                return true;
            }

            return def.GetModExtension<RM_LivePrepExtension>() == null;
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // The live-prep marker. Two jobs, both of them "say out loud what this
    // item is" so nothing has to infer it from a defName prefix:
    //
    //   * the lenient-viability option above reads it at runtime;
    //   * src/RimUtinni/RotSporeKit/selftest_live_prep.py reads it on disk
    //     and FAILS if a def carrying it lacks either CompTemperatureRuinable
    //     or CompLifespan — the linter the ticket demands, so ban 4 is
    //     enforced by a test as well as by the engine.
    //
    // MayRequire this <li> in content XML: without this assembly the
    // extension class cannot resolve and an ungated modExtension entry
    // DISCARDS THE WHOLE DEF (not just the extension).
    // ════════════════════════════════════════════════════════════════════
    public class RM_LivePrepExtension : DefModExtension
    {
        // Free-text, for the inspect-string and for a future kit that wants
        // to group its own live preparations separately. Never parsed.
        public string preparationFamily;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
        }
    }
}
