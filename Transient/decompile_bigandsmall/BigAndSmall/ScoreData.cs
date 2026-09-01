using System;
using System.Collections.Generic;
using System.Xml;
using RimWorld;
using Verse;

namespace BigAndSmall;

/// <summary>
/// This is a class which calculates a numeric score for a given object.
/// </summary>
public class ScoreData : IScoreProvider
{
	public class StatDefRange
	{
		public StatDef statDef;

		public FloatRange range;

		public void LoadDataFromXmlCustom(XmlNode xmlRoot)
		{
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			string text = xmlRoot.Attributes?["MayRequire"]?.Value;
			DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "statDef", xmlRoot.Name, text, (string)null, (Type)null);
			string[] array = xmlRoot.FirstChild.Value.Split('~', StringSplitOptions.None);
			range = new FloatRange(float.Parse(array[0]), float.Parse(array[1]));
		}
	}

	public float score = 1f;

	public List<string> thingDef;

	public List<string> fleshDef;

	public List<string> mutantDef;

	public List<string> pawnKindDef;

	public List<string> pawnType;

	public FloatRange? sizeRange;

	public FloatRange? wealthValueRange;

	public List<StatDefRange> statDefRanges = new List<StatDefRange>();

	/// <summary>
	/// If -1, all filters must match. Otherwise, this sets how many filters must match.
	/// </summary>
	public int requiredMatchCount = -1;

	public bool nullOnFail = true;

	/// <summary>
	/// Gets the score for a given object.
	/// </summary>
	/// <returns>Returns null if the match fails. Otherwise returns 0-&gt;100% based on match quality.</returns>
	public virtual float? GetScore(object obj)
	{
		bool num = requiredMatchCount == -1;
		bool allMached = true;
		int matchCount = 0;
		MatchObj(obj, ref allMached, ref matchCount);
		if ((num && allMached) || matchCount >= requiredMatchCount)
		{
			return score;
		}
		if (!nullOnFail)
		{
			return 0f;
		}
		return null;
	}

	protected virtual void MatchObj(object obj, ref bool allMached, ref int matchCount)
	{
		Thing val = (Thing)((obj is Thing) ? obj : null);
		if (val != null)
		{
			MatchThing(val, ref allMached, ref matchCount);
		}
	}

	protected virtual void MatchThing(Thing thing, ref bool allMached, ref int matchCount)
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		if (thingDef != null && thingDef.Count > 0)
		{
			if (!thingDef.Contains(((Def)thing.def).defName))
			{
				allMached = false;
			}
			else
			{
				matchCount++;
			}
		}
		if (wealthValueRange.HasValue)
		{
			FloatRange value = wealthValueRange.Value;
			if (!((FloatRange)(ref value)).Includes(StatExtension.GetStatValue(thing, StatDefOf.MarketValue, true, -1)))
			{
				allMached = false;
			}
			else
			{
				matchCount++;
			}
		}
		foreach (StatDefRange statDefRange in statDefRanges)
		{
			if (!((FloatRange)(ref statDefRange.range)).Includes(StatExtension.GetStatValue(thing, statDefRange.statDef, true, -1)))
			{
				allMached = false;
			}
			else
			{
				matchCount++;
			}
		}
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			MatchPawn(val, ref allMached, ref matchCount);
		}
	}

	protected virtual void MatchPawn(Pawn pawn, ref bool allMached, ref int matchCount)
	{
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		if (fleshDef != null && fleshDef.Count > 0)
		{
			RaceProperties raceProps = pawn.RaceProps;
			FleshTypeDef val = ((raceProps != null) ? raceProps.FleshType : null);
			if (val != null && fleshDef.Contains(((Def)val).defName))
			{
				matchCount++;
			}
			else
			{
				allMached = false;
			}
		}
		if (mutantDef != null && mutantDef.Count > 0)
		{
			Pawn_MutantTracker mutant = pawn.mutant;
			MutantDef val2 = ((mutant != null) ? mutant.Def : null);
			if (val2 != null && pawn.IsMutant && mutantDef.Contains(((Def)val2).defName))
			{
				matchCount++;
			}
			else
			{
				allMached = false;
			}
		}
		if (pawnKindDef != null && pawnKindDef.Count > 0)
		{
			if (!pawnKindDef.Contains(((Def)pawn.kindDef).defName))
			{
				allMached = false;
			}
			else
			{
				matchCount++;
			}
		}
		if (sizeRange.HasValue)
		{
			FloatRange value = sizeRange.Value;
			if (!((FloatRange)(ref value)).Includes(pawn.BodySize))
			{
				allMached = false;
			}
			else
			{
				matchCount++;
			}
		}
		if (pawnType == null || pawnType.Count <= 0)
		{
			return;
		}
		bool flag = false;
		foreach (string item in pawnType)
		{
			if (item == "Animal" && pawn.RaceProps.Animal)
			{
				flag = true;
				break;
			}
			if (item == "Humanlike" && pawn.RaceProps.Humanlike)
			{
				flag = true;
				break;
			}
			if (item == "Mechanoid" && pawn.RaceProps.IsMechanoid)
			{
				flag = true;
				break;
			}
			if (item == "ToolUser" && pawn.RaceProps.ToolUser)
			{
				flag = true;
				break;
			}
			if (item == "HumanlikeAnimal" && ((Thing)pawn).def.IsHumanlikeAnimal())
			{
				flag = true;
				break;
			}
		}
		if (flag)
		{
			matchCount++;
		}
		else
		{
			allMached = false;
		}
	}
}
