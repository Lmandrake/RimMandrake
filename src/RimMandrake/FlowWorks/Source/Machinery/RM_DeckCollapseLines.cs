using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>
	/// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 3 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P4):
	/// a deck that collapses destroys the cords and hoses on its squares, and a live cord it drops is a live fallen wire.
	///
	/// SUPPORT-OWNED: the deck is the support, and every way a deck gives way clears its squares through ONE call,
	/// RM_MapComponent_SuspensionBridges.ClearDeckTop (span collapse from a broken or deconstructed square, a lost anchor,
	/// the gravship launch tearing an edge bridge loose, the weight overload, and the one-square swing-down DropAlone). It
	/// calls <see cref="OnDeckCleared"/> FIRST, while the cords still stand, then destroys every building on the square as it
	/// always has (so the power net splits once, through vanilla's despawn path). A drawbridge leaf crashing down after its
	/// winch is lost (RM_Drawbridges.Crash) is NOT a collapse: the deck stays and its cords rejoin through the leaf toggle.
	///
	/// IDEMPOTENT: a cord already destroyed or a hose already reeled in is skipped, and a fallen square is recorded once, so
	/// clearing a square twice (or a collapse racing a swing-down) tears down nothing twice.
	///
	/// THE LIVE WIRE: the dropped cord's squares are kept by <see cref="RM_MapComponent_FallenCords"/>, each run split between
	/// the standing lines it hangs from (RM_DeckCollapseLinesMath.Split, one half per bank). A half is live while its end
	/// stands on a real, powered net (RM_DeckCollapseLinesMath.Live): it is never powered through a stale edge. The shock and
	/// the fuel ignition are Gimme Some Slack's own (RM_FallenWireShock): FlowWorks hands it the live cells through
	/// <see cref="RM_GssLiveWire"/>, a soft-reflection seam, so FlowWorks loads and runs without GSS (the cord still falls; there
	/// is nothing to shock with).
	///
	/// Setting RM_MachinerySettings.lineCrossingRulesEnabled; off, the deck still destroys what stands on it (its pre-ruling
	/// behaviour) but no hose is reeled in and no fallen cord is live.
	/// </summary>
	public static class RM_DeckCollapseLines
	{
		/// <summary>State reads for the functional script: cords dropped by collapsing decks, hoses reeled in by them, and the
		/// collapse squares that tore down at least one line.</summary>
		public static int CordsDropped, HosesCut, SquaresThatTore;

		public const string HoseCutReason = "the bridge deck it lay on collapsed";

		/// <summary>Called by ClearDeckTop before it destroys anything on the square.</summary>
		public static int OnDeckCleared(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map) || !RM_MachinerySettings.lineCrossingRulesEnabled)
			{
				return 0;
			}
			List<Thing> cords = RM_DeckCollapseLinesMath.CordsToDrop(true, new List<Thing>(c.GetThingList(map)), KindOfBuilt,
				t => t.Destroyed || !t.Spawned);
			int torn = 0;
			if (cords.Count > 0)
			{
				map.GetComponent<RM_MapComponent_FallenCords>()?.Notify_CordFell(c);
				CordsDropped += cords.Count;
				torn += cords.Count;
			}
			RM_MapComponent_Hoses hoses = map.GetComponent<RM_MapComponent_Hoses>();
			if (hoses != null)
			{
				foreach (CompHoseReel r in new List<CompHoseReel>(hoses.Reels))
				{
					if (r?.parent == null || !r.parent.Spawned || !RM_DeckCollapseLinesMath.HoseCrosses(r.laid, PathOf(r), c.x, c.z))
					{
						continue;
					}
					r.Retract(HoseCutReason);
					HosesCut++;
					torn++;
				}
			}
			if (torn > 0)
			{
				SquaresThatTore++;
			}
			return torn;
		}

		private static IEnumerable<(int X, int Z)> PathOf(CompHoseReel r)
		{
			if (!r.laid || !r.far.IsValid)
			{
				yield break;
			}
			if (r.trail != null && r.trail.Count > 0)
			{
				foreach (IntVec3 p in r.trail)
				{
					yield return (p.x, p.z);
				}
				yield break;
			}
			foreach (IntVec3 p in GenSight.PointsOnLineOfSight(r.parent.Position, r.far))
			{
				yield return (p.x, p.z);
			}
		}

		/// <summary>A BUILT line's kind (blueprints and frames answer null: ClearDeckTop removes those itself).</summary>
		private static LineKind? KindOfBuilt(Thing t)
		{
			if (t is Blueprint || t is Frame || t.def.category != ThingCategory.Building)
			{
				return null;
			}
			return RM_LineCrossing.KindOf(t.def);
		}
	}

	/// <summary>One fallen half: the standing line it hangs from, the squares it lies across, its tip.</summary>
	public class RM_FallenCordHalf : IExposable
	{
		public Thing end;
		public List<IntVec3> cells = new List<IntVec3>();
		public IntVec3 tip = IntVec3.Invalid;

		public void ExposeData()
		{
			Scribe_References.Look(ref end, "end");
			Scribe_Collections.Look(ref cells, "cells", LookMode.Value);
			Scribe_Values.Look(ref tip, "tip", IntVec3.Invalid);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && cells == null)
			{
				cells = new List<IntVec3>();
			}
		}
	}

	/// <summary>
	/// The cords collapsing decks dropped on this map (RM_DeckCollapseLines). Fallen squares are bound to the lines they hang
	/// from on the tick after they fall (when every square of the collapse has gone); a half whose end is lost is re-bound with
	/// any newly fallen squares next to it (a swing-down drops a deck one square at a time), and squares no standing line holds
	/// are forgotten: a dead wire never comes back to life. A square a deck stands on again is forgotten too.
	/// </summary>
	public class RM_MapComponent_FallenCords : MapComponent
	{
		private List<RM_FallenCordHalf> halves = new List<RM_FallenCordHalf>();
		private List<IntVec3> pending = new List<IntVec3>();
		private bool rebind;

		/// <summary>State reads: binds that dropped at least one live half (one per collapse), and the live halves they made.</summary>
		public static int LiveFalls, LiveHalvesMade;

		public RM_MapComponent_FallenCords(Map map) : base(map) { }

		public IReadOnlyList<RM_FallenCordHalf> Halves => halves;

		public override void ExposeData()
		{
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				halves.RemoveAll(h => !EndStanding(map, h.end));   // a dead half is never saved (no reference to a destroyed end)
			}
			Scribe_Collections.Look(ref halves, "rmFallenCordHalves", LookMode.Deep);
			Scribe_Collections.Look(ref pending, "rmFallenCordPending", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				halves = halves ?? new List<RM_FallenCordHalf>();
				halves.RemoveAll(h => h == null);
				pending = pending ?? new List<IntVec3>();
			}
		}

		public override void FinalizeInit()
		{
			RM_GssLiveWire.EnsureRegistered();
		}

		/// <summary>A cord on c fell with its deck. Recorded once.</summary>
		public void Notify_CordFell(IntVec3 c)
		{
			if (pending.Contains(c) || Holds(c))
			{
				return;
			}
			pending.Add(c);
			rebind = true;
		}

		/// <summary>Did a cord fall on c (pending bind or held by a half)? Read by LandWreck: the fallen cord lies on top of the
		/// rubble, so that square is left walkable (FALLEN_CORD_BUILD_RUBBLE_IS_NO_SHIELD).</summary>
		public bool CordFellAt(IntVec3 c) => pending.Contains(c) || Holds(c);

		private bool Holds(IntVec3 c)
		{
			foreach (RM_FallenCordHalf h in halves)
			{
				if (h.cells.Contains(c))
				{
					return true;
				}
			}
			return false;
		}

		public override void MapComponentTick()
		{
			if (rebind || pending.Count > 0)
			{
				rebind = false;
				Bind();
			}
			if (halves.Count > 0 && Find.TickManager.TicksGame % 250 == (map.uniqueID * 11 + 97) % 250)
			{
				Sweep();
			}
		}

		private static bool EndStanding(Map map, Thing end) => end != null && !end.Destroyed && end.Spawned && end.Map == map;

		/// <summary>Is this half a live wire right now?</summary>
		public bool Live(RM_FallenCordHalf h)
		{
			bool standing = EndStanding(map, h.end);
			PowerNet n = standing ? (h.end as Building)?.PowerComp?.PowerNet : null;
			bool registered = n != null && map.powerNetManager != null && map.powerNetManager.AllNetsListForReading.Contains(n);
			return RM_DeckCollapseLinesMath.Live(RM_MachinerySettings.lineCrossingRulesEnabled, standing, registered,
				registered && n.HasActivePowerSource);
		}

		/// <summary>The contact squares of every live half (square -> its live tip), for RM_FallenWireShock.</summary>
		public IEnumerable<KeyValuePair<IntVec3, IntVec3>> LiveContacts()
		{
			foreach (RM_FallenCordHalf h in halves)
			{
				if (!Live(h))
				{
					continue;
				}
				foreach (IntVec3 c in h.cells)
				{
					yield return new KeyValuePair<IntVec3, IntVec3>(c, h.tip);
				}
			}
		}

		/// <summary>The 250-tick sweep: forget squares a deck stands on again, re-bind halves whose end was lost, and let a live
		/// tip spark now and then so the wire is never an invisible hazard.</summary>
		private void Sweep()
		{
			bool changed = false;
			foreach (RM_FallenCordHalf h in halves)
			{
				changed |= h.cells.RemoveAll(c => !c.InBounds(map) || DeckedAt(c)) > 0;
				if (!EndStanding(map, h.end))
				{
					rebind = true;
				}
			}
			int before = halves.Count;
			halves.RemoveAll(h => h.cells.Count == 0);
			changed |= halves.Count != before;
			foreach (RM_FallenCordHalf h in halves)
			{
				if (h.tip.IsValid && h.tip.InBounds(map) && Rand.Chance(0.5f) && Live(h))
				{
					FleckMaker.ThrowMicroSparks(h.tip.ToVector3Shifted(), map);
				}
			}
			if (changed)
			{
				RM_GssLiveWire.Changed(map);
			}
		}

		private bool DeckedAt(IntVec3 c)
		{
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Building_SpanDeck d && d.Decked)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Bind the fallen squares to the standing lines they hang from. Squares in play: the newly fallen ones plus those
		/// of halves whose end is lost; halves with a standing end keep theirs untouched.</summary>
		private void Bind()
		{
			var loose = new List<(int X, int Z)>();
			foreach (IntVec3 c in pending)
			{
				loose.Add((c.x, c.z));
			}
			pending.Clear();
			for (int i = halves.Count - 1; i >= 0; i--)
			{
				if (!EndStanding(map, halves[i].end))
				{
					foreach (IntVec3 c in halves[i].cells)
					{
						loose.Add((c.x, c.z));
					}
					halves.RemoveAt(i);
				}
			}
			int live = 0;
			foreach (List<(int X, int Z)> run in RM_DeckCollapseLinesMath.Runs(loose))
			{
				var ends = new List<Thing>();
				var endCells = new List<(int X, int Z)>();
				var inRun = new HashSet<long>();
				foreach ((int X, int Z) c in run)
				{
					inRun.Add(RM_DeckCollapseLinesMath.Key(c.X, c.Z));
				}
				foreach ((int X, int Z) c in run)
				{
					foreach (IntVec3 d in GenAdj.CardinalDirections)
					{
						IntVec3 n = new IntVec3(c.X, 0, c.Z) + d;
						if (!n.InBounds(map) || inRun.Contains(RM_DeckCollapseLinesMath.Key(n.x, n.z)) || Holds(n))
						{
							continue;
						}
						Thing e = StandingLineAt(n);
						if (e != null && !ends.Contains(e))
						{
							ends.Add(e);
							endCells.Add((n.x, n.z));
						}
					}
				}
				foreach (RM_DeckCollapseLinesMath.Half part in RM_DeckCollapseLinesMath.Split(run, endCells))
				{
					var h = new RM_FallenCordHalf { end = ends[part.End], tip = new IntVec3(part.Tip.X, 0, part.Tip.Z) };
					foreach ((int X, int Z) c in part.Cells)
					{
						h.cells.Add(new IntVec3(c.X, 0, c.Z));
					}
					halves.Add(h);
					if (Live(h))
					{
						live++;
					}
				}
			}
			if (live > 0)
			{
				LiveFalls++;
				LiveHalvesMade += live;
				Messages.Message(RM_DeckCollapseLinesMath.LiveMessage(live), new TargetInfo(halves[halves.Count - 1].tip, map),
					MessageTypeDefOf.NegativeEvent, false);
			}
			RM_GssLiveWire.Changed(map);
		}

		/// <summary>The standing line a dropped cord can hang from: any built power transmitter (cord, conduit, battery...).</summary>
		private Thing StandingLineAt(IntVec3 c)
		{
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Building b && !b.Destroyed && b.def.EverTransmitsPower && b.PowerComp != null)
				{
					return b;
				}
			}
			return null;
		}
	}

	/// <summary>
	/// The soft seam into Gimme Some Slack's fallen-wire shock (design §P3: GSS and FlowWorks talk by soft reflection, the way
	/// GSS already reaches FlowWorks' liquid fire). FlowWorks has no compile-time reference to GSS: it looks up GSS's public
	/// entry points RM_FallenWireShock.RegisterLiveWireSource and LiveWiresChanged by name, once. GSS absent or renamed: the
	/// lookup finds nothing, one log line says so, and the fallen cord is simply not a shock source.
	/// </summary>
	public static class RM_GssLiveWire
	{
		public const string GssShockType = "RimMandrake.GimmeSomeSlack.Aerial.RM_FallenWireShock";
		private static bool resolved;
		private static MethodInfo changed;
		public static bool Registered { get; private set; }

		private static IEnumerable<KeyValuePair<IntVec3, IntVec3>> Source(Map map) =>
			map?.GetComponent<RM_MapComponent_FallenCords>()?.LiveContacts() ?? new KeyValuePair<IntVec3, IntVec3>[0];

		public static void EnsureRegistered()
		{
			if (resolved)
			{
				return;
			}
			resolved = true;
			try
			{
				Type t = GenTypes.GetTypeInAnyAssembly(GssShockType);
				if (t == null)
				{
					return;   // GSS not loaded: nothing to shock with, and nothing to say
				}
				MethodInfo reg = t.GetMethod("RegisterLiveWireSource", BindingFlags.Public | BindingFlags.Static, null,
					new[] { typeof(Func<Map, IEnumerable<KeyValuePair<IntVec3, IntVec3>>>) }, null);
				changed = t.GetMethod("LiveWiresChanged", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(Map) }, null);
				if (reg == null)
				{
					Log.Warning("[FlowWorks] Gimme Some Slack is loaded but RM_FallenWireShock.RegisterLiveWireSource was not found; "
						+ "a power cord dropped by a collapsing bridge will not shock anyone.");
					return;
				}
				reg.Invoke(null, new object[] { new Func<Map, IEnumerable<KeyValuePair<IntVec3, IntVec3>>>(Source) });
				Registered = true;
			}
			catch (Exception e)
			{
				Log.Warning("[FlowWorks] fallen-cord shock lookup into Gimme Some Slack failed; dropped cords will not shock: " + e.Message);
			}
		}

		/// <summary>Tell GSS the live cells changed, so its contacts follow at once instead of at its next sweep.</summary>
		public static void Changed(Map map)
		{
			EnsureRegistered();
			if (changed == null || map == null)
			{
				return;
			}
			try
			{
				changed.Invoke(null, new object[] { map });
			}
			catch (Exception e)
			{
				Log.ErrorOnce("[FlowWorks] RM_FallenWireShock.LiveWiresChanged threw; contacts will follow at GSS's sweep: " + e.Message, 0x4C1F0D);
				changed = null;
			}
		}
	}
}
