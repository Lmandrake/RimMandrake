using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Genes;

public class HediffComp_HumanEggLayer : HediffComp
{
	private float eggProgress;

	private int fertilizationCount;

	private Pawn fertilizedBy;

	public int pregnancyRemovalCounter = -1;

	public List<GeneDef> motherGenes = new List<GeneDef>();

	public List<GeneDef> fatherGenes = new List<GeneDef>();

	private bool Active
	{
		get
		{
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Invalid comparison between Unknown and I4
			Pawn pawn = ((Hediff)base.parent).pawn;
			if (Props.eggLayFemaleOnly && pawn != null && (int)pawn.gender != 2)
			{
				return false;
			}
			if (!pawn.ageTracker.CurLifeStage.reproductive)
			{
				return false;
			}
			if (StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.Fertility, true, -1) <= 0f)
			{
				return false;
			}
			if (GeneUtility.SterileGenes(pawn))
			{
				return false;
			}
			return true;
		}
	}

	public bool CanLayNow
	{
		get
		{
			if (!Active)
			{
				return false;
			}
			return eggProgress >= 1f;
		}
	}

	public bool FullyFertilized => fertilizationCount >= 1;

	private bool ProgressStoppedBecauseUnfertilized
	{
		get
		{
			if (Props.eggProgressUnfertilizedMax < 1f && fertilizationCount == 0)
			{
				return eggProgress >= Props.eggProgressUnfertilizedMax;
			}
			return false;
		}
	}

	public HediffCompProperties_HumanEggLayer Props => (HediffCompProperties_HumanEggLayer)(object)base.props;

	public override string CompLabelInBracketsExtra => GetLabel();

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<float>(ref eggProgress, "eggProgress", 0f, false);
		Scribe_Values.Look<int>(ref fertilizationCount, "fertilizationCount", 0, false);
		Scribe_Values.Look<int>(ref pregnancyRemovalCounter, "pregnancyRemovalCounter", -1, false);
		Scribe_References.Look<Pawn>(ref fertilizedBy, "fertilizedBy", false);
		Scribe_Collections.Look<GeneDef>(ref motherGenes, "motherGenes", (LookMode)4, Array.Empty<object>());
		Scribe_Collections.Look<GeneDef>(ref fatherGenes, "fatherGenes", (LookMode)4, Array.Empty<object>());
	}

	public override void CompPostTick(ref float severityAdjustment)
	{
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (pregnancyRemovalCounter > -1)
		{
			pregnancyRemovalCounter++;
			if (pregnancyRemovalCounter > 100)
			{
				((HediffComp)this).Pawn.health.RemoveHediff(((HediffComp)this).Pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PregnantHuman, false));
				pregnancyRemovalCounter = -1;
			}
		}
		if (!Active)
		{
			return;
		}
		float num = 1f / (Props.eggLayIntervalDays * 60000f);
		Pawn pawn = ((Hediff)base.parent).pawn;
		if (pawn != null)
		{
			num *= PawnUtility.BodyResourceGrowthSpeed(pawn);
		}
		if (((Thing)((HediffComp)this).Pawn).Map != null)
		{
			eggProgress += num;
		}
		if (eggProgress >= 1f)
		{
			eggProgress = 1f;
			if (((Thing)((HediffComp)this).Pawn).Map != null)
			{
				ProduceEgg();
			}
		}
		if (ProgressStoppedBecauseUnfertilized)
		{
			eggProgress = Props.eggProgressUnfertilizedMax;
		}
	}

	public void Fertilize(Pawn male)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		fertilizationCount = 1;
		fertilizedBy = male;
		Find.LetterStack.ReceiveLetter(TranslatorFormattedStringExtensions.Translate("VGE_EggPregnancyLabel", NamedArgument.op_Implicit(((HediffComp)this).Pawn.NameShortColored)), TranslatorFormattedStringExtensions.Translate("VGE_EggPregnancy", NamedArgument.op_Implicit(((HediffComp)this).Pawn.NameShortColored)), LetterDefOf.PositiveEvent, LookTargets.op_Implicit(TargetInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn)), (Faction)null, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
	}

	public void DisableNormalPregnancy()
	{
		pregnancyRemovalCounter = 0;
	}

	public ThingDef NextEggType()
	{
		if (fertilizationCount > 0)
		{
			return Props.eggFertilizedDef;
		}
		return Props.eggUnfertilizedDef;
	}

	public virtual Thing ProduceEgg()
	{
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_0184: Unknown result type (might be due to invalid IL or missing references)
		if (!Active)
		{
			Log.Error("LayEgg while not Active: " + (object)base.parent);
		}
		eggProgress = 0f;
		Thing val;
		if (fertilizationCount > 0)
		{
			val = ThingMaker.MakeThing(Props.eggFertilizedDef, (ThingDef)null);
			fertilizationCount = 0;
		}
		else
		{
			val = ThingMaker.MakeThing(Props.eggUnfertilizedDef, (ThingDef)null);
		}
		CompHumanHatcher compHumanHatcher = ThingCompUtility.TryGetComp<CompHumanHatcher>(val);
		if (compHumanHatcher != null)
		{
			compHumanHatcher.hatcheeFaction = ((Thing)((Hediff)base.parent).pawn).Faction;
			Pawn pawn = ((Hediff)base.parent).pawn;
			if (pawn != null)
			{
				compHumanHatcher.hatcheeParent = pawn;
				compHumanHatcher.motherGenes = motherGenes;
			}
			if (fertilizedBy != null)
			{
				compHumanHatcher.otherParent = fertilizedBy;
				compHumanHatcher.fatherGenes = fatherGenes;
			}
			if (Props.maleDominant)
			{
				compHumanHatcher.maleDominant = Props.maleDominant;
			}
			if (Props.femaleDominant)
			{
				compHumanHatcher.femaleDominant = Props.femaleDominant;
			}
		}
		GenPlace.TryPlaceThing(val, ((Thing)((HediffComp)this).Pawn).Position, ((Thing)((HediffComp)this).Pawn).Map, (ThingPlaceMode)1, (Action<Thing, int>)delegate(Thing t, int i)
		{
			if (((Thing)((HediffComp)this).Pawn).Faction != Faction.OfPlayer)
			{
				ForbidUtility.SetForbidden(t, true, true);
			}
		}, (Predicate<IntVec3>)null, (Rot4?)null, 1);
		Find.LetterStack.ReceiveLetter(TranslatorFormattedStringExtensions.Translate("VGE_EggLaidLabel", NamedArgument.op_Implicit(((HediffComp)this).Pawn.NameShortColored)), TranslatorFormattedStringExtensions.Translate("VGE_EggLaid", NamedArgument.op_Implicit(((HediffComp)this).Pawn.NameShortColored)), LetterDefOf.PositiveEvent, LookTargets.op_Implicit(TargetInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn)), (Faction)null, (Quest)null, (List<ThingDef>)null, (string)null, 0, true);
		return val;
	}

	public string GetLabel()
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Invalid comparison between Unknown and I4
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		if (!Active)
		{
			return null;
		}
		string text = TaggedString.op_Implicit(Translator.Translate("EggProgress") + ": " + GenText.ToStringPercent(eggProgress));
		if (Props.eggLayFemaleOnly && (int)((HediffComp)this).Pawn.gender == 1)
		{
			text = TaggedString.op_Implicit(text + ("\n" + Translator.Translate("VGE_Male_Egg")));
		}
		else if (fertilizationCount > 0)
		{
			text = TaggedString.op_Implicit(text + ("\n" + Translator.Translate("Fertilized")));
		}
		else if (ProgressStoppedBecauseUnfertilized)
		{
			text = TaggedString.op_Implicit(text + ("\n" + Translator.Translate("ProgressStoppedUntilFertilized")));
		}
		return text;
	}
}
