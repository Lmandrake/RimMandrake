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

    // RM_FactionSlotFallback, FactionInfo and the slot selection: Kernel/RM_ClaimKernel.cs.

    // A faction slot. The free mod lists vanilla defNames; the campaign layer (UtinniPatches) inserts its own
    // FactionDef names at the head of preferredFactions. Names, not cross-refs, so an absent def costs nothing.
    public class RM_FactionSlotDef : Def
    {
        public List<string> preferredFactions = new List<string>();
        public RM_FactionSlotFallback fallback = RM_FactionSlotFallback.Settlers;

        public Faction Resolve(Faction exclude)
        {
            List<Faction> all = Find.FactionManager.AllFactionsListForReading;
            List<FactionInfo> infos = new List<FactionInfo>(all.Count);
            for (int i = 0; i < all.Count; i++)
            {
                Faction f = all[i];
                infos.Add(new FactionInfo
                {
                    id = f.loadID, defName = f.def.defName, isPlayer = f.IsPlayer, defeated = f.defeated, temporary = f.temporary,
                    hidden = f.Hidden, humanlike = f.def.humanlikeFaction, hostile = !f.IsPlayer && f.HostileTo(Faction.OfPlayer),
                    permanentEnemy = f.def.permanentEnemy, techLevel = (int)f.def.techLevel, goodwill = f.IsPlayer ? 0 : f.PlayerGoodwill
                });
            }
            FactionInfo? hit = RM_ClaimKernel.Resolve(infos, preferredFactions, fallback, exclude != null ? exclude.loadID : -1);
            return hit.HasValue ? all.FirstOrDefault(f => f.loadID == hit.Value.id) : null;
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
            bool exists = false, historical = false;
            List<Quest> qs = Find.QuestManager.QuestsListForReading;
            for (int i = 0; i < qs.Count; i++)
            {
                if (qs[i].id == w.claimQuestId) { exists = true; historical = qs[i].Historical; if (!historical) break; }
            }
            bool held = RM_ClaimKernel.ClaimStillHeld(w.claimQuestId, exists, historical, out int newClaim);
            w.claimQuestId = newClaim; // the claiming quest is gone without cleanup: release
            return held;
        }

        public static bool OffersOpen()
        {
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            bool held = w != null && ClaimStillHeld(w);
            return RM_ClaimKernel.OffersOpen(RM_WeepingStonesSettings.condenserEnabled, RM_WeepingStonesSettings.condenserQuestsEnabled,
                w != null, w != null && w.ended, w != null && w.questsSettled, held);
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
            // Withdraw the rival offers now: waiting for their 250-tick poll left a window to accept both.
            List<Quest> qs = Find.QuestManager.QuestsListForReading;
            for (int i = qs.Count - 1; i >= 0; i--)
            {
                bool isClaim = qs[i].PartsListForReading.Any(p => p is RM_QuestPart_CondenserClaim);
                if (RM_ClaimKernel.RivalWithdrawsOnAccept(isClaim, qs[i].State == QuestState.NotYetAccepted, qs[i].id, quest.id))
                    qs[i].End(QuestEndOutcome.InvalidPreAcceptance, sendLetter: false);
            }
        }

        public override void QuestPartTick()
        {
            if (Find.TickManager.TicksGame % 250 != 0 || quest.State != QuestState.NotYetAccepted) return;
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            bool gone = crab == null || crab.Dead || crab.Destroyed;
            if (RM_ClaimKernel.Withdraws(gone, w != null, w != null && w.ended, w != null && w.questsSettled,
                    w != null && RM_CondenserQuestUtil.ClaimStillHeld(w), w != null ? w.claimQuestId : -1, quest.id)) quest.End(QuestEndOutcome.InvalidPreAcceptance, sendLetter: false);
        }

        public override void Cleanup()
        {
            base.Cleanup();
            RM_CondenserWorld w = RM_CondenserWorld.Get();
            if (w == null) return;
            RM_ClaimKernel.Cleanup(ref w.claimQuestId, ref w.questsSettled, quest.id, quest.State == QuestState.EndedSuccess);
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
