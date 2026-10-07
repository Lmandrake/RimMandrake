// GPT source read 2026-10-06 (design/RimMandrake/gss_gpt_source_read_2026-10-06.md): one offline row per fixed finding whose
// logic is Verse-free (the Verse-bound fixes are checked by validation.py O7). Each row carries a can-fail: the old rule
// computed beside the new one must give the wrong answer the finding described.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Hose;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class GptReadFixChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "gptfix: " + msg);

        public static void Run()
        {
            // B4: the reel's port cache starts at int.MinValue and must read as stale, not fresh
            Check(!HoseLive.CacheFresh(0, int.MinValue, 60), "B4 never-read port cache is stale at tick 0");
            Check(!HoseLive.CacheFresh(123456, int.MinValue, 60), "B4 never-read port cache is stale later in the game");
            Check(HoseLive.CacheFresh(100, 70, 60) && !HoseLive.CacheFresh(130, 70, 60), "B4 a read 30 ticks ago is fresh, 60 ago is not");
            Check(unchecked(0 - int.MinValue) < 60, "B4 can-fail: the old int subtraction overflows to fresh");

            // A19: lit and dark power strips draw at the same aspect (both PNGs are 64x32)
            Check(DecalAspect.Of(DecalKind.PowerStripDark) == DecalAspect.Of(DecalKind.PowerStrip) && DecalAspect.Of(DecalKind.PowerStrip) == 0.5f,
                  "A19 dark power strip aspect == lit == 0.5");
            Check(DecalAspect.Of(DecalKind.Plug) == 1f, "A19 can-fail: a square decal keeps aspect 1");

            // A1: two 500 W taps on a victim with 600 W surplus and no battery share 600 W, never 1000 W
            double k = 1.0 / 60000;
            double t1 = AerialMath.TapStolenPerTick(500, 600 * k, 0, k, false, true, 0, true);
            double t2 = AerialMath.TapStolenPerTick(500, 600 * k, 0, k, false, true, t1, true);
            Check(Math.Abs(t1 + t2 - 600 * k) < 1e-12, "A1 two taps share a 600 W surplus: " + ((t1 + t2) / k).ToString("0") + " W");
            Check(AerialMath.TapStolenPerTick(500, 600 * k, 0, k, false, true) * 2 > 600 * k * 1.5, "A1 can-fail: the old rule lets both claim 500 W");
            Check(Math.Abs(AerialMath.TapStolenPerTick(500, 600 * k, 1000 * k, k, false, true, 500 * k, true) - 500 * k) < 1e-12,
                  "A1 the second tap still drinks from stored energy once the surplus is gone");
            // A2: a switched-off or broken clamp drains nothing
            Check(AerialMath.TapStolenPerTick(500, 1000 * k, 600, k, false, true, 0, false) == 0, "A2 switched-off tap takes 0");
            Check(AerialMath.TapStolenPerTick(500, 1000 * k, 600, k, false, true, 0, true) > 0, "A2 can-fail: the same tap switched on takes power");
        }
    }
}
