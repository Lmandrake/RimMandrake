using System.Collections.Generic;
using Verse;

namespace RimMandrake.Miasma
{
	/// <summary>
	/// MIASMA_SCUTTLER_PREDATION_1. Data-driven prey whitelist for
	/// RM_CompPlantPredator — deliberately a defName list, not a ModExtension
	/// group-tag lookup, so this assembly needs no compile-time reference to
	/// RimMandrake.CreatureBehaviors (same self-contained idiom
	/// RM_CompVerminBreeder.Props.breedFoodThingDefNames already uses for an
	/// identical "match against a short list of named defs" problem).
	/// </summary>
	public class RM_CompProperties_PlantPredator : CompProperties
	{
		/// <summary>Wild-only prey this plant may kill. Never widen this to "any Pawn".</summary>
		public List<string> preyDefNames;

		/// <summary>Tiles around the plant it hunts within.</summary>
		public float huntRadius = 3f;

		public RM_CompProperties_PlantPredator()
		{
			compClass = typeof(RM_CompPlantPredator);
		}
	}
}
