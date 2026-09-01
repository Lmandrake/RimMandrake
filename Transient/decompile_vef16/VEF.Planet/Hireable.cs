using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Planet;

public class Hireable : IGrouping<string, HireableFactionDef>, IEnumerable<HireableFactionDef>, IEnumerable, ICommunicable, ILoadReferenceable
{
	private static readonly FieldRef<CrossRefHandler, LoadedObjectDirectory> loadedObjectInfo = AccessTools.FieldRefAccess<CrossRefHandler, LoadedObjectDirectory>("loadedObjectDirectory");

	private readonly List<HireableFactionDef> factions;

	public string Key { get; }

	public Hireable(string label, List<HireableFactionDef> list)
	{
		Key = label;
		factions = list;
		loadedObjectInfo.Invoke(Scribe.loader.crossRefs).RegisterLoaded((ILoadReferenceable)(object)this);
	}

	public string GetCallLabel()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.Hire", NamedArgument.op_Implicit(GenText.CapitalizeFirst(Key))));
	}

	public string GetInfoText()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.HireDesc", NamedArgument.op_Implicit(GenText.CapitalizeFirst(Key))));
	}

	public void TryOpenComms(Pawn negotiator)
	{
		Find.WindowStack.Add((Window)(object)new Dialog_Hire((Thing)(object)negotiator, this));
	}

	public Faction GetFaction()
	{
		return null;
	}

	public FloatMenuOption CommFloatMenuOption(Building_CommsConsole console, Pawn negotiator)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Expected O, but got Unknown
		return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(GetCallLabel(), (Action)delegate
		{
			console.GiveUseCommsJob(negotiator, (ICommunicable)(object)this);
		}, (MenuOptionPriority)7, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0), negotiator, LocalTargetInfo.op_Implicit((Thing)(object)console), "ReservedBy", (ReservationLayerDef)null);
	}

	public IEnumerator<HireableFactionDef> GetEnumerator()
	{
		return factions.GetEnumerator();
	}

	IEnumerator IEnumerable.GetEnumerator()
	{
		return GetEnumerator();
	}

	public string GetUniqueLoadID()
	{
		return "Hireable_" + Key;
	}
}
