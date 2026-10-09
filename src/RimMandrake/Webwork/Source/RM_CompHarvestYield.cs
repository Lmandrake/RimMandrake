using RimWorld;
using Verse;

namespace RimMandrake.Webwork
{
	public class RM_CompProperties_HarvestYield : CompProperties
	{
		public ThingDef yield;
		public int count = 1;

		public RM_CompProperties_HarvestYield()
		{
			compClass = typeof(RM_CompHarvestYield);
		}

		public override System.Collections.Generic.IEnumerable<string> ConfigErrors(ThingDef parentDef)
		{
			foreach (string e in base.ConfigErrors(parentDef))
			{
				yield return e;
			}
			if (yield == null)
			{
				yield return "RM_CompProperties_HarvestYield has no yield";
			}
		}
	}

	/// <summary>
	/// SHOKKWEAVE_SOLE_SOURCE_1, the border creep-web harvest route (owner card 2026-09-11: "yields, with teeth"; build
	/// ruled by question card 2026-10-09). The colonist job is vanilla Deconstruct: the creep-web nodes carry
	/// building.alwaysDeconstructible, so the player designates them with the ordinary Deconstruct tool and a
	/// constructor walks over and cuts them (WorkGiver_Deconstruct / JobDriver_Deconstruct). Vanilla deconstruct
	/// leavings refund the cost list, which a natural node does not have, so this comp drops the silk on
	/// DestroyMode.Deconstruct. The "teeth" are RM_CompEmergentSpawnOnDestroy on the same def, which counts a
	/// Deconstruct as a harvest. Combat destruction still yields through killedLeavings; this comp ignores it.
	/// Gate: RM_WebworkSettings.webHarvestEnabled (startup removes alwaysDeconstructible; this also refuses at runtime).
	/// </summary>
	public class RM_CompHarvestYield : ThingComp
	{
		public RM_CompProperties_HarvestYield Props => (RM_CompProperties_HarvestYield)props;

		// Proof read (static: the parent is gone by the time anyone asks); describes the last call only.
		public static int lastYieldSpawned;

		public override void PostDestroy(DestroyMode mode, Map previousMap)
		{
			base.PostDestroy(mode, previousMap);
			lastYieldSpawned = 0;
			if (!RM_WebworkSettings.webHarvestEnabled || mode != DestroyMode.Deconstruct || previousMap == null
				|| Props.yield == null || Props.count <= 0)
			{
				return;
			}
			IntVec3 pos = parent.PositionHeld;
			if (!pos.IsValid || !pos.InBounds(previousMap))
			{
				return;
			}
			Thing silk = ThingMaker.MakeThing(Props.yield);
			silk.stackCount = Props.count;
			if (GenPlace.TryPlaceThing(silk, pos, previousMap, ThingPlaceMode.Near))
			{
				lastYieldSpawned = Props.count;
			}
		}
	}
}
