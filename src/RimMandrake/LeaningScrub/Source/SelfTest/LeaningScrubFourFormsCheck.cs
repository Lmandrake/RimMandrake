using System;

namespace RimMandrake.LeaningScrub.SelfTest
{
    internal static class LeaningScrubFourFormsCheck
    {
        public static bool Run()
        {
            int bad = 0;
            void Eq(string n, bool got, bool want) { if (got != want) { bad++; Console.Error.WriteLine("FAIL " + n); } }
            void Near(string n, float got, float want) { if (Math.Abs(got - want) > 1e-4) { bad++; Console.Error.WriteLine("FAIL " + n + " " + got + " != " + want); } }
            Near("wrap climbs", RM_FourFormsKernel.WrapProgress(0.95f, 0.1f), 1f);
            Near("wrap never negative", RM_FourFormsKernel.WrapProgress(0.2f, -5f), 0.2f);
            Near("fresh wrap quarter", RM_FourFormsKernel.WrapDamage(0f, 8f), 2f);
            Near("full wrap full", RM_FourFormsKernel.WrapDamage(1f, 8f), 8f);
            Near("wrap clamps", RM_FourFormsKernel.WrapDamage(9f, 8f), 8f);
            Eq("ungrown no wrap", RM_FourFormsKernel.Wraps(true, 0.2f, 0.5f), false);
            Eq("off no wrap", RM_FourFormsKernel.Wraps(false, 1f, 0.5f), false);
            Eq("grown wraps", RM_FourFormsKernel.Wraps(true, 1f, 0.5f), true);
            Eq("weeps on low roll", RM_FourFormsKernel.WeepsNow(true, 1f, 0.5f, 0.01, 0.08f), true);
            Eq("no weep high roll", RM_FourFormsKernel.WeepsNow(true, 1f, 0.5f, 0.9, 0.08f), false);
            Eq("no weep off", RM_FourFormsKernel.WeepsNow(false, 1f, 0.5f, 0.0, 0.08f), false);
            if (RM_FourFormsKernel.PollutionRoom(20, 12) != 0 || RM_FourFormsKernel.PollutionRoom(-3, 12) != 12) { bad++; Console.Error.WriteLine("FAIL room"); }
            Eq("person wakes sleeper", RM_FourFormsKernel.Wakes(true, true, 1f, 0.5f, false, false), true);
            Eq("hare does not", RM_FourFormsKernel.Wakes(true, true, 0.2f, 0.5f, false, false), false);
            Eq("flyer does not", RM_FourFormsKernel.Wakes(true, true, 1f, 0.5f, true, false), false);
            Eq("awake stays", RM_FourFormsKernel.Wakes(true, false, 1f, 0.5f, false, false), false);
            Eq("lure drops", RM_FourFormsKernel.DropsFruit(true, 1f, 0.5f, 1, 3), true);
            Eq("lure capped", RM_FourFormsKernel.DropsFruit(true, 1f, 0.5f, 3, 3), false);
            Console.WriteLine(bad == 0 ? "four forms check: ok" : "four forms check: " + bad + " FAILED");
            return bad == 0;
        }
    }
}
