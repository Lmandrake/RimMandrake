using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
	// LANTERN_DEEPS_INJECTION_1 spec item 2b: the ruined-mineshaft entrance,
	// counterpart to RUT_LanternDeepEmergence's natural-mouth scatter
	// (GenStep_ScatterCavePortal). Both entrance types reach the SAME Deeps
	// (the_lantern_deeps.md's "Injection rule"), so both are bound by the
	// same host-biome gate; this one carries its own independent chance and
	// its own Mod Settings toggle so the two entrance types don't compete
	// for the same map roll or the same on/off switch.
	//
	// ASSUMPTION recorded, not guessed silently: the task brief's "near
	// existing mine/ruin sites rather than random biome scatter" is NOT
	// implemented here. Ruin/mine placement is a WORLD-layer concept
	// (WorldObjects/Sites); a GenStepDef runs at map-generation time with no
	// clean hook back to sibling site placement, and building one is a
	// larger world-authoring feature than this pass's budget covers. Left as
	// ordinary qualifying-biome scatter, same mechanism as the emergence
	// entrance, at a lower rate reflecting "old mineshaft" being the rarer
	// of the two entrance flavors — a real placement rule tying this to
	// actual ruin/mine world sites is owed at the caverns sitting.
	public class GenStep_ScatterMineshaftPortal : GenStep_ScatterGroup
	{
		private static readonly HashSet<string> AllowedBiomeDefNames = new HashSet<string>
		{
			"BiomeGRimond",
			"RUT_NightsideIce",
			"RUT_PropaneLake",
		};

		public float chancePerMap = 0.04f;

		private static ThingDef mineshaftDefCached;

		private static ThingDef MineshaftDef =>
			mineshaftDefCached ?? (mineshaftDefCached = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_LanternDeepMineshaft"));

		public override void Generate(Map map, GenStepParams parms)
		{
			if (!LanternDeepsSettings.mineshaftEnabled)
			{
				return;
			}
			if (map.Biome == null || !AllowedBiomeDefNames.Contains(map.Biome.defName))
			{
				return;
			}
			if (!Rand.Chance(Mathf.Clamp01(chancePerMap * LanternDeepsSettings.mineshaftChanceMultiplier)))
			{
				return;
			}

			ThingDef mineshaftDef = MineshaftDef;
			int placedBefore = (mineshaftDef != null) ? map.listerThings.ThingsOfDef(mineshaftDef).Count : 0;
			base.Generate(map, parms);
			if (mineshaftDef == null)
			{
				return;
			}
			List<Thing> portals = map.listerThings.ThingsOfDef(mineshaftDef);
			if (portals.Count <= placedBefore)
			{
				return; // the scatter step found no valid cell this map; nothing to dress
			}

			DressRuinedMineshaft(map, portals[portals.Count - 1].Position);
		}

		// "well-provisioned high-tech ruin ... corpses in excellent gear"
		// (LANTERN_DEEPS_INJECTION_1 spec item 2b). Reuses the same
		// pawn-generate-then-kill pattern vanilla's own UndercaveMapComponent
		// uses for its fleshbeast corpses (PawnGenerator.GeneratePawn +
		// GenSpawn.Spawn) -- deliberately NOT the KCSG-symbol pawn path that
		// crashed the sibling StructureInjectionsRUT mod's mechanoid symbol
		// (that failure was inside KCSG's own structure-resolution faction
		// handling; this GenStep never touches KCSG at all). AncientSoldier
		// is vanilla-shipped and already used elsewhere in this repo
		// (RUT_Symbol_RakataCasket) for the same "ancient tech corpse" flavor.
		private static void DressRuinedMineshaft(Map map, IntVec3 portalPos)
		{
			PawnKindDef corpseKind = DefDatabase<PawnKindDef>.GetNamedSilentFail("AncientSoldier");
			if (corpseKind != null
				&& CellFinder.TryFindRandomCellNear(portalPos, map, 4,
					c => c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null, out IntVec3 corpseCell))
			{
				var request = new PawnGenerationRequest(
					corpseKind,
					null,
					PawnGenerationContext.NonPlayer,
					forceGenerateNewPawn: true,
					canGeneratePawnRelations: false);
				Pawn pawn = PawnGenerator.GeneratePawn(request);
				GenSpawn.Spawn(pawn, corpseCell, map);
				pawn.Kill(null);
			}

			for (int i = 0; i < 5; i++)
			{
				if (CellFinder.TryFindRandomCellNear(portalPos, map, 5,
					c => c.InBounds(map) && c.Standable(map), out IntVec3 rubbleCell))
				{
					FilthMaker.TryMakeFilth(rubbleCell, map, ThingDefOf.Filth_RubbleRock, Rand.RangeInclusive(1, 2));
				}
			}
		}
	}
}
