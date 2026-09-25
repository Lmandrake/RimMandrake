using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// GREENTIDE_YEARNING_FRUIT_FILTH_1. See RM_HediffCompProperties_SeedPassage
	/// for the mechanic and why it fires where it does.
	///
	/// Fires once, at the hediff's own natural end — CompPostPostRemoved is
	/// the same seam RM_HediffComp_ForgeOnSurvival already uses and documents
	/// in detail (Verse/HediffWithComps.cs:197 -> comps[i].CompPostPostRemoved(),
	/// no removal reason passed through at all: a natural decay-to-zero, an
	/// amputation and a debug removal all fire it identically —
	/// Verse/Hediff.cs:608, Verse/HediffComp.cs:48). RUT_DigestiveAccelerant is
	/// isBad=false and carries only HediffCompProperties_SeverityPerDay driving
	/// its severity to 0, so in practice this only ever fires on the
	/// decays-to-zero path this item asks for — but the pawn.Dead/Spawned/Map
	/// guard below is the same defensive gate ForgeOnSurvival uses, so a
	/// mid-flight death or despawn never fires the payload off a corpse or a
	/// null map.
	///
	/// Works on ANY eater — colonist or wild animal grazing the bush alike,
	/// since HediffComp carries no notion of faction and nothing here reads
	/// anything colonist-specific.
	/// </summary>
	public class RM_HediffComp_SeedPassage : HediffComp
	{
		private RM_HediffCompProperties_SeedPassage Props => (RM_HediffCompProperties_SeedPassage)props;

		public override void CompPostPostRemoved()
		{
			base.CompPostPostRemoved();

			if (!RM_CreatureBehaviorsSettings.seedPassageEnabled)
			{
				return; // mod option: the fruit still digests fast, it just leaves nothing behind
			}

			Pawn pawn = base.Pawn;
			if (pawn == null || pawn.Dead || !pawn.Spawned || pawn.Map == null)
			{
				return; // death/despawn removals never pass seed
			}

			DropFilth(pawn);
			TryGerminate(pawn);
		}

		private void DropFilth(Pawn pawn)
		{
			RM_HediffCompProperties_SeedPassage props = Props;
			if (props.filthDef == null || props.filthCount <= 0)
			{
				return;
			}

			IntVec3 cell = pawn.Position;
			if (!cell.InBounds(pawn.Map))
			{
				return;
			}

			FilthMaker.TryMakeFilth(cell, pawn.Map, props.filthDef, props.filthCount);
		}

		private void TryGerminate(Pawn pawn)
		{
			RM_HediffCompProperties_SeedPassage props = Props;
			if (props.germinateThingDef == null)
			{
				return;
			}

			float chance = props.germinateChance
				* Mathf.Max(0f, RM_CreatureBehaviorsSettings.seedPassageGerminationMultiplier);
			if (!Rand.Chance(chance))
			{
				return;
			}

			Map map = pawn.Map;
			IntVec3 center = pawn.Position;
			int wanted = props.germinateCount.RandomInRange;
			int placed = 0;

			foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, props.germinateRadius, useCenter: true))
			{
				if (placed >= wanted)
				{
					break;
				}
				if (!cell.InBounds(map) || cell.GetPlant(map) != null)
				{
					continue;
				}
				if (!props.germinateThingDef.CanEverPlantAt(cell, map))
				{
					continue;
				}
				if (GenSpawn.Spawn(props.germinateThingDef, cell, map) is Plant plant)
				{
					plant.Growth = Mathf.Clamp01(props.germinateGrowth);
					placed++;
				}
			}
		}
	}
}
