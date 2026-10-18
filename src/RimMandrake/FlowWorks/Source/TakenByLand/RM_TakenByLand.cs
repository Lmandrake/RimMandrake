using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.TakenByLand
{
    // ════════════════════════════════════════════════════════════════════
    // TAKEN_BY_LAND_SERVICE_1 (design pass X-10): "the land takes a pawn and gives them back later" as ONE service. The river's
    // swept-away (FlowWorks) and the dune gale's carry (Stillsand) were the same thing built twice: a hold, a letter, a return.
    // A taker registers a RM_TakenPolicy under a kind ("river", "gale"); RM_TakenByLand.Take(pawn, kind, ...) does the rest:
    // removes the pawn (the policy's way), holds it as a world pawn, writes the taker's letter, leaves a ground trace where it
    // was taken (so no one vanishes without a readable sign), and RM_WorldComponent_TakenByLand returns it later with a second
    // letter. The old per-taker books (RM_WorldComponent_SweptAway, RM_GameComponent_GaleCarried) stay only to drain records saved
    // before this service; delete them once no save holds one.
    // The trace is the kit's RM_Filth_DragMark where Creature Behaviors is loaded, until EVENT_TRACE_PROPS_LIBRARY_1 lands a real prop.
    // ════════════════════════════════════════════════════════════════════

    public class RM_TakenRecord : IExposable
    {
        public Pawn pawn;
        public string kind;
        public int mapId = -1;
        public int takenTick = -1;
        public int returnTick;
        public bool wasPlayer;
        public IntVec3 origin;
        /// <summary>The taker's direction of travel (the gale's wind); zero for a taker with none.</summary>
        public IntVec3 dir;
        public float aliveChance = 1f;
        // RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS: who the pawn belonged to when taken, so it comes back the same.
        public bool captured;
        public Faction faction;
        public Faction hostFaction;
        public int guestStatus = -1;

        public void ExposeData()
        {
            Scribe_References.Look(ref pawn, "pawn", true);
            Scribe_Values.Look(ref kind, "kind");
            Scribe_Values.Look(ref mapId, "mapId", -1);
            Scribe_Values.Look(ref takenTick, "takenTick", -1);
            Scribe_Values.Look(ref returnTick, "returnTick");
            Scribe_Values.Look(ref wasPlayer, "wasPlayer");
            Scribe_Values.Look(ref origin, "origin");
            Scribe_Values.Look(ref dir, "dir");
            Scribe_Values.Look(ref aliveChance, "aliveChance", 1f);
            Scribe_Values.Look(ref captured, "captured");
            Scribe_References.Look(ref faction, "faction");
            Scribe_References.Look(ref hostFaction, "hostFaction");
            Scribe_Values.Look(ref guestStatus, "guestStatus", -1);
        }
    }

    /// <summary>What differs between takers. Defaults are the river's: hold only your own, back alive on a random edge.</summary>
    public abstract class RM_TakenPolicy
    {
        public abstract string Kind { get; }

        /// <summary>Does the service hold this pawn for a return? Default: only the player's (and the player's prisoners).</summary>
        public virtual bool Holds(Pawn p) => (p.Faction != null && p.Faction.IsPlayer) || (p.HostFaction != null && p.HostFaction.IsPlayer);

        /// <summary>Days until it is due back.</summary>
        public abstract float RollDays();

        /// <summary>Chance it comes back alive (1 = always).</summary>
        public virtual float AliveChance => 1f;

        /// <summary>Take the pawn off the map and into the world's keeping. Default: despawn + keep forever.</summary>
        public virtual void Remove(Pawn p, Map map, RM_TakenRecord r)
        {
            p.DeSpawn();
            Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
        }

        /// <summary>A pawn this policy does not hold: leave a readable sign and let the world have it.</summary>
        public virtual void TakeStranger(Pawn p, Map map)
        {
            Messages.Message(p.LabelShortCap + " was taken off the map.", new LookTargets(p.PositionHeld, map), MessageTypeDefOf.NeutralEvent);
            p.DeSpawn();
            Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Decide);
        }

        /// <summary>Where it comes back in. Default: a standable, dry edge cell.</summary>
        public virtual IntVec3 PickReturnCell(RM_TakenRecord r, Map map)
        {
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && !c.GetTerrain(map).IsWater, map, CellFinder.EdgeRoadChance_Neutral, out IntVec3 cell)
                && !CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map), map, 0f, out cell))
            {
                return IntVec3.Invalid;
            }
            return cell;
        }

        public virtual void AfterReturn(RM_TakenRecord r, Pawn p) { }

        // Letters. Return null for "no letter".
        public abstract void TakenLetter(RM_TakenRecord r, Pawn p, Map map, float days, out string label, out string text, out LetterDef def);
        public abstract void ReturnedLetter(RM_TakenRecord r, Pawn p, Pawn target, bool dead, out string label, out string text, out LetterDef def);
        public virtual void LostLetter(RM_TakenRecord r, string name, bool mapGone, out string label, out string text)
        {
            label = "Lost: " + name;
            text = name + " was taken and never given back" + (mapGone ? "; the map they were taken from is gone." : ".");
        }
        public virtual void DiedLetter(RM_TakenRecord r, Pawn p, out string label, out string text)
        {
            label = "Lost: " + p.LabelShortCap;
            text = p.LabelShortCap + " died out past the edge. The land kept the body.";
        }
    }

    public static class RM_TakenByLand
    {
        private static readonly Dictionary<string, RM_TakenPolicy> policies = new Dictionary<string, RM_TakenPolicy>();

        public static void Register(RM_TakenPolicy p) { policies[p.Kind] = p; }
        public static RM_TakenPolicy PolicyFor(string kind) { policies.TryGetValue(kind ?? "", out RM_TakenPolicy p); return p; }

        /// <summary>Take a spawned pawn on its map. Returns true when the service now holds it for a return.</summary>
        public static bool Take(Pawn p, string kind, IntVec3 dir = default(IntVec3), float days = -1f, float aliveChance = -1f)
        {
            RM_TakenPolicy policy = PolicyFor(kind);
            Map map = p?.Map;
            if (policy == null || map == null || !p.Spawned) return false;
            IntVec3 origin = p.Position;
            RM_WorldComponent_TakenByLand comp = Find.World?.GetComponent<RM_WorldComponent_TakenByLand>();
            if (!policy.Holds(p) || comp == null)
            {
                if (policy.Holds(p) && comp == null) return false;   // cannot hold them: leave the pawn rather than lose them
                LeaveTrace(map, origin);
                policy.TakeStranger(p, map);
                return false;
            }
            if (days < 0f) days = policy.RollDays();
            var r = new RM_TakenRecord
            {
                pawn = p,
                kind = kind,
                mapId = map.uniqueID,
                takenTick = Find.TickManager.TicksGame,
                returnTick = RM_TakenByLandKernel.ReturnTick(Find.TickManager.TicksGame, days, GenDate.TicksPerDay),
                wasPlayer = p.Faction != null && p.Faction.IsPlayer,
                origin = origin,
                dir = dir,
                aliveChance = aliveChance >= 0f ? aliveChance : policy.AliveChance,
            };
            Capture(r, p);
            // Held BEFORE the taker removes it: vanilla's faction swap (Pawn.Notify_PassedToWorld) fires inside PassToWorld.
            Held.Hold(p.thingIDNumber);
            try { policy.Remove(p, map, r); }
            catch
            {
                if (p.Spawned) Held.Release(p.thingIDNumber);   // not taken after all
                throw;
            }
            comp.Add(r);
            LeaveTrace(map, origin);
            policy.TakenLetter(r, p, map, days, out string label, out string text, out LetterDef def);
            if (label != null) Find.LetterStack.ReceiveLetter(label, text, def ?? LetterDefOf.NegativeEvent, new LookTargets(new TargetInfo(origin, map)));
            return true;
        }

        // ── RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS ─────────────────────────────────────────────────────────────────
        /// <summary>The pawns held right now (thingIDNumber). RM_Patch_TakenPawnNotFree reads it; the book rebuilds it on load.</summary>
        public static readonly RM_TakenHoldSet Held = new RM_TakenHoldSet();

        public static bool IsHeld(Pawn p) => p != null && Held.Contains(p.thingIDNumber);

        public static RM_TakenByLandKernel.TakenState StateOf(Pawn p)
        {
            Faction host = p.guest?.HostFaction;
            int gs = -1;
            if (p.guest != null && (host != null || p.guest.IsSlave)) gs = (int)p.guest.GuestStatus;
            return new RM_TakenByLandKernel.TakenState(p.Faction?.loadID ?? -1, host?.loadID ?? -1, gs);
        }

        public static RM_TakenByLandKernel.TakenState StateOf(RM_TakenRecord r) =>
            new RM_TakenByLandKernel.TakenState(r.faction?.loadID ?? -1, r.hostFaction?.loadID ?? -1, r.guestStatus);

        public static void Capture(RM_TakenRecord r, Pawn p)
        {
            r.captured = true;
            r.faction = p.Faction;
            r.hostFaction = p.guest?.HostFaction;
            r.guestStatus = StateOf(p).guestStatus;
        }

        /// <summary>Put the returning pawn back in the state it was taken in (call before it spawns). Records saved before
        /// the capture existed only know wasPlayer: such a pawn is made the player's again. Returns what was restored.</summary>
        public static RM_TakenByLandKernel.RestoreNeed Restore(RM_TakenRecord r, Pawn p)
        {
            if (r == null || p == null || p.Dead) return RM_TakenByLandKernel.RestoreNeed.None;
            if (!r.captured)
            {
                if (r.wasPlayer && p.Faction != Faction.OfPlayer)
                {
                    p.SetFaction(Faction.OfPlayer);
                    return RM_TakenByLandKernel.RestoreNeed.Faction;
                }
                return RM_TakenByLandKernel.RestoreNeed.None;
            }
            RM_TakenByLandKernel.RestoreNeed need = RM_TakenByLandKernel.NeedsRestore(StateOf(r), StateOf(p));
            if ((need & RM_TakenByLandKernel.RestoreNeed.Faction) != 0 && p.Faction != r.faction)
            {
                p.SetFaction(r.faction);
            }
            if ((need & RM_TakenByLandKernel.RestoreNeed.Guest) != 0 && p.guest != null
                && RM_TakenByLandKernel.NeedsRestore(StateOf(r), StateOf(p)) != RM_TakenByLandKernel.RestoreNeed.None)
            {
                if (r.guestStatus < 0) p.guest.SetGuestStatus(null);
                else if (r.guestStatus == (int)GuestStatus.Slave) p.guest.SetGuestStatus(r.faction, GuestStatus.Slave);
                else p.guest.SetGuestStatus(r.hostFaction, (GuestStatus)r.guestStatus);
            }
            if (need != RM_TakenByLandKernel.RestoreNeed.None)
            {
                Log.Warning("[FlowWorks] taken-by-land: " + p + " came back changed (" + StateOf(p) + " vs taken " + StateOf(r)
                    + "); restored " + need + ".");
            }
            return need;
        }

        // ── SWEEP_PRISONER_RETURN ───────────────────────────────────────────────────────────────────────────────────
        /// <summary>When each pawn was given back; RM_Patch_ReturnedPrisonerNoEscape and RM_Patch_ReturnedPrisonerLost read it.</summary>
        public static readonly RM_TakenReturnGuard Returned = new RM_TakenReturnGuard();

        /// <summary>The vanilla escape's open-door search from a district (JobGiver_PrisonerEscape: 25 regions, free-passage doors).</summary>
        public static bool OpenPathToEdge(District d)
        {
            if (d == null || d.Regions.Count == 0) return false;
            bool found = false;
            RegionTraverser.BreadthFirstTraverse(d.Regions[0], (Region from, Region reg) => reg.door == null || reg.door.FreePassage,
                reg => { if (reg.District.TouchesMapEdge) { found = true; return true; } return false; }, 25);
            return found;
        }

        private static RM_TakenByLandKernel.ReturnCandidate Candidate(RM_TakenByLandKernel.PrisonerSpot tier, IntVec3 c, Map map)
        {
            bool standable = c.InBounds(map) && c.Standable(map);
            District d = standable ? c.GetDistrict(map) : null;
            bool touches = d == null || d.TouchesMapEdge;
            return new RM_TakenByLandKernel.ReturnCandidate(tier, standable && d != null, c.OnEdge(map), touches,
                !touches && OpenPathToEdge(d));
        }

        /// <summary>A cell that holds a returning prisoner: its own bed, a free prisoner bed, a prison cell, any enclosed room,
        /// else an interior cell off the edge near the centre (secure = false). Invalid when the map has no standable cell.</summary>
        public static IntVec3 PickPrisonerReturnCell(Pawn p, Map map, out bool secure)
        {
            var cells = new List<IntVec3>();
            var cands = new List<RM_TakenByLandKernel.ReturnCandidate>();
            void Add(RM_TakenByLandKernel.PrisonerSpot tier, IntVec3 c)
            {
                if (!c.IsValid || cells.Count >= 400) return;
                cells.Add(c);
                cands.Add(Candidate(tier, c, map));
            }
            Building_Bed own = p.ownership?.OwnedBed;
            if (own != null && own.Spawned && own.Map == map && own.ForPrisoners) Add(RM_TakenByLandKernel.PrisonerSpot.OwnedBed, own.Position);
            foreach (Building_Bed b in map.listerBuildings.AllBuildingsColonistOfClass<Building_Bed>())
                if (b != own && b.ForPrisoners && !b.Medical && b.AnyUnoccupiedSleepingSlot) Add(RM_TakenByLandKernel.PrisonerSpot.PrisonerBed, b.Position);
            IReadOnlyList<Room> rooms = map.regionGrid.AllRooms;
            for (int pass = 0; pass < 2; pass++)
            {
                for (int i = 0; i < rooms.Count; i++)
                {
                    Room room = rooms[i];
                    if (room == null || room.TouchesMapEdge || (pass == 0) != room.IsPrisonCell || (pass == 1 && !room.ProperRoom)) continue;
                    int n = 0;
                    foreach (IntVec3 c in room.Cells)
                    {
                        if (!c.Standable(map)) continue;
                        Add(pass == 0 ? RM_TakenByLandKernel.PrisonerSpot.PrisonCell : RM_TakenByLandKernel.PrisonerSpot.EnclosedRoom, c);
                        if (++n >= 2) break;
                    }
                }
            }
            if (CellFinder.TryFindRandomCellNear(map.Center, map, Mathf.Max(8, Mathf.Min(map.Size.x, map.Size.z) / 3),
                    c => c.Standable(map) && !c.OnEdge(map) && !c.GetTerrain(map).IsWater, out IntVec3 inner))
            {
                Add(RM_TakenByLandKernel.PrisonerSpot.Interior, inner);
            }
            int k = RM_TakenByLandKernel.PickPrisonerReturn(cands, out secure);
            return k >= 0 ? cells[k] : IntVec3.Invalid;
        }

        /// <summary>Session counter for a dev/bridge read: ground traces left. Never saved.</summary>
        public static int TracesLeft;

        /// <summary>The ground trace at the spot a pawn was taken (nearest cell within 2 that takes filth).</summary>
        public static void LeaveTrace(Map map, IntVec3 at)
        {
            if (!RimMandrake.FlowWorks.Rivers.RM_RiversSettings.takenByLandTraceEnabled || map == null || !at.IsValid) return;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_DragMark");
            if (def == null) return;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(at, 2f, true))
            {
                if (c.InBounds(map) && FilthMaker.TryMakeFilth(c, map, def))
                {
                    TracesLeft++;
                    return;
                }
            }
        }
    }

    public class RM_WorldComponent_TakenByLand : WorldComponent
    {
        public const int ScanInterval = 250;
        private List<RM_TakenRecord> records = new List<RM_TakenRecord>();

        public RM_WorldComponent_TakenByLand(World world) : base(world) { RM_TakenByLand.Held.Clear(); RM_TakenByLand.Returned.Clear(); }

        public int PendingCount => records.Count;
        public int PendingOfKind(string kind) { int n = 0; foreach (RM_TakenRecord r in records) if (r.kind == kind) n++; return n; }

        public void Add(RM_TakenRecord r) { records.Add(r); }

        /// <summary>The held set from the book (load; also a dev read). Only pawns still waiting in the world's keeping.</summary>
        public void RebuildHeld()
        {
            var ids = new List<int>();
            foreach (RM_TakenRecord r in records)
                if (r?.pawn != null && !r.pawn.Destroyed && !r.pawn.Spawned) ids.Add(r.pawn.thingIDNumber);
            RM_TakenByLand.Held.Rebuild(ids);
        }

        /// <summary>Dev/proof read: every held pawn's state now vs taken ("id:Faction" pairs).</summary>
        public string DescribeHeld()
        {
            var sb = new System.Text.StringBuilder();
            foreach (RM_TakenRecord r in records)
            {
                if (r?.pawn == null) continue;
                sb.Append(' ').Append(r.pawn.ThingID).Append(':').Append(r.pawn.Faction?.def?.defName ?? "none")
                  .Append(r.faction == r.pawn.Faction ? "" : "(taken as " + (r.faction?.def?.defName ?? "none") + ")")
                  .Append(RM_TakenByLand.IsHeld(r.pawn) ? "" : "[NOT HELD]");
            }
            return sb.ToString();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref records, "rmTakenByLand", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                records = records ?? new List<RM_TakenRecord>();
                records.RemoveAll(r => r == null);
                RebuildHeld();
            }
        }

        public override void WorldComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (!RM_TakenByLandKernel.ShouldScan(records.Count, now, ScanInterval)) return;
            foreach (RM_TakenRecord r in RM_TakenByLandKernel.TakeWhere(records, c => RM_TakenByLandKernel.IsDue(c.returnTick, now)))
            {
                if (!SafeReturn(r)) records.Add(r);   // nowhere to walk home to yet: keep waiting
            }
        }

        /// <summary>Return every record taken from this map by an earlier event (a storm's end). Returns how many came back.</summary>
        public int ReturnEarlierOnMap(string kind, Map map, int eventStartTick)
        {
            int n = 0;
            foreach (RM_TakenRecord r in RM_TakenByLandKernel.TakeWhere(records,
                c => c.kind == kind && RM_TakenByLandKernel.EarlierEventOnMap(c.mapId, c.takenTick, map.uniqueID, eventStartTick)))
            {
                if (SafeReturn(r)) n++; else records.Add(r);
            }
            return n;
        }

        /// <summary>Bring everything back now (dev proof hook).</summary>
        public void ReturnAllNow()
        {
            foreach (RM_TakenRecord r in RM_TakenByLandKernel.TakeWhere(records, c => true))
            {
                if (!SafeReturn(r)) records.Add(r);
            }
        }

        private static bool SafeReturn(RM_TakenRecord r)
        {
            try { return Return(r); }
            catch (Exception e)
            {
                Log.Error("[FlowWorks] taken-by-land return of " + r?.pawn + " failed: " + e);
                // Return() takes the pawn out of the world's keeping before it spawns it. If it threw in between, put the pawn back
                // and retry in an hour, so a throw never leaves a pawn held by nothing (no pawn vanishes without a sign).
                Pawn p = r?.pawn;
                if (p != null && !p.Destroyed && !p.Discarded && !p.Spawned)
                {
                    RM_TakenByLand.Held.Hold(p.thingIDNumber);
                    if (!Find.WorldPawns.Contains(p)) Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
                    r.returnTick = Find.TickManager.TicksGame + GenDate.TicksPerHour;
                    return false;
                }
                return true;
            }
        }

        /// <summary>True when the record is finished with (returned or lost); false to keep it for later.</summary>
        private static bool Return(RM_TakenRecord r)
        {
            RM_TakenPolicy policy = RM_TakenByLand.PolicyFor(r.kind);
            if (policy == null) return false;   // the taker's mod is not loaded this session: hold on
            Pawn p = r.pawn;
            Map map = null;
            foreach (Map m in Find.Maps) if (m.uniqueID == r.mapId) map = m;
            if (map == null) map = SurfaceHomeMap();
            bool missing = p == null || p.Destroyed || p.Discarded;
            if (map == null && !missing) return false;   // nowhere to walk home to yet; keep waiting
            if (p != null && Find.WorldPawns.Contains(p)) Find.WorldPawns.RemovePawn(p);
            if (p != null) RM_TakenByLand.Held.Release(p.thingIDNumber);
            if (p != null && p.Spawned)
            {
                // Something else put the pawn on a map while it was held (it should not be able to now): take it back off
                // so it walks home from the edge like the rest, instead of GenSpawn erroring on a spawned pawn.
                Log.Warning("[FlowWorks] taken-by-land: " + p + " was spawned on " + p.Map + " while held; bringing it home.");
                p.DeSpawn();
            }
            bool alive = !missing && !p.Dead && Rand.Chance(r.aliveChance);
            TakenOutcome outcome = RM_TakenByLandKernel.Decide(missing, map == null, !missing && p.Dead, alive);
            if (outcome == TakenOutcome.LostMissing)
            {
                policy.LostLetter(r, p?.LabelShortCap ?? "a body", map == null, out string l1, out string t1);
                if (l1 != null) Find.LetterStack.ReceiveLetter(l1, t1, LetterDefOf.NeutralEvent);
                return true;
            }
            if (outcome == TakenOutcome.LostDead)
            {
                policy.DiedLetter(r, p, out string l2, out string t2);
                if (l2 != null) Find.LetterStack.ReceiveLetter(l2, t2, LetterDefOf.NeutralEvent);
                return true;
            }
            RM_TakenByLand.Restore(r, p);   // the same pawn, back as whose it was (colonist, prisoner, slave, guest, tamed)
            IntVec3 cell = policy.PickReturnCell(r, map);
            if (!cell.IsValid) cell = map.Center;
            // SWEEP_PRISONER_RETURN: a prisoner on the policy's edge cell escapes off it at once (vanilla); it comes back to a
            // cell that holds it, and vanilla's escape is off for the guard hour.
            bool unheldPrisoner = false;
            if (p.IsPrisonerOfColony)
            {
                IntVec3 safe = RM_TakenByLand.PickPrisonerReturnCell(p, map, out bool secure);
                if (safe.IsValid) cell = safe;
                unheldPrisoner = !secure;
            }
            RM_TakenByLand.Returned.Prune(Find.TickManager.TicksGame);
            RM_TakenByLand.Returned.Mark(p.thingIDNumber, Find.TickManager.TicksGame);
            GenSpawn.Spawn(p, cell, map, WipeMode.VanishOrMoveAside);
            policy.AfterReturn(r, p);
            if (unheldPrisoner && !p.Dead)
            {
                Messages.Message(p.LabelShortCap + " is back but no prison cell can hold " + p.ProObj() + ": give " + p.ProObj()
                    + " a cell within the hour or " + p.ProSubj() + " will try to escape.", p, MessageTypeDefOf.CautionInput);
            }
            if (outcome == TakenOutcome.SpawnThenKill && !p.Dead) p.Kill(null);
            Thing target = p.Dead ? (Thing)p.Corpse ?? p : p;
            policy.ReturnedLetter(r, p, null, p.Dead, out string label, out string text, out LetterDef def);
            if (label != null) Find.LetterStack.ReceiveLetter(label, text, def ?? (p.Dead ? LetterDefOf.Death : LetterDefOf.PositiveEvent), target);
            return true;
        }

        // SURFACE_HOME_MAP_HELPER_1: never the sea floor (ship is the only way down).
        private static Map SurfaceHomeMap()
        {
            foreach (Map m in Find.Maps)
                if (m.IsPlayerHome && !(m.Tile.Valid && m.Tile.Layer?.Def?.defName == "RM_SeabedLayer")) return m;
            return null;
        }
    }

    /// <summary>The river's swept-away, as a policy: only your own are held, back alive on a dry edge in 1-3 days.</summary>
    public class RM_RiverTakenPolicy : RM_TakenPolicy
    {
        public override string Kind => "river";

        public override float RollDays()
        {
            float min = Rivers.RM_RiversSettings.washedAwayMinDays;
            float max = Mathf.Max(min, Rivers.RM_RiversSettings.washedAwayMaxDays);
            return Rand.Range(min, max);
        }

        public override void TakeStranger(Pawn p, Map map)
        {
            Messages.Message(p.LabelShortCap + " was swept off the map by the river.", new LookTargets(p.PositionHeld, map), MessageTypeDefOf.NeutralEvent);
            p.DeSpawn();
            Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Decide);
        }

        public override void TakenLetter(RM_TakenRecord r, Pawn p, Map map, float days, out string label, out string text, out LetterDef def)
        {
            label = "Swept away: " + p.LabelShortCap;
            text = p.LabelShortCap + " was carried off the map by the river's current. " + p.ProSubj().CapitalizeFirst()
                 + " will make " + p.Possessive() + " way back on foot in about " + days.ToString("F1") + " days, bruised but alive. Wait for them.";
            def = LetterDefOf.NegativeEvent;
        }

        public override void ReturnedLetter(RM_TakenRecord r, Pawn p, Pawn target, bool dead, out string label, out string text, out LetterDef def)
        {
            label = "Back from the river: " + p.LabelShortCap;
            text = p.LabelShortCap + " has walked back after being washed away downstream.";
            def = LetterDefOf.PositiveEvent;
        }
    }

    /// <summary>RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS: a pawn the service holds is not a Free world pawn. Free is what lets
    /// vanilla hand a player's pawn to a random NPC faction as it enters the world (Pawn.Notify_PassedToWorld), redress it
    /// into a raid or trader group (PawnGenerator), or pick it for a quest. ReservedByQuest is vanilla's "spoken for".</summary>
    [RimMandrake.Shared.PatchFeature("Pawns taken by the land (river, gale) stay yours while away")]
    [HarmonyLib.HarmonyPatch(typeof(WorldPawns), nameof(WorldPawns.GetSituation))]
    public static class RM_Patch_TakenPawnNotFree
    {
        public static void Postfix(Pawn p, ref WorldPawnSituation __result)
        {
            if (RM_TakenByLandKernel.ShieldFromFree(__result == WorldPawnSituation.Free, RM_TakenByLand.IsHeld(p)))
            {
                __result = WorldPawnSituation.ReservedByQuest;
            }
        }
    }

    /// <summary>SWEEP_PRISONER_FIX_NEVER_RETURNS: a prisoner (or slave) of the player leaving the map from a cell the river's
    /// current carries pawns on is swept, not free: vanilla's escape (JobGiver_PrisonerEscape exits at once from an edge
    /// cell) would hand it to the world unbooked, and it never came back. The rule is RM_TakenByLandKernel.ExitIntoCurrentIsSwept.</summary>
    // Label only: a failed patch must not switch washOffMapEdge off (the colonists' sweep does not need this patch).
    [RimMandrake.Shared.PatchFeature("Washed off the map at the edge: an escape into the current is a sweep")]
    [HarmonyLib.HarmonyPatch(typeof(Pawn), nameof(Pawn.ExitMap))]
    public static class RM_Patch_EscapeIntoCurrentIsSwept
    {
        public static bool Prefix(Pawn __instance)
        {
            Pawn p = __instance;
            if (p == null || !p.Spawned || p.Map == null || p.Dead || !(p.IsPrisonerOfColony || p.IsSlaveOfColony)) return true;
            Rivers.RM_MapComponent_RiverCurrent cur = p.Map.GetComponent<Rivers.RM_MapComponent_RiverCurrent>();
            bool lane = cur != null && cur.HasCurrent(p.Position) && cur.IsCarried(p);
            bool caravan = p.teleporting || p.IsCaravanMember();
            if (!RM_TakenByLandKernel.ExitIntoCurrentIsSwept(Rivers.RM_RiversSettings.washOffMapEdge, Rivers.RM_RiversSettings.CurrentActive,
                    true, p.guest != null && p.guest.Released, lane, caravan)) return true;
            return !RM_TakenByLand.Take(p, "river");   // taken: vanilla's escape never runs
        }
    }

    /// <summary>SWEEP_PRISONER_RETURN: vanilla's escape is off for the guard hour after a return (live day 4: back on an edge
    /// cell, it walked off within 10 ticks). Rule: RM_TakenReturnGuard.InGuard (RM_TakenByLandKernel.ReturnGuardTicks).</summary>
    [RimMandrake.Shared.PatchFeature("A prisoner the land gave back does not escape in its first hour home")]
    [HarmonyLib.HarmonyPatch(typeof(JobGiver_PrisonerEscape), "TryGiveJob")]
    public static class RM_Patch_ReturnedPrisonerNoEscape
    {
        public static bool Prefix(Pawn pawn, ref Verse.AI.Job __result)
        {
            if (pawn == null || !RM_TakenByLand.Returned.InGuard(pawn.thingIDNumber, Find.TickManager.TicksGame)) return true;
            __result = null;
            return false;
        }
    }

    /// <summary>SWEEP_PRISONER_RETURN safety net: a returned prisoner or slave that leaves the map anyway (not swept, so not
    /// held) gets a letter, so it is never lost without a sign. Rule: RM_TakenByLandKernel.ExitIsLostReturn.</summary>
    [RimMandrake.Shared.PatchFeature("A returned prisoner who slips away off the map gets a letter")]
    [HarmonyLib.HarmonyPatch(typeof(Pawn), nameof(Pawn.ExitMap))]
    public static class RM_Patch_ReturnedPrisonerLost
    {
        public static void Prefix(Pawn __instance, out bool __state)
        {
            Pawn p = __instance;
            __state = p != null && p.Spawned && !p.Dead && RM_TakenByLandKernel.ExitIsLostReturn(
                p.IsPrisonerOfColony || p.IsSlaveOfColony, p.guest != null && p.guest.Released, p.teleporting || p.IsCaravanMember(),
                RM_TakenByLand.Returned.Recent(p.thingIDNumber, Find.TickManager.TicksGame));
        }

        public static void Postfix(Pawn __instance, bool __state)
        {
            Pawn p = __instance;
            if (!__state || p == null || p.Spawned || RM_TakenByLand.IsHeld(p)) return;   // swept again (held) or never left
            Find.LetterStack.ReceiveLetter("Escaped: " + p.LabelShortCap,
                p.LabelShortCap + " came home after being taken by the land, then slipped away off the map before anyone held "
                + p.ProObj() + ". " + p.ProSubj().CapitalizeFirst() + " is gone.", LetterDefOf.NegativeEvent);
        }
    }

    [StaticConstructorOnStartup]
    internal static class RM_TakenByLandStartup
    {
        static RM_TakenByLandStartup() { RM_TakenByLand.Register(new RM_RiverTakenPolicy()); }
    }
}
