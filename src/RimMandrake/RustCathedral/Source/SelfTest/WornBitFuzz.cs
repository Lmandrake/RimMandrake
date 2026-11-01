// RUSTCATHEDRAL_WORN_BIT_ARC_1: the arc kernel's gates and arithmetic, stated from the item's own criteria.
using System;
using System.Collections.Generic;

namespace RimMandrake.RustCathedral.Hum.SelfTest
{
    internal static class WornBitFuzz
    {
        private static int fails;

        private static void Check(string name, bool ok)
        {
            Console.WriteLine((ok ? "ok    " : "FAIL  ") + name);
            if (!ok) fails++;
        }

        public static bool Run()
        {
            float p = 0f;
            for (int i = 0; i < 2500; i++) p += RM_WornBitKernel.UnbitDelta(1, 1f, 0, false);
            Check("a lone worker adds nothing in 2,500 ticks", p == 0f);
            p = 0f;
            for (int i = 0; i < 2500; i++) p += 2 * RM_WornBitKernel.UnbitDelta(2, 1f, 1, false);
            Check("two workers raise it at band 1, one unit a tick", Math.Abs(p - 2500f) < 0.01f);
            Check("band 2 stops the work", RM_WornBitKernel.UnbitDelta(2, 1f, 2, false) == 0f);
            Check("a non-attitude map (-1) stops the work", RM_WornBitKernel.UnbitDelta(2, 1f, -1, false) == 0f);
            Check("a moving hulk stops the work", RM_WornBitKernel.UnbitDelta(2, 1f, 0, true) == 0f);
            Check("fee scales up with wealth", RM_WornBitKernel.ScaledFee(1500, 1.5f) == 2250);
            Check("fee clamps low", RM_WornBitKernel.ScaledFee(1500, 0.01f) == 1125);
            Check("fee clamps high", RM_WornBitKernel.ScaledFee(1500, 50f) == 3000);
            Check("a failed haggle raises the fee", RM_WornBitKernel.HaggledFee(1500, false) > 1500);
            Check("a good haggle lowers the fee", RM_WornBitKernel.HaggledFee(1500, true) < 1500);
            Check("haggle odds rise with Social and stay inside 0..1", RM_WornBitKernel.HaggleChance(0) < RM_WornBitKernel.HaggleChance(15) && RM_WornBitKernel.HaggleChance(99) <= 1f && RM_WornBitKernel.HaggleChance(-5) >= 0f);
            Check("everything present: none short", RM_WornBitKernel.FirstShort(new[] { 1, 12 }, new[] { 1, 12 }) == -1);
            Check("any one missing is named", RM_WornBitKernel.FirstShort(new[] { 1, 12, 6 }, new[] { 1, 11, 6 }) == 1);
            Check("delta scales by the multiplier", RM_WornBitKernel.Scaled(-15, 3f) == -45 && RM_WornBitKernel.ScaledF(10f, 3f) == 30f);
            Check("multiplier 0 removes the delta", RM_WornBitKernel.Scaled(-15, 0f) == 0);
            int iv = 300000;
            Check("serviced now: full bar", RM_WornBitKernel.MaintenanceLeft(1000, 1000, iv) == 1f);
            Check("half way: half bar", Math.Abs(RM_WornBitKernel.MaintenanceLeft(151000, 1000, iv) - 0.5f) < 0.001f);
            Check("5 days unserviced: it stops digging", !RM_WornBitKernel.KeptMayDig(true, 301000, 1000, iv));
            Check("maintenance off: it never stops", RM_WornBitKernel.KeptMayDig(false, 9999999, 1000, iv));
            Check("first favour is ready", RM_WornBitKernel.FavourReady(100, -1, 900000));
            Check("favour cooldown holds", !RM_WornBitKernel.FavourReady(900000, 1000, 900000));
            Check("favour cooldown ends", RM_WornBitKernel.FavourReady(901000, 1000, 900000));
            Check("the choice falls due at half", RM_WornBitKernel.ChoiceDue(6000f, 12000f, RM_WornBitChoice.None) && !RM_WornBitKernel.ChoiceDue(5999f, 12000f, RM_WornBitChoice.None));
            Check("a choice taken is never asked again", !RM_WornBitKernel.ChoiceDue(9000f, 12000f, RM_WornBitChoice.Keep));
            Check("dig is ten colonists at the default", Math.Abs(RM_WornBitKernel.ColonistDigPerTick * 10f - 8f) < 0.001f);
            // a seeded walk: progress never falls and only moves under the gate
            var r = new Random(20261002);
            float q = 0f;
            bool ok = true;
            for (int i = 0; i < 20000; i++)
            {
                int w = r.Next(0, 5), band = r.Next(-1, 6);
                bool moving = r.Next(4) == 0;
                float d = RM_WornBitKernel.UnbitDelta(w, 0.5f + (float)r.NextDouble(), band, moving);
                bool gate = w >= 2 && band >= 0 && band <= 1 && !moving;
                ok &= d >= 0f && (d > 0f) == gate;
                q += d;
            }
            Check("20,000 seeded ticks: progress moves exactly under the gate", ok && q > 0f);
            Console.WriteLine("WORNBIT " + (fails == 0 ? "PASS" : "FAIL") + " (" + fails + " failures)");
            return fails == 0;
        }
    }
}
