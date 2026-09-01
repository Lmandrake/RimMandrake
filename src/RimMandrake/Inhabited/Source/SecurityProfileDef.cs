using System.Collections.Generic;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// A faction's gate-search posture -- SETTLEMENT_VISIT_LOOP_1.
    ///
    /// Spec (design/Jawa/ownership_settlement_spec.md, "the event spine"): "Gate
    /// searches replace Visit Settlements' omniscient departure check: a faction
    /// searches leavers only if its profile says so (Empire pats down, Junkers
    /// wave through)."
    ///
    /// Deliberately thin. This v1 stub carries only whether and how often a
    /// search fires; it does NOT inspect the leaving party's inventory, does not
    /// read claim/perception state, and has no consequence beyond a log line and
    /// a casing record. Real per-faction tuning (search severity, what a search
    /// actually finds, confiscation, social fallout) is RimUtinni data landing
    /// with SETTLEMENT_VERBS_WAVE_1 -- this def only proves the HOOK exists and
    /// is wired to something a manifest can name.
    /// </summary>
    public class SecurityProfileDef : Def
    {
        /// <summary>Whether this faction ever searches leavers at all. False
        /// (wave through) is the correct default for most of the roster --
        /// only a handful of factions (the Empire) pat anyone down.</summary>
        public bool searchesLeavers;

        /// <summary>Chance a search actually triggers on any one departure,
        /// given searchesLeavers is true. 1.0 = every time.</summary>
        public float searchChance = 1f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (searchChance < 0f || searchChance > 1f)
            {
                yield return "searchChance out of 0-1: " + searchChance;
            }
        }
    }
}
