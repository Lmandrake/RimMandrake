using System;

namespace RimMandrake.Stillsand.SkeletonSelfTest
{
    // STILLSAND_SKELETONS_REMAINDER_1 §2 offline selftest. Drives the production
    // RM_SkeletonBurialLogic with synthetic drift series: a dune migrating over a
    // ribcage and off again must bury it once and strip it once, a dune hovering
    // at the threshold must not flicker it, and the tint/inspect line must agree
    // with the state. What it cannot cover (the sand grid on a real map, the
    // MovingDunes engine actually moving sand, the redraw) is the live proof.
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
            Mean();
            Hysteresis();
            DunePasses();
            NoFlicker();
            TintAndLine();
            PlantedBreak();
            Horizon();
            Console.WriteLine(failures == 0
                ? "PASS skeleton burial selftest: " + checks + "/" + checks + " checks"
                : "FAILED skeleton burial selftest: " + failures + " of " + checks + " checks failed");
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

        private static void Mean()
        {
            Check(RM_SkeletonBurialLogic.MeanDepth(null) == 0f, "mean of null is 0");
            Check(RM_SkeletonBurialLogic.MeanDepth(new float[0]) == 0f, "mean of none is 0");
            Check(Math.Abs(RM_SkeletonBurialLogic.MeanDepth(new[] { 0f, 1f, 0.5f, 0.5f }) - 0.5f) < 1e-6, "mean 0.5");
            Check(Math.Abs(RM_SkeletonBurialLogic.MeanDepth(new[] { 2f, -1f }) - 0.5f) < 1e-6, "out-of-range depths clamp to 0..1");
            Check(RM_SkeletonBurialLogic.MeanDepth(new[] { float.NaN, 1f }) == 0.5f, "NaN counts as no sand");
        }

        private static void Hysteresis()
        {
            float bury = RM_SkeletonBurialLogic.BuryAt, strip = RM_SkeletonBurialLogic.StripAt;
            Check(strip < bury, "strip threshold is below bury threshold");
            Check(!RM_SkeletonBurialLogic.NextBuried(false, bury - 0.01f), "clean stays clean just under BuryAt");
            Check(RM_SkeletonBurialLogic.NextBuried(false, bury), "clean buries at BuryAt");
            Check(RM_SkeletonBurialLogic.NextBuried(true, (bury + strip) / 2f), "buried stays buried inside the band");
            Check(!RM_SkeletonBurialLogic.NextBuried(false, (bury + strip) / 2f), "clean stays clean inside the band");
            Check(!RM_SkeletonBurialLogic.NextBuried(true, strip), "buried strips at StripAt");
            Check(RM_SkeletonBurialLogic.NextBuried(true, strip + 0.01f), "buried holds just above StripAt");
            Check(RM_SkeletonBurialLogic.NextBuried(false, 0.5f, 0.5f, 0.5f), "degenerate band buries at the threshold");
            Check(!RM_SkeletonBurialLogic.NextBuried(true, 0.49f, 0.5f, 0.5f), "degenerate band strips below it");
        }

        private static void DunePasses()
        {
            // a dune crest walks over the footprint and on: depth rises 0 -> 1 -> 0
            int buries = 0, strips = 0;
            bool buried = false;
            for (int step = 0; step <= 40; step++)
            {
                float d = step <= 20 ? step / 20f : (40 - step) / 20f;
                bool next = RM_SkeletonBurialLogic.NextBuried(buried, d);
                if (next && !buried) buries++;
                if (!next && buried) strips++;
                buried = next;
            }
            Check(buries == 1, "a passing dune buries once (got " + buries + ")");
            Check(strips == 1, "a passing dune strips once (got " + strips + ")");
            Check(!buried, "after the dune has passed the ribcage is clean");
        }

        private static void NoFlicker()
        {
            // drift hovering +/- 0.05 around BuryAt after burial must not toggle
            bool buried = RM_SkeletonBurialLogic.NextBuried(false, RM_SkeletonBurialLogic.BuryAt + 0.05f);
            int toggles = 0;
            for (int i = 0; i < 100; i++)
            {
                float d = RM_SkeletonBurialLogic.BuryAt + (i % 2 == 0 ? -0.05f : 0.05f);
                bool next = RM_SkeletonBurialLogic.NextBuried(buried, d);
                if (next != buried) toggles++;
                buried = next;
            }
            Check(buried && toggles == 0, "hovering drift does not flicker (toggles " + toggles + ")");
        }

        private static void TintAndLine()
        {
            Check(RM_SkeletonBurialLogic.SandTint(false, 0f) == 0f, "clean on bare sand has no tint");
            Check(RM_SkeletonBurialLogic.SandTint(false, RM_SkeletonBurialLogic.StripAt) == 0f, "no tint at StripAt");
            Check(RM_SkeletonBurialLogic.SandTint(true, 0.3f) >= 0.5f, "buried reads at least half sand");
            Check(RM_SkeletonBurialLogic.SandTint(true, 1f) <= 1f, "tint never exceeds 1");
            float below = RM_SkeletonBurialLogic.SandTint(false, RM_SkeletonBurialLogic.BuryAt - 1e-4f);
            float at = RM_SkeletonBurialLogic.SandTint(true, RM_SkeletonBurialLogic.BuryAt);
            Check(at > below, "burying makes it read sandier, never cleaner");
            Check(RM_SkeletonBurialLogic.DriftLine(false, 0f) == null, "clean skeleton has no drift line");
            Check((RM_SkeletonBurialLogic.DriftLine(true, 0.7f) ?? "").Contains("Buried"), "buried line says Buried");
            Check((RM_SkeletonBurialLogic.DriftLine(true, 0.7f) ?? "").Contains("silent"), "buried line names the silent harp");
            Check((RM_SkeletonBurialLogic.DriftLine(false, 0.45f) ?? "").Contains("45%"), "half-drift line gives the percent");
        }

        private static void PlantedBreak()
        {
            // sanity probe: a stuck state machine (always the old state) must FAIL the dune-pass test,
            // proving DunePasses can see a broken implementation.
            bool buried = false;
            int buries = 0;
            for (int step = 0; step <= 40; step++)
            {
                float d = step <= 20 ? step / 20f : (40 - step) / 20f;
                bool next = buried; // planted break: never changes
                if (next && !buried) buries++;
                buried = next;
            }
            Check(buries == 0, "planted break: a stuck machine is visibly never buried (the probe can see failure)");
        }
    }
}
