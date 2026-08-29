// JawaBenchLordTools2.cs - the four Lords-domain gaps left after
// jawa/lord_pawn_move (list/attach/detach), jawa/lord_set_job (swap an existing
// Lord's whole LordJob) and jawa/lord_poke (memo/signal) shipped.
//
// Filed from BRIDGE_CAPABILITY_ROSTER.md §0/§5: nothing on the bridge could
// destroy an arbitrary Lord, retarget a live DefendPoint/Travel toil without
// rebuilding its whole graph, or make a group walk a closed patrol circuit.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   Verse/AI/Group/LordManager.cs   RemoveLord(Lord) - the public route; Lord's
//                                   own Destroy() is PRIVATE, called only from
//                                   inside RemoveLord's own Cleanup() chain.
//   Verse/AI/Group/LordToil_DefendPoint.cs   SetDefendPoint(IntVec3), FlagLoc
//   Verse/AI/Group/LordToil_Travel.cs        SetDestination(IntVec3), FlagLoc,
//                                             ctor(IntVec3 dest)
//   Verse/AI/Group/StateGraph.cs             StartingToil, AddToil, AddTransition
//   Verse/AI/Group/Transition.cs             ctor(source, target), triggers
//   Verse/AI/Group/Trigger_Memo.cs           ctor(string memo)
//   Verse/AI/Group/LordJob.cs                CreateGraph() abstract, ExposeData()
//
// 🔴 TWO TRAPS THE SOURCE CONFIRMED:
//   * SetDefendPoint / SetDestination only write the toil's DATA. UpdateAllDuties()
//     is what actually re-issues each pawn's PawnDuty from that data - it normally
//     only runs on toil entry (GotoToil). A tool that wrote the field and stopped
//     there would report success while every pawn kept walking to the OLD point.
//     Both setters below call UpdateAllDuties() themselves, same rule as
//     JawaBenchLordJobTools.cs's SetJob+GotoToil pairing.
//   * A cyclic StateGraph (the ring transition pawns_patrol_route builds) is legal
//     by every check StateGraph.ErrorCheck() runs, but NO SHIPPED LordJob CONTAINS
//     ONE - this is a hypothesis about engine behaviour, not a measured fact, until
//     a live quicktest proves the ring actually cycles instead of stalling on its
//     closing transition. Said plainly in the tool's own Description.
//
// GATED behind JAWA_GM_TOOLS, same tier as jawa/lord_defend_spawn,
// jawa/lord_assault_spawn and jawa/social_cancel: every tool here either destroys
// or creates a live AI group, which is the world acting on the player's colony.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    /// <summary>
    /// A closed patrol circuit: one LordToil_Travel per waypoint, ring-transitioned
    /// on the "TravelArrived" memo LordToil_Travel already fires every 205 ticks
    /// once the whole group is within range and can reach. No custom Trigger, no
    /// Harmony - `BRIDGE_CAPABILITY_ROSTER.md` §5 names this "the single
    /// highest-value custom class on the whole roster."
    /// </summary>
    public class LordJob_Patrol : LordJob
    {
        public List<IntVec3> waypoints = new List<IntVec3>();

        public override StateGraph CreateGraph()
        {
            var g = new StateGraph();
            var toils = waypoints.Select(w => new LordToil_Travel(w)).ToList();
            g.StartingToil = toils[0];
            for (int i = 1; i < toils.Count; i++) g.AddToil(toils[i]);
            for (int i = 0; i < toils.Count; i++)
                g.AddTransition(new Transition(toils[i], toils[(i + 1) % toils.Count])
                {
                    triggers = { new Trigger_Memo("TravelArrived") }
                });
            return g;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref waypoints, "waypoints", LookMode.Value);
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        /// <summary>Address a Lord by index, optionally asserting its loadID - the
        /// same identity-check convention as jawa/lord_set_job.</summary>
        private static Lord ResolveLord(LordManager lm, int lordIndex, int loadID, out object err)
        {
            err = null;
            if (lordIndex < 0 || lordIndex >= lm.lords.Count)
            {
                err = Fail("lordIndex " + lordIndex + " is out of range (0.." + (lm.lords.Count - 1) +
                            "). Call jawa/lord_pawn_move action=list first.",
                    new
                    {
                        lords = lm.lords.Select((l, i) => new
                        {
                            index = i,
                            loadID = l.loadID,
                            faction = l.faction != null ? l.faction.Name : null,
                            pawns = l.ownedPawns != null ? l.ownedPawns.Count : 0,
                            job = LordJobName(l),
                            toil = LordToilName(l)
                        }).ToList()
                    });
                return null;
            }
            var lord = lm.lords[lordIndex];
            if (loadID >= 0 && lord.loadID != loadID)
            {
                err = Fail("Lord at index " + lordIndex + " has loadID " + lord.loadID +
                            ", not the " + loadID + " you asserted. Indices shift; re-read the list.");
                return null;
            }
            return lord;
        }

#if JAWA_GM_TOOLS
        [Tool(
            "jawa/lord_destroy",
            Description =
                "*** REMOVES A LIVE AI GROUP *** Destroy a Lord via LordManager.RemoveLord - " +
                "the public route, not Lord's own Destroy() (private, only reachable through " +
                "RemoveLord's Cleanup chain). This does NOT kill or despawn any pawn; it only " +
                "ends the group's shared state machine, so every member drops back to its " +
                "normal individual think tree (a colonist resumes work, a hostile resumes " +
                "default AI). Address the Lord by lordIndex from jawa/lord_pawn_move " +
                "action=list; pass loadID too and it is checked, because indices shift as " +
                "groups form and die between your list call and this one.",
            ResultDescription =
                "success, the destroyed Lord's index/loadID/faction/job/memberCount, and " +
                "lordsRemaining (map.lordManager.lords.Count after removal).")]
        public static async Task<object> LordDestroy(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Lord index from jawa/lord_pawn_move action=list.", DefaultValue = -1)]
            int lordIndex = -1,
            [ToolParameter(Description = "The Lord's loadID. Optional; if given it must match or the call is refused.", DefaultValue = -1)]
            int loadID = -1)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var lm = map.lordManager;

                object rerr;
                var lord = ResolveLord(lm, lordIndex, loadID, out rerr);
                if (lord == null) return rerr;

                var snapshot = new
                {
                    index = lordIndex,
                    loadID = lord.loadID,
                    faction = lord.faction != null ? lord.faction.Name : null,
                    job = LordJobName(lord),
                    memberCount = lord.ownedPawns != null ? lord.ownedPawns.Count : 0
                };

                try { lm.RemoveLord(lord); }
                catch (Exception e) { return Fail("LordManager.RemoveLord threw " + e.GetType().Name + ": " + e.Message, snapshot); }

                return new
                {
                    success = !lm.lords.Contains(lord),
                    destroyed = snapshot,
                    lordsRemaining = lm.lords.Count,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/lord_set_point",
            Description =
                "Move a DefendPoint Lord's territory centre live, without rebuilding its " +
                "graph - LordToil_DefendPoint.SetDefendPoint(IntVec3), then UpdateAllDuties() " +
                "so every member's PawnDuty is re-issued with the new point immediately " +
                "rather than on the toil's next natural entry. Refuses if the Lord's current " +
                "toil is not a LordToil_DefendPoint (name the actual toil type in the refusal), " +
                "so this cannot be used to silently no-op on a raid or a travelling group.",
            ResultDescription =
                "success, lordIndex, pointBefore, pointAfter (both from FlagLoc, the same " +
                "field the engine itself reads), memberCount, dutiesReissued.")]
        public static async Task<object> LordSetPoint(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Lord index from jawa/lord_pawn_move action=list.", DefaultValue = -1)]
            int lordIndex = -1,
            [ToolParameter(Description = "The Lord's loadID. Optional; if given it must match or the call is refused.", DefaultValue = -1)]
            int loadID = -1,
            [ToolParameter(Description = "New defend point, 'x,z'. Required.")]
            string point = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var lm = map.lordManager;

                object rerr;
                var lord = ResolveLord(lm, lordIndex, loadID, out rerr);
                if (lord == null) return rerr;

                var toil = lord.CurLordToil as LordToil_DefendPoint;
                if (toil == null)
                    return Fail("Lord " + lordIndex + "'s current toil is " + LordToilName(lord) +
                                ", not LordToil_DefendPoint. This tool only retargets a defend point.");

                if (!TryParseCellLocal(point, out var cell, out err)) return Fail(err);
                if (!cell.InBounds(map)) return Fail("Point " + cell + " is outside the map (" + map.Size.x + "x" + map.Size.z + ").");

                IntVec3 before = toil.FlagLoc;
                toil.SetDefendPoint(cell);
                try { lord.CurLordToil.UpdateAllDuties(); }
                catch (Exception e) { return Fail("SetDefendPoint applied but UpdateAllDuties threw " + e.GetType().Name + ": " + e.Message + ". Duties may be stale."); }

                return new
                {
                    success = true,
                    lordIndex,
                    pointBefore = new { x = before.x, z = before.z },
                    pointAfter = new { x = toil.FlagLoc.x, z = toil.FlagLoc.z },
                    memberCount = lord.ownedPawns != null ? lord.ownedPawns.Count : 0,
                    dutiesReissued = true,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/lord_travel_to",
            Description =
                "Move a travelling Lord's destination live - LordToil_Travel.SetDestination" +
                "(IntVec3), then UpdateAllDuties() so DutyDefOf.TravelOrLeave is re-issued to " +
                "every member with the new destination immediately. Refuses if the Lord's " +
                "current toil is not a LordToil_Travel. 🔴 DutyDefOf.TravelOrLeave carries " +
                "LEAVE-THE-MAP behaviour at the destination - this is the correct duty for a " +
                "caravan or exiting group, not a perimeter guard (use jawa/lord_set_point for " +
                "that instead).",
            ResultDescription =
                "success, lordIndex, destBefore, destAfter (both from FlagLoc), memberCount, dutiesReissued.")]
        public static async Task<object> LordTravelTo(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Lord index from jawa/lord_pawn_move action=list.", DefaultValue = -1)]
            int lordIndex = -1,
            [ToolParameter(Description = "The Lord's loadID. Optional; if given it must match or the call is refused.", DefaultValue = -1)]
            int loadID = -1,
            [ToolParameter(Description = "New destination, 'x,z'. Required.")]
            string dest = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                var lm = map.lordManager;

                object rerr;
                var lord = ResolveLord(lm, lordIndex, loadID, out rerr);
                if (lord == null) return rerr;

                var toil = lord.CurLordToil as LordToil_Travel;
                if (toil == null)
                    return Fail("Lord " + lordIndex + "'s current toil is " + LordToilName(lord) +
                                ", not LordToil_Travel. This tool only retargets a travel destination.");

                if (!TryParseCellLocal(dest, out var cell, out err)) return Fail(err);
                if (!cell.InBounds(map)) return Fail("Destination " + cell + " is outside the map (" + map.Size.x + "x" + map.Size.z + ").");

                IntVec3 before = toil.FlagLoc;
                toil.SetDestination(cell);
                try { lord.CurLordToil.UpdateAllDuties(); }
                catch (Exception e) { return Fail("SetDestination applied but UpdateAllDuties threw " + e.GetType().Name + ": " + e.Message + ". Duties may be stale."); }

                return new
                {
                    success = true,
                    lordIndex,
                    destBefore = new { x = before.x, z = before.z },
                    destAfter = new { x = toil.FlagLoc.x, z = toil.FlagLoc.z },
                    memberCount = lord.ownedPawns != null ? lord.ownedPawns.Count : 0,
                    dutiesReissued = true,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/pawns_patrol_route",
            Description =
                "*** ACTS ON THE LIVE COLONY *** Spawn a new Lord running a closed patrol " +
                "circuit: LordMaker.MakeNewLord(faction, new LordJob_Patrol{waypoints=...}, " +
                "map, pawns). One LordToil_Travel per waypoint, ring-transitioned on the " +
                "'TravelArrived' memo LordToil_Travel already fires every 205 ticks once the " +
                "whole group is within range and can reach the next point - no custom Trigger, " +
                "no Harmony. ⚠️ A CYCLIC StateGraph is legal by every check " +
                "StateGraph.ErrorCheck() runs, but no shipped LordJob contains one - this is a " +
                "hypothesis about engine behaviour read from source, NOT a measured fact, " +
                "until a live run proves the ring actually advances instead of stalling on its " +
                "closing transition. 🔴 LordToil_Travel waits for the WHOLE GROUP within 10f " +
                "and reachable before advancing - one blocked or stuck member stalls the " +
                "entire circuit. A pawn already in a Lord is REFUSED, not silently dropped, " +
                "same precheck as jawa/lord_defend_spawn.",
            ResultDescription =
                "success, lordIndex, faction, memberCount (off the new Lord's ownedPawns), " +
                "waypointCount, waypoints, and refused[] naming every pawn NOT added and why.")]
        public static async Task<object> PawnsPatrolRoute(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated pawn ids/names to send on patrol. Required.")]
            string pawns = null,
            [ToolParameter(Description = "FactionDef for the Lord. Empty uses the first resolved pawn's own Faction.")]
            string faction = null,
            [ToolParameter(Description = "Waypoints, '|'-separated 'x,z' pairs, e.g. '10,10|40,10|40,40|10,40'. At least 2 required.")]
            string waypoints = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                List<object> refused;
                var found = ResolveLordCandidates(pawns, map, out refused);
                if (found.Count == 0) return Fail("No pawn resolved to send on patrol. Nothing was created.", new { refused });

                if (string.IsNullOrWhiteSpace(waypoints)) return Fail("Give 'waypoints', '|'-separated 'x,z' pairs.");
                var route = new List<IntVec3>();
                foreach (var raw in waypoints.Split('|'))
                {
                    var tok = raw.Trim();
                    if (tok.Length == 0) continue;
                    if (!TryParseCellLocal(tok, out var cell, out err)) return Fail("Waypoint '" + tok + "': " + err);
                    if (!cell.InBounds(map)) return Fail("Waypoint " + cell + " is outside the map (" + map.Size.x + "x" + map.Size.z + ").");
                    route.Add(cell);
                }
                if (route.Count < 2) return Fail("Need at least 2 waypoints to form a patrol circuit; got " + route.Count + ".");

                Faction fac = null;
                if (!string.IsNullOrWhiteSpace(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = Find.FactionManager.FirstFactionOfDef(fd);
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                }
                else
                {
                    fac = found[0].Faction;
                    if (fac == null) return Fail("No 'faction' given and " + found[0].LabelShortCap + " has no Faction either. Give one explicitly.");
                }

                var job = new LordJob_Patrol { waypoints = route };
                Lord lord;
                try { lord = LordMaker.MakeNewLord(fac, job, map, found); }
                catch (Exception e) { return Fail("LordMaker.MakeNewLord threw " + e.GetType().Name + ": " + e.Message, new { refused }); }

                return new
                {
                    success = true,
                    lordIndex = map.lordManager.lords.IndexOf(lord),
                    loadID = lord.loadID,
                    faction = fac.Name,
                    memberCount = lord.ownedPawns != null ? lord.ownedPawns.Count : 0,
                    waypointCount = route.Count,
                    waypoints = route.Select(c => new { x = c.x, z = c.z }).ToList(),
                    refused,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
#endif
    }
}
