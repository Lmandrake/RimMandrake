using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI.Group;
using RimMandrake.Ninefold;

namespace RimMandrake.Aftermath
{
    // design/Jawa/proposals/plot_mechanisms_wave.md Part 2's battle recorder.
    // Opens a BattleRecord when IncidentWorker_Raid.TryGenerateRaidInfo
    // returns true (Patch_RaidGenerated.cs) and closes it when the raid's
    // Lord is removed (Patch_LordRemoved.cs) -- WITH a fallback poll
    // (CheckFallbackClosures, below) for the case where the Lord could not
    // be correlated (see TryCorrelateLord's own comment) or its removal
    // postfix is somehow missed. Reconciles with, rather than duplicates,
    // mandrake.rm.ninefold's existing Patch_BattleResolved.cs (a PER-DEATH
    // Sh'kaar hook on Pawn.Kill, unconditional on any raid): this recorder
    // adds a separate PER-BATTLE delta once per closed battle, calling the
    // same public GameComponent_Ninefold.ApplyDelta rather than adding a
    // second patch on Pawn.Kill.
    public class MapComponent_BattleRecorder : MapComponent
    {
        private const int FallbackPollIntervalTicks = 250;

        // In-memory only -- see BattleRecord's own header for why (a battle
        // open at save time is simply not resumed after a load).
        private readonly List<BattleRecord> open = new List<BattleRecord>();

        // Short closed-battle history, capped, for inspection/debugging only
        // -- nothing reads this except DevMode logging and (potentially)
        // future tooling. Not scribed.
        private readonly List<BattleRecord> closedHistory = new List<BattleRecord>();
        private const int ClosedHistoryCap = 20;

        public MapComponent_BattleRecorder(Map map) : base(map)
        {
        }

        public static MapComponent_BattleRecorder For(Map map) =>
            map?.GetComponent<MapComponent_BattleRecorder>();

        // --- Opening -----------------------------------------------------

        public void OpenBattle(Faction faction, List<Pawn> pawns, float points, int tick)
        {
            if (faction == null || pawns == null || pawns.Count == 0) return;
            // Scope per doc Part 2: this is about HOSTILE raids, not every
            // TryGenerateRaidInfo caller (RaidFriendly reuses the same
            // method with a friendly faction -- verified via rimsage,
            // IncidentWorker_Raid.TryGenerateRaidInfo is shared).
            if (!faction.HostileTo(Faction.OfPlayer)) return;

            open.Add(new BattleRecord(faction, new List<Pawn>(pawns), points, tick, map));

            if (Prefs.DevMode)
                Log.Message("[RimMandrake.Aftermath] battle opened: " + faction.Name +
                    ", " + pawns.Count + " pawns, " + points.ToString("F0") + " pts.");
        }

        // --- Lord correlation ---------------------------------------------

        // HEURISTIC, documented as such: TryGenerateRaidInfo does not itself
        // hand back the Lord that will eventually own these pawns (the raid
        // pipeline creates it afterward, inside the arrival-mode worker).
        // LordMaker.MakeNewLord(Faction faction, LordJob lordJob, Map map,
        // IEnumerable<Pawn> startingPawns) is the real, verified choke point
        // (Verse/AI/Group/LordMaker.cs) -- every Lord in the game passes
        // through it, not just raids. We correlate by (a) same map, (b) same
        // faction, (c) at least one pawn in `startingPawns` also present in
        // an open, not-yet-correlated record's OriginalPawns, preferring the
        // MOST RECENTLY opened matching record (LIFO) if more than one
        // qualifies (rare: two same-faction raids opened in the same tick).
        // This is deliberately loose rather than an exact set match, because
        // PostProcessSpawnedPawns can still be mutating the pawns list
        // between TryGenerateRaidInfo and the Lord's creation.
        public void TryCorrelateLord(Lord lord, IEnumerable<Pawn> startingPawns)
        {
            if (lord == null || lord.Map != map || lord.faction == null) return;
            var starting = startingPawns?.ToList();
            if (starting == null || starting.Count == 0) return;

            for (int i = open.Count - 1; i >= 0; i--)
            {
                BattleRecord record = open[i];
                if (record.Lord != null || record.RaidFaction != lord.faction) continue;
                if (record.OriginalPawns.Any(p => starting.Contains(p)))
                {
                    record.Lord = lord;
                    return;
                }
            }
        }

        // --- Closing --------------------------------------------------------

        public void TryCloseByLordRemoval(Lord lord)
        {
            BattleRecord record = open.FirstOrDefault(r => r.Lord == lord && !r.Closed);
            if (record != null) Close(record);
        }

        public void Notify_ColonistCasualty()
        {
            // Any battle still open on this map could plausibly be the
            // cause -- doc's "colonist deaths/kidnaps >= 1" is not scoped
            // to a specific raid's Lord (a raid we are LOSING can lose a
            // colonist to a raider who is not the one who eventually
            // leaves). Flagging every currently-open record is the
            // conservative reading: a colonist casualty during simultaneous
            // battles marks all of them LOST-eligible, never silently
            // attributed to the wrong one.
            foreach (BattleRecord r in open)
                if (!r.Closed) r.ColonistCasualty = true;
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % FallbackPollIntervalTicks != 0) return;
            CheckFallbackClosures();
        }

        private void CheckFallbackClosures()
        {
            // Iterate a snapshot -- Close() mutates `open`.
            foreach (BattleRecord record in open.ToList())
            {
                if (record.Closed) continue;
                if (record.AllPawnsAccountedFor()) Close(record);
            }
        }

        private void Close(BattleRecord record)
        {
            if (record.Closed) return;
            record.Closed = true;
            record.ClosedTick = Find.TickManager.TicksGame;
            record.Outcome = BattleOutcomeClassifier.Classify(
                record.OriginalPawns.Count,
                record.CountDeadOrDowned(),
                record.CountSurvivedAndExited(),
                record.ColonistCasualty);

            open.Remove(record);
            closedHistory.Add(record);
            while (closedHistory.Count > ClosedHistoryCap) closedHistory.RemoveAt(0);

            ApplyNinefoldDelta(record);
            AftermathRuleRunner.Instance?.OnBattleClosed(record);

            if (Prefs.DevMode)
                Log.Message("[RimMandrake.Aftermath] battle closed: " + record.RaidFaction?.Name +
                    " -> " + record.Outcome);
        }

        // design/Jawa/proposals/plot_mechanisms_wave.md Part 2: "fires
        // Sh'kaar +D - the battle hook Ninefold currently lacks". Magnitude
        // scaled by outcome severity -- a first-pass ordering (same UNTUNED
        // status as Ninefold's own EventMagnitude constants; real tuning is
        // SATIATION_TUNING_RIG's job, not this build's).
        private static void ApplyNinefoldDelta(BattleRecord record)
        {
            GameComponent_Ninefold ninefold = GameComponent_Ninefold.Instance;
            if (ninefold == null) return;

            float delta = record.Outcome switch
            {
                BattleOutcome.Repelled => EventMagnitude.Large,
                BattleOutcome.Lost => EventMagnitude.Medium,
                BattleOutcome.Routed => EventMagnitude.Medium,
                _ => EventMagnitude.Small,
            };

            ninefold.ApplyDelta(God.Shkaar, delta,
                "battle " + record.Outcome + ": " + (record.RaidFaction?.Name ?? "unknown faction"));
        }
    }
}
