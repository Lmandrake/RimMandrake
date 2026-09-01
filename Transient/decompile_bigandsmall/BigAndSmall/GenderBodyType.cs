using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class GenderBodyType
{
	public BodyTypeDef bodyType;

	public bool isDefault;

	public HashSet<Gender> apparentGender = new HashSet<Gender>();

	public HashSet<DevelopmentalStage> developmentalStage = new HashSet<DevelopmentalStage>();

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		List<string> list = xmlRoot.InnerText.Split(',', StringSplitOptions.None).ToList();
		for (int num = list.Count - 1; num >= 0; num--)
		{
			string text = list[num];
			DevelopmentalStage result2;
			if (Enum.TryParse<Gender>(text, out Gender result))
			{
				apparentGender.Add(result);
				list.RemoveAt(num);
			}
			else if (text == "Default" || text == "Any")
			{
				isDefault = true;
				list.RemoveAt(num);
			}
			else if (Enum.TryParse<DevelopmentalStage>(text, out result2))
			{
				developmentalStage.Add(result2);
				list.RemoveAt(num);
			}
		}
		if (developmentalStage.Count == 0)
		{
			developmentalStage.Add((DevelopmentalStage)8);
			developmentalStage.Add((DevelopmentalStage)0);
		}
		string name = xmlRoot.Name;
		string text2 = xmlRoot.Attributes?["MayRequire"]?.Value;
		DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "bodyType", name, text2, (string)null, (Type)null);
	}
}
