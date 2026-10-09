using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Webwork
{
	public class RM_CompProperties_EmergentSpawnOnDestroy : CompProperties
	{
		/// <summary>Chance per destruction that this fires.</summary>
		public float spawnChance = 0.03f;

		/// <summary>
		/// defName of the PawnKindDef to spawn, resolved by soft lookup at
		/// spawn time (never at load) so this mod never hard-errors if the
		/// species mod is absent — it simply never spawns anything.
		/// </summary>
		public string spawnPawnKindDefName = "RM_Ollathrix";

		public RM_CompProperties_EmergentSpawnOnDestroy()
		{
			compClass = typeof(RM_CompEmergentSpawnOnDestroy);
		}
	}

	/// <summary>
	/// SHOKK_SKIN_SHRINK_1 (moved from mandrake.rsw.shokk's
	/// RSW_CompEmergentSpawnOnDestroy, SHOKK_RSW_MOD_1, S6 ruling 1 —
	/// mechanism-not-IP, belongs in the free tier). RULED 2026-09-11,
	/// owner-verbatim on the sole-source boundary card: "(2) but it has a
	/// small chance of SPAWNING an emergent Shokk to get you." Attach via
	/// RM_CompProperties_EmergentSpawnOnDestroy to any Thing whose
	/// destruction represents a harvest (a creep-web node, a gutter, …) —
	/// on a DestroyMode.Vanish or Deconstruct (the harvest cases; never fires
	/// on Kill/Refund/etc.) it rolls the configured chance and spawns a hostile ollathrix
	/// (or whatever PawnKindDef the attaching def names) at the spot,
	/// manhunter-forced.
	///
	/// Attached to the creep-web nodes RM_Webwork_Anchor/_Web/_Gutter
	/// (SHOKKWEAVE_SOLE_SOURCE_1): a colonist cutting one with the vanilla
	/// Deconstruct job destroys it with DestroyMode.Deconstruct, which counts
	/// as a harvest here; combat destruction (KillFinalize) never fires it.
	/// </summary>
	public class RM_CompEmergentSpawnOnDestroy : ThingComp
	{
		public RM_CompProperties_EmergentSpawnOnDestroy Props => (RM_CompProperties_EmergentSpawnOnDestroy)props;

		public override void PostDestroy(DestroyMode mode, Map previousMap)
		{
			base.PostDestroy(mode, previousMap);
			if (!RM_EmergentKernel.Fires(RM_WebworkSettings.emergentSpawnEnabled, previousMap != null, mode == DestroyMode.Vanish || mode == DestroyMode.Deconstruct,
				Props.spawnChance, RM_WebworkSettings.emergentSpawnChanceMultiplier, Rand.Value))
			{
				return;
			}
			PawnKindDef kindDef = DefDatabase<PawnKindDef>.GetNamedSilentFail(Props.spawnPawnKindDefName);
			if (kindDef == null)
			{
				return;
			}
			IntVec3 pos = parent.PositionHeld;
			if (!pos.IsValid || !pos.InBounds(previousMap))
			{
				return;
			}
			Pawn pawn = PawnGenerator.GeneratePawn(kindDef);
			GenSpawn.Spawn(pawn, pos, previousMap);
			if (pawn.mindState != null)
			{
				pawn.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, forceWake: true);
			}
		}
	}
}
