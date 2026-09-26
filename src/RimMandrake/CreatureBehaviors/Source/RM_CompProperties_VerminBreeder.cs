using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Fields borrowed verbatim from vanilla
	/// CompProperties_SpawnerPawn (pawnSpawnIntervalDays, pawnSpawnRadius) —
	/// see RM_CompVerminBreeder's header for why that comp isn't reused as-is.
	/// </summary>
	public class RM_CompProperties_VerminBreeder : CompProperties
	{
		public FloatRange pawnSpawnIntervalDays = new FloatRange(1.0f, 2.0f);

		public int pawnSpawnRadius = 3;

		/// <summary>
		/// GREATBOLE_HARVEST_LADDER_1's widening: "does not gate on food;
		/// that is the gap." Null/empty (the default) is the original
		/// behaviour, completely unaffected — breeding is always allowed.
		/// When set, breeding only proceeds while at least one spawned item
		/// of one of these defNames exists within foodSearchRadius of the
		/// parent — "breed fast while there is fruit to eat" (the spec's
		/// own words for the grubs, §4a).
		/// </summary>
		public List<string> breedFoodThingDefNames;

		public float foodSearchRadius = 40f;

		/// <summary>
		/// When breedFoodThingDefNames is set and none of it exists nearby
		/// for at least famineGraceTicks, every pawn carrying this comp is
		/// flipped into this (real, unscoped) vanilla MentalStateDef —
		/// "when the fruit runs out, they go Manhunter" (§4a). Null (the
		/// default) disables the flip; breeding simply pauses while food is
		/// absent.
		/// </summary>
		public MentalStateDef famineMentalState;

		/// <summary>
		/// INVENTED: ~half an in-game day (30000 ticks) of sustained famine
		/// before the flip, so a fruit pile briefly fully eaten does not
		/// instantly turn the whole population hostile.
		/// </summary>
		public int famineGraceTicks = 30000;

		public RM_CompProperties_VerminBreeder()
		{
			compClass = typeof(RM_CompVerminBreeder);
		}
	}
}
