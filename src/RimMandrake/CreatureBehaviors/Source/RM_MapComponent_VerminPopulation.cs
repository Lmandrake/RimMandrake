using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Per-map population tracker for any race carrying
	/// RM_VerminPressureExtension, grouped by that extension's group tag.
	/// This is the whole "nuisance unless there are many" mechanism: everything
	/// else (breeder cap, gnaw damage, gnaw job frequency, the population alert)
	/// reads GetPressure()/GetPopulation() from here rather than re-deriving a
	/// count itself, so the curve is defined once.
	///
	/// Counts are recomputed at most once every RecomputeIntervalTicks and
	/// cached — a full-map pawn scan on every TryGiveJob call across every
	/// animal on the map would be needlessly expensive.
	/// </summary>
	public class RM_MapComponent_VerminPopulation : MapComponent
	{
		private const int RecomputeIntervalTicks = 250;

		private int nextRecomputeTick = -1;

		private readonly Dictionary<string, int> countsByGroup = new Dictionary<string, int>();

		public RM_MapComponent_VerminPopulation(Map map)
			: base(map)
		{
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (Find.TickManager.TicksGame >= nextRecomputeTick)
			{
				Recompute();
			}
		}

		private void Recompute()
		{
			nextRecomputeTick = Find.TickManager.TicksGame + RecomputeIntervalTicks;
			countsByGroup.Clear();
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn pawn = pawns[i];
				RM_VerminPressureExtension ext = pawn.def?.GetModExtension<RM_VerminPressureExtension>();
				if (ext == null)
				{
					continue;
				}
				string tag = ext.GroupTagFor(pawn.def);
				countsByGroup.TryGetValue(tag, out int count);
				countsByGroup[tag] = count + 1;
			}
		}

		private void EnsureFresh()
		{
			if (nextRecomputeTick < 0)
			{
				Recompute();
			}
		}

		/// <summary>Live population for the group this pawn's race belongs to (0 if untracked).</summary>
		public int GetPopulation(Pawn pawn)
		{
			RM_VerminPressureExtension ext = pawn.def?.GetModExtension<RM_VerminPressureExtension>();
			if (ext == null)
			{
				return 0;
			}
			return GetPopulation(ext.GroupTagFor(pawn.def));
		}

		public int GetPopulation(string groupTag)
		{
			EnsureFresh();
			countsByGroup.TryGetValue(groupTag, out int count);
			return count;
		}

		/// <summary>0..1 — 0 at or below the race's soft cap, 1 at or above its hard cap.</summary>
		public float GetPressure(Pawn pawn)
		{
			RM_VerminPressureExtension ext = pawn.def?.GetModExtension<RM_VerminPressureExtension>();
			if (ext == null)
			{
				return 0f;
			}
			int population = GetPopulation(ext.GroupTagFor(pawn.def));
			if (ext.populationHardCap <= ext.populationSoftCap)
			{
				return population >= ext.populationSoftCap ? 1f : 0f;
			}
			return Mathf.Clamp01((population - ext.populationSoftCap) / (float)(ext.populationHardCap - ext.populationSoftCap));
		}

		/// <summary>True once the group's population has reached its hard cap — RM_CompVerminBreeder's stop signal.</summary>
		public bool AtHardCap(Pawn pawn)
		{
			RM_VerminPressureExtension ext = pawn.def?.GetModExtension<RM_VerminPressureExtension>();
			if (ext == null)
			{
				return false;
			}
			return GetPopulation(ext.GroupTagFor(pawn.def)) >= ext.populationHardCap;
		}
	}
}
