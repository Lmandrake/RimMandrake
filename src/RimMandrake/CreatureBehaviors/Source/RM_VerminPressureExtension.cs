using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Attach to any race ThingDef that should be tracked by
	/// RM_MapComponent_VerminPopulation. "Nuisance unless there are many" (owner
	/// ruling, 2026-09-11, verbatim) is implemented entirely through the curve
	/// this extension parameterizes: below populationSoftCap the pressure this
	/// mod's comps/JobGivers read is 0 (a lone vermin is cheap and quiet);
	/// between soft and hard cap it ramps linearly to 1 (a swarm is loud,
	/// hungrier, and bites harder); at or above populationHardCap breeding
	/// itself stops (RM_CompVerminBreeder).
	///
	/// populationGroupTag lets several distinct races share one population pool
	/// (e.g. two vermin species that both count against the same ship-infestation
	/// pressure) — defaults to the race's own defName when left blank, so a
	/// single-species mod needs no XML for this field at all.
	/// </summary>
	public class RM_VerminPressureExtension : DefModExtension
	{
		public int populationSoftCap = 3;

		public int populationHardCap = 12;

		public string populationGroupTag;

		public string GroupTagFor(ThingDef race)
		{
			return populationGroupTag.NullOrEmpty() ? race.defName : populationGroupTag;
		}
	}
}
