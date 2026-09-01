using System.Collections.Generic;
using System.Linq;
using System.Xml;
using Verse;

namespace BigAndSmall;

public class BodyTypesPerGender : List<GenderBodyType>
{
	public List<GenderBodyType> BodytypesForGender(Pawn pawn, Gender gender)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		List<GenderBodyType> list = this.Where((GenderBodyType x) => x.apparentGender.Contains(gender)).ToList();
		List<GenderBodyType> list2 = this.Where((GenderBodyType x) => x.developmentalStage.Contains(pawn.DevelopmentalStage)).ToList();
		List<GenderBodyType> list3 = list.Intersect(list2).ToList();
		if (GenCollection.Any<GenderBodyType>(list3))
		{
			return list3;
		}
		if (list.Count == 0 && list2.Count > 0)
		{
			return list2;
		}
		if (list2.Count == 0)
		{
			list2 = this.Where((GenderBodyType x) => x.isDefault).ToList();
		}
		return list2;
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		foreach (XmlNode childNode in xmlRoot.ChildNodes)
		{
			GenderBodyType genderBodyType = new GenderBodyType();
			genderBodyType.LoadDataFromXmlCustom(childNode);
			Add(genderBodyType);
		}
	}
}
