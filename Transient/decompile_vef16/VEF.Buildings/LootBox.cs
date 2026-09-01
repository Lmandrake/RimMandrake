using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class LootBox : ThingWithComps, IOpenable
{
	public LootBoxExtension cachedLootBoxExtension;

	public CompQuality cachedCompQuality;

	public LootBoxExtension GetExtension
	{
		get
		{
			if (cachedLootBoxExtension == null)
			{
				cachedLootBoxExtension = ((Def)((Thing)this).def).GetModExtension<LootBoxExtension>();
			}
			return cachedLootBoxExtension;
		}
	}

	public CompQuality GetQuality
	{
		get
		{
			if (cachedCompQuality == null)
			{
				cachedCompQuality = ((ThingWithComps)this).GetComp<CompQuality>();
			}
			return cachedCompQuality;
		}
	}

	public int OpenTicks => 300;

	public bool CanOpen => true;

	public float AmountByQuality(QualityCategory quality)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Expected I4, but got Unknown
		return (int)quality switch
		{
			0 => 0.5f, 
			1 => 0.75f, 
			2 => 1f, 
			3 => 1.25f, 
			4 => 1.5f, 
			5 => 2.5f, 
			6 => 5f, 
			_ => 1f, 
		};
	}

	public void Open()
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		ThingSetMakerParams val = default(ThingSetMakerParams);
		val.totalMarketValueRange = GetExtension.totalMarketValueRange * AmountByQuality(GetQuality.Quality);
		val.minSingleItemMarketValuePct = GetExtension.minSingleItemMarketValuePct;
		val.allowNonStackableDuplicates = GetExtension.allowNonStackableDuplicates;
		int randomInRange = ((IntRange)(ref GetExtension.countRange)).RandomInRange;
		val.countRange = new IntRange(randomInRange, randomInRange);
		List<Thing> list = GetExtension.thingSetMakerDef.root.Generate(val);
		if (list == null)
		{
			return;
		}
		foreach (Thing item in list)
		{
			GenPlace.TryPlaceThing(item, ((Thing)this).Position, ((Thing)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
		}
		if (((Thing)this).Spawned)
		{
			((Thing)this).Destroy((DestroyMode)0);
		}
	}

	public override IEnumerable<StatDrawEntry> SpecialDisplayStats()
	{
		foreach (StatDrawEntry item in _003C_003En__0())
		{
			yield return item;
		}
		yield return new StatDrawEntry(StatCategoryDefOf.BasicsImportant, TaggedString.op_Implicit(Translator.Translate("VEF.TotalMarketValueRange")), ((object)(FloatRange)(ref GetExtension.totalMarketValueRange)/*cast due to .constrained prefix*/).ToString(), TaggedString.op_Implicit(Translator.Translate("VEF.TotalMarketValueRange_Desc")), 2749, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		StatCategoryDef basicsImportant = StatCategoryDefOf.BasicsImportant;
		string text = TaggedString.op_Implicit(Translator.Translate("VEF.TotalMarketValueRange_Quality"));
		FloatRange val = GetExtension.totalMarketValueRange * AmountByQuality(GetQuality.Quality);
		yield return new StatDrawEntry(basicsImportant, text, ((object)(FloatRange)(ref val)/*cast due to .constrained prefix*/).ToString(), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.TotalMarketValueRange_Quality_Desc", NamedArgument.op_Implicit(AmountByQuality(GetQuality.Quality).ToString()))), 2748, (string)null, (IEnumerable<Hyperlink>)null, false, false);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<StatDrawEntry> _003C_003En__0()
	{
		return ((ThingWithComps)this).SpecialDisplayStats();
	}
}
