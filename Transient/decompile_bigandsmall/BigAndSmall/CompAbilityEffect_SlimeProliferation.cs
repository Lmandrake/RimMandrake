using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;

namespace BigAndSmall;

public class CompAbilityEffect_SlimeProliferation : CompAbilityEffect
{
	public CompProperties_SlimeProliferation Props => (CompProperties_SlimeProliferation)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn != null)
		{
			DoProliferate(((AbilityComp)this).parent.pawn, pawn);
		}
	}

	public override bool Valid(LocalTargetInfo target, bool throwMessages = true)
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn == null)
		{
			pawn = ((AbilityComp)this).parent.pawn;
		}
		if (GeneHelpers.GetActiveGenesByName(pawn, "BS_SlimeProliferation").Count() == 0)
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_TargetLacksSlimeProliferation", NamedArgument.op_Implicit(((Entity)pawn).Label))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		return true;
	}

	public static void DoProliferate(Pawn parentA, Pawn parentB)
	{
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0301: Unknown result type (might be due to invalid IL or missing references)
		//IL_031a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0321: Expected O, but got Unknown
		//IL_02af: Unknown result type (might be due to invalid IL or missing references)
		List<GeneDef> list = (from x in parentA.GetAllActiveGenes()
			select x.def).ToList();
		List<GeneDef> list2 = (from x in parentB.GetAllActiveGenes()
			select x.def).ToList();
		List<GeneDef> sharedGenes = list.Intersect(list2).ToList();
		int num = list2.Count();
		int numberOfGenesToTransfer = Rand.RangeInclusive((int)((double)num * 0.1), num - 1);
		_ = parentA.kindDef;
		PawnGenerationRequest val = default(PawnGenerationRequest);
		((PawnGenerationRequest)(ref val))._002Ector(parentA.kindDef, ((Thing)parentA).Faction, (PawnGenerationContext)2, (PlanetTile?)PlanetTile.op_Implicit(-1), false, false, true, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)1, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false);
		((PawnGenerationRequest)(ref val)).IsCreepJoiner = parentA.IsCreepJoiner;
		Pawn val2 = PawnGenerator.GeneratePawn(val);
		val2.genes.Reset();
		if (parentB == null || parentB == parentA)
		{
			val2.genes.SetXenotype(parentA.genes.Xenotype);
		}
		else if (ModsConfig.IsActive("RedMattis.BetterGeneInheritance"))
		{
			foreach (GeneDef childGene in BSInheritanceWrapper.GetChildGenes(parentA, parentB))
			{
				val2.genes.AddGene(childGene, false);
			}
			BSInheritanceWrapper.TrySetXenotypeBasedOnParents(val2, new List<Pawn>(2) { parentA, parentB });
		}
		else
		{
			SetProliferateGenes(parentA, parentB, list, list2, sharedGenes, numberOfGenesToTransfer, val2);
		}
		Discombobulator.IntegrateGenes(val2);
		if (PawnUtility.TrySpawnHatchedOrBornPawn(val2, (Thing)(object)parentA, (IntVec3?)null))
		{
			if (val2.playerSettings != null && parentA.playerSettings != null)
			{
				val2.playerSettings.AreaRestrictionInPawnCurrentMap = parentA.playerSettings.AreaRestrictionInPawnCurrentMap;
			}
			if (val2.RaceProps.IsFlesh)
			{
				val2.relations.AddDirectRelation(PawnRelationDefOf.Parent, parentA);
				if (parentB != null)
				{
					val2.relations.AddDirectRelation(PawnRelationDefOf.Parent, parentB);
				}
			}
			if (((Thing)parentA).Spawned)
			{
				Lord lord = LordUtility.GetLord(parentA);
				if (lord != null)
				{
					lord.AddPawn(val2);
				}
			}
		}
		else
		{
			Find.WorldPawns.PassToWorld(val2, (PawnDiscardDecideMode)2);
		}
		TaleRecorder.RecordTale(TaleDefOf.GaveBirth, new object[2] { parentA, val2 });
		if (((Thing)parentA).Spawned)
		{
			FilthMaker.TryMakeFilth(((Thing)parentA).Position, ((Thing)parentA).Map, ThingDefOf.Filth_AmnioticFluid, GenText.LabelIndefinite(parentA), 5, (FilthSourceFlags)0);
			Pawn_CallTracker caller = parentA.caller;
			if (caller != null)
			{
				caller.DoCall(false);
			}
			Pawn_CallTracker caller2 = val2.caller;
			if (caller2 != null)
			{
				caller2.DoCall(false);
			}
		}
		ChoiceLetter_BabyBirth val3 = (ChoiceLetter_BabyBirth)LetterMaker.MakeLetter(Translator.Translate("BS_ProliferationBirth"), Translator.Translate("BS_ProliferationDescription"), LetterDefOf.BabyBirth, LookTargets.op_Implicit((Thing)(object)val2), (Faction)null, (Quest)null, (List<ThingDef>)null);
		val3.Start();
		Find.LetterStack.ReceiveLetter((Letter)(object)val3, (string)null, 0, true);
		int num2 = GenCollection.FirstOrDefault<PawnExtension>(val2.GetAllExtensions<PawnExtension>(), (Predicate<PawnExtension>)((PawnExtension x) => x.babyStartAge.HasValue))?.babyStartAge ?? 3;
		val2.ageTracker.AgeBiologicalTicks = num2 * 3600000;
	}

	private static void SetProliferateGenes(Pawn parentA, Pawn parentB, List<GeneDef> geneSetA, List<GeneDef> geneSetB, List<GeneDef> sharedGenes, int numberOfGenesToTransfer, Pawn babyPawn)
	{
		//IL_02e3: Unknown result type (might be due to invalid IL or missing references)
		foreach (GeneDef geneSetum in geneSetA)
		{
			babyPawn.genes.AddGene(geneSetum, false);
		}
		GeneHelpers.GetAllActiveEndoGenes(babyPawn).Sum((Gene x) => x.def.biostatMet);
		foreach (Gene item in babyPawn.genes.GenesListForReading.Where((Gene x) => !geneSetA.Contains(x.def)).ToList())
		{
			babyPawn.genes.RemoveGene(item);
		}
		if (parentA == parentB)
		{
			return;
		}
		int i = 0;
		List<GeneDef> list = new List<GeneDef>();
		for (; i < numberOfGenesToTransfer; i++)
		{
			if (geneSetB.Count <= 0)
			{
				break;
			}
			GeneDef val = GenCollection.RandomElement<GeneDef>((IEnumerable<GeneDef>)geneSetB);
			geneSetB.Remove(val);
			if (!babyPawn.genes.GenesListForReading.Select((Gene x) => x.def).Contains(val))
			{
				list.Add(val);
			}
		}
		foreach (GeneDef item2 in list)
		{
			babyPawn.genes.AddGene(item2, true);
		}
		babyPawn.GetAllActiveGenes().Sum((Gene x) => x.def.biostatMet);
		List<GeneDef> list2 = babyPawn.genes.Xenogenes.Select((Gene x) => x.def).ToList();
		babyPawn.genes.Xenogenes.Clear();
		foreach (GeneDef item3 in list2)
		{
			babyPawn.genes.AddGene(item3, true);
		}
		foreach (Gene item4 in babyPawn.genes.GenesListForReading.Where((Gene x) => x.Overridden).ToList())
		{
			babyPawn.genes.RemoveGene(item4);
		}
		GeneHelpers.RemoveRandomToMetabolism(0, babyPawn.genes, -5, sharedGenes);
		GeneHelpers.RemoveRandomToMetabolism(0, babyPawn.genes, -5);
		babyPawn.genes.xenotypeName = TaggedString.op_Implicit(Translator.Translate("Hybrid"));
	}
}
