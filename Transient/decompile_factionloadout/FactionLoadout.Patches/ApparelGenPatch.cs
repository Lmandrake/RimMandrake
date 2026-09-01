using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PawnApparelGenerator), "GenerateStartingApparelFor")]
public static class ApparelGenPatch
{
	public class AccumulatedApparelEdits
	{
		public HashSet<ThingDef> apparelRequired = new HashSet<ThingDef>();

		public HashSet<string> apparelTagsAllowed = new HashSet<string>();

		public List<SpecRequirementEdit> always = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> chance = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> pool1 = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> pool2 = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> pool3 = new List<SpecRequirementEdit>();

		public List<SpecRequirementEdit> pool4 = new List<SpecRequirementEdit>();

		public HashSet<HairDef> hairs = new HashSet<HairDef>();

		public HashSet<BeardDef> beards = new HashSet<BeardDef>();

		public HashSet<TattooDef> faceTattoos = new HashSet<TattooDef>();

		public HashSet<TattooDef> bodyTattoos = new HashSet<TattooDef>();

		public List<Color> hairColors = new List<Color>();

		public int editCount;

		public bool anyForceNaked;

		public bool anyForceOnlySelected;
	}

	private static void Postfix(Pawn pawn)
	{
		//IL_01ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null)
		{
			return;
		}
		AccumulatedApparelEdits edits = new AccumulatedApparelEdits();
		foreach (PawnKindEdit item in PawnKindEdit.GetEditsFor(pawn.kindDef, ((Thing)pawn).Faction?.def))
		{
			Accumulate(edits, item);
			edits.editCount++;
		}
		if (edits.anyForceNaked)
		{
			Pawn_ApparelTracker apparel = pawn.apparel;
			if (apparel != null)
			{
				apparel.DestroyAll((DestroyMode)0);
			}
		}
		if (edits.anyForceOnlySelected)
		{
			Pawn_ApparelTracker apparel2 = pawn.apparel;
			foreach (Apparel item2 in ((apparel2 == null) ? null : apparel2.WornApparel?.Where((Apparel a) => !edits.apparelRequired.Contains(((Thing)a).def) && !GenCollection.Any<string>(((Thing)a).def?.apparel?.tags ?? new List<string>(), (Predicate<string>)((string t) => edits.apparelTagsAllowed.Contains(t)))).ToList()) ?? new List<Apparel>())
			{
				ModCore.Debug(TaggedString.op_Implicit(((Def)((Thing)item2).def).LabelCap + "Destroyed"));
				((Thing)item2).Destroy((DestroyMode)0);
			}
		}
		if (edits.editCount > 0 && pawn.RaceProps.ToolUser)
		{
			ForceGiveClothes(pawn, edits);
		}
		if (edits.editCount > 0 && !edits.anyForceNaked)
		{
			HandleApparelPriceLimit(pawn);
		}
		HairDef forcedHair = GetForcedHair(edits);
		BeardDef forcedBeard = GetForcedBeard(edits);
		Color? forcedHairColor = GetForcedHairColor(edits);
		if (pawn.story == null)
		{
			return;
		}
		if (forcedBeard != null && pawn.style != null && pawn.style.beardDef != forcedBeard)
		{
			pawn.style.beardDef = forcedBeard;
		}
		if (forcedHair != null)
		{
			pawn.story.hairDef = forcedHair;
		}
		if (forcedHairColor.HasValue)
		{
			pawn.story.HairColor = forcedHairColor.Value;
		}
		if (ModsConfig.IdeologyActive && pawn.style != null)
		{
			TattooDef forcedTattoo = GetForcedTattoo(edits.faceTattoos);
			TattooDef forcedTattoo2 = GetForcedTattoo(edits.bodyTattoos);
			if (forcedTattoo != null)
			{
				pawn.style.FaceTattoo = forcedTattoo;
			}
			if (forcedTattoo2 != null)
			{
				pawn.style.BodyTattoo = forcedTattoo2;
			}
		}
		if (ModLister.IdeologyInstalled)
		{
			Pawn_StyleTracker style = pawn.style;
			if (style != null)
			{
				style.Notify_StyleItemChanged();
			}
			return;
		}
		Pawn_DrawTracker drawer = pawn.Drawer;
		if (drawer != null)
		{
			PawnRenderer renderer = drawer.renderer;
			if (renderer != null)
			{
				renderer.SetAllGraphicsDirty();
			}
		}
	}

	private static void ForceGiveClothes(Pawn pawn, AccumulatedApparelEdits edits)
	{
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		if (pawn.apparel == null)
		{
			return;
		}
		foreach (SpecRequirementEdit item in GetWhatToGive(pawn, edits))
		{
			if (item.Thing == null)
			{
				continue;
			}
			Apparel val;
			try
			{
				val = GenerateNewApparel(pawn, item);
				if (val == null)
				{
					continue;
				}
			}
			catch (Exception e)
			{
				ModCore.Error($"Exception generating required apparel '{((Def)item.Thing).LabelCap}'", e);
				continue;
			}
			pawn.apparel.Wear(val, false, false);
		}
	}

	private static void Accumulate(AccumulatedApparelEdits edits, PawnKindEdit edit)
	{
		//IL_02eb: Unknown result type (might be due to invalid IL or missing references)
		if (edit.CustomHair != null)
		{
			GenCollection.AddRange<HairDef>(edits.hairs, from r in edit.CustomHair
				select r.Def into d
				where d != null
				select d);
		}
		if (edit.CustomBeards != null)
		{
			GenCollection.AddRange<BeardDef>(edits.beards, from r in edit.CustomBeards
				select r.Def into d
				where d != null
				select d);
		}
		if (edit.CustomFaceTattoos != null)
		{
			GenCollection.AddRange<TattooDef>(edits.faceTattoos, from r in edit.CustomFaceTattoos
				select r.Def into d
				where d != null
				select d);
		}
		if (edit.CustomBodyTattoos != null)
		{
			GenCollection.AddRange<TattooDef>(edits.bodyTattoos, from r in edit.CustomBodyTattoos
				select r.Def into d
				where d != null
				select d);
		}
		if (edit.CustomHairColors != null)
		{
			edits.hairColors.AddRange(edit.CustomHairColors);
		}
		if (edit.ForceNaked)
		{
			edits.anyForceNaked = true;
			return;
		}
		if (edit.ForceOnlySelected)
		{
			edits.anyForceOnlySelected = true;
		}
		GenCollection.AddRange<ThingDef>(edits.apparelRequired, from r in edit.ApparelRequired ?? new List<DefRef<ThingDef>>()
			select r.Def into d
			where d != null
			select d);
		GenCollection.AddRange<string>(edits.apparelTagsAllowed, edit.ApparelTags ?? new List<string>());
		if (edit.SpecificApparel == null)
		{
			return;
		}
		foreach (SpecRequirementEdit item in edit.SpecificApparel)
		{
			switch (item.SelectionMode)
			{
			case ApparelSelectionMode.AlwaysTake:
				edits.always.Add(item);
				break;
			case ApparelSelectionMode.RandomChance:
				edits.chance.Add(item);
				break;
			case ApparelSelectionMode.FromPool1:
				edits.pool1.Add(item);
				break;
			case ApparelSelectionMode.FromPool2:
				edits.pool2.Add(item);
				break;
			case ApparelSelectionMode.FromPool3:
				edits.pool3.Add(item);
				break;
			case ApparelSelectionMode.FromPool4:
				edits.pool4.Add(item);
				break;
			default:
				Log.Warning($"Unknown selection mode '{item.SelectionMode} for '{((Def)item.Thing).LabelCap}'");
				break;
			}
		}
	}

	private static IEnumerable<SpecRequirementEdit> GetWhatToGive(Pawn pawn, AccumulatedApparelEdits edits)
	{
		foreach (SpecRequirementEdit alway in edits.always)
		{
			yield return alway;
		}
		foreach (SpecRequirementEdit item in edits.chance)
		{
			if (Rand.Chance(item.SelectionChance))
			{
				yield return item;
			}
		}
		SpecRequirementEdit specRequirementEdit = GenCollection.RandomElementByWeightWithFallback<SpecRequirementEdit>(edits.pool1.Where(delegate(SpecRequirementEdit a)
		{
			ThingDef thing = a.Thing;
			bool? obj;
			if (thing == null)
			{
				obj = null;
			}
			else
			{
				ApparelProperties apparel = thing.apparel;
				obj = ((apparel != null) ? new bool?(apparel.PawnCanWear(pawn, false)) : ((bool?)null));
			}
			return obj ?? true;
		}), (Func<SpecRequirementEdit, float>)((SpecRequirementEdit i) => i.SelectionChance), (SpecRequirementEdit)null);
		if (specRequirementEdit != null)
		{
			yield return specRequirementEdit;
		}
		specRequirementEdit = GenCollection.RandomElementByWeightWithFallback<SpecRequirementEdit>(edits.pool2.Where(delegate(SpecRequirementEdit a)
		{
			ThingDef thing2 = a.Thing;
			bool? obj2;
			if (thing2 == null)
			{
				obj2 = null;
			}
			else
			{
				ApparelProperties apparel2 = thing2.apparel;
				obj2 = ((apparel2 != null) ? new bool?(apparel2.PawnCanWear(pawn, false)) : ((bool?)null));
			}
			return obj2 ?? true;
		}), (Func<SpecRequirementEdit, float>)((SpecRequirementEdit i) => i.SelectionChance), (SpecRequirementEdit)null);
		if (specRequirementEdit != null)
		{
			yield return specRequirementEdit;
		}
		specRequirementEdit = GenCollection.RandomElementByWeightWithFallback<SpecRequirementEdit>(edits.pool3.Where(delegate(SpecRequirementEdit a)
		{
			ThingDef thing3 = a.Thing;
			bool? obj3;
			if (thing3 == null)
			{
				obj3 = null;
			}
			else
			{
				ApparelProperties apparel3 = thing3.apparel;
				obj3 = ((apparel3 != null) ? new bool?(apparel3.PawnCanWear(pawn, false)) : ((bool?)null));
			}
			return obj3 ?? true;
		}), (Func<SpecRequirementEdit, float>)((SpecRequirementEdit i) => i.SelectionChance), (SpecRequirementEdit)null);
		if (specRequirementEdit != null)
		{
			yield return specRequirementEdit;
		}
		specRequirementEdit = GenCollection.RandomElementByWeightWithFallback<SpecRequirementEdit>(edits.pool4.Where(delegate(SpecRequirementEdit a)
		{
			ThingDef thing4 = a.Thing;
			bool? obj4;
			if (thing4 == null)
			{
				obj4 = null;
			}
			else
			{
				ApparelProperties apparel4 = thing4.apparel;
				obj4 = ((apparel4 != null) ? new bool?(apparel4.PawnCanWear(pawn, false)) : ((bool?)null));
			}
			return obj4 ?? true;
		}), (Func<SpecRequirementEdit, float>)((SpecRequirementEdit i) => i.SelectionChance), (SpecRequirementEdit)null);
		if (specRequirementEdit != null)
		{
			yield return specRequirementEdit;
		}
	}

	private static Apparel GenerateNewApparel(Pawn pawn, SpecRequirementEdit spec)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0175: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_0106: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Expected I4, but got Unknown
		//IL_0115: Expected I4, but got Unknown
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		Thing val = ThingMaker.MakeThing(spec.Thing, spec.Material);
		if (val == null)
		{
			object arg = ((Def)spec.Thing).LabelCap;
			ThingDef material = spec.Material;
			ModCore.Error(string.Format("Failed to generate a '{0}' made out of '{1}'.", arg, (material != null) ? ((Def)material).LabelCap : TaggedString.op_Implicit("<nothing>")));
			return null;
		}
		Apparel val2 = (Apparel)(object)((val is Apparel) ? val : null);
		if (val2 == null)
		{
			ModCore.Error("Generated a " + ((Entity)val).LabelCap + " but it is not apparel?!?");
			val.Destroy((DestroyMode)0);
			return null;
		}
		if (spec.Style != null)
		{
			ThingStyleHelper.SetStyleDef(val, spec.Style);
		}
		CompQuality val3 = ThingCompUtility.TryGetComp<CompQuality>(val);
		if (val3 != null)
		{
			if (spec.Quality.HasValue)
			{
				val3.SetQuality(spec.Quality.Value, (ArtGenerationContext?)(ArtGenerationContext)0);
			}
			else
			{
				QualityCategory val4 = QualityUtility.GenerateQualityGeneratingPawn(pawn.kindDef, val.def);
				if (pawn.royalty != null && ((Thing)pawn).Faction != null)
				{
					RoyalTitleDef currentTitle = pawn.royalty.GetCurrentTitle(((Thing)pawn).Faction);
					if (currentTitle != null)
					{
						val4 = (QualityCategory)(byte)Mathf.Clamp((int)val4, (int)currentTitle.requiredMinimumApparelQuality, 6);
					}
				}
				val3.SetQuality(val4, (ArtGenerationContext?)(ArtGenerationContext)0);
			}
		}
		if (val.def.useHitPoints)
		{
			float randomInRange = ((FloatRange)(ref pawn.kindDef.gearHealthRange)).RandomInRange;
			if (randomInRange < 1f)
			{
				int hitPoints = Mathf.Max(1, Mathf.RoundToInt(randomInRange * (float)val.MaxHitPoints));
				val.HitPoints = hitPoints;
			}
		}
		if (spec.Color != default(Color))
		{
			CompColorableUtility.SetColor(val, spec.Color, false);
		}
		CompBiocodable val5 = ThingCompUtility.TryGetComp<CompBiocodable>(val);
		if (val5 == null || !val5.Biocodable)
		{
			return val2;
		}
		if (val5.Biocoded)
		{
			val5.UnCode();
		}
		if (spec.Biocode)
		{
			val5.CodeFor(pawn);
		}
		return val2;
	}

	private static HairDef GetForcedHair(AccumulatedApparelEdits edits)
	{
		if (edits.hairs.Count <= 0)
		{
			return null;
		}
		return GenCollection.RandomElement<HairDef>(edits.hairs);
	}

	private static BeardDef GetForcedBeard(AccumulatedApparelEdits edits)
	{
		if (edits.beards.Count <= 0)
		{
			return null;
		}
		return GenCollection.RandomElement<BeardDef>(edits.beards);
	}

	private static TattooDef GetForcedTattoo(HashSet<TattooDef> tattoos)
	{
		if (tattoos.Count <= 0)
		{
			return null;
		}
		return GenCollection.RandomElement<TattooDef>(tattoos);
	}

	private static Color? GetForcedHairColor(AccumulatedApparelEdits edits)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		if (edits.hairColors.Count == 0)
		{
			return null;
		}
		Color value = GenCollection.RandomElement<Color>((IEnumerable<Color>)edits.hairColors);
		value.a = 1f;
		return value;
	}

	private static void HandleApparelPriceLimit(Pawn pawn)
	{
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_013a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		if ((!MySettings.VerboseLogging && !MySettings.IgnorePriceLimits) || pawn.apparel == null || !pawn.RaceProps.ToolUser || !pawn.RaceProps.IsFlesh || !BodyHasTorso(pawn) || CoversTorso(pawn))
		{
			return;
		}
		ThingStuffPair? val = CheapestEligibleTorsoApparel(pawn);
		if (!val.HasValue)
		{
			return;
		}
		ThingStuffPair value = val.Value;
		float num = pawn.apparel.WornApparel.Sum((Apparel a) => StatExtension.GetStatValueAbstract((BuildableDef)(object)((Thing)a).def, StatDefOf.MarketValue, ((Thing)a).Stuff));
		float num2 = Mathf.Max(0f, pawn.kindDef.apparelMoney.max - num);
		if (!(((ThingStuffPair)(ref value)).Price <= num2))
		{
			if (MySettings.VerboseLogging)
			{
				string arg = ((value.stuff != null) ? $" ({((Def)value.stuff).LabelCap})" : "");
				string arg2 = ((num > 0f) ? $" (${num:F0} already spent on other apparel)" : "");
				ModCore.Warn($"Apparel slot left empty by price for '{((Def)pawn.kindDef).LabelCap}': no torso apparel affordable within apparelMoney {pawn.kindDef.apparelMoney}{arg2}. " + $"Cheapest matching option is {((Def)value.thing).LabelCap}{arg} at ${((ThingStuffPair)(ref value)).Price:F0} - raise apparelMoney or relax the apparel/material filters.");
			}
			if (MySettings.IgnorePriceLimits)
			{
				WearFallbackApparel(pawn, value);
			}
		}
	}

	private static bool BodyHasTorso(Pawn pawn)
	{
		RaceProperties raceProps = pawn.RaceProps;
		object obj;
		if (raceProps == null)
		{
			obj = null;
		}
		else
		{
			BodyDef body = raceProps.body;
			obj = ((body != null) ? body.AllParts : null);
		}
		if (obj == null)
		{
			obj = new List<BodyPartRecord>();
		}
		return ((IEnumerable<BodyPartRecord>)obj).Any((BodyPartRecord t) => t.IsInGroup(BodyPartGroupDefOf.Torso));
	}

	private static bool CoversTorso(Pawn pawn)
	{
		Pawn_ApparelTracker apparel = pawn.apparel;
		return ((apparel == null) ? ((bool?)null) : apparel.WornApparel?.Select((Apparel t) => ((Thing)t).def.apparel?.bodyPartGroups).Any((List<BodyPartGroupDef> groups) => groups?.Contains(BodyPartGroupDefOf.Torso) ?? false)) == true;
	}

	private static ThingStuffPair? CheapestEligibleTorsoApparel(Pawn pawn)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		ThingStuffPair? result = null;
		foreach (ThingStuffPair allApparelPair in PawnApparelGenerator.allApparelPairs)
		{
			ThingStuffPair current = allApparelPair;
			List<BodyPartGroupDef> list = current.thing.apparel?.bodyPartGroups;
			if (list == null || !list.Contains(BodyPartGroupDefOf.Torso) || !PawnApparelGenerator.CanUsePair(current, pawn, float.MaxValue, true, ((Thing)pawn).thingIDNumber))
			{
				continue;
			}
			if (result.HasValue)
			{
				float price = ((ThingStuffPair)(ref current)).Price;
				ThingStuffPair value = result.Value;
				if (!(price < ((ThingStuffPair)(ref value)).Price))
				{
					continue;
				}
			}
			result = current;
		}
		return result;
	}

	private static void WearFallbackApparel(Pawn pawn, ThingStuffPair pair)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			Thing obj = ThingMaker.MakeThing(pair.thing, pair.stuff);
			Apparel val = (Apparel)(object)((obj is Apparel) ? obj : null);
			if (val != null)
			{
				PawnApparelGenerator.PostProcessApparel(val, pawn);
				pawn.apparel.Wear(val, false, false);
				ModCore.Debug($"Ignore-price fallback dressed '{((Def)pawn.kindDef).LabelCap}' in {((Entity)val).LabelCap}.");
			}
		}
		catch (Exception e)
		{
			ModCore.Error($"Ignore-price apparel fallback failed for '{((Def)pawn.kindDef).LabelCap}'", e);
		}
	}
}
