// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS (design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md §Ruled design): offline
// checks on the production leaf rules (RM_DrawbridgeMath) and the production call sites (RM_Drawbridges, the span base, the
// pocket grid). Phase 1 (core): leaves by material, tip-first raise state, per-leaf saved record, a forced pocket rebuild and
// repath on every toggle, and no Collapse on a raise. Each case has a can-fail. NOT proven here: a colonist re-routing at
// once in a live game (RAISE_PATH), a save made mid-raise reloading (SAVE_MIDRAISE): live rows, owed.
using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DrawbridgeChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

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
            Case("Drawbridge_P1_materials_timber_and_steel_only", () =>
            {
                Assert(RM_DrawbridgeMath.IsDrawbridgeTier(SuspensionTier.Timber) && RM_DrawbridgeMath.IsDrawbridgeTier(SuspensionTier.Steel),
                    "timber and steel are drawbridges");
                Assert(!RM_DrawbridgeMath.IsDrawbridgeTier(SuspensionTier.Rope) && !RM_DrawbridgeMath.IsDrawbridgeTier(SuspensionTier.Heavy),
                    "can-fail: rope and heavy are not (answer 8)");
                Assert(RM_DrawbridgeMath.DefaultMaxLeaf(SuspensionTier.Timber) == 4 && RM_DrawbridgeMath.DefaultMaxLeaf(SuspensionTier.Steel) == 8
                    && RM_DrawbridgeMath.DefaultMaxLeaf(SuspensionTier.Rope) == 0, "leaf length by material: timber 4, steel 8");
                Assert(!RM_DrawbridgeMath.IsPowered(SuspensionTier.Timber) && RM_DrawbridgeMath.IsPowered(SuspensionTier.Steel),
                    "timber is hand-winched, steel powered");
            });

            Case("Drawbridge_P1_split_one_leaf_or_two_each_hinged_on_its_own_bank", () =>
            {
                List<LeafSpan> one = RM_DrawbridgeMath.SplitLeaves(1, 4, 4, true);
                Assert(one != null && one.Count == 1 && one[0].First == 1 && one[0].Last == 4 && one[0].HingeAtFirst, "4 squares of timber: one leaf on bank A");
                List<LeafSpan> two = RM_DrawbridgeMath.SplitLeaves(1, 7, 4, true);
                Assert(two != null && two.Count == 2, "7 squares of timber: two leaves");
                Assert(two[0].First == 1 && two[0].Last == 4 && two[0].HingeAtFirst, "the colony leaf takes the odd square, hinged on A");
                Assert(two[1].First == 5 && two[1].Last == 7 && !two[1].HingeAtFirst, "can-fail: the far leaf hinges on the FAR bank (review answer 2)");
                List<LeafSpan> rev = RM_DrawbridgeMath.SplitLeaves(1, 7, 4, false);
                Assert(rev[0].First == 4 && rev[0].Last == 7 && !rev[0].HingeAtFirst && rev[1].First == 1 && rev[1].Last == 3 && rev[1].HingeAtFirst,
                    "colony on bank B: mirror");
                Assert(RM_DrawbridgeMath.SplitLeaves(1, 9, 4, true) == null, "can-fail: 9 squares is longer than two timber leaves");
                Assert(RM_DrawbridgeMath.SplitLeaves(1, 16, 8, true).Count == 2 && RM_DrawbridgeMath.SplitLeaves(1, 17, 8, true) == null, "steel: up to 16");
                Assert(RM_DrawbridgeMath.SplitLeaves(1, 4, 0, true) == null, "no leaf length: not a drawbridge");
            });

            Case("Drawbridge_P1_leaf_is_rigid_off_its_seat_and_reversible", () =>
            {
                LeafSpan a = new LeafSpan(1, 4, true);
                int full = RM_DrawbridgeMath.FullTicks(SuspensionTier.Timber, 4, 1f);
                Assert(full == 4 * RM_DrawbridgeMath.HandTicksPerSquare, "timber: about 4 s per square");
                Assert(RM_DrawbridgeMath.FullTicks(SuspensionTier.Steel, 8, 1f) == RM_DrawbridgeMath.PoweredTicksPerLeaf, "steel: about 2 s per leaf");
                for (int i = 1; i <= 4; i++) Assert(!RM_DrawbridgeMath.IsRaised(a, i, 0, full), "lowered: nothing raised");
                for (int i = 1; i <= 4; i++) Assert(RM_DrawbridgeMath.IsRaised(a, i, 1, full),
                    "can-fail (phase 2): one tick off its seat, EVERY square of the leaf has stopped being ground (a tilted plank)");
                Assert(!RM_DrawbridgeMath.IsRaised(a, 5, full, full) && !RM_DrawbridgeMath.IsRaised(a, 0, full, full), "only the leaf's own squares");
                Assert(RM_DrawbridgeMath.Step(0, true, full, 5) == 5 && RM_DrawbridgeMath.Step(full - 2, true, full, 5) == full
                    && RM_DrawbridgeMath.Step(3, false, full, 5) == 0, "steps clamp");
                Assert(RM_DrawbridgeMath.AtTarget(0, false, full) && !RM_DrawbridgeMath.AtTarget(0, true, full), "at target");
                Assert(RM_DrawbridgeMath.StateLine(0, false, full, false) == "lowered" && RM_DrawbridgeMath.StateLine(full, true, full, false) == "raised"
                    && RM_DrawbridgeMath.StateLine(full / 2, true, full, true) == "raising 50% (stopped)", "readout");
            });

            Case("Drawbridge_P2_tip_order_nearest_hinge_then_cell", () =>
            {
                var order = RM_DrawbridgeMath.TipOrder(new[]
                {
                    new RM_DrawbridgeMath.Rider(1, 3, 50), new RM_DrawbridgeMath.Rider(2, 0, 90), new RM_DrawbridgeMath.Rider(3, 0, 10),
                    new RM_DrawbridgeMath.Rider(4, 2, 7),
                });
                Assert(order[0].Id == 3 && order[1].Id == 2 && order[2].Id == 4 && order[3].Id == 1, "can-fail: hinge-near first, ties by cell");
                LeafSpan far = new LeafSpan(5, 7, false);
                Assert(far.FromHinge(7) == 0 && far.FromHinge(5) == 2, "a far-bank leaf counts from ITS hinge (review answer 2)");
            });

            Case("Drawbridge_P2_six_riders_one_free_square_one_lands_five_fall", () =>
            {
                // a 7x7 bank, x along, z across; the anchor at (3,0); walls everywhere but the anchor and one square beside it
                const int W = 7;
                Func<int, IEnumerable<int>> nb = i => Nbrs(i, W, W);
                var open = new HashSet<int> { 3, 3 + W };   // the anchor square and the square behind it
                var occupied = new HashSet<int> { 3 };      // a guard already stands on the anchor square
                List<int> landings = RM_DrawbridgeMath.BankLandings(new[] { 3 }, nb, i => open.Contains(i), i => !occupied.Contains(i), RM_DrawbridgeMath.TipReach);
                Assert(landings.Count == 1 && landings[0] == 3 + W, "one free legal square");
                var riders = new List<RM_DrawbridgeMath.Rider>();
                for (int k = 0; k < 6; k++) riders.Add(new RM_DrawbridgeMath.Rider(100 + k, k / 3, 200 + k));
                Dictionary<int, int> to = RM_DrawbridgeMath.AssignTips(riders, landings);
                int landed = 0, fell = 0;
                foreach (var kv in to) { if (kv.Value >= 0) landed++; else fell++; }
                Assert(landed == 1 && fell == 5, "can-fail: six riders, one free bank square: one lands, five fall (RAISE_TIPS_RIDERS)");
                Assert(to[100] == 3 + W, "the rider nearest the hinge (lowest cell) gets it");
            });

            Case("Drawbridge_P2_landings_never_through_a_wall_and_within_reach", () =>
            {
                const int W = 9;
                Func<int, IEnumerable<int>> nb = i => Nbrs(i, W, W);
                // a wall row at z=1 except nothing: the free ground beyond it is unreachable
                Func<int, bool> pass = i => i / W != 1;
                List<int> l = RM_DrawbridgeMath.BankLandings(new[] { 4 }, nb, pass, i => i != 4, RM_DrawbridgeMath.TipReach);
                foreach (int c in l) Assert(c / W == 0, "can-fail: nobody is moved through a wall");
                Assert(l.Count == 6, "z=0 row within 3 steps of x=4, minus the anchor: x=1..3, 5..7");
                Assert(l[0] == 3 || l[0] == 5, "nearest first");
                List<int> wide = RM_DrawbridgeMath.BankLandings(new[] { 4 }, nb, i => true, i => i != 4, RM_DrawbridgeMath.TipReach);
                foreach (int c in wide) Assert(Math.Abs(c % W - 4) + c / W <= RM_DrawbridgeMath.TipReach, "no landing past the reach");
            });

            Case("Drawbridge_P2_tip_wiring_once_per_raise_band_aware_overflow_falls", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string tick = Body(db, "public static void Tick(RM_MapComponent_SuspensionBridges comp, int now)");
                int tip = tick.IndexOf("fallers = Tip(comp.map, r, l);"), apply = tick.IndexOf("Apply(comp.map, r, l);", Math.Max(tip, 0)), fall = tick.IndexOf("Fall(comp.map, r, fallers);");
                Assert(tip > 0 && apply > tip && fall > apply, "can-fail: riders tip BEFORE the squares open, the overflow falls AFTER");
                Assert(tick.Contains("if (l.progress > 0 && !l.tipCommitted)") && tick.Contains("l.tipCommitted = true;"), "the tip is committed once per raise");
                string t = Body(db, "public static List<Pawn> Tip(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)");
                Assert(t.Contains("RM_MapComponent_SuspensionBridges.PawnsOn(map, c)"), "riders by band (PawnsOn skips the floor band underneath)");
                Assert(t.Contains("int hinge = HingeIndex(l);") && Body(db, "public static int HingeIndex(DrawbridgeLeaf l)").Contains("l.hingeAtFirst ? l.first - 1 : l.last + 1"),
                    "each leaf tips toward its OWN hinge");
                Assert(t.Contains("!door.Open") && t.Contains("bridgeDeck.Contains(c)"), "never through a closed gate or across the bridge");
                Assert(t.Contains("p.Notify_Teleported(true, true);") && !t.Contains("SetFaction") && !t.Contains("TakeDamage"),
                    "tipped riders keep faction and take no landing damage");
                Assert(t.Contains("colonyBank && p.HostileTo(Faction.OfPlayer)") && t.Contains("pulled++"), "hostiles tipped onto the colony bank count as pulled inside");
                string f = Body(db, "public static void Fall(Map map, SuspensionBridgeRecord r, List<Pawn> fallers)");
                Assert(f.Contains("RM_SuperdeepTrap.OnForcedDescent(p, p.Position, state, drop);"), "the overflow falls through the ordinary descent event");
            });

            Case("Drawbridge_P3_sides_raise_either_lower_winch_only", () =>
            {
                Assert(RM_DrawbridgeMath.MayWorkFrom(true, true) && RM_DrawbridgeMath.MayWorkFrom(false, true), "a raise works from either bank");
                Assert(RM_DrawbridgeMath.MayWorkFrom(true, false) && !RM_DrawbridgeMath.MayWorkFrom(false, false),
                    "can-fail: a lower works only from the winch bank (LOWER_ONLY_FROM_WINCH)");
                string c = Src("Pits", "Drawbridge", "RM_DrawbridgeControl.cs");
                string job = Body(c, "public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)");
                Assert(job.Contains("RM_DrawbridgeMath.MayWorkFrom(t is Building_DrawbridgeWinch, raise)"), "the work giver offers a lower only at the winch");
                string spots = Body(c, "private static IEnumerable<(SuspensionBridgeRecord r, DrawbridgeLeaf l, Thing spot)> Spots(Map map)");
                Assert(spots.Contains("raise ? FarAnchor(map, r, l) : null"), "the far anchor is a work spot for a raise only");
                Assert(c.Contains("|| !RM_DrawbridgeMath.MayWorkFrom(job.targetA.Thing is Building_DrawbridgeWinch, raise))"),
                    "the driver re-checks the side when the colonist arrives (the order commits there)");
            });

            Case("Drawbridge_P3_drive_timber_hands_steel_power_freezes", () =>
            {
                Assert(RM_DrawbridgeMath.DriveMoves(SuspensionTier.Timber, true, false, true) && !RM_DrawbridgeMath.DriveMoves(SuspensionTier.Timber, true, true, false),
                    "can-fail: timber moves only while a colonist turns the winch");
                Assert(RM_DrawbridgeMath.DriveMoves(SuspensionTier.Steel, true, true, false) && !RM_DrawbridgeMath.DriveMoves(SuspensionTier.Steel, true, false, true),
                    "can-fail: steel moves on power, never by hand (no hand fallback)");
                Assert(!RM_DrawbridgeMath.DriveMoves(SuspensionTier.Timber, false, true, true), "no winch house: nothing moves it");
                Assert(RM_DrawbridgeMath.FrozenFor(SuspensionTier.Steel, true, false) && !RM_DrawbridgeMath.FrozenFor(SuspensionTier.Steel, true, true)
                    && !RM_DrawbridgeMath.FrozenFor(SuspensionTier.Timber, true, false), "steel without power freezes (STEEL_UNPOWERED_FREEZES)");
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string tick = Body(db, "public static void Tick(RM_MapComponent_SuspensionBridges comp, int now)");
                Assert(tick.IndexOf("l.frozen = RM_DrawbridgeMath.FrozenFor(") < tick.IndexOf("RM_DrawbridgeMath.Step(") && tick.Contains("if (l.frozen ||"),
                    "a frozen leaf holds where it is");
                Assert(tick.Contains("now <= l.workedUntilTick"), "the hand winch moves only while worked");
            });

            Case("Drawbridge_P3_winch_lost_crashes_down_and_hits", () =>
            {
                Assert(RM_DrawbridgeMath.WinchLossCrashes(1) && !RM_DrawbridgeMath.WinchLossCrashes(0), "a leaf off its seat crashes; a lowered one has nothing to crash");
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string lost = Body(db, "public static void Notify_WinchLost(Map map, Building_DrawbridgeWinch w)");
                Assert(lost.Contains("Crash(map, r, l);") && !lost.Contains("frozen = true"),
                    "can-fail: owner follow-up: a destroyed winch CRASHES the leaf (the withdrawn rule froze it)");
                string crash = Body(db, "public static void Crash(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)");
                Assert(crash.Contains("l.progress = 0;") && crash.Contains("Apply(map, r, l);") && crash.Contains("p.TakeDamage(dinfo);"),
                    "it slams down to lowered and hits anything under it");
                string c = Src("Pits", "Drawbridge", "RM_DrawbridgeControl.cs");
                Assert(Body(c, "public override void Destroy(DestroyMode mode = DestroyMode.Vanish)").Contains("RM_Drawbridges.Notify_WinchLost(map, this);"),
                    "the winch house reports its loss");
            });

            Case("Drawbridge_P3_one_winch_per_leaf_on_its_own_bank", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string link = Body(db, "public static void LinkWinch(Building_DrawbridgeWinch w)");
                Assert(link.Contains("if (l.winch != null && l.winch.Spawned)") && link.Contains("AdjacentToCardinal(r.Cell(lane, HingeIndex(l)))"),
                    "can-fail: a winch takes only a leaf with no winch, beside THAT leaf's hinge anchor");
                Assert(db.Contains("Scribe_References.Look(ref winch, \"winch\");"), "the leaf keeps a stable reference to its winch (R9)");
            });

            Case("Drawbridge_P3_peace_auto_lowers_free_hostiles_lock", () =>
            {
                Assert(RM_DrawbridgeMath.IsFreeHostile(true, false, false), "a free hostile");
                Assert(!RM_DrawbridgeMath.IsFreeHostile(true, true, false) && !RM_DrawbridgeMath.IsFreeHostile(true, false, true),
                    "can-fail: a hostile trapped in a pit or held prisoner does not lock (review answer 3)");
                Assert(RM_DrawbridgeMath.ShouldAutoLower(false, false, 50, true, false), "peace: a raised leaf lowers itself");
                Assert(!RM_DrawbridgeMath.ShouldAutoLower(true, false, 50, true, false), "can-fail: locked: it never lowers by itself");
                Assert(!RM_DrawbridgeMath.ShouldAutoLower(false, true, 50, true, false), "hold raised keeps it up in peace");
                Assert(!RM_DrawbridgeMath.ShouldAutoLower(false, false, 0, false, false), "already down: nothing to do");
                Assert(RM_DrawbridgeMath.ShouldCancelAutoLower(true, true) && !RM_DrawbridgeMath.ShouldCancelAutoLower(true, false),
                    "locking cancels a pending automatic lower (HOSTILE_LOCKS)");
                Assert(RM_DrawbridgeMath.HoldAfterOrder(true, false, false) && !RM_DrawbridgeMath.HoldAfterOrder(true, true, false)
                    && !RM_DrawbridgeMath.HoldAfterOrder(false, false, true), "a peacetime raise holds; a locked raise comes down after; lower clears");
                Assert(RM_DrawbridgeMath.LockLine(true, 2, false).StartsWith("Locked: 2 free hostiles"), "the readout says why it is locked");
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string mode = Body(db, "private static void Mode(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l, int now)");
                Assert(mode.Contains("FreeHostileCount(map, true) == 0"), "can-fail: the hostile check is made again when the lower commits (atomic)");
                Assert(!mode.Contains("l.targetRaised = true; l.autoLowering = true") && !mode.Contains("OrderRaise;"),
                    "a hostile's arrival never raises a leaf by itself");
                string count = Body(db, "public static int FreeHostileCount(Map map, bool fresh)");
                Assert(count.Contains("RM_SuperdeepTrap.IsTrapped(p)") && count.Contains("p.IsPrisoner") && count.Contains("GenHostility.IsActiveThreatTo"),
                    "the pit engine's own trapped test and prisoners");
            });

            Case("Drawbridge_P4_raid_plank_fits_and_commits_once", () =>
            {
                Assert(RM_DrawbridgeMath.RaidPlankFits(new[] { 0, 6, 6, 6, 0 }, 4), "a 3-square moat between level banks takes a plank");
                Assert(!RM_DrawbridgeMath.RaidPlankFits(new[] { 0, 6, 6, 6, 6, 6, 0 }, 4), "can-fail: 5 squares is past the span limit");
                Assert(!RM_DrawbridgeMath.RaidPlankFits(new[] { 0, 6, 6, 2 }, 4), "can-fail: banks at different heights");
                Assert(!RM_DrawbridgeMath.RaidPlankFits(new[] { 0, 0, 0 }, 4) && !RM_DrawbridgeMath.RaidPlankFits(new[] { 0, 0 }, 4), "no hole, no plank");
                Assert(RM_DrawbridgeMath.RaidPlankCount(1) == 1 && RM_DrawbridgeMath.RaidPlankCount(8) == 2 && RM_DrawbridgeMath.RaidPlankCount(0) == 0,
                    "one plank per four raiders");
                var led = new RM_DrawbridgeMath.PlankLedger();
                long line = RM_DrawbridgeMath.PlankLedger.LineKey(40, 10);
                Assert(line == RM_DrawbridgeMath.PlankLedger.LineKey(10, 40), "a line is the same from either end");
                Assert(led.TryCommit(7, line) && led.Laid == 1, "the first commit lays it");
                Assert(!led.TryCommit(7, RM_DrawbridgeMath.PlankLedger.LineKey(1, 2)), "can-fail: the same plank is never laid twice (RAID_PLANK)");
                Assert(!led.TryCommit(8, line), "can-fail: a second plank on a planked line is refused");
                Assert(led.Laid == 1, "counted exactly once");
            });

            Case("Drawbridge_P4_raiders_trench_hand_off_and_winch", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string repath = Body(db, "public static void RepathOver(Map map, List<IntVec3> changed)");
                Assert(repath.Contains("p.jobs.EndCurrentJob(JobCondition.InterruptForced);"), "can-fail: a raider's job over the leaf is ended (GPT #12)");
                string raid = Src("Pits", "Drawbridge", "RM_DrawbridgeRaid.cs");
                string give = Body(raid, "protected override Job TryGiveJob(Pawn pawn)");
                Assert(give.Contains("TraverseMode.PassAllDestroyableThings") && give.Contains("return null; // the colony is reachable"),
                    "the winch giver acts only when the colony is cut off");
                Assert(give.Contains("RM_RaiderTrench.IsSiege(pawn)"), "sieges never");
                string wj = Body(raid, "public static Job WinchJob(Pawn pawn, Building_DrawbridgeWinch winch)");
                Assert(wj.Contains("DigUtility.PassBlockerJob") && wj.Contains("JobDefOf.AttackMelee") && wj.Contains("CastPositionFinder.TryFindCastPosition"),
                    "walk and dig to it, hit it; from the far bank only shoot it");
                string patch = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")), "..", "Patches", "RaiderTrench", "FlowWorks_RaiderTrenchDuties.xml"));
                Assert(patch.Contains("<li Class=\"RimMandrake.FlowWorks.Pits.JobGiver_RM_DrawbridgeWinch\" />")
                    && patch.Split("JobGiver_RM_DrawbridgeWinch").Length - 1 == 2, "in the Sapper and Breaching duties only");
                string trench = Src("Superdeep", "RM_RaiderTrench.cs");
                string cross = Body(trench, "public static Job TryCross(Pawn p)");
                Assert(cross.IndexOf("RM_RaidPlanks.PlankJob(p, plan.cells, plan.depths)") > 0
                    && cross.IndexOf("RM_RaidPlanks.PlankJob") < cross.IndexOf("JumpJob(p, plan, k)"), "a carried plank is tried before the jump");
                string lay = Body(raid, "public static bool TryLay(Pawn p, IntVec3 lip, IntVec3 far)");
                Assert(lay.IndexOf("TryCommit(plank.thingIDNumber, line)") < lay.IndexOf("plank.Destroy(") && lay.Contains("raidPlank = true"),
                    "commit first, then the plank is used up and a raid-plank span is laid");
                string drv = Body(raid, "protected override IEnumerable<Toil> MakeNewToils()");
                Assert(drv.IndexOf("Toils_General.Wait") < drv.IndexOf("RM_RaidPlanks.TryLay"), "the commit is the job's last step: an interrupted carrier lays nothing");
            });

            Case("Drawbridge_P5_hoses_on_a_leaf_cut_while_raised_rejoin_lowered", () =>
            {
                string ends = Src("Hose", "HoseEnds.cs");
                string read = Body(ends, "public static HoseFreeEnd Read(CompHoseReel r)");
                Assert(read.Contains("if (Pits.RM_Drawbridges.HoseCut(r)) return e;"), "can-fail: a hose over a raised leaf has no end (disconnected)");
                Assert(read.IndexOf("HoseCut(r)") < read.IndexOf("e.Cell = r.far;"), "the cut is read before the end is joined");
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string cut = Body(db, "public static bool LineCutAt(Map map, IEnumerable<IntVec3> cells)");
                Assert(cut.Contains("StructuralDeckAt(map, c)") && cut.Contains("d.Raised"), "cut = a raised leaf square under the line; lowered, it rejoins");
                Assert(Body(db, "public static void NotifyToggled(Map map, List<IntVec3> changed)").Contains("InvalidateEnds()"),
                    "a toggle re-reads every hose end at once");
                string hoses = Src("Hose", "RM_MapComponent_Hoses.cs");
                Assert(Body(hoses, "public void InvalidateEnds()").Contains("ends.Clear();"), "the 60-tick end cache is dropped");
                Assert(!db.Contains("RouteCells("), "a cut hose never re-routes across the opened moat");
            });

            Case("Drawbridge_P5_gravship_edge_bridge_collapses_at_launch", () =>
            {
                string g = Src("Pits", "Drawbridge", "RM_DrawbridgeGravship.cs");
                Assert(g.Contains("[HarmonyPatch(typeof(GravshipUtility), nameof(GravshipUtility.GenerateGravship))]") && g.Contains("[HarmonyPrefix]"),
                    "can-fail: runs before the ship's things are gathered");
                string pre = Body(g, "public static void Prefix(Building_GravEngine engine)");
                Assert(pre.Contains("comp.CollapseSpan(d,") && pre.Contains("TouchesShip(r, ship)"), "a bridge touching the ship collapses, riders fall");
                Assert(Body(g, "public static bool TouchesShip(SuspensionBridgeRecord r, HashSet<IntVec3> ship)").Contains("for (int lane = 0; lane < r.width; lane++)"),
                    "every lane and both anchors count");
            });

            Case("Drawbridge_P5_length_by_material_from_settings", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string max = Body(db, "public static int MaxLeaf(SuspensionTier t)");
                Assert(max.Contains("RM_DrawbridgeSettings.maxLeafTimber") && max.Contains("RM_DrawbridgeSettings.maxLeafSteel") && max.Contains("default: return 0;"),
                    "can-fail: leaf length is the material's setting; rope and heavy have none");
                string set = Src("Pits", "Drawbridge", "RM_DrawbridgeSettings.cs");
                Assert(set.Contains("public static int maxLeafTimber = 4;") && set.Contains("public static int maxLeafSteel = 8;"), "defaults timber 4, steel 8");
                Assert(Body(db, "public static bool CanBeDrawbridge(SuspensionBridgeRecord r, out string why)").Contains("SplitLeaves(1, r.length - 2, MaxLeaf(r.tier), true) == null"),
                    "a bridge longer than two leaves of its material is refused");
            });

            Case("Drawbridge_P6_gate_never_open_on_a_raised_leaf_locked_only_by_order", () =>
            {
                Assert(RM_DrawbridgeMath.GateOpensFor(false, false, false), "peace, leaf down: a door for its people");
                Assert(!RM_DrawbridgeMath.GateOpensFor(false, true, true) && !RM_DrawbridgeMath.GateOpensFor(true, true, true),
                    "can-fail: never while the leaf is up, even held open");
                Assert(!RM_DrawbridgeMath.GateOpensFor(true, false, false) && RM_DrawbridgeMath.GateOpensFor(true, false, true),
                    "can-fail: locked, it opens for nobody automatically, only by the player's hold-open order");
                string c = Src("Pits", "Drawbridge", "RM_DrawbridgeControl.cs");
                Assert(c.Contains("public class Building_DrawbridgeGate : Building_Door"), "a custom door (R7), not vanilla semantics");
                string open = Body(c, "public override bool PawnCanOpen(Pawn p)");
                Assert(open.IndexOf("base.PawnCanOpen(p)") < open.IndexOf("GateOpensFor("), "the door's own faction rules first, then the bridge's mode");
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                Assert(Body(db, "private static void Mode(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l, int now)").Contains("map.reachability?.ClearCache();"),
                    "a lock or unlock re-reads reachability (gates change)");
            });

            Case("Drawbridge_P6_real_build_buttons", () =>
            {
                string d = Src("Pits", "Suspension", "Designator_SuspensionBridge.cs");
                Assert(d.Contains("public class Designator_Drawbridge_Timber : Designator_Drawbridge") && d.Contains("public class Designator_Drawbridge_Steel : Designator_Drawbridge"),
                    "timber and steel drawbridge buttons");
                Assert(!d.Contains("Designator_Drawbridge_Rope") && !d.Contains("Designator_Drawbridge_Heavy"), "can-fail: no rope or heavy drawbridge");
                Assert(d.Contains("if (why == null && Drawbridge && !RM_Drawbridges.MakeDrawbridge(r, RM_Drawbridges.ColonyEndIsFirst(map, r), out string dwhy))"),
                    "can-fail: the drag is cut into leaves BEFORE it is placed, or refused");
                Assert(Body(d, "public abstract class Designator_Drawbridge : Designator_SuspensionBridge").Contains("RM_DrawbridgeSettings.drawbridgesEnabled"),
                    "the buttons follow \"Drawbridges can be built\"");
                string patch = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")), "..", "Patches", "Pits", "RM_SuspensionBridges.xml"));
                Assert(patch.Contains("<li>RimMandrake.FlowWorks.Pits.Designator_Drawbridge_Timber</li>") && patch.Contains("<li>RimMandrake.FlowWorks.Pits.Designator_Drawbridge_Steel</li>"),
                    "in the Structure tab");
            });

            Case("Drawbridge_P6_art_contract_paths_with_stand_ins", () =>
            {
                string a = Src("Pits", "Drawbridge", "RM_DrawbridgeArt.cs");
                Assert(a.Contains("public const string Dir = \"Things/Building/FlowWorks/Drawbridge/\";") && a.Contains("\"RM_DrawbridgeLeafUp_\""),
                    "the design doc's contract paths");
                Assert(a.Contains("ContentFinder<Texture2D>.Get(p, false)") && !a.Contains("Get(p, true)"), "can-fail: looked up silently (no red error before install)");
                Assert(a.Contains("\"Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_\" + Material(t)"), "a stand-in that exists on disk");
                Assert(Body(a, "public static LeafView ViewFor(Rot4 spanFromHinge)").Contains("spanFromHinge == Rot4.North ? LeafView.Face : spanFromHinge == Rot4.South ? LeafView.Underside : LeafView.Edge"),
                    "north face, south underside, east/west edge (contract)");
                string xml = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")), "..", "Defs", "Pits", "ThingDefs", "RM_Drawbridge.xml"));
                Assert(!xml.Contains("Things/Building/FlowWorks/Drawbridge/"), "can-fail: no def names an uninstalled texture (it would load pink)");
                Assert(!xml.Contains("MinifiedThing") && !xml.Contains("<defName>RM_DrawbridgePlanks"), "the art planks are never an item (answer 1)");
            });

            Case("Drawbridge_P1_decked_reads_raised_and_only_drawbridge_decks_raise", () =>
            {
                string b = Src("Pits", "Building_SpanDeck.cs");
                Assert(b.Contains("public bool Decked => !collapsed && Spawned && !Raised;"), "can-fail: a raised square is not ground (R13.2)");
                Assert(b.Contains("public virtual bool Raised => false;"), "the base never raises");
                string d = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                Assert(d.Contains("public override bool Raised => leafRaised;"), "a suspension deck reads its leaf");
                Assert(d.Contains("leafRaised = RM_Drawbridges.RaisedAt(map, Position);"), "a reload reads the leaf record on spawn");
                Assert(!d.Contains("Scribe_Values.Look(ref leafRaised"), "the deck never saves its own raised flag (one saved state: the leaf)");
                string print = Body(d, "public override void Print(SectionLayer layer)");
                Assert(print.IndexOf("if (leafRaised)") >= 0 && print.IndexOf("if (leafRaised)") < print.IndexOf("RM_SuspensionDeckLink.Print"),
                    "a raised square draws empty (R12)");
            });

            Case("Drawbridge_P1_structure_reads_see_a_raised_leaf", () =>
            {
                string c = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                string span = Body(c, "public List<Building_SpanDeck> SpanDecks(IntVec3 c)");
                Assert(span.Contains("StructuralDeckAt(map, cell)"), "a span giving way takes its raised squares too (R6)");
                Assert(!span.Contains(" DeckAt(map, cell)"), "can-fail: the walking read would leave raised squares standing after a collapse");
                string tick = Body(c, "public override void MapComponentTick()");
                Assert(tick.Contains("StructuralDeckAt(map, c)") && tick.Contains("d.DropAlone();"), "a swing-down drops raised squares too");
                Assert(tick.Contains("RM_Drawbridges.Tick(this, now);"), "leaves move from the bridges tick");
                Assert(Body(c, "public static Building_SuspensionDeck StructuralDeckAt(Map map, IntVec3 c)").Contains("!d.Collapsed"), "structure = intact");
            });

            Case("Drawbridge_P1_toggle_forces_pocket_rebuild_and_repath", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string notify = Body(db, "public static void NotifyToggled(Map map, List<IntVec3> changed)");
                foreach (string must in new[] { "RecalculatePerceivedPathCostAt(c)", "reachability?.ClearCache()", "BumpClimbGeneration()",
                    "RM_SwimPathing.Bump(map)", "RM_PocketGrid.ForceRebuild(map)", "RepathOver(map, changed)" })
                {
                    Assert(notify.Contains(must), "can-fail: a toggle must " + must + " (R8)");
                }
                string apply = Body(db, "public static void Apply(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)");
                Assert(apply.Contains("NotifyToggled(map, changed)") && apply.Contains("if (changed != null)"), "every toggle that changed a square notifies");
                string repath = Body(db, "public static void RepathOver(Map map, List<IntVec3> changed)");
                Assert(repath.Contains("pf.curPathRequest != null") && repath.Contains("pf.StopDead();") && repath.Contains("pf.StartPath(dest, pe);"),
                    "a pending request (old generation) or a path over a changed square is re-pathed");
                string pg = Src("Superdeep", "RM_PocketGrid.cs");
                string force = Body(pg, "public static void ForceRebuild(Map map)");
                Assert(force.Contains("RebuildIfStale(map, RM_SuperdeepTrap.EngineOf(map), true)"), "can-fail: the forced rebuild bypasses the 60-tick limit");
            });

            Case("Drawbridge_P1_raise_never_collapses", () =>
            {
                // the RAW file (Src collapses whitespace, which would leave no line ends for the comment strip)
                string raw = File.ReadAllText(RiverSwitchFlipChecks.SrcPath(Path.Combine("Pits", "Drawbridge", "RM_Drawbridges.cs")));
                string code = StripComments(raw.Replace(Body(raw, "public static void Fall(Map map, SuspensionBridgeRecord r, List<Pawn> fallers)"), ""));
                Assert(code.Contains("public static void Tick(") && code.Contains("NotifyToggled("), "the strip kept the code (can-fail guard on the guard)");
                Assert(!code.Contains("OnForcedDescent("), "only the overflow (Fall) ever descends");
                foreach (string bad in new[] { "Collapse(", "CollapseSpan(", "DropAlone(", ".Destroy(", "LandWreck(" })
                {
                    Assert(!code.Contains(bad), "can-fail: a raise or lower must never call " + bad + " (R3)");
                }
            });

            Case("Drawbridge_P1_leaf_record_saves_per_leaf_versioned", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string ex = Body(db, "public void ExposeData()");
                foreach (string key in new[] { "\"v\"", "\"first\"", "\"last\"", "\"hingeAtFirst\"", "\"controlAtFirst\"", "\"targetRaised\"",
                    "\"progress\"", "\"frozen\"", "\"holdRaised\"", "\"tipCommitted\"" })
                {
                    Assert(ex.Contains(key), "can-fail: the leaf record saves " + key + " (R9)");
                }
                string c = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                Assert(c.Contains("Scribe_Collections.Look(ref leaves, \"rmDrawbridgeLeaves\", LookMode.Deep);"), "leaves are saved on their bridge");
                Assert(c.Contains("public bool IsDrawbridge => leaves != null && leaves.Count > 0;"), "an old save (no leaves) is a plain bridge, lowered");
                Assert(!c.Contains("raisedSquares"), "the withdrawn single raisedSquares int is gone (GPT #11)");
                string make = Body(db, "public static bool MakeDrawbridge(SuspensionBridgeRecord r, bool colonyBankAtFirst, out string why)");
                Assert(make.Contains("hingeAtFirst = s.HingeAtFirst, controlAtFirst = s.HingeAtFirst"), "each leaf is worked from its own winch bank");
                string can = Body(db, "public static bool CanBeDrawbridge(SuspensionBridgeRecord r, out string why)");
                Assert(can.Contains("IsDrawbridgeTier(r.tier)") && can.Contains("r.jetty") && can.Contains("r.towers"), "timber/steel, no jetty, no towers");
            });
        }

        private static IEnumerable<int> Nbrs(int i, int w, int h)
        {
            int x = i % w, z = i / w;
            if (x > 0) yield return i - 1;
            if (x < w - 1) yield return i + 1;
            if (z > 0) yield return i - w;
            if (z < h - 1) yield return i + w;
        }

        private static string StripComments(string s)
        {
            var sb = new System.Text.StringBuilder();
            foreach (string line in s.Split('\n'))
            {
                int i = line.IndexOf("//", StringComparison.Ordinal);
                string l = i >= 0 ? line.Substring(0, i) : line;
                if (l.TrimStart().StartsWith("///")) continue;
                sb.Append(l).Append('\n');
            }
            return sb.ToString();
        }
    }
}
