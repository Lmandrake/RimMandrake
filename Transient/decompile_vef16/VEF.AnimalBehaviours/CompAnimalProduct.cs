using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompAnimalProduct : CompHasGatherableBodyResource
{
	public int seasonalItemIndex;

	protected override int GatherResourcesIntervalDays => Props.gatheringIntervalDays;

	protected override int ResourceAmount => Props.resourceAmount;

	protected override ThingDef ResourceDef
	{
		get
		{
			if (Props.seasonalItems != null)
			{
				return ThingDef.Named(Props.seasonalItems[seasonalItemIndex]);
			}
			if (Props.isRandom)
			{
				return ThingDef.Named(GenCollection.RandomElement<string>((IEnumerable<string>)Props.randomItems));
			}
			return Props.resourceDef;
		}
	}

	protected override string SaveKey => "resourceGrowth";

	public CompProperties_AnimalProduct Props => (CompProperties_AnimalProduct)(object)((ThingComp)this).props;

	protected override bool Active
	{
		get
		{
			if (!((CompHasGatherableBodyResource)this).Active)
			{
				return false;
			}
			ThingWithComps parent = ((ThingComp)this).parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (val != null)
			{
				return val.ageTracker.CurLifeStage.shearable;
			}
			return true;
		}
	}

	public override void PostExposeData()
	{
		((CompHasGatherableBodyResource)this).PostExposeData();
		Scribe_Values.Look<int>(ref seasonalItemIndex, "seasonalItemIndex", 0, false);
	}

	public override string CompInspectStringExtra()
	{
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		if (!((CompHasGatherableBodyResource)this).Active)
		{
			return null;
		}
		if (Props.hideDisplayOnWildAnimals)
		{
			ThingWithComps parent = ((ThingComp)this).parent;
			if (((parent != null) ? ((Thing)parent).Faction : null) != Faction.OfPlayerSilentFail)
			{
				return null;
			}
		}
		if (!GenText.NullOrEmpty(Props.customResourceString))
		{
			return TaggedString.op_Implicit(Translator.Translate(Props.customResourceString) + ": " + GenText.ToStringPercent(((CompHasGatherableBodyResource)this).Fullness));
		}
		return TaggedString.op_Implicit(Translator.Translate("ResourceGrowth") + ": " + GenText.ToStringPercent(((CompHasGatherableBodyResource)this).Fullness));
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (DebugSettings.ShowDevGizmos && ((Thing)((ThingComp)this).parent).Faction == Faction.OfPlayer)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = "DEV: Set to produce now",
				defaultDesc = "Sets animal products to be ready to be gathered now",
				action = delegate
				{
					base.fullness = 1f;
				}
			};
		}
	}

	public void InformGathered(Pawn doer)
	{
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_018a: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a0: Unknown result type (might be due to invalid IL or missing references)
		if (!((CompHasGatherableBodyResource)this).Active)
		{
			Log.Error(((object)doer)?.ToString() + " gathered body resources while not Active: " + (object)((ThingComp)this).parent);
		}
		if (!Rand.Chance(StatExtension.GetStatValue((Thing)(object)doer, StatDefOf.AnimalGatherYield, true, -1)))
		{
			MoteMaker.ThrowText((((Thing)doer).DrawPos + ((Thing)((ThingComp)this).parent).DrawPos) / 2f, ((Thing)((ThingComp)this).parent).Map, TaggedString.op_Implicit(Translator.Translate("TextMote_ProductWasted")), 3.65f);
		}
		else
		{
			int num = GenMath.RoundRandom((float)((CompHasGatherableBodyResource)this).ResourceAmount * base.fullness);
			while (num > 0)
			{
				int num2 = Mathf.Clamp(num, 1, ((CompHasGatherableBodyResource)this).ResourceDef.stackLimit);
				num -= num2;
				Thing obj = ThingMaker.MakeThing(((CompHasGatherableBodyResource)this).ResourceDef, (ThingDef)null);
				obj.stackCount = num2;
				GenPlace.TryPlaceThing(obj, ((Thing)doer).Position, ((Thing)doer).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
			}
			if (Props.hasAditional && Rand.Chance((float)Props.additionalItemsProb / 100f))
			{
				if (Props.goInOrder)
				{
					foreach (string item in GenCollection.InRandomOrder<string>((IEnumerable<string>)Props.additionalItems, (IList<string>)null))
					{
						if (DefDatabase<ThingDef>.GetNamedSilentFail(item) != null)
						{
							Thing obj2 = ThingMaker.MakeThing(ThingDef.Named(GenCollection.RandomElement<string>((IEnumerable<string>)Props.additionalItems)), (ThingDef)null);
							obj2.stackCount = Props.additionalItemsNumber;
							GenPlace.TryPlaceThing(obj2, ((Thing)doer).Position, ((Thing)doer).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
						}
					}
				}
				else
				{
					Thing obj3 = ThingMaker.MakeThing(ThingDef.Named(GenCollection.RandomElement<string>((IEnumerable<string>)Props.additionalItems)), (ThingDef)null);
					obj3.stackCount = Props.additionalItemsNumber;
					GenPlace.TryPlaceThing(obj3, ((Thing)doer).Position, ((Thing)doer).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
				}
			}
		}
		base.fullness = 0f;
	}
}
