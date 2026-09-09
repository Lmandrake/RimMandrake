using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// The curated per-def override (item ruling #2: "a curated developer
    /// override (yes/no per def)"). Attach to a race ThingDef's
    /// &lt;modExtensions&gt; to move it off the bodySize-only default:
    ///
    ///   forceEnabled unset / omitted -&gt; auto: tier decided by bodySize alone.
    ///   forceEnabled = true          -&gt; force IN even if bodySize is below
    ///                                    the T1 floor (a dense small thing
    ///                                    opts in; floors at T1, or higher if
    ///                                    its bodySize genuinely qualifies).
    ///   forceEnabled = false         -&gt; force OUT regardless of bodySize (a
    ///                                    light big thing opts out entirely).
    /// </summary>
    public class RM_TitanicExtension : DefModExtension
    {
        public bool? forceEnabled;
    }
}
