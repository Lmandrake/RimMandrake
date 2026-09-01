using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using VEF.Factions;
using VEF.Things;
using Verse;
using Verse.AI;

namespace VEF.Planet;

public static class CustomSiegeUtility
{
	private static SiegeParameterSetDef customParams;

	public static bool AcceptsShell(Building_TurretGun artillery, ThingDef shellDef)
	{
		CompChangeableProjectile val = ThingCompUtility.TryGetComp<CompChangeableProjectile>(artillery.gun);
		if (val == null)
		{
			return false;
		}
		return val.allowedShellsSettings.AllowedToAccept(shellDef);
	}

	public static IEnumerable<Blueprint_Build> PlaceBlueprints(LordToilData_SiegeCustom data, Map map, Faction placeFaction)
	{
		customParams = FactionDefExtension.Get((Def)(object)placeFaction.def).siegeParameterSetDef;
		NonPublicFields.SiegeBlueprintPlacer_center.Invoke() = ((LordToilData_Siege)data).siegeCenter;
		NonPublicFields.SiegeBlueprintPlacer_faction.Invoke() = placeFaction;
		if (customParams.coverDef != null)
		{
			List<Blueprint_Build> coverBlueprints = PlaceCoverBlueprints(map).ToList();
			for (int i = 0; i < coverBlueprints.Count; i++)
			{
				yield return coverBlueprints[i];
			}
		}
		if (!GenList.NullOrEmpty<string>((IList<string>)customParams.artilleryBuildingTags))
		{
			List<Blueprint_Build> coverBlueprints = PlaceArtilleryBlueprints(data, map).ToList();
			for (int i = 0; i < coverBlueprints.Count; i++)
			{
				yield return coverBlueprints[i];
			}
		}
	}

	private static IEnumerable<Blueprint_Build> PlaceCoverBlueprints(Map map)
	{
		IntVec3 centre = NonPublicFields.SiegeBlueprintPlacer_center.Invoke();
		IntRange lengthRange = NonPublicFields.SiegeBlueprintPlacer_CoverLengthRange.Invoke();
		IntRange val = NonPublicFields.SiegeBlueprintPlacer_NumCoverRange.Invoke();
		NonPublicFields.SiegeBlueprintPlacer_placedCoverLocs.Invoke().Clear();
		int numSandbags = ((IntRange)(ref val)).RandomInRange;
		ThingDef coverStuff = (((BuildableDef)customParams.coverDef).MadeFromStuff ? GenStuff.RandomStuffInexpensiveFor(customParams.coverDef, NonPublicFields.SiegeBlueprintPlacer_faction.Invoke(), (Predicate<ThingDef>)null) : null);
		for (int i = 0; i < numSandbags; i++)
		{
			IntVec3 bagRoot = FindCoverRoot(map, customParams.coverDef, coverStuff);
			if (!((IntVec3)(ref bagRoot)).IsValid)
			{
				break;
			}
			Rot4 growDir = ((bagRoot.x <= centre.x) ? Rot4.East : Rot4.West);
			Rot4 growDirB = ((bagRoot.z <= centre.z) ? Rot4.North : Rot4.South);
			List<Blueprint_Build> coverLine = MakeCoverLine(bagRoot, map, growDir, ((IntRange)(ref lengthRange)).RandomInRange, customParams.coverDef, coverStuff).ToList();
			for (int j = 0; j < coverLine.Count; j++)
			{
				yield return coverLine[j];
			}
			bagRoot += ((Rot4)(ref growDirB)).FacingCell;
			coverLine = MakeCoverLine(bagRoot, map, growDirB, ((IntRange)(ref lengthRange)).RandomInRange, customParams.coverDef, coverStuff).ToList();
			for (int j = 0; j < coverLine.Count; j++)
			{
				yield return coverLine[j];
			}
			bagRoot = default(IntVec3);
			growDirB = default(Rot4);
		}
	}

	private static IntVec3 FindCoverRoot(Map map, ThingDef coverDef, ThingDef coverStuff)
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 val = NonPublicFields.SiegeBlueprintPlacer_center.Invoke();
		List<IntVec3> list = NonPublicFields.SiegeBlueprintPlacer_placedCoverLocs.Invoke();
		CellRect val2 = CellRect.CenteredOn(val, 13);
		((CellRect)(ref val2)).ClipInsideMap(map);
		CellRect val3 = CellRect.CenteredOn(val, 8);
		((CellRect)(ref val3)).ClipInsideMap(map);
		int num = 0;
		while (true)
		{
			num++;
			if (num > 200)
			{
				break;
			}
			IntVec3 randomCell = ((CellRect)(ref val2)).RandomCell;
			if (((CellRect)(ref val3)).Contains(randomCell) || !map.reachability.CanReach(randomCell, LocalTargetInfo.op_Implicit(val), (PathEndMode)1, (TraverseMode)2, (Danger)3) || !NonPublicMethods.SiegeBlueprintPlacer_CanPlaceBlueprintAt(randomCell, Rot4.North, coverDef, map, coverStuff))
			{
				continue;
			}
			bool flag = false;
			for (int i = 0; i < list.Count; i++)
			{
				IntVec3 val4 = list[i] - randomCell;
				if ((float)((IntVec3)(ref val4)).LengthHorizontalSquared < 36f)
				{
					flag = true;
				}
			}
			if (!flag)
			{
				return randomCell;
			}
		}
		return IntVec3.Invalid;
	}

	private static IEnumerable<Blueprint_Build> MakeCoverLine(IntVec3 root, Map map, Rot4 growDir, int maxLength, ThingDef coverThing, ThingDef coverStuff)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		List<IntVec3> placedSandbagLocs = NonPublicFields.SiegeBlueprintPlacer_placedCoverLocs.Invoke();
		IntVec3 cur = root;
		for (int i = 0; i < maxLength; i++)
		{
			if (!NonPublicMethods.SiegeBlueprintPlacer_CanPlaceBlueprintAt(cur, Rot4.North, coverThing, map, coverStuff))
			{
				break;
			}
			yield return GenConstruct.PlaceBlueprintForBuild((BuildableDef)(object)coverThing, cur, map, Rot4.North, NonPublicFields.SiegeBlueprintPlacer_faction.Invoke(), coverStuff, (Precept_ThingStyle)null, (ThingStyleDef)null, true);
			placedSandbagLocs.Add(cur);
			cur += ((Rot4)(ref growDir)).FacingCell;
		}
	}

	private static IEnumerable<Blueprint_Build> PlaceArtilleryBlueprints(LordToilData_SiegeCustom data, Map map)
	{
		IEnumerable<ThingDef> artyDefs = customParams.artilleryDefs;
		if (!artyDefs.Any())
		{
			Log.Error("Could not find any artillery ThingDefs matching the following tags: " + Gen.ToStringSafeEnumerable((IEnumerable)customParams.artilleryBuildingTags));
			yield break;
		}
		float points = ((LordToilData_Siege)data).blueprintPoints;
		int numArtillery = Mathf.RoundToInt(points / customParams.lowestArtilleryBlueprintPoints);
		numArtillery = Mathf.Clamp(numArtillery, customParams.artilleryCountRange.min, customParams.artilleryCountRange.max);
		int i = 0;
		while (points > 0f && i < numArtillery)
		{
			artyDefs = artyDefs.Where(delegate(ThingDef t)
			{
				ThingDefExtension modExtension = ((Def)t).GetModExtension<ThingDefExtension>();
				return modExtension != null && modExtension.siegeBlueprintPoints <= points;
			});
			if (!artyDefs.Any())
			{
				break;
			}
			Rot4 random = Rot4.Random;
			ThingDef artyDef = GenCollection.RandomElementByWeight<ThingDef>(artyDefs, (Func<ThingDef, float>)((ThingDef t) => ((Def)t).GetModExtension<ThingDefExtension>().siegeBlueprintPoints));
			IntVec3 val = NonPublicMethods.SiegeBlueprintPlacer_FindArtySpot(artyDef, random, map);
			if (!((IntVec3)(ref val)).IsValid)
			{
				break;
			}
			yield return GenConstruct.PlaceBlueprintForBuild((BuildableDef)(object)artyDef, val, map, random, NonPublicFields.SiegeBlueprintPlacer_faction.Invoke(), GenStuff.DefaultStuffFor((BuildableDef)(object)artyDef), (Precept_ThingStyle)null, (ThingStyleDef)null, true);
			if (data.artilleryCounts.ContainsKey(artyDef))
			{
				data.artilleryCounts[artyDef]++;
			}
			else
			{
				data.artilleryCounts.Add(artyDef, 1);
			}
			points -= ((Def)artyDef).GetModExtension<ThingDefExtension>().siegeBlueprintPoints;
			i++;
		}
	}
}
