using System.Collections.Generic;
using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_FIRE_HOOK_RATELIMITED_1. divine_satiation_engine.md §3⑦ lists
    // "every breakdown, jam, fire, explosion, electrical short..." as feeding
    // Zizzik (the wrong spark), and §3⑧/the shipped matrix lists "fires and
    // burning" among what feeds Sh'kaar (the evil sun, exposure, killing
    // light). Fire is a Zizzik+Sh'kaar input.
    //
    // Verified against decompiled source (RimSage): `Verse.FireUtility.
    // TryStartFireIn(IntVec3 c, Map map, float fireSize, Thing instigator, ...)`
    // is the single choke every NEW fire spawn passes through -- but it is
    // NOT one-call-per-incident. `Fire.TrySpread()` (Source/RimWorld/Fire.cs)
    // calls it again for every existing burning cell, roughly every
    // 75-150 ticks per fire, so a single forest fire that has grown to
    // dozens of burning cells calls TryStartFireIn dozens of times a
    // SECOND. A naive per-call ApplyDelta would flood Zizzik/Sh'kaar far
    // harder from one spreading blaze than from, say, one grenade
    // (Patch_ExplosionOccurred, which is already correctly one-call-per-
    // explosion at its own choke point).
    //
    // What distinguishes "one incident" from "one ignited cell": `Fire.
    // instigator` (a Thing reference: the bullet, launcher pawn, or
    // explosion.instigator that lit the first cell). `TrySpread` re-passes
    // the SAME `instigator` reference to every downstream TryStartFireIn
    // call as the fire spreads (Fire.cs:400, and the Spark it throws for
    // long-range jumps also threads the same instigator) -- so every fire
    // cell born from one original ignition shares one identity, even
    // dozens of spread-generations later. There is no vanilla incident/
    // GameCondition tracker for fire the way there is for e.g. a raid; this
    // instigator-identity chain is the closest thing vanilla gives us.
    // Ambient/natural ignition (`SteadyEnvironmentEffects`, dry heat and
    // lightning-triggered spread) passes `instigator: null` -- those fires
    // collapse into one shared "natural" bucket below, which only makes the
    // limiter MORE conservative (never counts two natural fires as two
    // incidents inside the same window), never floods.
    //
    // So this hook is BOTH incident-aware (keyed on instigator identity,
    // not on the cell) AND time-window rate-limited (per §-suggested
    // fallback) -- one Zizzik+Sh'kaar delta per instigator per
    // RateLimitWindowTicks, no matter how many cells that instigator's fire
    // ignites in that window. A long-lived blaze can still credit again
    // once the window rolls over (an ongoing fire IS worse than a
    // one-cell scorch), just not once per cell per tick.
    [HarmonyPatch(typeof(FireUtility), nameof(FireUtility.TryStartFireIn))]
    public static class Patch_FireStarted
    {
        // 🔴 UNTUNED -- first-pass ordering only, same status as
        // EventMagnitude/MoodAmplitude in GameComponent_Ninefold.cs. §10
        // explicitly defers real tuning to a throwaway-save test rig. Chosen
        // to be comfortably longer than Fire's own spread cadence (75-150
        // ticks, Fire.cs SpreadInterval) so one spreading blaze reliably
        // collapses to one credit, while still letting a fire burning for
        // whole in-game minutes credit again as it keeps growing.
        private const int RateLimitWindowTicks = 600; // ~10 seconds

        // Per-instigator last-credited tick. Reference-keyed on purpose --
        // two different instigators (two separate incendiary shells, say)
        // must not suppress each other. Pruned below so a long game does not
        // accumulate one entry per bullet/grenade ever fired.
        private static readonly Dictionary<Thing, int> lastCreditedTick = new Dictionary<Thing, int>();

        // Shared bucket for instigator == null (ambient/natural ignition --
        // ChanceToStartFireIn/SteadyEnvironmentEffects never has a Thing to
        // key on).
        private static int lastNaturalCreditTick = -RateLimitWindowTicks;

        [HarmonyPostfix]
        public static void Postfix(bool __result, Thing instigator)
        {
            if (!__result) return; // ChanceToStartFireIn was 0 -- no fire actually spawned

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            int ticks = Find.TickManager.TicksGame;
            if (!ShouldCreditIncident(instigator, ticks)) return;

            comp.ApplyDelta(God.Zizzik, EventMagnitude.Small, "the wrong spark catches");
            comp.ApplyDelta(God.Shkaar, EventMagnitude.Small, "fire and burning, the Searer's work");
        }

        private static bool ShouldCreditIncident(Thing instigator, int ticks)
        {
            if (instigator == null)
            {
                if (ticks - lastNaturalCreditTick < RateLimitWindowTicks) return false;
                lastNaturalCreditTick = ticks;
                return true;
            }

            if (lastCreditedTick.TryGetValue(instigator, out int last) &&
                ticks - last < RateLimitWindowTicks)
            {
                return false;
            }

            lastCreditedTick[instigator] = ticks;
            PruneStale(ticks);
            return true;
        }

        // Cheap bound on the dictionary: only pays the enumeration cost once
        // it has actually grown, and only evicts entries whose window has
        // already lapsed (so an instigator mid-blaze is never evicted out
        // from under itself).
        private static void PruneStale(int ticks)
        {
            if (lastCreditedTick.Count < 64) return;

            List<Thing> stale = null;
            foreach (KeyValuePair<Thing, int> kv in lastCreditedTick)
            {
                if (ticks - kv.Value >= RateLimitWindowTicks)
                    (stale ??= new List<Thing>()).Add(kv.Key);
            }
            if (stale == null) return;
            for (int i = 0; i < stale.Count; i++)
                lastCreditedTick.Remove(stale[i]);
        }
    }
}
