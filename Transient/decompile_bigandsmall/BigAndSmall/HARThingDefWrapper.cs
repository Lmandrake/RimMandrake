using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class HARThingDefWrapper
{
	public ThingDef HARThingDef;

	public List<BodyTypeDef> bodyDefs;

	public bool hasExtendedBodyGraphics;

	public bool HasBodyDefs
	{
		get
		{
			if (bodyDefs != null)
			{
				return bodyDefs.Count > 0;
			}
			return false;
		}
	}

	public HARThingDefWrapper(ThingDef harThingDef)
	{
		HARThingDef = harThingDef;
		bodyDefs = GetBodyTypes_V2(harThingDef);
		hasExtendedBodyGraphics = UsingCustomGraphics_V2(harThingDef);
	}

	private List<BodyTypeDef> GetBodyTypes_V2(ThingDef harThingDef)
	{
		return Traverse.Create((object)harThingDef).Field("alienRace").Field("compatibility")
			.Property("AvailableBodyTypes", (object[])null)
			.GetValue<List<BodyTypeDef>>();
	}

	private bool UsingCustomGraphics_V2(ThingDef harThingDef)
	{
		return Traverse.Create((object)harThingDef).Field("alienRace").Field("compatibility")
			.Property("UsingCustomGraphics", (object[])null)
			.GetValue<bool>();
	}
}
