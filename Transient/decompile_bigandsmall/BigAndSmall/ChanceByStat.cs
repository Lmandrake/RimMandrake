using System;
using System.Xml;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class ChanceByStat
{
	public StatDef statDef;

	public SimpleCurve curve = new SimpleCurve();

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		XmlNode firstChild = xmlRoot.FirstChild;
		DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "statDef", firstChild.Name, (string)null, (string)null, (Type)null);
		foreach (XmlNode childNode in firstChild.ChildNodes)
		{
			if (childNode.NodeType == XmlNodeType.Element)
			{
				curve.Add(new CurvePoint(ParseHelper.FromString<Vector2>(childNode.InnerText)), true);
			}
		}
	}

	public bool Evaluate(Thing thing, int seed)
	{
		float statValue = StatExtension.GetStatValue(thing, statDef, true, -1);
		float num = curve.Evaluate(statValue);
		RandBlock val = default(RandBlock);
		((RandBlock)(ref val))._002Ector(seed);
		try
		{
			if (Rand.Value > num)
			{
				return false;
			}
		}
		finally
		{
			((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
		}
		return true;
	}
}
