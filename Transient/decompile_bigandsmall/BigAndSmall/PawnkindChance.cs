using System;
using System.Xml;
using Verse;

namespace BigAndSmall;

public class PawnkindChance
{
	public PawnKindDef pawnKind;

	public float chance = 1f;

	public PawnkindChance()
	{
	}

	public PawnkindChance(PawnKindDef pawnKind, float chance)
	{
		this.pawnKind = pawnKind;
		this.chance = chance;
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "pawnKind", xmlRoot.Name, (string)null, (string)null, (Type)null);
		chance = ParseHelper.FromString<float>(xmlRoot.FirstChild.Value);
	}
}
