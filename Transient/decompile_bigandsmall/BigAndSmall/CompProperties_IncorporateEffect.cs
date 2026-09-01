using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_IncorporateEffect : CompAbilityEffect
{
	public CompProperties_Incorporate Props => ((AbilityComp)this).props as CompProperties_Incorporate;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		Pawn pawn = ((AbilityComp)this).parent.pawn;
		Thing thing = ((LocalTargetInfo)(ref target)).Thing;
		if (thing != null)
		{
			IncorporateGenes(pawn, thing, Props?.pickCount ?? 2, Props?.stealTraits ?? true);
		}
	}

	public static void IncorporateGenes(Pawn pawn, object target, int genePickCount = 4, bool stealTraits = true, bool userPicks = true, int randomPickCount = 4, bool excludeBodySwap = false)
	{
		Pawn val = (Pawn)((target is Pawn) ? target : null);
		if (val == null)
		{
			object obj = ((target is Corpse) ? target : null);
			val = ((obj != null) ? ((Corpse)obj).InnerPawn : null);
		}
		if (val == null)
		{
			Log.Warning($"Target {target} is not a pawn");
			return;
		}
		object obj2;
		if (val == null)
		{
			obj2 = null;
		}
		else
		{
			Pawn_GeneTracker genes = val.genes;
			obj2 = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list = (List<Gene>)obj2;
		List<GeneDef> list2 = list?.Select((Gene x) => x.def).ToList() ?? new List<GeneDef>();
		list2.AddRange(from x in GenesFromSpecial.GetGenesFromAnomalyCreature(val)
			where x != null
			select x);
		if (list == null && list2.Count == 0)
		{
			Log.Warning($"Target {val} has no valid genes");
			return;
		}
		List<GeneDef> list3 = new List<GeneDef>();
		if (stealTraits && val != null)
		{
			RaceProperties raceProps = val.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) == true)
			{
				GetGenesFromTraits(val, list3);
			}
		}
		genePickCount += list3.Count();
		bool flag = list != null && list.Sum((Gene x) => x.def.biostatCpx) == 0 && list.Count < 6;
		Pawn_GeneTracker val2 = val?.genes;
		if (val2 != null && val2.xenotype != XenotypeDefOf.Baseliner && !val2.hybrid)
		{
			flag = false;
		}
		if (flag)
		{
			List<string> humanGeneList = new List<string> { "Hands_Human", "Headbone_Human", "Ears_Human", "Nose_Human", "Jaw_Baseline", "Voice_Human" };
			List<GeneDef> collection = DefDatabase<GeneDef>.AllDefsListForReading.Where((GeneDef x) => ((Def)x).defName.StartsWith("GET_") || humanGeneList.Contains(((Def)x).defName)).ToList();
			list2.AddRange(collection);
		}
		if (excludeBodySwap && GenCollection.Any<Gene>(pawn.genes.GenesListForReading, (Predicate<Gene>)((Gene x) => x.def.exclusionTags?.Contains("ThingDefSwap") ?? false)))
		{
			list2 = list2.Where(delegate(GeneDef x)
			{
				List<string> exclusionTags = x.exclusionTags;
				return exclusionTags != null && !exclusionTags.Contains("ThingDefSwap");
			}).ToList();
		}
		while (list2.Count > 0 && list3.Count < genePickCount)
		{
			GeneDef gene = GenCollection.RandomElement<GeneDef>((IEnumerable<GeneDef>)list2);
			list2.Remove(gene);
			if (!GenCollection.Any<Gene>(pawn.genes.GenesListForReading, (Predicate<Gene>)((Gene x) => ((Def)x.def).defName == ((Def)gene).defName)) && !list3.Contains(gene) && !GenCollection.Any<Gene>(pawn.genes.GenesListForReading, (Predicate<Gene>)((Gene x) => ((Def)x.def).defName == ((Def)gene).defName)))
			{
				list3.Add(gene);
			}
		}
		List<GeneDef> allDefsListForReading = DefDatabase<GeneDef>.AllDefsListForReading;
		try
		{
			ReplaceGeneInList(list3, allDefsListForReading, "BS_GeneStabilizing_Extreme", "BS_Instability_Catastrophic");
			ReplaceGeneInList(list3, allDefsListForReading, "BS_GeneStabilizing_Great", "Instability_Major");
			ReplaceGeneInList(list3, allDefsListForReading, "BS_GeneStabilizing_Moderate", "Instability_Mild");
		}
		catch
		{
		}
		list3.RemoveAll((GeneDef x) => pawn.genes.Xenogenes.Select((Gene g) => g.def).Contains(x));
		if (!GenCollection.Any<GeneDef>(list3))
		{
			return;
		}
		if (userPicks)
		{
			list3.Reverse();
			Find.WindowStack.Add((Window)(object)new Dialog_PickGenes(pawn, list3));
			return;
		}
		List<GeneDef> list4 = new List<GeneDef>();
		while (randomPickCount > 0 && list3.Count > 0)
		{
			GeneDef item = GenCollection.RandomElement<GeneDef>((IEnumerable<GeneDef>)list3);
			list3.Remove(item);
			list4.Add(item);
			randomPickCount--;
		}
		foreach (GeneDef item2 in list4)
		{
			pawn.genes.AddGene(item2, true);
		}
	}

	private static void ReplaceGeneInList(List<GeneDef> genesToPick, List<GeneDef> allGeneDefs, string stabilityExtreme, string instabilityExtreme)
	{
		foreach (GeneDef item in genesToPick)
		{
			if (((Def)item).defName.StartsWith(stabilityExtreme))
			{
				GeneDef val = allGeneDefs.Where((GeneDef x) => ((Def)x).defName == instabilityExtreme).FirstOrDefault();
				if (val != null)
				{
					genesToPick.Remove(item);
					genesToPick.Add(val);
				}
			}
		}
	}

	public static void GetGenesFromTraits(Pawn target, List<GeneDef> genesToPick, bool onlyZeroCostGenes = false)
	{
		//IL_0295: Unknown result type (might be due to invalid IL or missing references)
		//IL_029b: Invalid comparison between Unknown and I4
		//IL_02d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d9: Invalid comparison between Unknown and I4
		if (target == null)
		{
			return;
		}
		List<GeneDef> allDefsListForReading = DefDatabase<GeneDef>.AllDefsListForReading;
		List<Trait> list = target?.story?.traits?.allTraits;
		if (list != null && !onlyZeroCostGenes)
		{
			IEnumerable<Trait> source = list.Where((Trait x) => ((Def)x.def).defName.StartsWith("Beauty"));
			if (source.Count() > 0)
			{
				Trait obj = source.First();
				if (obj.Degree == 2)
				{
					genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Beauty_Beautiful").First());
				}
				if (obj.Degree == 1)
				{
					genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Beauty_Pretty").First());
				}
				if (obj.Degree == -1)
				{
					genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Beauty_Ugly").First());
				}
				if (obj.Degree == -2)
				{
					genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Beauty_VeryUgly").First());
				}
			}
			if (GenCollection.Any<Trait>(list, (Predicate<Trait>)((Trait x) => ((Def)x.def).defName.StartsWith("Tough"))))
			{
				genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Robust").First());
			}
			IEnumerable<Trait> source2 = list.Where((Trait x) => ((Def)x.def).defName.StartsWith("SpeedOffset"));
			if (source2.Count() > 0)
			{
				Trait obj2 = source2.First();
				if (obj2.Degree == 2)
				{
					genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "MoveSpeed_VeryQuick").First());
				}
				if (obj2.Degree == 1)
				{
					genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "MoveSpeed_Quick").First());
				}
				if (obj2.Degree == -1)
				{
					genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "MoveSpeed_Slow").First());
				}
			}
		}
		try
		{
			if (target != null && (int)target.gender == 1)
			{
				genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Body_MaleOnly").First());
			}
			else if (target != null && (int)target.gender == 2)
			{
				genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Body_FemaleOnly").First());
			}
		}
		catch (Exception ex)
		{
			Log.Warning("Gender genes not found. Skipping.\n" + ex.Message + "\n" + ex.StackTrace);
		}
		if (target?.story.bodyType == BodyTypeDefOf.Male)
		{
			genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Body_Standard").First());
		}
		else if (target?.story.bodyType == BodyTypeDefOf.Female)
		{
			genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Body_Standard").First());
		}
		else if (target?.story.bodyType == BodyTypeDefOf.Hulk)
		{
			genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Body_Hulk").First());
		}
		else if (target?.story.bodyType == BodyTypeDefOf.Fat)
		{
			genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Body_Fat").First());
		}
		else if (target?.story.bodyType == BodyTypeDefOf.Thin)
		{
			genesToPick.Add(allDefsListForReading.Where((GeneDef x) => ((Def)x).defName == "Body_Thin").First());
		}
	}

	public override void PostApplied(List<LocalTargetInfo> targets, Map map)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).PostApplied(targets, map);
		foreach (LocalTargetInfo target in targets)
		{
			LocalTargetInfo current = target;
			Thing thing = ((LocalTargetInfo)(ref current)).Thing;
			if (thing != null)
			{
				thing.Destroy((DestroyMode)0);
			}
		}
		RemoveGenesOverLimit(((AbilityComp)this).parent.pawn, -9);
	}

	public static bool RemoveGenesOverLimit(Pawn pawn, int limit)
	{
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		limit -= BS.Settings.MetabolismLimit;
		List<Gene> xenogenes = pawn.genes.Xenogenes;
		bool flag = false;
		int i;
		for (i = 0; pawn.genes.GenesListForReading.Where((Gene x) => !x.Overridden).Sum((Gene x) => x.def.biostatMet) < limit || i > 100; i++)
		{
			if (xenogenes.Count == 0)
			{
				break;
			}
			Gene val = GenCollection.RandomElement<Gene>(xenogenes.Where((Gene x) => x.def.biostatMet <= 1));
			if (val == null)
			{
				break;
			}
			xenogenes.Remove(val);
			flag = true;
		}
		if (flag)
		{
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_GenesRemovedByOverLimit", NamedArgument.op_Implicit(pawn.Name.ToStringShort), NamedArgument.op_Implicit(i), NamedArgument.op_Implicit(limit))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.NegativeHealthEvent, true);
		}
		return flag;
	}
}
