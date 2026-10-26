namespace RimMandrake.DivingInteraction
{
    /// <summary>
    /// CHILL_FIRE_BAN_1 + CHILLFIREBAN_DECIDE_FUELLED_COOKING_POWER: what the seabed fire ban does to one fuel-burning
    /// building, with no Verse or UnityEngine type in it, so the offline fuzz (Source/SelfTest/DivingFuzz.cs,
    /// `python3 src/RimMandrake/Utils/selftest_divinginteraction_fuzz.py`) compiles THIS file and drives the code the
    /// game runs. Patch_ChillFireBan reads the comps and RM_ChillFireGate.IsIgnitionAllowed and plays what this returns.
    /// A `using Verse;` landing here breaks the selftest build.
    ///
    /// The ruling (CHILL_FIRE_BAN_1, card 2026-09-27): "total ban — no flame works on the Chill seabed map. Campfires
    /// fizzle, chemfuel won't light ... Heat is electric only." So a building that burns fuel (it has a CompRefuelable
    /// AND a flame use: light, heat, a flame sprite, cooking/smithing bills, or a power plant) does none of those while
    /// the ban holds, and burns no fuel either — it is simply out. Pumped air (an oxygenated cell) or a self-oxidizing
    /// def lifts the ban; that is IsIgnitionAllowed's job, not this file's. Electric buildings (no CompRefuelable) and
    /// fuelled things with no flame use (a turret's barrel, a shuttle's tank) are never touched.
    /// </summary>
    public static class RM_ChillFireBanKernel
    {
        /// <summary>
        /// A refuelable building whose fuel feeds a flame: a COMBUSTION generator — a fuelled power plant that pushes
        /// heat or draws a flame (WoodFiredGenerator, ChemfuelPoweredGenerator, BioferriteGenerator, the KotOR Rhydonium
        /// and Tibanna reactors all carry a heat pusher) — or an unpowered building that glows, heats, draws a flame or
        /// works bills. A fuelled plant with neither is not burning anything (RM_DecayCell digests rot, RUT_VaultHeart
        /// eats a persona core; CHILLFIREBAN_FIX_NONCOMBUSTION_PLANT_BANNED; Outer Rim's tibanna fusion reactors carry no
        /// heat pusher either) and keeps working. Heat is a proxy, not proof: VQE's four uranium Genetrons push heat and
        /// burn nothing, so they opt out per def (Patches/RM_ChillFireBan_FissionGenetrons.xml). Census of all 29 fuelled
        /// plants on the owner's list, def dump 2026-10-26: CHILLFIREBAN_FIX_MODDED_OVERRIDES_BYPASS.
        /// A powered CONSUMER with fuel is a machine, not a fire (CHILLFIREBAN_FIX_POWERED_MACHINE_FREE_FUEL: KoltoTank,
        /// Autobong, Spaceports_FuelProcessor — their glow is an electric status light), so it is never a flame building.
        /// </summary>
        public static bool UsesFlame(bool hasRefuelable, bool glow, bool heat, bool flameOverlay, bool workTable,
            bool powerPlant, bool poweredConsumer)
        {
            if (!hasRefuelable)
            {
                return false;
            }
            if (powerPlant)
            {
                return heat || flameOverlay;
            }
            return !poweredConsumer && (glow || heat || flameOverlay || workTable);
        }

        /// <summary>
        /// Gate one vanilla output (lit, pushing heat, usable for bills, producing power) of a building. The ban can only
        /// turn an output OFF, never on: a fuel-out campfire stays out wherever it is.
        /// </summary>
        public static bool Output(bool vanillaOn, bool hasRefuelable, bool ignitionAllowed)
        {
            return vanillaOn && (!hasRefuelable || ignitionAllowed);
        }

        /// <summary>True when the passive fuel burn of this tick is skipped: a flame building that cannot burn.</summary>
        public static bool SkipFuelBurn(bool usesFlame, bool ignitionAllowed)
        {
            return usesFlame && !ignitionAllowed;
        }

        /// <summary>True when the building's inspect pane says why it is out (the player sees a dead stove, not a bug).</summary>
        public static bool ShowNoAirNote(bool usesFlame, bool ignitionAllowed)
        {
            return usesFlame && !ignitionAllowed;
        }
    }
}
