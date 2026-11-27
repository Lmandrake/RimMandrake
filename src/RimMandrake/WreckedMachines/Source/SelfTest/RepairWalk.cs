// T_REPAIR_STATE_WALK (tree check C_repair_state_walk; models.md, Repair state walk): the shipped repair kernel
// (../Kernel/RM_WreckedMachinesRepair.cs) driven against a fake game around ONE machine.
//
// THE RANGE (declared; it is never "every case"):
//   states   level (Wrecked, Kludged, Refurbished) x where (standing, carried, destroyed) x line (on, off) x ground (the next level's,
//            other) x study of the wreck and of the Kludged machine (none, part, complete) x the two projects (finished or not) x the
//            repair record (none; ordered with 0..n delivered; working with part of the work) x the stock on the map
//   events   order, cancel, deliver (each material), work, uninstall, install, destroy, save and load, line off, line on, study,
//            research, floor laid, floor gone, component found
//   walk     breadth first from a fresh wreck on other ground with nothing studied: every reachable state, every event on it. Two
//            machines are walked: one whose Kludged level cannot be moved (the smelter's row) and one that moves at every level
//            (the carried machines' row). The walk uses unit amounts: 2 of one material for each repair, 1 scarce part for the
//            last repair, 2 units of work.
//   strings  seeded random event strings of length up to 40 on top, with random costs (1 to 3 materials, 1 to 120 each), random
//            delivery sizes (over-delivery included), random work amounts and totals.
//   cases    the event strings of the three live scenes (sc_repair_on_machine, sc_repair_cancelled, sc_uninstall_during_repair),
//            kept apart as named cases; each prints the proof line that the live scene must read at the same step.
//   left out colonist jobs, hauling and paths; the base game's study comp (the fake game's study is three steps and its research is
//            one event); placement; pictures; more than one machine at a time; a cost that changes while a repair is under way.
//
// THE ROWS. Each is read on every transition of the walk and of every string; a row with zero cases FAILS (it checked nothing).
//   cancel_never_loses_the_machine     after a cancel, or an uninstall that cancels: the machine is there at its old level with no
//                                      repair, and every delivered unit is back on the map
//   level_changes_only_on_complete_work a level moves only in a work event, one step up, from the Working phase with every material in
//                                      and the work at its total, the project finished, the ground right, the line on, the machine standing
//   signal_once_per_change             each transition raises exactly one signal when the level changed and none when it did not
//   materials_conserved                on the map + in the repair + used by complete repairs is constant (found components counted in)
//   record_sane                        delivered never above need; Working exactly when every material is in; a carried, destroyed or
//                                      Refurbished machine holds no repair; a machine that cannot be moved is never carried
//   save_load_identity                 Load(Save(record)) is the record, in every reachable state
//   blocks_named                       the kernel's reasons against an order equal an independent restatement, and an order is
//                                      accepted exactly when there is none
//   paused_repair_takes_nothing        while the machine's line is off or its ground is not the next level's, a delivery and work
//                                      change nothing: the repair waits, and a cancel still gives everything back
// PLANTED FAULTS: each fault corrupts what the fake game does with the kernel's answer (or what the kernel is told); the row it names
// must go red, or the run fails. The kernel's own faults are planted by maturation.py red-seen.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using RimMandrake.WreckedMachines;
using K = RimMandrake.WreckedMachines.RM_WreckedMachinesKernel;
using R = RimMandrake.WreckedMachines.RM_WreckedMachinesRepair;

namespace RimMandrake.WreckedMachines.SelfTest
{
    internal static class RepairWalk
    {
        private enum Ev { Order, Cancel, DeliverA, DeliverB, DeliverC, DeliverPart, Work, Uninstall, Install, Destroy, SaveLoad, LineOff, LineOn, Study, Research, FloorLaid, FloorGone, FindPart }
        private enum Fault { None, CancelDropsUnit, CancelDestroys, LevelOnDelivery, SignalTwice, SignalMissing, SaveDropsDelivered, OrderIgnoresResearch, WorkIgnoresGround, UninstallKeepsRepair, LevelSkips }
        private const string Part = "RM_WM_AncientComponent";
        private const int Standing = 0, Carried = 1, Destroyed = 2;

        private static readonly string[] Rows = { "cancel_never_loses_the_machine", "level_changes_only_on_complete_work", "signal_once_per_change",
            "materials_conserved", "record_sane", "save_load_identity", "blocks_named", "paused_repair_takes_nothing" };

        /// <summary>What a repair costs in this run of the fake game: for each step (index 1 to Kludged, 2 to Refurbished).</summary>
        private sealed class Costs
        {
            public string[][] defs = new string[3][];
            public int[][] counts = new int[3][];
            public float[] work = new float[3];
            public bool[] movable = { true, true, true };
        }

        private sealed class World
        {
            public Costs cost;
            public int level, where;
            public bool lineOn = true, groundOk;
            public int[] study = new int[3];
            public bool[] researched = new bool[3];
            public RM_RepairRecord rec = new RM_RepairRecord();
            public SortedDictionary<string, int> stock = new SortedDictionary<string, int>(StringComparer.Ordinal);
            public SortedDictionary<string, int> used = new SortedDictionary<string, int>(StringComparer.Ordinal);
            public int partsFound, partsCap = 1;
            // what the last event did (read by the rows, not part of the state)
            public int signals, sigFrom, sigTo;
            public bool accepted;

            public World Clone()
            {
                var w = (World)MemberwiseClone();
                w.study = (int[])study.Clone();
                w.researched = (bool[])researched.Clone();
                w.stock = new SortedDictionary<string, int>(stock, StringComparer.Ordinal);
                w.used = new SortedDictionary<string, int>(used, StringComparer.Ordinal);
                w.rec = CopyRec(rec);
                return w;
            }

            public string Key()
            {
                var sb = new StringBuilder();
                sb.Append(level).Append(where).Append(lineOn ? 1 : 0).Append(groundOk ? 1 : 0).Append(study[1]).Append(study[2])
                  .Append(researched[1] ? 1 : 0).Append(researched[2] ? 1 : 0).Append('/').Append(R.Save(rec)).Append('/');
                foreach (var kv in stock) sb.Append(kv.Key).Append('=').Append(kv.Value).Append(';');
                return sb.ToString();
            }

            public bool NeedsPart(int step) { return step <= 2 && step >= 1 && Array.IndexOf(cost.defs[step], Part) >= 0; }
            public bool SiteOk() { return lineOn && where == Standing && groundOk; }
            public int Stock(string d) { int n; return stock.TryGetValue(d, out n) ? n : 0; }
            public int Held(string d) { int i = Array.IndexOf(rec.defs, d); return i < 0 ? 0 : rec.delivered[i]; }
            public int Used(string d) { int n; return used.TryGetValue(d, out n) ? n : 0; }
        }

        private static RM_RepairRecord CopyRec(RM_RepairRecord r)
        {
            return new RM_RepairRecord { phase = r.phase, target = r.target, defs = (string[])r.defs.Clone(), need = (int[])r.need.Clone(),
                delivered = (int[])r.delivered.Clone(), workDone = r.workDone, workTotal = r.workTotal };
        }

        private static bool SameRec(RM_RepairRecord a, RM_RepairRecord b)
        {
            return a.phase == b.phase && a.target == b.target && a.workDone == b.workDone && a.workTotal == b.workTotal
                && a.defs.SequenceEqual(b.defs) && a.need.SequenceEqual(b.need) && a.delivered.SequenceEqual(b.delivered);
        }

        private static void Give(World w, List<KeyValuePair<string, int>> back, Fault f)
        {
            bool dropped = false;
            foreach (var kv in back)
            {
                int n = kv.Value;
                if (f == Fault.CancelDropsUnit && !dropped) { n--; dropped = true; }
                w.stock[kv.Key] = w.Stock(kv.Key) + n;
            }
        }

        /// <summary>One event on the fake game. `amount` is the delivery size or the work amount (the walk passes 1).</summary>
        private static void Apply(World w, Ev e, float amount, Fault f)
        {
            w.signals = 0; w.accepted = false;
            if (w.where == Destroyed) return;
            int next = w.level + 1;
            switch (e)
            {
                case Ev.Order:
                {
                    if (next > 2) { R.Order(w.level, R.NoHigherLevel, w.rec, new string[0], new int[0], 1f); return; }
                    bool proj = w.researched[next] || f == Fault.OrderIgnoresResearch;
                    int blocks = R.OrderBlocks(w.level, w.lineOn, w.where == Standing, w.rec, proj, w.groundOk, w.NeedsPart(next), w.Stock(Part) > 0);
                    w.accepted = R.Order(w.level, blocks, w.rec, w.cost.defs[next], w.cost.counts[next], w.cost.work[next]);
                    return;
                }
                case Ev.Cancel:
                    if (!R.Active(w.rec)) return;              // the cancel order is on the machine only while a repair is
                    Give(w, R.Cancel(w.rec), f);
                    if (f == Fault.CancelDestroys) w.where = Destroyed;
                    w.accepted = true;
                    return;
                case Ev.DeliverA: case Ev.DeliverB: case Ev.DeliverC: case Ev.DeliverPart:
                {
                    string d = e == Ev.DeliverPart ? Part : e == Ev.DeliverA ? "A" : e == Ev.DeliverB ? "B" : "C";
                    int carry = Math.Min((int)amount, w.Stock(d));
                    int took = R.Deliver(w.rec, d, carry, w.SiteOk());
                    if (took > 0) { w.stock[d] = w.Stock(d) - took; w.accepted = true; }
                    if (f == Fault.LevelOnDelivery && w.rec.phase == R.Working) Complete(w, new RM_LevelChange { changed = true, from = w.level, to = w.rec.target }, f);
                    return;
                }
                case Ev.Work:
                {
                    var held = CopyRec(w.rec);
                    bool site = f == Fault.WorkIgnoresGround ? (w.lineOn && w.where == Standing) : w.SiteOk();
                    RM_LevelChange ch = R.Work(w.level, w.rec, amount, site);
                    w.accepted = ch.changed || w.rec.workDone != held.workDone;
                    if (ch.changed)
                    {
                        for (int i = 0; i < held.defs.Length; i++) w.used[held.defs[i]] = w.Used(held.defs[i]) + held.delivered[i];
                        if (f == Fault.LevelSkips) ch.to = Math.Min(2, ch.to + 1);
                        Complete(w, ch, f);
                    }
                    return;
                }
                case Ev.Uninstall:
                {
                    if (w.where != Standing) return;
                    List<KeyValuePair<string, int>> back;
                    if (f == Fault.UninstallKeepsRepair) { if (w.cost.movable[w.level]) { w.where = Carried; w.accepted = true; } return; }
                    if (!R.Uninstall(w.rec, w.cost.movable[w.level], out back)) return;
                    Give(w, back, f);
                    w.where = Carried; w.accepted = true;
                    return;
                }
                case Ev.Install:
                    // a working level installs only on the ground it needs (the def's own ground need, the base game's rule)
                    if (w.where != Carried || (w.level >= K.Kludged && !w.groundOk)) return;
                    w.where = Standing; w.accepted = true;
                    return;
                case Ev.Destroy:
                    Give(w, R.Cancel(w.rec), Fault.None);      // what the repair held falls where the machine stood
                    w.where = Destroyed; w.accepted = true;
                    return;
                case Ev.SaveLoad:
                {
                    bool ok;
                    string text = R.Save(w.rec);
                    w.rec = R.Load(text, out ok);
                    if (f == Fault.SaveDropsDelivered) for (int i = 0; i < w.rec.delivered.Length; i++) w.rec.delivered[i] = 0;
                    w.accepted = ok;
                    return;
                }
                case Ev.LineOff: w.accepted = w.lineOn; w.lineOn = false; return;
                case Ev.LineOn: w.accepted = !w.lineOn; w.lineOn = true; return;
                case Ev.Study:
                    // the fake of the base game's study: three steps, on a standing machine, towards the project of its next level
                    if (w.where != Standing || next > 2 || w.study[next] >= 2) return;
                    w.study[next]++; w.accepted = true;
                    return;
                case Ev.Research:
                    for (int s = 1; s <= 2; s++)
                        if (!w.researched[s] && w.study[s] >= 2 && (s == 1 || w.researched[1])) { w.researched[s] = true; w.accepted = true; return; }
                    return;
                case Ev.FloorLaid: w.accepted = !w.groundOk; w.groundOk = true; return;
                case Ev.FloorGone:
                    // the floor under a standing working machine stays (the game refuses to take it); under a wreck or an empty site it goes
                    if (w.where == Standing && w.level >= K.Kludged) return;
                    w.accepted = w.groundOk; w.groundOk = false; return;
                case Ev.FindPart:
                    if (w.partsFound >= w.partsCap) return;
                    w.partsFound++; w.stock[Part] = w.Stock(Part) + 1; w.accepted = true;
                    return;
            }
        }

        private static void Complete(World w, RM_LevelChange ch, Fault f)
        {
            if (f == Fault.LevelOnDelivery)
            {
                for (int i = 0; i < w.rec.defs.Length; i++) w.used[w.rec.defs[i]] = w.Used(w.rec.defs[i]) + w.rec.delivered[i];
                bool ok; w.rec = R.Load("", out ok);
            }
            w.level = ch.to;
            w.signals = f == Fault.SignalMissing ? 0 : f == Fault.SignalTwice ? 2 : 1;
            w.sigFrom = ch.from; w.sigTo = ch.to;
        }

        private sealed class Tally
        {
            public Dictionary<string, long> cases = Rows.ToDictionary(r => r, r => 0L);
            public Dictionary<string, List<string>> bad = Rows.ToDictionary(r => r, r => new List<string>());
            public long cells, refused, changes, signals, cancels, cancelsWithGoods, uninstallCancels, destroysWithGoods, toRefurbished;
            public int[] cancelPhase = new int[3];        // cancels seen with no delivery, part delivery, in the Working phase
            public void Fail(string row, string msg) { if (bad[row].Count < 5) bad[row].Add(msg); else if (bad[row].Count == 5) bad[row].Add("..."); }
        }

        private static int Total(World w, string d) { return w.Stock(d) + w.Held(d) + w.Used(d); }

        /// <summary>The rows, read on one transition.</summary>
        private static void Read(World pre, Ev e, float amount, World post, Tally t, string at)
        {
            t.cells++;
            if (!post.accepted) t.refused++;
            bool hadRepair = R.Active(pre.rec);
            // cancel_never_loses_the_machine
            if ((e == Ev.Cancel && hadRepair) || (e == Ev.Uninstall && hadRepair && pre.where == Standing && pre.cost.movable[pre.level]))
            {
                t.cases[Rows[0]]++;
                t.cancels++;
                bool goods = pre.rec.delivered.Any(n => n > 0);
                if (goods) t.cancelsWithGoods++;
                if (e == Ev.Uninstall) t.uninstallCancels++;
                else t.cancelPhase[pre.rec.phase == R.Working ? 2 : goods ? 1 : 0]++;
                bool back = true;
                for (int i = 0; i < pre.rec.defs.Length; i++) back &= post.Stock(pre.rec.defs[i]) == pre.Stock(pre.rec.defs[i]) + pre.rec.delivered[i];
                if (post.where == Destroyed || post.level != pre.level || R.Active(post.rec) || !back
                    || post.where != (e == Ev.Uninstall ? Carried : pre.where))
                    t.Fail(Rows[0], at + ": after " + e + " the machine is " + Where(post) + " at " + R.LevelName(post.level) + ", repair " + R.PhaseName(post.rec) + ", materials back " + back);
            }
            // level_changes_only_on_complete_work
            t.cases[Rows[1]]++;
            if (post.level != pre.level)
            {
                t.changes++;
                if (post.level == K.Refurbished) t.toRefurbished++;
                int step = pre.level + 1;
                bool full = pre.rec.phase == R.Working && pre.rec.defs.Length == pre.cost.defs[Math.Min(step, 2)].Length;
                for (int i = 0; full && i < pre.rec.defs.Length; i++) full &= pre.rec.delivered[i] == pre.cost.counts[step][Array.IndexOf(pre.cost.defs[step], pre.rec.defs[i])];
                // the work is complete: what was done before plus this event's amount reaches the step's own total (never below 1)
                bool done = pre.rec.workDone + amount >= pre.rec.workTotal && pre.rec.workTotal >= Math.Max(1f, pre.cost.work[Math.Min(step, 2)]);
                if (e != Ev.Work || post.level != step || !full || !done || !pre.researched[step] || !pre.groundOk || !pre.lineOn || pre.where != Standing)
                    t.Fail(Rows[1], at + ": " + e + " moved the level " + R.LevelName(pre.level) + " -> " + R.LevelName(post.level) + " (working with every material " + full + ", work complete " + done
                        + ", project " + pre.researched[Math.Min(step, 2)] + ", ground " + pre.groundOk + ", line " + pre.lineOn + ", " + Where(pre) + ")");
            }
            // signal_once_per_change
            t.cases[Rows[2]]++;
            t.signals += post.signals;
            int want = post.level != pre.level ? 1 : 0;
            if (post.signals != want || (want == 1 && (post.sigFrom != pre.level || post.sigTo != post.level)))
                t.Fail(Rows[2], at + ": " + e + " raised " + post.signals + " signals (" + R.LevelName(post.sigFrom) + " -> " + R.LevelName(post.sigTo) + "), level " + R.LevelName(pre.level) + " -> " + R.LevelName(post.level));
            // materials_conserved
            t.cases[Rows[3]]++;
            foreach (string d in pre.stock.Keys.Union(post.stock.Keys).Union(pre.rec.defs).Union(post.used.Keys).Distinct())
            {
                int found = d == Part && e == Ev.FindPart && post.accepted ? 1 : 0;
                if (Total(post, d) != Total(pre, d) + found)
                    t.Fail(Rows[3], at + ": " + e + " changed the total of " + d + " from " + Total(pre, d) + " to " + Total(post, d));
            }
            if (e == Ev.Destroy && hadRepair && pre.rec.delivered.Any(n => n > 0)) t.destroysWithGoods++;
            // record_sane
            t.cases[Rows[4]]++;
            var r = post.rec;
            bool allIn = true;
            for (int i = 0; i < r.defs.Length; i++) { allIn &= r.delivered[i] == r.need[i]; if (r.delivered[i] < 0 || r.delivered[i] > r.need[i]) t.Fail(Rows[4], at + ": delivered " + r.delivered[i] + " of " + r.need[i] + " " + r.defs[i]); }
            if (R.Active(r) && ((r.phase == R.Working) != allIn || r.target != post.level + 1 || r.workDone >= r.workTotal))
                t.Fail(Rows[4], at + ": after " + e + " the record reads " + R.ProofLine(r) + " on a " + R.LevelName(post.level) + " machine");
            if (R.Active(r) && (post.where != Standing || post.level >= K.Refurbished))
                t.Fail(Rows[4], at + ": a " + Where(post) + " " + R.LevelName(post.level) + " machine holds a repair after " + e);
            if (e == Ev.Uninstall && pre.where == Standing && post.where == Carried && !pre.cost.movable[pre.level])
                t.Fail(Rows[4], at + ": a " + R.LevelName(pre.level) + " machine that cannot be moved was carried");
            // save_load_identity
            t.cases[Rows[5]]++;
            bool ok;
            var back2 = R.Load(R.Save(post.rec), out ok);
            if (!ok || !SameRec(back2, post.rec) || (e == Ev.SaveLoad && !SameRec(pre.rec, post.rec)))
                t.Fail(Rows[5], at + ": the record " + R.Save(pre.rec) + " came back as " + R.Save(e == Ev.SaveLoad ? post.rec : back2));
            // paused_repair_takes_nothing
            if (hadRepair && (!pre.lineOn || !pre.groundOk) && (e == Ev.Work || e == Ev.DeliverA || e == Ev.DeliverB || e == Ev.DeliverC || e == Ev.DeliverPart))
            {
                t.cases[Rows[7]]++;
                if (!SameRec(pre.rec, post.rec) || post.level != pre.level || post.accepted)
                    t.Fail(Rows[7], at + ": " + e + " on a paused repair (line " + pre.lineOn + ", ground " + pre.groundOk + ") changed " + R.ProofLine(pre.rec) + " to " + R.ProofLine(post.rec));
            }
            // blocks_named: an independent restatement of when an order is offered and available
            if (e == Ev.Order && pre.where != Destroyed)
            {
                t.cases[Rows[6]]++;
                int step = pre.level + 1;
                var why = new List<string>();
                if (step > 2) why.Add("no higher level");
                if (!pre.lineOn) why.Add("line off");
                if (pre.where != Standing) why.Add("carried");
                if (hadRepair) why.Add("under repair");
                if (step <= 2 && !pre.researched[step]) why.Add("research");
                if (!pre.groundOk) why.Add("ground");
                if (step <= 2 && pre.NeedsPart(step) && pre.Stock(Part) == 0) why.Add("component");
                int b = step > 2 ? R.NoHigherLevel : R.OrderBlocks(pre.level, pre.lineOn, pre.where == Standing, pre.rec, pre.researched[step], pre.groundOk, pre.NeedsPart(step), pre.Stock(Part) > 0);
                var got = new List<string>();
                if ((b & R.NoHigherLevel) != 0) got.Add("no higher level");
                if ((b & R.LineOff) != 0) got.Add("line off");
                if ((b & R.Carried) != 0) got.Add("carried");
                if ((b & R.UnderRepair) != 0) got.Add("under repair");
                if ((b & R.Research) != 0) got.Add("research");
                if ((b & R.Ground) != 0) got.Add("ground");
                if ((b & R.Component) != 0) got.Add("component");
                bool offered = step <= 2 && pre.lineOn && pre.where == Standing && !hadRepair;
                if (step <= 2 && !why.SequenceEqual(got)) t.Fail(Rows[6], at + ": the kernel names [" + string.Join(", ", got) + "], the state gives [" + string.Join(", ", why) + "]");
                if (post.accepted != (why.Count == 0) || R.OrderOffered(b) != offered)
                    t.Fail(Rows[6], at + ": order accepted " + post.accepted + " and offered " + R.OrderOffered(b) + " with [" + string.Join(", ", why) + "]");
                if (post.accepted && (post.rec.target != step || !post.rec.defs.SequenceEqual(pre.cost.defs[step].Where((d, i) => pre.cost.counts[step][i] > 0))))
                    t.Fail(Rows[6], at + ": the accepted order reads " + R.ProofLine(post.rec));
            }
        }

        private static string Where(World w) { return w.where == Standing ? "standing" : w.where == Carried ? "carried" : "destroyed"; }

        private static World Fresh(Costs c, bool smelterLike)
        {
            var w = new World { cost = c };
            c.movable = smelterLike ? new[] { true, false, true } : new[] { true, true, true };
            foreach (int step in new[] { 1, 2 })
                for (int i = 0; i < c.defs[step].Length; i++)
                    if (c.defs[step][i] != Part) w.stock[c.defs[step][i]] = w.Stock(c.defs[step][i]) + c.counts[step][i];
            return w;
        }

        private static Costs UnitCosts()
        {
            var c = new Costs();
            c.defs[1] = new[] { "A" }; c.counts[1] = new[] { 2 }; c.work[1] = 2f;
            c.defs[2] = new[] { "A", Part }; c.counts[2] = new[] { 2, 1 }; c.work[2] = 2f;
            return c;
        }

        private static readonly Ev[] WalkEvents = { Ev.Order, Ev.Cancel, Ev.DeliverA, Ev.DeliverPart, Ev.Work, Ev.Uninstall, Ev.Install, Ev.Destroy, Ev.SaveLoad,
            Ev.LineOff, Ev.LineOn, Ev.Study, Ev.Research, Ev.FloorLaid, Ev.FloorGone, Ev.FindPart };

        /// <summary>Breadth first over every reachable state; returns the count of states, and writes the table when asked.</summary>
        private static int Walk(bool smelterLike, Fault f, Tally t, StreamWriter table)
        {
            var start = Fresh(UnitCosts(), smelterLike);
            var seen = new Dictionary<string, int> { { start.Key(), 0 } };
            var queue = new Queue<World>();
            queue.Enqueue(start);
            while (queue.Count > 0)
            {
                World pre = queue.Dequeue();
                int id = seen[pre.Key()];
                foreach (Ev e in WalkEvents)
                {
                    World post = pre.Clone();
                    Apply(post, e, 1f, f);
                    string key = post.Key();
                    int to;
                    if (!seen.TryGetValue(key, out to))
                    {
                        to = seen.Count;
                        seen[key] = to;
                        if (seen.Count > 400000) throw new Exception("the walk passed 400000 states: the fake game is not finite (a hang guard, about 10 times the states of the shipped walk)");
                        queue.Enqueue(post);
                    }
                    Read(pre, e, 1f, post, t, (smelterLike ? "smelter" : "carried") + " state " + id + " [" + pre.Key() + "]");
                    if (table != null) table.WriteLine((smelterLike ? "smelter" : "carried") + "\t" + id + "\t" + pre.Key() + "\t" + e + "\t" + (post.accepted ? "done" : "refused") + "\t" + to + "\t" + key);
                }
            }
            return seen.Count;
        }

        private static List<string> Strings(int cases, int seed0, Fault f, Tally t)
        {
            var fails = new List<string>();
            var evs = (Ev[])Enum.GetValues(typeof(Ev));
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c;
                var r = new Random(seed);
                var cost = new Costs();
                string[] mats = { "A", "B", "C" };
                foreach (int step in new[] { 1, 2 })
                {
                    int n = r.Next(1, 4);
                    var defs = mats.Take(n).ToList();
                    var counts = defs.Select(_ => r.Next(1, 121)).ToList();
                    if (step == 2 || r.Next(8) == 0) { defs.Add(Part); counts.Add(1); }
                    cost.defs[step] = defs.ToArray(); cost.counts[step] = counts.ToArray();
                    cost.work[step] = 1f + (float)r.NextDouble() * 5000f;
                }
                World w = Fresh(cost, r.Next(2) == 0);
                w.partsCap = 3;
                bool driven = r.Next(2) == 0;      // half of the strings are driven towards a complete repair, with random events in between
                // most strings start past the study, so that they reach the repair inside 40 events
                if (r.Next(4) != 0) { w.study[1] = 2; w.researched[1] = true; w.groundOk = r.Next(3) != 0; }
                if (r.Next(3) == 0) { w.study[2] = 2; w.researched[2] = true; }
                if (r.Next(5) == 0 && w.researched[1] && w.groundOk) w.level = K.Kludged;
                int len = r.Next(1, 41);
                var trail = new StringBuilder();
                Tally mine = new Tally();
                for (int i = 0; i < len; i++)
                {
                    Ev e = r.Next(3) == 0 ? evs[r.Next(evs.Length)] : new[] { Ev.Order, Ev.DeliverA, Ev.DeliverB, Ev.DeliverC, Ev.DeliverPart, Ev.Work, Ev.Work, Ev.Cancel, Ev.FindPart, Ev.SaveLoad }[r.Next(10)];
                    if (driven && r.Next(10) < 7 && w.where == Standing)
                    {
                        int step = w.level + 1;
                        if (R.Active(w.rec) && w.rec.phase == R.Working) e = Ev.Work;
                        else if (R.Active(w.rec))
                        {
                            string d = w.rec.defs.First(x => R.Missing(w.rec, x) > 0);
                            e = d == Part ? Ev.DeliverPart : d == "A" ? Ev.DeliverA : d == "B" ? Ev.DeliverB : Ev.DeliverC;
                        }
                        else if (step <= 2)
                            e = !w.lineOn ? Ev.LineOn : !w.researched[step] ? (w.study[step] < 2 ? Ev.Study : Ev.Research) : !w.groundOk ? Ev.FloorLaid
                                : w.NeedsPart(step) && w.Stock(Part) == 0 ? Ev.FindPart : Ev.Order;
                    }
                    float amount = e != Ev.Work ? r.Next(1, 151) : R.Active(w.rec) ? (float)(r.NextDouble() * 0.8 + 0.05) * w.rec.workTotal : (float)r.NextDouble() * 4000f + 0.01f;
                    World pre = w.Clone();
                    Apply(w, e, amount, f);
                    trail.Append(e).Append(' ');
                    Read(pre, e, amount, w, mine, "string seed " + seed + " step " + i + " (" + trail.ToString().Trim() + ")");
                }
                foreach (string row in Rows) { t.cases[row] += mine.cases[row]; foreach (string b in mine.bad[row]) { t.Fail(row, b); } }
                t.cells += mine.cells; t.changes += mine.changes; t.signals += mine.signals; t.cancels += mine.cancels; t.cancelsWithGoods += mine.cancelsWithGoods;
                t.uninstallCancels += mine.uninstallCancels; t.destroysWithGoods += mine.destroysWithGoods; t.toRefurbished += mine.toRefurbished; t.refused += mine.refused;
                for (int i = 0; i < 3; i++) t.cancelPhase[i] += mine.cancelPhase[i];
                if (Rows.Any(row => mine.bad[row].Count > 0)) fails.Add("string seed " + seed);
            }
            return fails;
        }

        /// <summary>The event strings of the three live scenes: each step's proof line, as the live scene must read it.</summary>
        private static List<string> Scenes(Tally t, List<string> lines)
        {
            var bad = new List<string>();
            Action<string, bool, (Ev e, string level, string phase)[]> run = (name, smelter, steps) =>
            {
                World w = Fresh(UnitCosts(), smelter);
                w.study[1] = 2; w.researched[1] = true; w.groundOk = true;      // each scene's start: the first project finished, on the floor
                lines.Add("case " + name + ": start " + R.LevelName(w.level) + " | " + R.ProofLine(w.rec));
                int n = 0, sig = 0;
                foreach (var s in steps)
                {
                    World pre = w.Clone();
                    Apply(w, s.e, 1f, Fault.None);
                    sig += w.signals;
                    Read(pre, s.e, 1f, w, t, "case " + name + " step " + n);
                    lines.Add("case " + name + ": " + s.e + " -> LEVEL " + R.LevelName(w.level) + " (" + Where(w) + ") | " + R.ProofLine(w.rec) + (w.signals > 0 ? " | SIGNAL from " + R.LevelName(w.sigFrom) + " to " + R.LevelName(w.sigTo) : ""));
                    if (R.LevelName(w.level) != s.level || R.PhaseName(w.rec) != s.phase)
                        bad.Add("case " + name + " step " + n + " (" + s.e + "): reads " + R.LevelName(w.level) + "/" + R.PhaseName(w.rec) + ", the scene's row wants " + s.level + "/" + s.phase);
                    n++;
                }
                lines.Add("case " + name + ": " + sig + " signal(s), stock " + string.Join(", ", w.stock.Select(kv => kv.Key + " " + kv.Value)));
            };
            run("sc_repair_on_machine", true, new[] {
                (Ev.Order, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "working"), (Ev.Work, "Wrecked", "working"),
                (Ev.SaveLoad, "Wrecked", "working"), (Ev.Work, "Kludged", "none") });
            run("sc_repair_cancelled", true, new[] {
                (Ev.Order, "Wrecked", "ordered"), (Ev.Cancel, "Wrecked", "none"),
                (Ev.Order, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "ordered"), (Ev.Cancel, "Wrecked", "none"),
                (Ev.Order, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "working"), (Ev.Work, "Wrecked", "working"), (Ev.Cancel, "Wrecked", "none"),
                (Ev.Order, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "working"), (Ev.Work, "Wrecked", "working"), (Ev.Work, "Kludged", "none") });
            run("sc_uninstall_during_repair", false, new[] {
                (Ev.Order, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "ordered"), (Ev.Uninstall, "Wrecked", "none"), (Ev.Install, "Wrecked", "none"),
                (Ev.Order, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "ordered"), (Ev.DeliverA, "Wrecked", "working"), (Ev.Work, "Wrecked", "working"), (Ev.Work, "Kludged", "none"),
                (Ev.Uninstall, "Kludged", "none") });
            return bad;
        }

        private static readonly Dictionary<Fault, string> FaultRow = new Dictionary<Fault, string> {
            { Fault.CancelDropsUnit, Rows[0] }, { Fault.CancelDestroys, Rows[0] }, { Fault.UninstallKeepsRepair, Rows[4] }, { Fault.LevelOnDelivery, Rows[1] },
            { Fault.OrderIgnoresResearch, Rows[1] }, { Fault.WorkIgnoresGround, Rows[1] }, { Fault.LevelSkips, Rows[1] }, { Fault.SignalTwice, Rows[2] },
            { Fault.SignalMissing, Rows[2] }, { Fault.SaveDropsDelivered, Rows[5] } };

        public static bool Run(double scale, int? oneSeed, string tablePath)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var t = new Tally();
            int states = 0;
            StreamWriter table = null;
            if (tablePath != null) { table = new StreamWriter(tablePath, false, new UTF8Encoding(false)); table.WriteLine("machine\tstate\tkey\tevent\tresult\tnext\tnext key"); }
            try
            {
                states += Walk(true, Fault.None, t, table);
                states += Walk(false, Fault.None, t, table);
            }
            finally { if (table != null) table.Dispose(); }
            long walkCells = t.cells;
            int n = oneSeed.HasValue ? 1 : (int)Math.Round(4000 * scale);
            List<string> failedStrings = Strings(n, oneSeed ?? 7100000, Fault.None, t);
            var lines = new List<string>();
            List<string> sceneBad = Scenes(t, lines);
            foreach (string l in lines) Console.WriteLine(l);
            Console.WriteLine();

            bool fail = false;
            foreach (string row in Rows)
            {
                bool bad = t.bad[row].Count > 0 || t.cases[row] == 0;
                fail |= bad;
                Console.WriteLine((bad ? "FAIL " : "PASS ") + row.PadRight(36) + " worst " + t.bad[row].Count + (t.bad[row].Count > 5 ? "+" : "") + " broken, limit 0, " + t.cases[row] + " cases"
                    + (t.cases[row] == 0 ? " (it read nothing)" : ""));
                foreach (string b in t.bad[row]) Console.WriteLine("       " + b);
            }
            // the walk must have been able to see: each kind of case that a row speaks about happened at least once
            var seenRows = new (string what, long n)[] { ("level changes", t.changes), ("repairs to Refurbished", t.toRefurbished), ("cancels before a delivery", t.cancelPhase[0]),
                ("cancels after part of the delivery", t.cancelPhase[1]), ("cancels during the work", t.cancelPhase[2]), ("uninstalls that cancel", t.uninstallCancels),
                ("machines destroyed with materials in them", t.destroysWithGoods), ("refused events", t.refused) };
            foreach (var s in seenRows)
            {
                if (s.n == 0) { fail = true; Console.WriteLine("FAIL the run never saw: " + s.what); }
            }
            foreach (string b in sceneBad) { fail = true; Console.WriteLine("FAIL " + b); }
            if (failedStrings.Count > 0) Console.WriteLine("failing strings (replay with --walk-seed N): " + string.Join(", ", failedStrings.Take(10)));

            // planted faults: each must turn its row red
            int caught = 0;
            if (!oneSeed.HasValue)
            {
                foreach (var kv in FaultRow)
                {
                    var ft = new Tally();
                    try { Walk(true, kv.Key, ft, null); Walk(false, kv.Key, ft, null); }
                    catch (Exception ex) { ft.Fail(kv.Value, "the walk threw under the fault: " + ex.Message); }
                    Strings(300, 7100000, kv.Key, ft);
                    if (ft.bad[kv.Value].Count > 0) caught++;
                    else { fail = true; Console.WriteLine("FAIL planted fault " + kv.Key + " did not turn " + kv.Value + " red"); }
                }
                Console.WriteLine("planted faults: " + caught + " of " + FaultRow.Count + " caught");
            }
            Console.WriteLine("walk: " + states + " states, " + walkCells + " cells (state x event) over 2 machines; strings: " + n + " of length up to 40; "
                + t.cells + " transitions read in all; " + t.changes + " level changes, " + t.signals + " signals, " + t.cancels + " cancels ("
                + t.cancelsWithGoods + " with materials in), " + t.refused + " refused events; " + sw.Elapsed.TotalSeconds.ToString("0.00", CultureInfo.InvariantCulture) + "s"
                + (tablePath != null ? "; table " + tablePath : ""));
            Console.WriteLine("T_REPAIR_STATE_WALK: " + (fail ? "FAIL" : "PASS"));
            return !fail;
        }
    }
}
