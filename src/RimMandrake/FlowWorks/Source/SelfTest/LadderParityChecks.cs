// LADDER_PARITY_BUILD_NO_KEYS_REQUIRED (owner by card 2026-10-23, option (4) "Full parity both ways"; his words: "It's (4). We
// need a way to repair damage caused by people digging their way into a pit. Digging should be slow. Building ladders
// available to both sides on demand. Both sides should be able to use each other's ladders: makes NO sense otherwise (what are
// they locked with a key?). Can pick up each other's ladders too and move them. Raiders should show up with ladders sometimes
// but not always, and certainly not on every raider. Ladders should work to climb one-way over single walls without roofs as
// well."). Design: design/RimMandrake/ladder_parity_2026-10-23.md. One case per clause, each with a can-fail; the wiring
// cases read the production source.
// NOT proven here (live rows owed, see the item's criteria): a raider climbs a colonist's lowered ladder and a colonist a
// raider's; a raid arrives with a few ladder carriers; a colonist uninstalls a raider's ladder; a raider takes one; a breach
// scar is repaired by a dig order; a ladder against an unroofed wall carries a pawn over one way.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LadderParityChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static bool May(bool noKeys = true, bool faction = true, bool player = false, bool hostile = true,
            bool prisoner = false, bool breaking = false)
        {
            return RM_LadderParityMath.MayClimbLowered(noKeys, faction, player, hostile, prisoner, breaking);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("LadderParity_no_keys", () =>
            {
                Assert(May(), "a raider climbs anyone's lowered ladder (no keys)");
                Assert(May(player: true, hostile: false), "a colonist climbs it");
                Assert(May(hostile: false), "a friendly visitor climbs it");
                Assert(!May(noKeys: false), "can-fail: no-keys off restores the prison-door bar on hostiles");
                Assert(May(noKeys: false, hostile: false), "no-keys off: friendlies still climb");
                Assert(!May(faction: false, hostile: false), "can-fail: a wild animal never climbs a ladder");
                Assert(!May(prisoner: true, player: false, hostile: false), "can-fail: a prisoner stays down");
                Assert(May(prisoner: true, breaking: true), "a prisoner in a prison break climbs");
                // a RAISED wall ladder is still nobody's (his 2026-10-18 jail ruling): LadderUsable is unchanged
                Assert(!RM_PitTrapMath.LadderUsable(true, true, true, May()), "can-fail: a raised ladder stays shut to everyone");
            });
            Case("LadderParity_raids_bring_some_ladders_never_all", () =>
            {
                int brings = 0;
                for (int seed = 0; seed < 4000; seed++)
                {
                    if (RM_LadderParityMath.RaidBringsLadders(seed, 0.35f)) brings++;
                }
                Assert(brings > 4000 * 0.30 && brings < 4000 * 0.40, "about 35 % of raids bring ladders: " + brings);
                Assert(!RM_LadderParityMath.RaidBringsLadders(7, 0f), "can-fail: chance 0, never");
                Assert(RM_LadderParityMath.RaidBringsLadders(7, 1f), "chance 1, always");
                Assert(RM_LadderParityMath.RaidBringsLadders(123, 0.35f) == RM_LadderParityMath.RaidBringsLadders(123, 0.35f), "stable per raid");
                Assert(RM_LadderParityMath.CarrierCount(10, 0.25f) == 3, "a quarter of 10, rounded: 3");
                Assert(RM_LadderParityMath.CarrierCount(2, 0.25f) == 1, "at least one carrier when the raid brings ladders");
                Assert(RM_LadderParityMath.CarrierCount(1, 0.25f) == 0, "can-fail: a lone raider is never 'every raider'");
                Assert(RM_LadderParityMath.CarrierCount(5, 1f) == 4, "can-fail: never every raider, even at 100 %");
                Assert(RM_LadderParityMath.CarrierCount(10, 0f) == 0, "share 0: nobody");
                var ids = Enumerable.Range(1000, 12).ToList();
                List<int> a = RM_LadderParityMath.PickCarriers(ids, 0.25f);
                Assert(a.Count == 3 && a.All(ids.Contains), "picks 3 of 12 from the raid");
                Assert(a.SequenceEqual(RM_LadderParityMath.PickCarriers(ids.AsEnumerable().Reverse().ToList(), 0.25f)),
                    "can-fail: the pick does not depend on list order (a reload never re-rolls)");
            });
            Case("LadderParity_build_on_demand_and_carried_is_faster", () =>
            {
                int built = RM_LadderParityMath.RaiderLadderTicks(2.0, 1f, false);
                int set = RM_LadderParityMath.RaiderLadderTicks(2.0, 1f, true);
                Assert(built == RM_RaiderTrenchMath.LadderTicks(2.0, 1f), "built on demand: the 2026-10-18 time (10 s + 1 s/m)");
                Assert(set == 300, "a carried ladder is set in 4 s + 0.5 s/m: " + set);
                Assert(set < built, "can-fail: carrying one is faster than building one");
                Assert(RM_LadderParityMath.RaiderLadderTicks(2.0, 2f, true) == 150, "the speed slider divides it");
            });
            Case("LadderParity_take_each_others_ladders", () =>
            {
                Assert(RM_LadderParityMath.MayTakeLadder(true, false, 20 * 20, 25, false, false), "a ladderless raider takes one in reach");
                Assert(!RM_LadderParityMath.MayTakeLadder(true, true, 4, 25, false, false), "can-fail: one who carries a ladder takes none");
                Assert(!RM_LadderParityMath.MayTakeLadder(true, false, 26 * 26, 25, false, false), "can-fail: beyond the radius");
                Assert(!RM_LadderParityMath.MayTakeLadder(true, false, 4, 25, true, false), "can-fail: not a ladder its own crossing stands on");
                Assert(!RM_LadderParityMath.MayTakeLadder(true, false, 4, 25, false, true), "can-fail: not from under a pawn on it");
                Assert(!RM_LadderParityMath.MayTakeLadder(false, false, 4, 25, false, false), "can-fail: the setting off");
                string d = Src("..", "Defs", "Canals", "ThingDefs", "FlowWorks_PitAccess.xml");
                int at = d.IndexOf("<defName>RM_LadderPortable</defName>", StringComparison.Ordinal);
                int end = d.IndexOf("</ThingDef>", at, StringComparison.Ordinal);
                Assert(at > 0 && d.Substring(at, end - at).Contains("<alwaysUninstallable>true</alwaysUninstallable>"),
                    "colonists uninstall anyone's portable ladder (vanilla Designator_Uninstall's alwaysUninstallable)");
                Assert(!d.Substring(at, end - at).Contains("trapped enemies"), "can-fail: the description no longer promises the key");
            });
            Case("LadderParity_breach_scar_and_repair", () =>
            {
                Assert(RM_LadderParityMath.ScarAfterFill(0, 8) == 8, "the first fill remembers the depth before it");
                Assert(RM_LadderParityMath.ScarAfterFill(8, 7) == 8, "can-fail: a later fill never lowers the scar");
                Assert(RM_LadderParityMath.RepairTarget(8, 5) == 8, "repair digs back to the scar");
                Assert(RM_LadderParityMath.RepairTarget(8, 8) == 0, "can-fail: a healed square needs no order");
                Assert(RM_LadderParityMath.RepairTarget(0, 3) == 0, "can-fail: an unscarred square is not 'repaired'");
                Assert(RM_LadderParityMath.ScarHealed(8, 9) && !RM_LadderParityMath.ScarHealed(8, 7), "a scar clears at its depth");
                Assert(RM_LadderParityMath.DefaultRaiderFillSpeed == 0.5f, "digging in is slow: x0.5 (PROVISIONAL)");
                string r = Src("Superdeep", "RM_RaiderTrench.cs");
                RiverSwitchFlipChecks.Has(r, @"public static float raiderFillSpeed = RM_LadderParityMath\.DefaultRaiderFillSpeed;", "the shipped fill speed");
                RiverSwitchFlipChecks.Has(r, @"RM_BreachScars\.NoteFill\(map, c\);\s*eng\.FillIn\(c\);", "every raider fill records the scar first");
                string s = Src("Superdeep", "RM_LadderParity.cs");
                RiverSwitchFlipChecks.Has(s, @"class Designator_RM_RepairBreach", "the repair designator");
                RiverSwitchFlipChecks.Has(s, @"SetDigTarget\(c, target\)", "repair is an ordinary dig-to order");
            });
            Case("LadderParity_one_way_over_a_single_unroofed_wall", () =>
            {
                Func<bool, bool, bool, bool, int, bool, bool, bool, bool> O = (on, at, faces, usable, sq, wallRoof, fromRoof, toRoof) =>
                    RM_LadderParityMath.LadderOverWallOpen(on, at, faces, usable, sq, wallRoof, fromRoof, toRoof, true, true);
                Assert(O(true, true, true, true, 1, false, false, false), "a ladder at the foot, facing a single open wall: over");
                Assert(!O(true, false, true, true, 1, false, false, false), "can-fail: one way: no ladder on this side, no climb");
                Assert(!O(true, true, false, true, 1, false, false, false), "can-fail: a ladder facing elsewhere");
                Assert(!O(true, true, true, true, 2, false, false, false), "can-fail: a double wall is not a single wall");
                Assert(!O(true, true, true, true, 1, true, false, false), "can-fail: a roofed wall");
                Assert(!O(true, true, true, true, 1, false, false, true), "can-fail: a roofed landing");
                Assert(!O(false, true, true, true, 1, false, false, false), "can-fail: the setting off");
                Assert(!O(true, true, true, false, 1, false, false, false), "can-fail: a pawn the ladder rule refuses (a prisoner)");
                Assert(RM_LadderParityMath.PlaceOnWall(true, false, true, 1), "placeable on open ground against a wall");
                Assert(!RM_LadderParityMath.PlaceOnWall(true, false, false, 1), "can-fail: no wall in front");
                Assert(!RM_LadderParityMath.PlaceOnWall(true, false, true, 2), "can-fail: a double wall");
                Assert(!RM_LadderParityMath.PlaceOnWall(false, false, true, 1), "can-fail: the setting off");
                int ladder = RM_LadderParityMath.WallClimbTicks(RM_LadderParityMath.DefaultWallLadderSlowFactor, 13f);
                int gear = RM_WallClimbMath.ClimbTicks(1, RM_WallClimbMath.DefaultSlowFactor, 13f);
                Assert(ladder < gear && ladder >= 52, "a ladder is quicker than ropes and claws: " + ladder + " vs " + gear);
                string w = Src("Superdeep", "RM_WallClimb.cs");
                RiverSwitchFlipChecks.Has(w, @"RM_LadderParity\.CanClimbAt\(", "the climb seams ask the ladder too");
            });
            Case("LadderParity_wiring", () =>
            {
                string u = Src("Superdeep", "RM_LadderUtility.cs");
                RiverSwitchFlipChecks.Has(u, @"RM_LadderParityMath\.MayClimbLowered\(", "the prison-door read is the parity rule");
                string p = Src("Superdeep", "RM_LadderParity.cs");
                RiverSwitchFlipChecks.Has(p, @"\[HarmonyPatch\(typeof\(IncidentWorker_Raid\), ""PostProcessSpawnedPawns""\)\]", "carriers handed ladders at arrival");
                RiverSwitchFlipChecks.Has(p, @"RaidStrategyWorker_Siege", "never to a siege");
                RiverSwitchFlipChecks.Has(p, @"RM_LadderParityMath\.PickCarriers\(", "the carriers are picked by the rule");
                foreach (string f in new[] { "ladderNoKeys", "raidLadderChance", "raidLadderCarrierShare", "raiderTakeLadders",
                    "raiderTakeLadderRadius", "breachRepairEnabled", "ladderOverWalls", "wallLadderSlowFactor" })
                {
                    Assert(p.Contains("ref " + f + ", \"" + f + "\""), "scribed setting " + f);
                }
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("RM_LadderParitySettings.ExposeData();") && mod.Contains("RM_LadderParitySettings.DoSettingsSection);"),
                    "settings scribed and drawn");
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                Assert(csproj.Contains("Superdeep\\RM_LadderParity.cs") && csproj.Contains("Superdeep\\RM_LadderParityMath.cs"), "compiled");
                string r = Src("Superdeep", "RM_RaiderTrench.cs");
                RiverSwitchFlipChecks.Has(r, @"RM_LadderParity\.TakeCarried\(pawn\)", "a carried ladder is set from the inventory");
            });
        }
    }
}
