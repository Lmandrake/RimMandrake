using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShokkweaveEconomy
{
	// SHOKKWEAVE_SOLE_SOURCE_1, build-order step 4: scatters the two Webwork
	// harvest nodes (RUT_Webwork_SilkKnot, RUT_Webwork_Nest) onto RUT_Webwork
	// maps only. Pattern copied verbatim from
	// src/RimUtinni/FungalSoilTrade/Source/GenStep_ScatterFungalGround.cs (itself
	// copied from LanternDeeps' GenStep_ScatterCavePortal): a plain
	// GenStep_ScatterGroup subclass, self-gated by map.Biome.defName, discovered
	// by RimWorld's own GenStepDef loader the moment the XML names it in
	// genStep Class - no Harmony, no registration call needed for the scatter
	// itself. One class serves BOTH GenStepDefs (RUT_WebworkSilkScatter,
	// RUT_WebworkNestScatter) below; the things/density difference lives
	// entirely in each GenStepDef's own XML.
	//
	// Biome gate uses RUT_Webwork (our own biome, BIOME_OWNERSHIP_WAVE_1) - not
	// the donor AB_FeraliskInfestedJungle - because RUT_Webwork is the def
	// actually painted on the live world map (RUT_Webwork.xml's own header:
	// "Replaces the donor AB_FeraliskInfestedJungle").
	public class GenStep_ScatterWebworkSilk : GenStep_ScatterGroup
	{
		public const string WebworkBiomeDefName = "RUT_Webwork";

		public override void Generate(Map map, GenStepParams parms)
		{
			if (map.Biome == null || map.Biome.defName != WebworkBiomeDefName)
			{
				return;
			}
			base.Generate(map, parms);
		}
	}
}
