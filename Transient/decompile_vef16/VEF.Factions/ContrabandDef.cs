using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Factions;

public class ContrabandDef : Def
{
	public List<ThingDef> things;

	public List<ChemicalDef> chemicals;

	public List<ThingCategoryDef> thingCategories;

	public bool ignoreStuff;

	public bool ignoreRecipes;

	public HistoryEventDef giftedHistoryEvent;

	public HistoryEventDef soldHistoryEvent;

	public List<FactionDef> factions;

	public List<FactionDef> illegalFactions;

	public string giftWarningKey = "VEF.Factions.Contraband_Booze_GiftWarning";

	public string sellWarningKey = "VEF.Factions.Contraband_Booze_SellWarning";

	public string giftIllegalFactionWarningKey = "VEF.Factions.Contraband_Booze_GiftIllegalWarning";

	public string sellIllegalFactionWarningKey = "VEF.Factions.Contraband_Booze_SellIllegalWarning";

	public LetterDef letterType = LetterDefOf.ThreatSmall;

	public string letterLabelKey = "VEF.Factions.Contraband_Booze_LetterLabel";

	public string letterDescGiftKey = "VEF.Factions.Contraband_Booze_LetterDescGift";

	public string letterDescSoldKey = "VEF.Factions.Contraband_Booze_LetterDescSold";

	public string letterDescGifIllegalFactionKey = "VEF.Factions.Contraband_Booze_LetterDescIllegalGift";

	public string letterDescSoldIllegalFactionKey = "VEF.Factions.Contraband_Booze_LetterDescIllegalSold";

	public string relationInfoKey = "VEF.Factions.Contraband_Booze_RelationInfo";

	public float chanceToGetCaught = 0.5f;

	public float impactMultiplier = -1f;

	public FloatRange daysToImpact = new FloatRange(7f, 14f);

	public int ImpactInTicks => Find.TickManager.TicksGame + 60 + (int)(60000f * ((FloatRange)(ref daysToImpact)).RandomInRange);

	public virtual IEnumerable<Def> AllContraband()
	{
		if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)things))
		{
			foreach (ThingDef thing in things)
			{
				yield return (Def)(object)thing;
			}
		}
		if (!GenList.NullOrEmpty<ChemicalDef>((IList<ChemicalDef>)chemicals))
		{
			foreach (ChemicalDef chemical in chemicals)
			{
				yield return (Def)(object)chemical;
			}
		}
		if (GenList.NullOrEmpty<ThingCategoryDef>((IList<ThingCategoryDef>)thingCategories))
		{
			yield break;
		}
		foreach (ThingCategoryDef thingCategory in thingCategories)
		{
			yield return (Def)(object)thingCategory;
		}
	}

	public override string ToString()
	{
		StringBuilder stringBuilder = new StringBuilder(((Def)this).ToString());
		stringBuilder.AppendLine();
		if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)things))
		{
			stringBuilder.AppendLine($"Things: {things.Count}");
			foreach (ThingDef thing in things)
			{
				stringBuilder.AppendLine(" - " + ((Def)thing).label);
			}
		}
		if (!GenList.NullOrEmpty<ChemicalDef>((IList<ChemicalDef>)chemicals))
		{
			stringBuilder.AppendLine($"Chemicals: {chemicals.Count}");
			foreach (ChemicalDef chemical in chemicals)
			{
				stringBuilder.AppendLine(" - " + ((Def)chemical).label);
			}
		}
		stringBuilder.AppendLine($"Gifted History Event: {giftedHistoryEvent}");
		stringBuilder.AppendLine($"Sold History Event: {soldHistoryEvent}");
		if (!GenList.NullOrEmpty<FactionDef>((IList<FactionDef>)factions))
		{
			stringBuilder.AppendLine($"Factions: {factions.Count}");
			foreach (FactionDef faction in factions)
			{
				stringBuilder.AppendLine(" - " + ((Def)faction).label);
			}
		}
		stringBuilder.AppendLine("Gift Warning: " + giftWarningKey);
		stringBuilder.AppendLine("Sell Warning: " + sellWarningKey);
		stringBuilder.AppendLine("Letter Label: " + letterLabelKey);
		stringBuilder.AppendLine("Letter Description Gift: " + letterDescGiftKey);
		stringBuilder.AppendLine("Letter Description Sold: " + letterDescSoldKey);
		stringBuilder.AppendLine("Relation Info: " + relationInfoKey);
		stringBuilder.AppendLine($"Chance To Get Caught: {chanceToGetCaught}");
		return stringBuilder.ToString();
	}

	public bool IsThingContraband(Thing thing, out int count, out ThingDef contrabandThingDef, out ChemicalDef contrabandChemicalDef)
	{
		count = 0;
		contrabandThingDef = null;
		contrabandChemicalDef = null;
		if (IsThingDirectlyContraband(thing))
		{
			contrabandThingDef = thing.def;
			count++;
			return true;
		}
		if (IsThingDefChemicalDirectlyContraband(thing.def, out contrabandChemicalDef))
		{
			count++;
			return true;
		}
		if (!ignoreRecipes)
		{
			return false;
		}
		if (((BuildableDef)thing.def).costList != null)
		{
			foreach (ThingDefCountClass cost in ((BuildableDef)thing.def).costList)
			{
				ChemicalDef contrabandChemicalDef2;
				if (contrabandThingDef != null && cost.thingDef == contrabandThingDef)
				{
					count += cost.count;
				}
				else if (contrabandChemicalDef != null && IsThingDefChemicalDirectlyContraband(cost.thingDef, out contrabandChemicalDef2) && contrabandChemicalDef2 == contrabandChemicalDef)
				{
					count += cost.count;
				}
				else if (things.Contains(cost.thingDef))
				{
					count += cost.count;
				}
			}
			return count > 0;
		}
		foreach (RecipeDef item in DefDatabase<RecipeDef>.AllDefs.Where((RecipeDef r) => r.ProducedThingDef == thing.def))
		{
			foreach (IngredientCount item2 in item.ingredients.Where((IngredientCount x) => x.IsFixedIngredient))
			{
				if (things.Contains(item2.FixedIngredient))
				{
					contrabandThingDef = item2.FixedIngredient;
					count += Mathf.CeilToInt(item2.GetBaseCount());
				}
			}
		}
		return count > 0;
	}

	public bool IsThingDirectlyContraband(Thing thing)
	{
		if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)things))
		{
			if (things.Contains(thing.def))
			{
				return true;
			}
			if (!ignoreStuff && thing.Stuff != null && things.Contains(thing.Stuff))
			{
				return true;
			}
		}
		if (GenList.NullOrEmpty<ThingCategoryDef>((IList<ThingCategoryDef>)thingCategories))
		{
			return false;
		}
		if (!GenList.NullOrEmpty<ThingCategoryDef>((IList<ThingCategoryDef>)thing.def.thingCategories) && GenCollection.Any<ThingCategoryDef>(thingCategories, (Predicate<ThingCategoryDef>)((ThingCategoryDef tc) => thing.def.thingCategories.Contains(tc))))
		{
			return true;
		}
		if (!ignoreStuff && thing.Stuff != null)
		{
			return GenCollection.Any<ThingCategoryDef>(thingCategories, (Predicate<ThingCategoryDef>)((ThingCategoryDef tc) => thing.Stuff.thingCategories.Contains(tc)));
		}
		return false;
	}

	public bool IsThingDefChemicalDirectlyContraband(ThingDef thingDef, out ChemicalDef contrabandChemicalDef)
	{
		contrabandChemicalDef = null;
		if (GenList.NullOrEmpty<ChemicalDef>((IList<ChemicalDef>)chemicals) || !thingDef.HasComp<CompDrug>())
		{
			return false;
		}
		foreach (CompProperties_Drug item in thingDef.comps.OfType<CompProperties_Drug>())
		{
			if (chemicals.Contains(item.chemical))
			{
				contrabandChemicalDef = item.chemical;
				return true;
			}
		}
		return false;
	}

	public override IEnumerable<string> ConfigErrors()
	{
		foreach (string item in _003C_003En__0())
		{
			yield return item;
		}
		if (GenList.NullOrEmpty<FactionDef>((IList<FactionDef>)factions))
		{
			yield return "No factions targetted in ContrabandDef " + base.defName;
		}
		if (GenList.NullOrEmpty<FactionDef>((IList<FactionDef>)illegalFactions) && GenList.NullOrEmpty<ChemicalDef>((IList<ChemicalDef>)chemicals) && GenList.NullOrEmpty<ThingCategoryDef>((IList<ThingCategoryDef>)thingCategories))
		{
			yield return "ContrabandDef " + base.defName + " has no illegal items defined";
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0()
	{
		return ((Def)this).ConfigErrors();
	}
}
