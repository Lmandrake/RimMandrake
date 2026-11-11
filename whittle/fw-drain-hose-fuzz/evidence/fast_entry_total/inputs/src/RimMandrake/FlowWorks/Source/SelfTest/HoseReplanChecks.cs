// HOSE_RECHECK_TAME_REPLAN_OFF_TICK: the corridor recheck's replan (HoseMath.CheckReplan) runs on HoseReplanQueue, off the
// hose tick, under one per-tick start quota shared by every map. Cases (all HoseReplan_*):
//  R1 pending is never an answer: a replan still running reads Pending (no reason, no keep), however long it runs; it
//     answers "no route" only once it has landed
//  R2 the per-tick quota is shared: two queues (two maps) asking 10 reels each on one tick start MaxStartsPerTick in all
//  R3 a result that lands after the reel's lay epoch moved is dropped and the current replan started
//  R4 a retract searched on an older world serial is run again; a keep is applied stale; MaxStaleRetracts stale retracts
//     in a row are taken
//  R5 a search that throws answers keep (never a retract) and keeps its text
//  R6 source: TickRecheckBody runs no CheckReplan itself, a cut asks the queue (PollReplan), a pending reel is polled every
//     tick and dropped when no longer laid or forgotten, restarted when a lay lands mid-replan, and RM_HoseLinks.Live
//     carries nothing over a pending hose
//  R7 the real CheckReplan through the queue: a walled-in target is "no route" once landed, and Pending while deferred
//     (the in-flight cap full), never "no route" before it has run
using System;
using System.Threading;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseReplanChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static HoseReplanQueue.Work Stand(Func<string> body, int serial = 0) => new HoseReplanQueue.Work { Run = body, Serial = serial };

        private static string Body(string src, string signature)
        {
            int a = src.IndexOf(signature, StringComparison.Ordinal);
            Assert(a >= 0, "missing: " + signature);
            int open = src.IndexOf('{', a);
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(a, i - a + 1);
            }
            throw new Exception("unbalanced: " + signature);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HoseReplan_R1 pending is never an answer: a running replan reads Pending, 'no route' only once landed", () =>
            {
                HoseReplanQueue.ResetQuota();
                var q = new HoseReplanQueue();
                var gate = new ManualResetEventSlim(false);
                Func<HoseReplanQueue.Work> prep = () => Stand(() => { gate.Wait(10000); return "no route"; });
                int t = 1000;
                for (int i = 0; i < 50; i++, t++)
                {
                    HoseReplanQueue.Answer a = q.Ask(7, 0, 0, t, prep);
                    Assert(a.Pending && a.Why == null, $"tick {t}: a replan still running answered (why '{a.Why}')");
                }
                Assert(q.Started == 1, $"one job for one reel, started {q.Started}");
                gate.Set();
                Assert(q.Drain(5000), "the job never finished");
                HoseReplanQueue.Answer done = q.Ask(7, 0, 0, t, prep);
                Assert(!done.Pending && done.Why == "no route", $"the landed replan reads pending={done.Pending} why '{done.Why}'");
                Assert(q.Jobs == 0 && q.Answered == 1, "the answered job is gone");
            });

            Case("HoseReplan_R2 the per-tick start quota is shared by every queue (two maps, 20 reels, one tick)", () =>
            {
                HoseReplanQueue.ResetQuota();
                var a = new HoseReplanQueue { Async = false };
                var b = new HoseReplanQueue { Async = false };
                int runs = 0;
                Func<HoseReplanQueue.Work> prep = () => Stand(() => { runs++; return null; });
                var done = new bool[2, 10];
                int answered = 0, ticks = 0;
                for (int t = 500; answered < 20 && t < 550; t++)
                {
                    int before = runs;
                    for (int i = 0; i < 10; i++)
                        for (int m = 0; m < 2; m++)
                        {
                            if (done[m, i]) continue;
                            if (!(m == 0 ? a : b).Ask(i, 0, 0, t, prep).Pending) { done[m, i] = true; answered++; }
                        }
                    Assert(runs - before <= HoseReplanQueue.MaxStartsPerTick, $"tick {t} ran {runs - before} replans across two maps (quota {HoseReplanQueue.MaxStartsPerTick})");
                    if (t == 500) Assert(runs == HoseReplanQueue.MaxStartsPerTick && a.Deferred + b.Deferred == 20 - runs, $"the first tick ran {runs}, deferred {a.Deferred + b.Deferred}");
                    ticks++;
                }
                Assert(runs == 20 && answered == 20 && ticks == (20 + HoseReplanQueue.MaxStartsPerTick - 1) / HoseReplanQueue.MaxStartsPerTick,
                    $"20 replans took {ticks} ticks, ran {runs}, answered {answered}");
            });

            Case("HoseReplan_R3 a result that lands after the reel's lay epoch moved is dropped; the current replan starts", () =>
            {
                HoseReplanQueue.ResetQuota();
                var q = new HoseReplanQueue();
                var gate = new ManualResetEventSlim(false);
                int released = 0;
                q.Released = (w, reusable) => { if (reusable) released++; };
                Assert(q.Ask(3, 5, 0, 10, () => Stand(() => { gate.Wait(10000); return "no route"; })).Pending, "started");
                gate.Set();
                Assert(q.Drain(5000), "drain");
                HoseReplanQueue.Answer a = q.Ask(3, 6, 0, 11, () => Stand(() => null));
                Assert(a.Pending && q.Dropped == 1 && released == 1 && q.Started == 2, $"the old epoch's 'no route' was applied or not released (dropped {q.Dropped}, released {released}, started {q.Started})");
                Assert(q.Drain(5000), "drain 2");
                HoseReplanQueue.Answer b = q.Ask(3, 6, 0, 12, () => Stand(() => null));
                Assert(!b.Pending && b.Why == null, "the current epoch's keep lands");
            });

            Case("HoseReplan_R4 a stale retract runs again, a stale keep applies, MaxStaleRetracts stale retracts are taken", () =>
            {
                HoseReplanQueue.ResetQuota();
                var q = new HoseReplanQueue();
                int serial = 1, tick = 100;
                Func<HoseReplanQueue.Work> retract = () => { int s = serial; return Stand(() => "no route", s); };
                HoseReplanQueue.Answer Step(Func<HoseReplanQueue.Work> p)
                {
                    HoseReplanQueue.Answer x = q.Ask(9, 0, serial, tick++, p);
                    Assert(q.Drain(5000), "drain");
                    return x;
                }
                Step(retract);                     // started on serial 1
                serial = 2;                        // the world moved while it ran
                HoseReplanQueue.Answer a = Step(retract);
                Assert(a.Pending && q.Rerun == 1, $"a retract searched on an older world was applied (rerun {q.Rerun})");
                serial = 3;
                a = Step(retract);
                Assert(a.Pending && q.Rerun == 2, "second stale retract reruns");
                serial = 4;
                a = q.Ask(9, 0, serial, tick++, retract);
                Assert(!a.Pending && a.Why == "no route" && q.StaleTaken == 1, $"after {HoseReplanQueue.MaxStaleRetracts} stale reruns the retract is taken (pending {a.Pending}, taken {q.StaleTaken})");
                // a keep is applied even when stale
                var k = new HoseReplanQueue();
                k.Ask(4, 0, 1, tick++, () => Stand(() => null, 1));
                Assert(k.Drain(5000), "drain k");
                HoseReplanQueue.Answer kept = k.Ask(4, 0, 2, tick++, () => Stand(() => "no route", 2));
                Assert(!kept.Pending && kept.Why == null && k.Started == 1, "a stale keep is applied, not rerun");
            });

            Case("HoseReplan_R5 a replan that throws answers keep, never a retract, and keeps its text", () =>
            {
                HoseReplanQueue.ResetQuota();
                var q = new HoseReplanQueue { Async = false };
                HoseReplanQueue.Answer a = q.Ask(2, 0, 0, 7, () => Stand(() => throw new InvalidOperationException("boom")));
                Assert(!a.Pending && a.Why == null, $"a fault answered pending={a.Pending} why '{a.Why}'");
                Assert(q.Faulted == 1 && q.LastFault != null && q.LastFault.Contains("boom"), "the fault text is kept");
            });

            Case("HoseReplan_R6 (source) the tick runs no CheckReplan: a cut asks the queue, pending is polled, blocks flow, is dropped", () =>
            {
                string comp = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                string tick = Body(comp, "private void TickRecheckBody(");
                Assert(!tick.Contains("HoseMath.CheckReplan("), "TickRecheckBody still runs HoseMath.CheckReplan on the tick");
                Assert(tick.Contains("if (r.replanPending) { PollReplan(r, now); return; }") && tick.Contains("r.replanPending = true;") && tick.Contains("PollReplan(r, now);"),
                    "a cut corridor does not ask the replan queue");
                string poll = Body(comp, "private void PollReplan(");
                Assert(poll.Contains("replanQueue.Ask(r.parent.thingIDNumber, r.layEpoch, worldSerial, now,") && poll.Contains("if (a.Pending) return;")
                    && poll.Contains("r.Retract(a.Why)") && poll.Contains("r.layKey = null;"), "PollReplan is not ask -> pending | retract | re-lay");
                Assert(poll.IndexOf("if (a.Pending) return;", StringComparison.Ordinal) < poll.IndexOf("r.Retract(a.Why)", StringComparison.Ordinal),
                    "a pending answer can reach the retract");
                Assert(Body(comp, "private HoseReplanQueue.Work PrepareReplan(").Contains("HoseMath.CheckReplan(w, rect, far, len, failed, reason)")
                    && Body(comp, "private HoseReplanQueue.Work PrepareReplan(").Contains("TakeLayWorld()"), "the job is not CheckReplan on its own world copy");
                Assert(comp.Contains("if (r.replanPending || (now + r.parent.thingIDNumber) % 250 == 0) TickRecheck(r, now);"), "a pending replan is not polled every tick");
                Assert(comp.Contains("if (!r.laid) { if (r.replanPending) CancelReplan(r); continue; }"), "a reel no longer laid keeps its pending replan");
                Assert(comp.Contains("replanQueue.Forget(r.parent.thingIDNumber);"), "a forgotten reel's replan job is kept");
                // review: a lay that lands while the replan runs restarts it (the replan read the old lay and its failure reason)
                Assert(Body(comp, "private void ApplyLay(").Contains("if (r.replanPending) replanQueue.Forget(r.parent.thingIDNumber);"),
                    "a lay landing mid-replan leaves the replan of the old lay running (it could reel in a hose that now lays)");
                string net = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidNet.cs"));
                Assert(Body(net, "public bool Live(RM_NetLink l)").Contains("!r.replanPending"), "a pending hose still carries liquid (RM_HoseLinks.Live)");
            });

            Case("HoseReplan_R7 the real CheckReplan through the queue: deferred is Pending, landed is 'no route'", () =>
            {
                HoseReplanQueue.ResetQuota();
                var w = new CordWorld(40, 40);
                var reel = new HoseReelRect(5, 5, 2, 2);
                var far = new Cell(20, 20);
                for (int x = 19; x <= 21; x++)
                    for (int z = 19; z <= 21; z++)
                        if (x != 20 || z != 20) w.SetBlocked(new Cell(x, z), BlockKind.Wall);
                Assert(HoseMath.CheckReplan(w, reel, far, 30, false, null) == "no route", "can-fail: the walled-in target is 'no route' when run directly");
                Func<HoseReplanQueue.Work> prep = () => new HoseReplanQueue.Work { Run = () => HoseMath.CheckReplan(w, reel, far, 30, false, null) };
                // the quota spent this tick by other reels: this reel is deferred, and deferred is not an answer
                var other = new HoseReplanQueue { Async = false };
                for (int i = 0; i < HoseReplanQueue.MaxStartsPerTick; i++) other.Ask(100 + i, 0, 0, 77, () => Stand(() => null));
                var q = new HoseReplanQueue { Async = false };
                HoseReplanQueue.Answer a = q.Ask(1, 0, 0, 77, prep);
                Assert(a.Pending && a.Why == null && q.Deferred == 1, $"a replan deferred by the quota answered '{a.Why}'");
                a = q.Ask(1, 0, 0, 78, prep);
                Assert(!a.Pending && a.Why == "no route", $"next tick it ran and reads '{a.Why}'");
            });
        }
    }
}
