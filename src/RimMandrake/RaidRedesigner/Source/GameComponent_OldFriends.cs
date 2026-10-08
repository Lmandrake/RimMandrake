using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.RaidRedesigner
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §1.4: the persistent
    // roster of people the colony has met. Pure bookkeeping -- no LLM, no
    // menu authority, no letter rewrite. Eight Harmony postfixes (the other
    // Patch_*.cs files in this assembly) are the only writers of
    // RecordEncounter; this class owns the cap, the prune, and the
    // dead-collapse rule, nothing else.
    public class GameComponent_OldFriends : GameComponent
    {
        public const int MaxLivingEntries = 24;
        private const int DeathSweepIntervalTicks = 2500; // one in-game hour, same cadence as Ninefold's mood walk

        private List<OldFriendEntry> entries = new List<OldFriendEntry>();

        public GameComponent_OldFriends(Game game)
        {
        }

        public static GameComponent_OldFriends Instance =>
            Current.Game?.GetComponent<GameComponent_OldFriends>();

        public IReadOnlyList<OldFriendEntry> Entries => entries;

        // RAIDREDESIGNER_COVERAGE_GAPS_1: proof seam. Swaps the live roster for a scratch list and returns the
        // real one, so RaidRedesignerProof can drive RecordEncounter without touching the player's roster.
        public List<OldFriendEntry> ProofSwapEntries(List<OldFriendEntry> scratch)
        {
            List<OldFriendEntry> real = entries;
            entries = scratch;
            return real;
        }

        // The one entry point every capture hook calls. Idempotent per living
        // pawn: a pawn who already has a living entry gets a new Encounter
        // appended and deltas applied, never a duplicate entry. `role` only
        // ever upgrades an existing entry to Captain (the more notable tag) --
        // it never downgrades a more specific tag a prior hook already wrote
        // in the same call chain (e.g. EscapedPrisoner, set moments before
        // Pawn.ExitMap's own postfix also fires for the same departure).
        public OldFriendEntry RecordEncounter(Pawn pawn, Faction factionAtEntry, RoleTag role,
            int tick, string summary, int grudgeDelta = 0, int notabilityDelta = 0, bool pin = false)
        {
            // MOD_OPTIONS_RETROFIT_1: master switch. All eight capture hooks
            // funnel through this one method, so gating here alone turns the
            // whole mechanic into a no-op; every caller already null-checks
            // the return value.
            if (!RaidRedesignerSettings.rosterTrackingEnabled) return null;
            if (pawn == null) return null;

            // The find / role-upgrade / encounter / scaled-delta / cap-after-deltas flow is RM_RosterKernel.Record (fuzzed offline).
            RecordOutcome<OldFriendEntry> outcome = RM_RosterKernel.Record(entries, e => e.Pawn == pawn,
                () => new OldFriendEntry(pawn, factionAtEntry, role, tick), role, tick, summary, grudgeDelta, notabilityDelta,
                RaidRedesignerSettings.grudgeNotabilityMultiplier, RaidRedesignerSettings.maxLivingEntries);
            OldFriendEntry entry = outcome.Entry;

            // A pawn the cap just forgot (its own notability was the lowest) is not remembered, so it is not pinned either.
            if (pin && !outcome.EvictedSelf && RaidRedesignerSettings.pinEncounteredPawns)
            {
                bool keptBefore = Find.WorldPawns != null && Find.WorldPawns.ForcefullyKeptPawns.Contains(pawn);
                bool pinnedNow = WorldPawnPinning.PinForever(pawn);
                entry.PinnedByUs = RM_RosterKernel.PinnedByUsAfter(entry.PinnedByUs, keptBefore, keptBefore || pinnedNow);
            }
            // The roster forgot these people (cap): release the pins this mod placed so the world-pawn pool does not grow without bound.
            ReleasePins(outcome.Victims);

            return entry;
        }

        // Cap is player-tunable (RaidRedesignerSettings.maxLivingEntries,
        // default MaxLivingEntries=24); prune lowest notability. The
        // selection logic itself is pure (no Verse dependency) and lives in
        // RosterPruning so it can be offline-selftested -- this method is
        // just "ask, then remove."
        public void EnforceCap()
        {
            List<OldFriendEntry> victims = RosterPruning.SelectPruneVictims(entries, RaidRedesignerSettings.maxLivingEntries);
            foreach (OldFriendEntry victim in victims)
            {
                entries.Remove(victim);
            }
            ReleasePins(victims);
        }

        private static void ReleasePins(List<OldFriendEntry> forgotten)
        {
            foreach (OldFriendEntry victim in forgotten)
            {
                if (RM_RosterKernel.ShouldUnpin(victim.PinnedByUs, victim.Pawn != null && victim.Pawn.Faction != null && victim.Pawn.Faction.leader == victim.Pawn))
                {
                    WorldPawnPinning.Unpin(victim.Pawn);
                    victim.PinnedByUs = false;
                }
            }
        }

        public override void GameComponentTick()
        {
            base.GameComponentTick();
            if (Find.TickManager.TicksGame % DeathSweepIntervalTicks != 0) return;
            SweepForDeaths();
        }

        // A roster pawn can die off-screen (starvation as a world pawn, a
        // battle we never render) with no Harmony seam telling us directly --
        // an hourly poll of a <=24-entry list is the cheap, correct way to
        // learn it, mirroring Ninefold's own hourly-cadence housekeeping.
        public void SweepForDeaths()
        {
            for (int i = 0; i < entries.Count; i++)
            {
                OldFriendEntry e = entries[i];
                switch (RM_RosterKernel.Sweep(e.Dead, e.Pawn == null, e.Pawn != null && e.Pawn.Dead))
                {
                    case RM_RosterKernel.SweepVerdict.Died: e.MarkDead(Find.TickManager.TicksGame, "died"); break;
                    case RM_RosterKernel.SweepVerdict.Lost: e.MarkDead(Find.TickManager.TicksGame, "lost"); break;
                }
            }
            // The cap is player-tunable: lowering it takes effect at the next hourly sweep, not only when someone new arrives.
            EnforceCap();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref entries, "entries", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && entries == null)
                entries = new List<OldFriendEntry>();
        }
    }
}
