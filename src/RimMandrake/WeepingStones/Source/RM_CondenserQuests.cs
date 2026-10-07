using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.WeepingStones
{
    // WEEPINGSTONES_CONDENSER_QUESTS_1. Two optional quests on the walking condenser (RM_WalkingCondenser.cs):
    // RM_CondenserCapture (a wealthy collector wants the old gorrask alive) and RM_CondenserKeepFree (settlers ask
    // the colony to keep it alive through a season while hunters come for it). The quest TREES are XML
    // (Defs/QuestScriptDefs/RM_CondenserQuests.xml); C# supplies only the four verbs vanilla lacks:
    //   * find the one condenser crab and gate the offer on it        RM_QuestNode_GetCondenserCrab
    //   * fill a faction SLOT the campaign can remap by patching a def RM_QuestNode_GetFactionSlot + RM_FactionSlotDef
    //   * notice the crab is downed (no vanilla signal for it)         RM_QuestNode_CondenserSubdued
    //   * hand a downed crab to the buyer and end the moving oasis     RM_QuestNode_CondenserTaken
    //   * a raid that targets the crab, not the colony                 RM_QuestNode_CondenserHunters (vanilla QuestPart_RandomRaid)
    // Taking one quest forecloses the other: RM_QuestPart_CondenserClaim (added by the crab node) claims the crab
    // on accept and withdraws any rival offer; a quest that ends in Success settles the matter for the world.

    public enum RM_FactionSlotFallback : byte { Collector, Settlers, Hunters }

    // A faction slot. The free mod lists vanilla defNames; the campaign layer (UtinniPatches) inserts its own
    // FactionDef names at the head of preferredFactions. Names, not cross-refs, so an absent def costs nothing.
    public class RM_FactionSlotDef : Def
    {
        public List<string> preferredFactions = new List<string>();
        public RM_FactionSlotFallback fallback = RM_FactionSlotFallback.Settlers;

        private bool WantsHostile => fallback == RM_FactionSlotFallback.Hunters;

        private bool Usable(Faction f, Faction exclude)
        {
            if (f == null || f.IsPlayer || f.defeated || f.temporary || f.Hidden || !f.def.humanlikeFaction) return false;
            if (f == exclude) return false;
            return f.HostileTo(Faction.OfPlayer) == WantsHostile;
        }

        public Faction Resolve(Faction exclude)
        {
            List<Faction> all = Find.FactionManager.AllFactionsListForReading.Where(f => Usable(f, exclude)).ToList();
            if (all.Count == 0) return null;
            for (int i = 0; i < preferredFactions.Count; i++)
            {
                Faction hit = all.Where(f => f.def.defName == preferredFactions[i])
                    .OrderByDescending(f => f.PlayerGoodwill).FirstOrDefault();
                if (hit != null) return hit;
            }
            switch (fallback)
            {
                case RM_FactionSlotFallback.Collector:
                    return all.Where(f => !f.def.permanentEnemy)
                        .OrderByDescending(f => (int)f.def.techLevel).ThenByDescending(f => f.PlayerGoodwill).FirstOrDefault();
                case RM_FactionSlotFallback.Hunters:
                    return all.OrderByDescending(f => f.def.permanentEnemy).ThenByDescending(f => (int)f.def.techLevel).FirstOrDefault();
                default:
                    return all.Where(f => !f.def.permanentEnemy)
                        .OrderBy(f => f.def.techLevel > TechLevel.Industrial)
                        .ThenByDescending(f => f.PlayerGoodwill).FirstOrDefault();
            }
        }
    }

    internal static class RM_CondenserQuestUtil
    {
        public static Pawn FindCrab()
        {
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                if (!maps[i].IsPlayerHome) continue;
                IReadOnlyList<Pawn> pawns = maps[i].mapPawns.AllPawnsSpawned;
                for (int j = 0; j < pawns.Count; j++)
                {
                    Pawn p = pawns[j];
                    if (!p.Dead && p.Faction == null && p.TryGetComp<RM_CompWalkingCondenser>() != null) return p;
                }
            }
            return null;
        }

        public static bool ClaimStillHeld(RM_CondenserWorld w)
        {
            if (w.claimQuestId < 0) return false;
            List<Quest> qs = Find.QuestManager.QuestsListForReading;
            for (int i = 0; i < qs.Count; i++)
                if (qs[i].id == w.claimQuestId && !qs[i].Historical) return true;
            w.claimQuestId = -1; // the claiming quest is gone without cleanup: release
            return false;
        }

        public static bool OffersOpen()
        {
            if (!RM_WeepingStonesSettings.condenserEnabled || !RM_WeepingStonesSettings.condenserQuestsEnabled) return false;
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            if (w == null || w.ended || w.questsSettled) return false;
            return !ClaimStillHeld(w);
        }
    }

    // Gate + slate: stores the crab and its map; adds the claim part.
    public class RM_QuestNode_GetCondenserCrab : QuestNode
    {
        [NoTranslate] public SlateRef<string> storeAs;
        [NoTranslate] public SlateRef<string> storeMapAs;

        protected override bool TestRunInt(Slate slate)
        {
            if (!RM_CondenserQuestUtil.OffersOpen()) return false;
            Pawn crab = RM_CondenserQuestUtil.FindCrab();
            if (crab == null || crab.Downed) return false;
            slate.Set(storeAs.GetValue(slate) ?? "crab", crab);
            slate.Set(storeMapAs.GetValue(slate) ?? "map", crab.Map);
            return true;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            Pawn crab = RM_CondenserQuestUtil.FindCrab();
            if (crab == null) return;
            slate.Set(storeAs.GetValue(slate) ?? "crab", crab);
            slate.Set(storeMapAs.GetValue(slate) ?? "map", crab.Map);
            QuestGen.quest.AddPart(new RM_QuestPart_CondenserClaim { crab = crab });
        }
    }

    public class RM_QuestNode_GetFactionSlot : QuestNode
    {
        public RM_FactionSlotDef slot;
        public SlateRef<Faction> exclude;
        [NoTranslate] public SlateRef<string> storeAs;
        [NoTranslate] public SlateRef<string> storeLeaderAs;

        private bool Fill(Slate slate)
        {
            if (slot == null) return false;
            Faction f = slot.Resolve(exclude.GetValue(slate));
            if (f == null) return false;
            string leaderVar = storeLeaderAs.GetValue(slate);
            if (!leaderVar.NullOrEmpty())
            {
                if (f.leader == null) return false;
                slate.Set(leaderVar, f.leader);
            }
            slate.Set(storeAs.GetValue(slate) ?? "faction", f);
            return true;
        }

        protected override bool TestRunInt(Slate slate) { return Fill(slate); }
        protected override void RunInt() { Fill(QuestGen.slate); }
    }

    // Offer bookkeeping: ticks from the moment it is offered, so a rival accept withdraws this offer.
    public class RM_QuestPart_CondenserClaim : QuestPartActivable
    {
        public Pawn crab;

        public override void PostQuestAdded()
        {
            base.PostQuestAdded();
            if (State == QuestPartState.NeverEnabled) Enable(default(SignalArgs));
        }

        public override void PreQuestAccept()
        {
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            if (w != null) w.claimQuestId = quest.id;
        }

        public override void QuestPartTick()
        {
            if (Find.TickManager.TicksGame % 250 != 0 || quest.State != QuestState.NotYetAccepted) return;
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            bool gone = crab == null || crab.Dead || crab.Destroyed;
            bool taken = w == null || w.ended || w.questsSettled || (RM_CondenserQuestUtil.ClaimStillHeld(w) && w.claimQuestId != quest.id);
            if (gone || taken) quest.End(QuestEndOutcome.InvalidPreAcceptance, sendLetter: false);
        }

        public override void Cleanup()
        {
            base.Cleanup();
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            if (w == null) return;
            if (w.claimQuestId == quest.id) w.claimQuestId = -1;
            if (quest.State == QuestState.EndedSuccess) w.questsSettled = true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref crab, "crab");
        }
    }

    // ---- capture: notice the crab is down ---------------------------------------------------------------------
    public class RM_QuestNode_CondenserSubdued : QuestNode
    {
        public SlateRef<Pawn> crab;
        [NoTranslate] public SlateRef<string> outSignal;

        protected override bool TestRunInt(Slate slate) { return crab.GetValue(slate) != null; }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            RM_QuestPart_CondenserSubdued part = new RM_QuestPart_CondenserSubdued
            {
                crab = crab.GetValue(slate),
                inSignalEnable = slate.Get<string>("inSignal")
            };
            part.outSignalsCompleted.Add(QuestGenUtility.HardcodedSignalWithQuestID(outSignal.GetValue(slate)));
            QuestGen.quest.AddPart(part);
        }
    }

    public class RM_QuestPart_CondenserSubdued : QuestPartActivable
    {
        public Pawn crab;

        public override IEnumerable<GlobalTargetInfo> QuestLookTargets
        {
            get { if (crab != null && crab.Spawned) yield return crab; }
        }

        public override void QuestPartTick()
        {
            if (Find.TickManager.TicksGame % 60 != 0) return;
            if (crab != null && crab.Spawned && !crab.Dead && crab.Downed) Complete();
        }

        public override string ExtraInspectString(ISelectable target)
        {
            return target == crab ? "RM_CondenserQuestInspectCapture".Translate().ToString() : null;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref crab, "crab");
        }
    }

    // ---- capture: the buyer takes it; the moving oasis ends ----------------------------------------------------
    public class RM_QuestNode_CondenserTaken : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        public SlateRef<Pawn> crab;
        public SlateRef<Faction> buyer;

        protected override bool TestRunInt(Slate slate) { return crab.GetValue(slate) != null; }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new RM_QuestPart_CondenserTaken
            {
                inSignal = QuestGenUtility.HardcodedSignalWithQuestID(inSignal.GetValue(slate)) ?? slate.Get<string>("inSignal"),
                crab = crab.GetValue(slate),
                buyer = buyer.GetValue(slate)
            });
        }
    }

    public class RM_QuestPart_CondenserTaken : QuestPart
    {
        public string inSignal;
        public Pawn crab;
        public Faction buyer;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal || crab == null || crab.Dead) return;
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            if (w != null) { w.ended = true; w.capturedBy = buyer; }
            if (crab.Spawned)
            {
                crab.TryGetComp<RM_CompWalkingCondenser>()?.DryAllNow(crab.Map);
                // DeSpawn, never Destroy: a Destroyed signal here would fail the quest it is completing.
                crab.DeSpawn();
            }
            if (!crab.IsWorldPawn()) Find.WorldPawns.PassToWorld(crab, PawnDiscardDecideMode.KeepForever);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_References.Look(ref crab, "crab", saveDestroyedThings: true);
            Scribe_References.Look(ref buyer, "buyer");
        }
    }

    // ---- keep free: hunters whose target is the crab ---------------------------------------------------------
    public class RM_QuestNode_CondenserHunters : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        public SlateRef<Pawn> crab;
        public SlateRef<Faction> faction;
        public SlateRef<float> pointsFactor;

        protected override bool TestRunInt(Slate slate)
        {
            return crab.GetValue(slate)?.Map != null && faction.GetValue(slate) != null;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            Pawn c = crab.GetValue(slate);
            Faction f = faction.GetValue(slate);
            float factor = pointsFactor.GetValue(slate);
            if (factor <= 0f) factor = 1f;
            float pts = UnityEngine.Mathf.Max(300f, slate.Get("points", 500f) * factor);
            QuestPart_RandomRaid raid = new QuestPart_RandomRaid
            {
                inSignal = QuestGenUtility.HardcodedSignalWithQuestID(inSignal.GetValue(slate)) ?? slate.Get<string>("inSignal"),
                mapParent = c.Map.Parent,
                pointsRange = new FloatRange(pts * 0.9f, pts * 1.1f),
                faction = f,
                arrivalMode = PawnsArrivalModeDefOf.EdgeWalkIn,
                raidStrategy = RaidStrategyDefOf.ImmediateAttack,
                attackTargets = new List<Thing> { c },
                generateFightersOnly = true,
                customLetterLabel = "RM_CondenserHuntersLabel".Translate(f.Name).ToString(),
                customLetterText = "RM_CondenserHuntersText".Translate(f.Name, c.LabelShort).ToString()
            };
            QuestGen.quest.AddPart(raid);
        }
    }
}
