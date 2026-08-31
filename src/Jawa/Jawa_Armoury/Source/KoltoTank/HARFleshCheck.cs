using System;
using HarmonyLib;
using Verse;

namespace KoltoTank;

// Ported without a hard compile-time dependency on Humanoid Alien Races
// (kotorcore's own HARFleshCheck referenced AlienRace.dll directly; Jawa_Armoury
// does not already carry that dependency). Reflects for the same
// ThingDef_AlienRace.alienRace.compatibility.IsFleshPawn(pawn) path guy762's
// version called directly, falling back to vanilla RaceProps.IsFlesh when HAR
// isn't active/loaded or the reflected path is absent -- same effective
// behavior guarded by ModIsLoaded("Humanoid Alien Races") at the one call site
// (Building_KoltoTank.GetFloatMenuOptions), no new forced mod dependency.
public static class HARFleshCheck
{
    public static bool IsItFlesh(this Pawn pawn)
    {
        try
        {
            Type defType = pawn.def.GetType();
            if (defType.Name != "ThingDef_AlienRace")
            {
                return pawn.RaceProps.IsFlesh;
            }
            object alienRace = AccessTools.Field(defType, "alienRace")?.GetValue(pawn.def);
            object compatibility = alienRace?.GetType().GetField("compatibility")?.GetValue(alienRace);
            if (compatibility == null)
            {
                return pawn.RaceProps.IsFlesh;
            }
            object result = AccessTools.Method(compatibility.GetType(), "IsFleshPawn")?.Invoke(compatibility, new object[] { pawn });
            return result is bool isFlesh ? isFlesh : pawn.RaceProps.IsFlesh;
        }
        catch
        {
            return pawn.RaceProps.IsFlesh;
        }
    }
}
