using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.Util;
using RimWorld;
using Verse;

namespace FactionLoadout;

[HotSwappable]
public class InventoryOptionEdit : IExposable, IDeepCopyable<InventoryOptionEdit>
{
	public ThingDef Thing = ThingDefOf.WoodLog;

	public IntRange CountRange = IntRange.One;

	public float ChoiceChance = 1f;

	public float SkipChance;

	public string BufferA;

	public string BufferB;

	public List<InventoryOptionEdit> SubOptionsTakeAll;

	public List<InventoryOptionEdit> SubOptionsChooseOne;

	public InventoryOptionEdit()
	{
	}//IL_000c: Unknown result type (might be due to invalid IL or missing references)
	//IL_0011: Unknown result type (might be due to invalid IL or missing references)


	public static int GetSize(InventoryOptionEdit option)
	{
		return option?.GetSize() ?? 0;
	}

	public static int GetSize(PawnInventoryOption option)
	{
		if (option == null)
		{
			return 0;
		}
		int num = ((option.thingDef != null) ? 1 : 0);
		if (option.subOptionsTakeAll != null)
		{
			num += ((IEnumerable<PawnInventoryOption>)option.subOptionsTakeAll).Sum((Func<PawnInventoryOption, int>)GetSize);
		}
		if (option.subOptionsChooseOne != null)
		{
			num += ((IEnumerable<PawnInventoryOption>)option.subOptionsChooseOne).Sum((Func<PawnInventoryOption, int>)GetSize);
		}
		return num;
	}

	public InventoryOptionEdit DeepClone()
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		return new InventoryOptionEdit
		{
			Thing = Thing,
			CountRange = CountRange,
			ChoiceChance = ChoiceChance,
			SkipChance = SkipChance,
			SubOptionsTakeAll = SubOptionsTakeAll?.Select((InventoryOptionEdit o) => o.DeepClone()).ToList(),
			SubOptionsChooseOne = SubOptionsChooseOne?.Select((InventoryOptionEdit o) => o.DeepClone()).ToList()
		};
	}

	public InventoryOptionEdit(PawnInventoryOption option)
		: this()
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		if (option != null)
		{
			Thing = option.thingDef;
			CountRange = option.countRange;
			ChoiceChance = option.choiceChance;
			SkipChance = option.skipChance;
			List<PawnInventoryOption> subOptionsTakeAll = option.subOptionsTakeAll;
			SubOptionsTakeAll = ((subOptionsTakeAll != null && subOptionsTakeAll.Count > 0) ? subOptionsTakeAll.Select((PawnInventoryOption x) => new InventoryOptionEdit(x)).ToList() : null);
			List<PawnInventoryOption> subOptionsChooseOne = option.subOptionsChooseOne;
			SubOptionsChooseOne = ((subOptionsChooseOne != null && subOptionsChooseOne.Count > 0) ? subOptionsChooseOne.Select((PawnInventoryOption x) => new InventoryOptionEdit(x)).ToList() : null);
		}
	}

	public PawnInventoryOption ConvertToVanilla()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Expected O, but got Unknown
		PawnInventoryOption val = new PawnInventoryOption
		{
			thingDef = Thing,
			choiceChance = ChoiceChance,
			skipChance = SkipChance,
			countRange = CountRange
		};
		List<InventoryOptionEdit> subOptionsTakeAll = SubOptionsTakeAll;
		val.subOptionsTakeAll = ((subOptionsTakeAll != null && subOptionsTakeAll.Count > 0) ? SubOptionsTakeAll.Select((InventoryOptionEdit o) => o.ConvertToVanilla()).ToList() : null);
		subOptionsTakeAll = SubOptionsChooseOne;
		val.subOptionsChooseOne = ((subOptionsTakeAll != null && subOptionsTakeAll.Count > 0) ? SubOptionsChooseOne.Select((InventoryOptionEdit o) => o.ConvertToVanilla()).ToList() : null);
		return val;
	}

	public int GetSize()
	{
		int num = ((Thing != null) ? 1 : 0);
		if (SubOptionsChooseOne != null)
		{
			num += SubOptionsChooseOne.Sum((InventoryOptionEdit item) => item.GetSize());
		}
		if (SubOptionsTakeAll != null)
		{
			num += SubOptionsTakeAll.Sum((InventoryOptionEdit item) => item.GetSize());
		}
		return num;
	}

	public void ExposeData()
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		Scribe_Defs.Look<ThingDef>(ref Thing, "thing");
		Scribe_Values.Look<IntRange>(ref CountRange, "count", default(IntRange), false);
		Scribe_Values.Look<float>(ref ChoiceChance, "choiceChance", 0f, false);
		Scribe_Values.Look<float>(ref SkipChance, "skipChance", 0f, false);
		Scribe_Collections.Look<InventoryOptionEdit>(ref SubOptionsTakeAll, "takeAll", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<InventoryOptionEdit>(ref SubOptionsChooseOne, "takeOne", (LookMode)2, Array.Empty<object>());
	}
}
