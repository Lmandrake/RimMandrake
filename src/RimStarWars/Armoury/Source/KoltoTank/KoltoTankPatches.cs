using HarmonyLib;
using Verse;

namespace KoltoTank;

// Ported verbatim: the source class constructs a Harmony instance but never
// calls .Patch() on it -- genuinely a no-op in guy762.mm.kotorcore too, not a
// port defect. Kept for fidelity; costs nothing.
[StaticConstructorOnStartup]
public static class KoltoTankPatches
{
    static KoltoTankPatches()
    {
        _ = new Harmony("com.KoltoTank.rimworld.mod");
    }
}
