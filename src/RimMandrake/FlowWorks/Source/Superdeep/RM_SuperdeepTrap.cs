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
	/// is not flying, no ladder stands in the cell, and some W×W square of D = 4 cells contains
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
			return map?.GetComponent<RM_MapComponent_Excavation>();
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
			if (eng == null || eng.SuperdeepCellCount == 0)
			{
				return false;
			}
			bool onD4 = eng.IsSuperdeepExcavation(c);
			if (!onD4 || !RuleOn)
			{
				return false;
			}
			int w = RequiredWidth(p);
			bool wide = RM_PitTrapMath.PitWidthAt((x, z) => eng.IsSuperdeepExcavation(new IntVec3(x, 0, z)), c.x, c.z, w);
			return RM_PitTrapMath.Held(true, true, Captures(p), p.Flying,
				RM_LadderRules.LadderLetsOut(p.Map, c, p), wide);
		}

		// ── the reachability region, cached per pawn per tick ──────────────
		private sealed class RegionEntry
		{
			public int tick;
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
			if (regionCache.TryGetValue(p.thingIDNumber, out RegionEntry e) && e.pos == p.Position)
			{
				region = e.cells;
				return e.trapped;
			}
			e = new RegionEntry { tick = now, pos = p.Position, trapped = true };
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
					if (!e.cells.Contains(n) && eng.IsSuperdeepExcavation(n))
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
		internal static void OnDescent(Pawn p, IntVec3 cell, RM_SuperdeepTrapState state)
		{
			float dmg = 0f;
			if (RimMandrakeFlowWorksSettings.fallDamageEnabled)
			{
				dmg = RM_PitTrapMath.FallDamage(p.GetStatValue(StatDefOf.Mass), RimMandrakeFlowWorksSettings.fallDamageMultiplier);
				p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg));
			}
			state.RecordDescent(p, cell, dmg);
			PitDescent?.Invoke(p, cell);
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
			p.Position = cell;
			p.Notify_Teleported(true, true);
			// The detector sees the move on its next tick and fires the descent; the jumper
			// flag makes it count even with the own-faction carve-out on.
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
		private readonly List<Pawn> descents = new List<Pawn>();

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
		}

		public void Tick(Map map, RM_MapComponent_Excavation eng)
		{
			nextCell.Clear();
			descents.Clear();
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				IntVec3 pos = p.Position;
				if (lastCell.TryGetValue(p, out IntVec3 prev) && prev != pos
					&& RimMandrakeFlowWorksSettings.superdeepCaptureEnabled
					&& RM_PitTrapMath.IsPitDescent(eng.ExcavatedDepthAt(prev), eng.ExcavatedDepthAt(pos))
					&& !p.Flying && RM_SuperdeepTrap.Captures(p))
				{
					descents.Add(p);
				}
				nextCell[p] = pos;
			}
			Dictionary<Pawn, IntVec3> swap = lastCell;
			lastCell = nextCell;
			nextCell = swap;
			for (int i = 0; i < descents.Count; i++)
			{
				Pawn p = descents[i];
				if (p.Spawned)
				{
					RM_SuperdeepTrap.OnDescent(p, p.Position, this);
				}
			}
			if (jumpers.Count > 0)
			{
				jumpers.RemoveWhere(p => p == null || !p.Spawned || p.Map != map || !eng.IsSuperdeepExcavation(p.Position));
			}
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
	public static class RM_Patch_PathFollower_SuperdeepFloor
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn_PathFollower __instance, Pawn ___pawn)
		{
			Pawn pawn = ___pawn;
			if (pawn == null || !pawn.Spawned)
			{
				return true;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(pawn.Map);
			if (eng == null || eng.SuperdeepCellCount == 0)
			{
				return true;
			}
			int toD = eng.ExcavatedDepthAt(__instance.nextCell);
			if (!RM_PitTrapMath.StepBlocked(RM_SuperdeepTrap.IsHeld(pawn), toD))
			{
				return true;
			}
			// Vanilla's own PatherFailed shape (Pawn_PathFollower.cs l.573).
			__instance.StopDead();
			if (pawn.jobs?.curJob != null)
			{
				pawn.jobs.curDriver.Notify_PatherFailed();
			}
			return false;
		}
	}

	/// <summary>The reachability veto (seam 2), outside the region cache.</summary>
	[HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReach),
		new[] { typeof(IntVec3), typeof(LocalTargetInfo), typeof(PathEndMode), typeof(TraverseParms) })]
	public static class RM_Patch_Reachability_SuperdeepVeto
	{
		[HarmonyPostfix]
		public static void Postfix(IntVec3 start, LocalTargetInfo dest, PathEndMode peMode,
			TraverseParms traverseParams, ref bool __result)
		{
			if (!__result)
			{
				return;
			}
			Pawn p = traverseParams.pawn;
			if (p == null || !p.Spawned || start != p.Position)
			{
				return;
			}
			if (!RM_SuperdeepTrap.TryGetTrapRegion(p, out HashSet<IntVec3> region))
			{
				return;
			}
			if (!RM_SuperdeepTrap.AllowedDestination(region, dest, peMode))
			{
				__result = false;
			}
		}
	}

	[HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReachMapEdge),
		new[] { typeof(IntVec3), typeof(TraverseParms) })]
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
			if (p != null && p.Spawned && c == p.Position && RM_SuperdeepTrap.TryGetTrapRegion(p, out _))
			{
				__result = false;
			}
		}
	}

	/// <summary>"Jump into pit": warn + confirm; strands the jumper.</summary>
	[HarmonyPatch(typeof(Pawn), nameof(Pawn.GetGizmos))]
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
			if (eng == null || eng.SuperdeepCellCount == 0 || !eng.IsSuperdeepExcavation(__instance.Position)
				|| !RM_SuperdeepTrap.Captures(__instance))
			{
				return;
			}
			string line;
			if (RM_SuperdeepTrap.IsHeld(__instance))
			{
				line = "RMFlow_PitHeld".Translate();
			}
			else if (RM_SuperdeepTrap.MeasuredPitWidth(__instance.Map, __instance.Position) < RM_SuperdeepTrap.RequiredWidth(__instance))
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
