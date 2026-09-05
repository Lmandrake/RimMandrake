using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Aftermath
{
    // In-memory only (not IExposable) — a battle open at save time is simply
    // not resumed after a load; the rule runner only ever reacts to a CLOSED
    // record. Documented limitation, acceptable per this item's own verify
    // bar (offline/synthetic, no live-proof requirement to close the item).
    public class BattleRecord
    {
        public readonly Faction RaidFaction;
        public readonly List<Pawn> OriginalPawns;
        public readonly float StorytellerPoints;
        public readonly int OpenedTick;
        public readonly Map Map;

        // Set once LordMaker.MakeNewLord is correlated to this record
        // (Patch_LordCreatedForRaid) — see MapComponent_BattleRecorder's own
        // header for the correlation heuristic and why it is a heuristic.
        // Null until then; the fallback pawn-state poll in
        // MapComponent_BattleRecorder does not require this to be set.
        public Lord Lord;

        // Flipped by Patch_ColonistCasualty the moment a player-faction pawn
        // dies or is kidnapped while this record is open.
        public bool ColonistCasualty;

        public bool Closed;
        public BattleOutcome Outcome;
        public int ClosedTick;

        public BattleRecord(Faction faction, List<Pawn> pawns, float points, int tick, Map map)
        {
            RaidFaction = faction;
            OriginalPawns = pawns ?? new List<Pawn>();
            StorytellerPoints = points;
            OpenedTick = tick;
            Map = map;
        }

        // Live counts computed from current Pawn state — see
        // BattleOutcomeClassifier for why these three numbers (plus
        // ColonistCasualty) are all the classifier needs.
        public int CountDeadOrDowned()
        {
            int n = 0;
            foreach (Pawn p in OriginalPawns)
                if (p != null && (p.Dead || p.Downed)) n++;
            return n;
        }

        public int CountSurvivedAndExited()
        {
            int n = 0;
            foreach (Pawn p in OriginalPawns)
                if (p != null && !p.Dead && !p.Downed && !p.Spawned) n++;
            return n;
        }

        // "All accounted for" — every original raider is either
        // dead/downed or off the map. This is the fallback closing
        // condition when no Lord was ever correlated (see
        // MapComponent_BattleRecorder), and is ALSO true the instant the
        // correlated Lord empties out, so polling it costs nothing extra.
        public bool AllPawnsAccountedFor()
        {
            foreach (Pawn p in OriginalPawns)
            {
                if (p == null) continue;
                if (!p.Dead && !p.Downed && p.Spawned) return false;
            }
            return true;
        }
    }
}
