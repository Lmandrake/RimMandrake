using System;
using System.Xml;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class ConditionSucceedQuestsCount
{
	public QuestScriptDef questDef;

	public int count;

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "questDef", xmlRoot, (string)null, (string)null, (Type)null);
		count = ParseHelper.FromString<int>(xmlRoot.FirstChild.Value);
	}
}
