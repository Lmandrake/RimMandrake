using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml;
using RimWorld;
using Verse;

namespace Outposts;

public class AmountBySkill
{
	public int Count;

	public SkillDef Skill;

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		if (xmlRoot.ChildNodes.Count != 1)
		{
			Log.Error("Misconfigured AmountBySkill: " + xmlRoot.OuterXml);
			return;
		}
		DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "Skill", xmlRoot.Name, (string)null, (string)null, (Type)null);
		Count = ParseHelper.FromString<int>(xmlRoot.FirstChild.Value);
	}

	public int Amount(List<Pawn> pawns)
	{
		return Count * pawns.Sum((Pawn p) => p.skills.GetSkill(Skill).Level);
	}
}
