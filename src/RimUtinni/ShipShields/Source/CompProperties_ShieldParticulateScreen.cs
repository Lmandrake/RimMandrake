using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    public class CompProperties_ShieldParticulateScreen : CompProperties
    {
        public float radius = 9.9f;
        public int intervalTicks = 250;

        public CompProperties_ShieldParticulateScreen()
        {
            compClass = typeof(CompShieldParticulateScreen);
        }
    }
}
