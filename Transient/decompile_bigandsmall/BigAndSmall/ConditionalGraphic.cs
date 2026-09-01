using System;
using System.Collections.Generic;
using System.Linq;
using BigAndSmall.FilteredLists;
using RimWorld;
using Verse;

namespace BigAndSmall;

public abstract class ConditionalGraphic
{
	public class PartRecord
	{
		public BodyPartDef bodyPartDef;

		public bool mirrored;

		public bool partMissing;

		public bool mustBeReplacement;

		public bool implant;

		public bool mustBeBetterThanNatural;

		public HediffDef hasHediff;
	}

	public class HasTagGraphicOverride
	{
		public FlagString tag;

		public bool colorA;

		public bool colorB;

		public bool colorC;

		public FlagStringList customFlags = new FlagStringList();
	}

	public enum AltTrigger
	{
		Colonist,
		Male,
		Female,
		SlaveOfColony,
		PrisonerOfColony,
		SlaveOrPrisoner,
		OfColony,
		Unconcious,
		Dead,
		Rotted,
		Dessicated,
		HasForcedSkinColorGene,
		HasForcedHairColorGene,
		IsRecolored,
		BiotechDLC,
		IdeologyDLC,
		AnomalyDLC,
		CustomColorAIsSet,
		CustomColorBIsSet,
		CustomColorCIsSet,
		CustomSubColorAIsSet,
		CustomSubColorBIsSet,
		CustomSubColorCIsSet
	}

	public List<PartRecord> triggerBodyPart = new List<PartRecord>();

	public FilterListSet<string> triggerGeneTag = new FilterListSet<string>();

	public FilterListSet<GeneDef> triggerGene = new FilterListSet<GeneDef>();

	public FilterListSet<ApparelMatch> triggerApparel = new FilterListSet<ApparelMatch>();

	public FilterListSet<FlagString> triggerFlags = new FilterListSet<FlagString>();

	public int randSeed;

	private readonly List<AltTrigger> triggers = new List<AltTrigger>();

	public HasTagGraphicOverride customTagGraphicIsSet;

	private readonly List<AltTrigger> triggerConditions = new List<AltTrigger>();

	public float? chanceTrigger;

	public SimpleCurve chanceByAge;

	public ChanceByStat chanceByStat;

	public FlagStringList replaceFlags = new FlagStringList();

	public FlagStringList replaceFlagsAndInactive = new FlagStringList();

	public float replaceFlagMinPriority = float.MinValue;

	public bool HasGeneTriggers
	{
		get
		{
			if (!triggerGeneTag.AnyItems())
			{
				return triggerGene.AnyItems();
			}
			return true;
		}
	}

	public bool HasApparelTrigger => triggerApparel.AnyItems();

	public HashSet<AltTrigger> Triggers
	{
		get
		{
			HashSet<AltTrigger> hashSet = new HashSet<AltTrigger>();
			foreach (AltTrigger triggerCondition in triggerConditions)
			{
				hashSet.Add(triggerCondition);
			}
			foreach (AltTrigger trigger in triggers)
			{
				hashSet.Add(trigger);
			}
			return hashSet;
		}
	}

	public static void ResetStaticData()
	{
		ColorSetting.allLeatherColors = null;
		ColorSetting.randomClrPerId.Clear();
	}

	public List<GraphicsOverride> GetGraphicOverrides(Pawn pawn)
	{
		List<GraphicsOverride> allExtensions = pawn.GetAllExtensions<GraphicsOverride>();
		List<GraphicsOverride> allExtensionsPlusInactive = pawn.GetAllExtensionsPlusInactive<GraphicsOverride>();
		List<GraphicsOverride> list = ((pawn == null) ? null : ((Thing)pawn).Faction?.def.ExtensionsOnDef<GraphicsOverride, FactionDef>((List<Type>)null, (List<Type>)null, doSort: true)) ?? new List<GraphicsOverride>();
		List<GraphicsOverride> list2 = pawn?.kindDef?.ExtensionsOnDef<GraphicsOverride, PawnKindDef>((List<Type>)null, (List<Type>)null, doSort: true) ?? new List<GraphicsOverride>();
		List<GraphicsOverride> allExtensionsOnBackStories = pawn.GetAllExtensionsOnBackStories<GraphicsOverride>();
		HashSet<GraphicsOverride> hashSet = new HashSet<GraphicsOverride>();
		foreach (GraphicsOverride item in allExtensions)
		{
			hashSet.Add(item);
		}
		foreach (GraphicsOverride item2 in list)
		{
			hashSet.Add(item2);
		}
		foreach (GraphicsOverride item3 in list2)
		{
			hashSet.Add(item3);
		}
		foreach (GraphicsOverride item4 in allExtensionsOnBackStories)
		{
			hashSet.Add(item4);
		}
		HashSet<GraphicsOverride> hashSet2 = hashSet;
		hashSet = new HashSet<GraphicsOverride>();
		foreach (GraphicsOverride item5 in hashSet2)
		{
			hashSet.Add(item5);
		}
		foreach (GraphicsOverride item6 in allExtensionsPlusInactive)
		{
			hashSet.Add(item6);
		}
		HashSet<GraphicsOverride> hashSet3 = hashSet;
		FlagStringList flagStringList = replaceFlags;
		FlagStringList flagStringList2 = replaceFlagsAndInactive;
		List<FlagString> list3 = new List<FlagString>(flagStringList.Count + flagStringList2.Count);
		list3.AddRange(flagStringList);
		list3.AddRange(flagStringList2);
		List<FlagString> allFlags = list3;
		if (GenCollection.Any<GraphicsOverride>(hashSet3))
		{
			List<GraphicsOverride> list4 = (from x in hashSet2.SelectMany((GraphicsOverride x) => x.Overrides)
				where x.replaceFlags.Any((FlagString t) => replaceFlags.Contains(t))
				select x).ToList();
			List<GraphicsOverride> list5 = (from x in allExtensionsPlusInactive.SelectMany((GraphicsOverride x) => x.Overrides)
				where x.replaceFlags.Any((FlagString t) => allFlags.Contains(t))
				select x).ToList();
			List<GraphicsOverride> list6 = list4;
			List<GraphicsOverride> list7 = list5;
			int num = 0;
			GraphicsOverride[] array = new GraphicsOverride[list6.Count + list7.Count];
			foreach (GraphicsOverride item7 in list6)
			{
				array[num] = item7;
				num++;
			}
			foreach (GraphicsOverride item8 in list7)
			{
				array[num] = item8;
				num++;
			}
			return (from x in new List<GraphicsOverride>(new _003C_003Ez__ReadOnlyArray<GraphicsOverride>(array))
				where x.priority >= replaceFlagMinPriority
				orderby x.priority
				select x).ToList();
		}
		return new List<GraphicsOverride>();
	}

	private bool PartTriggersIsValid(Pawn pawn)
	{
		if (triggerBodyPart.Count > 0)
		{
			List<BodyPartRecord> allParts = pawn.RaceProps.body.AllParts;
			using List<PartRecord>.Enumerator enumerator = triggerBodyPart.GetEnumerator();
			if (enumerator.MoveNext())
			{
				PartRecord partRequire = enumerator.Current;
				bool flag = false;
				if (partRequire.bodyPartDef == null)
				{
					throw new Exception("PartRecord is missing a part definition.");
				}
				bool flag2 = false;
				bool flag3 = false;
				bool flag4 = false;
				bool flag5 = false;
				bool flag6 = false;
				foreach (Hediff item in pawn.health.hediffSet.hediffs.Where((Hediff x) => ((x == null) ? null : x.Part?.def) == partRequire.bodyPartDef && x.Part?.flipGraphic == partRequire.mirrored))
				{
					flag = true;
					AddedBodyPartProps addedPartProps = item.def.addedPartProps;
					if (addedPartProps != null && addedPartProps.betterThanNatural)
					{
						flag2 = true;
					}
					if (item is Hediff_AddedPart)
					{
						flag4 = true;
					}
					if (item.def.spawnThingOnRemoved != null)
					{
						flag3 = true;
					}
					if (item is Hediff_MissingPart)
					{
						flag5 = true;
					}
					if (item.def == partRequire.hasHediff)
					{
						flag6 = true;
					}
				}
				if (partRequire.partMissing && !flag && !GenCollection.Any<BodyPartRecord>(allParts, (Predicate<BodyPartRecord>)((BodyPartRecord x) => x.def == partRequire.bodyPartDef)))
				{
					flag5 = true;
				}
				if (partRequire.bodyPartDef != null && !flag)
				{
					return false;
				}
				if (partRequire.mustBeBetterThanNatural && !flag2)
				{
					return false;
				}
				if (partRequire.mustBeReplacement && !flag4)
				{
					return false;
				}
				if (partRequire.implant && !flag3)
				{
					return false;
				}
				if (partRequire.partMissing && !flag5)
				{
					return false;
				}
				if (partRequire.hasHediff != null && !flag6)
				{
					return false;
				}
				return true;
			}
		}
		return true;
	}

	private bool TriggerTagsValid(Pawn pawn)
	{
		if (triggerFlags.AnyItems())
		{
			List<FlagString> tagStrings = Flagger.GetTagStrings(pawn, includeInactive: false);
			FilterResult filterResultFromItemList = triggerFlags.GetFilterResultFromItemList(tagStrings);
			if (filterResultFromItemList.Denied() || (triggerFlags.requireExplicitPermission && filterResultFromItemList.NotExplicitlyAllowed()))
			{
				return false;
			}
		}
		return true;
	}

	private bool GeneTriggersValid(Pawn pawn)
	{
		if (HasGeneTriggers)
		{
			FilterResult filterResult = FilterResult.None;
			if (!triggerGeneTag.IsEmpty())
			{
				List<string> itemList = (from x in pawn.GetAllActiveGenes()
					where !GenList.NullOrEmpty<string>((IList<string>)x.def.exclusionTags)
					select x).SelectMany((Gene x) => x.def.exclusionTags).ToList();
				filterResult = triggerGeneTag.GetFilterResultFromItemList(itemList);
			}
			if (!triggerGene.IsEmpty())
			{
				List<GeneDef> itemList2 = GeneHelpers.GetAllActiveGeneDefs(pawn).ToList();
				filterResult = triggerGene.GetFilterResultFromItemList(itemList2).Fuse(filterResult);
			}
			if (!filterResult.ExplicitlyAllowed())
			{
				return false;
			}
		}
		return true;
	}

	private bool EquipTriggersValid(Pawn pawn)
	{
		if (HasApparelTrigger)
		{
			List<ApparelProperties> itemList = pawn.apparel.WornApparel.Select((Apparel x) => ((Thing)x).def.apparel).ToList();
			triggerApparel.GetFilterResultFromItemList(itemList, ApparelMatch.Matches);
		}
		return true;
	}

	private bool CustomTagGraphicIsSetIsValid(Pawn pawn)
	{
		if (customTagGraphicIsSet != null)
		{
			HasTagGraphicOverride tagOverride = customTagGraphicIsSet;
			if (tagOverride.colorA && !((Thing)(object)pawn).GetFlagColor(tagOverride.tag, 0).HasValue)
			{
				return false;
			}
			if (tagOverride.colorB && !((Thing)(object)pawn).GetFlagColor(tagOverride.tag, 1).HasValue)
			{
				return false;
			}
			if (tagOverride.colorC && !((Thing)(object)pawn).GetFlagColor(tagOverride.tag, 2).HasValue)
			{
				return false;
			}
			if (tagOverride.customFlags.Count != 0 && !tagOverride.customFlags.All((FlagString x) => ((Thing)(object)pawn).HasFlagTagValue(tagOverride.tag, x.mainTag, x.subTag)))
			{
				return false;
			}
		}
		return true;
	}

	/// <summary>
	/// "True" means use this graphic (if not chlidren are valid),
	/// "False" means skip and keep looking.
	/// "Null" is a valid result, but means that the graphic should be hidden.
	/// </summary>
	/// <returns></returns>
	public bool GetState(Pawn pawn, PawnRenderNode node = null)
	{
		int num = ((Thing)pawn).thingIDNumber + ((Def)((Thing)pawn).def).defName.GetHashCode() + randSeed;
		RandBlock val = default(RandBlock);
		if (chanceTrigger.HasValue)
		{
			((RandBlock)(ref val))._002Ector(num);
			try
			{
				if (Rand.Value > chanceTrigger.Value)
				{
					return false;
				}
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		if (chanceByAge != null)
		{
			float ageBiologicalYearsFloat = pawn.ageTracker.AgeBiologicalYearsFloat;
			float num2 = chanceByAge.Evaluate(ageBiologicalYearsFloat);
			((RandBlock)(ref val))._002Ector(num);
			try
			{
				if (Rand.Value > num2)
				{
					return false;
				}
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		if (chanceByStat != null && !chanceByStat.Evaluate((Thing)(object)pawn, num))
		{
			return false;
		}
		if (!TriggerTagsValid(pawn))
		{
			return false;
		}
		if (!PartTriggersIsValid(pawn))
		{
			return false;
		}
		if (!GeneTriggersValid(pawn))
		{
			return false;
		}
		if (!EquipTriggersValid(pawn))
		{
			return false;
		}
		if (!CustomTagGraphicIsSetIsValid(pawn))
		{
			return false;
		}
		if (Triggers.Count == 0)
		{
			return true;
		}
		Apparel val2 = node?.GetApparelFromNode();
		Thing customTarget = (Thing)(((object)val2) ?? ((object)pawn));
		return Triggers.All(delegate(AltTrigger x)
		{
			//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Invalid comparison between Unknown and I4
			//IL_00be: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c4: Invalid comparison between Unknown and I4
			//IL_018a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0190: Invalid comparison between Unknown and I4
			//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ae: Invalid comparison between Unknown and I4
			switch (x)
			{
			case AltTrigger.Colonist:
				return ((Thing)pawn).Faction == Faction.OfPlayerSilentFail && Faction.OfPlayerSilentFail != null;
			case AltTrigger.SlaveOfColony:
				return pawn.HostFaction == Faction.OfPlayerSilentFail && pawn.IsSlave;
			case AltTrigger.Male:
				return (int)pawn.gender == 1;
			case AltTrigger.Female:
				return (int)pawn.gender == 2;
			case AltTrigger.PrisonerOfColony:
				return pawn.HostFaction == Faction.OfPlayerSilentFail && pawn.IsPrisoner;
			case AltTrigger.SlaveOrPrisoner:
				return pawn.IsSlave || pawn.IsPrisoner;
			case AltTrigger.OfColony:
				return pawn.HostFaction == Faction.OfPlayerSilentFail || ((Thing)pawn).Faction == Faction.OfPlayerSilentFail;
			case AltTrigger.Unconcious:
				return pawn.Downed && !pawn.health.CanCrawl;
			case AltTrigger.Dead:
				return pawn.Dead;
			case AltTrigger.Rotted:
				return (int)pawn.Drawer.renderer.CurRotDrawMode == 2;
			case AltTrigger.Dessicated:
				return (int)pawn.Drawer.renderer.CurRotDrawMode == 4;
			case AltTrigger.HasForcedSkinColorGene:
				return pawn.GetAllActiveGenes().Any((Gene x) => x.def.skinColorOverride.HasValue);
			case AltTrigger.HasForcedHairColorGene:
				return pawn.GetAllActiveGenes().Any((Gene x) => x.def.hairColorOverride.HasValue);
			case AltTrigger.IsRecolored:
			{
				PawnRenderNode obj = node;
				int result;
				if (obj == null)
				{
					result = 0;
				}
				else
				{
					Apparel apparelFromNode = obj.GetApparelFromNode();
					bool? obj2;
					if (apparelFromNode == null)
					{
						obj2 = null;
					}
					else
					{
						CompColorable comp = ((ThingWithComps)apparelFromNode).GetComp<CompColorable>();
						obj2 = ((comp != null) ? new bool?(comp.Active) : ((bool?)null));
					}
					bool? flag = obj2;
					result = ((flag == true) ? 1 : 0);
				}
				return (byte)result != 0;
			}
			case AltTrigger.BiotechDLC:
				return ModsConfig.BiotechActive;
			case AltTrigger.IdeologyDLC:
				return ModsConfig.IdeologyActive;
			case AltTrigger.AnomalyDLC:
				return ModsConfig.AnomalyActive;
			case AltTrigger.CustomColorAIsSet:
				return CustomizableGraphic.Get(customTarget)?.colorA.HasValue ?? false;
			case AltTrigger.CustomColorBIsSet:
				return CustomizableGraphic.Get(customTarget)?.colorB.HasValue ?? false;
			case AltTrigger.CustomColorCIsSet:
				return CustomizableGraphic.Get(customTarget)?.colorC.HasValue ?? false;
			default:
				return false;
			}
		});
	}
}
