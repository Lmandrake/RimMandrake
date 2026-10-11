using System.Collections.Generic;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT: the pure counting rule behind
    // GameComponent_WokenAncients, kept free of Verse so the offline selftest
    // (Source/SelfTest) compiles THIS file and asserts on it directly.
    //
    // A casket is one observation: its thingID, how many living ancient
    // sleepers it holds now, and whether it is destroyed. A casket that held
    // sleepers at the previous poll and now holds none while still standing
    // was EJECTED (Building_AncientCryptosleepCasket.EjectContents, by an Open
    // job or by combat damage): those sleepers are woken. A casket destroyed
    // with sleepers in it is the LOOT reading (MapComponent_VaultSleepers'
    // RUT_SleepersLooted) and wakes no one. A casket first seen this poll only
    // seeds the snapshot; nothing is counted for it.
    public struct CasketObservation
    {
        public int id;
        public int sleepers;
        public bool destroyed;

        public CasketObservation(int id, int sleepers, bool destroyed)
        {
            this.id = id;
            this.sleepers = sleepers;
            this.destroyed = destroyed;
        }
    }

    public static class WokenAncientsKernel
    {
        // Updates `snapshot` (thingID -> sleepers at last poll) in place from
        // one map's observations and returns how many sleepers woke since the
        // last poll. Caskets absent from `observations` are left alone; the
        // caller prunes per map.
        public static int Observe(Dictionary<int, int> snapshot, IEnumerable<CasketObservation> observations)
        {
            int woken = 0;
            foreach (CasketObservation o in observations)
            {
                int before;
                bool seen = snapshot.TryGetValue(o.id, out before);
                if (o.destroyed)
                {
                    snapshot.Remove(o.id);
                    continue;
                }
                if (seen && before > o.sleepers)
                {
                    woken += before - o.sleepers;
                }
                snapshot[o.id] = o.sleepers;
            }
            return woken;
        }

        // The Reclamation fires once, the first time the woken count reaches
        // the threshold, and never while the feature is switched off.
        public static bool ShouldFire(bool enabled, bool alreadyFired, int wokenCount, int threshold)
        {
            if (!enabled || alreadyFired)
            {
                return false;
            }
            return wokenCount >= (threshold < 1 ? 1 : threshold);
        }
    }
}
