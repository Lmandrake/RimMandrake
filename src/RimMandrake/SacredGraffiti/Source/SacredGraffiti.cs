using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace Rimmandrake.rm.sacredgraffiti
{
    // GRAFFITI_MOD_EXPANSION_1 — the owner's ruling on placement: a sacred
    // mark is placed as a RITUAL OUTCOME (a reward off a Salvation Matrix
    // boon), not a Harmony patch on GraffitiMod's own spawn loop and not
    // hand-placement.
    //
    // Generic and god-agnostic on purpose. design/Jawa/divine_satiation_engine.md
    // "The Matrix" specs all nine gods' boons/curses in PROSE ONLY - "the
    // engine build ... files when the owner calls the build" - so there is
    // no real RitualDef/PreceptDef/outcomeEffect for any god yet. This class
    // does not invent one. It is the reusable MECHANISM: point any future
    // RitualOutcomeEffectDef's workerClass at this type, set its
    // filthDefToSpawn to a god's sacred-mark ThingDef (RM_SacredMark_Ishko
    // today; eight more once arted - see the item file), and it is live the
    // moment a real Matrix ritual references that RitualOutcomeEffectDef as
    // its outcomeEffect. No further C# needed per god.
    //
    // filthDefToSpawn/filthCountToSpawn are EXISTING vanilla
    // RitualOutcomeEffectDef fields (Source/RimWorld/RitualOutcomeEffectDef.cs),
    // already used for exactly "spawn this filth as part of a ritual outcome"
    // by RitualOutcomeEffectWorker_RemoveConsumableBuilding (e.g.
    // DestroyConsumableBuilding_Pyre spawning Filth_Ash - Defs/Ideology/
    // Rituals/Ritual_Outcomes.xml). That worker only fires at a CONSUMED
    // building's occupied rect and always destroys the target, which is the
    // wrong shape for a mark that should appear at an ordinary ritual site
    // and never destroy anything. This class reuses the same two fields for
    // their documented purpose, wired to a normal ritual's target/spot
    // instead.
    public class RitualOutcomeEffectWorker_PlaceSacredMark : RitualOutcomeEffectWorker_FromQuality
    {
        public RitualOutcomeEffectWorker_PlaceSacredMark()
        {
        }

        public RitualOutcomeEffectWorker_PlaceSacredMark(RitualOutcomeEffectDef def)
            : base(def)
        {
        }

        // Vanilla's own extension point - RitualOutcomeEffectWorker_FromQuality.Apply
        // calls this with the already-rolled outcome, so all of Apply's
        // letter/memory/development-point bookkeeping runs unmodified; this
        // only adds the mark and (if one was placed) a line in the outcome
        // letter naming it.
        protected override void ApplyExtraOutcome(Dictionary<Pawn, int> totalPresence,
            LordJob_Ritual jobRitual, RitualOutcomePossibility outcome,
            out string extraOutcomeDesc, ref LookTargets letterLookTargets)
        {
            extraOutcomeDesc = null;

            // A curse doesn't leave a mark - only a favorable outcome does.
            // Pillar bar (§19.5): this never grants a material reward, only a
            // devotional wall-mark (the mark's own statBases carry its
            // Beauty sign, positive or otherwise per the god's canon
            // temperament - see SacredMarks.xml).
            if (!outcome.Positive) return;
            if (def.filthDefToSpawn == null) return;

            Map map = jobRitual.Map;
            IntVec3 cell = jobRitual.selectedTarget.IsValid
                ? jobRitual.selectedTarget.Cell
                : IntVec3.Invalid;

            if (map == null || !cell.IsValid || !cell.InBounds(map))
            {
                // Fall back to wherever the ritual actually happened when the
                // target carried no cell (a pawn-only ritual target, say):
                // any participant's own position.
                Pawn fallback = totalPresence.Keys.FirstOrDefault(p => p.Spawned);
                if (fallback == null) return;
                cell = fallback.Position;
                map = fallback.Map;
            }

            int count = System.Math.Max(1, def.filthCountToSpawn.RandomInRange);
            if (FilthMaker.TryMakeFilth(cell, map, def.filthDefToSpawn, count))
            {
                extraOutcomeDesc = def.filthDefToSpawn.LabelCap + " is left behind, painted by unseen hands.";
            }
        }
    }
}
