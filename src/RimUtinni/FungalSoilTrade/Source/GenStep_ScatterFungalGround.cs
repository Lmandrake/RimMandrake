using RimWorld;
using Verse;

namespace RimMandrake.Utinni.FungalSoilTrade
{
	// FUNGAL_SOIL_TRADE_1: scatters RUT_MineableFungalGround knots onto Rot
	// (AB_MycoticJungle) maps only. Pattern copied from
	// src/RimUtinni/LanternDeeps/Source/GenStep_ScatterCavePortal.cs (a plain
	// GenStep_ScatterGroup subclass, self-gated by map.Biome.defName, discovered
	// by RimWorld's own GenStepDef the moment the XML names it in genStep Class -
	// no Harmony, no registration call needed for the scatter itself).
	//
	// ANTI-EXPONENTIAL (the item's hard constraint): the GenStepDef's
	// coveredCellsPer10Cells/clusterRectRadius bound how many knots a single map
	// gets, and RUT_MineableFungalGround has no regrowth and no craft recipe -
	// once a map's knots are mined out, that map's soil income is done. A player
	// wanting more must find another Rot map/tile, not re-dig the same one.
	public class GenStep_ScatterFungalGround : GenStep_ScatterGroup
	{
		public const string RotBiomeDefName = "AB_MycoticJungle";

		public override void Generate(Map map, GenStepParams parms)
		{
			if (!FungalSoilTradeSettings.scatterEnabled)
			{
				return;
			}
			if (map.Biome == null || map.Biome.defName != RotBiomeDefName)
			{
				return;
			}
			base.Generate(map, parms);
		}
	}
}
