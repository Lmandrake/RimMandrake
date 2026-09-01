using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout.Util;

public static class Extensions
{
	private static HashSet<PawnKindDef> tempKinds = new HashSet<PawnKindDef>();

	public static Rect GetCentered(this Rect area, float width, float height)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		return new Rect(((Rect)(ref area)).center.x - width * 0.5f, ((Rect)(ref area)).center.y - height * 0.5f, width, height);
	}

	public static Rect GetCentered(this Rect area, string text)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		Vector2 val = Text.CalcSize(text);
		return area.GetCentered(val.x, val.y);
	}

	public static IEnumerable<PawnKindDef> GetKindDefs(this FactionDef def)
	{
		if (def == null)
		{
			return null;
		}
		tempKinds.Clear();
		if (def.pawnGroupMakers != null)
		{
			foreach (PawnGroupMaker pawnGroupMaker in def.pawnGroupMakers)
			{
				Register(pawnGroupMaker.options);
				Register(pawnGroupMaker.traders);
				Register(pawnGroupMaker.guards);
				Register(pawnGroupMaker.carriers);
			}
		}
		RegisterSimple(def.fixedLeaderKinds);
		if (def.basicMemberKind != null)
		{
			tempKinds.Add(def.basicMemberKind);
		}
		if (DefCache.DefaultFactionKinds != null && DefCache.DefaultFactionKinds.TryGetValue(def, out var value))
		{
			foreach (PawnKindDef item in value)
			{
				tempKinds.Add(item);
			}
		}
		return tempKinds;
		static void Register(List<PawnGenOption> list)
		{
			if (list == null)
			{
				return;
			}
			foreach (PawnGenOption item2 in list)
			{
				tempKinds.Add(item2.kind);
			}
		}
		static void RegisterSimple(List<PawnKindDef> list)
		{
			if (list == null)
			{
				return;
			}
			foreach (PawnKindDef item3 in list)
			{
				tempKinds.Add(item3);
			}
		}
	}

	public static PawnKindDef RandomKindDef(this FactionDef def)
	{
		return GenCollection.RandomElement<PawnKindDef>(def.GetKindDefs());
	}
}
