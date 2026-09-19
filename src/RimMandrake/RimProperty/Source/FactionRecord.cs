using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Property
{
    // Spec item 6: "Consequences read the FACTION RECORD, never the event:
    // prices cool, guards shadow, a fence recognizes a serial, a bounty, a
    // recovery invoice, a raid. A crime nobody filed costs nothing." This
    // class IS that surface — the aggregate a future system (prices,
    // guards, bounties) queries. It never mutates itself on a schedule;
    // GetSuspicion computes the current propagated value from the raw
    // witness entries at call time, using PropertyTuning's generic
    // propagation rate until RimUtinni supplies a per-faction one.
    public class FactionRecord : IExposable
    {
        public Faction Faction;
        private List<WitnessEntry> entries = new List<WitnessEntry>();

        public FactionRecord()
        {
        }

        public FactionRecord(Faction faction)
        {
            Faction = faction;
        }

        public void RegisterWitness(ClaimantRef suspect, float confidence, int tick)
        {
            if (suspect.Kind != ClaimantKind.Pawn) return; // only individuals can be suspects
            // PROPERTY_SCRIBE_AND_WITNESS_INVARIANTS_1: GetSuspicion's lazy prune
            // is the only pruner, and nothing calls GetSuspicion yet (the
            // consequence-reader layer is unbuilt) - so entries grew unbounded
            // on any live campaign despite this class's own comment claiming
            // otherwise. Pruning here too means entries never outlive
            // SuspicionHalfLifeDays even with zero readers.
            PruneFullyDecayedEntries(tick);
            entries.Add(new WitnessEntry(suspect, confidence, tick));
        }

        // How much of this faction's accumulated knowledge about `suspect`
        // has propagated "to the top" by `nowTick` — 0..1, lazily computed,
        // never ticked. Consequences (not built by this fabric) read this.
        //
        // Each entry also decays linearly to zero over
        // PropertyTuning.SuspicionHalfLifeDays from its witness tick — without
        // this an entry's contribution never falls, and a couple of witnessed
        // events permanently saturate suspicion at 1.0. Entries that have
        // fully decayed are lazily pruned here (never on a scheduled tick),
        // so `entries` doesn't grow unbounded for the life of the save.
        public float GetSuspicion(ClaimantRef suspect, int nowTick, float propagationRatePerDay = PropertyTuning.DefaultPropagationRatePerDay)
        {
            PruneFullyDecayedEntries(nowTick);

            float total = 0f;
            for (int i = 0; i < entries.Count; i++)
            {
                WitnessEntry e = entries[i];
                if (!e.Suspect.Equals(suspect)) continue;

                float daysElapsed = (nowTick - e.TimestampTicks) / (float)GenDate.TicksPerDay;
                float propagated = Mathf.Clamp01(daysElapsed * propagationRatePerDay);
                float decay = Mathf.Clamp01(1f - daysElapsed / PropertySettings.suspicionHalfLifeDays);
                total += e.Confidence * propagated * decay;
            }
            return Mathf.Clamp01(total);
        }

        // Drops entries whose decayed contribution has reached ~0 for every
        // suspect, regardless of the propagation rate used to read them —
        // decay is monotonic in elapsed time alone, so once an entry passes
        // the configured half-life it contributes nothing to any future
        // read. Must read PropertySettings.suspicionHalfLifeDays (the
        // player-tunable value GetSuspicion's own decay uses), not the
        // PropertyTuning constant it defaults from — otherwise a player who
        // raises the slider above the 45-day default gets entries pruned
        // (and suspicion silently zeroed) before their own configured
        // half-life is reached.
        private void PruneFullyDecayedEntries(int nowTick)
        {
            for (int i = entries.Count - 1; i >= 0; i--)
            {
                float daysElapsed = (nowTick - entries[i].TimestampTicks) / (float)GenDate.TicksPerDay;
                if (daysElapsed >= PropertySettings.suspicionHalfLifeDays)
                {
                    entries.RemoveAt(i);
                }
            }
        }

        // Convenience for a UI-free "does this faction know ANYTHING is
        // wrong yet" read — still hidden from the player (spec item 6: "No
        // meter, no indicator, ever"), meant for other C# systems only.
        public bool HasAnyPropagatedKnowledge(int nowTick, float threshold = 0.05f, float propagationRatePerDay = PropertyTuning.DefaultPropagationRatePerDay)
        {
            for (int i = 0; i < entries.Count; i++)
            {
                WitnessEntry e = entries[i];
                float daysElapsed = (nowTick - e.TimestampTicks) / (float)GenDate.TicksPerDay;
                float propagated = Mathf.Clamp01(daysElapsed * propagationRatePerDay);
                float decay = Mathf.Clamp01(1f - daysElapsed / PropertySettings.suspicionHalfLifeDays);
                if (e.Confidence * propagated * decay >= threshold) return true;
            }
            return false;
        }

        // SETTLEMENT_VERBS_WAVE_1, social-fabric pass: the NEW write surface
        // this pass adds — spec item 9's "bribes and bought rounds as
        // propagation dampers." Every method above this point only ever
        // APPENDS (RegisterWitness) or READS (GetSuspicion/
        // HasAnyPropagatedKnowledge) entries; nothing before this pass could
        // reduce or remove one. Reduces (never fully erases in one call,
        // unless fraction is 1) each of `suspect`'s own entries' Confidence
        // by `fraction` — a partial "cools it off" rather than a hard wipe,
        // matching spec item 9's own word "dampers" rather than "erasers".
        // Called unconditionally by the verb regardless of whether `suspect`
        // has any entries here at all (module boundary: "Verbs ... must not
        // know perception outcomes" — the float-menu option never queries
        // GetSuspicion to decide whether to offer itself or to report
        // whether the bribe "worked"; it always fires, and this method is a
        // silent no-op when nothing matches).
        public void DampenSuspicion(ClaimantRef suspect, float fraction, int nowTick)
        {
            PruneFullyDecayedEntries(nowTick);
            fraction = Mathf.Clamp01(fraction);
            if (fraction <= 0f) return;

            for (int i = 0; i < entries.Count; i++)
            {
                WitnessEntry e = entries[i];
                if (!e.Suspect.Equals(suspect)) continue;
                e.Confidence *= (1f - fraction);
            }
        }

        public void ExposeData()
        {
            Scribe_References.Look(ref Faction, "faction");
            Scribe_Collections.Look(ref entries, "entries", LookMode.Deep);
            if (entries == null) entries = new List<WitnessEntry>();
        }
    }
}
