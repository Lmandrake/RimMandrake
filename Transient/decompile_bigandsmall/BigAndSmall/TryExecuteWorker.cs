using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(IncidentWorker_WandererJoin), "GeneratePawn")]
public static class TryExecuteWorker
{
	public static void Postfix(Pawn __result, IncidentWorker_WandererJoin __instance)
	{
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Expected O, but got Unknown
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Expected O, but got Unknown
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Expected O, but got Unknown
		//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Expected O, but got Unknown
		//IL_0299: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a4: Expected O, but got Unknown
		//IL_02cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0300: Unknown result type (might be due to invalid IL or missing references)
		//IL_0334: Unknown result type (might be due to invalid IL or missing references)
		//IL_0211: Unknown result type (might be due to invalid IL or missing references)
		//IL_021c: Expected O, but got Unknown
		//IL_03cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d4: Expected O, but got Unknown
		//IL_03b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_03bf: Expected O, but got Unknown
		//IL_0411: Unknown result type (might be due to invalid IL or missing references)
		IncidentDef val = ((IncidentWorker)(__instance?)).def;
		if (val == null || val != DefDatabase<IncidentDef>.GetNamedSilentFail("BS_WomanInBlueJoin"))
		{
			return;
		}
		PawnKindDef pawnKind = val.pawnKind;
		__result.apparel.DestroyAll((DestroyMode)0);
		__result.style.BodyTattoo = TattooDefOf.NoTattoo_Body;
		__result.style.FaceTattoo = TattooDefOf.NoTattoo_Face;
		List<NameTriple> list = new List<NameTriple>
		{
			new NameTriple("Skadi", "Skadi", "Huntress"),
			new NameTriple("Angrboda ", "Angra ", "Jarnvid"),
			new NameTriple("Gerd ", "Gerd ", "Evergreen")
		};
		while (list.Count > 0)
		{
			NameTriple val2 = GenCollection.RandomElement<NameTriple>((IEnumerable<NameTriple>)list);
			if (((Name)val2).UsedThisGame)
			{
				list.Remove(val2);
				continue;
			}
			__result.Name = (Name)(object)val2;
			if (val2.First == "Skadi")
			{
				if (!__result.story.traits.HasTrait(BSDefs.SpeedOffset))
				{
					__result.story.traits.GainTrait(new Trait(BSDefs.SpeedOffset, 2, false), false);
				}
				__result.skills.GetSkill(SkillDefOf.Melee).Level = Rand.Range(9, 18);
				__result.skills.GetSkill(SkillDefOf.Shooting).Level = Rand.Range(10, 16);
				__result.skills.GetSkill(SkillDefOf.Shooting).passion = (Passion)2;
				__result.skills.GetSkill(SkillDefOf.Plants).Level = Rand.Range(4, 16);
			}
			else if (val2.First == "Angrboda")
			{
				__result.Name = (Name)(object)val2;
				__result.skills.GetSkill(SkillDefOf.Melee).Level = Rand.Range(10, 16);
				__result.skills.GetSkill(SkillDefOf.Melee).passion = (Passion)2;
				if (!__result.story.traits.HasTrait(BSDefs.Tough))
				{
					__result.story.traits.GainTrait(new Trait(BSDefs.Tough, 0, false), false);
				}
				Trait trait = __result.story.traits.GetTrait(DefDatabase<TraitDef>.GetNamed("BS_Gentle", true));
				__result.story.traits.RemoveTrait(trait, false);
				__result.genes.AddGene(DefDatabase<GeneDef>.GetNamed("Fertile", true), false);
			}
			else if (val2.First == "Gerd")
			{
				__result.Name = (Name)(object)val2;
				__result.story.traits.GainTrait(new Trait(BSDefs.Beauty, 2, false), false);
				__result.skills.GetSkill(SkillDefOf.Plants).Level = 20;
				__result.skills.GetSkill(SkillDefOf.Plants).passion = (Passion)2;
				__result.skills.GetSkill(SkillDefOf.Social).Level = Rand.Range(12, 20);
				__result.skills.GetSkill(SkillDefOf.Social).passion = (Passion)1;
				__result.skills.GetSkill(SkillDefOf.Medicine).Level = Rand.Range(10, 20);
				__result.skills.GetSkill(SkillDefOf.Medicine).passion = (Passion)1;
			}
			break;
		}
		Pawn_NeedsTracker needs = __result.needs;
		if (needs != null)
		{
			Need_Food food = needs.food;
			if (food != null)
			{
				_ = ((Need)food).CurLevelPercentage;
				if (true)
				{
					((Need)__result.needs.food).CurLevelPercentage = 0.75f;
				}
			}
		}
		QualityCategory val4 = default(QualityCategory);
		foreach (ThingDef item in pawnKind.apparelRequired)
		{
			Apparel val3 = ((!(((Def)item).defName != "Apparel_Pants")) ? ((Apparel)ThingMaker.MakeThing(item, ThingDefOf.Steel)) : ((Apparel)ThingMaker.MakeThing(item, ThingDefOf.Leather_Plain)));
			if (QualityUtility.TryGetQuality((Thing)(object)val3, ref val4))
			{
				ThingCompUtility.TryGetComp<CompQuality>((Thing)(object)val3).SetQuality((QualityCategory)3, (ArtGenerationContext?)(ArtGenerationContext)0);
			}
			if (((Thing)val3).def.colorGenerator != null)
			{
				CompColorableUtility.SetColor((Thing)(object)val3, new Color(0.549f, 0.666f, 1f), false);
			}
			__result.apparel.Wear(val3, true, false);
		}
	}
}
