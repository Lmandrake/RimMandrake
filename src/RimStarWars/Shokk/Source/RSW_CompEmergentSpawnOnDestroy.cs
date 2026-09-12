using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Shokk
{
	public class RSW_CompProperties_EmergentSpawnOnDestroy : CompProperties
	{
		/// <summary>Chance per destruction that this fires.</summary>
		public float spawnChance = 0.03f;

		/// <summary>
		/// defName of the PawnKindDef to spawn, resolved by soft lookup at
		/// spawn time (never at load) so this mod never hard-errors if the
		/// species mod is absent — it simply never spawns anything.
		/// </summary>
		public string spawnPawnKindDefName = "Wyyyschokk";

		public RSW_CompProperties_EmergentSpawnOnDestroy()
		{
			compClass = typeof(RSW_CompEmergentSpawnOnDestroy);
		}
	}

	/// <summary>
	/// SHOKK_RSW_MOD_1 — the emergent-Shokk spawn hook. RULED 2026-09-11,
	/// owner-verbatim on the sole-source boundary card: "(2) but it has a
	/// small chance of SPAWNING an emergent Shokk to get you." Attach via
	/// RSW_CompProperties_EmergentSpawnOnDestroy to any Thing whose
	/// destruction represents a harvest (a creep-web node, a gutter, …) —
	/// on a DestroyMode.Vanish (the harvest case; never fires on Kill/Refund/
	/// etc.) it rolls the configured chance and spawns a hostile Wyyyschokk
	/// at the spot.
	///
	/// Not wired to any recipe by this mod: the creep-web harvest that will
	/// attach this comp belongs to SHOKKWEAVE_SOLE_SOURCE_1 (unbuilt as of
	/// this mod's creation). This ships the mechanism; that item's own
	/// ThingDef patch is the consumer, added with a MayRequire on this mod's
	/// packageId — the same cross-mod-boundary pattern RUT_Webwork.xml
	/// already uses for RSW_JewelBeetle.
	/// </summary>
	public class RSW_CompEmergentSpawnOnDestroy : ThingComp
	{
		public RSW_CompProperties_EmergentSpawnOnDestroy Props => (RSW_CompProperties_EmergentSpawnOnDestroy)props;

		public override void PostDestroy(DestroyMode mode, Map previousMap)
		{
			base.PostDestroy(mode, previousMap);
			if (!RSW_ShokkSettings.emergentSpawnEnabled)
			{
				return;
			}
			if (previousMap == null || mode != DestroyMode.Vanish)
			{
				return;
			}
			if (!Rand.Chance(Props.spawnChance * RSW_ShokkSettings.emergentSpawnChanceMultiplier))
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
