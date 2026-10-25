using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>SUSPENSION_TOWER_DIAGNOSE_UNSUPPLIED_IN_POOL (live 2026-10-25, jawa/workgiver_probe): every suspension bridge part
	/// and drawbridge sets canGenerateDefaultDesignator=false because its own designator places it (anchor-to-anchor drag,
	/// Designator_SuspensionTower). Vanilla Ideology reads that flag as "an ideo-only buildable": Ideo.MembersCanBuild is false
	/// for any non-classic ideo without a meme, style or precept naming the def, so GenConstruct.CanConstruct refused every
	/// colonist ("Only Faithholders can build") and the delivery WorkGiver never offered a haul. A blueprint on deep water and
	/// one on dry ground were refused alike; swimming was never the gate. Here: a def from a mandrake.* mod that hides the
	/// default designator is buildable by members of every ideo, as an ordinary building is.</summary>
	[HarmonyPatch(typeof(Ideo), nameof(Ideo.MembersCanBuild))]
	[RimMandrake.Shared.PatchFeature("Own-designator buildings are buildable by every ideo")]
	public static class RM_Patch_Ideo_MembersCanBuild_OwnDesignator
	{
		[HarmonyPostfix]
		public static void Postfix(Thing thing, ref bool __result)
		{
			if (!__result && thing != null && IsOwnDesignatorBuildable(thing.def.entityDefToBuild ?? thing.def))
			{
				__result = true;
			}
		}

		/// <summary>A buildable of ours placed only by its own designator (no default one generated).</summary>
		public static bool IsOwnDesignatorBuildable(BuildableDef d)
		{
			return d != null && !d.canGenerateDefaultDesignator && IsMandrakePackage(d.modContentPack?.PackageId);
		}

		public static bool IsMandrakePackage(string packageId)
		{
			return packageId != null && packageId.StartsWith("mandrake.", System.StringComparison.OrdinalIgnoreCase);
		}
	}
}
