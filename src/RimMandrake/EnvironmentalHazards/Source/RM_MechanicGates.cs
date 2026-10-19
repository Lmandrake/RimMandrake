using System;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD_FLOOR_PASS_1. The seam that lets a biome mod's own Mod Settings
    // switch off a mechanic whose C# lives in THIS shared assembly, without
    // this assembly ever referencing that mod (load order runs the other way:
    // mandrake.rm.terminalbiomes loadsAfter this one, so a reference from
    // here to there is forbidden).
    //
    // Two halves, both content-agnostic:
    //   - RM_MechanicGateExtension: a def (GameConditionDef, IncidentDef,
    //     GenStepDef, ThingDef ...) opts into a gate by carrying this
    //     extension with a string gateKey. A def with no extension is never
    //     gated — so every Greentide/Forge/Sump def that shares these classes
    //     behaves exactly as before.
    //   - RM_MechanicGates: a static registry of gateKey -> Func<bool>, filled
    //     by the owning mod's Mod constructor. An unregistered key reads
    //     ENABLED — a def gated to a mod that is absent, or that never
    //     registered, degrades to "on", never to a silent kill.
    //
    // Consumers call RM_MechanicGates.Enabled(def) at their own entry point
    // (CompTick, CanFireNowSub, ShouldSkipMap, GameConditionTick ...), never
    // by removing the def — a toggle flip takes effect on the next tick and
    // flipping it back restores the mechanic with nothing lost.
    public class RM_MechanicGateExtension : DefModExtension
    {
        public string gateKey;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }
            if (gateKey.NullOrEmpty())
            {
                yield return "RM_MechanicGateExtension has no gateKey — the def will never be gated.";
            }
        }
    }

    public static class RM_MechanicGates
    {
        private static readonly Dictionary<string, Func<bool>> gates = new Dictionary<string, Func<bool>>();

        /// <summary>Register (or replace) the predicate behind a gate key.
        /// Call from a Mod constructor; the predicate is re-read on every
        /// Enabled() call, so it should read live settings fields, not a
        /// snapshot.</summary>
        public static void Register(string key, Func<bool> isEnabled)
        {
            if (key.NullOrEmpty() || isEnabled == null)
            {
                Log.Error("[RM EnvironmentalHazards] RM_MechanicGates.Register called with an empty key or null predicate.");
                return;
            }
            gates[key] = isEnabled;
        }

        /// <summary>True unless a registered predicate for this key says
        /// false. Unregistered or empty keys are enabled.</summary>
        public static bool Enabled(string key)
        {
            if (key.NullOrEmpty() || !gates.TryGetValue(key, out Func<bool> isEnabled))
            {
                return true;
            }
            try
            {
                return isEnabled();
            }
            catch (Exception e)
            {
                Log.ErrorOnce(
                    "[RM EnvironmentalHazards] mechanic gate '" + key + "' threw; treating as enabled. " + e,
                    key.GetHashCode() ^ 0x6A7E);
                return true;
            }
        }

        // SUMP_TAR_LIVING_SYSTEMS_1: the same seam for a NUMBER (a frequency or intensity multiplier a biome mod's
        // setting owns). An unregistered key reads 1 (the def's own figure), so absence degrades to shipped behaviour.
        private static readonly Dictionary<string, Func<float>> scales = new Dictionary<string, Func<float>>();

        /// <summary>Register (or replace) the live reader behind a scale key. Call from a Mod constructor.</summary>
        public static void RegisterScale(string key, Func<float> scale)
        {
            if (key.NullOrEmpty() || scale == null)
            {
                Log.Error("[RM EnvironmentalHazards] RM_MechanicGates.RegisterScale called with an empty key or null reader.");
                return;
            }
            scales[key] = scale;
        }

        /// <summary>The registered multiplier for this key, or 1 when the key is empty or unregistered. A reader that
        /// throws or returns NaN reads 1, never a silent kill.</summary>
        public static float Scale(string key)
        {
            if (key.NullOrEmpty() || !scales.TryGetValue(key, out Func<float> scale))
            {
                return 1f;
            }
            try
            {
                float v = scale();
                return float.IsNaN(v) ? 1f : v;
            }
            catch (Exception e)
            {
                Log.ErrorOnce(
                    "[RM EnvironmentalHazards] mechanic scale '" + key + "' threw; treating as 1. " + e,
                    key.GetHashCode() ^ 0x5CA1);
                return 1f;
            }
        }

        /// <summary>True unless the def carries an RM_MechanicGateExtension
        /// whose key is registered and currently off.</summary>
        public static bool Enabled(Def def)
        {
            RM_MechanicGateExtension ext = def?.GetModExtension<RM_MechanicGateExtension>();
            return ext == null || Enabled(ext.gateKey);
        }
    }
}
