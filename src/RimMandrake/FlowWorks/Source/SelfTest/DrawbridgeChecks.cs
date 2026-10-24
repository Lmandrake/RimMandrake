// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS (design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md §Ruled design): offline
// checks on the production leaf rules (RM_DrawbridgeMath) and the production call sites (RM_Drawbridges, the span base, the
// pocket grid). Phase 1 (core): leaves by material, tip-first raise state, per-leaf saved record, a forced pocket rebuild and
// repath on every toggle, and no Collapse on a raise. Each case has a can-fail. NOT proven here: a colonist re-routing at
// once in a live game (RAISE_PATH), a save made mid-raise reloading (SAVE_MIDRAISE): live rows, owed.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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
                string t = Body(db, "public static List<Pawn> Tip(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l, int[] preview = null)");
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
                int frz = tick.IndexOf("l.frozen = RM_DrawbridgeMath.FrozenFor(");
                Assert(frz >= 0 && frz < tick.IndexOf("RM_DrawbridgeMath.Step(") && tick.Contains("if (l.frozen ||"),
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
                Assert(Body(c, "public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)").Contains("RM_Drawbridges.Notify_WinchLost(map, this);"),
                    "the winch house reports its loss");
            });

            Case("Drawbridge_P3_winch_gone_any_way_crashes_and_unlinks", () =>
            {
                // the review (7d97084652): only Destroy reported; a gravship launch DeSpawns (WillReplace) without destroying,
                // leaving a stale leaf.winch and no crash. Every despawn now reports; destroy reaches it through DeSpawn.
                Assert(RM_DrawbridgeMath.WinchDepartureCrashes(5, false), "flown off / deconstructed / any despawn while up: crash (ruled general rule)");
                Assert(!RM_DrawbridgeMath.WinchDepartureCrashes(0, false), "a lowered leaf has nothing to crash");
                Assert(!RM_DrawbridgeMath.WinchDepartureCrashes(5, true), "can-fail: a bridge torn loose at the same launch already fell; no second crash");
                string c = Src("Pits", "Drawbridge", "RM_DrawbridgeControl.cs");
                Assert(!c.Contains("public override void Destroy(DestroyMode mode"), "can-fail: the loss hook sits on Destroy only (a gravship despawn never fires it)");
                string despawn = Body(c, "public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)");
                Assert(despawn.Contains("base.DeSpawn(mode);") && !despawn.Contains("mode ==") && !despawn.Contains("Destroyed"),
                    "every despawn mode reports, not just a kill or a destroy");
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string lost = Body(db, "public static void Notify_WinchLost(Map map, Building_DrawbridgeWinch w)");
                int unlink = lost.IndexOf("l.winch = null;", StringComparison.Ordinal);
                Assert(lost.Contains("if (l.winch != w)") && unlink >= 0 && unlink < lost.IndexOf("Crash(map, r, l);", StringComparison.Ordinal),
                    "idempotent: the link is cleared before the crash, and a second call finds no leaf on this winch");
                Assert(lost.Contains("RM_DrawbridgeMath.WinchDepartureCrashes(l.progress, tornLoose)")
                    && lost.Contains("GravshipUtility.generatingGravship && RM_Patch_GravshipLaunch_Bridges.TornLoose.Contains(r)"),
                    "the launch exception is read only during the launch, from the bridges that launch tore loose");
                string g = Src("Pits", "Drawbridge", "RM_DrawbridgeGravship.cs");
                string pre = Body(g, "public static void Prefix(Building_GravEngine engine)");
                int added = pre.IndexOf("TornLoose.Add(r);", StringComparison.Ordinal);
                Assert(pre.IndexOf("TornLoose.Clear();", StringComparison.Ordinal) >= 0
                    && added >= 0 && added < pre.IndexOf("comp.CollapseSpan(d,", StringComparison.Ordinal),
                    "each launch refills the torn-loose set before collapsing");
                string swap = Body(c, "public override void PostSwapMap()");
                Assert(swap.Contains("!RM_Drawbridges.LeafOfWinch(this, out _, out _)") && swap.Contains("RM_Drawbridges.LinkWinch(this);"),
                    "a winch that landed re-keys to a leaf beside it on the landing map, as a new one does (GSS GS-1 PostSwapMap)");
            });

            Case("Drawbridge_P1_tower_mid_span_refused", () =>
            {
                Assert(RM_DrawbridgeMath.TowerMayJoin(false) && !RM_DrawbridgeMath.TowerMayJoin(true), "can-fail: a drawbridge takes no tower");
                Assert(RM_DrawbridgeMath.TowerOnDrawbridgeRefused.Contains("cannot stand on towers"), "the rejection says why");
                string pw = Body(Src("Pits", "Suspension", "Designator_SuspensionBridge.cs"), "public class PlaceWorker_SuspensionOverHole : PlaceWorker");
                Assert(pw.Contains("RM_DrawbridgeMath.TowerMayJoin(RM_MapComponent_SuspensionBridges.Of(map)?.RecordAt(loc)?.IsDrawbridge ?? false)")
                    && pw.Contains("return RM_DrawbridgeMath.TowerOnDrawbridgeRefused;"),
                    "can-fail: placement over a drawbridge (a raised leaf is not decked) is refused");
                string built = Body(Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs"), "public void Notify_TowerBuilt(Building_SuspensionTower t)");
                int refuse = built.IndexOf("!RM_DrawbridgeMath.TowerMayJoin(r.IsDrawbridge)", StringComparison.Ordinal);
                Assert(refuse >= 0 && refuse < built.IndexOf("r.towers.Add(i);", StringComparison.Ordinal),
                    "can-fail: a frame completed or a rebuild finished on a drawbridge is not added to its supports");
                // review pass 2 (2026-10-21): the refused tower, deconstructed, still swung the whole drawbridge down
                // (Notify_SupportLost re-added it with WithTower and queued both sides)
                Assert(Body(Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs"), "public void Notify_SupportLost(IntVec3 c)")
                    .Contains("if (!r.towers.Remove(i))"), "can-fail: losing a tower that never held the bridge swings nothing down");
                Assert(Body(Src("Pits", "Drawbridge", "RM_Drawbridges.cs"), "public static bool CanBeDrawbridge(SuspensionBridgeRecord r, out string why)")
                    .Contains("a drawbridge cannot stand on towers"), "the forming rule still refuses a bridge on towers");
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
                int commit = lay.IndexOf("TryCommit(plank.thingIDNumber, line)");
                Assert(commit >= 0 && commit < lay.IndexOf("plank.Destroy(") && lay.Contains("raidPlank = true"),
                    "commit first, then the plank is used up and a raid-plank span is laid");
                string drv = Body(raid, "protected override IEnumerable<Toil> MakeNewToils()");
                int wait = drv.IndexOf("Toils_General.Wait");
                Assert(wait >= 0 && wait < drv.IndexOf("RM_RaidPlanks.TryLay"), "the commit is the job's last step: an interrupted carrier lays nothing");
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

            // DRAWBRIDGE_HOSE_FIX_STAYS_LINKED_RAISED (GPT review FA_core_sim_1.3 / FB_hose_gss_1.4): the liquid net built its links
            // from the relay index and rebuilt a null end as a free Intake/Outflow port, so a hose over a raised leaf kept moving liquid
            Case("Drawbridge_hose_cut_by_a_raised_leaf_carries_no_liquid", () =>
            {
                string net = Src("Machinery", "RM_LiquidNet.cs");
                string ends = Body(net, "private static bool Ends(RM_MapComponent_Hoses comp, CompHoseReel r, out object inlet, out object far)");
                int cut = ends.IndexOf("RM_Drawbridges.HoseCut(r)", StringComparison.Ordinal);
                Assert(cut >= 0, "can-fail: the net's link builder reads the leaf cut");
                Assert(cut < ends.IndexOf("comp.FeedsInto(r)", StringComparison.Ordinal) && cut < ends.IndexOf("r.FreeEnd()", StringComparison.Ordinal),
                    "the cut is read before the relay and before a null end becomes a free Intake/Outflow port");
                Assert(Body(net, "public bool Live(RM_NetLink l)").Contains("RM_Drawbridges.HoseCut(r)"),
                    "a route's link re-checked at transfer time drops the moment the leaf goes up");
            });

            // RAID_PLANK_FIX_SURFACE_HEIGHT_SUNKEN (GPT review FC_pits_superdeep_1.9): a plank between two sunken banks was registered
            // with deckNotches 0, a surface deck
            Case("Drawbridge_raid_plank_between_sunken_banks_lies_at_their_depth", () =>
            {
                string raid = Src("Pits", "Drawbridge", "RM_DrawbridgeRaid.cs");
                string lay = Body(raid, "public static bool TryLay(Pawn p, IntVec3 lip, IntVec3 far)");
                Assert(lay.Contains("deckNotches = RM_SuspensionMath.DeckNotchesFor(depths[0], depths[n], RM_SuspensionSettings.sunkenBridges)"),
                    "can-fail: the plank's record carries the banks' depth, read the way a built bridge reads it");
                string free = Body(raid, "public static bool LineFree(Map map, List<IntVec3> cells, int[] depths)");
                Assert(free.Contains("RM_SuspensionMath.DeckNotchesFor(depths[0], depths[depths.Length - 1], RM_SuspensionSettings.sunkenBridges) < 0"),
                    "a line whose banks no bridge could stand on (sunken, sunken bridges off) is refused before the commit");
                Assert(RM_SuspensionMath.DeckNotchesFor(4, 4, true) == 4 && RM_SuspensionMath.DeckNotchesFor(4, 4, false) < 0
                    && RM_SuspensionMath.DeckNotchesFor(0, 0, false) == 0, "the shared height rule: equal banks, sunken only when allowed");
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
                int baseRule = open.IndexOf("base.PawnCanOpen(p)");
                Assert(baseRule >= 0 && baseRule < open.IndexOf("GateOpensFor("), "the door's own faction rules first, then the bridge's mode");
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
                Assert(DrawbridgeArtPaths.Dir == "Things/Building/FlowWorks/Drawbridge/" && a.Contains("DrawbridgeArtPaths.LeafUp("),
                    "the design doc's contract paths");
                Assert(a.Contains("ContentFinder<Texture2D>.Get(p, false)") && !a.Contains("Get(p, true)"), "can-fail: looked up silently (no red error before install)");
                Assert(a.Contains("\"Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionDeck_\" + Material(t)"), "a stand-in that exists on disk");
                Assert(Body(a, "public static LeafView ViewFor(Rot4 spanFromHinge)").Contains("spanFromHinge == Rot4.North ? LeafView.Face : spanFromHinge == Rot4.South ? LeafView.Underside : LeafView.Edge"),
                    "north face, south underside, east/west edge (contract)");
                string xml = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")), "..", "Defs", "Pits", "ThingDefs", "RM_Drawbridge.xml"));
                // every Drawbridge/ texPath a def names is installed: selftest_flowworks_drawbridge_art.py (this staging has no Textures/)
                Assert(!xml.Contains("MinifiedThing") && !xml.Contains("<defName>RM_DrawbridgePlanks"), "the art planks are never an item (answer 1)");
            });

            Case("Drawbridge_Looks_paths_look_first_then_material", () =>
            {
                foreach (SuspensionTier t in new[] { SuspensionTier.Timber, SuspensionTier.Steel })
                {
                    string m = t == SuspensionTier.Steel ? "Steel" : "Timber";
                    foreach (string look in DrawbridgeArtPaths.Looks)
                    {
                        string[] leaf = DrawbridgeArtPaths.LeafUp(t, look, "Face");
                        // DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK (owner by card 2026-10-22, "Material picks win"): material first, look second
                        Assert(leaf.Length == 2 && leaf[0] == DrawbridgeArtPaths.Dir + "RM_DrawbridgeLeafUp_" + m + "_Face"
                            && leaf[1] == DrawbridgeArtPaths.Dir + "RM_DrawbridgeLeafUp_Face_" + look, "can-fail: leaf material first, then look: " + string.Join(",", leaf));
                        Assert(DrawbridgeArtPaths.Planks(t, look)[0] == DrawbridgeArtPaths.Dir + "RM_DrawbridgePlanks_" + m
                            && DrawbridgeArtPaths.Planks(t, look)[1] == DrawbridgeArtPaths.Dir + "RM_DrawbridgePlanks_" + look, "can-fail: planks material first, then look");
                        Assert(DrawbridgeArtPaths.Winch(t, look)[0] == DrawbridgeArtPaths.Dir + "RM_DrawbridgeWinch_" + m
                            && DrawbridgeArtPaths.Winch(t, look)[1] == DrawbridgeArtPaths.Dir + "RM_DrawbridgeWinch_" + m + "_" + look,
                            "can-fail: winch material first; a look's winch keeps its material (the drive differs)");
                        Assert(DrawbridgeArtPaths.Gate(t, look, false)[0] == DrawbridgeArtPaths.Dir + "RM_DrawbridgeGate_" + m + "_Closed"
                            && DrawbridgeArtPaths.Gate(t, look, false)[1] == DrawbridgeArtPaths.Dir + "RM_DrawbridgeGate_Closed_" + look
                            && DrawbridgeArtPaths.Gate(t, look, true)[0] == DrawbridgeArtPaths.Dir + "RM_DrawbridgeGate_" + m + "_Open", "can-fail: gate material then look");
                    }
                    Assert(DrawbridgeArtPaths.LeafUp(t, null, "Edge").Length == 1, "no looks loaded: the material's picture only");
                }
                Assert(DrawbridgeArtPaths.GateFacing(false) == "_south" && DrawbridgeArtPaths.GateFacing(true) == "_east",
                    "a door turned North (east-west wall) shows its face (north reuses south); turned East, its edge");
            });

            Case("Drawbridge_Looks_raid_plank_pieces", () =>
            {
                // record: lip 0, planks 1..length-2, far bank length-1
                Assert(DrawbridgeArtPaths.PieceAt(0, 6) == DrawbridgeArtPaths.RaidPlankPiece.None && DrawbridgeArtPaths.PieceAt(5, 6) == DrawbridgeArtPaths.RaidPlankPiece.None,
                    "can-fail: the banks draw nothing");
                Assert(DrawbridgeArtPaths.PieceAt(1, 6) == DrawbridgeArtPaths.RaidPlankPiece.EndNear && DrawbridgeArtPaths.PieceAt(4, 6) == DrawbridgeArtPaths.RaidPlankPiece.EndFar,
                    "an end piece on each bank end");
                Assert(DrawbridgeArtPaths.PieceAt(2, 6) == DrawbridgeArtPaths.RaidPlankPiece.Mid && DrawbridgeArtPaths.PieceAt(3, 6) == DrawbridgeArtPaths.RaidPlankPiece.Mid, "mid pieces between");
                Assert(DrawbridgeArtPaths.PieceAt(1, 3) == DrawbridgeArtPaths.RaidPlankPiece.EndNear, "a one-square plank hooks the lip");
                Assert(DrawbridgeArtPaths.TopTowardLip(DrawbridgeArtPaths.RaidPlankPiece.EndNear) && !DrawbridgeArtPaths.TopTowardLip(DrawbridgeArtPaths.RaidPlankPiece.EndFar),
                    "can-fail: each end's hooks point at its own bank");
            });

            Case("Drawbridge_Looks_wired_at_the_draw_sites", () =>
            {
                string a = Src("Pits", "Drawbridge", "RM_DrawbridgeArt.cs");
                Assert(Body(a, "public static void DrawLeafUp(").Contains("LeafUp(r.tier, LookOf(r), ViewFor(spanFromHinge), out string path)"), "can-fail: the raised leaf reads its bridge's look");
                Assert(Body(a, "public static void DrawPlanks(").Contains("Planks(r.tier, LookOf(r))"), "the planks read the look");
                Assert(Body(a, "public static string LookOf(").Contains("r.look"), "the look is the bridge's own");
                string c = Src("Pits", "Drawbridge", "RM_DrawbridgeControl.cs");
                Assert(c.Contains("lookGraphic = RM_DrawbridgeArt.Winch(Tier, look) ?? base.Graphic;"), "can-fail: the winch house draws its look");
                string gate = Body(c, "public class Building_DrawbridgeGate : Building_Door");
                Assert(gate.Contains("RM_DrawbridgeArt.DrawGate(this, drawLoc, artTier, artLook, OpenPct >= 0.5f)") && gate.Contains("base.DrawAt(drawLoc, flip);"),
                    "can-fail: the gate draws its art, the vanilla door only where none exists");
                string d = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                string print = Body(d, "public override void Print(SectionLayer layer)");
                Assert(print.IndexOf("RM_DrawbridgeArt.PrintRaidPlank(layer, this, Record)") > 0
                    && print.IndexOf("RM_DrawbridgeArt.PrintRaidPlank(layer, this, Record)") < print.IndexOf("RM_SuspensionDeckLink.Print"),
                    "can-fail: a laid raid plank draws its own pieces, not the deck atlas");
                Assert(Body(a, "public static bool PrintRaidPlank(").Contains("r.raidPlank"), "only a raid plank record");
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

            Case("Drawbridge_raised_leaf_draws_without_its_winch", () =>
            {
                // TIMBER_LEAF_DIAGNOSE_UP_AND_INVISIBLE: a raised leaf with no winch house drew nothing (drawn from the winch's DrawAt)
                string c = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                string upd = Body(c, "public override void MapComponentUpdate()");
                Assert(upd.Contains("RM_DrawbridgeArt.DrawLeaves(map, bridges);"), "can-fail: the bridges' map component draws every leaf");
                Assert(upd.IndexOf("RM_DrawbridgeArt.DrawLeaves(map, bridges);") < upd.IndexOf("if (floorBand.Count == 0)"),
                    "can-fail: leaves draw even with nobody under a deck");
                string a = Src("Pits", "Drawbridge", "RM_DrawbridgeArt.cs");
                string leaves = Body(a, "public static void DrawLeaves(Map map, IReadOnlyList<SuspensionBridgeRecord> bridges)");
                Assert(leaves.IndexOf("DrawLeafUp(map, r, l);") >= 0 && leaves.IndexOf("DrawLeafUp(map, r, l);") < leaves.IndexOf("if (l.winch != null"),
                    "can-fail: the raised leaf is not gated on a winch");
                string w = Body(Src("Pits", "Drawbridge", "RM_DrawbridgeControl.cs"), "protected override void DrawAt(Vector3 drawLoc, bool flip = false)");
                Assert(!w.Contains("DrawLeafUp") && !w.Contains("DrawPlanks"), "can-fail: the winch must not draw the leaf a second time");
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

            DrawbridgeCableChecks.Run(Case);   // DRAWBRIDGE_CABLES_FIX_STOP_SHORT
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

    /// <summary>
    /// DRAWBRIDGE_CABLES_FIX_STOP_SHORT (owner 2026-10-23: "bridges have gaps in their support cables"; raised: "Ropes should
    /// now be slack and disconnected"). The anchors' rope geometry (RM_DrawbridgeCableMath) graded against the art's own
    /// attachment points, measured from the PNGs' alpha by art_source/Drawbridge/measure_cable_art.py into
    /// anchor_cable_art.json (selftest_flowworks_drawbridge_art.py proves that fixture is current). The expected world
    /// positions below are derived here from the fixture's picture frame, not from the math under test.
    /// </summary>
    internal static class DrawbridgeCableChecks
    {
        private const double Px = 1.0 / 256.0;

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        internal sealed class Measured
        {
            public double Lateral, Thick, Attach, End;
        }

        internal static Dictionary<string, List<Measured>> Anchors(out Dictionary<string, double[]> leafBody)
        {
            string src = RiverSwitchFlipChecks.SrcPath("RM_DrawbridgeMath.cs");
            string path = Path.Combine(Path.GetDirectoryName(src), "..", "art_source", "Drawbridge", "anchor_cable_art.json");
            Assert(File.Exists(path), "fixture missing: " + path + " (run art_source/Drawbridge/measure_cable_art.py)");
            using var doc = System.Text.Json.JsonDocument.Parse(File.ReadAllText(path));
            var res = new Dictionary<string, List<Measured>>();
            foreach (var kv in doc.RootElement.GetProperty("anchors").EnumerateObject())
            {
                var l = new List<Measured>();
                foreach (var r in kv.Value.EnumerateArray())
                {
                    l.Add(new Measured
                    {
                        Lateral = r.GetProperty("lateral").GetDouble(),
                        Thick = r.GetProperty("thick").GetDouble(),
                        Attach = r.GetProperty("attach").GetDouble(),
                        End = r.GetProperty("end").GetDouble(),
                    });
                }
                res[kv.Name] = l;
            }
            leafBody = new Dictionary<string, double[]>();
            foreach (var kv in doc.RootElement.GetProperty("leafEdges").EnumerateObject())
            {
                var b = kv.Value.GetProperty("body");
                leafBody[kv.Name] = new[] { b[0].GetDouble(), b[1].GetDouble(), kv.Value.GetProperty("eyeTop").GetDouble() };
            }
            return res;
        }

        /// <summary>A print setup per rotation, as Graphic.Print prints the anchor: a styled (Graphic_Multi) picture is printed
        /// unturned from its facing file, west = the east file mirrored; the unstyled single is turned to the rotation.</summary>
        internal static IEnumerable<(string rotName, string facing, bool flip, double angle, int fx, int fz)> Setups(bool styled)
        {
            if (styled)
            {
                yield return ("N", "north", false, 0, 0, 1);
                yield return ("E", "east", false, 0, 1, 0);
                yield return ("S", "south", false, 0, 0, -1);
                yield return ("W", "east", true, 0, -1, 0);
            }
            else
            {
                yield return ("N", "single", false, 0, 0, 1);
                yield return ("E", "single", false, 90, 1, 0);
                yield return ("S", "single", false, 180, 0, -1);
                yield return ("W", "single", false, 270, -1, 0);
            }
        }

        /// <summary>Where the picture's own frame puts (along, lateral) in the world, derived from the fixture's frame: along
        /// runs toward the deck (f), +lateral is left of f, mirrored when the print mirrors.</summary>
        internal static (double X, double Z) Expected(int fx, int fz, bool flip, double a, double l)
        {
            double lx = -fz, lz = fx;   // left of f
            if (flip)
            {
                lx = -lx;
                lz = -lz;
            }
            return ((a - 0.5) * fx + l * lx, (a - 0.5) * fz + l * lz);
        }

        private static double Dist((double X, double Z) p, (double X, double Z) q) => Math.Sqrt((p.X - q.X) * (p.X - q.X) + (p.Z - q.Z) * (p.Z - q.Z));

        /// <summary>The whole grade for one table against the measured art; returns the failures (empty = pass). The can-fail
        /// cases feed it a perturbed table.</summary>
        internal static List<string> Grade(Dictionary<string, RM_DrawbridgeCableMath.RopeArt[]> table, Dictionary<string, List<Measured>> measured)
        {
            var bad = new List<string>();
            foreach (var kv in measured)
            {
                string[] parts = kv.Key.Split('/');
                bool styled = parts[parts.Length - 1] != "single";   // base anchors are upright per-facing bollards too
                string key = table.ContainsKey(kv.Key) ? kv.Key : parts[0] + "/" + parts[1];   // per-facing entry first (upright bollards)
                if (!table.TryGetValue(key, out RM_DrawbridgeCableMath.RopeArt[] ropes) || ropes.Length != kv.Value.Count)
                {
                    bad.Add(kv.Key + ": no rope table");
                    continue;
                }
                foreach (Measured m in kv.Value)
                {
                    RM_DrawbridgeCableMath.RopeArt r = ropes[0];
                    foreach (var c in ropes) if (Math.Abs(c.Lateral - m.Lateral) < Math.Abs(r.Lateral - m.Lateral)) r = c;
                    if (Math.Abs(r.Lateral - m.Lateral) > 1.5 * Px || Math.Abs(r.Attach - m.Attach) > 1.5 * Px || Math.Abs(r.End - m.End) > 1.0 * Px)
                    {
                        bad.Add($"{kv.Key}: table rope (lat {r.Lateral:F4}, attach {r.Attach:F4}, end {r.End:F4}) != art (lat {m.Lateral:F4}, attach {m.Attach:F4}, end {m.End:F4})");
                        continue;
                    }
                    foreach (var su in Setups(styled))
                    {
                        if (styled && su.facing != parts[2]) continue;   // each facing file grades the rotations printed from it
                        string where = kv.Key + " rot " + su.rotName;
                        // LOWERED: painted run + drawn run cover the art's attachment point to past the deck edge, gapless, on the rope's line
                        List<RM_DrawbridgeCableMath.Piece> taut = RM_DrawbridgeCableMath.Taut(r);
                        taut.Sort((x, y) => Math.Min(x.A0, x.A1).CompareTo(Math.Min(y.A0, y.A1)));
                        (double X, double Z) startW = RM_DrawbridgeCableMath.ToWorld(su.facing, su.flip, su.angle, taut[0].A0, taut[0].L0);
                        (double X, double Z) startE = Expected(su.fx, su.fz, su.flip, m.Attach, m.Lateral);
                        if (Dist(startW, startE) > 1.5 * Px) bad.Add(where + $": lowered rope starts {Dist(startW, startE) / Px:F1}px from the bollard's attachment point");
                        double reach = Math.Min(taut[0].A0, taut[0].A1);
                        bool painted = false, drawn = false;
                        foreach (var pc in taut)
                        {
                            double a0 = Math.Min(pc.A0, pc.A1), a1 = Math.Max(pc.A0, pc.A1);
                            if (a0 > reach + 0.25 * Px) bad.Add(where + $": gap in the lowered rope at along {reach:F3}..{a0:F3}");
                            reach = Math.Max(reach, a1);
                            if (Math.Abs(pc.L0 - m.Lateral) > 1.5 * Px || Math.Abs(pc.L1 - m.Lateral) > 1.5 * Px) bad.Add(where + ": a lowered rope piece leaves the rope's line");
                            if (pc.Painted)
                            {
                                painted = true;
                                if (Math.Abs(a1 - m.End) > 1.0 * Px) bad.Add(where + ": the painted run is not the art's painted run");
                            }
                            else drawn = true;
                        }
                        (double X, double Z) endW = RM_DrawbridgeCableMath.ToWorld(su.facing, su.flip, su.angle, reach, m.Lateral);
                        double endAlong = endW.X * su.fx + endW.Z * su.fz;
                        if (endAlong < 0.5 - 1e-6) bad.Add(where + $": the lowered rope stops {(0.5 - endAlong) / Px:F1}px short of the deck edge");
                        if (endAlong > 0.5 + 0.08) bad.Add(where + ": the lowered rope runs too far onto the deck");
                        if (!painted || (m.End < 1.0 - 0.5 * Px && !drawn)) bad.Add(where + ": the art stops short and nothing is drawn on");
                        // RAISED: slack, from the attachment point, never over the pit, sagging, the two loops apart
                        double foot = RM_DrawbridgeCableMath.SlackFoot(parts[0] + "/" + parts[1], su.facing);
                        List<(double A, double L)> sl = RM_DrawbridgeCableMath.Slack(r, su.fz != 0, foot);
                        string flat = FlatOnGround(sl, su.facing, su.flip, su.angle);
                        if (flat != null) bad.Add(where + ": " + flat);
                        string grounded = AtFoot(sl, foot);
                        if (grounded != null) bad.Add(where + ": " + grounded);
                        double toDeck = sl[sl.Count - 1].A - sl[sl.Count - 3].A;   // the loose end: from the coil's last turn out
                        if (toDeck > 0.01) bad.Add(where + $": the coil's loose end points toward the deck (+{toDeck:F3} along): reads as still tied on");
                        (double X, double Z) s0 = RM_DrawbridgeCableMath.ToWorld(su.facing, su.flip, su.angle, sl[0].A, sl[0].L);
                        if (Dist(s0, startE) > 1.5 * Px) bad.Add(where + ": the slack rope does not start at the bollard's attachment point");
                        double sag = 0, maxAlong = -1;
                        foreach (var pt in sl)
                        {
                            (double X, double Z) w = RM_DrawbridgeCableMath.ToWorld(su.facing, su.flip, su.angle, pt.A, pt.L);
                            double along = w.X * su.fx + w.Z * su.fz;
                            maxAlong = Math.Max(maxAlong, along);
                            (double X, double Z) onLine = Expected(su.fx, su.fz, su.flip, pt.A, m.Lateral);
                            sag = Math.Max(sag, Dist(w, onLine));
                            if (Math.Abs(w.X) > 0.5 || Math.Abs(w.Z) > 0.5) bad.Add(where + ": the slack rope leaves its own square");
                        }
                        if (maxAlong > 0.5 - 0.05) bad.Add(where + $": the slack rope reaches {maxAlong:F3} toward the pit (must stay on the bank)");
                        if (sag < 0.08) bad.Add(where + $": the raised rope is not slack (sag {sag:F3})");
                    }
                }
                // the two slack loops never touch, in either screen orientation
                foreach (bool vertical in new[] { true, false })
                {
                    double foot = vertical && parts.Length == 3 ? RM_DrawbridgeCableMath.SlackFoot(parts[0] + "/" + parts[1], parts[2]) : -1;
                    List<(double A, double L)> p0 = RM_DrawbridgeCableMath.Slack(ropes[0], vertical, foot), p1 = RM_DrawbridgeCableMath.Slack(ropes[1], vertical, foot);
                    double gap = 9;
                    foreach (var a in p0) foreach (var b in p1) gap = Math.Min(gap, Math.Sqrt((a.A - b.A) * (a.A - b.A) + (a.L - b.L) * (a.L - b.L)));
                    if (gap < Math.Max(ropes[0].Thick, ropes[1].Thick) * 1.2) bad.Add(kv.Key + $": the two slack loops touch (gap {gap:F3}, vertical {vertical})");
                }
            }
            return bad;
        }

        /// <summary>SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE (art brief C6, the true perspective plane): a rope lying on the ground
        /// is seen as a squashed ring, wider across the screen than up it. A loop whose screen-vertical extent passes 0.7 of its
        /// horizontal one reads as a hook standing up off the bollard. Null = flat.</summary>
        internal static string FlatOnGround(List<(double A, double L)> rope, string facing, bool flip, double angle)
        {
            double x0 = 9, x1 = -9, z0 = 9, z1 = -9;
            foreach (var pt in rope.Skip(1))   // the coil itself: point 0 is the attachment the rope drops from
            {
                (double X, double Z) w = RM_DrawbridgeCableMath.ToWorld(facing, flip, angle, pt.A, pt.L);
                x0 = Math.Min(x0, w.X); x1 = Math.Max(x1, w.X); z0 = Math.Min(z0, w.Z); z1 = Math.Max(z1, w.Z);
            }
            double wide = x1 - x0, tall = z1 - z0;
            if (wide < 0.15) return $"the slack coil is only {wide:F3} wide on screen (a dangling strand, not a coil)";
            return tall > 0.7 * wide ? $"the slack coil stands up: {tall:F3} tall on screen vs {wide:F3} wide (a ground coil is squashed, <= 0.7)" : null;
        }

        /// <summary>An upright post with the deck up the screen (foot >= 0): its head is drawn above its foot, so a coil that
        /// does not reach down to the foot floats at head height like a halo (art-eval run slack_coil_20261023, GPT K1/K2), and
        /// one reaching behind the foot draws its far arc over the post (run _r2, LAYER_ORDER). The coil's far edge must sit at
        /// the foot (±0.03). Null = on the ground in front of the post (or no foot rule for this print).</summary>
        internal static string AtFoot(List<(double A, double L)> rope, double foot)
        {
            if (foot < 0) return null;
            double a0 = 9, a1 = -9;
            foreach (var pt in rope.Skip(1)) { a0 = Math.Min(a0, pt.A); a1 = Math.Max(a1, pt.A); }
            if (a0 > foot) return $"the slack coil (along {a0:F3}..{a1:F3}) floats off the post's foot ({foot:F3}): a halo at head height, not rope on the ground";
            if (a1 > foot + 0.03) return $"the slack coil (along {a0:F3}..{a1:F3}) reaches behind the post's foot ({foot:F3}): its far arc would be drawn over the post";
            if (a1 < foot - 0.03) return $"the slack coil (along {a0:F3}..{a1:F3}) stops short of the post's foot ({foot:F3}): the rope never reaches the ground";
            return null;
        }

        /// <summary>The shipped raised loop before SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE: a narrow U along the rope, the same in
        /// every rotation (copied, so the can-fail case keeps it after the code moved on).</summary>
        internal static List<(double A, double L)> OldSlack(RM_DrawbridgeCableMath.RopeArt r, int n = 14)
        {
            double s = r.Lateral >= 0 ? 1.0 : -1.0, reach = 0.9;
            double f = Math.Min(1.0, 0.8 * Math.Abs(r.Lateral) / 0.17);
            double[] A = { r.Attach, reach, reach, r.Attach + 0.3 * (reach - r.Attach) };
            double[] L = { r.Lateral, r.Lateral + 0.05 * s * f, r.Lateral - 0.13 * s * f, r.Lateral - 0.17 * s * f };
            var pts = new List<(double A, double L)>();
            for (int i = 0; i <= n; i++)
            {
                double t = (double)i / n, u = 1 - t;
                double b0 = u * u * u, b1 = 3 * u * u * t, b2 = 3 * u * t * t, b3 = t * t * t;
                pts.Add((b0 * A[0] + b1 * A[1] + b2 * A[2] + b3 * A[3], b0 * L[0] + b1 * L[1] + b2 * L[2] + b3 * L[3]));
            }
            return pts;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Drawbridge_Cables_slack_coil_lies_flat_canfail_old_hook", () =>
            {
                int oldStood = 0, wrongStood = 0, setups = 0;
                foreach (var kv in RM_DrawbridgeCableMath.Art)
                {
                    bool styled = !kv.Key.EndsWith("/single");
                    string facingFile = kv.Key.Split('/').Length == 3 ? kv.Key.Split('/')[2] : null;
                    foreach (var su in Setups(styled))
                    {
                        if (facingFile != null && su.facing != facingFile) continue;
                        if (styled && facingFile == null && su.facing != "east") continue;   // shared Heavy table: graded once per print
                        bool vertical = su.fz != 0;
                        foreach (var r in kv.Value)
                        {
                            setups++;
                            string baseKey = kv.Key.Split('/').Length == 3 ? kv.Key.Substring(0, kv.Key.LastIndexOf('/')) : kv.Key;
                            string now = FlatOnGround(RM_DrawbridgeCableMath.Slack(r, vertical, RM_DrawbridgeCableMath.SlackFoot(baseKey, su.facing)), su.facing, su.flip, su.angle);
                            Assert(now == null, kv.Key + " rot " + su.rotName + ": " + now);
                            if (vertical && FlatOnGround(OldSlack(r), su.facing, su.flip, su.angle) != null) oldStood++;
                            if (vertical && FlatOnGround(RM_DrawbridgeCableMath.Slack(r, false), su.facing, su.flip, su.angle) != null) wrongStood++;
                        }
                    }
                }
                Assert(setups >= 80, "graded only " + setups + " rope prints");
                Assert(oldStood > 0, "can-fail: the shipped N/S hook loop must read as standing up");
                // the halo: a coil ahead of the head (no foot rule) on an upright _north print floats off the foot
                int halo = 0, ring = 0, north = 0;
                foreach (var kv in RM_DrawbridgeCableMath.Art)
                {
                    if (!kv.Key.EndsWith("/north")) continue;
                    double foot = RM_DrawbridgeCableMath.SlackFoot(kv.Key.Substring(0, kv.Key.Length - 6), "north");
                    Assert(foot >= 0, kv.Key + ": an upright _north print has no foot rule");
                    foreach (var r in kv.Value)
                    {
                        north++;
                        Assert(AtFoot(RM_DrawbridgeCableMath.Slack(r, true, foot), foot) == null, kv.Key + ": " + AtFoot(RM_DrawbridgeCableMath.Slack(r, true, foot), foot));
                        if (AtFoot(RM_DrawbridgeCableMath.Slack(r, true), foot) != null) halo++;
                        // the r2 ring centred ON the foot (its far arc over the post base): centre = (foot + ra) - ra
                        if (AtFoot(RM_DrawbridgeCableMath.Slack(r, true, foot + RM_DrawbridgeCableMath.CoilAspect * RM_DrawbridgeCableMath.CoilWide), foot) != null) ring++;
                    }
                }
                Assert(north >= 16, "graded only " + north + " upright _north ropes");
                Assert(halo == north, $"can-fail: every coil placed ahead of a _north head must float off the foot ({halo}/{north})");
                Assert(ring == north, $"can-fail: every coil ringed round a _north foot must reach behind the post ({ring}/{north})");
                Assert(RM_DrawbridgeCableMath.SlackFoot("Scrapper/Heavy", "east") < 0 && RM_DrawbridgeCableMath.SlackFoot("base/Rope", "single") < 0
                    && RM_DrawbridgeCableMath.SlackFoot("Scrapper/Timber", "east") < 0, "the foot rule is for upright _north prints only");
                Assert(wrongStood > 0, "can-fail: an E/W-shaped coil printed in N/S must read as standing up");
            });

            Case("Drawbridge_BaseAnchors_upright_multi_per_facing", () =>
            {
                // ANCHOR_BASE_REDRAW_STILL_LYING_FLAT: the unstyled anchors are upright bollards (per-facing files, per-facing rope table)
                string root = Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_DrawbridgeMath.cs")), "..");
                string xml = File.ReadAllText(Path.Combine(root, "Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml"));
                var measured = Anchors(out _);
                foreach (string m in new[] { "Rope", "Timber", "Steel", "Heavy" })
                {
                    var d = System.Text.RegularExpressions.Regex.Match(xml, "<defName>RM_SuspensionAnchor_" + m + "</defName>.*?<graphicClass>(\\w+)</graphicClass>", System.Text.RegularExpressions.RegexOptions.Singleline);
                    Assert(d.Success && d.Groups[1].Value == "Graphic_Multi", "RM_SuspensionAnchor_" + m + " is " + (d.Success ? d.Groups[1].Value : "missing") + ", an upright bollard needs Graphic_Multi");
                    foreach (string f in new[] { "south", "east", "north" })
                    {
                        Assert(measured.ContainsKey("base/" + m + "/" + f), m + " " + f + " picture not in the measured fixture (anchor_cable_art.json)");
                        Assert(RM_DrawbridgeCableMath.Art.ContainsKey("base/" + m + "/" + f), "no rope table base/" + m + "/" + f);
                    }
                    Assert(RM_DrawbridgeCableMath.KeyOf("Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionAnchor_" + m, true) == "base/" + m, "KeyOf must key the upright base " + m + " as base/" + m);
                }
            });

            Case("Drawbridge_StyledHeavyAnchors_upright_per_facing", () =>
            {
                // ANCHOR_BASE_REDRAW_STILL_LYING_FLAT A2: the styled Heavy anchors stand upright like the styled Timber/Steel ones,
                // so their rope attachment is per facing (look/Heavy/facing), not the one shared flat-fixture row
                foreach (string look in new[] { "Scrapper", "Industrial", "Modern", "Futuristic" })
                {
                    foreach (string f in new[] { "south", "east", "north" })
                        Assert(RM_DrawbridgeCableMath.Art.ContainsKey(look + "/Heavy/" + f), "no per-facing rope table " + look + "/Heavy/" + f + ": the styled Heavy anchor is still the flat fixture");
                    Assert(!RM_DrawbridgeCableMath.Art.ContainsKey(look + "/Heavy"), look + "/Heavy still has the shared flat-fixture row");
                }
            });

            Case("Drawbridge_Cables_lowered_reach_deck_raised_slack_vs_art", () =>
            {
                var measured = Anchors(out _);
                Assert(measured.Count >= 48, "the fixture measured " + measured.Count + " anchor pictures (expected 48: 4 looks x 3 materials x 3 facings + 4 base x 3 facings)");
                List<string> bad = RM_DrawbridgeCableMath.Art.Count > 0 ? Grade(RM_DrawbridgeCableMath.Art, measured) : new List<string> { "empty table" };
                Assert(bad.Count == 0, bad.Count + " cable failures, first: " + string.Join(" | ", bad.GetRange(0, Math.Min(4, bad.Count))));
            });

            Case("Drawbridge_Cables_canfail_old_stop_short_and_moved_attach", () =>
            {
                var measured = Anchors(out _);
                // the shipped bug: the rope only as painted (no drawn run), reproduced by a table claiming the art reaches the edge
                var shortTable = new Dictionary<string, RM_DrawbridgeCableMath.RopeArt[]>();
                var movedTable = new Dictionary<string, RM_DrawbridgeCableMath.RopeArt[]>();
                foreach (var kv in RM_DrawbridgeCableMath.Art)
                {
                    shortTable[kv.Key] = Array.ConvertAll(kv.Value, r => new RM_DrawbridgeCableMath.RopeArt(r.Lateral, r.Thick, r.Attach, 1.0 + RM_DrawbridgeCableMath.DeckOverlap));
                    movedTable[kv.Key] = Array.ConvertAll(kv.Value, r => new RM_DrawbridgeCableMath.RopeArt(r.Lateral, r.Thick, r.Attach + 3 * Px, r.End));
                }
                Assert(Grade(shortTable, measured).Count > 0, "can-fail: a table that ignores the art's painted end must fail");
                Assert(Grade(movedTable, measured).Count > 0, "can-fail: an attachment point 3px off the art must fail");
            });

            Case("Drawbridge_Cables_raised_leaf_edge_crops_the_stiff_rope", () =>
            {
                Anchors(out Dictionary<string, double[]> body);
                Assert(body.Count == 6, "six edge pictures measured, got " + body.Count);
                foreach (var kv in body)
                {
                    Assert(RM_DrawbridgeCableMath.LeafEdgeBody.TryGetValue(kv.Key, out double[] crop), kv.Key + ": no crop, the painted rope stub draws");
                    Assert(crop.Length == 3 && Math.Abs(crop[0] - kv.Value[0]) <= 1.5 * Px && Math.Abs(crop[1] - kv.Value[1]) <= 1.5 * Px,
                        kv.Key + ": crop " + crop[0] + ".." + crop[1] + " is not the leaf body " + kv.Value[0] + ".." + kv.Value[1]);
                    Assert(Math.Abs(crop[2] - kv.Value[2]) <= 2.0 / 1024.0, kv.Key + ": the top cut " + crop[2] + " is not the hook eye's top " + kv.Value[2]
                        + " (above it the stiff rope stub draws)");
                }
            });

            Case("Drawbridge_Cables_ropes_for_unmeasured_print_is_null_not_throw", () =>
            {
                // DRAWBRIDGE_ROPES_FIX_DEAD_SINGLE_FACING: every rope table is per facing since the anchors stand upright; a print
                // with no measured table (a rotated single, an unknown key) gets null and prints as before, never KeyNotFound
                RM_DrawbridgeCableMath.RopeArt[] single = null, unknown = null;
                string threw = null;
                try
                {
                    single = RM_DrawbridgeCableMath.RopesFor("base/Steel", "single");
                    unknown = RM_DrawbridgeCableMath.RopesFor("NoLook/NoMat", "east");
                }
                catch (Exception e)
                {
                    threw = e.GetType().Name;
                }
                Assert(threw == null, "can-fail: RopesFor threw " + threw + " for a print with no per-facing table");
                Assert(single == null && unknown == null, "an unmeasured print must get no rope table");
                Assert(RM_DrawbridgeCableMath.RopesFor("base/Steel", "north") == RM_DrawbridgeCableMath.Art["base/Steel/north"], "a measured facing still finds its table");
                foreach (string k in RM_DrawbridgeCableMath.Art.Keys)
                    Assert(k.Split('/').Length == 3, "rope table " + k + " is not per facing (look/material/facing)");
                string art = RiverSwitchFlipChecks.Src(Path.Combine("Pits", "Drawbridge", "RM_DrawbridgeArt.cs"));
                Assert(art.Contains("if (p.ropes == null)"), "AnchorPrintFor prints as before when the print has no rope table");
            });

            Case("Drawbridge_Cables_call_sites", () =>
            {
                string deck = RiverSwitchFlipChecks.Src(Path.Combine("Pits", "Suspension", "Building_SuspensionDeck.cs"));
                string art = RiverSwitchFlipChecks.Src(Path.Combine("Pits", "Drawbridge", "RM_DrawbridgeArt.cs"));
                Assert(deck.Contains("RM_DrawbridgeArt.AnchorPrintFor(this)") && deck.Contains("RM_DrawbridgeArt.PrintBollards(layer, p)")
                    && deck.Contains("RM_DrawbridgeArt.PrintRopes(layer, p)"), "the anchor prints its ropes through the cable math");
                Assert(art.Contains("Mesh mesh = LeafMesh(path, spanFromHinge == Rot4.West);"), "the raised leaf draws through the stub crop");
                Assert(art.Contains("slack = deck.leafRaised"), "raised = the deck square the ropes face is a raised leaf");
            });
        }
    }
}
