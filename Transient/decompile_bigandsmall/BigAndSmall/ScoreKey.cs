using System;
using System.Linq;
using System.Xml;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ScoreKey : IScoreProvider
{
	public string keyTag = "";

	public float value = 1f;

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		keyTag = xmlRoot.Name;
		value = float.Parse(xmlRoot.FirstChild.Value);
	}

	public virtual float? GetScore(object obj)
	{
		Pawn val = (Pawn)((obj is Pawn) ? obj : null);
		if (val != null)
		{
			float? num = ScorePawn(val);
			if (num.HasValue)
			{
				return num.GetValueOrDefault();
			}
		}
		return null;
	}

	protected virtual float? ScorePawn(Pawn pawn)
	{
		string[] source = keyTag.Split('_', StringSplitOptions.None);
		if (source.Contains("ThingDef") && source.Contains(((Def)((Thing)pawn).def).defName))
		{
			return value;
		}
		if (source.Contains("FleshDef"))
		{
			RaceProperties raceProps = pawn.RaceProps;
			FleshTypeDef val = ((raceProps != null) ? raceProps.FleshType : null);
			if (val != null && source.Contains(((Def)val).defName))
			{
				return value;
			}
		}
		if (source.Contains("MutantDef"))
		{
			Pawn_MutantTracker mutant = pawn.mutant;
			MutantDef val2 = ((mutant != null) ? mutant.Def : null);
			if (val2 != null && pawn.IsMutant && source.Contains(((Def)val2).defName))
			{
				return value;
			}
		}
		return null;
	}
}
