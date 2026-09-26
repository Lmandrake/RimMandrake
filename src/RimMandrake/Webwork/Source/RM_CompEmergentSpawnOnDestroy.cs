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
	/// on a DestroyMode.Vanish (the harvest case; never fires on Kill/Refund/
	/// etc.) it rolls the configured chance and spawns a hostile ollathrix
	/// (or whatever PawnKindDef the attaching def names) at the spot,
	/// manhunter-forced.
	///
	/// Not wired to any recipe by this mod: the creep-web harvest that will
	/// attach this comp belongs to SHOKKWEAVE_SOLE_SOURCE_1 (unbuilt as of
	/// this move) — see that item's own note on why the two harvest nodes
	/// shipped so far (RUT_Webwork_Anchor/_Web/_Gutter, combat-destroyed via
	/// DestroyMode.KillFinalize) cannot use this comp as-is.
	/// </summary>
	public class RM_CompEmergentSpawnOnDestroy : ThingComp
	{
		public RM_CompProperties_EmergentSpawnOnDestroy Props => (RM_CompProperties_EmergentSpawnOnDestroy)props;

		public override void PostDestroy(DestroyMode mode, Map previousMap)
		{
			base.PostDestroy(mode, previousMap);
			if (!RM_WebworkSettings.emergentSpawnEnabled)
			{
				return;
			}
			if (previousMap == null || mode != DestroyMode.Vanish)
			{
				return;
			}
			if (!Rand.Chance(Props.spawnChance * RM_WebworkSettings.emergentSpawnChanceMultiplier))
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
