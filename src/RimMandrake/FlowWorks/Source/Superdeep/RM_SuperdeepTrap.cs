using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SUPERDEEP_HOLDER_RETIRE_1 — a pit is a canal cell dug to SUPERDEEP (D = 4) and nothing
	/// else. Owner, 2026-10-02: <i>"There's no 'pit' as a special thing, it's just a
	/// channel/canal dig."</i> The retired RM_SuperdeepPit holder despawned a captured pawn
	/// into a container; here the pawn STAYS SPAWNED on terrain and the trap is a grid rule.
	///
	/// HELD (per pawn, per cell, re-read live) = capture + ladder settings on, the cell's DUG
	/// depth is 4, the pawn's faction is captured (own-faction carve-out, or it jumped in), it
	/// is not flying, no ladder in the cell lets THIS pawn climb (lowered, prison-door rule:
	/// RM_LadderRules.LadderLetsOut), and some W×W square of D = 4 cells contains
	/// the cell, W = RM_PitTrapMath.RequiredWidth(BodySize) (owner Q4: "the pit has to be as
	/// wide as the creature to hold it. Otherwise it gets out.").
	///
	/// SEAMS (SUPERDEEP_SEAM_MEASURE_1, decompiled 1.6):
	///   • hard per-move floor: prefix on Pawn_PathFollower.TryEnterNextPathCell — pawn.Position
	///     is still the cell being LEFT and nextCell the target; a held pawn may step only onto
	///     another D = 4 cell.
	///   • reachability veto: postfix on the public Reachability.CanReach(IntVec3,
	///     LocalTargetInfo, PathEndMode, TraverseParms) every overload funnels into, OUTSIDE its
	///     region-keyed cache (it only narrows true → false), plus CanReachMapEdge. A trapped
	///     pawn reaches only its own D = 4 component (and Touch targets adjacent to it). It is
	///     "trapped" only if it is held on EVERY cell of that component — a ladder cell or a
	///     too-narrow arm it can walk to is a way out, so no veto then.
	/// </summary>
	public static class RM_SuperdeepTrap
	{
		/// <summary>Spikes hook (CANAL_BOTTOM_SPIKES_1): raised after fall damage on every
		/// descent into a D = 4 cell.</summary>
		public static event Action<Pawn, IntVec3> PitDescent;

		private const int MaxRegionCells = 4000;

		public static RM_MapComponent_Excavation EngineOf(Map map)
		{
			// Cached: this sits under the CanReach / PawnCanOpen / TryEnterNextPathCell
			// hooks, ahead of the SuperdeepCellCount early-out, and GetComponent walks
			// every map component on every call.
			return RM_SuperdeepShooting.EngineFor(map);
		}

		public static bool RuleOn =>
			RimMandrakeFlowWorksSettings.superdeepCaptureEnabled
			&& RimMandrakeFlowWorksSettings.ladderRequiredToExitEnabled;

		/// <summary>Whose fall the hole takes: everyone but the player's own faction (Mod
		/// Setting carve-out, so a builder can place the ladder), plus anyone who jumped.</summary>
		public static bool Captures(Pawn p)
		{
			if (p == null)
			{
				return false;
			}
			if (RimMandrakeFlowWorksSettings.superdeepCapturesOwnFaction)
			{
				return true;
			}
			if (p.Faction != Faction.OfPlayer)
			{
				return true;
			}
			RM_MapComponent_Excavation eng = EngineOf(p.MapHeld);
			return eng != null && eng.SuperdeepTrap.IsJumper(p);
		}

		public static int RequiredWidth(Pawn p)
		{
			return p == null ? 1 : RM_PitTrapMath.RequiredWidth(p.BodySize,
				RimMandrakeFlowWorksSettings.pitWidthBodySizeMultiplier);
		}

		public static int MeasuredPitWidth(Map map, IntVec3 c)
		{
			RM_MapComponent_Excavation eng = EngineOf(map);
			if (eng == null)
			{
				return 0;
			}
			return RM_PitTrapMath.MeasuredPitWidth((x, z) => eng.IsSuperdeepExcavation(new IntVec3(x, 0, z)), c.x, c.z);
		}

		/// <summary>Relative rule's "too big for it": in a pocket of its band, but no square of that pocket as wide as it is
		/// contains its cell.</summary>
		public static bool InOwnPocketTooNarrow(Pawn p)
		{
			// Width 1 fits every pocket cell: skip the grid (the step floor asks this on every step).
			if (p == null || !p.Spawned || RequiredWidth(p) <= 1)
			{
				return false;
			}
			int k = RM_PocketGrid.ClimbLimitOf(p);
			RM_PocketGrid g = RM_PocketGrid.For(p.Map);
			int comp = g.ComponentOf(k, p.Position);
			return g.ComponentIsPocket(k, comp) && g.MeasuredWidth(k, p.Position) < RequiredWidth(p);
		}

		public static bool IsHeld(Pawn p)
		{
			return p != null && p.Spawned && IsHeldAt(p, p.Position);
		}

		/// <summary>The trap predicate at an arbitrary cell (the pawn need not stand there).</summary>
		public static bool IsHeldAt(Pawn p, IntVec3 c)
		{
			if (p == null || !p.Spawned)
			{
				return false;
			}
			RM_MapComponent_Excavation eng = EngineOf(p.Map);
			if (RM_PocketGrid.Relative)
			{
				return IsHeldAtRelative(p, c, eng);
			}
			if (eng == null || eng.SuperdeepCellCount == 0)
			{
				return false;
			}
			bool onD4 = eng.IsSuperdeepExcavation(c);
			// PIT_COVER_FALL_REWIRE_1: an intact cover is ground until it gives way.
			if (!onD4 || !RuleOn || Pits.RM_PitCoverUtility.IsCovered(p.Map, c))
			{
				return false;
			}
			int w = RequiredWidth(p);
			bool wide = RM_PitTrapMath.PitWidthAt((x, z) => eng.IsSuperdeepExcavation(new IntVec3(x, 0, z)), c.x, c.z, w);
			return RM_PitTrapMath.Held(true, true, Captures(p), p.Flying,
				RM_LadderRules.LadderLetsOut(p.Map, c, p), wide);
		}

		// ── PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP: the relative rule (design §8.1-8.3) ──────────

		/// <summary>Is any cell dug, or a dry pond bed (POND_BED step 2) (the relative rule's early-out, as SuperdeepCellCount is the absolute rule's)?</summary>
		public static bool AnyHole(RM_MapComponent_Excavation eng)
		{
			return eng != null && (RM_PocketGrid.Relative ? eng.ClimbCellCount > 0 : eng.SuperdeepCellCount > 0);
		}

		/// <summary>The depth a step is judged on: ClimbDepthAt, an intact cover read as ground (0).</summary>
		public static int StepDepthAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			if (eng == null || !c.InBounds(map))
			{
				return 0;
			}
			int d = eng.ClimbDepthAt(c);
			return d > 0 && Pits.RM_PitCoverUtility.IsCovered(map, c) ? 0 : d;
		}

		/// <summary>Held here under the relative rule: in a pocket of this pawn's climb band, captured, not a flyer, no usable
		/// ladder in this cell, and some W×W square of the pocket's cells contains the cell.</summary>
		private static bool IsHeldAtRelative(Pawn p, IntVec3 c, RM_MapComponent_Excavation eng)
		{
			if (!RuleOn || eng == null || eng.ClimbCellCount == 0 || eng.ClimbDepthAt(c) == 0
				|| Pits.RM_PitCoverUtility.IsCovered(p.Map, c))
			{
				return false;
			}
			int k = RM_PocketGrid.ClimbLimitOf(p);
			if (RM_PocketGridMath.BandFor(k, RM_PocketGrid.BandCount) == 0)
			{
				return false;
			}
			RM_PocketGrid g = RM_PocketGrid.For(p.Map);
			int comp = g.ComponentOf(k, c);
			bool inPocket = g.ComponentIsPocket(k, comp);
			if (!inPocket)
			{
				return false;
			}
			return RM_PitTrapMath.HeldRelative(true, inPocket, Captures(p), RM_PocketGrid.CanFly(p),
				RM_LadderRules.LadderLetsOut(p.Map, c, p), g.WideAt(k, comp, c, RequiredWidth(p)));
		}

		/// <summary>No way out at all: held where it stands and, under the relative rule, no usable ladder anywhere in its
		/// pocket and the pocket wide enough for it on every cell (RM_PocketGrid.TrappedIn). The absolute rule keeps its BFS.</summary>
		public static bool IsTrapped(Pawn p)
		{
			if (!RM_PocketGrid.Relative)
			{
				return TryGetTrapRegion(p, out _);
			}
			if (p == null || !p.Spawned || !IsHeld(p))
			{
				return false;
			}
			int k = RM_PocketGrid.ClimbLimitOf(p);
			RM_PocketGrid g = RM_PocketGrid.For(p.Map);
			return g.TrappedIn(k, g.ComponentOf(k, p.Position), p);
		}

		/// <summary>Is the destination inside component <paramref name="comp"/> (or, for a non-OnCell end mode, touching it)?</summary>
		private static bool DestInComponent(RM_PocketGrid g, int k, int comp, LocalTargetInfo dest, PathEndMode peMode, Map map)
		{
			if (!dest.IsValid)
			{
				return false;
			}
			if (g.ComponentOf(k, dest.Cell) == comp)
			{
				return true;
			}
			if (peMode == PathEndMode.OnCell)
			{
				return false;
			}
			CellRect rect = dest.HasThing ? dest.Thing.OccupiedRect() : CellRect.SingleCell(dest.Cell);
			foreach (IntVec3 c in rect.ExpandedBy(1))
			{
				if (c.InBounds(map) && g.ComponentOf(k, c) == comp)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Design §8.5 step 6: AND vanilla reachability with "same band component". A pocket never reaches the surface;
		/// two surface areas cut apart by a sheer trench are told apart (GPT #1). Pawnless queries use the person band (GPT #9).
		/// A ladder that is a way for this query (the pawn's: one it may climb; pawnless: any lowered one) or a pocket too narrow
		/// for the pawn is a way in or out, and vanilla decides.
		/// Applies only to pawns the hole captures (or pawnless): the capture policy is unchanged until the connectivity masks
		/// make the step rule physics for everyone (the next build item); a colonist the pit ignores is never vetoed here.</summary>
		public static bool RelativeVeto(Map map, IntVec3 start, LocalTargetInfo dest, PathEndMode peMode, Pawn p)
		{
			if (!RuleOn || map == null || !dest.IsValid || !start.InBounds(map) || !dest.Cell.InBounds(map))
			{
				return false;
			}
			RM_MapComponent_Excavation eng = EngineOf(map);
			if (eng == null || eng.ClimbCellCount == 0)
			{
				return false;
			}
			// With the cliff masks on, the step rule is physics for everyone (design §8.1): the pathfinder refuses a colonist's
			// cliff too, so reachability must agree for every pawn but flyers. Without them, only pawns the hole captures.
			if (p != null && (RM_PocketGrid.CanFly(p) || (!RM_CliffMask.On && !Captures(p))))
			{
				return false;
			}
			int k = p == null ? RM_PocketGrid.PersonBand : RM_PocketGrid.ClimbLimitOf(p);
			if (RM_PocketGridMath.BandFor(k, RM_PocketGrid.BandCount) == 0)
			{
				return false;
			}
			RM_PocketGrid g = RM_PocketGrid.For(map);
			int cs = g.ComponentOf(k, start);
			if (cs < 0 || DestInComponent(g, k, cs, dest, peMode, map))
			{
				return false;
			}
			// V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT: pawnless queries included. Vanilla Pawn_PathFollower.StartPath checks a
			// PAWNLESS CanReach (TraverseMode.PassDoors) before every walk; a pawnless query counts any lowered ladder
			// (RM_PocketGridMath.LadderIsAWay), or every walk down or up a ladder failed there.
			bool startPocket = g.ComponentIsPocket(k, cs);
			bool startWayOut = startPocket && !g.TrappedIn(k, cs, p);
			int cd = g.ComponentOf(k, dest.Cell);
			bool destPocket = g.ComponentIsPocket(k, cd);
			// REACH_VETO_FIX_ONE_END_ENOUGH: both ends are judged; a way out of the start no longer excuses a sealed destination.
			bool destWayIn = destPocket
				&& (g.UsableLadderIn(k, cd, p) || !g.WideEverywhere(k, cd, RequiredWidth(p)));
			return RM_PocketGridMath.ReachVetoed(false, startPocket, startWayOut, destPocket, destWayIn);
		}

		// ── the reachability region, cached per pawn per tick ──────────────
		private sealed class RegionEntry
		{
			public int tick;
			public Map map;   // a fixture reload re-issues the same thingIDNumber at the same tick: the map (a new object per load) tells them apart
			public IntVec3 pos;
			public bool trapped;
			public HashSet<IntVec3> cells = new HashSet<IntVec3>();
		}

		private static readonly Dictionary<int, RegionEntry> regionCache = new Dictionary<int, RegionEntry>();
		private static int regionCacheTick = -1;

		/// <summary>True when the pawn is held where it stands AND held on every cell of the
		/// 8-connected D = 4 component it can walk to — i.e. there is no way out at all.
		/// <paramref name="region"/> is that component.</summary>
		public static bool TryGetTrapRegion(Pawn p, out HashSet<IntVec3> region)
		{
			region = null;
			if (p == null || !p.Spawned || !IsHeld(p))
			{
				return false;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			if (now != regionCacheTick)
			{
				regionCache.Clear();
				regionCacheTick = now;
			}
			if (regionCache.TryGetValue(p.thingIDNumber, out RegionEntry e) && e.pos == p.Position && ReferenceEquals(e.map, p.Map))
			{
				region = e.cells;
				return e.trapped;
			}
			e = new RegionEntry { tick = now, map = p.Map, pos = p.Position, trapped = true };
			RM_MapComponent_Excavation eng = EngineOf(p.Map);
			var q = new Queue<IntVec3>();
			q.Enqueue(p.Position);
			e.cells.Add(p.Position);
			while (q.Count > 0)
			{
				IntVec3 c = q.Dequeue();
				if (!IsHeldAt(p, c))
				{
					e.trapped = false;
					break;
				}
				if (e.cells.Count >= MaxRegionCells)
				{
					e.trapped = false;
					break;
				}
				for (int i = 0; i < 8; i++)
				{
					IntVec3 n = c + GenAdj.AdjacentCells[i];
					// Only OPEN pit cells: an intact cover is ground, so it is a way out, never part of the hold.
					// (Enqueued, a covered neighbour would fail IsHeldAt and mark the whole pit untrapped.)
					// REACH_VETO_FIX_ONE_END_ENOUGH (GPT C3-F12): never through a wall into the next pit.
					if (!e.cells.Contains(n) && n.InBounds(p.Map) && n.Walkable(p.Map) && eng.IsSuperdeepExcavation(n)
						&& !Pits.RM_PitCoverUtility.IsCovered(p.Map, n))
					{
						e.cells.Add(n);
						q.Enqueue(n);
					}
				}
			}
			regionCache[p.thingIDNumber] = e;
			region = e.cells;
			return e.trapped;
		}

		public static bool AllowedDestination(HashSet<IntVec3> region, LocalTargetInfo dest, PathEndMode peMode)
		{
			if (!dest.IsValid)
			{
				return false;
			}
			if (region.Contains(dest.Cell))
			{
				return true;
			}
			if (peMode == PathEndMode.OnCell)
			{
				return false;
			}
			CellRect rect = dest.HasThing ? dest.Thing.OccupiedRect() : CellRect.SingleCell(dest.Cell);
			foreach (IntVec3 c in rect.ExpandedBy(1))
			{
				if (region.Contains(c))
				{
					return true;
				}
			}
			return false;
		}

		// ── the descent event ─────────────────────────────────────────────
		internal static void OnDescent(Pawn p, IntVec3 cell, RM_SuperdeepTrapState state, int drop = -1)
		{
			float dmg = 0f;
			if (RimMandrakeFlowWorksSettings.fallDamageEnabled)
			{
				float scale = 1f;
				if (RM_PocketGrid.Relative)
				{
					// Design §8.5 step 8 (PROVISIONAL): damage scales by drop ÷ 2 m, capped (never by the dig cap: an 8 m cap would
					// soften every fall; P7 owns metres fallen); unknown drop = from the surface.
					RM_MapComponent_Excavation eng = EngineOf(p.Map);
					int d = drop >= 0 ? drop : (eng?.ClimbDepthAt(cell) ?? RM_PitTrapMath.Superdeep);
					scale = RM_PitTrapMath.FallDropScale(d, RM_PitTrapMath.Superdeep);
				}
				dmg = scale * RM_PitTrapMath.FallDamage(p.GetStatValue(StatDefOf.Mass), RimMandrakeFlowWorksSettings.fallDamageMultiplier);
				p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg));
			}
			state.RecordDescent(p, cell, dmg);
			PitDescent?.Invoke(p, cell);
		}

		/// <summary>FLOWWORKS_PIT_FALL_ONLY_FORCED_1: a forced arrival (skip, flyer landing, a cover
		/// giving way, a mod's push). Everyone falls; one of your own who was forced in is then held
		/// like a jumper ("If you're in a superdeep pit, you can't climb out. Period.") — a lowered
		/// ladder is their way out.</summary>
		internal static void OnForcedDescent(Pawn p, IntVec3 cell, RM_SuperdeepTrapState state, int drop = -1)
		{
			if (p == null || state == null)
			{
				return;
			}
			if (p.Faction == Faction.OfPlayer)
			{
				state.AddJumper(p);
			}
			state.NoteHandledArrival(p, cell);
			OnDescent(p, cell, state, drop);
		}

		// ── "Jump into pit" ───────────────────────────────────────────────
		/// <summary>Voluntary descent: the pawn steps into the D = 4 cell, takes the fall, and
		/// is stranded like anyone else (it counts as captured until it is off D = 4).</summary>
		public static bool TryJumpInto(Pawn p, IntVec3 cell)
		{
			if (p == null || !p.Spawned)
			{
				return false;
			}
			RM_MapComponent_Excavation eng = EngineOf(p.Map);
			if (eng == null || !eng.IsSuperdeepExcavation(cell) || eng.IsSuperdeepExcavation(p.Position)
				|| !cell.Standable(p.Map) || !p.Position.AdjacentTo8WayOrInside(cell))
			{
				return false;
			}
			eng.SuperdeepTrap.AddJumper(p);
			p.jobs?.StopAll();
			p.pather?.StopDead();
			IntVec3 from = p.Position;
			p.Position = cell;
			p.Notify_Teleported(true, true);
			// PIT_FALL_MEND_SAVED_MIDAIR (GPT C3-F1): the fall used to wait for the detector's next pass, which compares against
			// an unsaved last cell, so a jump made while paused and saved before unpausing never fell. Resolve it now, by the
			// detector's own test; the jumper flag makes it count even with the own-faction carve-out on.
			eng.SuperdeepTrap.ResolveArrivalNow(p.Map, eng, p, from);
			return true;
		}

		public static IntVec3 JumpTargetFor(Pawn p)
		{
			RM_MapComponent_Excavation eng = EngineOf(p?.Map);
			if (eng == null || eng.SuperdeepCellCount == 0 || eng.IsSuperdeepExcavation(p.Position))
			{
				return IntVec3.Invalid;
			}
			for (int i = 0; i < 4; i++)
			{
				IntVec3 c = p.Position + GenAdj.CardinalDirections[i];
				if (eng.IsSuperdeepExcavation(c) && c.Standable(p.Map))
				{
					return c;
				}
			}
			return IntVec3.Invalid;
		}
	}

	/// <summary>Per-map trap state, scribed by RM_MapComponent_Excavation: the jumper set
	/// (references) and, derived and never scribed, the per-pawn last cell the descent
	/// detector compares against.</summary>
	public class RM_SuperdeepTrapState : IExposable
	{
		private HashSet<Pawn> jumpers = new HashSet<Pawn>();
		private Dictionary<Pawn, IntVec3> lastCell = new Dictionary<Pawn, IntVec3>();
		private Dictionary<Pawn, IntVec3> nextCell = new Dictionary<Pawn, IntVec3>();
		/// <summary>Superdeep cells a pawn's own path follower stepped it into since the last
		/// detector pass (RM_Patch_PathFollower_WalkedStep). Absent = the arrival was forced.</summary>
		private readonly Dictionary<Pawn, IntVec3> walkedInto = new Dictionary<Pawn, IntVec3>();
		private readonly List<Pawn> descents = new List<Pawn>();
		private readonly HashSet<Pawn> forced = new HashSet<Pawn>();
		private readonly Dictionary<Pawn, int> dropOf = new Dictionary<Pawn, int>();

		/// <summary>Read by the bridge (jawa/flowworks_pit_report): newest last, max 32.</summary>
		public readonly List<string> RecentDescents = new List<string>();
		public int DescentCount;

		public bool IsJumper(Pawn p)
		{
			return p != null && jumpers.Contains(p);
		}

		public void AddJumper(Pawn p)
		{
			if (p != null)
			{
				jumpers.Add(p);
			}
		}

		public void ResetDetector()
		{
			lastCell.Clear();
			nextCell.Clear();
			walkedInto.Clear();
		}

		public void NoteWalkedStep(Pawn p, IntVec3 cell)
		{
			if (p != null)
			{
				walkedInto[p] = cell;
			}
		}

		/// <summary>An arrival already handled as a fall elsewhere: the detector must not count it
		/// again (it compares against lastCell on its next pass).</summary>
		public void NoteHandledArrival(Pawn p, IntVec3 cell)
		{
			if (p != null)
			{
				lastCell[p] = cell;
			}
		}

		public void Tick(Map map, RM_MapComponent_Excavation eng)
		{
			nextCell.Clear();
			descents.Clear();
			forced.Clear();
			dropOf.Clear();
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				IntVec3 pos = p.Position;
				if (lastCell.TryGetValue(p, out IntVec3 prev) && prev != pos
					&& RimMandrakeFlowWorksSettings.superdeepCaptureEnabled
					&& IsFallingArrival(map, eng, p, prev, pos)
					&& !Pits.RM_PitCoverUtility.IsCovered(map, pos)
					&& !p.Flying)
				{
					// FLOWWORKS_PIT_FALL_ONLY_FORCED_1: who falls is decided by HOW the pawn arrived.
					bool walked = walkedInto.TryGetValue(p, out IntVec3 w) && w == pos;
					if (RM_PitTrapMath.DescentFalls(walked, RM_LadderRules.LadderLetsOut(map, pos, p),
						p.Faction == Faction.OfPlayer, RM_SuperdeepTrap.Captures(p)))
					{
						descents.Add(p);
						dropOf[p] = eng.ClimbDepthAt(pos) - RM_SuperdeepTrap.StepDepthAt(map, eng, prev);
						if (!walked)
						{
							forced.Add(p);
						}
					}
				}
				nextCell[p] = pos;
			}
			walkedInto.Clear();
			Dictionary<Pawn, IntVec3> swap = lastCell;
			lastCell = nextCell;
			nextCell = swap;
			for (int i = 0; i < descents.Count; i++)
			{
				Pawn p = descents[i];
				if (p.Spawned)
				{
						int drop = dropOf.TryGetValue(p, out int dd) ? dd : -1;
						if (forced.Contains(p))
						{
							RM_SuperdeepTrap.OnForcedDescent(p, p.Position, this, drop);
						}
						else
						{
							RM_SuperdeepTrap.OnDescent(p, p.Position, this, drop);
						}
				}
			}
			if (jumpers.Count > 0)
			{
				// Scan first: RemoveWhere's capturing lambda would allocate a closure every tick a jumper exists.
				bool stale = false;
				foreach (Pawn j in jumpers)
				{
					if (j == null || !j.Spawned || j.Map != map || !InHole(eng, j.Position))
					{
						stale = true;
						break;
					}
				}
				if (stale)
				{
					PruneJumpers(map, eng);
				}
			}
		}

		/// <summary>PIT_FALL_MEND_SAVED_MIDAIR: one forced arrival (prev to the pawn's cell) judged now by the detector's own test
		/// (Tick), instead of on its next pass. A fall marks the arrival handled (OnForcedDescent), so Tick never counts it twice.</summary>
		internal void ResolveArrivalNow(Map map, RM_MapComponent_Excavation eng, Pawn p, IntVec3 prev)
		{
			if (p == null || !p.Spawned || map == null || eng == null)
			{
				return;
			}
			IntVec3 pos = p.Position;
			if (prev != pos && RimMandrakeFlowWorksSettings.superdeepCaptureEnabled && IsFallingArrival(map, eng, p, prev, pos)
				&& !Pits.RM_PitCoverUtility.IsCovered(map, pos) && !p.Flying
				&& RM_PitTrapMath.DescentFalls(false, RM_LadderRules.LadderLetsOut(map, pos, p), p.Faction == Faction.OfPlayer,
					RM_SuperdeepTrap.Captures(p)))
			{
				RM_SuperdeepTrap.OnForcedDescent(p, pos, this, eng.ClimbDepthAt(pos) - RM_SuperdeepTrap.StepDepthAt(map, eng, prev));
			}
		}

		/// <summary>Absolute rule: a descent into D = 4 from shallower. Relative (design §8.5 step 8): the arrival drops more than
		/// this pawn climbs (RM_PitTrapMath.ArrivalDropsTooFar); who takes the fall is still DescentFalls.</summary>
		private static bool IsFallingArrival(Map map, RM_MapComponent_Excavation eng, Pawn p, IntVec3 prev, IntVec3 pos)
		{
			if (!RM_PocketGrid.Relative)
			{
				return RM_PitTrapMath.IsPitDescent(eng.ExcavatedDepthAt(prev), eng.ExcavatedDepthAt(pos));
			}
			int to = eng.ClimbDepthAt(pos);
			if (to == 0)
			{
				return false;
			}
			int from = RM_SuperdeepTrap.StepDepthAt(map, eng, prev);
			return to > from && RM_PitTrapMath.ArrivalDropsTooFar(from, to, RM_PocketGrid.ClimbLimitOf(p));
		}

		/// <summary>Still down the hole, for the jumper flag: D = 4 (absolute), any dug cell (relative).</summary>
		private static bool InHole(RM_MapComponent_Excavation eng, IntVec3 c)
		{
			return RM_PocketGrid.Relative ? eng.ClimbDepthAt(c) > 0 : eng.IsSuperdeepExcavation(c);
		}

		// Separate method on purpose: a lambda capturing Tick's parameters would make the compiler allocate the
		// closure at Tick's entry, every tick, whether or not it ever runs.
		private void PruneJumpers(Map map, RM_MapComponent_Excavation eng)
		{
			jumpers.RemoveWhere(p => p == null || !p.Spawned || p.Map != map || !InHole(eng, p.Position));
		}

		internal void RecordDescent(Pawn p, IntVec3 cell, float dmg)
		{
			DescentCount++;
			RecentDescents.Add(p.ThingID + "@" + cell.x + "," + cell.z + " t=" + Find.TickManager.TicksGame
				+ " fall=" + dmg.ToString("F1"));
			if (RecentDescents.Count > 32)
			{
				RecentDescents.RemoveAt(0);
			}
		}

		public void ExposeData()
		{
			if (Scribe.mode == LoadSaveMode.Saving && jumpers != null)
			{
				// Tick prunes only while superdeep cells exist; a discarded pawn left
				// here would save as an unresolvable reference.
				jumpers.RemoveWhere(p => p == null || p.Destroyed);
			}
			Scribe_Collections.Look(ref jumpers, "jumpers", LookMode.Reference);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (jumpers == null)
				{
					jumpers = new HashSet<Pawn>();
				}
				jumpers.RemoveWhere(p => p == null);
			}
		}
	}

	// ── Harmony ────────────────────────────────────────────────────────────

	/// <summary>The hard per-move floor (seam 1).</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), "TryEnterNextPathCell")]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PathFollower_SuperdeepFloor
	{
		private const int RerouteCooldown = 60;
		private static readonly Dictionary<int, int> lastReroute = new Dictionary<int, int>();
		// The game lastReroute belongs to. A reload re-issues the same thingIDNumbers, and loading an EARLIER save made
		// now - last negative, which refused every reroute for that pawn until the clock caught up (PIT_REROUTE_FIX_TIME_TRAVEL_FORGIVEN).
		private static Game rerouteGame;

		[HarmonyPrefix]
		public static bool Prefix(Pawn_PathFollower __instance, Pawn ___pawn)
		{
			Pawn pawn = ___pawn;
			if (pawn == null || !pawn.Spawned)
			{
				return true;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(pawn.Map);
			if (!RM_SuperdeepTrap.AnyHole(eng))
			{
				return true;
			}
			if (RM_PocketGrid.Relative)
			{
				if (RelativeStepAllowed(pawn, eng, __instance.nextCell))
				{
					return true;
				}
			}
			else
			{
				// A covered destination is ground for the floor: a held pawn may not climb out onto an intact cover.
				int toD = Pits.RM_PitCoverUtility.IsCovered(pawn.Map, __instance.nextCell) ? 0 : eng.ExcavatedDepthAt(__instance.nextCell);
				if (!RM_PitTrapMath.StepBlocked(RM_SuperdeepTrap.IsHeld(pawn), toD))
				{
					return true;
				}
			}
			// A path planned before the pawn was held (or a stale one) tries to leave over the lip.
			// If this pit has a way out for it, re-plan (RM_PitPathing routes it to the ladder) rather
			// than fail the job — failing is what left the pit_escape friendly on Wait forever. At
			// most once per RerouteCooldown ticks, so a route that still cannot work fails as before.
			int now = Find.TickManager?.TicksGame ?? 0;
			if (!ReferenceEquals(rerouteGame, Current.Game))
			{
				lastReroute.Clear();
				rerouteGame = Current.Game;
			}
			if (!RM_SuperdeepTrap.IsTrapped(pawn)
				&& (!lastReroute.TryGetValue(pawn.thingIDNumber, out int last) || now < last || now - last >= RerouteCooldown))
			{
				lastReroute[pawn.thingIDNumber] = now;
				if (lastReroute.Count > 256)
				{
					lastReroute.Clear();
					lastReroute[pawn.thingIDNumber] = now;
				}
				__instance.ResetToCurrentPosition();
				return false;
			}
			// Vanilla's own PatherFailed shape (Pawn_PathFollower.cs l.573).
			__instance.StopDead();
			if (pawn.jobs?.curJob != null)
			{
				pawn.jobs.curDriver.Notify_PatherFailed();
			}
			return false;
		}

		/// <summary>Design §8.5 step 4: the step must be allowed for the pawn's climb limit (RM_PitTrapMath.StepAllowed; a diagonal
		/// also needs both corners within K, DiagonalAllowed). A covered cell reads as ground (StepDepthAt).
		/// PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: while the cliff masks are on (RM_CliffMask.On) the pathfinder is edge-correct,
		/// so the floor checks EVERY pawn but flyers, as a guard against stale paths and other mods' movers; a ramp, or a ladder
		/// this pawn may climb, joins its step whatever the depth difference (RM_ClimbJoins.ForPawn). With the masks off (the
		/// absolute ladder rule's switch off), only a HELD pawn is checked, as before: a universal floor over cliff-blind A* would
		/// fail the pather in a loop.</summary>
		internal static bool RelativeStepAllowed(Pawn pawn, RM_MapComponent_Excavation eng, IntVec3 next)
		{
			bool everyone = RM_CliffMask.On;
			// PIT_REACH_VERIFY_FLYERS_AND_GIANTS (GPT C3-F5): a pawn too wide for the pocket it stands in is not held there
			// (IsHeldAtRelative's width rule), so the floor lets it climb out, as the masks do (RM_CliffMask.Swap).
			if (everyone ? RM_PocketGrid.CanFly(pawn) || RM_SuperdeepTrap.InOwnPocketTooNarrow(pawn) : !RM_SuperdeepTrap.IsHeld(pawn))
			{
				return true;
			}
			Map map = pawn.Map;
			IntVec3 from = pawn.Position;
			if (!next.InBounds(map) || next == from)
			{
				return true;
			}
			int k = RM_PocketGrid.ClimbLimitOf(pawn);
			if (everyone && RM_PocketGridMath.BandFor(k, RM_PocketGrid.BandCount) == 0)
			{
				return true; // climbs every step there is
			}
			int fromD = RM_SuperdeepTrap.StepDepthAt(map, eng, from);
			int toD = RM_SuperdeepTrap.StepDepthAt(map, eng, next);
			if (from.x != next.x && from.z != next.z)
			{
				return RM_PitTrapMath.DiagonalAllowed(fromD, toD,
					RM_SuperdeepTrap.StepDepthAt(map, eng, new IntVec3(next.x, 0, from.z)),
					RM_SuperdeepTrap.StepDepthAt(map, eng, new IntVec3(from.x, 0, next.z)), k);
			}
			bool join = everyone && RM_ClimbJoins.ForPawn(map, eng, from, next, fromD, toD, pawn, out _, out _);
			return RM_PitTrapMath.StepAllowed(fromD, toD, k, join);
		}
	}

	/// <summary>The reachability veto (seam 2), outside the region cache.</summary>
	[HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReach),
		new[] { typeof(IntVec3), typeof(LocalTargetInfo), typeof(PathEndMode), typeof(TraverseParms) })]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_Reachability_SuperdeepVeto
	{
		[HarmonyPostfix]
		public static void Postfix(IntVec3 start, LocalTargetInfo dest, PathEndMode peMode,
			TraverseParms traverseParams, ref bool __result, Map ___map)
		{
			if (!__result)
			{
				return;
			}
			Pawn p = traverseParams.pawn;
			if (RM_PocketGrid.Relative)
			{
				// Design §8.5 step 6: same band component, from ANY start, pawnless included (GPT #9).
				// PIT_REACH_VERIFY_FLYERS_AND_GIANTS (GPT C3-F4): vanilla StartPath's pawnless check is answered for the pawn
				// that is starting the walk, so a flyer or a big climber is not judged at the person band.
				Pawn walker = p ?? RM_Patch_PathFollower_ReachWalker.WalkerAt(___map, start);
				if (RM_SuperdeepTrap.RelativeVeto(___map, start, dest, peMode, walker))
				{
					__result = false;
					return;
				}
				if (p != null && p.Spawned && start == p.Position && RM_PitPathing.OutsiderBarredFromFloor(p, start, dest, peMode))
				{
					__result = false;
				}
				return;
			}
			if (p == null || !p.Spawned || start != p.Position)
			{
				return;
			}
			if (!RM_SuperdeepTrap.TryGetTrapRegion(p, out HashSet<IntVec3> region))
			{
				// FLOWWORKS_LADDER_RAISE_LOWER_1: from outside, the pit floor only down a usable ladder.
				if (RM_PitPathing.OutsiderBarredFromFloor(p, start, dest, peMode))
				{
					__result = false;
				}
				return;
			}
			if (!RM_SuperdeepTrap.AllowedDestination(region, dest, peMode))
			{
				__result = false;
			}
		}
	}

	/// <summary>PIT_REACH_VERIFY_FLYERS_AND_GIANTS (GPT C3-F4): vanilla Pawn_PathFollower.StartPath (decompiled 1.6) asks
	/// Reachability.CanReach(pawn.Position, dest, peMode, TraverseParms.For(TraverseMode.PassDoors)) with NO pawn before
	/// every walk. RelativeVeto answered that at the person band with no flyer exemption, so a flyer ordered into a
	/// ladderless pocket, or a K3+ animal up a 3-level step, failed its pather. This remembers which pawn is starting a walk
	/// (save/restore: StartPath can nest through PatherFailed and a new job) so the veto answers for it.</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), nameof(Pawn_PathFollower.StartPath))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_PathFollower_ReachWalker
	{
		[ThreadStatic]
		private static Pawn walker;

		/// <summary>The pawn whose StartPath is running, when the query starts where it stands on this map; else null.</summary>
		public static Pawn WalkerAt(Map map, IntVec3 start)
		{
			Pawn w = walker;
			return w != null && w.Spawned && w.Map == map && w.Position == start ? w : null;
		}

		[HarmonyPrefix]
		public static void Prefix(Pawn ___pawn, out Pawn __state)
		{
			__state = walker;
			walker = ___pawn;
		}

		[HarmonyFinalizer]
		public static void Finalizer(Pawn __state)
		{
			walker = __state;
		}
	}

	[HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReachMapEdge),
		new[] { typeof(IntVec3), typeof(TraverseParms) })]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_Reachability_SuperdeepMapEdge
	{
		[HarmonyPostfix]
		public static void Postfix(IntVec3 c, TraverseParms traverseParms, ref bool __result)
		{
			if (!__result)
			{
				return;
			}
			Pawn p = traverseParms.pawn;
			if (p == null || !p.Spawned)
			{
				return;
			}
			if (RM_CliffMask.On)
			{
				// Physics for everyone (design §8.1): a pocket with no way out for this pawn never reaches the map edge.
				if (RM_PocketGrid.CanFly(p) || !c.InBounds(p.Map))
				{
					return;
				}
				int k = RM_PocketGrid.ClimbLimitOf(p);
				if (RM_PocketGridMath.BandFor(k, RM_PocketGrid.BandCount) == 0 || RM_SuperdeepTrap.EngineOf(p.Map)?.ClimbCellCount is null or 0)
				{
					return;
				}
				RM_PocketGrid g = RM_PocketGrid.For(p.Map);
				int comp = g.ComponentOf(k, c);
				// REACH_VETO_FIX_ONE_END_ENOUGH (GPT C3-F9): nor does a surface island ringed by a sheer trench (no border
				// cell in its component), the same "two surface components stay apart" rule CanReach's veto applies.
				if (g.TrappedIn(k, comp, p) || (!g.ComponentIsPocket(k, comp) && !g.TouchesEdge(k, comp)))
				{
					__result = false;
				}
				return;
			}
			if (c != p.Position)
			{
				return;
			}
			if (RM_SuperdeepTrap.IsTrapped(p))
			{
				__result = false;
			}
		}
	}

	/// <summary>"Jump into pit": warn + confirm; strands the jumper.</summary>
	[HarmonyPatch(typeof(Pawn), nameof(Pawn.GetGizmos))]
	[RimMandrake.Shared.PatchFeature("Superdeep pits trap", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_Pawn_JumpIntoPitGizmo
	{
		[HarmonyPostfix]
		public static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> __result, Pawn __instance)
		{
			foreach (Gizmo g in __result)
			{
				yield return g;
			}
			if (!RimMandrakeFlowWorksSettings.superdeepCaptureEnabled || __instance == null
				|| !__instance.Spawned || !__instance.IsColonistPlayerControlled || __instance.Downed)
			{
				yield break;
			}
			IntVec3 target = RM_SuperdeepTrap.JumpTargetFor(__instance);
			if (!target.IsValid)
			{
				yield break;
			}
			Pawn pawn = __instance;
			yield return new Command_Action
			{
				defaultLabel = "RMFlow_JumpIntoPit".Translate(),
				defaultDesc = "RMFlow_JumpIntoPitDesc".Translate(),
				icon = TexCommand.Attack,
				action = () => Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
					"RMFlow_JumpIntoPitConfirm".Translate(pawn.LabelShort),
					() => RM_SuperdeepTrap.TryJumpInto(pawn, target), destructive: true))
			};
		}
	}
}

namespace RimMandrake.FlowWorks
{
	/// <summary>One inspect line on a pawn standing in a pit: held, or too big for it.</summary>
	[HarmonyLib.HarmonyPatch(typeof(Verse.Pawn), nameof(Verse.Pawn.GetInspectString))]
	public static class RM_Patch_Pawn_PitInspectLine
	{
		[HarmonyLib.HarmonyPostfix]
		public static void Postfix(Verse.Pawn __instance, ref string __result)
		{
			if (__instance == null || !__instance.Spawned || !RM_SuperdeepTrap.RuleOn)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(__instance.Map);
			bool relative = RM_PocketGrid.Relative;
			if (eng == null || !RM_SuperdeepTrap.AnyHole(eng)
				|| !(relative ? eng.ClimbDepthAt(__instance.Position) > 0 : eng.IsSuperdeepExcavation(__instance.Position)))
			{
				return;
			}
			// PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS (design §8.2: "Climbs out of steps up to K deep."), for anyone in a hole.
			if (relative && !RM_PocketGrid.CanFly(__instance))
			{
				string climb = "RMFlow_ClimbsSteps".Translate(RM_Volume.FormatMetres(RM_PocketGrid.ClimbLimitOf(__instance)));
				__result = string.IsNullOrEmpty(__result) ? climb : __result + "\n" + climb;
			}
			if (!RM_SuperdeepTrap.Captures(__instance))
			{
				return;
			}
			string line;
			if (RM_SuperdeepTrap.IsHeld(__instance))
			{
				line = "RMFlow_PitHeld".Translate();
			}
			else if (relative
				? RM_SuperdeepTrap.InOwnPocketTooNarrow(__instance)
				: RM_SuperdeepTrap.MeasuredPitWidth(__instance.Map, __instance.Position) < RM_SuperdeepTrap.RequiredWidth(__instance))
			{
				line = "RMFlow_PitTooBig".Translate();
			}
			else
			{
				return;
			}
			__result = string.IsNullOrEmpty(__result) ? line : __result + "\n" + line;
		}
	}
}
