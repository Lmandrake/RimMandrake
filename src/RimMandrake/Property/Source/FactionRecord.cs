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
                float decay = Mathf.Clamp01(1f - daysElapsed / PropertyTuning.SuspicionHalfLifeDays);
                total += e.Confidence * propagated * decay;
            }
            return Mathf.Clamp01(total);
        }

        // Drops entries whose decayed contribution has reached ~0 for every
        // suspect, regardless of the propagation rate used to read them —
        // decay is monotonic in elapsed time alone, so once an entry passes
        // SuspicionHalfLifeDays it contributes nothing to any future read.
        private void PruneFullyDecayedEntries(int nowTick)
        {
            for (int i = entries.Count - 1; i >= 0; i--)
            {
                float daysElapsed = (nowTick - entries[i].TimestampTicks) / (float)GenDate.TicksPerDay;
                if (daysElapsed >= PropertyTuning.SuspicionHalfLifeDays)
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
                float decay = Mathf.Clamp01(1f - daysElapsed / PropertyTuning.SuspicionHalfLifeDays);
                if (e.Confidence * propagated * decay >= threshold) return true;
            }
            return false;
        }

        public void ExposeData()
        {
            Scribe_References.Look(ref Faction, "faction");
            Scribe_Collections.Look(ref entries, "entries", LookMode.Deep);
            if (entries == null) entries = new List<WitnessEntry>();
        }
    }
}
