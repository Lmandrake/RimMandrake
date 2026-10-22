using System.Collections.Generic;
using RimWorld;
using Verse;
using UnityEngine;
using Verse.AI;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>The material of a drawbridge part (its own extension: RM_SuspensionExtension marks suspension-bridge parts,
	/// which the drag designator and the part reads treat as the bridge itself).</summary>
	public class RM_DrawbridgeExtension : DefModExtension
	{
		public SuspensionTier tier = SuspensionTier.Timber;
	}

	[DefOf]
	public static class RM_DrawbridgeDefOf
	{
		public static JobDef RM_WorkDrawbridge;
		public static ThingDef RM_DrawbridgeWinch_Timber;
		public static ThingDef RM_DrawbridgeWinch_Steel;

		static RM_DrawbridgeDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_DrawbridgeDefOf));
		}
	}

	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS phase 3 (R2, owner follow-ups 2026-10-20): the winch house of ONE leaf, built on the
	/// leaf's own hinge bank beside its hinge anchor (a two-leaf bridge has one on each bank). Timber: a hand winch a colonist
	/// turns. Steel: powered (CompPowerTrader); without power its leaf freezes where it is. Gone from the map any way (destroyed,
	/// deconstructed, flown off on a gravship) while its leaf is up, the leaf crashes down and hits anything under it.
	/// </summary>
	public class Building_DrawbridgeWinch : Building
	{
		public SuspensionTier Tier => def.GetModExtension<RM_DrawbridgeExtension>()?.tier ?? SuspensionTier.Timber;

		/// <summary>Steel: its power is on. Timber has no power and is always "powered" for this read (it is never frozen).</summary>
		public bool Powered
		{
			get
			{
				CompPowerTrader c = GetComp<CompPowerTrader>();
				return c == null ? !RM_DrawbridgeMath.IsPowered(Tier) : c.PowerOn;
			}
		}

		/// <summary>The functional script's power override (RM_DrawbridgeProofs.ProofWinchPower): 0 none, 1 held on, 2 held off.
		/// Saved, so a proof's save/load keeps its staging; never set in play.</summary>
		public int proofPower;

		/// <summary>Re-assert a proof's held power state on the trader (the drive calls this before reading Powered).</summary>
		internal void HoldProofPower()
		{
			CompPowerTrader c = proofPower == 0 ? null : GetComp<CompPowerTrader>();
			if (c != null && c.PowerOn != (proofPower == 1))
			{
				c.PowerOn = proofPower == 1;
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref proofPower, "rmProofPower", 0);
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				RM_Drawbridges.LinkWinch(this);
			}
		}

		/// <summary>Every way off the map passes here (Destroy, deconstruct and kill call DeSpawn; a gravship launch despawns
		/// without destroying, WillReplace; the winch is not minifiable). The leaf stays behind on the map, so this is a lost winch: the leaf crashes and the
		/// link is cleared (idempotent: a second call finds no leaf on this winch). A map removed whole takes winch and leaf
		/// together and despawns nothing.</summary>
		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			base.DeSpawn(mode);
			if (map != null)
			{
				RM_Drawbridges.Notify_WinchLost(map, this);
			}
		}

		/// <summary>Landed with a gravship (the SAME instance respawns on the new map, GSS GS-1): a winch that flew is unlinked
		/// already; it takes a leaf on the landing map if it came down beside one's hinge anchor, as a newly built one does.</summary>
		public override void PostSwapMap()
		{
			base.PostSwapMap();
			if (Spawned && !RM_Drawbridges.LeafOfWinch(this, out _, out _))
			{
				RM_Drawbridges.LinkWinch(this);
			}
		}

		/// <summary>Phase 6 (R12): the winch house draws its leaf upright while it is raised, and the art planks beside it.
		/// Its own picture is printed with the map mesh (drawerType MapMeshAndRealTime), so the base draw is not repeated.</summary>
		protected override void DrawAt(Vector3 drawLoc, bool flip = false)
		{
			if (RM_Drawbridges.LeafOfWinch(this, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				RM_DrawbridgeArt.DrawLeafUp(Map, r, l);
				RM_DrawbridgeArt.DrawPlanks(Map, r, l);
			}
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			string line = RM_Drawbridges.LeafOfWinch(this, out SuspensionBridgeRecord r, out DrawbridgeLeaf l)
				? RM_Drawbridges.InspectLine(Map, r, l) : "Not beside a drawbridge's hinge anchor: it works nothing.";
			return s.NullOrEmpty() ? line : s + "\n" + line;
		}

		public override IEnumerable<Gizmo> GetGizmos()
		{
			foreach (Gizmo g in base.GetGizmos())
			{
				yield return g;
			}
			if (RM_Drawbridges.LeafOfWinch(this, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				foreach (Gizmo g in RM_Drawbridges.Gizmos(Map, r, l))
				{
					yield return g;
				}
			}
		}
	}

	/// <summary>
	/// Phase 3: a colonist walks to the leaf to work it (R2). Work spots: the leaf's winch house (raise or lower), and for a
	/// raise only, the anchor on the leaf's FAR bank (the wall-ladder rule, answer 3). Wanted while a player order waits, or
	/// while a hand-winched (timber) leaf is short of its target (a resumed raise, a peace-mode lower).
	/// </summary>
	public class WorkGiver_Drawbridge : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override Danger MaxPathDanger(Pawn pawn) => Danger.Deadly;

		/// <summary>Does this leaf need a pair of hands, and which way?</summary>
		public static bool NeedsHands(SuspensionBridgeRecord r, DrawbridgeLeaf l, out bool raise)
		{
			raise = l.pendingOrder == RM_DrawbridgeMath.OrderRaise || (l.pendingOrder == RM_DrawbridgeMath.OrderNone && l.targetRaised);
			if (l.pendingOrder != RM_DrawbridgeMath.OrderNone)
			{
				return true;
			}
			return !RM_DrawbridgeMath.IsPowered(r.tier) && !RM_DrawbridgeMath.AtTarget(l.progress, l.targetRaised, RM_Drawbridges.FullTicks(r, l));
		}

		/// <summary>The anchor on this leaf's far bank (lane 0), where a raise may also be worked.</summary>
		public static Building_SuspensionAnchor FarAnchor(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			int far = l.hingeAtFirst ? r.length - 1 : 0;
			return RM_MapComponent_SuspensionBridges.BuiltAt<Building_SuspensionAnchor>(map, r.Cell(0, far));
		}

		private static IEnumerable<(SuspensionBridgeRecord r, DrawbridgeLeaf l, Thing spot)> Spots(Map map)
		{
			RM_MapComponent_SuspensionBridges comp = RM_MapComponent_SuspensionBridges.Of(map);
			if (comp == null)
			{
				yield break;
			}
			foreach (SuspensionBridgeRecord r in comp.Bridges)
			{
				if (!r.IsDrawbridge)
				{
					continue;
				}
				foreach (DrawbridgeLeaf l in r.leaves)
				{
					if (!NeedsHands(r, l, out bool raise) || l.winch == null || !l.winch.Spawned)
					{
						continue;   // no winch house: nothing to work it with
					}
					yield return (r, l, l.winch);
					Building_SuspensionAnchor a = raise ? FarAnchor(map, r, l) : null;
					if (a != null)
					{
						yield return (r, l, a);
					}
				}
			}
		}

		public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
		{
			foreach (var s in Spots(pawn.Map))
			{
				yield return s.spot;
			}
		}

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			foreach (var _ in Spots(pawn.Map))
			{
				return false;
			}
			return true;
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			foreach (var s in Spots(pawn.Map))
			{
				if (s.spot != t)
				{
					continue;
				}
				NeedsHands(s.r, s.l, out bool raise);
				if (!RM_DrawbridgeMath.MayWorkFrom(t is Building_DrawbridgeWinch, raise))
				{
					continue;   // lowering only from the winch bank
				}
				if (t.Faction != pawn.Faction || (!forced && t.IsForbidden(pawn)) || !pawn.CanReserve(t, 1, -1, null, forced))
				{
					continue;
				}
				// WINCH_REACH_DIAGNOSE_CANREACH_FIBS: CanReach is vanilla regions AND the depth-only pocket grid, and walls plus a
				// trench can cut a route neither projection sees alone. Only A* sees the joint graph, so the job needs an
				// executable path (as WinchJob does for raiders). Cheap checks above run first; this runs only while a leaf
				// needs hands.
				using (PawnPath path = pawn.Map.pathFinder.FindPathNow(pawn.Position, t, TraverseParms.For(pawn, Danger.Deadly),
					null, PathEndMode.Touch))
				{
					if (path == null || !path.Found)
					{
						continue;
					}
				}
				Job job = JobMaker.MakeJob(RM_DrawbridgeDefOf.RM_WorkDrawbridge, t);
				job.count = s.r.leaves.IndexOf(s.l);
				return job;
			}
			return null;
		}
	}

	/// <summary>Phase 3: walk to the spot, then work the leaf. The order is committed when the colonist arrives (so a lower is
	/// only ever begun from the winch bank). Timber: the colonist turns the winch until the leaf is home (an interrupted job
	/// leaves the leaf where it is). Steel: a lever throw and the power does the rest.</summary>
	public class JobDriver_WorkDrawbridge : JobDriver
	{
		private bool raise;
		private int leverTicks;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref raise, "rmRaise", false);
		}

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		private bool Resolve(out SuspensionBridgeRecord r, out DrawbridgeLeaf l)
		{
			r = null;
			l = null;
			Thing t = job.targetA.Thing;
			if (t is Building_DrawbridgeWinch w)
			{
				return RM_Drawbridges.LeafOfWinch(w, out r, out l);
			}
			r = t == null || !t.Spawned ? null : RM_MapComponent_SuspensionBridges.Of(t.Map)?.RecordAt(t.Position);
			if (r == null || !r.IsDrawbridge || job.count < 0 || job.count >= r.leaves.Count)
			{
				return false;
			}
			l = r.leaves[job.count];
			return true;
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			Toil work = ToilMaker.MakeToil("RM_WorkDrawbridge");
			work.initAction = () =>
			{
				if (!Resolve(out SuspensionBridgeRecord r, out DrawbridgeLeaf l) || !WorkGiver_Drawbridge.NeedsHands(r, l, out raise)
					|| !RM_DrawbridgeMath.MayWorkFrom(job.targetA.Thing is Building_DrawbridgeWinch, raise))
				{
					EndJobWith(JobCondition.Incompletable);
					return;
				}
				l.targetRaised = raise;
				l.pendingOrder = RM_DrawbridgeMath.OrderNone;
				if (raise)
				{
					l.autoLowering = false;
				}
			};
			work.tickAction = () =>
			{
				if (!Resolve(out SuspensionBridgeRecord r, out DrawbridgeLeaf l) || l.targetRaised != raise)
				{
					EndJobWith(JobCondition.Incompletable);   // someone ordered it the other way
					return;
				}
				if (RM_DrawbridgeMath.IsPowered(r.tier))
				{
					if (++leverTicks >= RM_DrawbridgeMath.LeverTicks)
					{
						ReadyForNextToil();   // the lever is thrown; the powered winch does the rest
					}
					return;
				}
				int now = Find.TickManager.TicksGame;
				l.workedUntilTick = now + 2 * RM_Drawbridges.TickInterval;
				if (RM_DrawbridgeMath.AtTarget(l.progress, l.targetRaised, RM_Drawbridges.FullTicks(r, l)))
				{
					ReadyForNextToil();
				}
			};
			work.defaultCompleteMode = ToilCompleteMode.Never;
			yield return work;
		}
	}

	/// <summary>
	/// Phase 6 (R7): the gate leaf, a door in the wall line beside a leaf's hinge anchor (one per lane). Not vanilla door
	/// semantics: it opens for nobody while its leaf is off its seat (the far side is a pit), and while the map is LOCKED (a
	/// free hostile, R4) it opens only when the player holds it open (the order, given at the gate on the hinge bank). In
	/// peace it is an ordinary door for its own faction. Not beside a drawbridge, or drawbridges off: a plain door.
	/// </summary>
	public class Building_DrawbridgeGate : Building_Door
	{
		public override bool PawnCanOpen(Pawn p)
		{
			if (!base.PawnCanOpen(p))
			{
				return false;
			}
			if (!RM_DrawbridgeSettings.drawbridgesEnabled || !RM_Drawbridges.LeafOfGate(this, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				return true;
			}
			return RM_DrawbridgeMath.GateOpensFor(RM_Drawbridges.Locked(Map), l.progress > 0, HoldOpen);
		}

		/// <summary>REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE: shut to every pawn whatever its faction (locked and not held, or its
		/// leaf off its seat): the wall-aware reach map closes it to everyone but a door-basher (RM_WallReach).</summary>
		public bool ShutToEveryone => Spawned && RM_DrawbridgeSettings.drawbridgesEnabled
			&& RM_Drawbridges.LeafOfGate(this, out SuspensionBridgeRecord r, out DrawbridgeLeaf l)
			&& !RM_DrawbridgeMath.GateOpensFor(RM_Drawbridges.Locked(Map), l.progress > 0, HoldOpen);

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			if (!RM_Drawbridges.LeafOfGate(this, out SuspensionBridgeRecord r, out DrawbridgeLeaf l))
			{
				return s;
			}
			string line = l.progress > 0 ? "Gate: shut (the leaf is up)"
				: RM_Drawbridges.Locked(Map) ? (HoldOpen ? "Gate: held open by order" : "Gate: locked (hostiles on the map); hold it open to pass")
				: "Gate: opens for your people";
			return s.NullOrEmpty() ? line : s + "\n" + line;
		}
	}
}
