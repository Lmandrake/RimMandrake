// Unit group for the production static_call argument coercion and Thing lookup. Prints "U <name> ok" or
// "U <name> FAIL <why>" per case and "U-count <n>" last; driven by
// src/RimMandrake/Utils/selftest_static_call_args_core.py.
using System;
using System.Collections.Generic;
using Verse;
using C = JawaBench.BridgeTools.JawaBenchStaticCallArgsCore;

namespace JawaBench.BridgeTools
{
    internal enum Probe { Alpha, Beta }

    // jawa/comp_set writes one scalar field of a live comp (RIMMANDRAKE_DECIDE_SLACK_WALK_BAR_CODE_PLAYS_NO_WEEK)
    internal class Base0 { private int hidden = 3; public int Hidden() { return hidden; } }
    internal class Target : Base0
    {
        public int ticks = 12;
        private bool on = false;
        public readonly int fixedOne = 1;
        public const int Never = 5;
        public int[] list = new int[0];
        public bool On() { return on; }
    }

    internal static class Program
    {
        static int n;

        static void U(string name, bool ok, string why = "")
        {
            n++;
            Console.WriteLine("U " + name + (ok ? " ok" : " FAIL " + why));
        }

        // value and exact runtime type must both match: MethodInfo.Invoke refuses an Int32 boxed for an Int64 slot
        static void Is(string name, Type pt, string a, object want)
        {
            try
            {
                bool h = C.Handles(pt);
                object got = h ? C.Coerce(pt, a) : null;
                U(name, h && got != null && got.GetType() == want.GetType() && got.Equals(want),
                    "handles=" + h + " got=" + (got == null ? "null" : got + " (" + got.GetType().Name + ")"));
            }
            catch (Exception e) { U(name, false, e.GetType().Name + ": " + e.Message); }
        }

        static void Throws(string name, Type pt, string a)
        {
            try { object got = C.Coerce(pt, a); U(name, false, "accepted as " + got); }
            catch (Exception) { U(name, true); }
        }

        static void ThingArgs()
        {
            var titan = new Thing { ThingID = "RM_TestTitanT253196", thingIDNumber = 53196 };
            Find.CurrentMap = new Map();
            Find.CurrentMap.listerThings.AllThings.Add(titan);
            Find.Maps = new List<Map> { Find.CurrentMap };

            Thing got = JawaBenchTerrainTools.ResolveThingForTest(titan.ThingID, out string foundAt);
            U("thing_id.digit_ending_def_name", got == titan && foundAt == "current map, by ThingID",
                "expected RM_TestTitanT253196 (#53196), got " + (got?.ThingID ?? "no match"));

            got = JawaBenchTerrainTools.ResolveThingForTest("53196", out foundAt);
            U("thing_id.bare_number", got == titan && foundAt == "current map, by thingIDNumber",
                "expected #53196, got " + (got?.ThingID ?? "no match"));
        }

        static int Main()
        {
            // ---------------- the pour-label case: RM_GodLiquidMath.StepLabel(long)
            Is("long.100", typeof(long), "100", 100L);
            Is("long.1000", typeof(long), "1000", 1000L);
            Is("long.full_pit_2048000", typeof(long), "2048000", 2048000L);
            Is("long.beyond_int32", typeof(long), "4294967296", 4294967296L);
            Is("long.negative", typeof(long), "-7", -7L);
            Throws("long.garbage_refused", typeof(long), "12x");
            Throws("long.overflow_refused", typeof(long), "9223372036854775808");

            // ---------------- the other integer widths
            Is("ulong.max", typeof(ulong), "18446744073709551615", ulong.MaxValue);
            Is("uint.big", typeof(uint), "4000000000", 4000000000u);
            Is("short", typeof(short), "-300", (short)-300);
            Is("ushort", typeof(ushort), "60000", (ushort)60000);
            Is("byte", typeof(byte), "255", (byte)255);
            Is("sbyte", typeof(sbyte), "-128", (sbyte)-128);
            Throws("byte.overflow_refused", typeof(byte), "256");
            Is("decimal", typeof(decimal), "0.1", 0.1m);

            // ---------------- unchanged behaviour
            Is("int", typeof(int), "42", 42);
            Throws("int.beyond_int32_refused", typeof(int), "4294967296");
            Is("float.invariant", typeof(float), "1.5", 1.5f);
            Is("double.invariant", typeof(double), "2.25", 2.25);
            Is("bool", typeof(bool), "true", true);
            Is("string", typeof(string), "a b", "a b");

            // ---------------- enums, by name or number
            Is("enum.by_name", typeof(Probe), "Beta", Probe.Beta);
            Is("enum.by_name_any_case", typeof(Probe), "beta", Probe.Beta);
            Is("enum.by_number", typeof(Probe), "0", Probe.Alpha);
            Throws("enum.unknown_name_refused", typeof(Probe), "Gamma");
            Throws("enum.undefined_number_refused", typeof(Probe), "9");

            // ---------------- not ours: the game-typed cases stay in the tool
            U("handles.not_object", !C.Handles(typeof(object)));
            U("handles.not_array", !C.Handles(typeof(int[])));

            // ---------------- SetField (jawa/comp_set): the write reads back, a wrong ask is refused and writes nothing
            var t = new Target();
            string e1 = C.SetField(t, "ticks", "60000", out object was, out object now);
            U("set.public_int", e1 == null && (int)was == 12 && (int)now == 60000 && t.ticks == 60000, e1);
            e1 = C.SetField(t, "on", "true", out was, out now);
            U("set.private_bool", e1 == null && t.On(), e1);
            e1 = C.SetField(t, "hidden", "9", out was, out now);
            U("set.private_of_base", e1 == null && t.Hidden() == 9, e1);
            e1 = C.SetField(t, "nope", "1", out was, out now);
            U("set.missing_member_refused", e1 != null && e1.Contains("nope"), e1);
            e1 = C.SetField(t, "list", "1", out was, out now);
            U("set.not_scalar_refused", e1 != null && t.list.Length == 0, e1);
            e1 = C.SetField(t, "ticks", "12x", out was, out now);
            U("set.bad_text_refused_unwritten", e1 != null && t.ticks == 60000, e1);
            e1 = C.SetField(t, "fixedOne", "7", out was, out now);
            U("set.readonly_refused", e1 != null && t.fixedOne == 1, e1);
            e1 = C.SetField(t, "Never", "7", out was, out now);
            U("set.const_refused", e1 != null, e1);
            ThingArgs();

            Console.WriteLine("U-count " + n);
            return 0;
        }
    }
}
