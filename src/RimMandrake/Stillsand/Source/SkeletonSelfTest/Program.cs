using System;

namespace RimMandrake.Stillsand.SkeletonSelfTest
{
    // Offline selftest of the skeleton kit's pure math: the dust-on-the-horizon timing (RM_HorizonMath).
    // (The dune-burial logic it also covered was cut 2026-10-23, fluff review.)
    internal static class Program
    {
        private static int failures;
        private static int checks;

        private static void Check(bool ok, string what)
        {
            checks++;
            if (!ok)
            {
                failures++;
                Console.WriteLine("FAIL " + what);
            }
        }

        private static int Main()
        {
            Horizon();
            Console.WriteLine(failures == 0
                ? "PASS skeleton selftest: " + checks + "/" + checks + " checks"
                : "FAILED skeleton selftest: " + failures + " of " + checks + " checks failed");
            return failures == 0 ? 0 : 1;
        }

        // DUST_SETTLED_LETTER_1: the plume outlives the announced fire tick through the retry window; a group that never
        // arrives turns back only AFTER the window; an arrived group never turns back; entries match by def + cell.
        private static void Horizon()
        {
            int fire = 10000;
            Check(RM_HorizonMath.PlumeUntil(fire) > fire + RM_HorizonMath.RetryTicks - 1, "plume stands through the retry window, not just to the fire tick");
            Check(!RM_HorizonMath.TurnedBack(fire, fire, false), "not turned back at the fire tick (the queue is still retrying)");
            Check(!RM_HorizonMath.TurnedBack(fire + RM_HorizonMath.RetryTicks, fire, false), "not turned back at the end of the retry window");
            Check(RM_HorizonMath.TurnedBack(RM_HorizonMath.PlumeUntil(fire) + 1, fire, false), "turned back once the window and grace are past");
            Check(!RM_HorizonMath.TurnedBack(fire * 100, fire, true), "an arrived group never turns back");
            Check(RM_HorizonMath.Matches("RaidEnemy", 3, 4, "RaidEnemy", 3, 4), "same def and cell match");
            Check(!RM_HorizonMath.Matches("RaidEnemy", 3, 4, "RaidEnemy", 3, 5), "another cell does not match");
            Check(!RM_HorizonMath.Matches("RaidEnemy", 3, 4, "TraderCaravanArrival", 3, 4), "another def does not match");
            Check(!RM_HorizonMath.Matches("", 3, 4, "", 3, 4), "an untracked (older save) entry never matches");
        }
    }
}
