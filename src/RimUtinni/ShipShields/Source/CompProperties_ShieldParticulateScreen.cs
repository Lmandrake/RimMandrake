using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    public class CompProperties_ShieldParticulateScreen : CompProperties
    {
        public float radius = 9.9f;
        public int intervalTicks = 250;

        // shd:particulate-screen, remaining half: "repels small animals" and
        // "handle... damage completely". Any wild animal at or below this
        // body size found in radius is pushed out via a real vanilla flee
        // job; animals above it (thrumbos, muffalo-scale wildlife) are
        // deliberately not shoved around by a filtration field.
        public float smallAnimalMaxBodySize = 0.35f;
        public int smallAnimalFleeDistance = 12;

        public CompProperties_ShieldParticulateScreen()
        {
            compClass = typeof(CompShieldParticulateScreen);
        }
    }
}
