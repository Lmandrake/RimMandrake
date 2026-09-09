using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// The eight chassis families, by name, for XML that has to talk about a
    /// family. The integer values ARE DroidworksExtension.chassisClass's own
    /// documented mapping ("0 labour 1 protocol 2 astromech 3 battle 4 heavy
    /// 5 probe 6 power 7 primitive", DroidworksModExtension.cs) - the same
    /// house pattern DroidFormatTier already uses, where the enum's integer
    /// values ARE the hediff severity ladder minus one.
    ///
    /// Why an enum at all when CompDWHeadDropper/CompDWPartDropper switch on
    /// the raw int: the per-family weights below are a table a DESIGNER edits
    /// in XML, and "&lt;chassis&gt;Protocol&lt;/chassis&gt;" is reviewable where
    /// "&lt;chassisClass&gt;1&lt;/chassisClass&gt;" is not. DroidworksExtension's
    /// field is deliberately NOT retyped to this enum: it is read by three
    /// other files and written by gen_droidworks_defs.py, and a retype there
    /// is a refactor, not this packet. ChassisOf() below is the ONE place the
    /// int becomes the enum.
    /// </summary>
    public enum DroidChassis
    {
        Labour = 0,
        Protocol = 1,
        Astromech = 2,
        Battle = 3,
        Heavy = 4,
        Probe = 5,
        Power = 6,
        Primitive = 7
    }

    /// <summary>One family's draw weight for one idiosyncrasy trait.</summary>
    public class ChassisTraitWeight
    {
        public DroidChassis chassis;
        public float weight = 1f;
    }

    /// <summary>
    /// DROIDWORKS_SERVICE_RECORD_DRIFT_1 (packet E2). Marker DefModExtension
    /// declaring a TraitDef to be an ACCRETING IDIOSYNCRASY - something a droid
    /// grows into over a long unwiped service life - and carrying that trait's
    /// per-chassis-family draw weights.
    ///
    /// Marker-on-the-def rather than a defName list in C#, for exactly the
    /// reason DroidworksHardwareQuirks (packet B10) gives for its own
    /// HardwareQuirkExtension: the pool must be answerable as a QUESTION in two
    /// places at once - "which traits may drift in?" and "which traits must a
    /// memory wipe strip?" - and a marker on the def cannot drift out of sync
    /// with itself. A later packet adds an idiosyncrasy with XML alone.
    ///
    /// 🔴 An idiosyncrasy is NOT a hardware quirk, and nothing may carry both
    /// markers. They are opposite mechanisms:
    ///   quirk (B10)        accretes from wipe SEVERITY, permanent, never reset
    ///   idiosyncrasy (E2)  accretes from TIME UNWIPED, and a wipe erases it
    /// </summary>
    public class DroidIdiosyncrasyExtension : DefModExtension
    {
        /// <summary>Weight for any family not named in chassisWeights.</summary>
        public float defaultWeight = 1f;

        /// <summary>
        /// Per-family overrides. Deliberately a plain List of a plain class -
        /// no LoadDataFromXmlCustom anywhere near it, so ordinary &lt;li&gt;
        /// entries are correct here (see rimworld-custom-loader-li-trap for
        /// the field shape where they are NOT).
        /// </summary>
        public List<ChassisTraitWeight> chassisWeights;

        public float WeightFor(DroidChassis chassis)
        {
            if (chassisWeights != null)
            {
                for (int i = 0; i < chassisWeights.Count; i++)
                {
                    if (chassisWeights[i].chassis == chassis) return chassisWeights[i].weight;
                }
            }
            return defaultWeight;
        }
    }

    /// <summary>
    /// The idiosyncrasy pool, the chassis-weighted draw, and the wipe erasure.
    ///
    /// ⚠️ Same caveat B10's DroidworksHardwareQuirks carries, inverted: nothing
    /// in the engine marks a trait as "erasable by a wipe". What makes the
    /// erasure real is that Recipe_DWMemoryWipe calls NotifyWiped below before
    /// it re-rolls anything. Any future route that wipes or reformats a droid
    /// must call it too, or a wiped droid keeps a personality it earned in a
    /// life it no longer has.
    /// </summary>
    public static class DroidServiceRecordUtility
    {
        public static bool IsIdiosyncrasy(TraitDef def) =>
            def != null && def.HasModExtension<DroidIdiosyncrasyExtension>();

        public static bool IsIdiosyncrasy(Trait trait) => trait != null && IsIdiosyncrasy(trait.def);

        /// <summary>
        /// Every TraitDef marked as an accreting idiosyncrasy. Not cached, for
        /// B10's reason: a handful of defs, read at most once per droid per
        /// in-game day, and a cache could go stale across a def reload.
        /// </summary>
        public static IEnumerable<TraitDef> Pool =>
            DefDatabase<TraitDef>.AllDefsListForReading.Where(IsIdiosyncrasy);

        /// <summary>
        /// This pawn's chassis family. Reads DroidworksExtension exactly the way
        /// CompDWHeadDropper does - LastOrDefault, because XML inheritance
        /// APPENDS modExtensions and the race's own copy always sorts after the
        /// family abstract's inherited one - and falls back to Labour (0), the
        /// same default those two comps already use.
        /// </summary>
        public static DroidChassis ChassisOf(Pawn pawn)
        {
            DroidworksExtension ext = pawn?.def?.modExtensions?.OfType<DroidworksExtension>().LastOrDefault();
            return (DroidChassis)(ext?.chassisClass ?? 0);
        }

        public static int AccretedCount(Pawn pawn) =>
            pawn?.story?.traits == null ? 0 : pawn.story.traits.allTraits.Count(IsIdiosyncrasy);

        /// <summary>
        /// Adds one idiosyncrasy the pawn does not already carry, drawn by this
        /// chassis family's weights. Returns the trait gained, or null if the
        /// pool is exhausted (every idiosyncrasy already held, or every
        /// remaining one at weight 0 for this family).
        /// </summary>
        public static Trait TryAccreteIdiosyncrasy(Pawn pawn)
        {
            if (pawn?.story?.traits == null) return null;

            DroidChassis chassis = ChassisOf(pawn);
            List<TraitDef> candidates = Pool
                .Where(d => !pawn.story.traits.HasTrait(d))
                // Defensive: the shipped idiosyncrasies declare no exclusionTags
                // and no conflictingTraits (same rule the quirk pool follows -
                // they must be able to accrete alongside each other and
                // alongside whatever ordinary traits the droid already has), so
                // this should never exclude anything today. It is here so a
                // later XML-only addition that DOES conflict cannot produce an
                // engine-level trait collision.
                .Where(d => !pawn.story.traits.allTraits.Any(t => d.ConflictsWith(t)))
                .ToList();
            if (candidates.Count == 0) return null;

            TraitDef chosen = candidates.RandomElementByWeightWithFallback(
                d => WeightOf(d, chassis), null);
            if (chosen == null) return null;

            // degree 0 (every idiosyncrasy is single-degree), forced: true - the
            // same shape DroidworksHardwareQuirks.TryGainRandomQuirk and
            // DroidAssembly.SpawnDroid already use for a deliberately granted
            // rather than rolled trait.
            Trait gained = new Trait(chosen, 0, true);
            pawn.story.traits.GainTrait(gained);
            return gained;
        }

        private static float WeightOf(TraitDef def, DroidChassis chassis)
        {
            DroidIdiosyncrasyExtension ext = def.GetModExtension<DroidIdiosyncrasyExtension>();
            if (ext == null) return 0f;
            float w = ext.WeightFor(chassis);
            // Clamped without Mathf on purpose: this file has no other reason to
            // reference UnityEngine, and a negative weight would make
            // RandomElementByWeight's running total nonsense rather than just
            // making the trait rare.
            return w < 0f ? 0f : w;
        }

        /// <summary>
        /// What a memory wipe does to the service record: every accreted
        /// idiosyncrasy is REMOVED, and the clock goes back to zero.
        ///
        /// 🔑 Why the traits go and do not merely stop accruing. Three reasons,
        /// two of them already written down before this packet existed:
        ///  1. B10 (Recipe_DWMemoryWipe.ApplyOnPawn) left the call site for this
        ///     with the comment "When the behavior triad's 'EXPERIENCED' tier
        ///     lands as real hediffs, this is where they get cleared." The
        ///     question was answered there; this is the answer being honoured.
        ///  2. The wipe ALREADY removes every non-quirk trait
        ///     (Recipe_DWMemoryWipe.RandomizeTraits) - keeping idiosyncrasies
        ///     through a wipe would have meant deliberately marking them as
        ///     exempt, i.e. quietly making them quirks, which is the one
        ///     conflation B10 and this packet must not make.
        ///  3. The design's own framing (droid_system_build_spec.md unit 11:
        ///     "long-unwiped droids are PEOPLE"). If a wipe left the personality
        ///     standing it would not be a wipe, and the whole moral weight the
        ///     unit is built around - that wiping a long-served droid destroys
        ///     someone - would evaporate.
        ///
        /// Called BEFORE RandomizeTraits so the idiosyncrasies are gone by the
        /// time vanilla counts how many ordinary traits to re-roll: a droid that
        /// came out of the factory with 2 traits and grew 3 idiosyncrasies comes
        /// out of the wipe with 2 traits again, not 5.
        /// </summary>
        public static void NotifyWiped(Pawn pawn)
        {
            if (pawn == null) return;

            if (pawn.story?.traits != null)
            {
                List<Trait> accreted = pawn.story.traits.allTraits.Where(IsIdiosyncrasy).ToList();
                foreach (Trait trait in accreted)
                {
                    pawn.story.traits.RemoveTrait(trait);
                }
            }

            pawn.TryGetComp<CompDWServiceRecord>()?.ResetClock();
        }
    }
}
