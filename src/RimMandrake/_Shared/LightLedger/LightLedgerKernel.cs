// LIGHT_LEDGER_ONE_1 — the arithmetic of one light's radius, with no Verse type in it so the offline
// selftest (src/RimMandrake/_Shared/LightLedger/SelfTest) compiles THIS file. Compiled into every
// consuming mod by a linked <Compile Include>; design: design/RimMandrake/light_ledger_design.md.
using System;
using System.Collections.Generic;

namespace RimMandrake.Shared
{
    internal static class LightLedgerKernel
    {
        // Modifier keys inside one light's dictionary. An owner's key follows the prefix: "mul:abyss.dark".
        public const string Base = "base";
        public const string Mul = "mul:";
        public const string Sub = "sub:";
        public const string Cap = "cap:";
        public const string Tag = "tag:";

        /// <summary>A written radius differs from the one already on the light by at least this, or nothing is written.</summary>
        public const float WriteTolerance = 0.01f;

        /// <summary>
        /// base × every multiplier − every subtraction, then no larger than any cap, then never below 0.
        /// <paramref name="defaultBase"/> is the def's own radius, used when no owner has set a base.
        /// </summary>
        public static float Compute(float defaultBase, IDictionary<string, float> mods)
        {
            if (mods == null || mods.Count == 0) return Math.Max(0f, defaultBase);
            float r = mods.TryGetValue(Base, out float b) ? b : defaultBase;
            float sub = 0f;
            float cap = float.MaxValue;
            foreach (KeyValuePair<string, float> kv in mods)
            {
                string k = kv.Key;
                if (k.StartsWith(Mul, StringComparison.Ordinal)) r *= kv.Value;
                else if (k.StartsWith(Sub, StringComparison.Ordinal)) sub += kv.Value;
                else if (k.StartsWith(Cap, StringComparison.Ordinal)) cap = Math.Min(cap, kv.Value);
            }
            r -= sub;
            if (r > cap) r = cap;
            return r < 0f ? 0f : r;
        }

        /// <summary>The radius before subtractions and caps: what sippers and grazers take a share OF.</summary>
        public static float Scaled(float defaultBase, IDictionary<string, float> mods)
        {
            if (mods == null) return Math.Max(0f, defaultBase);
            float r = mods.TryGetValue(Base, out float b) ? b : defaultBase;
            foreach (KeyValuePair<string, float> kv in mods)
            {
                if (kv.Key.StartsWith(Mul, StringComparison.Ordinal)) r *= kv.Value;
            }
            return r < 0f ? 0f : r;
        }

        /// <summary>
        /// The radius before subtractions and caps, leaving out one modifier: what an owner whose share is a
        /// PROPORTION (the sippers) scales against without counting itself.
        /// </summary>
        public static float ScaledExcept(float defaultBase, IDictionary<string, float> mods, string fullKey)
        {
            if (mods == null) return Math.Max(0f, defaultBase);
            float r = mods.TryGetValue(Base, out float b) ? b : defaultBase;
            foreach (KeyValuePair<string, float> kv in mods)
            {
                if (kv.Key != fullKey && kv.Key.StartsWith(Mul, StringComparison.Ordinal)) r *= kv.Value;
            }
            return r < 0f ? 0f : r;
        }

        /// <summary>
        /// Writes one modifier; the neutral value removes the key instead (mul 1, sub 0, cap below 0), so a
        /// light every effect has let go of carries an empty dictionary and reads as its plain base.
        /// Returns true when the dictionary changed.
        /// </summary>
        public static bool Set(IDictionary<string, float> mods, string key, float value)
        {
            bool neutral =
                (key.StartsWith(Mul, StringComparison.Ordinal) && Math.Abs(value - 1f) < 1e-6f)
                || (key.StartsWith(Sub, StringComparison.Ordinal) && Math.Abs(value) < 1e-6f)
                || (key.StartsWith(Cap, StringComparison.Ordinal) && value < 0f);
            if (neutral) return mods.Remove(key);
            if (mods.TryGetValue(key, out float old) && old == value) return false;
            mods[key] = value;
            return true;
        }

        public static bool NeedsWrite(float current, float want)
        {
            return Math.Abs(current - want) >= WriteTolerance;
        }
    }
}
