// Selftest for RosterPruning (PLOT_MECHANISM_MODS_WAVE_1's OldFriends roster
// cap/prune rule). Same offline-selftest discipline as
// RimMandrake.Property.SelfTest: compiles the REAL production RosterPruning.cs
// (plus its OldFriendEntry/Encounter/RoleTag dependencies) directly, using
// OldFriendEntry instances with a null Pawn - a valid state for this test
// since RosterPruning's own ordering (Notability, then LastSeenTick) never
// touches the Pawn field itself, exactly the same reasoning Property's own
// SelfTest uses for ClaimantRef.OfPawn(null).
//
// Run (written apart only because an XML comment cannot hold two adjacent hyphens):
//   "%USERPROFILE%\.dotnet\dotnet.exe" run [dash][dash]project D:\Luke\dev\Rimworld\src\RimMandrake\RaidRedesigner\Source\SelfTest\RimMandrakeRaidRedesigner.SelfTest.csproj -c Release

using System;
using System.Collections.Generic;
using RimMandrake.RaidRedesigner;

namespace RimMandrake.RaidRedesigner.SelfTest
{
    internal static class Program
    {
        private static int passed;
        private static int failed;

        private static void Case(string name, Action fn)
        {
            try
            {
                fn();
                passed++;
                Console.WriteLine("ok    " + name);
            }
            catch (Exception ex)
            {
                failed++;
                Console.WriteLine("FAIL  " + name + "\n        " + ex.Message);
            }
        }

        private static void Assert(bool cond, string msg)
        {
            if (!cond) throw new Exception(msg);
        }

        // Pawn=null is a deliberately valid state here - RosterPruning never
        // dereferences it, only Notability/LastSeenTick.
        private static OldFriendEntry Entry(int notability, int lastSeenTick)
        {
            var e = new OldFriendEntry(null, null, RoleTag.FledRaider, lastSeenTick);
            e.Notability = notability;
            return e;
        }

        private static int Main()
        {
            Case("No_overflow_prunes_nothing", () =>
            {
                var entries = new List<OldFriendEntry> { Entry(10, 100), Entry(20, 200) };
                var victims = RosterPruning.SelectPruneVictims(entries, 24);
                Assert(victims.Count == 0, "under-cap list must prune nothing");
            });

            Case("Overflow_prunes_exactly_the_overflow_count", () =>
            {
                var entries = new List<OldFriendEntry>();
                for (int i = 0; i < 26; i++) entries.Add(Entry(i, i));
                var victims = RosterPruning.SelectPruneVictims(entries, 24);
                Assert(victims.Count == 2, "26 living over a cap of 24 must prune exactly 2, got " + victims.Count);
            });

            Case("Prunes_the_LOWEST_notability_first", () =>
            {
                var low = Entry(1, 500);
                var mid = Entry(50, 500);
                var high = Entry(99, 500);
                var entries = new List<OldFriendEntry> { high, low, mid }; // order-independence check
                var victims = RosterPruning.SelectPruneVictims(entries, 2);
                Assert(victims.Count == 1 && victims[0] == low,
                    "the single lowest-notability entry must be the one pruned");
            });

            Case("Ties_break_on_STALER_lastSeenTick_first", () =>
            {
                var stale = Entry(10, 100);   // same notability, older tick
                var fresh = Entry(10, 900);   // same notability, newer tick
                var entries = new List<OldFriendEntry> { fresh, stale };
                var victims = RosterPruning.SelectPruneVictims(entries, 1);
                Assert(victims.Count == 1 && victims[0] == stale,
                    "equal notability must break the tie on the STALER (lower) LastSeenTick");
            });

            Case("Dead_entries_never_count_against_the_cap", () =>
            {
                var entries = new List<OldFriendEntry>();
                for (int i = 0; i < 30; i++)
                {
                    var e = Entry(i, i);
                    if (i < 10) e.MarkDead(9999, "test");
                    entries.Add(e);
                }
                // 30 total, 10 dead -> 20 living, under a cap of 24.
                var victims = RosterPruning.SelectPruneVictims(entries, 24);
                Assert(victims.Count == 0, "20 LIVING entries under a cap of 24 must prune nothing, "
                    + "even though the raw list has 30 entries total");
            });

            Console.WriteLine();
            Console.WriteLine((passed + failed) + " total, " + passed + " passed, " + failed + " failed.");
            return failed == 0 ? 0 : 1;
        }
    }
}
