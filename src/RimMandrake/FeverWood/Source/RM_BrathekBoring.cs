using RimWorld;
using Verse;

namespace RimMandrake.FeverWood
{
    /// <summary>
    /// FEVERWOOD_RM_CAST_COMPLETION_1: the brathek's only wood damage is
    /// vanilla tree-eating (foodType carries Tree in RM_FeverWoodCast.xml).
    /// RM_FeverWoodSettings.brathekBoresWood off strips the Tree flag, so it
    /// grazes like any other animal. No wall, building or boughway damage is
    /// built: the dig rate and whether it can be directed are open rulings
    /// (fauna roster §3), not guessed here.
    /// </summary>
    public static class RM_BrathekBoring
    {
        public const string RaceName = "RM_Brathek";

        public static void ApplySettings()
        {
            ThingDef race = DefDatabase<ThingDef>.GetNamedSilentFail(RaceName);
            if (race?.race == null)
            {
                return;
            }
            if (RM_FeverWoodSettings.brathekBoresWood)
            {
                race.race.foodType |= FoodTypeFlags.Tree;
            }
            else
            {
                race.race.foodType &= ~FoodTypeFlags.Tree;
            }
        }

        [StaticConstructorOnStartup]
        public static class Startup
        {
            static Startup()
            {
                ApplySettings();
            }
        }
    }
}
