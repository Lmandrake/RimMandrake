// HUGE_WALLS_FIX_DECIDER_RETRIES_FOREVER: the walls-and-slots decider's unreachable-destination cooldown (UnreachableMemo) and the
// pruned held-crossing book (HeldBook), both Verse-free in Kernel/RM_WallsSlotsMemoKernel.cs. Oracles are written here from the
// requirement, never from the kernel:
//   memo      a noted (creature, destination) is blocked for exactly UnreachableMemo.CooldownTicks, never for another destination or
//             creature, never after the cooldown; a tick that goes backwards (a load) forgets everything; the table stays bounded
//             however many creatures note; a memo from the far future never applies.
//   heldprune expired, dead-creature and other-map entries are pruned and nothing live is; each creature keeps at most
//             MaxPerCreature entries and the book at most MaxCreatures creatures; Any is false exactly when the book is empty.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings.SelfTest
{
    internal static class WallsSlotsMemoFuzz
    {
        public static long Cases, Checks;
        public static readonly string[] Families = { "memo", "heldprune" };

        private static void Check(bool ok, string msg)
        {
            Checks++;
            if (!ok) throw new Exception(msg);
        }

        internal static string CaseMemo(int seed)
        {
            var r = new Random(seed);
            var m = new UnreachableMemo();
            int now = r.Next(1000, 5000000);
            int id = r.Next(1, 100000);
            long dest = r.Next(1, 1000000);
            Check(!m.Blocked(id, dest, now), "a fresh memo blocks");
            m.Note(id, dest, now);
            int cd = UnreachableMemo.CooldownTicks;
            Check(cd > 0, "cooldown must be positive");
            int dt = r.Next(0, cd * 2);
            Check(m.Blocked(id, dest, now + dt) == (dt < cd), "blocked at +" + dt + " (cooldown " + cd + ")");
            Check(!m.Blocked(id, dest + 1, now + 1) && !m.Blocked(id + 1, dest, now + 1), "another destination or creature is blocked");
            Check(m.Blocked(id, dest, now), "not blocked on the tick it was noted");
            // time going backwards (a load of an earlier save) forgets everything
            m.Sync(now + 5);
            m.Sync(now + 2);
            Check(m.Count == 0 && !m.Blocked(id, dest, now + 3), "a backwards tick did not clear the memo");
            // a memo stamped in the far future (stale from another game) never applies
            var m2 = new UnreachableMemo();
            m2.Note(id, dest, now + 10 * cd);
            Check(!m2.Blocked(id, dest, now), "a memo from the far future applied");
            // bounded: many creatures noting never grows the table past MaxEntries
            var m3 = new UnreachableMemo();
            int n = UnreachableMemo.MaxEntries * 3 + r.Next(100);
            for (int i = 0; i < n; i++) m3.Note(i, i, now + i / 4);
            Check(m3.Count <= UnreachableMemo.MaxEntries, "memo grew to " + m3.Count);
            Check(m3.Blocked(n - 1, n - 1, now + (n - 1) / 4), "the newest note was evicted");
            // expired entries are pruned
            m3.Prune(now + n + cd * 2);
            Check(m3.Count == 0, "prune left " + m3.Count + " expired entries");
            // re-noting after expiry blocks again (a memo that still holds the expired note, not one a backwards Sync emptied)
            var m4 = new UnreachableMemo();
            m4.Note(id, dest, now);
            Check(!m4.Blocked(id, dest, now + cd + 1), "an expired note still blocks");
            m4.Note(id, dest, now + cd * 3);
            Check(m4.Blocked(id, dest, now + cd * 3 + 1), "re-note after expiry did not block");
            return m3.Count.ToString();
        }

        internal static string CaseHeld(int seed)
        {
            var r = new Random(seed);
            var b = new HeldBook();
            int memo = 2500;
            int now = r.Next(10000, 1000000);
            var live = new HashSet<int>();
            var adds = new List<(int id, int map, int until)>();
            int creatures = r.Next(1, 40);
            for (int i = 0; i < creatures; i++)
            {
                int id = 1000 + i;
                int per = r.Next(1, 14);
                for (int k = 0; k < per; k++)
                {
                    int map = r.Next(0, 3);
                    int at = now - r.Next(0, 4000);
                    b.Add(id, map, at, memo, new[] { r.Next(0, 5000) });
                    adds.Add((id, map, at + memo));
                }
                if (r.Next(3) != 0) live.Add(id);
            }
            Check(b.Any == (b.Count > 0), "Any disagrees with Count");
            Check(b.CreatureCount <= HeldBook.MaxCreatures, "too many creatures held");
            for (int i = 0; i < creatures; i++) Check(b.EntryCount(1000 + i) <= HeldBook.MaxPerCreature, "creature " + i + " holds " + b.EntryCount(1000 + i));
            int liveMap = r.Next(0, 3);
            b.Prune(now, memo, id => live.Contains(id), map => map == liveMap);
            // the oracle from the requirement: of each creature's adds, the last MaxPerCreature are kept (no creature eviction:
            // creatures < MaxCreatures here), and of those exactly the unexpired, live-map entries of a live creature survive
            for (int i = 0; i < creatures; i++)
            {
                int id = 1000 + i;
                var mine = adds.FindAll(x => x.id == id);
                int want = 0;
                for (int k = Math.Max(0, mine.Count - HeldBook.MaxPerCreature); k < mine.Count; k++)
                    if (live.Contains(id) && mine[k].map == liveMap && mine[k].until > now && mine[k].until - now <= memo) want++;
                Check(b.EntryCount(id) == want, "creature " + id + " kept " + b.EntryCount(id) + " entries after the prune, the requirement says " + want);
            }
            // every survivor is unexpired, on the live map, of a live creature; every unexpired live-map live creature entry that
            // was kept under the per-creature cap survives
            var cells = new List<int>();
            for (int i = 0; i < creatures; i++)
            {
                int id = 1000 + i;
                for (int map = 0; map < 3; map++)
                {
                    b.CellsFor(id, map, now, memo, cells);
                    if (!live.Contains(id) || map != liveMap) Check(cells.Count == 0, "a dead creature's or other map's crossing survived the prune");
                }
                if (!live.Contains(id)) Check(b.EntryCount(id) == 0, "dead creature " + id + " still has entries");
            }
            for (int i = 0; i < creatures; i++)
            {
                int id = 1000 + i;
                Check(b.EntryCount(id) == 0 || (live.Contains(id) && b.EntryCountOnMap(id, liveMap) == b.EntryCount(id)), "off-map entry survived");
            }
            // a wall leaving the map: RemoveWhere returns exactly the creatures that lost a crossing (the decider forgets their
            // unreachable cooldown by that list, pass 3), and nothing it returns still holds a matching crossing
            int hitCell = r.Next(0, 5000);
            var had = new HashSet<int>();
            for (int i = 0; i < creatures; i++)
            {
                b.CellsFor(1000 + i, liveMap, now, memo, cells);
                if (cells.Contains(hitCell)) had.Add(1000 + i);
            }
            List<int> touched = b.RemoveWhere(liveMap, cs => Array.IndexOf(cs, hitCell) >= 0);
            Check(had.Count == 0 ? touched == null : touched != null && new HashSet<int>(touched).SetEquals(had),
                "RemoveWhere returned " + (touched == null ? "null" : touched.Count.ToString()) + " creatures, " + had.Count + " held the cell");
            foreach (int id in had)
            {
                b.CellsFor(id, liveMap, now, memo, cells);
                Check(!cells.Contains(hitCell), "creature " + id + " still holds the removed cell");
            }
            var um = new UnreachableMemo();
            um.Note(42, 9, now);
            um.Forget(42);
            Check(!um.Blocked(42, 9, now + 1), "Forget left the creature's goal blocked");
            // after everything expires, the book is empty and Any is false
            b.Prune(now + memo * 3, memo, id => true, map => true);
            Check(b.Count == 0 && !b.Any && b.CreatureCount == 0, "expired entries left behind: " + b.Count);
            // an entry stamped in the far future (stale save) is pruned too
            b.Add(7, 0, now + memo * 40, memo, new[] { 1 });
            b.Prune(now, memo, id => true, map => true);
            Check(b.Count == 0, "a far-future entry survived the prune");
            // a load clears the book outright
            b.Add(8, 0, now, memo, new[] { 2 });
            b.Clear();
            Check(b.Count == 0 && !b.Any, "Clear left entries");
            // the creature table is bounded
            for (int i = 0; i < HeldBook.MaxCreatures * 3; i++) b.Add(i, 0, now, memo, new[] { i });
            Check(b.CreatureCount <= HeldBook.MaxCreatures, "creature table grew to " + b.CreatureCount);
            return b.CreatureCount.ToString();
        }

        public static bool Run(double scale, int? one, string only)
        {
            int N(int baseN) => Math.Max(scale > 0 ? 1 : 0, (int)(baseN * scale));
            bool ok = true;
            if (only == null || only == "memo") ok &= Family("memo", N(2000), one, CaseMemo);
            if (only == null || only == "heldprune") ok &= Family("heldprune", N(2000), one, CaseHeld);
            Console.WriteLine("walls memo fuzz: " + Cases + " cases, " + Checks + " checks");
            return ok;
        }

        private static bool Family(string name, int n, int? one, Func<int, string> run)
        {
            int fails = 0, ran = 0;
            for (int i = 0; i < n; i++)
            {
                int seed = one ?? (i * 7919 + name.Length * 104729);
                Cases++;
                ran++;
                try { run(seed); }
                catch (Exception e) { if (fails++ < 5) Console.WriteLine("FAIL " + name + " seed " + seed + ": " + e.Message); }
                if (one.HasValue) break;
            }
            Console.WriteLine((fails == 0 && ran > 0 ? "PASS " : "FAIL ") + name + ": " + ran + " cases, " + fails + " failed");
            return fails == 0 && ran > 0;
        }
    }
}
