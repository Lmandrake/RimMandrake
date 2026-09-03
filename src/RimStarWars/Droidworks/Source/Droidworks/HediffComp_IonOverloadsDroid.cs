using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    public class HediffCompProperties_IonOverloadsDroid : HediffCompProperties
    {
        public HediffCompProperties_IonOverloadsDroid() =>
            compClass = typeof(HediffComp_IonOverloadsDroid);
    }

    /// <summary>
    /// DROIDWORKS_POWEREDDOWN_NOT_WIRED_1. Wired onto RimMandrake.StarWars.JawaIonWeapons' RSW_JawaIon_Stun
    /// via Patches/IonBuildup_PowersDownDroid.xml (FindMod-gated on "Jawa Ion
    /// Weapons (local)" — a no-op if that mod isn't active).
    ///
    /// Corrected 2026-09-02, pass 3: DW_ race droids are non-flesh
    /// (Races_Base.xml sets fleshType RSW_DW_FleshType_Droid, not Human's
    /// organic one). DamageWorker_IonBuildup gates its RSW_JawaIon_Stun buildup
    /// on IsMechanoid (droids are deliberately NOT FleshTypeDefOf.Mechanoid, so
    /// they still accumulate it) and separately applies the vanilla EMP tier
    /// (ApplyMachineTier) to every non-flesh pawn including droids — both fire.
    /// RSW_JawaIon_Stun's own capMods cap Consciousness, downing the pawn, but
    /// that hediff self-decays (HediffCompProperties_SeverityPerDay), so an
    /// ion-overloaded droid just wobbles back up on its own like a person
    /// would, never touching RSW_DW_PoweredDown (the persistent, reboot-only
    /// state the rest of the droid state machine — Need_Power,
    /// Recipe_RebootDroid — is built around).
    ///
    /// This comp closes that gap without any cross-assembly build dependency
    /// (RimMandrake.StarWars.JawaIonWeapons.dll never references RimMandrake.StarWars.Droidworks.dll or vice versa; the
    /// XML <comps> Class="" attribute resolves by reflection across whichever
    /// assemblies happen to be loaded, so RimWorld only requires DROIDWORKS
    /// itself to be active — exactly what the FindMod gate already guarantees).
    /// Once RSW_JawaIon_Stun's severity reaches its FLOOR "overloaded" stage
    /// (minSeverity 0.5, the same Consciousness cap as the top 0.9 stage —
    /// DROIDWORKS_ION_GUARD_1, HediffDefs_JawaIonStun.xml), a pawn whose
    /// RaceProps.FleshType is RSW_DW_FleshType_Droid gets swapped over: the
    /// buildup hediff is removed and RSW_DW_PoweredDown is applied in its place, so
    /// the droid stays down until Recipe_RebootDroid reboots it, matching every
    /// other route into state 3.
    /// </summary>
    public class HediffComp_IonOverloadsDroid : HediffComp
    {
        // RSW_JawaIon_Stun's DROIDWORKS_ION_GUARD_1 FLOOR stage minSeverity, NOT
        // its top "overloaded" stage (0.9). Both stages cap Consciousness
        // identically, but the floor stage is where the droid actually becomes
        // Downed - fixed 2026-09-02 (opus code review) after the original 0.9
        // threshold left a window (Downed at 0.5, converted only at 0.9) where
        // combat naturally stops (AI won't keep hitting a Downed target) and the
        // buildup can plateau and decay back out before ever reaching 0.9,
        // self-recovering exactly like the bug this comp exists to prevent.
        private const float OverloadThreshold = 0.5f;

        public override void CompPostTick(ref float severityAdjustment)
        {
            if (parent.Severity < OverloadThreshold)
            {
                return;
            }

            Pawn pawn = parent.pawn;
            // Fixed 2026-09-02: was gated on GetModExtension<DroidworksExtension>(),
            // present only on DW_Family_* descendants - every non-Droidworks droid
            // race (Droid Depot, KotOR, JDS, ...) silently failed this gate with no
            // log. Key on the actual "is this a droid" signal instead.
            if (pawn?.RaceProps?.FleshType != DroidworksDefOf.RSW_DW_FleshType_Droid)
            {
                return;
            }

            if (pawn.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_PoweredDown))
            {
                return; // already powered down some other way (e.g. Need_Power) — leave it alone
            }

            // Fixed 2026-09-02: add DW_PoweredDown BEFORE removing parent. The old
            // order left the droid with no Consciousness-capping hediff for one
            // instant, which un-downs it mid-conversion (CheckForStateChange fires
            // a "no longer downed" message and can abort an in-flight rescue/
            // capture job on this exact pawn) before the replacement hediff lands.
            pawn.health.AddHediff(DroidworksDefOf.RSW_DW_PoweredDown);
            pawn.health.RemoveHediff(parent);
        }
    }
}
