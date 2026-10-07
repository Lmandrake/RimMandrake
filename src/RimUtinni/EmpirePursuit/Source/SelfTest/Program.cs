// EMPIRE_ESCALATION_LADDER_1 selftest: the ladder's pure arithmetic, called on the REAL
// EmpireLadderMath.cs. Covers: band -> interval multiplier (design §2), rung interval factor,
// climb/hold with floor and top clamp (§3), tile-memory decay (§4), the starting rung after a
// move (owner ruling 2026-10-03: full reset to rung 1, leak floor permanent), the probe's
// sighting predicate, and the REPELLED mirror of Aftermath's 60% rule.
// NOT covered (needs a running game): the contacts themselves, lords, letters, scheduling.
using System;
using RuthlessPursuingMechanoids;

internal static class Program
{
    private static int pass, fail;

    private static void Check(string name, bool ok)
    {
        if (ok) { pass++; Console.WriteLine("ok   " + name); }
        else { fail++; Console.WriteLine("FAIL " + name); }
    }

    private static bool Near(float a, float b) => Math.Abs(a - b) < 1e-4f;

    private static int Main()
    {
        // band multipliers, including the edges (BandFor uses < 20/40/60/80)
        Check("absent visibility -> 1", Near(EmpireLadderMath.BandIntervalMultiplier(-1f), 1f));
        Check("hidden 0 -> 2.0", Near(EmpireLadderMath.BandIntervalMultiplier(0f), 2f));
        Check("19.9 hidden -> 2.0", Near(EmpireLadderMath.BandIntervalMultiplier(19.9f), 2f));
        Check("20 discreet -> 1.4", Near(EmpireLadderMath.BandIntervalMultiplier(20f), 1.4f));
        Check("50 noticed -> 1.0", Near(EmpireLadderMath.BandIntervalMultiplier(50f), 1f));
        Check("60 marked -> 0.7", Near(EmpireLadderMath.BandIntervalMultiplier(60f), 0.7f));
        Check("100 exposed -> 0.5", Near(EmpireLadderMath.BandIntervalMultiplier(100f), 0.5f));

        // rung interval factor
        Check("probe base 1", Near(EmpireLadderMath.RungIntervalFactor(1, false), 1f));
        Check("blind probe 1.5", Near(EmpireLadderMath.RungIntervalFactor(1, true), 1.5f));
        Check("spotter ignores blind", Near(EmpireLadderMath.RungIntervalFactor(2, true), 1f));
        Check("strike half", Near(EmpireLadderMath.RungIntervalFactor(3, false), 0.5f));
        Check("bombardment half", Near(EmpireLadderMath.RungIntervalFactor(6, false), 0.5f));

        // climb / hold
        Check("probe success climbs to 2", EmpireLadderMath.NextRungAfter(1, true, 0) == 2);
        Check("probe fail holds at 1", EmpireLadderMath.NextRungAfter(1, false, 0) == 1);
        Check("strike repelled holds at 3", EmpireLadderMath.NextRungAfter(3, false, 0) == 3);
        Check("top never exceeded", EmpireLadderMath.NextRungAfter(6, true, 0) == 6);
        Check("floor lifts a hold", EmpireLadderMath.NextRungAfter(1, false, 3) == 3);

        // decay
        Check("no time away keeps rung", EmpireLadderMath.DecayedRung(4, 0.9f, 1) == 4);
        Check("one season drops one", EmpireLadderMath.DecayedRung(4, 1.0f, 1) == 3);
        Check("2.5 seasons x2 drops four", EmpireLadderMath.DecayedRung(5, 2.5f, 2) == 1);
        Check("decay floors at 0", EmpireLadderMath.DecayedRung(2, 10f, 3) == 0);
        Check("decay 0 per season remembers forever", EmpireLadderMath.DecayedRung(5, 99f, 0) == 5);
        Check("negative seasons = none", EmpireLadderMath.DecayedRung(3, -2f, 1) == 3);

        // starting rung after a move
        Check("fresh tile starts at probe", EmpireLadderMath.StartingRung(0, true, -1) == 1);
        Check("probes off starts at strike", EmpireLadderMath.StartingRung(0, false, -1) == 3);
        Check("leak floor 2 skips probe", EmpireLadderMath.StartingRung(2, true, -1) == 2);
        Check("maximal leak floor 3", EmpireLadderMath.StartingRung(3, true, -1) == 3);
        Check("remembered tile starts higher", EmpireLadderMath.StartingRung(0, true, 4) == 4);
        Check("remembered 0 still probes", EmpireLadderMath.StartingRung(0, true, 0) == 1);
        Check("clamp never below 1", EmpireLadderMath.Clamp(0, 0) == 1);
        Check("clamp never above 6", EmpireLadderMath.Clamp(9, 0) == 6);

        // sighting predicate
        Check("clear sight in range", EmpireLadderMath.Sees(10f, true, 1f));
        Check("no LOS = unseen", !EmpireLadderMath.Sees(10f, false, 1f));
        Check("beyond range = unseen", !EmpireLadderMath.Sees(27f, true, 1f));
        Check("dark at distance = unseen", !EmpireLadderMath.Sees(10f, true, 0.1f));
        Check("dark but close = seen", EmpireLadderMath.Sees(5f, true, 0.1f));
        Check("spotter range 45", EmpireLadderMath.Sees(40f, true, 1f, 45f, 10f));

        // repelled mirror
        Check("6 of 10 down = repelled", EmpireLadderMath.Repelled(10, 6));
        Check("5 of 10 down = not repelled", !EmpireLadderMath.Repelled(10, 5));
        Check("2 of 3 down = repelled", EmpireLadderMath.Repelled(3, 2));
        Check("1 of 3 down = not repelled", !EmpireLadderMath.Repelled(3, 1));
        Check("no raiders = repelled", EmpireLadderMath.Repelled(0, 0));

        Console.WriteLine($"{pass}/{pass + fail} passed");
        return fail == 0 ? 0 : 1;
    }
}
