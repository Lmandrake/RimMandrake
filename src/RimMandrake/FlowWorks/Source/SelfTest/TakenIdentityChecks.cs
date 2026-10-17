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
