using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PawnGenerator), "GetBodyTypeFor")]
public static class PawnGenPatchBodyTypeDef
{
	[HarmonyPostfix]
	public static void Postfix(ref BodyTypeDef __result, Pawn pawn)
	{
		BodyTypeDef val = default(BodyTypeDef);
		GenCollection.TryRandomElement<BodyTypeDef>(from r in PawnKindEdit.GetEditsFor(pawn.kindDef, ((Thing)pawn).Faction?.def).SelectMany((PawnKindEdit e) => e.BodyTypes ?? new List<DefRef<BodyTypeDef>>())
			select r.Def into d
			where d != null
			select d, ref val);
		if (val != null)
		{
			__result = val;
		}
	}
}
