using RimWorld;
using Verse;

namespace RimMandrake.Utinni.RustCathedralWalls
{
	// RUST_CATHEDRAL_MECHANICS_1 §2, Tier 3. A plain GenStep rather than a
	// GenStep_ScatterGroup subclass: the vanilla scatter classes have no
	// hook to set faction on what they place, and a sacred wall is
	// meaningless without being owned by faction 13 (vanilla `Mechanoid`,
	// reskinned "the Forgotten/Forsaken Arsenal" —
	// src/RimUtinni/UtinniPatches/Patches/ForgottenArsenal.xml — the SAME
	// faction, not a new one). Self-gated on RUT_RustCathedral, same
	// convention as GenStep_ScatterCathedralWallTiers.
	//
	// v1 scope: places at most one instance of the single ruled sacred wall
	// variant per qualifying map, at low chance — the sheet's ~10-building
	// sacred tier across 236 tiles is not "one per map" density. See the
	// GenStepDef's own header for the exact placeholder numbers.
	public class GenStep_ScatterSacredWalls : GenStep
	{
		public const string CathedralBiomeDefName = "RUT_RustCathedral";

		public ThingDef thingDef;

		public float chancePerMap = 0.15f;

		public IntRange countRange = new IntRange(1, 1);

		public int minEdgeDistance = 8;

		public override int SeedPart => 1789452361;

		public override void Generate(Map map, GenStepParams parms)
		{
			if (!RustCathedralWallsSettings.sacredWallsEnabled)
			{
				return;
			}
			if (map.Biome == null || map.Biome.defName != CathedralBiomeDefName)
			{
				return;
			}
			if (thingDef == null)
			{
				Log.Error("[RustCathedralWalls] GenStep_ScatterSacredWalls has no thingDef configured.");
				return;
			}
			float effectiveChance = UnityEngine.Mathf.Clamp01(chancePerMap * RustCathedralWallsSettings.sacredWallChanceMultiplier);
			if (!Rand.Chance(effectiveChance))
			{
				return;
			}

			Faction sacredOwner = Faction.OfMechanoids;
			int count = countRange.RandomInRange;
			for (int i = 0; i < count; i++)
			{
				if (!CellFinderLoose.TryFindRandomNotEdgeCellWith(minEdgeDistance,
					    (IntVec3 c) => CanPlaceAt(c, map), map, out IntVec3 cell))
				{
					continue;
				}

				Thing wall = ThingMaker.MakeThing(thingDef);
				GenSpawn.Spawn(wall, cell, map, WipeMode.Vanish);
				// Faction ownership is what makes vanilla's own AttackedBuilding
				// goodwill hook fire on damage/claim — engine-default behaviour
				// on any faction-owned building, no new code needed for that
				// part (per this item's own brief). The −15 magnitude and the
				// hum-irritation bump both ride §1 (hum-mood system), which does
				// not exist yet — nothing here references it.
				if (sacredOwner != null)
				{
					wall.SetFaction(sacredOwner);
				}
			}
		}

		private bool CanPlaceAt(IntVec3 c, Map map)
		{
			if (!c.Standable(map))
			{
				return false;
			}
			if (!c.GetAffordances(map).Contains(thingDef.terrainAffordanceNeeded))
			{
				return false;
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (t.def.category == ThingCategory.Building)
				{
					return false;
				}
			}
			return true;
		}
	}
}
