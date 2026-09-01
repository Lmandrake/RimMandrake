using System;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Plants;

public class IncidentWorker_Weeds : IncidentWorker
{
	private const float Radius = 11f;

	private static readonly SimpleCurve WeedChancePerRadius;

	private static readonly SimpleCurve RadiusFactorPerPointsCurve;

	protected override bool CanFireNowSub(IncidentParms parms)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Expected O, but got Unknown
		Plant_Blooming plant;
		return TryFindRandomWeedablePlant((Map)parms.target, out plant);
	}

	protected override bool TryExecuteWorker(IncidentParms parms)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Expected O, but got Unknown
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		Map val = (Map)parms.target;
		float num = RadiusFactorPerPointsCurve.Evaluate(parms.points);
		if (!TryFindRandomWeedablePlant(val, out var plant))
		{
			return false;
		}
		Room room = RegionAndRoomQuery.GetRoom((Thing)(object)plant, (RegionType)15);
		int i = 0;
		for (int num2 = GenRadial.NumCellsInRadius(11f * num); i < num2; i++)
		{
			IntVec3 val2 = ((Thing)plant).Position + GenRadial.RadialPattern[i];
			if (GenGrid.InBounds(val2, val) && GridsUtility.GetRoom(val2, val) == room)
			{
				Plant_Blooming firstWeedableNowPlant = GetFirstWeedableNowPlant(val2, val);
				if (firstWeedableNowPlant != null && Rand.Chance(WeedChance(((Thing)firstWeedableNowPlant).Position, ((Thing)plant).Position, num)))
				{
					firstWeedableNowPlant.hasWeeds = true;
				}
			}
		}
		((IncidentWorker)this).SendStandardLetter(TranslatorFormattedStringExtensions.Translate("VEF_LetterLabelWeeds", new NamedArgument((object)((Thing)plant).def, "PLANTDEF")), TranslatorFormattedStringExtensions.Translate("VEF_LetterWeeds", new NamedArgument((object)((Thing)plant).def, "PLANTDEF")), LetterDefOf.NegativeEvent, parms, LookTargets.op_Implicit(new TargetInfo(((Thing)plant).Position, val, false)), Array.Empty<NamedArgument>());
		return true;
	}

	private bool TryFindRandomWeedablePlant(Map map, out Plant_Blooming plant)
	{
		Thing val = default(Thing);
		bool result = GenCollection.TryRandomElement<Thing>(from x in map.listerThings.ThingsInGroup((ThingRequestGroup)27)
			where x is Plant_Blooming plant_Blooming && plant_Blooming != null && !plant_Blooming.GetExtension.ImmuneToWeeds
			select x, ref val);
		plant = (Plant_Blooming)(object)val;
		return result;
	}

	private float WeedChance(IntVec3 c, IntVec3 root, float radiusFactor)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		float num = IntVec3Utility.DistanceTo(c, root) / radiusFactor;
		return WeedChancePerRadius.Evaluate(num);
	}

	public Plant_Blooming GetFirstWeedableNowPlant(IntVec3 c, Map map)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		if (GridsUtility.GetPlant(c, map) is Plant_Blooming { hasWeeds: false } plant_Blooming && plant_Blooming != null && !plant_Blooming.GetExtension.ImmuneToWeeds)
		{
			return plant_Blooming;
		}
		return null;
	}

	static IncidentWorker_Weeds()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Expected O, but got Unknown
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Expected O, but got Unknown
		SimpleCurve val = new SimpleCurve();
		val.Add(new CurvePoint(0f, 1f), true);
		val.Add(new CurvePoint(8f, 1f), true);
		val.Add(new CurvePoint(11f, 0.3f), true);
		WeedChancePerRadius = val;
		SimpleCurve val2 = new SimpleCurve();
		val2.Add(new CurvePoint(100f, 0.6f), true);
		val2.Add(new CurvePoint(500f, 1f), true);
		val2.Add(new CurvePoint(2000f, 2f), true);
		RadiusFactorPerPointsCurve = val2;
	}
}
