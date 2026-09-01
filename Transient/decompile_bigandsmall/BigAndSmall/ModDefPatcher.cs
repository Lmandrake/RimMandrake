using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

/// <summary>
/// Patch defs in other mods. And things related to defs.
/// </summary>
public static class ModDefPatcher
{
	public static void PatchDefs()
	{
		IEnumerable<GeneDef> source = DefDatabase<GeneDef>.AllDefsListForReading.Where((GeneDef x) => ((Def)x).modExtensions != null && GenCollection.Any<DefModExtension>(((Def)x).modExtensions, (Predicate<DefModExtension>)((DefModExtension y) => y is PawnExtension)));
		if (!ModsConfig.IsActive("OskarPotocki.VFE.Insectoid2"))
		{
			return;
		}
		try
		{
			FieldInfo fieldInfo = AccessTools.Field(AccessTools.TypeByName("VFEInsectoids.PathFinder_FindPath_Patch"), "allowedGenes");
			if (fieldInfo != null)
			{
				HashSet<string> hashSet = fieldInfo.GetValue(null) as HashSet<string>;
				IEnumerable<GeneDef> source2 = source.Where((GeneDef x) => GenCollection.Any<DefModExtension>(((Def)x).modExtensions, (Predicate<DefModExtension>)((DefModExtension y) => y is PawnExtension pawnExtension && pawnExtension.canWalkOnCreep)));
				GenCollection.AddRange<string>(hashSet, source2.Select((GeneDef x) => ((Def)x).defName));
				Log.Message(string.Format("[Big and Small]: Patched VFEInsectoids 2 with {0} genes.\nIt now contains the following genes: {1}", source2.Count(), string.Join(", ", hashSet)));
			}
			else
			{
				Log.Message("Failed to patch VFEInsectoids 2's Creep with additional genes.");
			}
		}
		catch (Exception ex)
		{
			Log.Error("Failed to patch VFEInsectoids 2's Creep with additional genes.\n" + ex.Message + "\n" + ex.StackTrace);
		}
	}
}
