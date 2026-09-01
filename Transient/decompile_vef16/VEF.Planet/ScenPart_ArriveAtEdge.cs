using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Planet;

public class ScenPart_ArriveAtEdge : ScenPart
{
	private PlayerPawnsArriveMethod method;

	private IntVec3 location;

	public override void ExposeData()
	{
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		((ScenPart)this).ExposeData();
		Scribe_Values.Look<PlayerPawnsArriveMethod>(ref method, "method", (PlayerPawnsArriveMethod)0, false);
		Scribe_Values.Look<IntVec3>(ref location, "location", default(IntVec3), false);
	}

	public override void DoEditInterface(Listing_ScenEdit listing)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Expected O, but got Unknown
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Expected O, but got Unknown
		if (!Widgets.ButtonText(listing.GetScenPartRect((ScenPart)(object)this, ScenPart.RowHeight), PlayerPawnsArriveMethodExtension.ToStringHuman(method), true, true, true, (TextAnchor?)null))
		{
			return;
		}
		List<FloatMenuOption> list = new List<FloatMenuOption>();
		foreach (object value in Enum.GetValues(typeof(PlayerPawnsArriveMethod)))
		{
			PlayerPawnsArriveMethod val = (PlayerPawnsArriveMethod)value;
			PlayerPawnsArriveMethod localM = val;
			list.Add(new FloatMenuOption(PlayerPawnsArriveMethodExtension.ToStringHuman(localM), (Action)delegate
			{
				//IL_0007: Unknown result type (might be due to invalid IL or missing references)
				//IL_000c: Unknown result type (might be due to invalid IL or missing references)
				method = localM;
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
		}
		Find.WindowStack.Add((Window)new FloatMenu(list));
	}

	public override string Summary(Scenario scen)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Invalid comparison between Unknown and I4
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		if ((int)method == 1)
		{
			return TaggedString.op_Implicit(Translator.Translate("ScenPart_ArriveInDropPods"));
		}
		return null;
	}

	public override void Randomize()
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		method = (PlayerPawnsArriveMethod)0;
	}

	public override void GenerateIntoMap(Map map)
	{
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Invalid comparison between Unknown and I4
		if (Find.GameInitData == null)
		{
			return;
		}
		RCellFinder.TryFindRandomPawnEntryCell(ref location, map, 1f, false, (Predicate<IntVec3>)null);
		List<List<Thing>> list = new List<List<Thing>>();
		foreach (Pawn startingAndOptionalPawn in Find.GameInitData.startingAndOptionalPawns)
		{
			list.Add(new List<Thing> { (Thing)(object)startingAndOptionalPawn });
		}
		List<Thing> list2 = new List<Thing>();
		foreach (ScenPart allPart in Find.Scenario.AllParts)
		{
			list2.AddRange(allPart.PlayerStartingThings());
		}
		int num = 0;
		foreach (Thing item in list2)
		{
			if (item.def.CanHaveFaction)
			{
				item.SetFactionDirect(Faction.OfPlayer);
			}
			list[num].Add(item);
			num++;
			if (num >= list.Count)
			{
				num = 0;
			}
		}
		DropPodUtility.DropThingGroupsNear(location, map, list, 110, Find.GameInitData.QuickStarted || (int)method != 1, true, true, true, false, false, (Faction)null);
	}

	public override void PostMapGenerate(Map map)
	{
		_ = Find.GameInitData;
	}
}
