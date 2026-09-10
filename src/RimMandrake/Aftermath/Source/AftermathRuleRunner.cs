using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Aftermath
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §2.1's rule engine.
    // Evaluates BattleOutcome-triggered rules (1, 2, 3) AND
    // MentalBreakNearBattle (rule 6, PLOT_MECHANISM_MODS_WAVE_1 2026-09-09
    // wiring pass) - see AftermathTriggerKind.cs for exactly which of the
    // remaining four are shipped as DATA but not yet WIRED, and why.
    public class AftermathRuleRunner : GameComponent
    {
        // §2.2: "No stacking beyond one queued aftermath per faction and two
        // total. A battle that would queue a third is simply remembered by
        // the roster instead [not this mod's concern - it just declines]."
        private const int MaxPerFaction = 1;
        private const int MaxTotal = 2;

        // Rule 6's own window ("a mental break WITHIN 2 DAYS after a
        // battle"). GenDate.TicksPerDay, same constant TryQueue already uses
        // for delayDays -> delayTicks below.
        private const int MentalBreakNearBattleWindowTicks = 2 * GenDate.TicksPerDay;

        private List<QueuedAftermathMarker> queued = new List<QueuedAftermathMarker>();

        // Per-map "last battle that closed here", for rule 6's trigger. IN-
        // MEMORY ONLY, not scribed - same documented limitation BattleRecord
        // and MapComponent_BattleRecorder's closedHistory already carry: a
        // mental break that happens to land just after a save/reload will
        // not see a battle that closed before the reload. Acceptable per
        // this item's own bar (a missed escalation is not a broken one).
        private readonly Dictionary<Map, BattleRecord> lastClosedByMap = new Dictionary<Map, BattleRecord>();

        public AftermathRuleRunner(Game game)
        {
        }

        public static AftermathRuleRunner Instance =>
            Current.Game?.GetComponent<AftermathRuleRunner>();

        public override void GameComponentTick()
        {
            base.GameComponentTick();
            if (Find.TickManager.TicksGame % 5000 != 0) return; // hourly-ish housekeeping, cheap list
            queued.RemoveAll(q => Find.TickManager.TicksGame >= q.FireTick);
        }

        public void OnBattleClosed(BattleRecord record)
        {
            if (record?.Map != null) lastClosedByMap[record.Map] = record;
            if (record?.RaidFaction == null) return;

            int survivors = record.CountSurvivedAndExited();
            foreach (RM_AftermathRuleDef def in DefDatabase<RM_AftermathRuleDef>.AllDefsListForReading)
            {
                if (!AftermathRuleEligibility.IsEligible(def, record.Outcome, survivors)) continue;
                TryQueue(def, record);
            }
        }

        // Rule 6 ("Zizzik's aftermath"): "a mental break within 2 days after
        // a battle while Zizzik >= Content." Called from
        // Patch_MentalBreakNearBattle's postfix on the SAME vanilla seam
        // Ninefold's own mental-break hook patches
        // (MentalStateHandler.TryStartMentalState) - a different Harmony id,
        // coexists safely. Reuses the same TryQueue path as rules 1-3 (same
        // discipline caps, same cooldown-mod bypass, same telegraph/chronicle
        // wiring) against the CACHED record of whichever battle closed here
        // most recently, rather than duplicating that logic.
        public void OnMentalBreakNearBattle(Pawn pawn)
        {
            Map map = pawn?.Map;
            if (map == null) return;
            if (!lastClosedByMap.TryGetValue(map, out BattleRecord record) || record == null) return;

            int sinceBattle = Find.TickManager.TicksGame - record.ClosedTick;
            if (sinceBattle < 0 || sinceBattle > MentalBreakNearBattleWindowTicks) return;

            // NinefoldBandBridge is a soft-hook reflection query (the mirror
            // of ChronicleSubscriber's soft-hook subscribe on Ninefold's own
            // side) - CHRONICLE_NINEFOLD_DECOUPLE_1 forbids a hard reference
            // in either direction. Ninefold absent/renamed -> false -> this
            // rule simply never fires (law 2: whole with the consumer
            // absent), same as every other Ninefold-tied rule's null guard.
            if (!NinefoldBandBridge.ZizzikAtLeastContent()) return;

            foreach (RM_AftermathRuleDef def in DefDatabase<RM_AftermathRuleDef>.AllDefsListForReading)
            {
                if (!AftermathRuleEligibility.IsEligibleMentalBreakNearBattle(def)) continue;
                TryQueue(def, record);
            }
        }

        private void TryQueue(RM_AftermathRuleDef def, BattleRecord record)
        {
            Faction targetFaction = ResolveTargetFaction(def, record);
            if (targetFaction == null) return;

            if (!PassesDiscipline(targetFaction)) return;

            IncidentDef incidentDef = DefDatabase<IncidentDef>.GetNamedSilentFail(def.payloadIncidentDefName);
            if (incidentDef == null)
            {
                Log.Warning("[RimMandrake.Aftermath] " + def.defName + ": payload IncidentDef '" +
                    def.payloadIncidentDefName + "' not found - skipping.");
                return;
            }

            float delayDays = Rand.Range(def.delayDaysMin, def.delayDaysMax);
            int delayTicks = (int)(delayDays * GenDate.TicksPerDay);
            int fireTick = Find.TickManager.TicksGame + delayTicks;

            IncidentParms parms = new IncidentParms
            {
                target = record.Map,
                faction = targetFaction,
                // §2.2: "points never exceed the storyteller's own" - reusing
                // the ORIGINAL battle's own points trivially satisfies this
                // (never more, and it is the storyteller's own number).
                points = record.StorytellerPoints,
                forced = true, // CONFIRMED bypass of mlie.factionraidcooldown, not
                                // assumed: `strings` on its actual shipped DLL
                                // (Steam Workshop id 3547098393,
                                // 1.6/Assemblies/FactionRaidCooldown.dll) shows a
                                // Harmony patch class
                                // "IncidentWorker_RaidEnemy_FactionCanBeGroupSource"
                                // built against the literal type string
                                // "RimWorld.IncidentWorker_RaidEnemy, Assembly-CSharp"
                                // and method "FactionCanBeGroupSource" -- i.e. it
                                // patches EXACTLY IncidentWorker_RaidEnemy.
                                // FactionCanBeGroupSource, the method vanilla's own
                                // TryResolveRaidFaction (RimWorld/
                                // IncidentWorker_RaidEnemy.cs:58) only calls from
                                // its SECOND and THIRD branches (the "pick a random
                                // faction" fallbacks). Its FIRST branch --
                                // `if (parms.faction != null && parms.faction.
                                // HostileTo(Faction.OfPlayer) && (!parms.faction.
                                // deactivated || parms.forced)) return true;` --
                                // returns immediately once `faction` is pre-set,
                                // never reaching FactionCanBeGroupSource at all.
                                // `forced` additionally covers a deactivated
                                // faction. Also required by vanilla's own
                                // `IncidentWorker.CanFireNow` to skip its
                                // FiredTooRecently(map)/points-band/etc. gates --
                                // note CanFireNowSub itself is NOT skipped by
                                // forced (RimWorld/IncidentWorker.cs:35-154), but
                                // neither IncidentWorker_Raid nor
                                // IncidentWorker_RaidEnemy override CanFireNowSub
                                // in 1.6, so there is nothing there to bypass.
            };

            Find.Storyteller.incidentQueue.Add(incidentDef, fireTick, parms);
            queued.Add(new QueuedAftermathMarker(targetFaction, fireTick));

            SendTelegraph(def, targetFaction);

            // CHRONICLE_NINEFOLD_DECOUPLE_1: this used to reach into
            // GameComponent_Ninefold.ApplyDelta with def.godTie as a God
            // enum. It now PUBLISHES the queued rule on the spine and lets
            // whoever cares about godTie/godDelta (Ninefold's own
            // ChronicleSubscriber) read them off the def as data. Raised
            // unconditionally -- a consumer other than Ninefold may want a
            // queued-rule signal that carries no god tie at all.
            ChronicleEvents.Raise(new ChronicleEvent(
                ChronicleEventKind.RuleQueued,
                Find.TickManager.TicksGame,
                record.Map,
                record.OriginalPawns,
                null,
                record.Outcome.ToString(),
                def));

            if (Prefs.DevMode)
                Log.Message("[RimMandrake.Aftermath] queued " + def.defName + " for " + targetFaction.Name +
                    " at tick " + fireTick + " (" + delayDays.ToString("F1") + "d).");
        }

        private Faction ResolveTargetFaction(RM_AftermathRuleDef def, BattleRecord record)
        {
            switch (def.payloadFactionMode)
            {
                case AftermathPayloadFactionMode.SameAsTrigger:
                    return record.RaidFaction;

                case AftermathPayloadFactionMode.AllyOfTrigger:
                    string defeatedDefName = record.RaidFaction.def?.defName;
                    if (defeatedDefName == null) return null;
                    RM_AlliancePairDef pair = DefDatabase<RM_AlliancePairDef>.AllDefsListForReading
                        .FirstOrDefault(p => p.a == defeatedDefName);
                    if (pair == null) return null;
                    FactionDef allyDef = DefDatabase<FactionDef>.GetNamedSilentFail(pair.b);
                    if (allyDef == null) return null;
                    Faction ally = Find.FactionManager.FirstFactionOfDef(allyDef);
                    // An ally faction that is friendly to the player is not
                    // "not friendly to the player" per the doc's own trigger
                    // condition - skip rather than send a friendly faction's
                    // pawns as a hostile payload.
                    if (ally == null || !ally.HostileTo(Faction.OfPlayer)) return null;
                    return ally;

                default:
                    // HuttClaimant / HeldPrisonerHome - rules 4/8, not wired
                    // (see AftermathTriggerKind.cs). OnBattleClosed never
                    // reaches a def with one of these modes today because
                    // those defs' triggerKind is not BattleOutcome.
                    return null;
            }
        }

        private bool PassesDiscipline(Faction targetFaction)
        {
            int now = Find.TickManager.TicksGame;
            int liveTotal = queued.Count(q => q.FireTick > now);
            int liveForFaction = queued.Count(q => q.FireTick > now && q.Faction == targetFaction);

            if (liveForFaction >= MaxPerFaction) return false;
            if (liveTotal >= MaxTotal) return false;
            return true;
        }

        private static void SendTelegraph(RM_AftermathRuleDef def, Faction targetFaction)
        {
            string label = def.telegraphLabel ?? def.label ?? def.defName;
            string text = string.Format(def.telegraphText ?? "{0} is stirring.", targetFaction.Name);
            Find.LetterStack.ReceiveLetter(label, text, LetterDefOf.ThreatBig, null, targetFaction);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref queued, "queued", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && queued == null)
                queued = new List<QueuedAftermathMarker>();
        }
    }
}
