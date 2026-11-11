// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED (owner 2026-10-25: "You can't dig without them. Hands don't work"; "Shovels now v1.";
// Q1 "Siege is mortar-based. Sappers however would bring shovels & ladders."; Q2 yes, sand and drift too; Q3 yes, every
// scenario we ship starts with one). Design: design/RimMandrake/shovels_v1_2026-10-25.md. The pure rules (RM_ShovelMath)
// with a can-fail per clause, then the wiring read from the production source.
// NOT proven here (the SH_* live rows owed on the item): a colonist fetches a shovel then digs; the shovel stays in the
// pack; a raid really arrives with shovels; a raider without one does not fill; vanilla sand clearing refuses bare hands.
using System;
using System.IO;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ShovelChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        public static void Run(Action<string, Action> Case)
        {
            Case("Shovels: who needs one (setting x machine x bare-handed, 8 rows)", () =>
            {
                for (int i = 0; i < 8; i++)
                {
                    bool on = (i & 1) != 0, machine = (i & 2) != 0, bare = (i & 4) != 0;
                    bool want = on && !machine && !bare;
                    Assert(RM_ShovelMath.NeedsShovel(on, machine, bare) == want,
                        "NeedsShovel(" + on + ", " + machine + ", " + bare + ") should be " + want);
                }
                Assert(RM_ShovelMath.NeedsShovel(true, false, false), "can-fail: a plain colonist with the setting on needs one");
            });

            Case("Shovels: a siege brings none, sappers their share, others the assault share, clamped", () =>
            {
                Assert(RM_ShovelMath.ShareFor(true, false, 1f, 1f) == 0f, "siege: none even at 100%");
                Assert(RM_ShovelMath.ShareFor(true, true, 1f, 1f) == 0f, "siege wins over sapper");
                Assert(RM_ShovelMath.ShareFor(false, true, 0.25f, 0.5f) == 0.5f, "sappers: the sapper share");
                Assert(RM_ShovelMath.ShareFor(false, false, 0.25f, 0.5f) == 0.25f, "assault: the assault share");
                Assert(RM_ShovelMath.ShareFor(false, false, -1f, 0.5f) == 0f && RM_ShovelMath.ShareFor(false, true, 0.25f, 3f) == 1f,
                    "clamped to [0, 1]");
                Assert(RM_ShovelMath.DefaultSapperShovelShare > RM_ShovelMath.DefaultRaiderShovelShare,
                    "sappers bring more than an assault");
            });

            Case("Shovels: GetsShovel bounds, rate, determinism, not the jump-pack people", () =>
            {
                int hits = 0, differ = 0;
                for (int id = 1; id <= 10000; id++)
                {
                    Assert(!RM_ShovelMath.GetsShovel(id, 0f) && RM_ShovelMath.GetsShovel(id, 1f), "0 nobody, 1 everybody (id " + id + ")");
                    bool g = RM_ShovelMath.GetsShovel(id, 0.25f);
                    Assert(g == RM_ShovelMath.GetsShovel(id, 0.25f), "deterministic per id");
                    if (g) hits++;
                    if (g != RM_RaiderTrenchMath.GetsJumpPack(id, 0.25f)) differ++;
                }
                Assert(hits >= 2300 && hits <= 2700, "25% share hits " + hits + " of 10000");
                Assert(differ > 1000, "shovel and jump-pack shares pick different people (" + differ + " differ)");
            });

            Case("Shovels: colonist WorkGivers gate, fetch first, drivers fail without", () =>
            {
                foreach (string wg in new[] { "WorkGiver_DigCanal.cs", "WorkGiver_FillInCanal.cs" })
                {
                    string s = Src(wg);
                    RiverSwitchFlipChecks.Has(s, @"if \(!RM_Shovels\.CanWorkOrFetch\(pawn, forced\)\)", wg + " HasJobOnCell gate");
                    RiverSwitchFlipChecks.Has(s, @"if \(!RM_Shovels\.Ready\(pawn\)\) \{ return RM_Shovels\.FetchJobFor\(pawn, forced\);", wg + " JobOnCell fetches first");
                }
                RiverSwitchFlipChecks.Has(Src("JobDriver_DigCanal.cs"), @"FailOn\(this, \(\) => !RM_Shovels\.Ready\(pawn\)\)", "dig driver fails without");
                RiverSwitchFlipChecks.Has(Src("JobDriver_FillInCanal.cs"), @"this\.FailOn\(\(\) => !RM_Shovels\.Ready\(pawn\)\)", "fill driver fails without");
                string sh = Src("RM_Shovels.cs");
                RiverSwitchFlipChecks.Has(sh, @"GetNamedSilentFail\(""TakeInventory""\)", "the fetch is vanilla TakeInventory");
                RiverSwitchFlipChecks.Has(sh, @"job\.count = 1;", "one shovel, not the stack");
                RiverSwitchFlipChecks.Has(sh, @"RM_ShovelMath\.NeedsShovel\(Required, RM_DigLabor\.IsMachineLabour\(pawn\), DigsBareHanded\(pawn\)\)", "machines dig bare");
            });

            Case("Shovels: raiders fill only with one; sieges none; sappers bring shovels and ladders", () =>
            {
                string r = Src("Superdeep", "RM_RaiderTrench.cs");
                int gate = r.IndexOf("if (RM_Shovels.Needs(p) && !RM_Shovels.HasShovel(p))", StringComparison.Ordinal);
                int fetch = r.IndexOf("return FetchJob(p, c);", StringComparison.Ordinal);
                Assert(gate > 0 && fetch > gate, "FillJob's shovel gate comes before FetchJob");
                RiverSwitchFlipChecks.Has(r, @"FindShovelFor\(p, false, FetchRadius, true\)", "a raider grabs any loose shovel within FetchRadius");
                RiverSwitchFlipChecks.Has(r, @"this\.FailOn\(\(\) => !IsLadder && !RM_Shovels\.Ready\(pawn\)\)", "trench fill work fails without");
                RiverSwitchFlipChecks.Has(r, @"each <= 0 \|\| !RM_Shovels\.Ready\(pawn\)", "the fetched fill is not tipped without");
                foreach (string f in new[] { "raiderShovelShare", "sapperShovelShare" })
                {
                    Assert(r.Contains("ref " + f + ", \"" + f + "\""), "scribed setting " + f);
                }
                Assert(r.IndexOf("sapperShovelShare =", StringComparison.Ordinal) < r.IndexOf("RM_SettingsReset.Snapshot", StringComparison.Ordinal),
                    "the share fields sit above the reset snapshot");
                string sh = Src("RM_Shovels.cs");
                RiverSwitchFlipChecks.Has(sh, @"ShareFor\(worker is RaidStrategyWorker_Siege, worker is RaidStrategyWorker_ImmediateAttackSappers,", "the raid postfix keys siege and sapper by strategy worker");
                RiverSwitchFlipChecks.Has(sh, @"!RM_Shovels\.Required \|\| !RM_RaiderTrench\.On", "no shovels handed out with the rule or the raider feature off");
                Assert(!Regex.IsMatch(sh + r, @"siegeBorrowPits|siegeBreachEnabled|siegeShovelShare"), "can-fail: siege digging is out of scope (owner Q1)");
                string l = Src("Superdeep", "RM_LadderParity.cs");
                RiverSwitchFlipChecks.Has(l, @"bool sappers = parms\.raidStrategy\?\.Worker is RaidStrategyWorker_ImmediateAttackSappers;", "sapper raid detected");
                RiverSwitchFlipChecks.Has(l, @"\(!sappers && !RM_LadderParityMath\.RaidBringsLadders\(", "a sapper raid always brings ladders");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("Scribe_Values.Look(ref shovelRequired") && Regex.Matches(mod, "\"shovelRequired\"").Count >= 3,
                    "shovelRequired saved and registered");
                Assert(mod.IndexOf("public static bool shovelRequired", StringComparison.Ordinal) < mod.IndexOf("shippedDefaults = CaptureDefaults()", StringComparison.Ordinal),
                    "shovelRequired sits above the shipped-defaults capture");
            });

            Case("Shovels: Pyrelands sand, Moving Dunes drift and the Utinni scenario", () =>
            {
                string py = Src("..", "..", "Pyrelands", "Source", "RM_TerrainDig.cs");
                RiverSwitchFlipChecks.Has(py, @"return RimMandrake\.Shared\.FlowWorksShovelRead\.CanWorkOrFetch\(pawn, forced\);", "sand shovelling gate");
                RiverSwitchFlipChecks.Has(py, @"\|\| !RimMandrake\.Shared\.FlowWorksShovelRead\.Ready\(pawn\)\);", "sand driver fails without");
                string md = Src("..", "..", "MovingDunes", "Source", "Patch_ClearSandShovel.cs");
                RiverSwitchFlipChecks.Has(md, @"map\.sandGrid\.GetDepth\(c\) > 0f", "only sandy cells, snow stays vanilla");
                RiverSwitchFlipChecks.Has(md, @"FlowWorksShovelRead\.CanWorkOrFetch\(__0, __2\)", "drift clear gate");
                string mdm = Src("..", "..", "MovingDunes", "Source", "MovingDunesMod.cs");
                RiverSwitchFlipChecks.Has(mdm, @"typeof\(WorkGiver_ClearSnowOrSand\), ""HasJobOnCell""", "drift gate patched on the vanilla scanner");
                string rd = Src("..", "..", "_Shared", "FlowWorksShovels", "FlowWorksShovelRead.cs");
                RiverSwitchFlipChecks.Has(rd, @"TypeByName\(""RimMandrake\.FlowWorks\.RM_Shovels""\)", "the reader names the real class");
                RiverSwitchFlipChecks.Has(rd, @"return ready == null \|\| fetch == null \|\| ready\(pawn\);", "FlowWorks absent: nobody needs a shovel");
                string scen = Src("..", "..", "..", "RimUtinni", "UtinniPatches", "Defs", "ScenarioDefs", "Scenario_Utinni.xml");
                RiverSwitchFlipChecks.Has(scen, @"<li Class=""ScenPart_StartingThing_Defined"" MayRequire=""mandrake\.rm\.flowworks""> <def>StartingThing_Defined</def> <thingDef>RM_Shovel</thingDef>", "the scenario starts with a shovel");
            });
        }
    }
}
