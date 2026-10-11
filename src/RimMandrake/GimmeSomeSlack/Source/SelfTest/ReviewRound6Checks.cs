// Owner code round 6 (2026-10-04): the offline, load-bearing checks. Each property carries a planted fault (the round-5
// behaviour, or a plausible wrong rule) that must turn it red. The round's hose checks (draw order over the hose, hose
// length, reel relays) moved to FlowWorks/Source/SelfTest with the hose port (2026-10-11); what stays here:
//   lamp     "I don't see the standing lamps changing their look when I change the cable"
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class ReviewRound6Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review6: " + msg);

        private static bool Near(double a, double b, double eps = 1e-4) => Math.Abs(a - b) < eps;

        // ---------------------------------------------------------------- lamps follow their run
        private static void Lamp()
        {
            const string D = "Scrapper";
            // (lamp look, run look before, expected follow)
            var cases = new (string, string, bool)[]
            {
                (null, "Industrial", true),        // vanilla-art lamp on a styled run: follows
                ("Industrial", "Industrial", true), // built in the run's look: follows
                ("Futuristic", "Industrial", false),// given its own look: kept
                (D, null, true),                    // unstyled run draws the default: a default-look lamp follows
                ("Modern", null, false),            // unstyled run, a Modern lamp: deliberate, kept
                (null, null, true)
            };
            int ok = cases.Count(c => ConduitStyles.LampFollowsRun(c.Item1, c.Item2, D) == c.Item3);
            Check(ok == cases.Length, "a restyle repaints the run's lamps unless one was styled on purpose (" + ok + "/" + cases.Length + ")");
            int never = cases.Count(c => !c.Item3), always = cases.Count(c => c.Item3);
            Check(never < cases.Length && always < cases.Length,
                "can-fail: round 5's 'lamps never follow' is right in " + never + "/" + cases.Length + ", 'always follow' in " + always + "/" + cases.Length);
            // a bridge repaints the LOSING run's lamps by the same rule, but never stamps an unstyled (older-save) lamp
            Check(ConduitStyles.LampFollowsRun("Modern", "Modern", D, restyle: false) && !ConduitStyles.LampFollowsRun(null, "Modern", D, restyle: false) &&
                  !ConduitStyles.LampFollowsRun("Futuristic", "Modern", D, restyle: false),
                "bridge: the loser's Modern lamp turns with it, a vanilla-art lamp stores nothing, a deliberately different lamp is kept");
            Check(ConduitStyles.IsLampDef("StandingLamp") && ConduitStyles.KeysFor("StandingLamp").Count == 4 &&
                  ConduitStyles.KeysFor("StandingLamp").All(AerialStyles.IsLook),
                "the floor lamp's Restyle offers exactly the four looks");
        }

        public static void Run()
        {
            Lamp();
        }
    }
}
