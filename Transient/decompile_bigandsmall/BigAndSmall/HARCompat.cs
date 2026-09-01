using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class HARCompat
{
	private static bool? harActive = null;

	private static bool harSetupCompleted = false;

	/// <summary>
	/// HAR Races use a subclass of ThingDef which we don't have direct access to, so we need a wrapper class built from reflection.
	/// </summary>
	public static Dictionary<ThingDef, HARThingDefWrapper> harThings = new Dictionary<ThingDef, HARThingDefWrapper>();

	public static bool HARActive
	{
		get
		{
			bool valueOrDefault = harActive == true;
			if (!harActive.HasValue)
			{
				valueOrDefault = ModLister.GetActiveModWithIdentifier("erdelf.HumanoidAlienRaces", false) != null || ModLister.GetActiveModWithIdentifier("erdelf.HumanoidAlienRaces.dev", false) != null;
				harActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	public static void TrySetupHARThingsIfHARIsActive()
	{
		if (!HARActive || harSetupCompleted)
		{
			return;
		}
		harSetupCompleted = true;
		List<ThingDef> list = DefDatabase<ThingDef>.AllDefsListForReading.Where((ThingDef x) => ((object)x).GetType().Name == "ThingDef_AlienRace").ToList();
		Log.Message($"[Big and Small]: Found {list.Count} AlienRace.ThingDef_AlienRace ThingDefs." + "\nThese are either from HAR races or B&S races automatically converted for compatibility.");
		foreach (ThingDef item in list)
		{
			harThings[item] = new HARThingDefWrapper(item);
		}
	}

	public static HARThingDefWrapper TryGetHarWrapper(ThingDef thingDef)
	{
		TrySetupHARThingsIfHARIsActive();
		if (HARActive && harThings.TryGetValue(thingDef, out var value) && value != null)
		{
			return value;
		}
		return null;
	}

	public static List<BodyTypeDef> TryGetHarBodiesForThingdef(ThingDef thingDef)
	{
		TrySetupHARThingsIfHARIsActive();
		if (HARActive && harThings.TryGetValue(thingDef, out var value) && value.HasBodyDefs)
		{
			return value.bodyDefs;
		}
		return null;
	}

	public static bool IsHarRaceWithExtendedBodyGraphics(ThingDef thingDef)
	{
		TrySetupHARThingsIfHARIsActive();
		if (HARActive && harThings.TryGetValue(thingDef, out var value) && value.hasExtendedBodyGraphics)
		{
			return true;
		}
		return false;
	}
}
