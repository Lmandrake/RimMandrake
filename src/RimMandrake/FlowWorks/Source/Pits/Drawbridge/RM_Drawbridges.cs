using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

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

		public static float SpeedMultiplier => 1f;

		public static int MaxLeaf(SuspensionTier t)
		{
			return RM_DrawbridgeMath.DefaultMaxLeaf(t);
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

		/// <summary>Set a leaf's target. Phase 1 is the order itself; who may give it and from which bank is phase 3's.</summary>
		public static void Order(SuspensionBridgeRecord r, DrawbridgeLeaf l, bool raise)
		{
			if (r == null || l == null)
			{
				return;
			}
			l.targetRaised = raise;
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
					if (l.frozen || RM_DrawbridgeMath.AtTarget(l.progress, l.targetRaised, full))
					{
						continue;
					}
					l.progress = RM_DrawbridgeMath.Step(l.progress, l.targetRaised, full, TickInterval);
					if (l.progress == 0)
					{
						l.tipCommitted = false;
					}
					Apply(comp.map, r, l);
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
				LocalTargetInfo dest = pf.Destination;
				PathEndMode pe = PeMode(pf);
				pf.StopDead();
				pf.StartPath(dest, pe);
				RepathCount++;
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
					action = () => Order(r, l, !l.targetRaised),
				};
			}
		}
	}
}

