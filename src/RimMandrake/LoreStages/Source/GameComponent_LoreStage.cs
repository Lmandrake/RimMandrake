using System.Collections.Generic;
using Verse;

namespace RimMandrake.LoreStages
{
    // Holds where each reveal ladder stands, and is the only thing that ever
    // calls the applier.
    //
    // Game-scoped on purpose. The stage is per-COLONY progress and rides the
    // .rws; the def text it produces is process-global and rides nothing. That
    // asymmetry is the whole hazard the class manages — see FinalizeInit.
    //
    // Auto-instantiated: Game.FillComponents (Game.cs:472-490) constructs every
    // non-abstract GameComponent subclass in every loaded assembly, so there is
    // nothing to register and no def to ship.
    public class GameComponent_LoreStage : GameComponent
    {
        // ladderId -> current rung. Absent means 0: nothing revealed.
        private Dictionary<string, int> stages = new Dictionary<string, int>();

        public GameComponent_LoreStage(Game game)
        {
        }

        public static GameComponent_LoreStage Current =>
            Verse.Current.Game?.GetComponent<GameComponent_LoreStage>();

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref stages, "loreStages", LookMode.Value, LookMode.Value);
            if (stages == null)
            {
                // Scribe_Collections hands back null for an empty/absent
                // dictionary; every read below would NRE on it.
                stages = new Dictionary<string, int>();
            }
        }

        // 🔴 The load hazard, handled here and nowhere else.
        //
        // Defs are NOT reloaded when a savegame is loaded (LoadAllPlayData runs
        // only at process start and on a language change), so the descriptions
        // left on the defs when the player quit a stage-5 colony are still there
        // when they load a stage-0 save in the same session. FinalizeInit runs
        // on BOTH a new game and every load, and ResetAndApply restores every
        // baseline before applying, so whatever the previous game did is undone
        // before this game's stage is written. Never "advance by one" here.
        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Apply();
        }

        public int GetStage(string ladderId)
        {
            if (ladderId.NullOrEmpty()) return 0;
            return stages.TryGetValue(ladderId, out int stage) ? stage : 0;
        }

        // Set a ladder's rung and re-apply. Returns true when the stage moved.
        // Idempotent: setting the stage it already holds re-applies anyway,
        // which is harmless and keeps the caches honest.
        public bool SetStage(string ladderId, int stage)
        {
            if (ladderId.NullOrEmpty()) return false;

            RM_LoreStageTableDef table = TableFor(ladderId);
            if (table != null && table.maxStage > 0 && stage > table.maxStage)
            {
                stage = table.maxStage;
            }

            if (stage < 0) stage = 0;

            bool changed = GetStage(ladderId) != stage;
            stages[ladderId] = stage;
            Apply();
            return changed;
        }

        // The normal consumer call: a reveal gate fired, move this ladder up one
        // rung (clamped at the table's maxStage).
        public bool AdvanceStage(string ladderId)
        {
            return SetStage(ladderId, GetStage(ladderId) + 1);
        }

        public static RM_LoreStageTableDef TableFor(string ladderId)
        {
            foreach (RM_LoreStageTableDef table in DefDatabase<RM_LoreStageTableDef>.AllDefsListForReading)
            {
                if (table.LadderId == ladderId) return table;
            }

            return null;
        }

        private void Apply()
        {
            List<RM_LoreStageTableDef> tables = DefDatabase<RM_LoreStageTableDef>.AllDefsListForReading;
            if (tables.Count == 0) return;

            if (!LoreStageApplier.CachesReachable)
            {
                // Loud, because the failure it predicts is invisible: biome and
                // inspector text would update while trade/transfer tooltips and
                // hediff descriptions silently kept the old stage's words.
                Log.Error("[LoreStages] cannot reach the private description caches by reflection (" +
                          LoreStageApplier.CacheReachabilityReport +
                          "). Staged text will go STALE in trade/transfer and hediff tooltips. " +
                          "The engine renamed a field; fix LoreStageApplier before shipping.");
            }

            int applied = LoreStageApplier.ResetAndApply(
                tables,
                EffectiveStage,
                LoreStageDefDatabase.Resolve,
                Log.Warning);

            if (Prefs.DevMode)
            {
                Log.Message($"[LoreStages] applied {applied} staged field(s) across {tables.Count} ladder(s).");
            }
        }

        // MOD_OPTIONS_RETROFIT_1: the master toggle. Off means every ladder
        // reads as stage 0 (defs show their shipped baseline text) — the real
        // per-ladder progress in `stages` is untouched and untracked calls
        // (SetStage/AdvanceStage from a debug action or a consumer mod) keep
        // recording it normally, so flipping the toggle back on resumes right
        // where the colony's progress actually is. Never deletes or corrupts
        // `stages`.
        private int EffectiveStage(string ladderId)
        {
            return RM_LoreStagesSettings.stagedTextEnabled ? GetStage(ladderId) : 0;
        }

        /// <summary>Re-applies immediately — called live from the Mod Settings checkbox.</summary>
        public void Reapply()
        {
            Apply();
        }
    }
}
