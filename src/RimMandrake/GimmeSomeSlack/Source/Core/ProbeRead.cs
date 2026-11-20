// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE (in-game visit 2, 2026-11-19: M8 FAIL in 7 of 9 runs). The first census
// after a one-cell cut listed the live end only; the next poll, no tick later, listed the dead end too. The census read the
// published pieces while the frame's build still owed edges to the graph or lay worker (CordBuilder AsyncLay: a frame's Build
// shows the previous pieces until the workers land), so a scripted read saw a set from before the cut. A probe read of the laid
// set now first finishes the build the component owes, with the complete Rebuild (every edge laid on the caller).
namespace RimMandrake.GimmeSomeSlack.Core
{
    internal static class ProbeRead
    {
        /// <summary>The probe commands whose answer is read off the laid set (pieces, ends, decals, graph). Each one first settles
        /// a build the component owes (<see cref="OwesBuild"/>). Left out on purpose: motion (its slice window measures the frame
        /// builds, and a probe build would sit in it), strands: (it compares the pieces with what the sections last printed, and a
        /// probe build moves the pieces ahead of the print), poll, rebuild and sameframe: (each runs its own build or none by
        /// design), and every command that reads or writes no laid set (settings, selection, pawns, counters).</summary>
        public static bool ReadsLaidSet(string cmd)
        {
            if (cmd == null) return false;
            switch (cmd)
            {
                case "census": case "fresh": case "artfit": case "shapetable": case "kinks": case "shapeaudit": case "bends":
                case "doorstrays": case "slack": case "styles":
                    return true;
            }
            foreach (string p in Prefixed)
                if (cmd.StartsWith(p, System.StringComparison.Ordinal)) return true;
            return false;
        }

        private static readonly string[] Prefixed = { "rect:", "worlddump:", "strandsnear:", "ends:", "endkind:", "joins:", "under:" };

        /// <summary>True when the published pieces are not yet the build the component has committed to: a build left edges to
        /// the workers (<paramref name="lastPending"/> &gt; 0, a waiting graph job included: CordBuilder sets it to at least 1), or a
        /// dirty event marked the cords stale and the next frame's rebuild has not run (<paramref name="staleOffscreen"/>). A
        /// change no event announced is NOT owed: a probe read must still see that bug (D2_fresh_builder_same, live_flip_fresh.py).</summary>
        public static bool OwesBuild(bool enabled, int lastPending, bool staleOffscreen) =>
            enabled && (lastPending > 0 || staleOffscreen);
    }
}
