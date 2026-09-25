using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // shd:cryo-envelope (v2->v1, ship_shields_deep_design.md ruling table).
    // Owner's own words: "The opposite of the thermal rejection shield:
    // thermal absorptivity. Pulls in heat in both directions and allows the
    // shields to start glowing with red-orange black body radiation, holding
    // severe cold at bay. But slowly decreases the temperature within the
    // ship... still better than the extreme cold of the night-side
    // atmosphere."
    public class CompProperties_ShieldCryoEnvelope : CompProperties
    {
        // Same partial-correction-toward-comfort idiom as CompShieldThermalVeil,
        // but stronger -- the ruling's language for cryo ("holding severe
        // cold at bay") reads as a firmer claim than thermal's ("not nearly
        // as badly"), so this factor is higher than thermal veil's 0.45.
        public float insulationFactor = 0.6f;
        public float comfortTemperature = 21f;

        // The one thing thermal veil does NOT have: a genuine, un-mitigated
        // drain, applied every interval regardless of which direction the
        // correction above ran. This is the honest reading of "pulls in
        // heat in both directions... slowly decreases the temperature
        // within the ship" -- cryo's own cost, distinct from thermal veil's
        // (imperfect correction only). Degrees C removed from the room per
        // interval while the field is active and powered.
        public float interiorDriftPerInterval = 0.15f;

        public int intervalTicks = 250;

        public CompProperties_ShieldCryoEnvelope()
        {
            compClass = typeof(CompShieldCryoEnvelope);
        }
    }
}
