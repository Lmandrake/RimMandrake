using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.RustCathedralHum
{
	// RUST_CATHEDRAL_MECHANICS_1 §3 -- "the one real piece of C#" the kit spec
	// budgets for the living bolts.
	//
	// WHAT IT DOES, HONESTLY: the engine has no "dance". This emits a short
	// chain of Goto jobs whose target cells are sampled off a generated
	// figure (a loop, a lobed figure, or a straight alignment) centred on
	// where the bolt already stands. The first job is returned to the think
	// tree; the rest go on the pawn's own job queue and are dequeued by the
	// ThinkNode_QueuedJob that sits directly above this node in
	// RUT_ThinkTree_LivingBolt. VERIFIED this pass that Pawn_JobTracker.
	// StartJob does NOT clear the job queue (Verse/AI/Pawn_JobTracker.cs --
	// ClearQueuedJobs is called only from CaptureAndClearJobQueue,
	// EndCurrentJob's explicit paths and the notify/cleanup paths, never from
	// StartJob), so a queued figure survives being handed out one job at a
	// time. That is the whole trick; there is no animation system involved.
	//
	// PATTERN ENERGY is read from §1's public API -- RM_MapComponent_
	// BiomeAttitude.GetBand(Map) -- and nothing else. Energy is FULL at band
	// 0 and falls to nothing at worstBand: §1 shipped band 0 = calmest and
	// band 4 = worst-and-silent, so as the Cathedral's mood worsens the
	// figures get smaller, shorter and rarer ("the bolts' dances go stiff,
	// then stop", §1's own player-experience paragraph) and the separate
	// higher-priority freeze node takes over at the top. See the band-
	// direction note in RUT_ThinkTree_LivingBolt.xml for why this is
	// inverted relative to the kit spec's literal pre-§1 wording.
	//
	// This node is a no-op for every pawn that is not on a map governed by an
	// RM_BiomeAttitudeDef, so nothing outside the Rust Cathedral changes --
	// though in practice only RUT_LivingBolt's own think tree names it at
	// all.
	//
	// DEFERRED per the kit spec's own v1 line, not forgotten: dance
	// choreography variety passes, synchronized multi-bolt figures, and
	// fleck/sound garnish per dance. The three figure shapes below are the
	// minimum that reads as "patterned" rather than "random walk"; they are
	// not a choreography system and do not pretend to be.
	public class RM_JobGiver_ResonantDance : ThinkNode_JobGiver
	{
		// The band at which energy reaches zero. Matches the governing
		// RM_BiomeAttitudeDef's WorstBand (bandThresholds.Count). Kept as an
		// XML field rather than read off the def so this node never needs the
		// map component's internals.
		public int worstBand = 4;

		// Chance per think cycle of starting a figure, at full energy.
		public float baseChance = 0.35f;

		// Steps in a figure, lerped by energy.
		public int minSteps = 3;
		public int maxSteps = 7;

		// Figure radius in cells, lerped by energy.
		public float minRadius = 1.4f;
		public float maxRadius = 4.5f;

		public override ThinkNode DeepCopy(bool resolve = true)
		{
			RM_JobGiver_ResonantDance obj = (RM_JobGiver_ResonantDance)base.DeepCopy(resolve);
			obj.worstBand = worstBand;
			obj.baseChance = baseChance;
			obj.minSteps = minSteps;
			obj.maxSteps = maxSteps;
			obj.minRadius = minRadius;
			obj.maxRadius = maxRadius;
			return obj;
		}

		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RustCathedralHumSettings.BoltDisplayActive)
			{
				return null; // mod option off -- vanilla wander below takes over
			}
			if (pawn == null || pawn.jobs == null)
			{
				return null;
			}
			Map map = pawn.Map;
			if (map == null)
			{
				return null;
			}
			int band = RM_MapComponent_BiomeAttitude.GetBand(map);
			if (band < 0)
			{
				return null; // no attitude def governs this biome
			}
			float energy = DanceEnergy(band);
			if (energy <= 0f)
			{
				return null; // worst band -- the freeze node owns this case
			}
			if (!Rand.Chance(baseChance * energy))
			{
				return null;
			}

			List<IntVec3> figure = BuildFigure(pawn, map, energy);
			if (figure.Count == 0)
			{
				return null;
			}

			Job first = MakeStep(figure[0], energy);
			for (int i = 1; i < figure.Count; i++)
			{
				pawn.jobs.jobQueue.EnqueueLast(MakeStep(figure[i], energy));
			}
			return first;
		}

		// 1 at band 0, 0 at worstBand and above. A worstBand of 0 or less
		// would be a malformed def; treat it as "always full energy" rather
		// than dividing by zero.
		private float DanceEnergy(int band)
		{
			if (worstBand <= 0)
			{
				return 1f;
			}
			return Mathf.Clamp01(1f - (float)band / worstBand);
		}

		private List<IntVec3> BuildFigure(Pawn pawn, Map map, float energy)
		{
			List<IntVec3> cells = new List<IntVec3>();
			int steps = Mathf.Max(2, Mathf.RoundToInt(Mathf.Lerp(minSteps, maxSteps, energy)));
			float radius = Mathf.Lerp(minRadius, maxRadius, energy);
			IntVec3 anchor = pawn.Position;
			float phase = Rand.Range(0f, Mathf.PI * 2f);

			// Three figure shapes, chosen fresh each time: a plain loop, a
			// lobed figure (the petals of |cos(k*t)| -- reads as a figure-eight
			// or trefoil on the ground), and a straight alignment the bolt
			// paces out and back along. All three are closed or symmetric, so
			// the bolt ends roughly where it began and a colony of them stays
			// put instead of drifting off the map.
			int shape = Rand.RangeInclusive(0, 2);
			int lobes = Rand.RangeInclusive(2, 3);

			for (int i = 0; i < steps; i++)
			{
				float t = (float)i / steps;
				float ang = phase + t * Mathf.PI * 2f;
				float r;
				switch (shape)
				{
					case 1:
						r = radius * (0.4f + 0.6f * Mathf.Abs(Mathf.Cos(ang * lobes)));
						break;
					case 2:
						r = radius * Mathf.Cos(ang);
						break;
					default:
						r = radius;
						break;
				}
				IntVec3 candidate = anchor + new IntVec3(
					Mathf.RoundToInt(Mathf.Cos(ang) * r),
					0,
					Mathf.RoundToInt(Mathf.Sin(ang) * r));

				if (candidate == anchor)
				{
					continue;
				}
				if (cells.Count > 0 && cells[cells.Count - 1] == candidate)
				{
					continue;
				}
				if (!candidate.InBounds(map) || !candidate.Standable(map))
				{
					continue;
				}
				if (!pawn.CanReach(candidate, PathEndMode.OnCell, Danger.Deadly))
				{
					continue;
				}
				cells.Add(candidate);
			}
			return cells;
		}

		private Job MakeStep(IntVec3 cell, float energy)
		{
			Job job = JobMaker.MakeJob(JobDefOf.Goto, cell);
			// A lively bolt trots its figure; a stiffening one walks it.
			job.locomotionUrgency = energy > 0.66f ? LocomotionUrgency.Jog : LocomotionUrgency.Walk;
			// A step that cannot complete (something moved into the cell, the
			// bolt got boxed in) expires instead of wedging the whole figure.
			job.expiryInterval = 600;
			return job;
		}
	}
}
