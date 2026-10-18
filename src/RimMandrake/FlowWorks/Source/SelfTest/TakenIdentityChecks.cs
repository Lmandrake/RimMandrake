// RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS (live 2026-10-17, R3.c: 3 of 3 swept colonists came back TradersGuild /
// PirateWaster / Outlander*, twice). Root cause: vanilla Pawn.Notify_PassedToWorld hands a Free world pawn of the
// player's (or factionless humanlike) to a random NPC faction; the hold was a Free world pawn. A mock of the take/return
// path: a fake world that runs vanilla's rule (RM_TakenByLandKernel.VanillaReassignsOnPassToWorld) with the situation the
// Harmony postfix reports (ShieldFromFree over RM_TakenHoldSet), and the restore step (NeedsRestore) on the way back.
// The can-fail runs the pre-fix order (no hold) and shows the live result.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.TakenByLand;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class TakenIdentityChecks
    {
        private const int Player = 1, TradersGuild = 7, PirateWaster = 8, Ancients = 3, None = -1;
        private const int GuestGuest = 0, GuestPrisoner = 1, GuestSlave = 2;   // GuestStatus order in 1.6

        private sealed class FakePawn
        {
            public int id;
            public int faction;
            public int host = None;
            public int guest = -1;
            public bool humanlike = true;
            public bool dead;
            public bool spawned = true;
            public string gear = "pants,revolver";
            public RM_TakenByLandKernel.TakenState State => new RM_TakenByLandKernel.TakenState(faction, host, guest);
        }

        private sealed class FakeWorld
        {
            public readonly RM_TakenHoldSet held = new RM_TakenHoldSet();
            public readonly HashSet<int> worldPawns = new HashSet<int>();
            private readonly int[] npc = { TradersGuild, PirateWaster };
            private int next;

            // WorldPawns.GetSituation + RM_Patch_TakenPawnNotFree
            public bool SituationFree(FakePawn p) => !RM_TakenByLandKernel.ShieldFromFree(true, held.Contains(p.id));

            // WorldPawns.PassToWorld -> AddPawn -> Pawn.Notify_PassedToWorld (the faction swap; a swap clears guest status)
            public void PassToWorld(FakePawn p)
            {
                worldPawns.Add(p.id);
                if (RM_TakenByLandKernel.VanillaReassignsOnPassToWorld(p.faction == None, p.faction == Player, p.faction == Ancients,
                        p.humanlike, p.dead, SituationFree(p)))
                {
                    p.faction = npc[next++ % npc.Length];
                    p.host = None;
                    p.guest = -1;
                }
            }

            // PawnGenerator redress: a Free world pawn may be dressed for an NPC group
            public void RedressPass(FakePawn p)
            {
                if (worldPawns.Contains(p.id) && SituationFree(p)) p.gear = "raider kit";
            }
        }

        /// <summary>RM_TakenByLand.Take (hold, then remove) and Return (release, restore, spawn), against the fake world.</summary>
        private static FakePawn TakeAndReturn(FakePawn p, FakeWorld w, bool holdFirst, bool restore)
        {
            RM_TakenByLandKernel.TakenState captured = p.State;
            if (holdFirst) w.held.Hold(p.id);
            p.spawned = false;
            w.PassToWorld(p);
            w.RedressPass(p);
            // ... days pass; the book holds the record ...
            w.worldPawns.Remove(p.id);
            w.held.Release(p.id);
            if (restore)
            {
                RM_TakenByLandKernel.RestoreNeed need = RM_TakenByLandKernel.NeedsRestore(captured, p.State);
                if ((need & RM_TakenByLandKernel.RestoreNeed.Faction) != 0) { p.faction = captured.factionId; p.host = None; p.guest = -1; }
                if ((need & RM_TakenByLandKernel.RestoreNeed.Guest) != 0) { p.host = captured.hostFactionId; p.guest = captured.guestStatus; }
            }
            p.spawned = true;
            return p;
        }

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("RIVER_SWEEP_can_fail_pre_fix_take_hands_colonists_to_npc_factions", () =>
            {
                // The live 2026-10-17 result: no hold, no restore -> same pawn ids, NPC factions, redressed.
                var w = new FakeWorld();
                var got = new List<int>();
                for (int i = 0; i < 3; i++)
                {
                    var p = TakeAndReturn(new FakePawn { id = 54279 + 6 * i, faction = Player }, w, holdFirst: false, restore: false);
                    Assert(p.id == 54279 + 6 * i, "the pre-fix path keeps the pawn object (same thingIDNumber)");
                    got.Add(p.faction);
                    Assert(p.gear == "raider kit", "a Free held pawn is a redress candidate");
                }
                Assert(got.TrueForAll(f => f != Player), "can-fail: 3 of 3 come back with an NPC faction, as live: " + string.Join(",", got));
            });

            Case("RIVER_SWEEP_held_pawns_keep_faction_state_and_gear", () =>
            {
                var w = new FakeWorld();
                var cases = new[]
                {
                    ("colonist", new FakePawn { id = 1, faction = Player }),
                    ("prisoner", new FakePawn { id = 2, faction = PirateWaster, host = Player, guest = GuestPrisoner }),
                    ("slave", new FakePawn { id = 3, faction = Player, host = None, guest = GuestSlave }),
                    ("guest", new FakePawn { id = 4, faction = TradersGuild, host = Player, guest = GuestGuest }),
                    ("tamed animal", new FakePawn { id = 5, faction = Player, humanlike = false }),
                    ("factionless wanderer (gale)", new FakePawn { id = 6, faction = None }),
                };
                foreach (var (label, p) in cases)
                {
                    RM_TakenByLandKernel.TakenState before = p.State;
                    string gear = p.gear;
                    var back = TakeAndReturn(p, w, holdFirst: true, restore: true);
                    Assert(back.id == p.id, label + ": same pawn");
                    Assert(RM_TakenByLandKernel.NeedsRestore(before, back.State) == RM_TakenByLandKernel.RestoreNeed.None,
                        label + ": came back " + back.State + ", taken " + before);
                    Assert(back.gear == gear, label + ": gear kept (no redress while held)");
                    Assert(!w.held.Contains(p.id), label + ": released from the hold on return");
                }
            });

            Case("RIVER_SWEEP_hold_alone_stops_the_swap_and_restore_alone_mends_it", () =>
            {
                var w = new FakeWorld();
                var a = TakeAndReturn(new FakePawn { id = 11, faction = Player }, w, holdFirst: true, restore: false);
                Assert(a.faction == Player, "the hold alone keeps the faction (the swap never fires)");
                var b = TakeAndReturn(new FakePawn { id = 12, faction = Player, guest = GuestSlave }, w, holdFirst: false, restore: true);
                Assert(b.faction == Player && b.guest == GuestSlave, "restore alone puts back faction and slave status: " + b.State);
                var c = TakeAndReturn(new FakePawn { id = 13, faction = PirateWaster, host = Player, guest = GuestPrisoner }, w, false, true);
                Assert(c.faction == PirateWaster && c.host == Player && c.guest == GuestPrisoner, "a prisoner is unaffected: " + c.State);
            });

            // SWEEP_PRISONER_FIX_NEVER_RETURNS (live day 3, sweep_identity.json): the prisoner staged in moving water on the
            // map edge was gone at tick 250 (the river took the colonist and the muffalo at 500), never booked (2 for 3), and
            // after ProofSwept "return" still off the map, still a Prisoner. It escaped (vanilla JobGiver_PrisonerEscape: its
            // district touches the edge, so it exits from the edge cell at once), so the river's Take never ran.
            Case("SWEEP_PRISONER_escape_into_the_current_is_a_sweep", () =>
            {
                var cases = new[]
                {
                    ("prisoner", new FakePawn { id = 49770, faction = PirateWaster, host = Player, guest = GuestPrisoner }),
                    ("slave", new FakePawn { id = 49771, faction = Player, host = None, guest = GuestSlave }),
                };
                foreach (var (label, p0) in cases)
                {
                    // The edge exit, with and without the prefix: swept -> the service's take (held, booked); else vanilla's
                    // ExitMap (PassToWorld, Decide: no hold, no record; nothing ever brings it back).
                    bool Exit(FakePawn fp, FakeWorld fw, List<int> bk, bool prefix)
                    {
                        bool swept = prefix && RM_TakenByLandKernel.ExitIntoCurrentIsSwept(true, true, true, false, true, false);
                        if (swept) { fw.held.Hold(fp.id); bk.Add(fp.id); }
                        fp.spawned = false;
                        fw.PassToWorld(fp);
                        return swept;
                    }
                    var w0 = new FakeWorld();
                    var book0 = new List<int>();
                    var pre = new FakePawn { id = p0.id, faction = p0.faction, host = p0.host, guest = p0.guest };
                    Assert(!Exit(pre, w0, book0, prefix: false) && book0.Count == 0 && !w0.held.Contains(pre.id) && !pre.spawned,
                        label + " can-fail: pre-fix the escape leaves it in the world, unbooked and unheld (the live 2 for 3, never back)");
                    var book = new List<int>();
                    var w1 = new FakeWorld();
                    var probe = new FakePawn { id = p0.id, faction = p0.faction, host = p0.host, guest = p0.guest };
                    Assert(Exit(probe, w1, book, prefix: true) && book.Contains(probe.id) && w1.held.Contains(probe.id),
                        label + ": with the fix the exit into the current is booked and held");
                    var w = new FakeWorld();
                    RM_TakenByLandKernel.TakenState before = p0.State;
                    var back = TakeAndReturn(p0, w, holdFirst: true, restore: true);
                    Assert(back.spawned && back.id == p0.id, label + ": back on the map, same pawn");
                    Assert(RM_TakenByLandKernel.NeedsRestore(before, back.State) == RM_TakenByLandKernel.RestoreNeed.None,
                        label + ": still the player's " + label + ": " + back.State + " vs " + before);
                }
                Assert(!RM_TakenByLandKernel.ExitIntoCurrentIsSwept(true, true, true, false, false, false), "an escape over dry ground stays vanilla's");
                Assert(!RM_TakenByLandKernel.ExitIntoCurrentIsSwept(true, true, true, true, true, false), "a released prisoner walks off free");
                Assert(!RM_TakenByLandKernel.ExitIntoCurrentIsSwept(true, true, false, false, true, false), "a colonist or stranger exit is not this rule");
                Assert(!RM_TakenByLandKernel.ExitIntoCurrentIsSwept(true, true, true, false, true, true), "a caravan or a teleport leaves as vanilla says");
                Assert(!RM_TakenByLandKernel.ExitIntoCurrentIsSwept(false, true, true, false, true, false), "edge washing off: vanilla's escape");
                Assert(!RM_TakenByLandKernel.ExitIntoCurrentIsSwept(true, false, true, false, true, false), "no current running: vanilla's escape");
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("TakenByLand", "RM_TakenByLand.cs"));
                RiverSwitchFlipChecks.Has(src, @"\[HarmonyLib\.HarmonyPatch\(typeof\(Pawn\), nameof\(Pawn\.ExitMap\)\)\] public static class RM_Patch_EscapeIntoCurrentIsSwept",
                    "the ExitMap prefix exists");
                RiverSwitchFlipChecks.Has(src, @"!\(p\.IsPrisonerOfColony \|\| p\.IsSlaveOfColony\)\) return true;", "prisoners and slaves of the player only");
                RiverSwitchFlipChecks.Has(src, @"bool lane = cur != null && cur\.HasCurrent\(p\.Position\) && cur\.IsCarried\(p\);", "the lane test is the current's own");
                RiverSwitchFlipChecks.Has(src, @"return !RM_TakenByLand\.Take\(p, ""river""\);", "taken through the service (held, booked, walked home); vanilla's exit skipped only when taken");
                string pol = src;
                Assert(pol.Contains("public virtual bool Holds(Pawn p) => (p.Faction != null && p.Faction.IsPlayer) || (p.HostFaction != null && p.HostFaction.IsPlayer);"),
                    "the river policy holds the player's prisoners (host) and slaves (faction)");
            });

            // SWEEP_PRISONER_RETURN (live day 4, sweep_identity_fix3.json, DLL 6699957b8): the prisoner came back as itself
            // (letter fired) on the policy's EDGE cell and was off the map within 10 ticks, not held, not a world pawn. A
            // 600-tick walk of vanilla's escape (VanillaPrisonerStartsEscape: secure prisoner whose district touches the edge
            // goes; from an edge cell its exit spot is where it stands) against the return cell and the guard.
            Case("SWEEP_PRISONER_RETURN_edge_cell_escapes_pre_fix_stays_post_fix", () =>
            {
                const int Stay = 600;
                // A fake map's candidates: the policy's random edge cell (outdoors, district touches the edge), an outdoor
                // interior cell, a room whose door is open to the outside, and the prisoner's own prison cell.
                var edge = new RM_TakenByLandKernel.ReturnCandidate(RM_TakenByLandKernel.PrisonerSpot.Interior, true, true, true, false);
                var yard = new RM_TakenByLandKernel.ReturnCandidate(RM_TakenByLandKernel.PrisonerSpot.Interior, true, false, true, false);
                var openRoom = new RM_TakenByLandKernel.ReturnCandidate(RM_TakenByLandKernel.PrisonerSpot.EnclosedRoom, true, false, false, true);
                var cellBed = new RM_TakenByLandKernel.ReturnCandidate(RM_TakenByLandKernel.PrisonerSpot.OwnedBed, true, false, false, false);
                var wallCell = new RM_TakenByLandKernel.ReturnCandidate(RM_TakenByLandKernel.PrisonerSpot.PrisonCell, false, false, false, false);

                // Ticks until it is off the map, -1 = still here after Stay. Escape is checked every tick (the think tree);
                // walking to the exit spot takes distToEdge ticks (0 on an edge cell: ExitMap at once).
                int OffMapAt(RM_TakenByLandKernel.ReturnCandidate at, bool guard, int distToEdge)
                {
                    var g = new RM_TakenReturnGuard();
                    const int id = 63628, back = 17038;
                    if (guard) g.Mark(id, back);
                    int startedAt = -1;
                    for (int t = back; t <= back + Stay; t++)
                    {
                        if (startedAt < 0 && !g.InGuard(id, t)
                            && RM_TakenByLandKernel.VanillaPrisonerStartsEscape(true, true, false, at.districtTouchesEdge, at.openPathToEdge))
                            startedAt = t;
                        if (startedAt >= 0 && t - startedAt >= distToEdge) return t - back;
                    }
                    return -1;
                }

                int pre = OffMapAt(edge, guard: false, distToEdge: 0);
                Assert(pre >= 0 && pre <= 10, "can-fail: pre-fix on the edge cell it is off the map within 10 ticks (live day 4): " + pre);
                Assert(OffMapAt(edge, guard: true, distToEdge: 0) < 0, "the guard alone holds it on the map for " + Stay + " ticks");

                var all = new List<RM_TakenByLandKernel.ReturnCandidate> { edge, yard, openRoom, wallCell, cellBed };
                int k = RM_TakenByLandKernel.PickPrisonerReturn(all, out bool secure);
                Assert(k == 4 && secure, "the pick is its own bed in its cell (secure), not the edge, the yard, the open room or a wall: " + k);
                Assert(OffMapAt(all[k], guard: false, distToEdge: 30) < 0, "in its cell vanilla never starts an escape, guard or not");
                Assert(OffMapAt(all[k], guard: true, distToEdge: 30) < 0, "post-fix (cell + guard): still on the map after " + Stay + " ticks");

                // No cell on the map: the best off-edge cell (never the edge), not secure; the guard holds it the hour.
                var noCell = new List<RM_TakenByLandKernel.ReturnCandidate> { edge, yard };
                k = RM_TakenByLandKernel.PickPrisonerReturn(noCell, out secure);
                Assert(k == 1 && !secure, "no secure cell: the off-edge yard cell, flagged not secure: " + k + "/" + secure);
                Assert(OffMapAt(noCell[k], guard: true, distToEdge: 0) < 0, "no cell: the guard keeps it on the map for " + Stay + " ticks");
                Assert(RM_TakenByLandKernel.PickPrisonerReturn(new List<RM_TakenByLandKernel.ReturnCandidate> { edge }, out secure) < 0 && !secure,
                    "only the edge: no pick (the caller keeps its cell; the guard still holds)");
                Assert(RM_TakenByLandKernel.PickPrisonerReturn(new List<RM_TakenByLandKernel.ReturnCandidate> { openRoom, yard }, out secure) == 0 && !secure,
                    "an open-door room is not secure (vanilla's 25-region search reaches the edge), but beats the yard");

                // The guard window and the lost-prisoner letter rule.
                var gw = new RM_TakenReturnGuard();
                gw.Mark(7, 1000);
                Assert(gw.InGuard(7, 1000) && gw.InGuard(7, 1000 + RM_TakenByLandKernel.ReturnGuardTicks - 1)
                       && !gw.InGuard(7, 1000 + RM_TakenByLandKernel.ReturnGuardTicks) && !gw.InGuard(8, 1000) && !gw.InGuard(7, 999),
                    "guard: from the return tick for ReturnGuardTicks, that pawn only");
                Assert(RM_TakenByLandKernel.ReturnGuardTicks >= Stay, "the guard outlasts the live proof's 600-tick stay");
                Assert(gw.Recent(7, 1000 + RM_TakenByLandKernel.ReturnWatchTicks - 1) && !gw.Recent(7, 1000 + RM_TakenByLandKernel.ReturnWatchTicks),
                    "watch window");
                gw.Prune(1000 + RM_TakenByLandKernel.ReturnWatchTicks);
                Assert(gw.Count == 0, "prune forgets old returns");
                Assert(RM_TakenByLandKernel.ExitIsLostReturn(true, false, false, true), "a returned prisoner slipping off: letter");
                Assert(!RM_TakenByLandKernel.ExitIsLostReturn(true, true, false, true), "released: no letter");
                Assert(!RM_TakenByLandKernel.ExitIsLostReturn(true, false, true, true), "caravan/teleport: no letter");
                Assert(!RM_TakenByLandKernel.ExitIsLostReturn(true, false, false, false), "an ordinary vanilla escape: vanilla's own message");
                Assert(!RM_TakenByLandKernel.ExitIsLostReturn(false, false, false, true), "a colonist leaving: not this rule");
                Assert(!RM_TakenByLandKernel.VanillaPrisonerStartsEscape(true, true, true, true, false), "mirror: a lord-secure prisoner stays");
                Assert(!RM_TakenByLandKernel.VanillaPrisonerStartsEscape(true, false, false, true, false), "mirror: an insecure prisoner stays");

                // The Verse side wires it: restore before the cell (IsPrisonerOfColony reads the restored state), the pick, the
                // guard mark before the spawn, the two patches.
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("TakenByLand", "RM_TakenByLand.cs"));
                int iRestore = src.IndexOf("RM_TakenByLand.Restore(r, p);", StringComparison.Ordinal);
                int iPick = src.IndexOf("RM_TakenByLand.PickPrisonerReturnCell(p, map, out bool secure)", StringComparison.Ordinal);
                int iMark = src.IndexOf("RM_TakenByLand.Returned.Mark(p.thingIDNumber", StringComparison.Ordinal);
                int iSpawn = src.IndexOf("GenSpawn.Spawn(p, cell, map", StringComparison.Ordinal);
                Assert(iRestore > 0 && iRestore < iPick && iPick < iMark && iMark < iSpawn, "Return(): restore, pick, mark, spawn in that order: "
                    + iRestore + "," + iPick + "," + iMark + "," + iSpawn);
                RiverSwitchFlipChecks.Has(src, @"\[HarmonyLib\.HarmonyPatch\(typeof\(JobGiver_PrisonerEscape\), ""TryGiveJob""\)\] public static class RM_Patch_ReturnedPrisonerNoEscape",
                    "the escape guard patch exists");
                RiverSwitchFlipChecks.Has(src, @"RM_TakenByLand\.Returned\.InGuard\(pawn\.thingIDNumber, Find\.TickManager\.TicksGame\)", "the guard reads the kernel window");
                RiverSwitchFlipChecks.Has(src, @"public static class RM_Patch_ReturnedPrisonerLost", "the lost-prisoner letter patch exists");
            });

            Case("RIVER_SWEEP_kernel_rules", () =>
            {
                Assert(RM_TakenByLandKernel.VanillaReassignsOnPassToWorld(false, true, false, true, false, true), "free colonist: swapped");
                Assert(RM_TakenByLandKernel.VanillaReassignsOnPassToWorld(false, true, false, false, false, true), "free tamed animal: swapped");
                Assert(RM_TakenByLandKernel.VanillaReassignsOnPassToWorld(true, false, false, true, false, true), "factionless humanlike: swapped");
                Assert(!RM_TakenByLandKernel.VanillaReassignsOnPassToWorld(true, false, false, false, false, true), "factionless animal: kept");
                Assert(!RM_TakenByLandKernel.VanillaReassignsOnPassToWorld(false, false, false, true, false, true), "NPC pawn: kept");
                Assert(!RM_TakenByLandKernel.VanillaReassignsOnPassToWorld(false, true, false, true, true, true), "dead: kept");
                Assert(!RM_TakenByLandKernel.VanillaReassignsOnPassToWorld(false, true, false, true, false, false), "not Free: kept");
                Assert(RM_TakenByLandKernel.ShieldFromFree(true, true) && !RM_TakenByLandKernel.ShieldFromFree(true, false)
                       && !RM_TakenByLandKernel.ShieldFromFree(false, true), "only a Free AND held pawn is shielded");
                var cap = new RM_TakenByLandKernel.TakenState(Player, None, -1);
                Assert(RM_TakenByLandKernel.NeedsRestore(cap, cap) == RM_TakenByLandKernel.RestoreNeed.None, "same state: nothing");
                Assert(RM_TakenByLandKernel.NeedsRestore(cap, new RM_TakenByLandKernel.TakenState(TradersGuild, None, -1))
                       == (RM_TakenByLandKernel.RestoreNeed.Faction | RM_TakenByLandKernel.RestoreNeed.Guest), "faction change: faction then guest");
                var pris = new RM_TakenByLandKernel.TakenState(PirateWaster, Player, GuestPrisoner);
                Assert(RM_TakenByLandKernel.NeedsRestore(pris, new RM_TakenByLandKernel.TakenState(PirateWaster, None, -1))
                       == RM_TakenByLandKernel.RestoreNeed.Guest, "a released prisoner: guest only");
                var hs = new RM_TakenHoldSet();
                hs.Hold(5); hs.Hold(-1); hs.Hold(5);
                Assert(hs.Count == 1 && hs.Contains(5), "hold set: ids only, no duplicates, no negatives");
                hs.Rebuild(new[] { 7, 8 });
                Assert(hs.Count == 2 && !hs.Contains(5) && hs.Contains(8), "rebuild replaces the set (load)");
                hs.Release(7); hs.Clear();
                Assert(hs.Count == 0, "release/clear");
            });
        }
    }
}
