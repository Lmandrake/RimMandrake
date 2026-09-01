using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompExplodingEggLayer : ThingComp
{
	private float eggProgress;

	private int fertilizationCount;

	private Pawn fertilizedBy;

	private bool Active
	{
		get
		{
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Invalid comparison between Unknown and I4
			ThingWithComps parent = base.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (!Props.eggLayFemaleOnly || val == null || (int)val.gender == 2)
			{
				if (val != null)
				{
					return val.ageTracker.CurLifeStage.milkable;
				}
				return true;
			}
			return false;
		}
	}

	public bool CanLayNow
	{
		get
		{
			if (Active)
			{
				return eggProgress >= 1f;
			}
			return false;
		}
	}

	public bool FullyFertilized => fertilizationCount >= Props.eggFertilizationCountMax;

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

	public CompProperties_ExplodingEggLayer Props => (CompProperties_ExplodingEggLayer)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<float>(ref eggProgress, "eggProgress", 0f, false);
		Scribe_Values.Look<int>(ref fertilizationCount, "fertilizationCount", 0, false);
		Scribe_References.Look<Pawn>(ref fertilizedBy, "fertilizedBy", false);
	}

	public override void CompTick()
	{
		if (Active)
		{
			float num = 1f / (Props.eggLayIntervalDays * 60000f);
			ThingWithComps parent = base.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (val != null)
			{
				num *= PawnUtility.BodyResourceGrowthSpeed(val);
			}
			eggProgress += num;
			if (eggProgress > 1f)
			{
				eggProgress = 1f;
			}
			if (ProgressStoppedBecauseUnfertilized)
			{
				eggProgress = Props.eggProgressUnfertilizedMax;
			}
		}
	}

	public void Fertilize(Pawn male)
	{
		fertilizationCount = Props.eggFertilizationCountMax;
		fertilizedBy = male;
	}

	public virtual Thing ProduceEgg()
	{
		if (!Active)
		{
			Log.Error("LayEgg while not Active: " + (object)base.parent);
		}
		eggProgress = 0f;
		int randomInRange = ((IntRange)(ref Props.eggCountRange)).RandomInRange;
		if (randomInRange == 0)
		{
			return null;
		}
		Thing val;
		if (fertilizationCount > 0)
		{
			val = ThingMaker.MakeThing(Props.eggFertilizedDef, (ThingDef)null);
			fertilizationCount = Mathf.Max(0, fertilizationCount - randomInRange);
		}
		else
		{
			val = ThingMaker.MakeThing(Props.eggUnfertilizedDef, (ThingDef)null);
		}
		val.stackCount = randomInRange;
		CompExplodingHatcher compExplodingHatcher = ThingCompUtility.TryGetComp<CompExplodingHatcher>(val);
		if (compExplodingHatcher != null)
		{
			compExplodingHatcher.hatcheeFaction = ((Thing)base.parent).Faction;
			ThingWithComps parent = base.parent;
			Pawn val2 = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (val2 != null)
			{
				compExplodingHatcher.hatcheeParent = val2;
			}
			if (fertilizedBy != null)
			{
				compExplodingHatcher.otherParent = fertilizedBy;
			}
		}
		return val;
	}

	public override string CompInspectStringExtra()
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		if (!Active)
		{
			return null;
		}
		string text = TaggedString.op_Implicit(Translator.Translate("EggProgress") + ": " + GenText.ToStringPercent(eggProgress));
		if (fertilizationCount > 0)
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
