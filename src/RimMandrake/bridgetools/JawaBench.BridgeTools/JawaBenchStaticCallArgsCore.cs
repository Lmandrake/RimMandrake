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
using System.Reflection;

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

        /// <summary>True when <paramref name="pt"/> is a delegate that returns nothing (Action, Action&lt;T&gt;, a
        /// void callback type). jawa/static_call takes one as 'noop'. Kept out of <see cref="Handles"/> so
        /// jawa/comp_set never writes a delegate field.</summary>
        public static bool IsVoidDelegate(Type pt)
        {
            if (pt == null || !typeof(Delegate).IsAssignableFrom(pt) || pt == typeof(Delegate) || pt == typeof(MulticastDelegate))
                return false;
            MethodInfo invoke = pt.GetMethod("Invoke");
            return invoke != null && invoke.ReturnType == typeof(void);
        }

        /// <summary>'noop' -> a delegate of <paramref name="pt"/> that does nothing; 'null' or empty -> null.
        /// Any other text, or a delegate that returns a value, throws ArgumentException.
        /// LAUNCH_HELD_COLONIST_WARNING_1: vanilla GravshipUtility.PreLaunchConfirmation(engine, Action) builds the
        /// launch dialog; a live test reads that dialog, so its launch callback must do nothing.</summary>
        public static Delegate Noop(Type pt, string a)
        {
            if (!IsVoidDelegate(pt)) throw new ArgumentException(pt?.Name + " is not a delegate that returns nothing");
            string s = (a ?? "").Trim();
            if (s.Length == 0 || s == "null") return null;
            if (s != "noop") throw new ArgumentException("a delegate argument takes 'noop' (does nothing) or 'null', not '" + a + "'");
            if (pt == typeof(Action)) return (Action)NoopBody;
            ParameterInfo[] ps = pt.GetMethod("Invoke").GetParameters();
            var args = new System.Linq.Expressions.ParameterExpression[ps.Length];
            for (int i = 0; i < ps.Length; i++) args[i] = System.Linq.Expressions.Expression.Parameter(ps[i].ParameterType);
            return System.Linq.Expressions.Expression.Lambda(pt, System.Linq.Expressions.Expression.Empty(), args).Compile();
        }

        static void NoopBody() { }

        /// <summary>jawa/comp_set: write one scalar instance field (private and inherited ones too) and read it back.
        /// Returns null when written, else the refusal; a refusal writes nothing.</summary>
        public static string SetField(object target, string member, string text, out object before, out object after)
        {
            before = after = null;
            const BindingFlags F = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
            FieldInfo fi = null;
            for (Type t = target.GetType(); t != null && fi == null; t = t.BaseType) fi = t.GetField(member ?? "", F);
            if (fi == null) return "No instance field '" + member + "' on " + target.GetType().FullName + ".";
            if (fi.IsInitOnly) return "Field '" + member + "' is readonly.";
            if (!Handles(fi.FieldType)) return "Field '" + member + "' is a " + fi.FieldType.Name + ", not a scalar.";
            object v;
            try { v = Coerce(fi.FieldType, (text ?? "").Trim()); }
            catch (Exception e) { return "Cannot coerce '" + text + "' to " + fi.FieldType.Name + ": " + e.Message; }
            before = fi.GetValue(target);
            fi.SetValue(target, v);
            after = fi.GetValue(target);
            return null;
        }
    }
}
