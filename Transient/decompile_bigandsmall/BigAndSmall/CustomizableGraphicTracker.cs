using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CustomizableGraphicTracker : GameComponent
{
	public static CustomizableGraphicTracker GInstance;

	public Dictionary<string, CustomizableGraphic> thingGraphics = new Dictionary<string, CustomizableGraphic>();

	public CustomizableGraphicTracker(Game game)
	{
		GInstance = this;
	}

	public override void ExposeData()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Invalid comparison between Unknown and I4
		if ((int)Scribe.mode == 1)
		{
			CleanupDestroyedItems();
		}
		Scribe_Collections.Look<string, CustomizableGraphic>(ref thingGraphics, "thingCustomGraphics", (LookMode)1, (LookMode)2);
		if (thingGraphics == null)
		{
			thingGraphics = new Dictionary<string, CustomizableGraphic>();
		}
	}

	private void CleanupDestroyedItems()
	{
		List<string> toKeep = new List<string>();
		HashSet<Thing> allThingsEverywhere = GetAllThingsEverywhere();
		foreach (KeyValuePair<string, CustomizableGraphic> thingGraphic in thingGraphics)
		{
			foreach (Thing item in allThingsEverywhere)
			{
				if (item.ThingID == thingGraphic.Key)
				{
					toKeep.Add(thingGraphic.Key);
					break;
				}
			}
		}
		thingGraphics = thingGraphics.Where((KeyValuePair<string, CustomizableGraphic> kvp) => toKeep.Contains(kvp.Key)).ToDictionary((KeyValuePair<string, CustomizableGraphic> kvp) => kvp.Key, (KeyValuePair<string, CustomizableGraphic> kvp) => kvp.Value);
	}

	public static HashSet<Thing> GetAllThingsEverywhere()
	{
		List<Thing> first = Current.Game.Maps.SelectMany((Map x) => x.listerThings.AllThings).ToList();
		List<Pawn> second = Current.Game.Maps.SelectMany((Map x) => x.mapPawns.AllPawns).ToList();
		List<Thing> source = first.Concat((IEnumerable<Thing>)second).ToList();
		HashSet<Thing> hashSet = new HashSet<Thing>();
		foreach (Thing item in source.Where((Thing x) => !x.Destroyed))
		{
			hashSet.Add(item);
			IThingHolder val = (IThingHolder)(object)((item is IThingHolder) ? item : null);
			if (val != null && val.GetDirectlyHeldThings() != null)
			{
				foreach (Thing item2 in ((IEnumerable<Thing>)val.GetDirectlyHeldThings()).Where((Thing x) => !x.Destroyed))
				{
					hashSet.Add(item2);
				}
			}
			Pawn val2 = (Pawn)(object)((item is Pawn) ? item : null);
			if (val2 == null)
			{
				continue;
			}
			if (val2.apparel != null)
			{
				foreach (Apparel item3 in val2.apparel.WornApparel.Where((Apparel x) => !((Thing)x).Destroyed))
				{
					hashSet.Add((Thing)(object)item3);
				}
			}
			if (val2.equipment == null)
			{
				continue;
			}
			foreach (ThingWithComps item4 in val2.equipment.AllEquipmentListForReading.Where((ThingWithComps x) => !((Thing)x).Destroyed))
			{
				hashSet.Add((Thing)(object)item4);
			}
		}
		return hashSet;
	}
}
