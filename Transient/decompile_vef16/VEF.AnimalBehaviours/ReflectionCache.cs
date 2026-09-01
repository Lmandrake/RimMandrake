using HarmonyLib;
using Verse;

namespace VEF.AnimalBehaviours;

public class ReflectionCache
{
	public static readonly FieldRef<Pawn, Pawn_DrawTracker> drawer = AccessTools.FieldRefAccess<Pawn, Pawn_DrawTracker>(AccessTools.Field(typeof(Pawn), "drawer"));
}
