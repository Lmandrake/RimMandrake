using System.Collections.Generic;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimWorld;
using VEF.Apparels;
using VEF.Hediffs;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(StatPart_TerrainMoveSpeed), "ExplanationPart")]
[HarmonyPatchCategory("MoveSpeedFactorByTerrainTag")]
public static class VanillaExpandedFramework_StatPart_TerrainMoveSpeed_ExplanationPart
{
	private static readonly Dictionary<string, float> totalSpeed = new Dictionary<string, float>();

	private static readonly HashSet<(string, string)> usedTags = new HashSet<(string, string)>();

	public static bool Prefix(StatRequest req, out string __result)
	{
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		Thing thing = ((StatRequest)(ref req)).Thing;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val == null)
		{
			__result = null;
			return false;
		}
		try
		{
			FillSpeedFactorsData(val);
			if (totalSpeed.Count == 0)
			{
				__result = null;
				return false;
			}
			StringBuilder stringBuilder = new StringBuilder();
			string text = default(string);
			float num = default(float);
			foreach (KeyValuePair<string, float> item in totalSpeed.OrderBy((KeyValuePair<string, float> x) => x.Key))
			{
				GenCollection.Deconstruct<string, float>(item, ref text, ref num);
				string text2 = text;
				float num2 = num;
				if (stringBuilder.Length > 0)
				{
					stringBuilder.AppendLine();
				}
				TaggedString val2 = Translator.Translate("TerrainTag" + text2);
				stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("StatsReport_TerrainSpeedMultiplier", NamedArgument.op_Implicit(val2)) + ": x" + GenText.ToStringPercent(num2)));
			}
			__result = stringBuilder.ToString();
			return false;
		}
		finally
		{
			totalSpeed.Clear();
			usedTags.Clear();
		}
	}

	private static void FillSpeedFactorsData(Pawn pawn)
	{
		if (pawn.kindDef?.moveSpeedFactorByTerrainTag != null)
		{
			string text = default(string);
			float speedFactor = default(float);
			foreach (KeyValuePair<string, float> item in pawn.kindDef.moveSpeedFactorByTerrainTag)
			{
				GenCollection.Deconstruct<string, float>(item, ref text, ref speedFactor);
				string terrainTag = text;
				AddSpeed(speedFactor, terrainTag);
			}
		}
		if (ModsConfig.BiotechActive)
		{
			Pawn_GeneTracker genes = pawn.genes;
			if (((genes != null) ? genes.GenesListForReading : null) != null)
			{
				foreach (Gene item2 in pawn.genes.GenesListForReading)
				{
					AddSpeed(((Def)item2.def).GetModExtension<GeneExtension>()?.moveSpeedFactorByTerrainTag);
				}
			}
		}
		if (pawn.health?.hediffSet?.hediffs != null)
		{
			foreach (Hediff hediff in pawn.health.hediffSet.hediffs)
			{
				AddSpeed(HediffUtility.TryGetComp<HediffComp_MoveSpeedFactorByTerrainTag>(hediff)?.Props.moveSpeedFactorByTerrainTag);
			}
		}
		Pawn_EquipmentTracker equipment = pawn.equipment;
		if (((equipment != null) ? equipment.AllEquipmentListForReading : null) != null)
		{
			foreach (ThingWithComps item3 in pawn.equipment.AllEquipmentListForReading)
			{
				ThingDef def = ((Thing)item3).def;
				AddSpeed((def != null) ? ((Def)def).GetModExtension<ApparelExtension>()?.moveSpeedFactorByTerrainTag : null);
			}
		}
		Pawn_ApparelTracker apparel = pawn.apparel;
		if (((apparel != null) ? apparel.WornApparel : null) == null)
		{
			return;
		}
		foreach (Apparel item4 in pawn.apparel.WornApparel)
		{
			ThingDef def2 = ((Thing)item4).def;
			AddSpeed((def2 != null) ? ((Def)def2).GetModExtension<ApparelExtension>()?.moveSpeedFactorByTerrainTag : null);
		}
	}

	private static void AddSpeed(Dictionary<string, List<MoveSpeedFactor>> moveSpeedFactorByTerrainTag)
	{
		if (GenDictionary.NullOrEmpty<string, List<MoveSpeedFactor>>(moveSpeedFactorByTerrainTag))
		{
			return;
		}
		string text = default(string);
		List<MoveSpeedFactor> list = default(List<MoveSpeedFactor>);
		foreach (KeyValuePair<string, List<MoveSpeedFactor>> item in moveSpeedFactorByTerrainTag)
		{
			GenCollection.Deconstruct<string, List<MoveSpeedFactor>>(item, ref text, ref list);
			string terrainTag = text;
			foreach (MoveSpeedFactor item2 in list)
			{
				AddSpeed(item2.moveSpeedFactor, terrainTag, item2.tag);
			}
		}
	}

	private static void AddSpeed(float speedFactor, string terrainTag, string speedFactorTag = null)
	{
		if (terrainTag != null && (speedFactorTag == null || !usedTags.Add((terrainTag, speedFactorTag))))
		{
			float value = ((!totalSpeed.TryGetValue(terrainTag, out value)) ? speedFactor : (value * speedFactor));
			totalSpeed[terrainTag] = value;
		}
	}
}
