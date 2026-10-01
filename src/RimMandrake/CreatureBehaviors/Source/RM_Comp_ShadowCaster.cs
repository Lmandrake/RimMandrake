using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_GLITTER_BIRDS_COMMENSALS_1. Marker + tuning comp — its presence
	/// on a spawned Pawn is what RM_JobGiver_FollowShadowCaster scans the map
	/// for, and followers track the host's live Position. No tick logic.
	/// LONGSHADE_GPT_ENRICHMENT_1 §2: a host whose props set castShadeHeight
	/// also registers with RM_MapComponent_ShadeGrid, which casts its body's
	/// shade into a moving-shade layer on the grid's own refresh.
	/// </summary>
	public class RM_Comp_ShadowCaster : ThingComp
	{
		public RM_CompProperties_ShadowCaster Props => (RM_CompProperties_ShadowCaster)props;

		/// <summary>LONGSHADE_GPT_ENRICHMENT_1 §2: true when this host's body
		/// casts moving shade into the grid.</summary>
		public bool CastsMovingShade => Props.castShadeHeight > 0f;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			if (CastsMovingShade)
			{
				RM_MapComponent_ShadeGrid.For(parent.Map)?.RegisterMovingCaster(parent);
			}
		}

		public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
		{
			base.PostDeSpawn(map, mode);
			RM_MapComponent_ShadeGrid.For(map)?.UnregisterMovingCaster(parent);
		}
	}
}
