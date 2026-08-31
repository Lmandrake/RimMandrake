using UnityEngine;
using Verse;

namespace RimMandrake.Visibility
{
    /// <summary>
    /// COLONY_VISIBILITY_BUILD_1, rehomed from mandrake.rut.doctrine's
    /// COLONY_VISIBILITY_STAT_1 build (src/RimUtinni/Doctrine/Source/DoctrineCore/
    /// ColonyVisibility.cs) into its own dedicated mod per the item's own
    /// packageId (mandrake.rm.visibility) - the mechanism itself (a 0-100
    /// dial + band ladder + threat-point multiplier) is engine-generic; the
    /// Ash'karr-flavored triggers that would feed it (Ishko/Sh'kaar/Ta'Baa/
    /// Ozzik hooks) are still entirely TODO and would live in a RUT-tier
    /// content pack that calls into Adjust() here.
    ///
    /// Tracks the shared 0-100 Colony Visibility dial
    /// (design/Jawa/worldbuilding/colony_visibility_stat.md §1-3) as a
    /// GameComponent - not a MapComponent, because the gravship's own map
    /// persists across launches (a MapComponent would never reset).
    /// Registered automatically by Verse.Game.FillComponents() via
    /// reflection over GameComponent subclasses - no Def/XML needed.
    /// </summary>
    public class GameComponent_ColonyVisibility : GameComponent
    {
        public float shipVisibility = 10f; // Hidden-band start, per design doc §5 skeleton

        /// <summary>
        /// Sh'kaar's escalation-meter seam (design doc §2 "multiplies it,
        /// does not add to it"). No-op (1f) until Sh'kaar's meter is tracked
        /// in code (Ninefold's own TODO) - wire when that lands.
        /// </summary>
        public float ShkaarEscalationMultiplier = 1f;

        public GameComponent_ColonyVisibility(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref shipVisibility, "shipVisibility", 10f);
            Scribe_Values.Look(ref ShkaarEscalationMultiplier, "shkaarEscalationMultiplier", 1f);
        }

        public VisibilityBand Band => BandFor(shipVisibility);

        public static VisibilityBand BandFor(float v)
        {
            if (v < 20f) return VisibilityBand.Hidden;
            if (v < 40f) return VisibilityBand.Discreet;
            if (v < 60f) return VisibilityBand.Noticed;
            if (v < 80f) return VisibilityBand.Marked;
            return VisibilityBand.Exposed;
        }

        /// <summary>
        /// The one generic mutator - every raise/lower hook in the design
        /// doc's §2 table (once its trigger exists in code) should call
        /// this. delta may be positive or negative; reason is the matrix
        /// citation, logged on a band crossing (dev-mode only) - the real
        /// F17-signed letter this design doc's §3 wants is not built.
        /// </summary>
        public void Adjust(float delta, string reason)
        {
            VisibilityBand before = Band;
            shipVisibility = Mathf.Clamp(shipVisibility + delta, 0f, 100f);
            if (Prefs.DevMode && Band != before)
            {
                Log.Message($"[ColonyVisibility] {before} -> {Band} ({shipVisibility:F1}): {reason}");
            }
        }

        /// <summary>
        /// Ta'Baa's launch reset (design doc §2 "Resets it" / §5 skeleton).
        /// Wired for real - see ColonyVisibilityRaidPatch's postfix on
        /// GravshipUtility.GenerateGravship. Floor is illustrative (5-15,
        /// owner's call whether a snatched-free launch should reset lower
        /// than a routine one), not tuned.
        /// </summary>
        public void ResetOnLaunch()
        {
            float before = shipVisibility;
            shipVisibility = Mathf.Clamp(shipVisibility * 0.15f, 5f, 15f);
            if (Prefs.DevMode)
            {
                Log.Message($"[ColonyVisibility] launch reset: {before:F1} -> {shipVisibility:F1}");
            }
        }

        /// <summary>
        /// Illustrative S/M/L deltas, the design doc's own convention (§2
        /// magnitudes, matching divine_satiation_engine.md §8b). Not tuned -
        /// deferred to a throwaway-save test rig. Vocabulary for future
        /// wiring code, not applied anywhere yet.
        /// </summary>
        public const float DeltaSmall = 3f;
        public const float DeltaMedium = 8f;
        public const float DeltaLarge = 20f;
    }

    public enum VisibilityBand
    {
        Hidden,
        Discreet,
        Noticed,
        Marked,
        Exposed
    }
}
