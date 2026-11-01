// BESKAR_ARMORER_QUEST_1 spec 3.2, 3.3, 4.2: the custom quest nodes, each a small QuestPart so the XML keeps the shape.
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.BeskarArmorer
{
    internal static class Sig
    {
        public static string Of(SlateRef<string> r, Slate slate)
        {
            string s = r.GetValue(slate);
            return s.NullOrEmpty() ? slate.Get<string>("inSignal") : QuestGenUtility.HardcodedSignalWithQuestID(s);
        }
        public static string Out(SlateRef<string> r, Slate slate) { return QuestGenUtility.HardcodedSignalWithQuestID(r.GetValue(slate)); }
        public static void Send(string tag) { if (!tag.NullOrEmpty()) Find.SignalManager.SendSignal(new Signal(tag)); }
    }

    public class RM_QuestNode_RevealArmorerCovert : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        [NoTranslate] public SlateRef<string> outSignal;
        [NoTranslate] public SlateRef<string> outSignalRefused;

        protected override bool TestRunInt(Slate slate) { return ModsConfig.OdysseyActive; }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new RM_QuestPart_RevealCovert
            {
                inSignal = Sig.Of(inSignal, slate),
                outSignal = Sig.Out(outSignal, slate),
                outSignalRefused = Sig.Out(outSignalRefused, slate),
            });
        }
    }

    public class RM_QuestPart_RevealCovert : QuestPart
    {
        public string inSignal, outSignal, outSignalRefused;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal) return;
            RM_ArmorerCovert covert = RM_ArmorerState.Get.Reveal(out string refused);
            if (covert == null)
            {
                Log.Message("[BeskarArmorer] reveal refused: " + refused);
                Sig.Send(outSignalRefused);
                return;
            }
            Find.LetterStack.ReceiveLetter("Coordinates from the Creed",
                "A tight beam from orbit, no name on it. The Armorer has heard of the clan that keeps beskar honourably, and she has sent coordinates. "
                + "Her covert is in orbit, and only a gravship reaches it. Bring beskar and she will reforge it into what you wish; she keeps one part in "
                + BeskarArmorerSettings.tributeOneIn + " for the foundlings. You may return whenever you like. Do not raise a hand there.",
                LetterDefOf.PositiveEvent, covert, null, quest);
            Sig.Send(outSignal);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref outSignal, "outSignal");
            Scribe_Values.Look(ref outSignalRefused, "outSignalRefused");
        }
    }

    public class RM_QuestNode_AddHeat : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        public SlateRef<Faction> faction;
        public SlateRef<int> amount;
        [NoTranslate] public SlateRef<string> source;

        protected override bool TestRunInt(Slate slate) { return true; }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new RM_QuestPart_AddHeat { inSignal = Sig.Of(inSignal, slate), faction = faction.GetValue(slate), amount = amount.GetValue(slate), source = source.GetValue(slate) });
        }
    }

    public class RM_QuestPart_AddHeat : QuestPart
    {
        public string inSignal, source;
        public Faction faction;
        public int amount;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag == inSignal) RM_HeatEvents.Record(faction, amount, source);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref source, "source");
            Scribe_Values.Look(ref amount, "amount");
            Scribe_References.Look(ref faction, "faction");
        }
    }

    public class RM_QuestNode_GetEmpire : QuestNode
    {
        [NoTranslate] public SlateRef<string> storeAs;

        protected override bool TestRunInt(Slate slate)
        {
            if (Faction.OfEmpire == null) return false;
            slate.Set(storeAs.GetValue(slate), Faction.OfEmpire);
            return true;
        }

        protected override void RunInt() { QuestGen.slate.Set(storeAs.GetValue(QuestGen.slate), Faction.OfEmpire); }
    }

    /// <summary>Spec 4.2's open question closed by not asking it: `.LeftMap` differs across a caravan, a departing gravship and the map
    /// edge, so this polls the one thing that is true of all three. He joins you when you land, and he is out the moment he is
    /// alive and not on the site map. He cannot be left behind: as a player pawn he blocks the map's removal.</summary>
    public class RM_QuestNode_Breakout : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignalArrived;
        [NoTranslate] public SlateRef<string> outSignalOut;
        [NoTranslate] public SlateRef<string> outSignalDead;
        [NoTranslate] public SlateRef<string> outSignalSiteGone;
        public SlateRef<Pawn> detainee;
        public SlateRef<Site> site;

        protected override bool TestRunInt(Slate slate) { return true; }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new RM_QuestPart_Breakout
            {
                inSignalEnable = QuestGen.quest.InitiateSignal,
                inSignalArrived = Sig.Of(inSignalArrived, slate),
                outSignalSiteGone = Sig.Out(outSignalSiteGone, slate),
                outSignalOut = Sig.Out(outSignalOut, slate),
                outSignalDead = Sig.Out(outSignalDead, slate),
                detainee = detainee.GetValue(slate),
                site = site.GetValue(slate),
            });
        }
    }

    public class RM_QuestPart_Breakout : QuestPartActivable
    {
        public string inSignalArrived, outSignalOut, outSignalDead, outSignalSiteGone;
        public Pawn detainee;
        public Site site;
        public bool armed, done;

        public override IEnumerable<GlobalTargetInfo> QuestLookTargets
        {
            get
            {
                foreach (GlobalTargetInfo t in base.QuestLookTargets) yield return t;
                if (detainee != null) yield return detainee;
            }
        }

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignalArrived || armed || detainee == null) return;
            armed = true;
            if (detainee.Dead) return;
            detainee.guest?.SetGuestStatus(null);
            detainee.SetFaction(Faction.OfPlayer);
            Messages.Message(detainee.LabelShort + " has broken his cuffs. He fights beside you until he is out.", detainee, MessageTypeDefOf.PositiveEvent, false);
        }

        public override void QuestPartTick()
        {
            base.QuestPartTick();
            if (done || Find.TickManager.TicksGame % 60 != 0) return;
            if (!armed)
            {
                // QuestNode_NoWorldObject cannot stand here: walking him off the map removes the site, and it would end the quest first
                if (site == null || site.Destroyed) { done = true; Sig.Send(outSignalSiteGone); }
                return;
            }
            if (detainee.Dead || detainee.Destroyed) { done = true; Sig.Send(outSignalDead); return; }
            Map onMap = detainee.MapHeld;
            if (onMap == null || onMap.Parent != site) { done = true; Sig.Send(outSignalOut); }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref outSignalOut, "outSignalOut");
            Scribe_Values.Look(ref outSignalDead, "outSignalDead");
            Scribe_Values.Look(ref inSignalArrived, "inSignalArrived");
            Scribe_Values.Look(ref outSignalSiteGone, "outSignalSiteGone");
            Scribe_Values.Look(ref armed, "armed");
            Scribe_Values.Look(ref done, "done");
            Scribe_References.Look(ref detainee, "detainee");
            Scribe_References.Look(ref site, "site");
        }
    }

    public class RM_QuestNode_PursuitRaid : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        public SlateRef<Faction> faction;
        public SlateRef<float> pointsFactor;

        protected override bool TestRunInt(Slate slate) { return true; }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new RM_QuestPart_PursuitRaid { inSignal = Sig.Of(inSignal, slate), faction = faction.GetValue(slate), pointsFactor = pointsFactor.GetValue(slate) });
        }
    }

    public class RM_QuestPart_PursuitRaid : QuestPart
    {
        public string inSignal;
        public Faction faction;
        public float pointsFactor = 1.5f;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal) return;
            Map home = Find.AnyPlayerHomeMap;
            if (home != null && faction != null) ArmorerRaids.Fire(home, faction, pointsFactor, false);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref pointsFactor, "pointsFactor");
            Scribe_References.Look(ref faction, "faction");
        }
    }

    public class RM_QuestNode_DetaineeLeaves : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        public SlateRef<Pawn> detainee;

        protected override bool TestRunInt(Slate slate) { return true; }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new RM_QuestPart_DetaineeLeaves { inSignal = Sig.Of(inSignal, slate), detainee = detainee.GetValue(slate) });
        }
    }

    public class RM_QuestPart_DetaineeLeaves : QuestPart
    {
        public string inSignal;
        public Pawn detainee;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal || detainee == null || detainee.Dead) return;
            Caravan c = detainee.GetCaravan();
            c?.RemovePawn(detainee);
            if (detainee.Spawned) detainee.ExitMap(false, Rot4.Invalid);
            if (!detainee.IsWorldPawn() && c != null) Find.WorldPawns.PassToWorld(detainee, PawnDiscardDecideMode.KeepForever);
            Faction pirate = Find.FactionManager.OfPirates;
            if (pirate != null) detainee.SetFaction(pirate);
            Find.LetterStack.ReceiveLetter("He pays his debt", detainee.LabelShort + " has gone back to Blackstar. He said the Creed keeps its debts, and left.", LetterDefOf.NeutralEvent, null, null, quest);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_References.Look(ref detainee, "detainee");
        }
    }

    public class RM_IncidentWorker_PrisonBreakOffer : IncidentWorker_GiveQuest
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            RM_ArmorerState s = RM_ArmorerState.Get;
            if (s == null || !BeskarArmorerSettings.modEnabled) return false;
            if (!ArmorerKernel.RouteTwoOffers(BeskarArmorerSettings.routeTwoEnabled, GenDate.DaysPassedSinceSettleFloat, BeskarArmorerSettings.prisonBreakEarliestDay,
                s.revealed || RM_ArmorerState.Covert != null, s.lost, RM_ArmorerState.RouteQuestRunning)) return false;
            return base.CanFireNowSub(parms);
        }
    }
}
