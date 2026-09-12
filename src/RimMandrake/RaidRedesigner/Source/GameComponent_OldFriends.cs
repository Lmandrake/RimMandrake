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

            OldFriendEntry entry = entries.Find(e => !e.Dead && e.Pawn == pawn);
            bool isNewEntry = entry == null;
            if (isNewEntry)
            {
                entry = new OldFriendEntry(pawn, factionAtEntry, role, tick);
                entries.Add(entry);
            }
            else if (role == RoleTag.Captain)
            {
                entry.Role = RoleTag.Captain;
            }

            entry.AddEncounter(new Encounter(tick, role, summary));
            float mult = RaidRedesignerSettings.grudgeNotabilityMultiplier;
            entry.Grudge = Mathf_Clamp(entry.Grudge + (int)(grudgeDelta * mult), -100, 100);
            entry.Notability = Mathf_Clamp(entry.Notability + (int)(notabilityDelta * mult), 0, 100);

            // Enforce the cap only after this call's own deltas are applied --
            // otherwise a brand-new entry is judged for pruning at Notability
            // 0, before the very notabilityDelta this call is about to award
            // it, and can be evicted (as an orphaned, no-longer-in-`entries`
            // object) in the same call that created it.
            if (isNewEntry) EnforceCap();

            if (pin && RaidRedesignerSettings.pinEncounteredPawns) WorldPawnPinning.PinForever(pawn);

            return entry;
        }

        // Cap is player-tunable (RaidRedesignerSettings.maxLivingEntries,
        // default MaxLivingEntries=24); prune lowest notability. The
        // selection logic itself is pure (no Verse dependency) and lives in
        // RosterPruning so it can be offline-selftested -- this method is
        // just "ask, then remove."
        private void EnforceCap()
        {
            foreach (OldFriendEntry victim in RosterPruning.SelectPruneVictims(entries, RaidRedesignerSettings.maxLivingEntries))
            {
                entries.Remove(victim);
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
        private void SweepForDeaths()
        {
            for (int i = 0; i < entries.Count; i++)
            {
                OldFriendEntry e = entries[i];
                if (!e.Dead && e.Pawn != null && e.Pawn.Dead)
                {
                    e.MarkDead(Find.TickManager.TicksGame, "died");
                }
            }
        }

        private static int Mathf_Clamp(int value, int min, int max)
        {
            if (value < min) return min;
            if (value > max) return max;
            return value;
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
