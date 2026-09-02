using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // design/Jawa/divine_satiation_engine.md §8b.B: "A birth -> ↑Oomo
    // (large), ↑Mob'Unloo (small) -- the sanctuary vision made real."
    //
    // Verified against decompiled source (RimSage):
    // `PregnancyUtility.ApplyBirthOutcome` (Source/RimWorld/PregnancyUtility.cs:225)
    // is the one shared exit point for every vanilla birth path (bed labor,
    // growth vat, debug tools) and already exposes `outcome.Positive` to
    // distinguish a live birth from a stillbirth -- no Rand re-roll or
    // health-state polling needed.
    //
    // Filtered to the player's own colony: `geneticMother.Faction ==
    // Faction.OfPlayer`. A stillbirth is left alone here (§8b makes no
    // Oomo claim about it either way, and this pass is not the place to
    // guess a sign for grief).
    [HarmonyPatch(typeof(PregnancyUtility), nameof(PregnancyUtility.ApplyBirthOutcome))]
    public static class Patch_BirthOutcome
    {
        [HarmonyPostfix]
        public static void Postfix(RitualOutcomePossibility outcome, Pawn geneticMother)
        {
            if (outcome == null || !outcome.Positive) return;
            if (geneticMother == null || geneticMother.Faction != Faction.OfPlayer) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Oomo, EventMagnitude.Large,
                "birth: " + geneticMother.LabelShortCap);
            comp.ApplyDelta(God.MobUnloo, EventMagnitude.Small,
                "birth (new soul on the ledger): " + geneticMother.LabelShortCap);
        }
    }
}
