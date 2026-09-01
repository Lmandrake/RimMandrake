using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using VEF.Apparels;
using VEF.Things;
using Verse;

namespace VEF.Pawns;

public static class PawnShieldGenerator
{
	private static List<ThingStuffPair> allShieldPairs;

	private static List<ThingStuffPair> workingShields = new List<ThingStuffPair>();

	public static void Reset()
	{
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		allShieldPairs = ThingStuffPair.AllWith((Predicate<ThingDef>)isShield);
		using (IEnumerator<ThingDef> enumerator = DefDatabase<ThingDef>.AllDefs.Where((ThingDef td) => isShield(td)).GetEnumerator())
		{
			while (enumerator.MoveNext())
			{
				ThingDef thingDef = enumerator.Current;
				float num = allShieldPairs.Where((ThingStuffPair pa) => pa.thing == thingDef).Sum((ThingStuffPair pa) => ((ThingStuffPair)(ref pa)).Commonality);
				float num2 = thingDef.generateCommonality / num;
				if (num2 == 1f)
				{
					continue;
				}
				for (int i = 0; i < allShieldPairs.Count; i++)
				{
					ThingStuffPair val = allShieldPairs[i];
					if (val.thing == thingDef)
					{
						allShieldPairs[i] = new ThingStuffPair(val.thing, val.stuff, val.commonalityMultiplier * num2);
					}
				}
			}
			enumerator.Dispose();
		}
		static bool isShield(ThingDef td)
		{
			CompProperties_Shield compProperties = td.GetCompProperties<CompProperties_Shield>();
			if (compProperties != null)
			{
				return !GenList.NullOrEmpty<string>((IList<string>)compProperties.shieldTags);
			}
			return false;
		}
	}

	public static void TryGenerateShieldFor(Pawn pawn)
	{
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0163: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d3: Expected O, but got Unknown
		//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_021e: Unknown result type (might be due to invalid IL or missing references)
		workingShields.Clear();
		PawnKindDefExtension pawnKindDefExtension = PawnKindDefExtension.Get((Def)(object)pawn.kindDef);
		if (GenList.NullOrEmpty<string>((IList<string>)pawnKindDefExtension.shieldTags) || !pawn.RaceProps.ToolUser)
		{
			return;
		}
		ThingWithComps primary = pawn.equipment.Primary;
		if ((primary != null && !((Thing)primary).def.UsableWithShields()) || GenCollection.Count<ThingWithComps>(pawn.equipment.AllEquipmentListForReading, (Predicate<ThingWithComps>)((ThingWithComps t) => (int)((Thing)t).def.equipmentType == 1)) > 1 || !pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) || !pawn.CanUseShields() || (pawn.story != null && pawn.WorkTagIsDisabled((WorkTags)8)))
		{
			return;
		}
		float randomInRange = ((FloatRange)(ref pawnKindDefExtension.shieldMoney)).RandomInRange;
		for (int i = 0; i < allShieldPairs.Count; i++)
		{
			ThingStuffPair val = allShieldPairs[i];
			if (((ThingStuffPair)(ref val)).Price <= randomInRange)
			{
				CompProperties_Shield shieldProps = val.thing.GetCompProperties<CompProperties_Shield>();
				if ((pawnKindDefExtension.shieldTags == null || GenCollection.Any<string>(pawnKindDefExtension.shieldTags, (Predicate<string>)((string tag) => shieldProps.shieldTags.Contains(tag)))) && (val.thing.generateAllowChance >= 1f || Rand.ChanceSeeded(val.thing.generateAllowChance, ((Thing)pawn).thingIDNumber ^ ((Def)val.thing).shortHash ^ 0x1B3B648)))
				{
					workingShields.Add(val);
				}
			}
		}
		if (workingShields.Count == 0)
		{
			return;
		}
		ThingStuffPair val2 = default(ThingStuffPair);
		if (GenCollection.TryRandomElementByWeight<ThingStuffPair>((IEnumerable<ThingStuffPair>)workingShields, (Func<ThingStuffPair, float>)((ThingStuffPair w) => ((ThingStuffPair)(ref w)).Commonality * ((ThingStuffPair)(ref w)).Price), ref val2))
		{
			Apparel val3 = (Apparel)ThingMaker.MakeThing(val2.thing, val2.stuff);
			PawnGenerator.PostProcessGeneratedGear((Thing)(object)val3, pawn);
			if (((Thing)pawn).Faction != null)
			{
				ThingDefExtension modExtension = ((Def)val2.thing).GetModExtension<ThingDefExtension>();
				if (modExtension != null && !GenList.NullOrEmpty<PawnKindDef>((IList<PawnKindDef>)modExtension.useFactionColourForPawnKinds) && modExtension.useFactionColourForPawnKinds.Contains(pawn.kindDef))
				{
					CompColorableUtility.SetColor((Thing)(object)val3, ((Thing)pawn).Faction.Color, true);
				}
			}
			pawn.AddShield(val3);
		}
		workingShields.Clear();
	}
}
