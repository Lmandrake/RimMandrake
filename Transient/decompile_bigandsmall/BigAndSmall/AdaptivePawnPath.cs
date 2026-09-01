using System;
using System.Collections.Generic;
using System.Xml;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class AdaptivePawnPath
{
	public string tag;

	public string texturePath;

	private Gender? _gender;

	private BodyTypeDef _bodyType;

	private int priority = -1;

	private bool initialized;

	private static bool defsLoaded = false;

	private static List<BodyTypeDef> bodyTypeDefs = new List<BodyTypeDef>();

	public BodyTypeDef GetBodyType()
	{
		TrySetup();
		return _bodyType;
	}

	public Gender? GetGender()
	{
		TrySetup();
		return _gender;
	}

	public int GetPriority()
	{
		TrySetup();
		return priority;
	}

	private void TrySetup()
	{
		if (!defsLoaded)
		{
			bodyTypeDefs = DefDatabase<BodyTypeDef>.AllDefsListForReading;
			defsLoaded = true;
		}
		if (initialized)
		{
			return;
		}
		_gender = ((tag == "Male") ? new Gender?((Gender)1) : ((tag == "Female") ? new Gender?((Gender)2) : ((tag == "None") ? new Gender?((Gender)0) : ((Gender?)null))));
		if (!_gender.HasValue)
		{
			_bodyType = GenCollection.FirstOrDefault<BodyTypeDef>(bodyTypeDefs, (Predicate<BodyTypeDef>)((BodyTypeDef x) => tag.Contains("Body_" + ((Def)x).defName)));
			_gender = (tag.StartsWith("Female") ? new Gender?((Gender)2) : (tag.StartsWith("Male") ? new Gender?((Gender)1) : (tag.StartsWith("None") ? new Gender?((Gender)0) : ((Gender?)null))));
			priority = ((!_gender.HasValue) ? 10 : 100);
		}
		else
		{
			priority = -10;
		}
		initialized = true;
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		tag = xmlRoot.Name;
		texturePath = xmlRoot.FirstChild.Value;
	}
}
