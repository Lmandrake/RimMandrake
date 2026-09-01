using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public static class PawnUtility_Mated
{
	[HarmonyPatch(typeof(PawnUtility))]
	[HarmonyPatch("Mated")]
	public static class VanillaExpandedFramework_PawnUtility_Mated_Patch
	{
		public static bool Prefix(Pawn male, Pawn female)
		{
			if (!female.ageTracker.CurLifeStage.reproductive)
			{
				return false;
			}
			CompExplodingEggLayer compExplodingEggLayer = ThingCompUtility.TryGetComp<CompExplodingEggLayer>((Thing)(object)female);
			if (compExplodingEggLayer != null)
			{
				compExplodingEggLayer.Fertilize(male);
				return false;
			}
			return true;
		}
	}
}
