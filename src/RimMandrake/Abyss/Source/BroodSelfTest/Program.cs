using System;

namespace RimMandrake.Abyss.BroodSelfTest
{
    // ABYSS_LIGHTFALL_BROOD_WRECK_1 offline selftest. Drives the production RM_BroodWakeLogic.cs:
    // the hidden line, the signs in order and always before the wake, the greed dial (a modest haul is
    // safe at every roll, the whole haul plus the egg wakes her at every roll), decay that softens greed
    // without erasing it, the egg refund, the imprint gate, the ship's accept/refuse, the repair spread,
    // and the bane's victim choice. Plus a planted-break probe. What it cannot cover (a real map, the
    // genstep finding room in a chasm, bills at the wreck, a hatch) is L1/L2 live proof.
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

        private static bool Near(float a, float b) { return Math.Abs(a - b) < 1e-4f; }

        private static int Main()
        {
            Threshold();
            SignsInOrder();
            SignAlwaysBeforeWake();
            GreedDial();
            DecayFloor();
            Rearm();
            EggRefund();
            Imprint();
            ShipFit();
            Spread();
            Bane();
            PlantedBreak();
            if (failures == 0)
            {
                Console.WriteLine("PASS abyss brood selftest: " + checks + "/" + checks + " checks");
                return 0;
            }
            Console.WriteLine("FAIL abyss brood selftest: " + failures + " of " + checks + " checks failed");
            return 1;
        }

        private static void Threshold()
        {
            Check(Near(BroodWakeLogic.RollThreshold(0f, 1f), 0.85f), "lowest roll is 0.85");
            Check(Near(BroodWakeLogic.RollThreshold(1f, 1f), 1.15f), "highest roll is 1.15");
            Check(Near(BroodWakeLogic.RollThreshold(0.5f, 2f), 2.0f), "sleep depth 2 doubles the line");
            Check(Near(BroodWakeLogic.RollThreshold(-3f, 1f), 0.85f) && Near(BroodWakeLogic.RollThreshold(9f, 1f), 1.15f), "roll is clamped");
            Check(BroodWakeLogic.RollThreshold(0f, 0f) > 0f, "a zero sleep depth never makes a zero line");
        }

        private static void SignsInOrder()
        {
            var w = new BroodWakeLogic { threshold = 1f };
            Check(w.Add(0.3f) == BroodStage.Asleep, "0.30: no sign");
            Check(w.Add(0.2f) == BroodStage.Stirring, "0.50: stirring");
            Check(w.Add(0.05f) == BroodStage.Asleep, "0.55: stirring is said once");
            Check(w.Add(0.2f) == BroodStage.Rumbling, "0.75: rumbling");
            Check(w.Stage == BroodStage.Rumbling && w.Describe().Contains("rumble"), "inspect reads the rumble");
            Check(w.Add(0.3f) == BroodStage.Awake && w.awake, "1.05: awake");
            Check(w.Add(0.5f) == BroodStage.Asleep, "awake is announced exactly once");
            Check(w.Decay(50f) == BroodStage.Asleep && w.awake && w.Stage == BroodStage.Awake, "nothing decays once awake");
            Check(w.Describe().Contains("Run"), "awake inspect says run");
            Check(!w.Describe().Contains("1.0") && !w.Describe().Contains("%"), "inspect never shows the number");

            var j = new BroodWakeLogic { threshold = 1f };
            Check(j.Add(0.8f) == BroodStage.Rumbling, "a jump straight to rumble announces the rumble");
            Check(j.Add(0.05f) == BroodStage.Asleep, "and never the lesser stir after it");
        }

        private static void SignAlwaysBeforeWake()
        {
            // every roll, every step size the game uses: the first sign before awake is never Awake itself
            float[] steps = { 0.12f, 0.18f, 0.35f, 0.004f, 10f };
            for (int r = 0; r <= 10; r++)
            {
                float t = BroodWakeLogic.RollThreshold(r / 10f, 1f);
                foreach (float s in steps)
                {
                    var w = new BroodWakeLogic { threshold = t };
                    bool sawSign = false, wokeWithoutSign = false;
                    for (int i = 0; i < 400 && !w.awake; i++)
                    {
                        BroodStage e = w.Add(s);
                        if (e == BroodStage.Asleep) e = w.Recheck();
                        if (e == BroodStage.Rumbling || e == BroodStage.Stirring) sawSign = true;
                        if (e == BroodStage.Awake && !sawSign) wokeWithoutSign = true;
                    }
                    Check(w.awake && !wokeWithoutSign, "roll " + r + " step " + s + ": a sign before the wake");
                }
            }
            // the worst case named in the code: 0.55 on the lowest line, then the egg
            var x = new BroodWakeLogic { threshold = 0.85f };
            x.Add(0.55f);
            Check(x.Add(0.35f) == BroodStage.Rumbling && !x.awake, "egg past the line from below the rumble: rumble first");
            Check(x.Recheck() == BroodStage.Awake && x.awake, "then the next recheck wakes her");
        }

        private static void GreedDial()
        {
            float[] greed = { 0.12f, 0.12f, 0.12f, 0.12f, 0.12f, 0.18f, 0.12f };   // RM_RescueShipWreck.xml
            for (int r = 0; r <= 10; r++)
            {
                float t = BroodWakeLogic.RollThreshold(r / 10f, 1f);
                var modest = new BroodWakeLogic { threshold = t };
                modest.Add(0.18f); modest.Add(0.12f); modest.Add(0.12f); modest.Recheck();
                Check(!modest.awake, "roll " + r + ": three parts (the greediest) never wake her");

                var whole = new BroodWakeLogic { threshold = t };
                foreach (float g in greed) { whole.Add(g); whole.Recheck(); }
                whole.Add(BroodWakeLogic.EggWeight); whole.Recheck();
                Check(whole.awake, "roll " + r + ": the whole wreck and the egg wake her");
            }
        }

        private static void DecayFloor()
        {
            var w = new BroodWakeLogic { threshold = 1f };
            w.Add(0.6f);
            w.Decay(1f);
            Check(Near(w.pressure, 0.55f), "one quiet day takes 0.05");
            w.Decay(100f);
            Check(Near(w.pressure, 0.3f), "decay stops at half the peak");
            Check(w.Decay(0f) == BroodStage.Asleep && Near(w.pressure, 0.3f), "no time, no change");
        }

        private static void Rearm()
        {
            var w = new BroodWakeLogic { threshold = 1f };
            Check(w.Add(0.5f) == BroodStage.Stirring, "stir at 0.5");
            w.Add(-0.2f);   // 0.30 < 0.45*0.8
            Check(w.Add(0.2f) == BroodStage.Stirring, "falling well below re-arms the stir");
            var h = new BroodWakeLogic { threshold = 1f };
            h.Add(0.46f);
            h.Add(-0.02f);  // 0.44: just under, inside the hysteresis band
            Check(h.Add(0.02f) == BroodStage.Asleep, "no flicker at the stir line");
        }

        private static void EggRefund()
        {
            var w = new BroodWakeLogic { threshold = 1f };
            w.Add(BroodWakeLogic.EggWeight);
            w.Add(-BroodWakeLogic.EggWeight * BroodWakeLogic.EggReturnRefund);
            Check(Near(w.pressure, 0.07f), "returning the egg refunds 80%");
            w.Add(-5f);
            Check(w.pressure == 0f, "pressure never goes negative");
        }

        private static void Imprint()
        {
            Check(BroodImprintLogic.Decide(true, true, true) == ImprintResult.Bonded, "player's egg + bone aboard: bonded");
            Check(BroodImprintLogic.Decide(true, false, true) == ImprintResult.WildNoBone, "no bone aboard: wild");
            Check(BroodImprintLogic.Decide(false, true, true) == ImprintResult.WildNotPlayers, "unclaimed egg: wild");
            Check(BroodImprintLogic.WhyNot(ImprintResult.WildNoBone).Contains("great bone"), "inspect says why: the bone");
            Check(BroodImprintLogic.WhyNot(ImprintResult.Bonded).Contains("imprint on you"), "inspect says it will bond");
        }

        private static void ShipFit()
        {
            Check(ShipFitLogic.Decide(true, 3) == FitResult.Fits, "accepted part, worn ship: fits");
            Check(ShipFitLogic.Decide(false, 3) == FitResult.RefusedForeign, "refused part: refused even when worn");
            Check(ShipFitLogic.Decide(true, 0) == FitResult.NothingToRestore, "nothing worn: kept, not wasted");
            Check(ShipFitLogic.Reason(FitResult.RefusedForeign).Contains("will not take"), "refusal is plain words");
            Check(ShipFitLogic.Reason(FitResult.RefusedForeign).Contains("Sell") , "refusal says it is still loot");
        }

        private static void Spread()
        {
            int[] give = ShipFitLogic.Spread(new[] { 50, 300, 100 }, 350);
            Check(give[1] == 300 && give[2] == 50 && give[0] == 0, "worst-worn first: 300 then 50");
            int[] all = ShipFitLogic.Spread(new[] { 10, 20 }, 1000);
            Check(all[0] == 10 && all[1] == 20, "never over-repairs");
            int[] none = ShipFitLogic.Spread(new[] { 10 }, 0);
            Check(none[0] == 0, "no budget, no repair");
            Check(ShipFitLogic.Spread(new int[0], 100).Length == 0, "nothing worn, empty spread");
        }

        private static void Bane()
        {
            Check(SummBaneLogic.ShouldHunt(1f, 0.1f) && !SummBaneLogic.ShouldHunt(1f, 0.5f), "fed: hunts about a fifth of the time");
            Check(SummBaneLogic.ShouldHunt(0.2f, 0.5f) && !SummBaneLogic.ShouldHunt(0.2f, 0.9f), "hungry: hunts most of the time");
            Check(SummBaneLogic.PickVictimKind(0, 0, 0.5f) == -1, "nothing to kill");
            Check(SummBaneLogic.PickVictimKind(3, 2, 0.5f) == 0, "wild first");
            Check(SummBaneLogic.PickVictimKind(3, 2, 0.05f) == 1, "sometimes a tame one");
            Check(SummBaneLogic.PickVictimKind(0, 2, 0.9f) == 1, "only tame ones left: a tame one");
            Check(SummBaneLogic.PickVictimKind(3, 0, 0.01f) == 0, "no tame ones: wild");
            Check(Near(SummBaneLogic.HungerSeverity(9f), 3f) && Near(SummBaneLogic.HungerSeverity(0f), 0.5f), "hunger slider clamped");
        }

        // A planted break: a wake meter with the sign-before-wake guard removed must be caught by the same probe.
        private static void PlantedBreak()
        {
            var x = new BroodWakeLogic { threshold = 0.85f };
            x.Add(0.55f);
            x.rumbleAnnounced = true;   // simulate the guard missing: the line is crossed with no rumble ever said
            BroodStage e = x.Add(0.35f);
            Check(e == BroodStage.Awake, "planted break: without the guard the egg wakes her with no sign (the probe sees it)");
        }
    }
}
