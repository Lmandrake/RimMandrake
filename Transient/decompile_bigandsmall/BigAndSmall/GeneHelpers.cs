using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class GeneHelpers
{
	public static FieldInfo xenoTypeField;

	private static FieldInfo cachedGenesField;

	public static void RefreshAllGenes(Pawn pawn, List<Gene> genesAdded, List<Gene> genesRemoved)
	{
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0268: Unknown result type (might be due to invalid IL or missing references)
		//IL_026d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0277: Expected O, but got Unknown
		if (pawn?.genes == null)
		{
			return;
		}
		BigSmall.performScaleCalculations = false;
		try
		{
			foreach (Gene item in genesRemoved)
			{
				if (!GenList.NullOrEmpty<AbilityDef>((IList<AbilityDef>)item.def.abilities))
				{
					foreach (AbilityDef ability in item.def.abilities)
					{
						pawn.abilities.RemoveAbility(ability);
					}
				}
				if (item.def.passionMod != null)
				{
					SkillRecord skill = pawn.skills.GetSkill(item.def.passionMod.skill);
					skill.passion = item.NewPassionForOnRemoval(skill);
				}
			}
			for (int num = pawn.story.traits.allTraits.Count - 1; num >= 0; num--)
			{
				Trait trait = pawn.story.traits.allTraits[num];
				if (trait.sourceGene != null && pawn.story.traits.HasTrait(trait.def) && GenCollection.Any<Gene>(genesRemoved, (Predicate<Gene>)((Gene x) => x.def == trait.sourceGene.def)))
				{
					pawn.story.traits.RemoveTrait(trait, false);
				}
			}
			pawn.genes.CheckForOverrides();
			foreach (Gene item2 in genesAdded.Where((Gene g) => g.Active))
			{
				if (!GenList.NullOrEmpty<AbilityDef>((IList<AbilityDef>)item2.def.abilities))
				{
					foreach (AbilityDef ability2 in item2.def.abilities)
					{
						pawn.abilities.GainAbility(ability2);
					}
				}
				if (!GenList.NullOrEmpty<GeneticTraitData>((IList<GeneticTraitData>)item2.def.forcedTraits) && pawn.story != null)
				{
					for (int i = 0; i < item2.def.forcedTraits.Count; i++)
					{
						Trait val = new Trait(item2.def.forcedTraits[i].def, item2.def.forcedTraits[i].degree, false)
						{
							sourceGene = item2
						};
						pawn.story.traits.GainTrait(val, true);
					}
				}
				if (item2.def.passionMod != null)
				{
					SkillRecord skill2 = pawn.skills.GetSkill(item2.def.passionMod.skill);
					item2.passionPreAdd = skill2.passion;
					skill2.passion = item2.def.passionMod.NewPassionFor(skill2);
				}
				Pawn_StoryTracker story = pawn.story;
				if (story != null)
				{
					TraitSet traits = story.traits;
					if (traits != null)
					{
						traits.RecalculateSuppression();
					}
				}
			}
			foreach (Gene item3 in genesAdded)
			{
				item3.PostAdd();
			}
			if (genesRemoved.Count > 0)
			{
				foreach (Gene item4 in genesAdded)
				{
					CustomGeneAddedOrRemovedEvent(item4, added: false);
				}
			}
			if (genesAdded.Count > 0)
			{
				foreach (Gene item5 in genesAdded.Where((Gene g) => g.def.skinIsHairColor || g.def.hairColorOverride.HasValue || g.def.skinColorBase.HasValue || g.def.skinColorOverride.HasValue || g.def.bodyType.HasValue || g.def.forcedHeadTypes != null || g.def.forcedHair != null || g.def.hairTagFilter != null || g.def.beardTagFilter != null || g.def.fur != null || g.def.RandomChosen || g.def.soundCall != null))
				{
					pawn.genes.Notify_GenesChanged(item5.def);
				}
				foreach (Gene item6 in genesAdded)
				{
					CustomGeneAddedOrRemovedEvent(item6, added: true);
				}
			}
			ClearCachedGenes(pawn);
			Gene val2 = pawn.genes.AddGene(BSDefs.Robust, true);
			pawn.genes.RemoveGene(val2);
		}
		finally
		{
			BigSmall.performScaleCalculations = true;
		}
		FastAcccess.GetCache(pawn, force: true);
	}

	public static void CustomGeneAddedOrRemovedEvent(Gene gene, bool added)
	{
		if (added)
		{
			NotifyGenesChanges.Gene_PostAddPatch(gene);
		}
		else
		{
			NotifyGenesChanges.Gene_PostRemovePatch(gene);
		}
	}

	public static List<Gene> GetActiveGeneByName(Pawn pawn, string geneName)
	{
		List<Gene> list = new List<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list2 = (List<Gene>)obj;
		if (list2 == null)
		{
			return list;
		}
		for (int i = 0; i < list2.Count; i++)
		{
			if (list2[i].Active && ((Def)list2[i].def).defName == geneName)
			{
				list.Add(list2[i]);
			}
		}
		return list;
	}

	public static List<Gene> GetGeneByName(Pawn pawn, string geneName)
	{
		List<Gene> list = new List<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list2 = (List<Gene>)obj;
		if (list2 == null)
		{
			return list;
		}
		for (int i = 0; i < list2.Count; i++)
		{
			if (((Def)list2[i].def).defName == geneName)
			{
				list.Add(list2[i]);
			}
		}
		return list;
	}

	public static HashSet<Gene> GetAllActiveGenes(this Pawn pawn)
	{
		HashSet<Gene> hashSet = new HashSet<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list = (List<Gene>)obj;
		if (list == null)
		{
			return hashSet;
		}
		int count = list.Count;
		for (int i = 0; i < count; i++)
		{
			if (list[i].Active)
			{
				hashSet.Add(list[i]);
			}
		}
		return hashSet;
	}

	public static HashSet<Gene> GetAllActiveRandomChosenGenes(Pawn pawn)
	{
		HashSet<Gene> hashSet = new HashSet<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list = (List<Gene>)obj;
		if (list == null)
		{
			return hashSet;
		}
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i].def.randomChosen && list[i].Active)
			{
				hashSet.Add(list[i]);
			}
		}
		return hashSet;
	}

	public static List<Gene> GetAllGenes(Pawn pawn)
	{
		List<Gene> result = new List<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list = (List<Gene>)obj;
		if (list == null)
		{
			return result;
		}
		return list;
	}

	public static HashSet<GeneDef> GetAllActiveGeneDefs(Pawn pawn)
	{
		HashSet<GeneDef> hashSet = new HashSet<GeneDef>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list = (List<Gene>)obj;
		if (list == null)
		{
			return hashSet;
		}
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i].Active)
			{
				hashSet.Add(list[i].def);
			}
		}
		return hashSet;
	}

	public static List<Gene> GetAllInactiveGenes(Pawn pawn)
	{
		List<Gene> list = new List<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list2 = (List<Gene>)obj;
		if (list2 == null)
		{
			return list;
		}
		for (int i = 0; i < list2.Count; i++)
		{
			if (!list2[i].Active)
			{
				list.Add(list2[i]);
			}
		}
		return list;
	}

	public static Hediff GetFirstHediffOfDefName(this HediffSet instance, string defName, bool mustBeVisible = false)
	{
		for (int i = 0; i < instance.hediffs.Count; i++)
		{
			if (((Def)instance.hediffs[i].def).defName == defName && (!mustBeVisible || instance.hediffs[i].Visible))
			{
				return instance.hediffs[i];
			}
		}
		return null;
	}

	public static List<XenotypeChance> GetXenotypeChances(this PawnKindDef pawnKind)
	{
		if (pawnKind == null)
		{
			Log.Warning("Trying to GetXenotypeChances, but PawnKindDef is null");
			return new List<XenotypeChance>();
		}
		if (pawnKind.xenotypeSet == null)
		{
			return new List<XenotypeChance>();
		}
		if (xenoTypeField == null)
		{
			xenoTypeField = AccessTools.Field(typeof(XenotypeSet), "xenotypeChances");
		}
		if (xenoTypeField == null)
		{
			Log.Warning("Could not find xenotypeChances field in XenotypeSet");
			return new List<XenotypeChance>();
		}
		return xenoTypeField.GetValue(pawnKind.xenotypeSet) as List<XenotypeChance>;
	}

	public static XenotypeDef GetRandomXenotype(this List<XenotypeChance> xenoTypeChances)
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Expected O, but got Unknown
		if (xenoTypeChances.Sum((XenotypeChance x) => x.chance) < 1f)
		{
			xenoTypeChances.Add(new XenotypeChance(XenotypeDefOf.Baseliner, 1f - xenoTypeChances.Sum((XenotypeChance x) => x.chance)));
		}
		return GenCollection.RandomElementByWeight<XenotypeChance>((IEnumerable<XenotypeChance>)xenoTypeChances, (Func<XenotypeChance, float>)((XenotypeChance x) => x.chance)).xenotype;
	}

	public static List<Gene> GetActiveGenesByNames(Pawn pawn, List<string> geneNames)
	{
		List<Gene> list = new List<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.GenesListForReading : null);
		}
		List<Gene> list2 = (List<Gene>)obj;
		if (list2 == null)
		{
			return list;
		}
		for (int i = 0; i < list2.Count; i++)
		{
			if (list2[i].Active && geneNames.Contains(((Def)list2[i].def).defName))
			{
				list.Add(list2[i]);
			}
		}
		return list;
	}

	public static List<Gene> GetAllActiveEndoGenes(Pawn pawn)
	{
		List<Gene> list = new List<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.Endogenes : null);
		}
		List<Gene> list2 = (List<Gene>)obj;
		if (list2 == null)
		{
			return list;
		}
		for (int i = 0; i < list2.Count; i++)
		{
			if (list2[i].Active)
			{
				list.Add(list2[i]);
			}
		}
		return list;
	}

	public static List<Gene> GetAllActiveXenoGenes(Pawn pawn)
	{
		List<Gene> list = new List<Gene>();
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes = pawn.genes;
			obj = ((genes != null) ? genes.Xenogenes : null);
		}
		List<Gene> list2 = (List<Gene>)obj;
		if (list2 == null)
		{
			return list;
		}
		for (int i = 0; i < list2.Count; i++)
		{
			if (list2[i].Active)
			{
				list.Add(list2[i]);
			}
		}
		return list;
	}

	public static Hediff GetHediffOnPawnByName(string name, Pawn pawn)
	{
		HediffDef namedSilentFail = DefDatabase<HediffDef>.GetNamedSilentFail(name);
		if (namedSilentFail == null)
		{
			Log.Error("Could not find hediff with name " + name);
			return null;
		}
		if (pawn.health.hediffSet.HasHediff(namedSilentFail, false))
		{
			return pawn.health.hediffSet.GetFirstHediffOfDef(namedSilentFail, false);
		}
		return null;
	}

	public static bool HasActiveGene(this Pawn pawn, GeneDef geneDef)
	{
		if (pawn.genes == null)
		{
			return false;
		}
		Gene gene = pawn.genes.GetGene(geneDef);
		if (gene == null)
		{
			return false;
		}
		return gene.Active;
	}

	public static bool HasGene(this Pawn pawn, GeneDef geneDef)
	{
		if (pawn.genes == null)
		{
			return false;
		}
		return pawn.genes.GetGene(geneDef) != null;
	}

	public static void RemoveRandomToMetabolism(int initialMet, List<GeneDef> newGenes, int minMet = -6, List<GeneDef> exclusionList = null)
	{
		if (exclusionList == null)
		{
			exclusionList = new List<GeneDef>();
		}
		for (int i = 0; newGenes.Sum((GeneDef x) => x.biostatMet) + initialMet < minMet || newGenes.Count <= 1 || i > 200; i++)
		{
			if (newGenes.Count == 1)
			{
				break;
			}
			GeneDef val = GenCollection.RandomElement<GeneDef>(newGenes.Where((GeneDef x) => x.biostatMet <= 1 && !exclusionList.Contains(x)));
			if (val != null)
			{
				newGenes.Remove(val);
				continue;
			}
			break;
		}
	}

	public static void RemoveRandomToMetabolism(int initialMet, Pawn_GeneTracker genes, int minMet = -6, List<GeneDef> exclusionList = null)
	{
		if (exclusionList != null)
		{
			exclusionList = new List<GeneDef>();
		}
		for (int i = 0; genes.GenesListForReading.Where((Gene x) => !x.Overridden).Sum((Gene x) => x.def.biostatMet) + initialMet < minMet || genes.GenesListForReading.Count <= 1 || i > 200; i++)
		{
			if (genes.GenesListForReading.Count == 1)
			{
				break;
			}
			Gene val = GenCollection.RandomElement<Gene>(genes.GenesListForReading.Where((Gene x) => x.def.biostatMet < 0 && !exclusionList.Contains(x.def)));
			if (val != null)
			{
				genes.RemoveGene(val);
				continue;
			}
			break;
		}
	}

	public static void RemoveAllGenesSlow(Pawn pawn)
	{
		if (pawn?.genes != null)
		{
			List<Gene> list = pawn.genes.GenesListForReading.ToList();
			for (int num = list.Count - 1; num >= 0; num--)
			{
				Gene val = list[num];
				pawn.genes.RemoveGene(val);
			}
		}
	}

	public static void RemoveAllGenesSlow_ExceptColor(Pawn pawn)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Invalid comparison between Unknown and I4
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Invalid comparison between Unknown and I4
		if (pawn?.genes == null)
		{
			return;
		}
		List<Gene> list = pawn.genes.GenesListForReading.ToList();
		for (int num = list.Count - 1; num >= 0; num--)
		{
			Gene val = list[num];
			if ((int)val.def.endogeneCategory != 1 && (int)val.def.endogeneCategory != 2)
			{
				pawn.genes.RemoveGene(val);
			}
		}
	}

	public static void AddAllXenotypeGenes(Pawn pawn, XenotypeDef def, string name = null, bool xenogene = false)
	{
		pawn.genes.SetXenotypeDirect(def);
		foreach (GeneDef xenotypeGene in def.genes)
		{
			if (!GenCollection.Any<Gene>(pawn.genes.GenesListForReading, (Predicate<Gene>)((Gene x) => ((Def)x.def).defName == ((Def)xenotypeGene).defName)))
			{
				pawn.genes.AddGene(xenotypeGene, xenogene);
			}
		}
		if (name != null)
		{
			pawn.genes.xenotypeName = name;
		}
	}

	public static void ClearCachedGenes(Pawn pawn)
	{
		Pawn_GeneTracker val = pawn?.genes;
		if (val != null)
		{
			if (cachedGenesField == null)
			{
				cachedGenesField = AccessTools.Field(typeof(Pawn_GeneTracker), "cachedGenes");
			}
			cachedGenesField.SetValue(val, null);
		}
	}

	public static List<Gene> GetActiveGenesByName(Pawn pawn, string geneName)
	{
		return GetActiveGenesByNames(pawn, new List<string>(1) { geneName });
	}

	public static void ChangeXenotypeFast(Pawn pawn, XenotypeDef targetXenottype)
	{
		List<Gene> allGenesBefore = pawn.genes.GenesListForReading.ToList();
		(from x in pawn.GetAllActiveGenes()
			select x.def).ToHashSet();
		bool inheritable = targetXenottype.inheritable;
		pawn.genes.Xenotype.AllGenes.ToList();
		List<Gene> collection = pawn.genes.Xenogenes.Select((Gene x) => x).ToList();
		if (inheritable)
		{
			pawn.genes.Endogenes.Clear();
		}
		pawn.genes.Xenogenes.Clear();
		foreach (GeneDef gene in targetXenottype.genes)
		{
			if (inheritable)
			{
				pawn.genes.Endogenes.Add(GeneMaker.MakeGene(gene, pawn));
			}
			else
			{
				pawn.genes.Xenogenes.Add(GeneMaker.MakeGene(gene, pawn));
			}
		}
		if (inheritable)
		{
			pawn.genes.Xenogenes.AddRange(collection);
		}
		foreach (Gene item in (from x in pawn.genes.GenesListForReading.ToList()
			where ((Def)x.def).modExtensions != null && GenCollection.Any<DefModExtension>(((Def)x.def).modExtensions, (Predicate<DefModExtension>)((DefModExtension y) => y is PawnExtension && GenCollection.Any<MorphTarget>((y as PawnExtension).morphTargets, (Predicate<MorphTarget>)((MorphTarget x) => x.xenotype == pawn.genes.Xenotype))))
			select x).ToList())
		{
			pawn.genes.RemoveGene(item);
		}
		ClearCachedGenes(pawn);
		pawn.genes.CheckForOverrides();
		List<Gene> allGenesNow = pawn.genes.GenesListForReading.ToList();
		List<Gene> genesAdded = allGenesNow.Where((Gene n) => !GenCollection.Any<Gene>(allGenesBefore, (Predicate<Gene>)((Gene b) => b.def == n.def))).ToList();
		List<Gene> genesRemoved = allGenesBefore.Where((Gene b) => !GenCollection.Any<Gene>(allGenesNow, (Predicate<Gene>)((Gene n) => n.def == b.def))).ToList();
		RefreshAllGenes(pawn, genesAdded, genesRemoved);
		pawn.genes.SetXenotypeDirect(targetXenottype);
	}
}
