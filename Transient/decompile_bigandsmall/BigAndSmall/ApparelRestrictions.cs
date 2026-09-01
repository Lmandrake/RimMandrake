using System;
using System.Collections.Generic;
using System.Linq;
using BigAndSmall.FilteredLists;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ApparelRestrictions
{
	public bool absolutelyNothing;

	public bool noClothes;

	public bool noArmor;

	public bool exceptNudistFriendly;

	public FilterListSet<string> tags;

	[Obsolete("Obsoleted because it had issues with cases where ApparelProperties were used with no access to the thing.")]
	public FilterListSet<ThingDef> thingDefs;

	/// <summary>
	/// OnSkin, Shell, Middle, etc.
	/// </summary>
	public FilterListSet<ApparelLayerDef> apparelLayers;

	/// <summary>
	/// Torso, Legs, LeftHand, etc.
	/// </summary>
	public FilterListSet<BodyPartGroupDef> bodyPartGroups;

	public bool NoApparel
	{
		get
		{
			if (!noClothes || !noArmor)
			{
				return absolutelyNothing;
			}
			return true;
		}
	}

	/// <summary>
	/// Returns the error if not, otherwise returns null.
	/// </summary>
	public string CanWear(ApparelProperties apparel, out FilterResult result)
	{
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		result = FilterResult.Neutral;
		string text = "";
		if (apparel == null)
		{
			return null;
		}
		if (apparelLayers != null)
		{
			result = apparelLayers.GetFilterResultFromItemList(apparel.layers).Fuse(result);
			if (text == "" && result.Denied())
			{
				text = TaggedString.op_Implicit(Translator.Translate("BS_CannotWearLayer"));
			}
		}
		if (bodyPartGroups != null)
		{
			result = bodyPartGroups.GetFilterResultFromItemList(apparel.bodyPartGroups).Fuse(result);
			if (text == "" && result.Denied())
			{
				text = TaggedString.op_Implicit(Translator.Translate("BS_CannotWearBodyPart"));
			}
		}
		if (exceptNudistFriendly && !apparel.countsAsClothingForNudity)
		{
			result = FilterResult.ForceAllow;
			return null;
		}
		List<string> list = apparel?.tags;
		if (list != null)
		{
			if (!apparel.HasRequiredApparelTags(tags?.ExplicitlyAcceptedItems))
			{
				return TaggedString.op_Implicit(Translator.Translate("BS_CannotWearTag"));
			}
			if (tags != null)
			{
				result = tags.GetFilterResultFromItemList(list).Fuse(result);
				if (text == "" && result.Denied())
				{
					text = TaggedString.op_Implicit(Translator.Translate("BS_CannotWearTag"));
				}
			}
		}
		if (thingDefs != null && thingDefs.AnyItems())
		{
			Log.WarningOnce("ApparelRestrictions Via thingDefs is obsoleted.\nThis is due to issues with the ThingDef sometimes being unavailablw when Ludeon runs checks.\nUse tags instead.\nTags can be patched onto any apparel via regular xml PatchOps.", 158733299);
		}
		if (NoApparel && !result.ForceAllowed())
		{
			if (exceptNudistFriendly && !apparel.countsAsClothingForNudity)
			{
				return null;
			}
			return TaggedString.op_Implicit(Translator.Translate("BS_CannotWearApparel"));
		}
		if (!result.Accepted())
		{
			return text;
		}
		return null;
	}

	public static void DebugTestAllWearable(Pawn testPawn)
	{
		BSCache cache = HumanoidPawnScaler.GetCache(testPawn, forceRefresh: true);
		if (cache != null)
		{
			CollectionExtensions.Do<ThingDef>((IEnumerable<ThingDef>)DefDatabase<ThingDef>.AllDefsListForReading.Where((ThingDef x) => x.IsApparel).ToList(), (Action<ThingDef>)delegate(ThingDef x)
			{
				string text = cache.apparelRestrictions?.CanWear(x);
				if (text != null)
				{
					Log.Message(((Entity)testPawn).LabelCap + " cannot wear " + ((Def)x).defName + ": " + text);
				}
			});
		}
		else
		{
			Log.Warning("[BigAndSmall] " + ((Def)((Thing)testPawn).def).defName + " could not generate a cache..");
		}
	}

	/// <summary>
	/// Returns the error if not, otherwise returns null.
	/// </summary>
	public string CanWear(ThingDef thingDef)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		if (thingDef == null)
		{
			return null;
		}
		FilterResult filterResult = FilterResult.Neutral;
		if (!thingDef.HasRequiredWeaponClassTags(tags?.ExplicitlyAcceptedItems))
		{
			return TaggedString.op_Implicit(Translator.Translate("BS_LacksRequiredClassTag"));
		}
		if (!thingDef.HasRequiredWeaponTags(tags?.ExplicitlyAcceptedItems))
		{
			return TaggedString.op_Implicit(Translator.Translate("BS_LacksRequiredTag"));
		}
		if (!thingDef.IsApparel)
		{
			return null;
		}
		FilterResult result;
		string text = CanWear(thingDef.apparel, out result);
		if (text != null)
		{
			return text;
		}
		if (result.ForceAllowed())
		{
			return null;
		}
		filterResult.Fuse(result);
		bool flag = IsArmor(thingDef);
		if (noArmor && flag)
		{
			return TaggedString.op_Implicit(Translator.Translate("BS_CannotWearArmor"));
		}
		if (noClothes && IsClothing(thingDef))
		{
			return TaggedString.op_Implicit(Translator.Translate("BS_CannotWearClothing"));
		}
		return TaggedString.op_Implicit(filterResult.Accepted() ? TaggedString.op_Implicit((string)null) : Translator.Translate("BS_CannotWearThis"));
	}

	private bool IsArmor(ThingDef thing)
	{
		List<string> list = thing.apparel.tags;
		if (list == null || !GenCollection.Any<string>(list, (Predicate<string>)((string x) => x.ToLower().Contains("armor", StringComparison.OrdinalIgnoreCase) || x.ToLower().Contains("armour", StringComparison.OrdinalIgnoreCase))))
		{
			List<ThingCategoryDef> thingCategories = thing.thingCategories;
			if (thingCategories == null || !GenCollection.Any<ThingCategoryDef>(thingCategories, (Predicate<ThingCategoryDef>)((ThingCategoryDef x) => ((Def)x).defName.ToLower().Contains("armor", StringComparison.OrdinalIgnoreCase))))
			{
				List<string> tradeTags = thing.tradeTags;
				if ((tradeTags == null || !GenCollection.Any<string>(tradeTags, (Predicate<string>)((string x) => x.ToLower().Contains("armor", StringComparison.OrdinalIgnoreCase)))) && !((Def)thing).defName.ToLower().Contains("armor", StringComparison.OrdinalIgnoreCase) && !((Def)thing).defName.ToLower().Contains("helmet", StringComparison.OrdinalIgnoreCase) && !((Def)thing).defName.ToLower().Contains("armour", StringComparison.OrdinalIgnoreCase))
				{
					RecipeMakerProperties recipeMaker = thing.recipeMaker;
					if (recipeMaker != null)
					{
						List<ThingDef> recipeUsers = recipeMaker.recipeUsers;
						if (((recipeUsers != null) ? new bool?(GenCollection.Any<ThingDef>(recipeUsers, (Predicate<ThingDef>)((ThingDef x) => ((Def)x).defName.ToLower().Contains("smithy")))) : ((bool?)null)) == true)
						{
							goto IL_017d;
						}
					}
					List<StuffCategoryDef> stuffCategories = ((BuildableDef)thing).stuffCategories;
					if (stuffCategories == null)
					{
						return false;
					}
					return GenCollection.Any<StuffCategoryDef>(stuffCategories, (Predicate<StuffCategoryDef>)((StuffCategoryDef x) => ((Def)x).defName.ToLower().Contains("metallic")));
				}
			}
		}
		goto IL_017d;
		IL_017d:
		return true;
	}

	private bool IsClothing(ThingDef thing)
	{
		return !IsArmor(thing);
	}

	public ApparelRestrictions MakeFusionWith(ApparelRestrictions other)
	{
		if (other == null)
		{
			return this;
		}
		if (this == null)
		{
			return other;
		}
		if (this == null && other == null)
		{
			return null;
		}
		return new ApparelRestrictions
		{
			absolutelyNothing = (absolutelyNothing || other.absolutelyNothing),
			noClothes = (noClothes || other.noClothes),
			noArmor = (noArmor || other.noArmor),
			exceptNudistFriendly = (exceptNudistFriendly || other.exceptNudistFriendly),
			tags = tags.MergeFilters(other.tags),
			apparelLayers = apparelLayers.MergeFilters(other.apparelLayers),
			bodyPartGroups = bodyPartGroups.MergeFilters(other.bodyPartGroups)
		};
	}
}
