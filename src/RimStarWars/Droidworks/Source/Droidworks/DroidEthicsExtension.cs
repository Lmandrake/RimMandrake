using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Where a faction stands on destroying a sapient droid's mind, verbatim from
    /// the owner's frozen sheet row `abf_format_murder`
    /// (design/Jawa/droid_verbs_decisions.json): "SOME factions embrace deformatting
    /// (junkers, geneticists, empire). Most consider it unethical but not murder
    /// equivalent and necessary in some cases similar to lobotomization in human
    /// illness. A few consider it fully murder (neutral droid factions, moisture
    /// farmers)." — restated as design/Jawa/droid_system_spec.md section 8.
    /// </summary>
    public enum DeformatStance
    {
        /// <summary>Junkers, Ascendant Helix, the Empire. No goodwill consequence.</summary>
        Embraces = 0,

        /// <summary>Most factions: unethical, sometimes necessary. THE DEFAULT.</summary>
        Regrettable = 1,

        /// <summary>Free Droid Enclaves, Homestead moisture farmers. Murder, full stop.</summary>
        Murder = 2
    }

    /// <summary>
    /// Attach to a FactionDef to declare that faction's stance. ABSENT MEANS
    /// <see cref="DeformatStance.Regrettable"/> - which is the correct default,
    /// since the owner's own wording makes that the majority position.
    ///
    /// 🔴 NOTHING IN THIS MOD ATTACHES THIS EXTENSION TO ANY FACTION. Droidworks is
    /// the platform; which faction holds which stance is campaign data and belongs
    /// with the faction loadout work (DROID_FACTION_LOADOUTS_1, packet C1) in the
    /// RimUtinni tier. Until that lands, every faction reads as Regrettable and the
    /// goodwill hit is uniform. This class exists so that pass has a real field to
    /// set instead of inventing one at the point of use.
    /// </summary>
    public class DroidEthicsExtension : DefModExtension
    {
        public DeformatStance deformatStance = DeformatStance.Regrettable;

        /// <summary>
        /// Goodwill impact when this faction learns you destroyed one of its sapient
        /// droids. Calibrated against vanilla's own scale: Recipe_RemoveBodyPart
        /// reports a harvested organ at -70, so "murder, full stop" sits above it and
        /// "unethical but sometimes necessary" well below.
        /// </summary>
        public static int GoodwillImpactFor(DeformatStance stance)
        {
            switch (stance)
            {
                case DeformatStance.Embraces: return 0;
                case DeformatStance.Murder: return -100;
                default: return -25;
            }
        }

        public static DeformatStance StanceOf(Faction faction)
        {
            DroidEthicsExtension ext = faction?.def?.GetModExtension<DroidEthicsExtension>();
            return ext?.deformatStance ?? DeformatStance.Regrettable;
        }
    }
}
