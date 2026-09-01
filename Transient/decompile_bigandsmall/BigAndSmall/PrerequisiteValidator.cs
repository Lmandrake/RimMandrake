using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class PrerequisiteValidator
{
	public static string GeneDefLabelDefName(string defName)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		GeneDef namedSilentFail = DefDatabase<GeneDef>.GetNamedSilentFail(defName);
		if (namedSilentFail != null)
		{
			return TaggedString.op_Implicit(((Def)namedSilentFail).LabelCap);
		}
		return defName;
	}

	public static string Validate(GeneDef gene, Pawn pawn)
	{
		try
		{
			if (((Def)gene).HasModExtension<GenePrerequisites>())
			{
				GenePrerequisites modExtension = ((Def)gene).GetModExtension<GenePrerequisites>();
				if (modExtension.prerequisiteSets != null)
				{
					return ValidationDescription(pawn, modExtension.prerequisiteSets);
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error("Caught Exception in PrerequisiteValidator: " + ex.Message + "\n" + ex.StackTrace);
		}
		return "";
	}

	public static bool SetIsValid(Pawn pawn, List<PrerequisiteSet> prerequisiteSets)
	{
		return ValidationDescription(pawn, prerequisiteSets) == "";
	}

	public static string ValidationDescription(Pawn pawn, List<PrerequisiteSet> prerequisiteSets)
	{
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0273: Unknown result type (might be due to invalid IL or missing references)
		//IL_0278: Unknown result type (might be due to invalid IL or missing references)
		if (prerequisiteSets == null || prerequisiteSets.Count == 0)
		{
			return "";
		}
		try
		{
			List<Gene> otherGenes = pawn.genes.GenesListForReading.Where((Gene x) => x.overriddenByGene == null).ToList();
			foreach (PrerequisiteSet prerequisiteSet in prerequisiteSets)
			{
				if (prerequisiteSet.prerequisites == null)
				{
					continue;
				}
				bool flag = false;
				switch (prerequisiteSet.type)
				{
				case PrerequisiteSet.PrerequisiteType.AnyOf:
					flag = GenCollection.Any<string>(prerequisiteSet.prerequisites, (Predicate<string>)((string geneName) => GenCollection.Any<Gene>(otherGenes, (Predicate<Gene>)((Gene y) => ((Def)y.def).defName == geneName))));
					if (!flag)
					{
						return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_PrerequisitesNotMetAnyOf", NamedArgument.op_Implicit(string.Join(", ", prerequisiteSet.prerequisites.Select(GeneDefLabelDefName)) ?? "")));
					}
					break;
				case PrerequisiteSet.PrerequisiteType.AllOf:
					flag = (float)GenCollection.Count<string>(prerequisiteSet.prerequisites, (Predicate<string>)((string geneName) => GenCollection.Any<Gene>(otherGenes, (Predicate<Gene>)((Gene y) => ((Def)y.def).defName == geneName)))) / (float)prerequisiteSet.prerequisites.Count >= prerequisiteSet.allOfPerecntage;
					if (!flag)
					{
						return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_PrerequisitesNotMetAllOf", NamedArgument.op_Implicit(string.Join(", ", prerequisiteSet.prerequisites.Select(GeneDefLabelDefName)) ?? "")));
					}
					break;
				case PrerequisiteSet.PrerequisiteType.NoneOf:
				{
					flag = (float)GenCollection.Count<string>(prerequisiteSet.prerequisites, (Predicate<string>)((string geneName) => GenCollection.Any<Gene>(otherGenes, (Predicate<Gene>)((Gene y) => ((Def)y.def).defName == geneName)))) / (float)prerequisiteSet.prerequisites.Count <= prerequisiteSet.noneOfPercentage;
					if (flag)
					{
						break;
					}
					List<string> source = prerequisiteSet.prerequisites.Where((string geneName) => GenCollection.Any<Gene>(otherGenes, (Predicate<Gene>)((Gene y) => ((Def)y.def).defName == geneName))).ToList();
					return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_PrerequisitesNotMetNoneOf", NamedArgument.op_Implicit(string.Join(", ", source.Select(GeneDefLabelDefName)) ?? "")));
				}
				}
				if (!flag)
				{
					return "";
				}
			}
			return "";
		}
		catch (Exception ex)
		{
			Log.Error("Caught Exception in PrerequisiteValidator.ValidationDescription: " + ex.Message + "\n" + ex.StackTrace);
			return "ERROR";
		}
	}
}
