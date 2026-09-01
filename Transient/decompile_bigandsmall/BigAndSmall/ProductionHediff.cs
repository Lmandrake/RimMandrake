using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ProductionHediff : TickdownHediffComp
{
	private const int ticksPerDay = 60000;

	protected float fullness;

	private const int tickFrequency = 1000;

	private ProductionHediffSettings Props => ((HediffComp)this).props as ProductionHediffSettings;

	protected float GatherResourcesIntervalDays => Props.frequencyInDays * 60000f;

	protected virtual bool ProductionActive
	{
		get
		{
			if (((Thing)((Hediff)((HediffComp)this).parent).pawn).Suspended)
			{
				return false;
			}
			return true;
		}
	}

	public virtual bool Active
	{
		get
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Invalid comparison between Unknown and I4
			if (Props.femaleOnly && (int)((Hediff)((HediffComp)this).parent).pawn.gender != 2)
			{
				return false;
			}
			if (!ProductionActive)
			{
				return false;
			}
			HediffWithComps parent = ((HediffComp)this).parent;
			int? obj;
			if (parent == null)
			{
				obj = null;
			}
			else
			{
				Pawn pawn = ((Hediff)parent).pawn;
				if (pawn == null)
				{
					obj = null;
				}
				else
				{
					Pawn_AgeTracker ageTracker = pawn.ageTracker;
					obj = ((ageTracker != null) ? new int?(ageTracker.AgeBiologicalYears) : ((int?)null));
				}
			}
			if (!(obj >= Props.activationAge))
			{
				return false;
			}
			return true;
		}
	}

	public virtual bool ActiveAndFull => fullness >= 1f;

	public override string CompDescriptionExtra => string.Concat(((HediffComp)this).CompDescriptionExtra + ColoredText.Colorize("\n\n" + string.Join(", ", Props.products.Select((ProductionHediffSettings.ProductionSettings p) => p.ProductTooltip() + " x" + ModifyProductionBasedOnSize(p.baseAmount, ((Hediff)((HediffComp)this).parent).pawn))), ColoredText.TipSectionTitleColor), ", (", GenText.ToStringPercent(fullness), ")");

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<float>(ref fullness, Props.saveKey, 0f, false);
	}

	public static int ModifyProductionBasedOnSize(int result, Pawn pawn)
	{
		BSCache cachePrepatched = pawn.GetCachePrepatched();
		if (cachePrepatched != null)
		{
			result = Math.Max(1, (int)((float)result * cachePrepatched.scaleMultiplier.DoubleMaxLinear));
		}
		return result;
	}

	public override void TickEvent()
	{
		Pawn val = ((Hediff)(((HediffComp)this).parent?)).pawn;
		if (val == null)
		{
			return;
		}
		if (ActiveAndFull)
		{
			if (val == null || val.Dead || val.Deathresting)
			{
				return;
			}
			Pawn_InventoryTracker inventory = val.inventory;
			foreach (ProductionHediffSettings.ProductionSettings product in Props.products)
			{
				if (!(Props.chance < 1f) || !(Rand.Value > Props.chance))
				{
					int amountToProduce = ModifyProductionBasedOnSize(product.baseAmount, val);
					if (GenCollection.Any<ThingDef>(product.randomProduct))
					{
						ThingDef resourceToProduce = GenCollection.RandomElement<ThingDef>((IEnumerable<ThingDef>)product.randomProduct);
						Produce(resourceToProduce, amountToProduce, val, inventory);
					}
					else if (product.product != null)
					{
						Produce(product.product, amountToProduce, val, inventory);
					}
				}
			}
			fullness = 0f;
		}
		if (Active)
		{
			float num = 1000f / GatherResourcesIntervalDays;
			if (val != null)
			{
				num *= PawnUtility.BodyResourceGrowthSpeed(val);
			}
			fullness += num;
			if (fullness > 1f)
			{
				fullness = 1f;
			}
		}
	}

	private void Produce(ThingDef resourceToProduce, int amountToProduce, Pawn pawn, Pawn_InventoryTracker inventory)
	{
		Thing val = ThingMaker.MakeThing(resourceToProduce, (ThingDef)null);
		val.stackCount = amountToProduce;
		if (((Thing)pawn).Map == null || !((Thing)pawn).Spawned)
		{
			((ThingOwner)inventory.innerContainer).TryAdd(val, true);
		}
		else
		{
			Piloted.TryEjectFromPawn(val, pawn);
		}
	}

	public override void ResetCountdown()
	{
		tickDown = 1000;
	}
}
