using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class PregnancyPatches
{
	public static bool disableBirthPatch = false;

	public static List<GeneDef> newBabyGenes = null;

	public static int? babyStartAge = null;

	public static List<Pawn> parents = new List<Pawn>();

	public static void ApplyPatches()
	{
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Expected O, but got Unknown
		BSCore.harmony.Patch((MethodBase)AccessTools.Method(typeof(PregnancyUtility), "ApplyBirthOutcome", new Type[11]
		{
			typeof(RitualOutcomePossibility),
			typeof(float),
			typeof(Precept_Ritual),
			typeof(List<GeneDef>),
			typeof(Pawn),
			typeof(Thing),
			typeof(Pawn),
			typeof(Pawn),
			typeof(LordJob_Ritual),
			typeof(RitualRoleAssignments),
			typeof(bool)
		}, (Type[])null), new HarmonyMethod(typeof(PregnancyPatches), "ApplyBirthOutcome_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
	}

	public static bool ApplyBirthOutcome_Prefix(RitualOutcomePossibility outcome, float quality, Precept_Ritual ritual, List<GeneDef> genes, Pawn geneticMother, Thing birtherThing, Pawn father, Pawn doctor, LordJob_Ritual lordJobRitual, RitualRoleAssignments assignments, bool preventLetter)
	{
		if (disableBirthPatch || geneticMother?.genes == null)
		{
			return true;
		}
		geneticMother.GetAllActiveGenes();
		List<PawnExtension> list = geneticMother.GetAllPawnExtensions().ToList();
		if (list == null || list.Count == 0)
		{
			return true;
		}
		List<int> list2 = GenCollection.FirstOrDefault<PawnExtension>(list, (Predicate<PawnExtension>)((PawnExtension x) => x.babyBirthCount != null))?.babyBirthCount;
		int num = 1;
		if (list2 != null)
		{
			num = GenCollection.RandomElement<int>((IEnumerable<int>)list2);
			num = Mathf.Max(num, 1);
		}
		disableBirthPatch = true;
		float num2 = list.Sum((PawnExtension x) => x.pregnancyQuality);
		float num3 = Mathf.Pow(quality, 1f / (float)num);
		num3 = Mathf.Min(num2 + num3, 1f);
		num3 = Mathf.Max(quality, num3);
		if (num3 >= 0.5f && outcome != null && outcome.positivityIndex < 0)
		{
			outcome.positivityIndex = 0;
		}
		bool flag = false;
		try
		{
			babyStartAge = GenCollection.FirstOrDefault<PawnExtension>(list, (Predicate<PawnExtension>)((PawnExtension x) => x.babyStartAge.HasValue))?.babyStartAge ?? ((int?)null);
			parents = new List<Pawn> { geneticMother, father }.Where((Pawn x) => x != null).ToList();
			try
			{
				for (int i = 0; i < num; i++)
				{
					if (BSInheritanceWrapper.ModActive == true && i > 0)
					{
						newBabyGenes = BSInheritanceWrapper.GetChildGenes(geneticMother, father);
					}
					PregnancyUtility.ApplyBirthOutcome(outcome, num3, ritual, genes, geneticMother, birtherThing, father, doctor, lordJobRitual, assignments, preventLetter);
					newBabyGenes = null;
				}
			}
			finally
			{
				parents.Clear();
			}
			flag = true;
		}
		finally
		{
			disableBirthPatch = false;
			newBabyGenes = null;
			babyStartAge = null;
			if (!flag)
			{
				Log.Error("An Exception was thrown during the birth process.\nThe error was not captured but start-state has been salvaged.\nThe exception which occured may prevent Better Gene Inheritance genes from being appliedcorrectly, or prevent the likes of litterbirth genes from working.");
			}
		}
		return false;
	}

	[HarmonyPatch(typeof(PawnGenerator), "GeneratePawn", new Type[] { typeof(PawnGenerationRequest) })]
	[HarmonyPostfix]
	public static void MaySetBabyGenesIfBabyBirth(Pawn __result, PawnGenerationRequest request)
	{
		if (GenList.NullOrEmpty<Pawn>((IList<Pawn>)parents))
		{
			return;
		}
		Pawn val = __result;
		Pawn val2 = parents.First();
		if (((Thing)val2).def.IsHumanlikeAnimal())
		{
			val.SwapThingDef(((Thing)val2).def, state: true, 9999, force: true);
		}
		if (newBabyGenes != null)
		{
			val.genes.Endogenes.Clear();
			val.genes.Xenogenes.Clear();
			foreach (GeneDef newBabyGene in newBabyGenes)
			{
				val.genes.AddGene(newBabyGene, false);
			}
		}
		if (parents.Count > 0)
		{
			if (BSInheritanceWrapper.ModActive == true)
			{
				BSInheritanceWrapper.TrySetXenotypeBasedOnParents(val, parents);
			}
			else
			{
				List<(Pawn, float)> list = new List<(Pawn, float)>();
				foreach (Pawn item2 in parents.Where(delegate(Pawn x)
				{
					Pawn_GeneTracker genes = x.genes;
					return ((genes != null) ? genes.Xenotype : null) != null;
				}))
				{
					IEnumerable<GeneDef> babyGeneDefs = val.genes.GenesListForReading.Select((Gene x) => x.def);
					XenotypeDef xenotype = item2.genes.Xenotype;
					List<GeneDef> genes2 = xenotype.genes;
					_ = xenotype.inheritable;
					float item = (float)genes2.Sum((GeneDef x) => babyGeneDefs.Contains(x) ? 1 : 0) / (float)genes2.Count;
					list.Add((item2, item));
				}
				if (list.Count > 0)
				{
					(Pawn, float) tuple = list.OrderByDescending<(Pawn, float), float>(((Pawn pawn, float score) x) => x.score).First();
					var (val3, _) = tuple;
					if (tuple.Item2 > 0.8f)
					{
						val.genes.SetXenotypeDirect(val3.genes.Xenotype);
					}
				}
			}
		}
		if (babyStartAge.HasValue)
		{
			val.ageTracker.AgeBiologicalTicks = (babyStartAge * 3600000).Value;
		}
		__result = val;
	}
}
