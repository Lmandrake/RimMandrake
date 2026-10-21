using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS (design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md R9): one leaf of a
	/// drawbridge, saved on its bridge record. Every leaf records its own hinge bank, control bank and movement; none of it is
	/// inferred from faction or from where pawns stand (R1). Versioned; no pathing cache is saved; a completed tip is
	/// committed once (tipCommitted) and never replayed on load.
	/// </summary>
	public class DrawbridgeLeaf : IExposable
	{
		public int version = RM_DrawbridgeMath.LeafRecordVersion;
		/// <summary>Deck indices along the bridge record, inclusive.</summary>
		public int first;
		public int last;
		/// <summary>The hinge (and its winch house) is on the bank beside `first` (record index 0, anchor A); else beside `last`.</summary>
		public bool hingeAtFirst = true;
		/// <summary>The bank the leaf is LOWERED from (the winch side, R2). Raising works from either bank.</summary>
		public bool controlAtFirst = true;
		public bool targetRaised;
		/// <summary>Ticks of travel, 0 = lowered, FullTicks = raised. An interrupted move holds its part-way point.</summary>
		public int progress;
		/// <summary>The leaf cannot move (a steel leaf without power, R2); it holds where it is.</summary>
		public bool frozen;
		/// <summary>The player's "hold raised" (R4): peace mode never lowers it.</summary>
		public bool holdRaised;
		/// <summary>The tip rule (R3) has run for the raise now under way; cleared when the leaf is fully lowered again.</summary>
		public bool tipCommitted;
		/// <summary>Phase 3: a player order (RM_DrawbridgeMath.Order*) waiting for a colonist at the winch (or, raising, at the
		/// far anchor).</summary>
		public int pendingOrder;
		/// <summary>Phase 3, R4: this lower was started by peace mode (not ordered); locking cancels it.</summary>
		public bool autoLowering;
		/// <summary>Phase 3: the winch house this leaf hangs on (one per leaf, on its own hinge bank). Null: none built (or lost).</summary>
		public Building_DrawbridgeWinch winch;
		/// <summary>A colonist is at the hand winch until this tick (not saved: a reload resumes the job, which sets it again).</summary>
		public int workedUntilTick = -1;

		public LeafSpan Span => new LeafSpan(first, last, hingeAtFirst);

		public void ExposeData()
		{
			Scribe_Values.Look(ref version, "v", 0);
			Scribe_Values.Look(ref first, "first", 0);
			Scribe_Values.Look(ref last, "last", 0);
			Scribe_Values.Look(ref hingeAtFirst, "hingeAtFirst", true);
			Scribe_Values.Look(ref controlAtFirst, "controlAtFirst", true);
			Scribe_Values.Look(ref targetRaised, "targetRaised", false);
			Scribe_Values.Look(ref progress, "progress", 0);
			Scribe_Values.Look(ref frozen, "frozen", false);
			Scribe_Values.Look(ref holdRaised, "holdRaised", false);
			Scribe_Values.Look(ref tipCommitted, "tipCommitted", false);
			Scribe_Values.Look(ref pendingOrder, "pendingOrder", 0);
			Scribe_Values.Look(ref autoLowering, "autoLowering", false);
			Scribe_References.Look(ref winch, "winch");
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				version = RM_DrawbridgeMath.LeafRecordVersion;
			}
		}
	}

	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS, phase 1 (core): making a suspension bridge a drawbridge, moving its leaves and
	/// telling every path at once (R8). A raise or a lower is a reversible state change on the leaf record: the deck squares
	/// stay built and only stop (or start) being ground. Nothing here destroys, collapses or drops a deck square; structural
	/// failure stays the suspension bridge's own (CollapseSpan, the swing-down), which reads StructuralDeckAt and so still
	/// takes a raised leaf with its span (R6).
	/// </summary>
	public static class RM_Drawbridges
	{
		/// <summary>Leaves move in steps of this many ticks (the progress is in ticks, so the speed does not depend on it).</summary>
		public const int TickInterval = 5;

		private static readonly AccessTools.FieldRef<Pawn_PathFollower, PathEndMode> PeMode =
			AccessTools.FieldRefAccess<Pawn_PathFollower, PathEndMode>("peMode");

		/// <summary>Set by the functional script / proofs: how many toggles forced a repath, and how many pawns were re-pathed.</summary>
		public static int ToggleCount;
		public static int RepathCount;
		public static int HostileJobsEnded;

		public static float SpeedMultiplier => RM_DrawbridgeSettings.raiseSpeed;

		/// <summary>The longest leaf of this material (Mod Settings; 0 = not a drawbridge material).</summary>
		public static int MaxLeaf(SuspensionTier t)
		{
			switch (t)
			{
				case SuspensionTier.Timber: return RM_DrawbridgeSettings.maxLeafTimber;
				case SuspensionTier.Steel: return RM_DrawbridgeSettings.maxLeafSteel;
				default: return 0;
			}
		}

		public static int FullTicks(SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			return RM_DrawbridgeMath.FullTicks(r.tier, l.Span.Length, SpeedMultiplier);
		}

		/// <summary>Whether this bridge can be a drawbridge: timber or steel, a bridge (not a jetty), no towers (a leaf swings
		/// from a bank, never from a tower), and a deck no longer than two leaves of its material.</summary>
		public static bool CanBeDrawbridge(SuspensionBridgeRecord r, out string why)
		{
			why = null;
			if (r == null)
			{
				why = "no bridge";
			}
			else if (!RM_DrawbridgeMath.IsDrawbridgeTier(r.tier))
			{
				why = "only timber and steel bridges can be drawbridges";
			}
			else if (r.jetty)
			{
				why = "a jetty has no far bank";
			}
			else if (r.towers != null && r.towers.Count > 0)
			{
				why = "a drawbridge cannot stand on towers";
			}
			else if (RM_DrawbridgeMath.SplitLeaves(1, r.length - 2, MaxLeaf(r.tier), true) == null)
			{
				why = "too long: a " + RM_SuspensionMath.TierLabel(r.tier) + " drawbridge spans at most " + (2 * MaxLeaf(r.tier)) + " squares";
			}
			return why == null;
		}

		/// <summary>Which end of a planned bridge is the colony's: the one in the home area when only one is; else the one nearer
		/// the colony's buildings (their mean position); else end A.</summary>
		public static bool ColonyEndIsFirst(Map map, SuspensionBridgeRecord r)
		{
			IntVec3 a = r.Cell(0, 0), b = r.Cell(0, r.length - 1);
			Area home = map?.areaManager?.Home;
			if (home != null && a.InBounds(map) && b.InBounds(map) && home[a] != home[b])
			{
				return home[a];
			}
			List<Building> mine = map?.listerBuildings?.allBuildingsColonist;
			if (mine == null || mine.Count == 0)
			{
				return true;
			}
			long sx = 0, sz = 0;
			foreach (Building bd in mine)
			{
				sx += bd.Position.x;
				sz += bd.Position.z;
			}
			IntVec3 c = new IntVec3((int)(sx / mine.Count), 0, (int)(sz / mine.Count));
			return a.DistanceToSquared(c) <= b.DistanceToSquared(c);
		}

		/// <summary>Cut the bridge into leaves (lowered). colonyBankAtFirst: the single leaf (or the larger one) hinges on anchor A.</summary>
		public static bool MakeDrawbridge(SuspensionBridgeRecord r, bool colonyBankAtFirst, out string why)
		{
			if (!CanBeDrawbridge(r, out why))
			{
				return false;
			}
			if (r.IsDrawbridge)
			{
				why = "already a drawbridge";
				return false;
			}
			r.leaves = new List<DrawbridgeLeaf>();
			foreach (LeafSpan s in RM_DrawbridgeMath.SplitLeaves(1, r.length - 2, MaxLeaf(r.tier), colonyBankAtFirst))
			{
				r.leaves.Add(new DrawbridgeLeaf { first = s.First, last = s.Last, hingeAtFirst = s.HingeAtFirst, controlAtFirst = s.HingeAtFirst });
			}
			return true;
		}

		public static DrawbridgeLeaf LeafOf(SuspensionBridgeRecord r, int index)
		{
			if (r == null || !r.IsDrawbridge)
			{
				return null;
			}
			foreach (DrawbridgeLeaf l in r.leaves)
			{
				if (l.Span.Contains(index))
				{
					return l;
				}
			}
			return null;
		}

		/// <summary>Is the deck square on this cell a raised leaf square (the record's verdict, read on spawn)?</summary>
		public static bool RaisedAt(Map map, IntVec3 c)
		{
			SuspensionBridgeRecord r = map?.GetComponent<RM_MapComponent_SuspensionBridges>()?.RecordAt(c);
			if (r == null || !r.IsDrawbridge || !r.TryIndexOf(c, out _, out int i))
			{
				return false;
			}
			DrawbridgeLeaf l = LeafOf(r, i);
			return l != null && RM_DrawbridgeMath.IsRaised(l.Span, i, l.progress, FullTicks(r, l));
		}

		/// <summary>Phase 3: the player's order. A colonist carries it out (WorkGiver_Drawbridge): raising from either bank,
		/// lowering only from the winch bank. A raise ordered in peace holds the leaf up; one ordered while locked comes down
		/// again once the threat is gone; a lower clears the hold.</summary>
		public static void Order(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l, bool raise)
		{
			if (r == null || l == null)
			{
				return;
			}
			bool locked = FreeHostileCount(map, true) > 0;
			l.holdRaised = RM_DrawbridgeMath.HoldAfterOrder(raise, locked, l.holdRaised);
			l.pendingOrder = raise ? RM_DrawbridgeMath.OrderRaise : RM_DrawbridgeMath.OrderLower;
			l.autoLowering = false;
		}

		/// <summary>Dev only: set the target directly (the drive still has to move it).</summary>
		public static void DevSetTarget(DrawbridgeLeaf l, bool raise)
		{
			l.targetRaised = raise;
			l.holdRaised = raise;
			l.pendingOrder = RM_DrawbridgeMath.OrderNone;
		}

		/// <summary>From the bridges map component's tick: move every leaf that is not at its target and may move.</summary>
		public static void Tick(RM_MapComponent_SuspensionBridges comp, int now)
		{
			if (now % TickInterval != 0)
			{
				return;
			}
			IReadOnlyList<SuspensionBridgeRecord> bridges = comp.Bridges;
			for (int b = 0; b < bridges.Count; b++)
			{
				SuspensionBridgeRecord r = bridges[b];
				if (!r.IsDrawbridge)
				{
					continue;
				}
				foreach (DrawbridgeLeaf l in r.leaves)
				{
					int full = FullTicks(r, l);
					if (!RM_DrawbridgeSettings.drawbridgesEnabled)
					{
						// R11 all off: a suspension bridge stuck lowered; a raised leaf is set down (no crash, nobody hit)
						if (l.progress > 0 || l.targetRaised)
						{
							l.progress = 0;
							l.targetRaised = false;
							l.tipCommitted = false;
							l.autoLowering = false;
							l.pendingOrder = RM_DrawbridgeMath.OrderNone;
							Apply(comp.map, r, l);
						}
						continue;
					}
					Mode(comp.map, r, l, now);
					Building_DrawbridgeWinch w = l.winch != null && l.winch.Spawned ? l.winch : null;
					w?.HoldProofPower();
					bool powered = w != null && w.Powered;
					l.frozen = RM_DrawbridgeMath.FrozenFor(r.tier, w != null, powered);
					if (RM_DrawbridgeMath.AtTarget(l.progress, l.targetRaised, full))
					{
						if (l.progress == 0)
						{
							l.autoLowering = false;
						}
						continue;
					}
					if (l.frozen || !RM_DrawbridgeMath.DriveMoves(r.tier, w != null, powered, now <= l.workedUntilTick))
					{
						continue;
					}
					l.progress = RM_DrawbridgeMath.Step(l.progress, l.targetRaised, full, TickInterval);
					// R3: the moment the leaf leaves its seat its riders tip to the hinge bank (once per raise: tipCommitted is
					// saved, so a reload mid-raise never tips again); the overflow falls once the squares are open hole
					List<Pawn> fallers = null;
					if (l.progress > 0 && !l.tipCommitted)
					{
						fallers = Tip(comp.map, r, l);
						l.tipCommitted = true;
					}
					if (l.progress == 0)
					{
						l.tipCommitted = false;
					}
					Apply(comp.map, r, l);
					if (fallers != null && fallers.Count > 0)
					{
						Fall(comp.map, r, fallers);
					}
				}
			}
		}

		/// <summary>Bring every deck square of this leaf in line with its progress; any square that changed is announced at once.</summary>
		public static void Apply(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			if (map == null)
			{
				return;
			}
			int full = FullTicks(r, l);
			List<IntVec3> changed = null;
			for (int lane = 0; lane < r.width; lane++)
			{
				for (int i = l.first; i <= l.last; i++)
				{
					IntVec3 c = r.Cell(lane, i);
					Building_SuspensionDeck d = RM_MapComponent_SuspensionBridges.StructuralDeckAt(map, c);
					if (d == null)
					{
						continue;
					}
					bool up = RM_DrawbridgeMath.IsRaised(l.Span, i, l.progress, full);
					if (d.leafRaised != up)
					{
						d.leafRaised = up;
						(changed ?? (changed = new List<IntVec3>())).Add(c);
					}
				}
			}
			if (changed != null)
			{
				NotifyToggled(map, changed);
			}
		}

		/// <summary>R8, the pathing contract: a square that stopped or started being ground is seen by every path NOW. The path
		/// grid recosts it, reachability forgets, the climb generation moves (cliff masks follow it), the pocket grid is rebuilt
		/// at once instead of within 60 ticks, the swim grids re-derive, and every pawn holding a path (or a pending request)
		/// over a changed square is re-pathed.</summary>
		public static void NotifyToggled(Map map, List<IntVec3> changed)
		{
			ToggleCount++;
			foreach (IntVec3 c in changed)
			{
				map.pathing?.RecalculatePerceivedPathCostAt(c);
				map.mapDrawer?.MapMeshDirty(c, MapMeshFlagDefOf.Buildings);
				RM_MapComponent_SuspensionBridges.DirtyAround(map, c);
			}
			map.reachability?.ClearCache();
			RM_SuperdeepTrap.EngineOf(map)?.BumpClimbGeneration();
			Swimming.RM_SwimPathing.Bump(map);
			RM_PocketGrid.ForceRebuild(map);
			RepathOver(map, changed);
			map.GetComponent<Hose.RM_MapComponent_Hoses>()?.InvalidateEnds();   // phase 5: hoses on the leaf cut / rejoin now
		}

		/// <summary>A pawn whose path crosses a changed square, or whose path is still being computed (1.6 batches path jobs: a
		/// result computed before the toggle can arrive after it), is stopped and sent again to the same destination.</summary>
		public static void RepathOver(Map map, List<IntVec3> changed)
		{
			HashSet<IntVec3> cells = new HashSet<IntVec3>(changed);
			List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
			foreach (Pawn p in pawns)
			{
				Pawn_PathFollower pf = p?.pather;
				if (pf == null || !pf.Moving || !pf.Destination.IsValid)
				{
					continue;
				}
				bool hit = pf.curPathRequest != null;
				if (!hit && pf.curPath != null)
				{
					List<IntVec3> nodes = pf.curPath.NodesReversed;
					for (int i = 0; i < nodes.Count && !hit; i++)
					{
						hit = cells.Contains(nodes[i]);
					}
				}
				if (!hit)
				{
					continue;
				}
				if (p.HostileTo(Faction.OfPlayer) && p.GetLord() != null && p.jobs?.curJob != null)
				{
					// R5 / GPT #12: a raider's job holding a path over the leaf is ended, so its duty thinks again (and, with
					// nothing reachable, the trench rules or the winch givers take over)
					p.jobs.EndCurrentJob(JobCondition.InterruptForced);
					HostileJobsEnded++;
					continue;
				}
				LocalTargetInfo dest = pf.Destination;
				PathEndMode pe = PeMode(pf);
				pf.StopDead();
				pf.StartPath(dest, pe);
				RepathCount++;
			}
		}
			// ── Phase 2: the tip rule (R3) ──────────────────────────────────────────────────────────────

		/// <summary>Read by the functional script: pawns tipped onto a bank, hostiles tipped onto the colony bank ("pulled
		/// inside", answer 2), and overflow riders that fell.</summary>
		public static int TippedCount;
		public static int PulledInside;
		public static int FellCount;

		/// <summary>The colony bank: the first leaf made is the colony's (MakeDrawbridge adds it first).</summary>
		public static bool ColonyBankAtFirst(SuspensionBridgeRecord r)
		{
			return !r.IsDrawbridge || r.leaves[0].hingeAtFirst;
		}

		/// <summary>The bridge index of the anchor squares this leaf hinges on.</summary>
		public static int HingeIndex(DrawbridgeLeaf l)
		{
			return l.hingeAtFirst ? l.first - 1 : l.last + 1;
		}

		/// <summary>R3: everyone riding the leaf (chosen by band: PawnsOn skips the floor band underneath, flyers and the dead)
		/// goes, nearest the hinge first, to the nearest free standable square on the hinge bank reachable from the anchors
		/// without passing a wall, a closed door or the bridge itself, keeping faction, gear and job-free; no fall damage. Items
		/// slide to the hinge bank, or stay (and go down with the leaf) when it is full. Returns the overflow, who fall once the
		/// squares are hole (Fall). Never a collapse: no deck is destroyed. preview (4 slots): the plan only, nothing moved:
		/// riders, landers, fallers, free bank squares (RM_DrawbridgeProofs.ProofTipPreview reads the production plan).</summary>
		public static List<Pawn> Tip(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l, int[] preview = null)
		{
			List<Pawn> fallers = new List<Pawn>();
			if (map == null)
			{
				return fallers;
			}
			LeafSpan span = l.Span;
			CellIndices ci = map.cellIndices;
			List<RM_DrawbridgeMath.Rider> riders = new List<RM_DrawbridgeMath.Rider>();
			Dictionary<int, Pawn> byId = new Dictionary<int, Pawn>();
			List<Thing> items = new List<Thing>();
			HashSet<IntVec3> bridgeDeck = new HashSet<IntVec3>();
			for (int lane = 0; lane < r.width; lane++)
			{
				for (int i = 1; i <= r.length - 2; i++)
				{
					bridgeDeck.Add(r.Cell(lane, i));
				}
				for (int i = l.first; i <= l.last; i++)
				{
					IntVec3 c = r.Cell(lane, i);
					foreach (Pawn p in RM_MapComponent_SuspensionBridges.PawnsOn(map, c))
					{
						if (!byId.ContainsKey(p.thingIDNumber))
						{
							byId[p.thingIDNumber] = p;
							riders.Add(new RM_DrawbridgeMath.Rider(p.thingIDNumber, span.FromHinge(i), ci.CellToIndex(c)));
						}
					}
					foreach (Thing t in c.GetThingList(map))
					{
						if (t.def.category == ThingCategory.Item)
						{
							items.Add(t);
						}
					}
				}
			}
			int hinge = HingeIndex(l);
			List<int> starts = new List<int>();
			for (int lane = 0; lane < r.width; lane++)
			{
				IntVec3 a = r.Cell(lane, hinge);
				if (a.InBounds(map))
				{
					starts.Add(ci.CellToIndex(a));
				}
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			System.Func<int, IEnumerable<int>> neighbours = idx => Cardinals(map, ci.IndexToCell(idx));
			System.Func<int, bool> passable = idx =>
			{
				IntVec3 c = ci.IndexToCell(idx);
				if (bridgeDeck.Contains(c) || !c.Walkable(map))
				{
					return false;
				}
				if (c.GetDoor(map) is Building_Door door && !door.Open)
				{
					return false;   // never through a closed gate or door
				}
				return eng == null || eng.ClimbDepthAt(c) == 0 || RM_SpanUtility.DeckedAt(map, c);
			};
			System.Func<int, bool> free = idx =>
			{
				IntVec3 c = ci.IndexToCell(idx);
				return c.Standable(map) && c.GetFirstPawn(map) == null && c.GetDoor(map) == null;
			};
			List<int> landings = RM_DrawbridgeMath.BankLandings(starts, neighbours, passable, free, RM_DrawbridgeMath.TipReach);
			Dictionary<int, int> to = RM_DrawbridgeMath.AssignTips(riders, landings);
			if (preview != null && preview.Length >= 4)
			{
				int land = 0;
				foreach (int v in to.Values)
				{
					if (v >= 0)
					{
						land++;
					}
				}
				preview[0] = riders.Count;
				preview[1] = land;
				preview[2] = riders.Count - land;
				preview[3] = landings.Count;
				return fallers;
			}
			bool colonyBank = l.hingeAtFirst == ColonyBankAtFirst(r);
			int tipped = 0, pulled = 0;
			foreach (RM_DrawbridgeMath.Rider rd in RM_DrawbridgeMath.TipOrder(riders))
			{
				Pawn p = byId[rd.Id];
				if (to[rd.Id] < 0)
				{
					fallers.Add(p);
					continue;
				}
				p.Position = ci.IndexToCell(to[rd.Id]);
				p.Notify_Teleported(true, true);
				tipped++;
				if (colonyBank && p.HostileTo(Faction.OfPlayer))
				{
					pulled++;
				}
			}
			if (items.Count > 0 && starts.Count > 0)
			{
				HashSet<IntVec3> bank = new HashSet<IntVec3>();
				foreach (int idx in RM_DrawbridgeMath.BankLandings(starts, neighbours, passable, i => ci.IndexToCell(i).Standable(map),
					RM_DrawbridgeMath.TipReach))
				{
					bank.Add(ci.IndexToCell(idx));
				}
				IntVec3 h = ci.IndexToCell(starts[0]);
				foreach (Thing t in items)
				{
					if (t.Destroyed || !t.Spawned)
					{
						continue;
					}
					IntVec3 was = t.Position;
					t.DeSpawn();
					if (!GenPlace.TryPlaceThing(t, h, map, ThingPlaceMode.Near, null, c => bank.Contains(c), null, RM_DrawbridgeMath.TipReach + 1))
					{
						GenSpawn.Spawn(t, was, map);   // the bank is full: it goes down with the leaf
					}
				}
			}
			TippedCount += tipped;
			PulledInside += pulled;
			if (tipped + fallers.Count > 0)
			{
				string msg = "The drawbridge tipped " + tipped + " onto its hinge bank" + (pulled > 0 ? " (" + pulled + " hostile pulled inside)" : "")
					+ (fallers.Count > 0 ? "; " + fallers.Count + " found no room and fell into the pit." : ".");
				List<Thing> look = new List<Thing>(byId.Values);
				Messages.Message(msg, new LookTargets(look), fallers.Count > 0 ? MessageTypeDefOf.NegativeEvent : MessageTypeDefOf.NeutralEvent);
			}
			return fallers;
		}

		private static IEnumerable<int> Cardinals(Map map, IntVec3 c)
		{
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = c + GenAdj.CardinalDirections[i];
				if (n.InBounds(map))
				{
					yield return map.cellIndices.CellToIndex(n);
				}
			}
		}

		/// <summary>The overflow falls through the pit's ordinary descent event (fall damage by metres, the pit's own rules), from
		/// the deck's height on a sunken bridge. Called after Apply, when their squares are already open hole.</summary>
		public static void Fall(Map map, SuspensionBridgeRecord r, List<Pawn> fallers)
		{
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			RM_SuperdeepTrapState state = eng?.SuperdeepTrap;
			if (state == null)
			{
				return;
			}
			foreach (Pawn p in fallers)
			{
				if (p == null || !p.Spawned || p.Dead || p.Flying)
				{
					continue;
				}
				int drop = r.deckNotches > 0 ? System.Math.Max(0, eng.ClimbDepthAt(p.Position) - r.deckNotches) : -1;
				RM_SuperdeepTrap.OnForcedDescent(p, p.Position, state, drop);
				FellCount++;
			}
		}

		// ── Phase 3: control mode (R4), winch loss ───────────────────────────────────────────────

		private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Map, int[]> lastLocked =
			new System.Runtime.CompilerServices.ConditionalWeakTable<Map, int[]>();

		/// <summary>Is this map locked (any free hostile, R4)?</summary>
		public static bool Locked(Map map)
		{
			return FreeHostileCount(map, false) > 0;
		}

		/// <summary>Per map: [0] the free-hostile count, [1] the tick it was read (weak: a dropped map is not kept alive).</summary>
		private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Map, int[]> hostileRead =
			new System.Runtime.CompilerServices.ConditionalWeakTable<Map, int[]>();

		/// <summary>Free hostiles on the map (R4, review answer 3): active hostile threats to the colony that the pit engine does
		/// not hold trapped and that are not prisoners. fresh: count now (the commit-time check); else the count is re-read at
		/// most every ModeCheckInterval ticks.</summary>
		public static int FreeHostileCount(Map map, bool fresh)
		{
			if (map == null)
			{
				return 0;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			int[] read = hostileRead.GetValue(map, _ => new[] { 0, int.MinValue / 2 });
			if (!fresh && now - read[1] < RM_DrawbridgeMath.ModeCheckInterval)
			{
				return read[0];
			}
			int n = 0;
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (!p.HostileTo(Faction.OfPlayer))
				{
					continue;
				}
				bool threat = GenHostility.IsActiveThreatTo(p, Faction.OfPlayer);
				if (RM_DrawbridgeMath.IsFreeHostile(threat, threat && RM_SuperdeepTrap.IsTrapped(p), p.IsPrisoner))
				{
					n++;
				}
			}
			read[0] = n;
			read[1] = now;
			return n;
		}

		/// <summary>R4 for one leaf: locking cancels a pending automatic lower (back to raised); in peace a leaf that is up and
		/// not held lowers itself, the hostile check made again at the moment it commits.</summary>
		private static void Mode(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l, int now)
		{
			bool locked = FreeHostileCount(map, false) > 0;
			int[] seen = lastLocked.GetValue(map, _ => new[] { -1 });
			if (seen[0] != (locked ? 1 : 0))
			{
				seen[0] = locked ? 1 : 0;
				map.reachability?.ClearCache();   // phase 6: drawbridge gates open for nobody while locked (R4, R7)
			}
			if (RM_DrawbridgeMath.ShouldCancelAutoLower(locked, l.autoLowering))
			{
				l.targetRaised = true;
				l.autoLowering = false;
				return;
			}
			if (RM_DrawbridgeMath.ShouldAutoLower(locked, l.holdRaised, l.progress, l.targetRaised, l.autoLowering)
				&& l.pendingOrder != RM_DrawbridgeMath.OrderRaise && FreeHostileCount(map, true) == 0)
			{
				l.targetRaised = false;
				l.autoLowering = true;
			}
		}

		/// <summary>A winch house was built: it takes the leaf whose hinge anchor it stands beside (one winch per leaf).</summary>
		public static void LinkWinch(Building_DrawbridgeWinch w)
		{
			RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(w.Map);
			if (comp == null)
			{
				return;
			}
			foreach (SuspensionBridgeRecord r in comp.Bridges)
			{
				if (!r.IsDrawbridge)
				{
					continue;
				}
				foreach (DrawbridgeLeaf l in r.leaves)
				{
					if (l.winch != null && l.winch.Spawned)
					{
						continue;
					}
					for (int lane = 0; lane < r.width; lane++)
					{
						if (w.Position.AdjacentToCardinal(r.Cell(lane, HingeIndex(l))))
						{
							l.winch = w;
							return;
						}
					}
				}
			}
		}

		/// <summary>Phase 6 (R7): the leaf a gate stands at: the gate is cardinally beside one of the leaf's hinge anchors.</summary>
		public static bool LeafOfGate(Building gate, out SuspensionBridgeRecord rec, out DrawbridgeLeaf leaf)
		{
			rec = null;
			leaf = null;
			RM_MapComponent_SuspensionBridges comp = gate?.Map == null ? null : RM_MapComponent_SuspensionBridges.Of(gate.Map);
			if (comp == null)
			{
				return false;
			}
			foreach (SuspensionBridgeRecord r in comp.Bridges)
			{
				if (!r.IsDrawbridge)
				{
					continue;
				}
				foreach (DrawbridgeLeaf l in r.leaves)
				{
					for (int lane = 0; lane < r.width; lane++)
					{
						if (gate.Position.AdjacentToCardinal(r.Cell(lane, HingeIndex(l))))
						{
							rec = r;
							leaf = l;
							return true;
						}
					}
				}
			}
			return false;
		}

		/// <summary>The leaf (and its bridge) a winch house works, or false.</summary>
		public static bool LeafOfWinch(Building_DrawbridgeWinch w, out SuspensionBridgeRecord rec, out DrawbridgeLeaf leaf)
		{
			rec = null;
			leaf = null;
			RM_MapComponent_SuspensionBridges comp = w?.Map == null ? null : RM_MapComponent_SuspensionBridges.Of(w.Map);
			if (comp == null)
			{
				return false;
			}
			foreach (SuspensionBridgeRecord r in comp.Bridges)
			{
				if (r.IsDrawbridge)
				{
					foreach (DrawbridgeLeaf l in r.leaves)
					{
						if (l.winch == w)
						{
							rec = r;
							leaf = l;
							return true;
						}
					}
				}
			}
			return false;
		}

		/// <summary>Owner follow-up (2026-10-20): a destroyed winch house crashes its leaf down, and anything under it is hit.
		/// Steel losing only its power still freezes (Tick).</summary>
		public static void Notify_WinchLost(Map map, Building_DrawbridgeWinch w)
		{
			RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(map);
			if (comp == null)
			{
				return;
			}
			foreach (SuspensionBridgeRecord r in comp.Bridges)
			{
				if (!r.IsDrawbridge)
				{
					continue;
				}
				foreach (DrawbridgeLeaf l in r.leaves)
				{
					if (l.winch != w)
					{
						continue;
					}
					l.winch = null;
					if (RM_DrawbridgeMath.WinchLossCrashes(l.progress))
					{
						Crash(map, r, l);
					}
				}
			}
		}

		public static int CrashCount;
		public static int CrashHits;

		/// <summary>The leaf slams down to lowered at once: everyone on its squares (down in the hole under it; nobody rides a
		/// raised leaf) is hit like a falling bridge square. The deck is not destroyed; it is ground again.</summary>
		public static void Crash(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			List<Pawn> hit = new List<Pawn>();
			for (int lane = 0; lane < r.width; lane++)
			{
				for (int i = l.first; i <= l.last; i++)
				{
					foreach (Thing t in r.Cell(lane, i).GetThingList(map))
					{
						if (t is Pawn p && !p.Dead && !p.Flying)
						{
							hit.Add(p);
						}
					}
				}
			}
			l.progress = 0;
			l.targetRaised = false;
			l.tipCommitted = false;
			l.autoLowering = false;
			l.holdRaised = false;
			l.pendingOrder = RM_DrawbridgeMath.OrderNone;
			Apply(map, r, l);
			foreach (Pawn p in hit)
			{
				if (!p.Spawned || p.Dead)
				{
					continue;
				}
				var dinfo = new DamageInfo(DamageDefOf.Crush, Rand.RangeInclusive(RM_SuspensionMath.CrushDamageMin, RM_SuspensionMath.CrushDamageMax),
					0f, -1f, null, null, null, DamageInfo.SourceCategory.Collapse);
				dinfo.SetBodyRegion(BodyPartHeight.Top, BodyPartDepth.Outside);
				p.TakeDamage(dinfo);
				CrashHits++;
			}
			CrashCount++;
			Messages.Message("A drawbridge lost its winch house and crashed down" + (hit.Count > 0 ? " on " + hit.Count + "." : "."),
				new TargetInfo(r.Cell(0, l.first), map), MessageTypeDefOf.NegativeEvent);
		}

		/// <summary>The readout lines for one leaf (R11).</summary>
		public static string InspectLine(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			int full = FullTicks(r, l);
			int n = FreeHostileCount(map, false);
			string s = "Drawbridge leaf: " + RM_DrawbridgeMath.StateLine(l.progress, l.targetRaised, full, l.frozen);
			if (l.frozen)
			{
				s += " (no power)";
			}
			if (l.winch == null || !l.winch.Spawned)
			{
				s += "\nNo winch house: build one beside the hinge anchor";
			}
			if (l.pendingOrder != RM_DrawbridgeMath.OrderNone)
			{
				s += "\nWaiting for a colonist to " + (l.pendingOrder == RM_DrawbridgeMath.OrderRaise ? "raise" : "lower (winch bank only)") + " it";
			}
			return s + "\n" + RM_DrawbridgeMath.LockLine(n > 0, n, l.holdRaised);
		}

		/// <summary>The player's controls for one leaf: raise, lower (carried out by a colonist), hold raised.</summary>
		public static IEnumerable<Gizmo> Gizmos(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			if (map == null || r == null || l == null)
			{
				yield break;
			}
			yield return new Command_Action
			{
				defaultLabel = "Raise drawbridge",
				defaultDesc = "A colonist raises this leaf, from either bank (timber by hand at the winch, steel by its powered winch). "
					+ "Anyone on it is tipped onto the hinge bank; whoever finds no room falls into the pit. Raised in peacetime, it stays up; "
					+ "raised while hostiles are about, it lowers itself for your people once they are gone.",
				icon = RM_DrawbridgeArt.Icon("RM_DrawbridgeRaise", TexCommand.ForbidOff),
				action = () => Order(map, r, l, true),
			};
			yield return new Command_Action
			{
				defaultLabel = "Lower drawbridge",
				defaultDesc = "A colonist lowers this leaf. Only from the winch house's bank.",
				icon = RM_DrawbridgeArt.Icon("RM_DrawbridgeLower", TexCommand.ForbidOn),
				action = () => Order(map, r, l, false),
			};
			yield return new Command_Toggle
			{
				defaultLabel = "Hold raised",
				defaultDesc = "In peacetime a drawbridge lowers itself for your people. Hold raised keeps it up.",
				icon = RM_DrawbridgeArt.Icon("RM_DrawbridgeHoldRaised", TexCommand.HoldOpen),
				isActive = () => l.holdRaised,
				toggleAction = () => l.holdRaised = !l.holdRaised,
			};
		}

		// ── Phase 5: lines on a leaf (review answer 6) ───────────────────────────────────────────

		/// <summary>Is any of these cells a raised drawbridge leaf square? A flexible line (hose; the power cord of
		/// POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS reads this too) lying over one is disconnected while it is up.</summary>
		public static bool LineCutAt(Map map, IEnumerable<IntVec3> cells)
		{
			if (map == null || cells == null || !AnyRaised(map))
			{
				return false;
			}
			foreach (IntVec3 c in cells)
			{
				Building_SuspensionDeck d = RM_MapComponent_SuspensionBridges.StructuralDeckAt(map, c);
				if (d != null && d.Raised)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Any leaf on the map off its seat (the cheap gate before a per-cell read).</summary>
		public static bool AnyRaised(Map map)
		{
			RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(map);
			if (comp == null)
			{
				return false;
			}
			foreach (SuspensionBridgeRecord r in comp.Bridges)
			{
				if (r.IsDrawbridge)
				{
					foreach (DrawbridgeLeaf l in r.leaves)
					{
						if (l.progress > 0)
						{
							return true;
						}
					}
				}
			}
			return false;
		}

		/// <summary>A laid hose whose walked trail (or, for a planned hose with no trail, the straight line from reel to end)
		/// crosses a raised leaf square.</summary>
		public static bool HoseCut(Hose.CompHoseReel r)
		{
			Map map = r?.parent?.Map;
			if (map == null || !r.laid || !AnyRaised(map))
			{
				return false;
			}
			if (r.trail != null && r.trail.Count > 0)
			{
				return LineCutAt(map, r.trail);
			}
			return LineCutAt(map, GenSight.PointsOnLineOfSight(r.parent.Position, r.far));
		}

		/// <summary>The gizmos a selected deck square shows: its leaf's controls, then the dev tools.</summary>
		public static IEnumerable<Gizmo> DeckGizmos(Map map, SuspensionBridgeRecord r, IntVec3 at)
		{
			if (r != null && r.IsDrawbridge && r.TryIndexOf(at, out _, out int i) && LeafOf(r, i) is DrawbridgeLeaf l)
			{
				foreach (Gizmo g in Gizmos(map, r, l))
				{
					yield return g;
				}
			}
			foreach (Gizmo g in DevGizmos(map, r))
			{
				yield return g;
			}
		}

		/// <summary>Phase 1 has no player controls yet (phase 3 adds the winch job and the sided orders): god-mode gizmos to make
		/// a bridge a drawbridge and to raise or lower each leaf, for the functional script and a joint look.</summary>
		public static IEnumerable<Gizmo> DevGizmos(Map map, SuspensionBridgeRecord r)
		{
			if (!DebugSettings.godMode || map == null || r == null)
			{
				yield break;
			}
			if (!r.IsDrawbridge)
			{
				if (CanBeDrawbridge(r, out _))
				{
					yield return new Command_Action
					{
						defaultLabel = "DEV: make drawbridge",
						action = () =>
						{
							if (!MakeDrawbridge(r, true, out string why))
							{
								Messages.Message("Not a drawbridge: " + why, MessageTypeDefOf.RejectInput, false);
							}
						},
					};
				}
				yield break;
			}
			for (int k = 0; k < r.leaves.Count; k++)
			{
				DrawbridgeLeaf l = r.leaves[k];
				yield return new Command_Action
				{
					defaultLabel = "DEV: " + (l.targetRaised ? "lower" : "raise") + " leaf " + (k + 1),
					action = () => DevSetTarget(l, !l.targetRaised),
				};
			}
		}
	}
}

