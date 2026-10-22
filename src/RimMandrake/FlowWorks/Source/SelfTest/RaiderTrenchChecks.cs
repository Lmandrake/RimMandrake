// RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP (owner 2026-10-18, card Q7: "Go around, and breach if no way"; his words: "(4) plus
// some may have jump packs to cross. Ladders make sense for shallower pits (they could start building them in preparation).
// Siege raids still work fine with mortars."). Offline: the decision order (RM_RaiderTrenchMath.Choose), the crossing line, the
// least-fill causeway, the ladder slots, the work times, the jump-pack share, and the production wiring (duty patch, the own-
// ladder exemption in the prison-door rule and the closed-ladder grid, settings). Each case has a can-fail.
// NOT proven here (live rows owed, after P2's raid result): a raid against a sheer-trench island stalls no longer; a raider
// sets a ladder down and up and the raid walks in; a 4 m trench is breached by fill; a jump-pack raider lands across on its
// feet; a siege still only shells; shooting the ladder strands the raiders below.
using System;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class RaiderTrenchChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string ModRoot => Path.GetFullPath(Path.Combine(
            Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RimMandrakeFlowWorksMod.cs")), ".."));

        private static RM_RaiderTrenchMath.Crossing C(bool master = true, bool eligible = true, bool siege = false,
            bool reach = false, bool jumpOn = true, bool jumpReady = false, bool tool = true, bool laddersOn = true,
            bool ladderOk = false, bool fillOn = true, bool fillOk = false)
        {
            return RM_RaiderTrenchMath.Choose(master, eligible, siege, reach, jumpOn, jumpReady, tool, laddersOn, ladderOk, fillOn, fillOk);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("RaiderTrench_decision_order", () =>
            {
                var X = RM_RaiderTrenchMath.Crossing.None;
                Assert(C(reach: true, jumpReady: true, ladderOk: true, fillOk: true) == RM_RaiderTrenchMath.Crossing.GoAround,
                    "a reachable target: go around, whatever else they could do");
                Assert(C(jumpReady: true, ladderOk: true, fillOk: true) == RM_RaiderTrenchMath.Crossing.Jump, "jump first");
                Assert(C(ladderOk: true, fillOk: true) == RM_RaiderTrenchMath.Crossing.Ladder, "ladders before breaching");
                Assert(C(fillOk: true) == RM_RaiderTrenchMath.Crossing.Fill, "breach if no way");
                Assert(C(siege: true, jumpReady: true, ladderOk: true, fillOk: true) == X, "can-fail: a siege never crosses (mortars)");
                Assert(C(master: false, jumpReady: true) == X, "can-fail: the master switch off");
                Assert(C(eligible: false, jumpReady: true) == X, "can-fail: not a raider of a lord (or trapped)");
                Assert(C(jumpOn: false, jumpReady: true, ladderOk: true) == RM_RaiderTrenchMath.Crossing.Ladder, "jumps off: ladders");
                Assert(C(tool: false, ladderOk: true, fillOk: true) == X, "can-fail: an animal neither sets ladders nor shovels");
                Assert(C(tool: false, jumpReady: true) == RM_RaiderTrenchMath.Crossing.Jump, "a leaping animal still jumps");
                Assert(C(laddersOn: false, ladderOk: true, fillOk: true) == RM_RaiderTrenchMath.Crossing.Fill, "ladders off: fill");
                Assert(C(fillOn: false, fillOk: true) == X, "can-fail: everything off: they mill and leave, as before");
            });
            Case("RaiderTrench_cardinal_line", () =>
            {
                var l = RM_RaiderTrenchMath.CardinalLine(0, 0, 3, 2, 100);
                Assert(l[0] == (0, 0) && l[l.Count - 1] == (3, 2), "both ends included");
                for (int i = 1; i < l.Count; i++)
                {
                    int d = Math.Abs(l[i].x - l[i - 1].x) + Math.Abs(l[i].z - l[i - 1].z);
                    Assert(d == 1, "every step cardinal (the masks judge cardinal edges)");
                }
                Assert(l.Count == 6, "|dx| + |dz| + 1 squares: " + l.Count);
                Assert(RM_RaiderTrenchMath.CardinalLine(5, 5, 5, 1, 100).Count == 5, "a straight line");
                Assert(RM_RaiderTrenchMath.CardinalLine(0, 0, 50, 0, 10).Count == 10, "can-fail: capped at maxCells");
            });
            Case("RaiderTrench_fill_causeway", () =>
            {
                // A sheer 2 m trench (4 levels) three squares wide, a person (k = 2).
                int[] d = { 0, 4, 4, 4, 0 };
                int[] t = RM_RaiderTrenchMath.FillTargets(d, 2);
                Assert(t[0] == 0 && t[1] == 2 && t[2] == 4 && t[3] == 2 && t[4] == 0, "slope down, floor kept, slope up: " + string.Join(",", t));
                Assert(RM_RaiderTrenchMath.FillLevels(d, t) == 4, "four levels shovelled, not twelve");
                Assert(RM_RaiderTrenchMath.StepsClimbable(t, 2), "every step climbable");
                Assert(!RM_RaiderTrenchMath.StepsClimbable(d, 2), "can-fail: the trench as dug is not");
                Assert(RM_RaiderTrenchMath.NextFill(d, t) == 1, "shovel the near square first");
                int[] d2 = { 0, 2, 4, 4, 0 };
                Assert(RM_RaiderTrenchMath.NextFill(d2, t) == 3, "then the far wall's square");
                Assert(RM_RaiderTrenchMath.NextFill(t, t) == -1, "done: the causeway stands");
                // A 4 m trench (8 levels), one square wide: fill only.
                int[] n = { 0, 8, 0 };
                int[] tn = RM_RaiderTrenchMath.FillTargets(n, 2);
                Assert(tn[1] == 2 && RM_RaiderTrenchMath.StepsClimbable(tn, 2), "a narrow deep slot is filled to 1 m");
                // An end deeper than its neighbour by more than k: fill only makes the neighbour shallower.
                int[] bad = { 6, 0, 0 };
                Assert(!RM_RaiderTrenchMath.StepsClimbable(RM_RaiderTrenchMath.FillTargets(bad, 2), 2),
                    "can-fail: fill never fixes a climb up out of the raider's own end");
                Assert(RM_RaiderTrenchMath.FillTargets(new[] { 0, 4, 0 }, 0)[1] == 1, "k 0 climbs as 1 (StepAllowed's max(1, k))");
            });
            Case("RaiderTrench_ladder_slots", () =>
            {
                int[] d = { 0, 4, 4, 4, 0 };
                var s = RM_RaiderTrenchMath.LadderSlots(d, 2, 6);
                Assert(s != null && s.Count == 2, "down the near wall, up the far one");
                Assert(s[0].cell == 1 && s[0].toward == 0 && s[0].drop == 4, "the near ladder stands in the trench, hung on the near lip");
                Assert(s[1].cell == 3 && s[1].toward == 4, "the far ladder hangs on the far lip");
                Assert(RM_RaiderTrenchMath.LadderSlots(new[] { 0, 8, 8, 0 }, 2, 6) == null, "can-fail: 4 m is past a 3 m ladder (shallower pits only)");
                Assert(RM_RaiderTrenchMath.LadderSlots(new[] { 0, 8, 8, 0 }, 2, 0) != null, "reach 0 = any depth");
                Assert(RM_RaiderTrenchMath.LadderSlots(new[] { 0, 4, 0 }, 2, 6) == null, "can-fail: a one-square slot would need two ladders in one square");
                Assert(RM_RaiderTrenchMath.LadderSlots(new[] { 0, 2, 4, 2, 0 }, 2, 6).Count == 0, "a climbable profile needs no ladder");
                var step = RM_RaiderTrenchMath.LadderSlots(new[] { 0, 1, 5, 5, 0 }, 2, 6);
                Assert(step != null && step.Count == 2 && step[0].cell == 2 && step[0].toward == 1, "a wall inside the line: ladder in the deeper square");
                Assert(RM_RaiderTrenchMath.LadderSlots(new[] { 4, 0, 0 }, 2, 6) == null, "can-fail: never a ladder on the raider's own end");
            });
            Case("RaiderTrench_times_and_jump_share", () =>
            {
                Assert(RM_RaiderTrenchMath.LadderTicks(0, 1f) == 600, "10 s");
                Assert(RM_RaiderTrenchMath.LadderTicks(2, 1f) == 720, "+1 s a metre");
                Assert(RM_RaiderTrenchMath.LadderTicks(2, 2f) == 360, "the speed setting halves it");
                Assert(RM_RaiderTrenchMath.LadderTicks(2, 0f) > 0, "can-fail: speed 0 never divides by zero");
                Assert(RM_RaiderTrenchMath.FillTicks(1700, 1f, 1f) == 1000, "vanilla's 1.7 work a tick");
                Assert(RM_RaiderTrenchMath.FillTicks(1700, 2f, 1f) == 500, "a better miner shovels faster");
                int got = 0;
                for (int id = 1; id <= 20000; id++)
                {
                    if (RM_RaiderTrenchMath.GetsJumpPack(id, 0.1f)) got++;
                }
                Assert(got > 1700 && got < 2300, "about 10% of raiders bring a jump pack: " + got);
                Assert(!RM_RaiderTrenchMath.GetsJumpPack(7, 0f), "can-fail: 0% gives none");
                Assert(RM_RaiderTrenchMath.GetsJumpPack(7, 1f), "100% gives all");
                int mono = 0;
                for (int id = 1; id <= 2000; id++)
                {
                    if (RM_RaiderTrenchMath.GetsJumpPack(id, 0.3f) && !RM_RaiderTrenchMath.GetsJumpPack(id, 0.6f)) mono++;
                }
                Assert(mono == 0, "a raider with a pack at a 30% share keeps it at 60% (a fixed draw per pawn, not a re-roll): " + mono);
                Assert(RM_RaiderTrenchMath.JumpLanding(0, 4, 4, i => i >= 1, i => i <= 2) == 1, "the nearest valid landing in range");
                Assert(RM_RaiderTrenchMath.JumpLanding(0, 4, 4, i => i >= 3, i => i <= 2) == -1, "can-fail: none in range");
            });
            Case("RaiderTrench_breach_fits_a_raid", () =>
            {
                // CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP (belt 2026-10-22): the proof's 4 m ring, two squares wide, a person (k = 2);
                // Mercenary_Gunner MiningSpeed 0.336; the raid stood at the lip from ~t+2,000 and left at ~t+28,000.
                int[] d = { 0, 8, 8, 0 };
                int[] t = RM_RaiderTrenchMath.FillTargets(d, 2);
                Assert(RM_RaiderTrenchMath.FillLevels(d, t) == 12, "the causeway is 12 levels: " + string.Join(",", t));
                int perLevel = RM_RaiderTrenchMath.FillTicks(RM_RaiderTrenchMath.FillWorkPerLevel, 0.336f, 1f);
                Assert(perLevel < 3000, "one level is a shovelling job, not a dig: " + perLevel);
                int raid = RM_RaiderTrenchMath.BreachTicks(d, t, perLevel, RM_RaiderTrenchMath.MaxFillersPerSquare);
                Assert(raid <= 15000, "the raid fills the causeway well inside its ~26,000 ticks at the lip: " + raid);
                // can-fail: the deep-dig curve per level (the old price) and one raider a square (the old reservation)
                int old = 0;
                for (int i = 1; i < d.Length - 1; i++)
                {
                    for (int lv = d[i]; lv > t[i]; lv--)
                    {
                        old += RM_RaiderTrenchMath.FillTicks(RM_DigDepthMath.WorkToCut(lv) / 2, 0.336f, 1f);
                    }
                }
                Assert(old > 26000, "can-fail: the old price could never finish inside a raid: " + old);
                Assert(RM_RaiderTrenchMath.BreachTicks(d, t, perLevel, 1) > raid, "can-fail: one raider a square is slower");
                Assert(RM_RaiderTrenchMath.FillWorkPerLevel == RM_DigDepthMath.WorkToCut(1) / 2, "a level of fill = half the first notch's cut, at every depth");
                // one crossing per raid, kept while it is worked
                Assert(RM_RaiderTrenchMath.LipTick(false, 0, 100, 2500, false, false) == 100, "no lip yet: remember this one");
                Assert(RM_RaiderTrenchMath.LipTick(true, 0, 100, 2500, false, false) == -1, "a live lip stands: a later raider's own lip is ignored");
                Assert(RM_RaiderTrenchMath.LipTick(true, 0, 2400, 2500, true, true) == 2400, "worked on: the lip is renewed");
                Assert(RM_RaiderTrenchMath.LipTick(true, 2400, 4000, 2500, false, false) == -1,
                    "renewed, it outlives the first 2,500 ticks (the old memory expired here and the raid scattered over 4 lines)");
                Assert(RM_RaiderTrenchMath.LipTick(true, 0, 2500, 2500, false, false) == 2500, "can-fail: an abandoned lip still expires");
                Assert(RM_RaiderTrenchMath.LipTick(true, 0, 100, 2500, true, false) == -1, "planning alone does not renew it");
                string r = Src("Superdeep", "RM_RaiderTrench.cs");
                RiverSwitchFlipChecks.Has(r, @"int work = RM_RaiderTrenchMath\.FillWorkPerLevel;", "the driver prices fill flat");
                RiverSwitchFlipChecks.Has(r, @"IsLadder \? 1 : RM_RaiderTrenchMath\.MaxFillersPerSquare", "fillers share a square, ladders do not");
                RiverSwitchFlipChecks.Has(r, @"p\.CanReserve\(c, RM_RaiderTrenchMath\.MaxFillersPerSquare\)", "the giver asks for a shared slot");
                RiverSwitchFlipChecks.Has(r, @"job\.count = t\[i\];", "the job carries the square's causeway target");
                RiverSwitchFlipChecks.Has(r, @"StepDepthAt\(map, eng, c\) > job\.count", "the last shoveller never over-fills the step");
                RiverSwitchFlipChecks.Has(r, @"RememberLip\(p, plan\.cells\[0\], true\)", "an issued job renews the raid's crossing");
            });
            Case("RaiderTrench_wiring", () =>
            {
                string r = Src("Superdeep", "RM_RaiderTrench.cs");
                RiverSwitchFlipChecks.Has(r, @"switch \(RM_RaiderTrenchMath\.Choose\(", "the Verse half decides by Choose");
                RiverSwitchFlipChecks.Has(r, @"LordJob is LordJob_Siege", "sieges are refused");
                RiverSwitchFlipChecks.Has(r, @"TraverseMode\.PassAllDestroyableThings\);\s*if \(reachable\)", "go around: a reachable target is vanilla's (walls are the sappers')");
                RiverSwitchFlipChecks.Has(r, @"!RM_SuperdeepTrap\.IsTrapped\(p\)", "a trapped raider stays trapped (the pit trap is still a trap)");
                RiverSwitchFlipChecks.Has(r, @"RM_LadderUtility\.MaxLevelsOf\(def\)", "ladders use the portable ladder's reach");
                RiverSwitchFlipChecks.Has(r, @"ladder\.SetFaction\(pawn\.Faction\)", "the scaling ladder is the raid's own");
                RiverSwitchFlipChecks.Has(r, @"eng\.FillIn\(c\)", "the breach fills through the excavation engine");
                RiverSwitchFlipChecks.Has(r, @"\[HarmonyPatch\(typeof\(IncidentWorker_Raid\), ""PostProcessSpawnedPawns""\)\]", "jump packs handed out at arrival");
                RiverSwitchFlipChecks.Has(r, @"RaidStrategyWorker_Siege", "never to a siege");
                RiverSwitchFlipChecks.Has(r, @"CanWearWithoutDroppingAnything\(jumpPack\)", "never swaps out a shield belt");
                // RM_RaiderTrench review minors (2026-10-18): lords die with the save; the proof probe is a dry run; a range-0 jump
                // source does not hide the next one.
                RiverSwitchFlipChecks.Has(r, @"\[HarmonyPatch\(typeof\(Game\), nameof\(Game\.FinalizeInit\)\)\]", "per-lord memos cleared on every game load");
                RiverSwitchFlipChecks.Has(r, @"public static void ClearMemos\(\)\s*\{\s*lordLips\.Clear\(\);\s*warned\.Clear\(\);", "ClearMemos empties both statics");
                RiverSwitchFlipChecks.Has(r, @"dryRun = true;\s*try\s*\{\s*j = TryCross\(p\);\s*\}\s*finally\s*\{\s*dryRun = false;", "ProofDecision decides dry");
                RiverSwitchFlipChecks.Has(r, @"if \(dryRun \|\| lord == null \|\| !warned\.Add\(lord\)\)", "a dry run warns nobody");
                RiverSwitchFlipChecks.Has(r, @"if \(r > 0f\)\s*\{\s*verb = v;", "a pack with range 0 falls through to the next source");
                RiverSwitchFlipChecks.Has(r, @"if \(r > 0f\)\s*\{\s*ability = a;", "a range-0 ability falls through to the next ability");
                // TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG minors: ladders that cannot do it after all breach by fill (but a raider
                // waiting on a ladder another is setting does not start a breach); one raider a LADDER square (fill squares are
                // shared up to MaxFillersPerSquare since CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP).
                RiverSwitchFlipChecks.Has(r, @"Job ladder = LadderJob\(p, plan, k, out bool waiting\);\s*chosen = ladder \?\? \(waiting \? null : FillJob\(p, plan, k\)\);",
                    "a null ladder job falls back to the fill breach unless it is only waiting");
                RiverSwitchFlipChecks.Has(r, @"if \(!p\.CanReserve\(cell\) \|\| !p\.CanReach\(cell, PathEndMode\.Touch, Danger\.Deadly\)\)\s*\{\s*waiting = true;",
                    "a slot held by another raider, or out of reach, is a wait, not a breach");
                RiverSwitchFlipChecks.Has(r, @"!eng\.CanFillIn\(c\) \|\| !p\.CanReserve\(c, RM_RaiderTrenchMath\.MaxFillersPerSquare\)", "a square already shovelled by the most raiders is skipped");
                RiverSwitchFlipChecks.Has(r, @"TryMakePreToilReservations\(bool errorOnFailed\)\s*\{\s*return pawn\.Reserve\(job\.targetA, job, IsLadder \? 1 : RM_RaiderTrenchMath\.MaxFillersPerSquare, -1, null, errorOnFailed\);",
                    "can-fail: the work driver reserves its square");
                string u = Src("Superdeep", "RM_LadderUtility.cs");
                RiverSwitchFlipChecks.Has(u, @"MayClimb\(p\) \|\| ClimbsOwnLadder\(ladder, p\)", "the prison door lets a raid climb its own ladder");
                RiverSwitchFlipChecks.Has(u, @"ladder\.Faction != Faction\.OfPlayer && p\.Faction == ladder\.Faction", "only the ladder's own (non-player) faction");
                string pp = Src("Superdeep", "RM_PitPathing.cs");
                RiverSwitchFlipChecks.Has(pp, @"LoweredLadderAt\(map, ladders\[i\]\.Position\) && \(own == null \|\| ladders\[i\]\.Faction != own\)", "the closed-ladder grid leaves a raid's own ladders open");
                string patch = File.ReadAllText(Path.Combine(ModRoot, "Patches", "RaiderTrench", "FlowWorks_RaiderTrenchDuties.xml"));
                foreach (string duty in new[] { "AssaultColony", "Breaching", "Sapper" })
                {
                    Assert(patch.Contains("DutyDef[defName=\"" + duty + "\"]"), "the crossing giver is in the " + duty + " duty");
                }
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(patch, @"DutyDef\[defName=""[^""]*Siege"), "can-fail: no siege duty is touched");
                string jobs = File.ReadAllText(Path.Combine(ModRoot, "Defs", "Canals", "JobDefs", "FlowWorks_RaiderTrench.xml"));
                Assert(jobs.Contains("<defName>RM_RaiderSetLadder</defName>") && jobs.Contains("<defName>RM_RaiderFillTrench</defName>"), "both JobDefs");
                foreach (string f in new[] { "raiderTrenchEnabled", "raiderJumpsEnabled", "raiderLaddersEnabled", "raiderFillEnabled",
                    "raiderLadderSpeed", "raiderFillSpeed", "raiderJumpPackShare" })
                {
                    Assert(r.Contains("ref " + f + ", \"" + f + "\""), "scribed setting " + f);
                }
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("RM_RaiderTrenchSettings.ExposeData();") && mod.Contains("RM_RaiderTrenchSettings.DoSettingsSection);"),
                    "the settings are scribed and drawn");
            });
        }
    }
}
