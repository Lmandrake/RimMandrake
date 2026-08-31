using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Doctrine
{
    /// <summary>
    /// COLONY_VISIBILITY_STAT_1 safe core. Tracks the shared 0-100 Colony
    /// Visibility dial (design/Jawa/worldbuilding/colony_visibility_stat.md
    /// §1-3) as a GameComponent - not a MapComponent, because the gravship's
    /// own map persists across launches (a MapComponent would never reset).
    ///
    /// Registered automatically by Verse.Game.FillComponents() via reflection
    /// over GameComponent subclasses (AllSubclassesNonAbstract, confirmed via
    /// RimSage read of Source/Verse/Game.cs) - no Def/XML needed.
    ///
    /// WHAT IS REAL vs TODO (per the item's own instruction not to invent
    /// detection logic for deeds/boons/curses that have no code yet - the
    /// nine-god satiation engine itself is design-doc-only; confirmed no C#
    /// under src/ referenced any of the nine gods or satiation before this
    /// item):
    ///
    ///   REAL, wired: Adjust() (the generic mutator), the band ladder,
    ///     ExposeData persistence, and ResetOnLaunch() - which IS wired to a
    ///     real Harmony postfix on GravshipUtility.GenerateGravship
    ///     (see ColonyVisibilityRaidPatch.cs) - the one hook in the design
    ///     doc's §2 table that is both a real, always-firing vanilla event
    ///     and unambiguous as specced (Ta'Baa's launch reset).
    ///
    ///   TODO, not wired to anything yet: every OTHER raise/lower hook in the
    ///     design doc's §2 table (spotted/raided at home, challenge
    ///     broadcasts, Renown, THE SHAMING, Overcurrent, melee fighting,
    ///     flare-lighting, ambush kills, undetected-raid survival, concealed
    ///     construction, darkness, blackout reign, Unseen Berth, the
    ///     Unburdening rite). Each needs either a new Harmony detection patch
    ///     for a vanilla event with no discrete existing signal, or the
    ///     not-yet-built satiation engine's own deed/boon/curse firing system
    ///     to call into - and the design doc's own magnitudes for these are
    ///     explicitly "illustrative, not tuned" (item file "decisions owed"
    ///     #3). Adjust() is ready to be called the moment any of those exist;
    ///     DeltaSmall/Medium/Large below give the doc's own vocabulary for
    ///     that future wiring. ShkaarEscalationMultiplier is a similar seam
    ///     (default 1f, no-op) for when Sh'kaar's escalation meter (matrix
    ///     §3⑧) gets built.
    ///
    ///   NOT modeled at all (structurally different from a delta, flagged
    ///     rather than guessed): Orange Dusk / The Long Shadow (§2's boon
    ///     rows) are decay-RATE modifiers ("small detection-clock slow",
    ///     "detection clock pauses at night"), not one-shot Adjust() calls -
    ///     they need a modifier-list mechanism this pass does not build.
    /// </summary>
    public class GameComponent_ColonyVisibility : GameComponent
    {
        public float shipVisibility = 10f; // Hidden-band start, per design doc §5 skeleton

        /// <summary>
        /// Sh'kaar's escalation-meter seam (design doc §2 "multiplies it,
        /// does not add to it"). No-op (1f) until Sh'kaar's meter is tracked
        /// in code - TODO, wire when that lands. Read by
        /// ColonyVisibilityRaidPatch.RaidThreatPointsNow.
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
        /// The one real, generic mutator - every raise/lower hook in the
        /// design doc's §2 table (once its trigger exists in code) should
        /// call this. delta may be positive or negative; reason is the
        /// matrix citation, logged on a band crossing for now (dev-mode
        /// only) - the real F17-signed letter this design doc's §3 wants
        /// is not built; F17's letter/interface layer doesn't exist in code
        /// yet either.
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
        /// owner's call per the item's "decisions owed" #4: whether a
        /// snatched-free launch should reset lower than a routine one), not
        /// tuned.
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
        /// deferred to a throwaway-save test rig per that doc's §9/§10.
        /// Vocabulary for future wiring code, not applied anywhere yet.
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
