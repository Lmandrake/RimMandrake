using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// The guarded healing pass shared by the tank (CompBactaImmersion, a continuous
    /// 250-tick-interval loop) and the field consumables (CompUseEffect_BactaHeal, a single
    /// burst dose) — BACTA_SIDE_ITEMS_1's own brief: "reuse that logic at a smaller,
    /// item-scale dose rather than reinventing it." Extracted from
    /// CompBactaImmersion.TryHealPawn exactly as it stood at BACTA_TANK_CORE_1's live-tested
    /// state (see that item's 2026-09-24 "live test v2" entry); the tank's own call site
    /// passes precisely the values it always did, so this refactor changes nothing about the
    /// tank's already live-proven behaviour.
    ///
    /// Both ruled laws (BACTA_TANK_CORE_1 card 2, owner verbatim) live here once, not twice:
    ///   - bacta never regrows anything — Hediff_MissingPart is skipped outright;
    ///   - bacta never touches the brain or the mind — any hediff on the
    ///     ConsciousnessSource-tagged part is skipped outright.
    /// </summary>
    public static class BactaHealingUtility
    {
        private static readonly List<Hediff> tmpHediffs = new List<Hediff>();

        /// <summary>
        /// Applies one guarded healing pass to <paramref name="pawn"/>. Returns true if
        /// anything a player would call healing actually happened.
        /// </summary>
        public static bool ApplyHealingDose(Pawn pawn, float woundHeal, float scarHeal,
            float tendQuality, float immunityGain, bool scarErasureEnabled, bool infectionAssistEnabled)
        {
            if (pawn?.health == null || pawn.Dead)
            {
                return false;
            }

            bool did = false;

            tmpHediffs.Clear();
            tmpHediffs.AddRange(pawn.health.hediffSet.hediffs);

            for (int i = 0; i < tmpHediffs.Count; i++)
            {
                Hediff hediff = tmpHediffs[i];
                if (hediff == null || hediff.pawn != pawn)
                {
                    continue;
                }

                // ---- LAW: bacta never regrows anything. -------------------------------
                if (hediff is Hediff_MissingPart)
                {
                    continue;
                }

                // ---- LAW: physical only, never the brain and never the mind. ----------
                if (IsBrainOrMind(hediff))
                {
                    continue;
                }

                if (hediff is Hediff_Injury injury)
                {
                    if (injury.IsPermanent())
                    {
                        // Scars and permanent physical injuries: slow erasure (tank) or, at
                        // item scale, usually not enabled at all — see CompUseEffect_BactaHeal.
                        if (!scarErasureEnabled)
                        {
                            continue;
                        }

                        injury.Severity -= scarHeal;
                        did = true;

                        if (injury.Severity <= 0.001f)
                        {
                            pawn.health.RemoveHediff(injury);
                        }
                        continue;
                    }

                    // Fresh wound, burn, or damaged organ (an organ injury is a
                    // Hediff_Injury whose Part is the organ — same branch, by design).
                    if (injury.TendableNow(ignoreTimer: true) && !injury.IsTended())
                    {
                        injury.Tended(tendQuality, tendQuality);
                        did = true;
                    }

                    if (injury.Severity > 0f)
                    {
                        injury.Heal(woundHeal);
                        did = true;

                        if (injury.Severity <= 0.001f)
                        {
                            pawn.health.RemoveHediff(injury);
                        }
                    }
                    continue;
                }

                // ---- Infections: only where medicine would have helped. ---------------
                if (!infectionAssistEnabled)
                {
                    continue;
                }

                if (hediff.TryGetComp<HediffComp_TendDuration>() == null)
                {
                    continue;
                }

                if (!hediff.def.PossibleToDevelopImmunityNaturally())
                {
                    continue;
                }

                if (hediff.TendableNow(ignoreTimer: true) && !hediff.IsTended())
                {
                    hediff.Tended(tendQuality, tendQuality);
                    did = true;
                }

                if (BoostImmunity(pawn, hediff, immunityGain))
                {
                    did = true;
                }
            }

            tmpHediffs.Clear();
            return did;
        }

        /// <summary>
        /// Cheap read-only scan: would ApplyHealingDose find anything to do at all? Used so a
        /// field item's "Use"/"Apply" option can grey itself out rather than fire on nothing
        /// (the same UX CompUseEffect_FixWorstHealthCondition gives MechSerumHealer, but
        /// scoped to what THIS mechanism can actually touch).
        /// </summary>
        public static bool HasHealableCondition(Pawn pawn, bool scarErasureEnabled, bool infectionAssistEnabled)
        {
            if (pawn?.health?.hediffSet == null)
            {
                return false;
            }

            List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
            for (int i = 0; i < hediffs.Count; i++)
            {
                Hediff hediff = hediffs[i];
                if (hediff is Hediff_MissingPart || IsBrainOrMind(hediff))
                {
                    continue;
                }

                if (hediff is Hediff_Injury injury)
                {
                    if (injury.IsPermanent())
                    {
                        if (scarErasureEnabled)
                        {
                            return true;
                        }
                        continue;
                    }
                    if (injury.Severity > 0f)
                    {
                        return true;
                    }
                    continue;
                }

                if (!infectionAssistEnabled)
                {
                    continue;
                }
                if (hediff.TryGetComp<HediffComp_TendDuration>() == null)
                {
                    continue;
                }
                if (hediff.def.PossibleToDevelopImmunityNaturally())
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// Nudges the pawn's real immunity record for this disease. Deliberately reaches
        /// ImmunityListForReading rather than GetImmunityRecord: the latter can hand back a
        /// freshly-built detached record for gene-granted immunity, and writing to that would
        /// look like it worked and do nothing.
        /// </summary>
        private static bool BoostImmunity(Pawn pawn, Hediff hediff, float amount)
        {
            if (amount <= 0f || pawn.health.immunity == null)
            {
                return false;
            }

            List<ImmunityRecord> records = pawn.health.immunity.ImmunityListForReading;
            for (int i = 0; i < records.Count; i++)
            {
                ImmunityRecord record = records[i];
                if (record.hediffDef != hediff.def)
                {
                    continue;
                }
                if (record.immunity >= 1f)
                {
                    return false;
                }
                record.immunity = Mathf.Clamp01(record.immunity + amount);
                return true;
            }
            return false;
        }

        /// <summary>
        /// True for anything bacta must not touch on neurological grounds. Structural, not by
        /// defName: the brain is the body part tagged ConsciousnessSource in every body def,
        /// including modded and alien ones.
        /// </summary>
        private static bool IsBrainOrMind(Hediff hediff)
        {
            BodyPartRecord part = hediff.Part;
            if (part?.def?.tags == null)
            {
                return false;
            }
            return part.def.tags.Contains(BodyPartTagDefOf.ConsciousnessSource);
        }
    }
}
