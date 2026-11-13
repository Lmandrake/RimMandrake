using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands.Fuzz
{
    // Family `rewards`: the fire-hawk's two hunt rewards (RM_FireHawkRewardsKernel). The first-sighting letter's gate is driven
    // through the same TryClaimSighting the GameComponent calls, over random streams of hawk observations: at most one letter a
    // game, exactly one when an eligible sighting happens, none with the toggle or the Pyrelands master off, none for a fogged,
    // ember-less or off-home hawk. The crestfeather's flat chance is rolled the way the butcher postfix rolls it.
    internal static class FireHawkRewardsFuzz
    {
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        public static List<string> Run(int n, int seed)
        {
            var fails = new List<string>();
            try
            {
                // 1. The gate's truth table: a letter only for an ember-carrying hawk, seen (not fogged), on a player home, with the
                //    toggle and the master on, and only while none has been sent.
                for (int m = 0; m < 64; m++)
                {
                    bool letterOn = (m & 1) != 0, master = (m & 2) != 0, sent = (m & 4) != 0, carrying = (m & 8) != 0,
                         home = (m & 16) != 0, fogged = (m & 32) != 0;
                    bool before = sent;
                    bool got = RM_FireHawkRewardsKernel.TryClaimSighting(ref sent, letterOn, master, carrying, home, fogged);
                    bool want = letterOn && master && !before && carrying && home && !fogged;
                    PyrelandsFuzz.Cases++;
                    Check(got == want, $"gate letter={letterOn} master={master} sent={before} carrying={carrying} home={home} fogged={fogged}: sent a letter={got}, ruled {want}");
                    Check(sent == (before || want), $"gate case {m}: the saved flag reads {sent} after the call");
                }

                // 2. A game is a stream of observations (one per hawk per look). Toggle off = no letter ever; on = one letter at the
                //    first eligible observation and never again, however many hawks follow.
                var r = new Random(seed);
                for (int g = 0; g < n; g++)
                {
                    bool letterOn = r.Next(4) != 0, master = r.Next(6) != 0;
                    bool sent = false;
                    int letters = 0, firstEligible = -1, firstLetter = -1;
                    int obs = r.Next(0, 200);
                    for (int i = 0; i < obs; i++)
                    {
                        bool carrying = r.Next(3) == 0, home = r.Next(5) != 0, fogged = r.Next(4) == 0;
                        bool eligible = carrying && home && !fogged;
                        if (eligible && firstEligible < 0) firstEligible = i;
                        if (RM_FireHawkRewardsKernel.TryClaimSighting(ref sent, letterOn, master, carrying, home, fogged))
                        {
                            letters++;
                            if (firstLetter < 0) firstLetter = i;
                        }
                        PyrelandsFuzz.Steps++;
                    }
                    PyrelandsFuzz.Cases++;
                    int want = letterOn && master && firstEligible >= 0 ? 1 : 0;
                    Check(letters == want, $"game seed {seed} #{g}: {letters} letters from {obs} sightings (toggle {letterOn}, master {master}, first eligible {firstEligible}); ruled {want}");
                    Check(want == 0 || firstLetter == firstEligible, $"game #{g}: the letter came at sighting {firstLetter}, the first eligible was {firstEligible}");
                }

                // 3. The look cadence: one look every SightingLookIntervalTicks, never per tick, and a whole day sees ~240 looks.
                int looks = 0;
                for (int t = 0; t < 60000; t++) if (RM_FireHawkRewardsKernel.LookThisTick(t)) looks++;
                PyrelandsFuzz.Cases++;
                Check(RM_FireHawkRewardsKernel.SightingLookIntervalTicks >= 60 && RM_FireHawkRewardsKernel.SightingLookIntervalTicks <= 600,
                    $"look interval {RM_FireHawkRewardsKernel.SightingLookIntervalTicks} ticks is not between a second and ten");
                Check(looks == 60000 / RM_FireHawkRewardsKernel.SightingLookIntervalTicks, $"{looks} looks in a day");

                // 4. The compass word for the letter: +z is north (RimWorld's map), eight sectors, none for the hawk's own cell.
                var compass = new (int dx, int dz, int want)[]
                {
                    (0, 9, 0), (7, 7, 1), (9, 0, 2), (7, -7, 3), (0, -9, 4), (-7, -7, 5), (-9, 0, 6), (-7, 7, 7), (0, 0, -1),
                    (2, 20, 0), (-2, 20, 0), (20, 2, 2), (20, -2, 2), (-20, 1, 6), (1, -20, 4),
                };
                foreach (var c in compass)
                {
                    PyrelandsFuzz.Cases++;
                    int got = RM_FireHawkRewardsKernel.Compass8(c.dx, c.dz);
                    Check(got == c.want, $"Compass8({c.dx},{c.dz}) = {got}, want {c.want}");
                }
                for (int k = 0; k < n; k++)
                {
                    int dx = r.Next(-300, 301), dz = r.Next(-300, 301);
                    int got = RM_FireHawkRewardsKernel.Compass8(dx, dz);
                    PyrelandsFuzz.Cases++;
                    if (dx == 0 && dz == 0) { Check(got == -1, "Compass8(0,0) is not -1"); continue; }
                    double deg = (Math.Atan2(dx, dz) * 180.0 / Math.PI + 360.0) % 360.0;   // 0 = north, clockwise
                    int sector = (int)Math.Floor((deg + 22.5) / 45.0) % 8;
                    double edge = Math.Abs(((deg + 22.5) % 45.0));
                    Check(got == sector || edge < 1e-6 || Math.Abs(edge - 45.0) < 1e-6, $"Compass8({dx},{dz}) = {got}, bearing {deg:F1} is sector {sector}");
                }

                // 5. The crestfeather: a flat chance, rolled once per butchered hawk. 0 never drops, 1 always, 0.35 drops ~35 %.
                PyrelandsFuzz.Cases++;
                Check(!RM_FireHawkRewardsKernel.TrophyDrops(0f, 0f) && !RM_FireHawkRewardsKernel.TrophyDrops(0.999f, 0f), "chance 0 dropped one");
                Check(RM_FireHawkRewardsKernel.TrophyDrops(0f, 1f) && RM_FireHawkRewardsKernel.TrophyDrops(0.999f, 1f), "chance 1 did not drop one");
                Check(RM_FireHawkRewardsKernel.TrophyDrops(0.3499f, 0.35f) && !RM_FireHawkRewardsKernel.TrophyDrops(0.35f, 0.35f), "the 0.35 edge is wrong");
                int trials = Math.Max(20000, n * 20), hits = 0;
                for (int k = 0; k < trials; k++) if (RM_FireHawkRewardsKernel.TrophyDrops((float)r.NextDouble(), 0.35f)) hits++;
                double rate = (double)hits / trials, sigma = Math.Sqrt(0.35 * 0.65 / trials);
                PyrelandsFuzz.Cases++;
                Check(Math.Abs(rate - 0.35) < 4 * sigma, $"0.35 dropped {rate:P2} of {trials} butchered hawks");
                Console.WriteLine($"rewards: crestfeather rate {rate:P2} over {trials} hawks (ruled 35 %), look every {RM_FireHawkRewardsKernel.SightingLookIntervalTicks} ticks");
            }
            catch (Exception e) { fails.Add("rewards: " + e.Message); }
            return fails;
        }
    }
}
