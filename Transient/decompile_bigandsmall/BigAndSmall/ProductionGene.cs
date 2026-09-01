using System;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ProductionGene : TickdownGene
{
	private ProductionGeneSettings Props;

	private const int ticksPerDay = 60000;

	protected float fullness;

	private const int tickFrequency = 1000;

	protected int ResourceAmount => ModifyProductionBasedOnSize(Props.baseAmount, ((Gene)this).pawn);

	protected float GatherResourcesIntervalDays => Props.frequencyInDays * 60000f;

	protected ThingDef ResourceDef => Props.product;

	protected virtual bool ProductionActive
	{
		get
		{
			if (((Thing)((Gene)this).pawn).Faction == null)
			{
				return false;
			}
			if (((Thing)((Gene)this).pawn).Suspended)
			{
				return false;
			}
			return true;
		}
	}

	public bool ActiveAndFull
	{
		get
		{
			if (!((Gene)this).Active)
			{
				return false;
			}
			return fullness >= 1f;
		}
	}

	public override void ExposeData()
	{
		base.ExposeData();
		Props = ((Def)((Gene)this).def).GetModExtension<ProductionGeneSettings>();
		Scribe_Values.Look<float>(ref fullness, Props.saveKey, 0f, false);
	}

	public static int ModifyProductionBasedOnSize(int result, Pawn pawn)
	{
		BSCache cache = FastAcccess.GetCache(pawn);
		if (cache != null)
		{
			result = Math.Max(1, (int)((float)result * cache.scaleMultiplier.DoubleMaxLinear));
		}
		return result;
	}

	public override void TickEvent()
	{
		if (Props == null)
		{
			Props = ((Def)((Gene)this).def).GetModExtension<ProductionGeneSettings>();
			if (Props == null)
			{
				Log.Error("ProductionGeneSettings not found for " + ((Def)((Gene)this).def).defName);
			}
		}
		if (Props != null && ActiveAndFull)
		{
			Pawn pawn = ((Gene)this).pawn;
			if (pawn == null || pawn.Dead || ((Gene)this).pawn.Deathresting)
			{
				return;
			}
			ThingDef resourceDef = ResourceDef;
			int resourceAmount = ResourceAmount;
			Pawn_InventoryTracker inventory = ((Gene)this).pawn.inventory;
			Produce(resourceDef, resourceAmount, inventory);
			foreach (ProductionGeneSettings.SubProductionGeneSettings item in Props.extra)
			{
				ThingDef product = item.product;
				int amountToProduce = ModifyProductionBasedOnSize(item.baseAmount, ((Gene)this).pawn);
				Produce(product, amountToProduce, inventory);
			}
			fullness = 0f;
		}
		if (((Gene)this).Active)
		{
			float num = 1000f / GatherResourcesIntervalDays;
			if (((Gene)this).pawn != null)
			{
				num *= PawnUtility.BodyResourceGrowthSpeed(((Gene)this).pawn);
			}
			fullness += num;
			if (fullness > 1f)
			{
				fullness = 1f;
			}
		}
	}

	private void Produce(ThingDef resourceToProduce, int amountToProduce, Pawn_InventoryTracker inventory)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		Thing val = ThingMaker.MakeThing(resourceToProduce, (ThingDef)null);
		val.stackCount = amountToProduce;
		if (((Thing)((Gene)this).pawn).Map == null || !((Thing)((Gene)this).pawn).Spawned)
		{
			((ThingOwner)inventory.innerContainer).TryAdd(val, true);
		}
		else
		{
			GenPlace.TryPlaceThing(val, ((Thing)((Gene)this).pawn).Position, ((Thing)((Gene)this).pawn).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
		}
	}

	public override void ResetCountdown()
	{
		tickDown = 1000;
	}
}
