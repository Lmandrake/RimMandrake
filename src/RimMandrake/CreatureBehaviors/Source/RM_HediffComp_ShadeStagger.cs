using System;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_STAGGERSEED_BUILD_1. design/Jawa/worldbuilding/biomes/desert.md
	/// §4b "The seed that uses you": the cycle plant's fruit, eaten raw,
	/// "hatches its seeds inside your belly. It kills quickly, and the dying
	/// animal does what every dying animal here does: staggers toward the next
	/// shade — and dies in it. The seeds germinate there, in the one place they
	/// could not otherwise reach." ⇒ "It disperses by killing, and it aims at
	/// shade."
	///
	/// Two halves, both on this one comp because they are one organism's life
	/// cycle and splitting them would let a def carry the death without the
	/// dispersal:
	///
	///   1. STAGGER — once the brood's severity passes minSeverityToStagger,
	///      poll on steerIntervalTicks and force a plain vanilla Goto toward
	///      the best-shaded reachable cell within staggerRadius. Once the
	///      carrier is standing somewhere at/above minShadeToSettle it stops
	///      being steered and dies where it is.
	///   2. GERMINATE — on Notify_PawnDied, place germinateCount plants of
	///      germinateThingDef around the corpse, at a chance interpolated
	///      between germinateChanceInSun and germinateChanceInShade by the
	///      shade at the corpse's own cell. A corpse in the open is mostly a
	///      wasted seed; that asymmetry IS the "aims at shade" ruling, rather
	///      than a flat chance with flavour text over it.
	///
	/// Why new C#: there is no vanilla CompProperties for "bias a dying
	/// creature's movement, then spawn a plant at its corpse". The nearest
	/// vanilla shapes each cover one quarter of it and none compose —
	/// HediffComp_ExplodeOnDeath fires at death but only explodes,
	/// CompSpawnSubplant spawns plants but off a living thing's own tick,
	/// JobGiver_SeekShade-alikes steer but are ThinkTree nodes that only reach
	/// animals carrying a race extension (this must also work on a colonist who
	/// ate the fruit). CLAUDE.md's own tier ladder puts "behave differently"
	/// at tier c; this is that.
	///
	/// Shade is read from RM_MapComponent_ShadeGrid, the same keystone grid
	/// RM_JobGiver_WanderInShadeGrid and RM_HediffComp_ShadeDrivenSeverity
	/// already read (DESERT_SHADE_GRID_KEYSTONE_1) — desert_ecology_feasibility.md
	/// §2: neither GlowGrid nor outdoor temperature varies per cell, so shade
	/// has to be a thing we compute. No consumer re-derives it.
	///
	/// MEASURED from the decompiled engine this pass (Verse/Pawn.cs Kill, phase
	/// 6): health.hediffSet.Notify_PawnDied runs AFTER the corpse has been made
	/// and placed, so Pawn.Corpse is spawned and carries the position and map we
	/// need. That is the same seam vanilla's own HediffComp_ExplodeOnDeath uses
	/// when it calls base.Pawn.Corpse.Destroy(). The pawn itself is already
	/// despawned by then, so nothing here may read Pawn.Position or Pawn.Map.
	/// </summary>
	public class RM_HediffComp_ShadeStagger : HediffComp
	{
		private IntVec3 staggerTarget = IntVec3.Invalid;

		private bool germinated;

		private RM_HediffCompProperties_ShadeStagger Props => (RM_HediffCompProperties_ShadeStagger)props;

		public override void CompExposeData()
		{
			base.CompExposeData();
			Scribe_Values.Look(ref staggerTarget, "staggerTarget", IntVec3.Invalid);
			Scribe_Values.Look(ref germinated, "germinated", defaultValue: false);
		}

		public override void CompPostTickInterval(ref float severityAdjustment, int delta)
		{
			base.CompPostTickInterval(ref severityAdjustment, delta);

			if (!RM_CreatureBehaviorsSettings.shadeStaggerEnabled)
			{
				return; // mod option: the brood still kills, it just no longer steers the dying
			}

			Pawn pawn = base.Pawn;
			if (pawn == null || pawn.Dead || !pawn.Spawned || pawn.Map == null || pawn.Downed || pawn.jobs == null)
			{
				return;
			}

			if (parent.Severity < Props.minSeverityToStagger)
			{
				return; // not dying yet
			}

			if (!pawn.IsHashIntervalTick(Math.Max(1, Props.steerIntervalTicks), delta))
			{
				return;
			}

			TryStagger(pawn);
		}

		private void TryStagger(Pawn pawn)
		{
			Map map = pawn.Map;
			RM_MapComponent_ShadeGrid grid = map.GetComponent<RM_MapComponent_ShadeGrid>();
			if (grid == null)
			{
				return; // no grid on this map — degrade to plain vanilla dying, never a guessed shade
			}

			if (grid.ShadeAt(pawn.Position) >= Props.minShadeToSettle)
			{
				staggerTarget = IntVec3.Invalid;
				return; // arrived. This shadow is where it dies, and where the seeds wanted to be.
			}

			if (staggerTarget.IsValid && pawn.CurJobDef == JobDefOf.Goto
				&& pawn.CurJob != null && pawn.CurJob.targetA.Cell == staggerTarget)
			{
				return; // already staggering there — do not re-issue the job every interval
			}

			IntVec3 target = FindShadeCell(pawn, map, grid);
			if (!target.IsValid)
			{
				return; // nothing better than here within reach; it dies in the open
			}

			staggerTarget = target;
			Job job = JobMaker.MakeJob(JobDefOf.Goto, target);
			job.locomotionUrgency = LocomotionUrgency.Jog; // staggering, not strolling
			pawn.jobs.StartJob(job, JobCondition.InterruptForced, resumeCurJobAfterwards: false, cancelBusyStances: true);
		}

		/// <summary>
		/// Nearest strictly-better-shaded reachable cell, or IntVec3.Invalid.
		/// GenRadial walks outward, so a strict improvement test keeps the
		/// NEAREST cell of each shade tier — desert.md's "the NEXT shade", not
		/// the best shade on the map. The reachability check sits last
		/// deliberately: ShadeAt is quantized into a handful of values by the
		/// grid's own falloff, so CanReach runs a few times per search rather
		/// than once per cell.
		/// </summary>
		private IntVec3 FindShadeCell(Pawn pawn, Map map, RM_MapComponent_ShadeGrid grid)
		{
			IntVec3 best = IntVec3.Invalid;
			float bestShade = grid.ShadeAt(pawn.Position);
			TraverseParms traverse = TraverseParms.For(pawn);

			foreach (IntVec3 cell in GenRadial.RadialCellsAround(pawn.Position, Props.staggerRadius, useCenter: false))
			{
				if (!cell.InBounds(map))
				{
					continue;
				}
				float shade = grid.ShadeAt(cell);
				if (shade <= bestShade)
				{
					continue;
				}
				if (!cell.Standable(map))
				{
					continue;
				}
				if (!map.reachability.CanReach(pawn.Position, cell, PathEndMode.OnCell, traverse))
				{
					continue;
				}
				bestShade = shade;
				best = cell;
			}

			return best;
		}

		public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
		{
			base.Notify_PawnDied(dinfo, culprit);

			if (germinated || Props.germinateThingDef == null)
			{
				return;
			}

			if (!RM_CreatureBehaviorsSettings.shadeStaggerEnabled)
			{
				return; // mod option: the carrier still dies, it just leaves nothing behind
			}

			// The pawn is despawned by this point; the corpse is the only thing
			// that still knows where it fell (Verse/Pawn.cs Kill, phase 6).
			Corpse corpse = base.Pawn?.Corpse;
			if (corpse == null || !corpse.Spawned || corpse.Map == null)
			{
				return;
			}

			germinated = true;
			Germinate(corpse.Position, corpse.Map);
		}

		private void Germinate(IntVec3 center, Map map)
		{
			RM_MapComponent_ShadeGrid grid = map.GetComponent<RM_MapComponent_ShadeGrid>();
			float shade = (grid != null) ? grid.ShadeAt(center) : 0f;

			float chance = Mathf.Lerp(Props.germinateChanceInSun, Props.germinateChanceInShade, shade);
			chance *= Mathf.Max(0f, RM_CreatureBehaviorsSettings.shadeStaggerGerminationMultiplier);
			if (!Rand.Chance(chance))
			{
				return;
			}

			int wanted = Props.germinateCount.RandomInRange;
			int placed = 0;

			foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, Props.germinateRadius, useCenter: true))
			{
				if (placed >= wanted)
				{
					break;
				}
				if (!cell.InBounds(map) || cell.GetPlant(map) != null)
				{
					continue;
				}
				if (!Props.germinateThingDef.CanEverPlantAt(cell, map))
				{
					continue;
				}
				if (GenSpawn.Spawn(Props.germinateThingDef, cell, map) is Plant plant)
				{
					plant.Growth = Mathf.Clamp01(Props.germinateGrowth);
					placed++;
				}
			}
		}
	}
}
