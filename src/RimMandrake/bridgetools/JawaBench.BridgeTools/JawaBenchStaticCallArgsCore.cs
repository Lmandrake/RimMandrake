// JawaBenchStaticCallArgsCore.cs - the Verse-free scalar coercion behind jawa/static_call
// (JawaBenchCompanionProbeTools.cs): one '|'-separated text argument -> the parameter's CLR type.
//
// Kept free of RimWorld/Unity references ON PURPOSE: bridgetools/StaticCallArgsSelfTest compiles
// THIS production file into a plain net8.0 harness (src/RimMandrake/Utils/selftest_static_call_args_core.py),
// so a `using Verse;` here breaks that build - the guard rail working.
//
// Why it exists (RIMMANDRAKE_PASS_BRIDGE_STATIC_CALL_INT64_POUR_LABELS_UNASKED): the tool knew only
// int/float/double/bool/string, so RM_GodLiquidMath.StepLabel(long) was refused "Unsupported parameter
// type Int64" and FlowWorks visit 1 left three pour-label rows UNMEASURED.

using System;
using System.Globalization;

namespace JawaBench.BridgeTools
{
    public static class JawaBenchStaticCallArgsCore
    {
        /// <summary>True when <paramref name="pt"/> is a scalar this core coerces (the game-typed
        /// cases - IntVec3, Map, Def, Thing - stay in the tool).</summary>
        public static bool Handles(Type pt)
        {
            return pt.IsEnum || pt == typeof(string) || pt == typeof(bool) || Integral(pt) ||
                pt == typeof(float) || pt == typeof(double) || pt == typeof(decimal);
        }

        static bool Integral(Type pt)
        {
            return pt == typeof(int) || pt == typeof(long) || pt == typeof(short) || pt == typeof(sbyte) ||
                pt == typeof(uint) || pt == typeof(ulong) || pt == typeof(ushort) || pt == typeof(byte);
        }

        /// <summary>Coerce trimmed text <paramref name="a"/> to <paramref name="pt"/>; throws on
        /// malformed or out-of-range text (the tool reports "Cannot coerce arg i").</summary>
        public static object Coerce(Type pt, string a)
        {
            if (pt == typeof(string)) return a;
            if (pt == typeof(bool)) return bool.Parse(a);
            if (pt.IsEnum)
            {
                // a name (any case) or a number, refused unless it names a defined member
                object e = Enum.Parse(pt, a, true);
                if (!Enum.IsDefined(pt, e)) throw new ArgumentException("'" + a + "' is not a defined " + pt.Name);
                return e;
            }
            if (Integral(pt))
            {
                // parsed exactly at the parameter's own width: Invoke refuses an Int32 boxed for an Int64 slot,
                // and an out-of-range value is an OverflowException, never a silent wrap
                return Convert.ChangeType(decimal.Parse(a, NumberStyles.Integer, CultureInfo.InvariantCulture), pt, CultureInfo.InvariantCulture);
            }
            if (pt == typeof(float)) return float.Parse(a, CultureInfo.InvariantCulture);
            if (pt == typeof(double)) return double.Parse(a, CultureInfo.InvariantCulture);
            if (pt == typeof(decimal)) return decimal.Parse(a, CultureInfo.InvariantCulture);
            throw new ArgumentException("not a scalar this core coerces: " + pt.Name);
        }
    }
}
