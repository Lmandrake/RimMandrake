using System.Collections.Generic;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT. Owner, 2026-10-10 story sitting
    // card 13 (decision taken by question card): the Reclamation starts when
    // enough ancients are woken -- a count, the number owed tuning. Card 12:
    // independent of the crater event, either order. Replaces the built
    // trigger (a 45-day QuestNode_Delay after RUT_WokenClaimRefused inside
    // RUT_VaultClaimConflict), which gen_vault_quests.py no longer emits.
    //
    // What "woken" counts: every living humanlike pawn of the Ancients or
    // AncientsHostile faction that leaves an AncientCryptosleepCasket on any
    // map while the casket still stands -- the V6 vault's Rakata caskets and
    // every vanilla ancient-shrine casket alike (design: "the ones you woke,
    // and the ones they woke on the way"). A casket destroyed with sleepers
    // inside is the LOOT reading and wakes nobody. The rule itself lives in
    // WokenAncientsKernel so the offline selftest can assert on it.
    //
    // No Harmony: polls the caskets every PollTicks. The per-casket snapshot
    // is deliberately NOT saved -- after a load the first poll only seeds it,
    // and no ejection can happen between a save and its load.
    public class GameComponent_WokenAncients : GameComponent
    {
        private const int PollTicks = 250;
        private const string ReclamationIncident = "RUT_GiveQuest_Reclamation";

        public int wokenCount;
        public bool reclamationFired;

        private readonly Dictionary<int, int> snapshot = new Dictionary<int, int>();
        private readonly List<CasketObservation> observations = new List<CasketObservation>();
        private readonly HashSet<int> seenThisPoll = new HashSet<int>();
        private readonly List<int> stale = new List<int>();

        public GameComponent_WokenAncients(Game game)
        {
        }

        public static GameComponent_WokenAncients Instance =>
            Current.Game?.GetComponent<GameComponent_WokenAncients>();

        public override void GameComponentTick()
        {
            if (Find.TickManager.TicksGame % PollTicks != 0)
            {
                return;
            }
            Poll();
            TryFireReclamation();
        }

        private void Poll()
        {
            seenThisPoll.Clear();
            int woken = 0;
            List<Map> maps = Find.Maps;
            for (int m = 0; m < maps.Count; m++)
            {
                observations.Clear();
                List<Thing> caskets = maps[m].listerThings.ThingsOfDef(ThingDefOf.AncientCryptosleepCasket);
                for (int i = 0; i < caskets.Count; i++)
                {
                    if (!(caskets[i] is Building_Casket casket))
                    {
                        continue;
                    }
                    seenThisPoll.Add(casket.thingIDNumber);
                    observations.Add(new CasketObservation(casket.thingIDNumber, Sleepers(casket), casket.Destroyed));
                }
                woken += WokenAncientsKernel.Observe(snapshot, observations);
            }
            stale.Clear();
            foreach (int id in snapshot.Keys)
            {
                if (!seenThisPoll.Contains(id))
                {
                    stale.Add(id);
                }
            }
            for (int i = 0; i < stale.Count; i++)
            {
                snapshot.Remove(stale[i]);
            }
            if (woken > 0)
            {
                wokenCount += woken;
            }
        }

        private static int Sleepers(Building_Casket casket)
        {
            int n = 0;
            ThingOwner held = casket.GetDirectlyHeldThings();
            for (int i = 0; i < held.Count; i++)
            {
                if (held[i] is Pawn p && !p.Dead && p.RaceProps.Humanlike
                    && p.Faction != null
                    && (p.Faction == Faction.OfAncientsHostile || p.Faction == Faction.OfAncients))
                {
                    n++;
                }
            }
            return n;
        }

        public void TryFireReclamation()
        {
            if (!WokenAncientsKernel.ShouldFire(
                    StructureInjectionsRUTSettings.reclamationByWokenCount,
                    reclamationFired, wokenCount,
                    StructureInjectionsRUTSettings.reclamationWokenThreshold))
            {
                return;
            }
            IncidentDef def = DefDatabase<IncidentDef>.GetNamedSilentFail(ReclamationIncident);
            Map home = Find.AnyPlayerHomeMap;
            if (def == null || home == null)
            {
                return; // no home map yet: try again next poll
            }
            IncidentParms parms = StorytellerUtility.DefaultParmsNow(def.category, home);
            if (def.Worker.TryExecute(parms))
            {
                reclamationFired = true;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wokenCount, "rutWokenAncientsCount", 0);
            Scribe_Values.Look(ref reclamationFired, "rutReclamationFired", false);
        }

        [DebugAction("Quests", "Reclamation: add one woken ancient", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DebugAddWoken()
        {
            GameComponent_WokenAncients c = Instance;
            if (c == null)
            {
                return;
            }
            c.wokenCount++;
            Log.Message($"[RUT] woken ancients: {c.wokenCount} of {StructureInjectionsRUTSettings.reclamationWokenThreshold}; "
                      + $"fired={c.reclamationFired}");
            c.TryFireReclamation();
        }

        [DebugAction("Quests", "Reclamation: log woken count", allowedGameStates = AllowedGameStates.Playing)]
        private static void DebugLogWoken()
        {
            GameComponent_WokenAncients c = Instance;
            Log.Message(c == null
                ? "[RUT] GameComponent_WokenAncients missing"
                : $"[RUT] woken ancients: {c.wokenCount} of {StructureInjectionsRUTSettings.reclamationWokenThreshold}; "
                  + $"fired={c.reclamationFired}; enabled={StructureInjectionsRUTSettings.reclamationByWokenCount}");
        }
    }
}
