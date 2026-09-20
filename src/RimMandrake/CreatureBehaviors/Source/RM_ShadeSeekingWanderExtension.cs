using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_GRID_KEYSTONE_1. Attach to a race ThingDef to make
	/// RM_JobGiver_WanderInShadeGrid steer its idle wandering toward shaded
	/// cells (per RM_MapComponent_ShadeGrid.ShadeAt) instead of picking a
	/// uniformly random destination — desert_ecology_feasibility.md §3's
	/// "shade preference" behaviour, built as the wander-insert half named
	/// there (JobGiver_WanderInRoofedCellsInPen-pattern), separate from this
	/// same assembly's RM_SeekShadeExtension (an emergency "duck under roof"
	/// reaction keyed to a temperature threshold). No ThingDef carries this
	/// extension yet — EXTREME_DESERT_GIANT_COMMENSALS_1 and
	/// DESERT_BURST_PREDATOR_FLAGSHIP_1 are the intended first consumers.
	/// </summary>
	public class RM_ShadeSeekingWanderExtension : DefModExtension
	{
		/// <summary>Minimum ShadeAt score (0..1) a wander destination must clear to be preferred.</summary>
		public float minShadeToPrefer = 0.5f;
	}
}
