using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S2 spike (sump_kit_spec.md "the dig lottery").
    // A lightweight Def, not a ThingSetMakerDef: the spec's own ❓ asked
    // whether vanilla ThingSetMakerDef composes weighted-outcome-with-side-
    // effects (a trap row that telegraphs and detonates, not just a yielded
    // Thing) cleanly enough to replace this. It does not — ThingSetMakerDef's
    // whole contract is "produce a List<Thing>", with no seam for a row that
    // instead schedules a fuse and calls GenExplosion.DoExplosion. A custom
    // Def with a `isTrap` row flag is smaller than bolting a side-effect onto
    // something that wasn't built for one. Resolves that ❓: not a ThingSetMaker,
    // by design, not by oversight.
    //
    // Ban #1 as arithmetic (sheet §6, ruled sump_kit_spec.md hard-ban table):
    // in every stratum, weight(trap) > weight(era remains) > 0, and no
    // whole-body era row exists. ConfigErrors below is the linter this spec
    // promised — it fires at def-load, not at build-review time, so a content
    // author cannot ship a stratum that quietly violates the ban.
    public class RM_LotteryTableDef : Def
    {
        /// <summary>One row per stratum depth (index 0 = shallowest). Each
        /// stratum lists its own weighted rows — depth already changes both
        /// rarity and trap weight per the spec (S2 "Depth"), so this is a
        /// list-of-lists rather than one flat table with a depth multiplier;
        /// the multiplier version can replace this at build if authoring by
        /// hand proves easier, this is the spike's own call, not a lore fact.</summary>
        public List<RM_LotteryStratum> strata = new List<RM_LotteryStratum>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (strata.NullOrEmpty())
            {
                yield return "RM_LotteryTableDef " + defName + " has no strata.";
                yield break;
            }

            for (int i = 0; i < strata.Count; i++)
            {
                RM_LotteryStratum stratum = strata[i];
                if (stratum.rows.NullOrEmpty())
                {
                    yield return $"RM_LotteryTableDef {defName} stratum {i} has no rows.";
                    continue;
                }

                float trapWeight = 0f;
                float eraRemainsWeight = 0f;
                bool hasTrapRow = false;
                bool hasEraRemainsRow = false;

                foreach (RM_LotteryRow row in stratum.rows)
                {
                    if (row.isWholeBodyEraRemains)
                    {
                        yield return $"RM_LotteryTableDef {defName} stratum {i}: row '{row.rowLabel}' is flagged isWholeBodyEraRemains — ban #1 (the_sump.md, sump_kit_spec.md hard-ban table) forbids any whole-body Assailant/Rakatan row in a Sump dig table.";
                    }

                    if (row.isTrap)
                    {
                        hasTrapRow = true;
                        trapWeight += row.weight;
                    }
                    else if (row.isEraRemains)
                    {
                        hasEraRemainsRow = true;
                        eraRemainsWeight += row.weight;
                    }
                }

                if (hasEraRemainsRow && !hasTrapRow)
                {
                    yield return $"RM_LotteryTableDef {defName} stratum {i}: era-remains row present with no trap row — ban #1 requires weight(trap) > weight(era remains) > 0 in every stratum.";
                }
                else if (hasEraRemainsRow && trapWeight <= eraRemainsWeight)
                {
                    yield return $"RM_LotteryTableDef {defName} stratum {i}: trap weight ({trapWeight}) does not exceed era-remains weight ({eraRemainsWeight}) — ban #1 violation (sump_kit_spec.md: 'trap rows outweigh both remains rows in every stratum').";
                }
            }
        }
    }

    public class RM_LotteryStratum
    {
        public List<RM_LotteryRow> rows = new List<RM_LotteryRow>();
    }

    public class RM_LotteryRow
    {
        public string rowLabel;

        /// <summary>Relative weight within this stratum's roll. Ban #1 is
        /// checked as a weight inequality against this field — see
        /// RM_LotteryTableDef.ConfigErrors.</summary>
        public float weight = 1f;

        public bool isTrap;

        /// <summary>Partial/GM-tier era remains — never a whole body. See
        /// isWholeBodyEraRemains for the thing this flag must never be true
        /// alongside.</summary>
        public bool isEraRemains;

        /// <summary>Must never be true on a shipped row — content-authoring
        /// guard for ban #1, not a mechanic. Existing only so ConfigErrors
        /// has something to catch if it ever is.</summary>
        public bool isWholeBodyEraRemains;

        public ThingDef thingDef;

        public IntRange countRange = new IntRange(1, 1);
    }
}
