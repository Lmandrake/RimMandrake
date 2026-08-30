using Verse;

namespace Droidworks
{
    public class HediffCompProperties_IonOverloadsDroid : HediffCompProperties
    {
        public HediffCompProperties_IonOverloadsDroid() =>
            compClass = typeof(HediffComp_IonOverloadsDroid);
    }

    /// <summary>
    /// DROIDWORKS_POWEREDDOWN_NOT_WIRED_1. Wired onto JawaIonWeapons' JawaIon_Stun
    /// via Patches/IonBuildup_PowersDownDroid.xml (FindMod-gated on "Jawa Ion
    /// Weapons (local)" — a no-op if that mod isn't active).
    ///
    /// Until DROIDWORKS_ISFLESH_RELATIONS_CRASH_1 lands, DW_ race droids inherit
    /// Human's organic fleshType (see Races_Base.xml's header note), so
    /// DamageWorker_IonBuildup.Apply() treats them exactly like a flesh pawn:
    /// JawaIon_Stun accumulates and its own capMods cap Consciousness, downing the
    /// pawn — but that hediff self-decays (HediffCompProperties_SeverityPerDay),
    /// so an ion-overloaded droid just wobbles back up on its own like a person
    /// would, never touching DW_PoweredDown (the persistent, reboot-only state
    /// the rest of the droid state machine — Need_Power, Recipe_RebootDroid — is
    /// built around).
    ///
    /// This comp closes that gap without any cross-assembly build dependency
    /// (JawaIonWeapons.dll never references Droidworks.dll or vice versa; the
    /// XML <comps> Class="" attribute resolves by reflection across whichever
    /// assemblies happen to be loaded, so RimWorld only requires DROIDWORKS
    /// itself to be active — exactly what the FindMod gate already guarantees).
    /// Once JawaIon_Stun's severity reaches its own top "overloaded" stage
    /// (minSeverity 0.9, HediffDefs_JawaIonStun.xml), a pawn that carries a
    /// DroidworksExtension (i.e. is a DW_ race droid) gets swapped over: the
    /// buildup hediff is removed and DW_PoweredDown is applied in its place, so
    /// the droid stays down until Recipe_RebootDroid reboots it, matching every
    /// other route into state 3.
    /// </summary>
    public class HediffComp_IonOverloadsDroid : HediffComp
    {
        private const float OverloadThreshold = 0.9f; // JawaIon_Stun's own top "overloaded" stage minSeverity

        public override void CompPostTick(ref float severityAdjustment)
        {
            if (parent.Severity < OverloadThreshold)
            {
                return;
            }

            Pawn pawn = parent.pawn;
            if (pawn?.def?.GetModExtension<DroidworksExtension>() == null)
            {
                return;
            }

            if (pawn.health.hediffSet.HasHediff(DroidworksDefOf.DW_PoweredDown))
            {
                return; // already powered down some other way (e.g. Need_Power) — leave it alone
            }

            pawn.health.RemoveHediff(parent);
            pawn.health.AddHediff(DroidworksDefOf.DW_PoweredDown);
        }
    }
}
