using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using LudeonTK;
using RimWorld;
using RimWorld.BaseGen;
using RimWorld.Planet;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_WORLD_FOUNDRY_1 — the line runs in the world (owner Q1=A, 2026-10-03; design
    /// droid_mass_production_quest_chain_2026-10-02.md §4.2, §4.4). The Enclaves hold the line and the player gets its
    /// fruits: no player-owned line building, and the line never makes heads or pawns.
    ///
    /// "The line stands" from the moment the chain's epilogue sets GameComponent_RUT_UnfinishedLine.lineCompleted, until
    /// a volunteer is bolted or wiped (the Enclaves' conditions, §4.4 brake 4). While it stands:
    ///   regrowth    Enclave settlement maps generate more defenders, rising from 1x to a cap over N days
    ///               (prefix on SymbolResolver_Settlement.Resolve; vanilla settlements only).
    ///   stock       every Enclave trader (settlement, caravan) adds Foundry-grade frames and part sets: the donor-tier
    ///               part ThingDefs at fixed Good quality, so they always install into the STANDARD bucket
    ///               (DroidAssembly.BucketedHediff): better than Primitive, never the donor's Excellent+. Never heads,
    ///               never the brain trio (postfix on ThingSetMaker_TraderStock.Generate, filtered on makingFaction).
    ///   heat        accrues per day; IncidentDef RUT_FoundryStrike can fire only once heat reaches the threshold and
    ///               weighs more the hotter the line runs; a strike resets heat.
    ///   volunteers  on a timer, while the Enclaves are your allies and under the cap, RUT_LineVolunteer is offered: one
    ///               re-bodied free droid who chooses to join. Bolting or wiping one collapses Enclave goodwill and the
    ///               line stops running for you.
    /// All numbers are PROVISIONAL (Mod Settings).
    /// </summary>
    public class WorldComponent_RUT_EnclaveFoundry : WorldComponent
    {
        public const string VolunteerQuestDefName = "RUT_LineVolunteer";
        private const int TickInterval = 2500;

        public float standingDays;
        public float heat;
        public int nextVolunteerTick = -1;
        public int volunteersArrived;
        public bool betrayed;
        public List<Pawn> volunteers = new List<Pawn>();

        public WorldComponent_RUT_EnclaveFoundry(World world) : base(world)
        {
        }

        public static WorldComponent_RUT_EnclaveFoundry Get => Find.World?.GetComponent<WorldComponent_RUT_EnclaveFoundry>();

        public static bool LineCompleted => GameComponent_RUT_UnfinishedLine.Get?.lineCompleted == true;

        /// <summary>The line is running in the world for the player right now.</summary>
        public bool LineRuns
        {
            get
            {
                if (!UnfinishedLineSettings.lineInWorldEnabled || betrayed || !LineCompleted) return false;
                Faction e = LineFactions.Enclaves;
                return e != null && !e.defeated;
            }
        }

        public float RegrowthFactor
        {
            get
            {
                if (!LineRuns) return 1f;
                float full = Mathf.Max(1f, UnfinishedLineSettings.regrowthDaysToFull);
                return 1f + (UnfinishedLineSettings.regrowthMaxFactor - 1f) * Mathf.Clamp01(standingDays / full);
            }
        }

        public bool StrikeReady => LineRuns && UnfinishedLineSettings.empireStrikesEnabled
            && heat >= UnfinishedLineSettings.strikeHeatThreshold;

        public override void WorldComponentTick()
        {
            if (Find.TickManager.TicksGame % TickInterval != 0 || !LineRuns) return;
            float days = TickInterval / (float)GenDate.TicksPerDay;
            standingDays += days;
            if (UnfinishedLineSettings.empireStrikesEnabled)
            {
                // Capped at three thresholds' worth: the strike weight stops rising there (ChanceFactorNow).
                heat = Mathf.Min(heat + UnfinishedLineSettings.lineHeatPerDay * days, UnfinishedLineSettings.strikeHeatThreshold * 3f);
            }
            CheckBetrayal();
            if (!betrayed) TickVolunteers();
        }

        // ---------------------------------------------------------------- volunteers

        public string VolunteerBlocker()
        {
            if (!LineRuns) return "line not running";
            if (UnfinishedLineSettings.volunteerDays <= 0) return "volunteers off (rate 0)";
            if (volunteersArrived >= UnfinishedLineSettings.volunteerCap) return "cap reached " + volunteersArrived;
            Faction e = LineFactions.Enclaves;
            if (e == null || e.RelationKindWith(Faction.OfPlayer) != FactionRelationKind.Ally) return "Enclaves not allied";
            if (Find.AnyPlayerHomeMap == null) return "no home map";
            if (Find.QuestManager.QuestsListForReading.Any(q => q.root != null && q.root.defName == VolunteerQuestDefName
                    && (q.State == QuestState.NotYetAccepted || q.State == QuestState.Ongoing)))
                return "a volunteer is already offered";
            return null;
        }

        private void ScheduleNext(float days)
        {
            nextVolunteerTick = Find.TickManager.TicksGame + Mathf.Max(GenDate.TicksPerDay, (int)(days * GenDate.TicksPerDay));
        }

        private void TickVolunteers()
        {
            if (UnfinishedLineSettings.volunteerDays <= 0) return;
            if (nextVolunteerTick < 0)
            {
                ScheduleNext(UnfinishedLineSettings.volunteerDays * Rand.Range(0.8f, 1.2f));
                return;
            }
            if (Find.TickManager.TicksGame < nextVolunteerTick) return;
            if (VolunteerBlocker() != null || TryOfferVolunteer() != null)
            {
                ScheduleNext(1f); // not now: look again tomorrow
                return;
            }
            ScheduleNext(UnfinishedLineSettings.volunteerDays * Rand.Range(0.8f, 1.2f));
        }

        /// <summary>Offers RUT_LineVolunteer now. Returns null on success, else why not.</summary>
        public string TryOfferVolunteer()
        {
            QuestScriptDef def = DefDatabase<QuestScriptDef>.GetNamedSilentFail(VolunteerQuestDefName);
            Map home = Find.AnyPlayerHomeMap;
            if (def == null) return "no " + VolunteerQuestDefName;
            if (home == null) return "no home map";
            Slate slate = new Slate();
            slate.Set("points", StorytellerUtility.DefaultThreatPointsNow(home));
            if (!def.CanRun(slate, home)) return VolunteerQuestDefName + " cannot run now (TestRun false)";
            Quest quest = QuestUtility.GenerateQuestAndMakeAvailable(def, slate);
            if (!quest.hidden && quest.root.sendAvailableLetter)
            {
                QuestUtility.SendLetterQuestAvailable(quest);
            }
            return null;
        }

        /// <summary>A volunteer has arrived. They come free: any bolt or wipe mark a generator left on them is removed
        /// here, so the watch below only ever sees what the colony did.</summary>
        public void RegisterVolunteer(Pawn p)
        {
            if (p == null || volunteers.Contains(p)) return;
            foreach (HediffDef h in ControlHediffs())
            {
                Hediff found;
                while ((found = p.health.hediffSet.GetFirstHediffOfDef(h)) != null)
                {
                    p.health.RemoveHediff(found);
                }
            }
            volunteers.Add(p);
            volunteersArrived++;
        }

        private static List<HediffDef> controlHediffs;

        private static List<HediffDef> ControlHediffs()
        {
            if (controlHediffs == null)
            {
                controlHediffs = new[] { "RSW_DW_RestrainingBolt", "OuterRim_RestraintBolt", "RSW_DW_RecentlyWiped" }
                    .Select(n => DefDatabase<HediffDef>.GetNamedSilentFail(n)).Where(h => h != null).ToList();
            }
            return controlHediffs;
        }

        private void CheckBetrayal()
        {
            volunteers.RemoveAll(p => p == null || p.Destroyed || p.Dead);
            List<HediffDef> marks = ControlHediffs();
            foreach (Pawn p in volunteers)
            {
                if (p.Faction == Faction.OfPlayer && marks.Any(h => p.health.hediffSet.HasHediff(h)))
                {
                    Betray(p);
                    return;
                }
            }
        }

        public void Betray(Pawn p)
        {
            betrayed = true;
            Faction e = LineFactions.Enclaves;
            if (e != null && UnfinishedLineSettings.volunteerBetrayalGoodwill > 0)
            {
                e.TryAffectGoodwillWith(Faction.OfPlayer, -UnfinishedLineSettings.volunteerBetrayalGoodwill,
                    canSendMessage: true, canSendHostilityLetter: true,
                    reason: DefDatabase<HistoryEventDef>.GetNamedSilentFail("RUT_LineVolunteerBolted"));
            }
            Find.LetterStack.ReceiveLetter("The line is closed to you",
                (p != null ? p.LabelShortCap : "A volunteer") + " came to you born free, and you put a bolt in them or wiped them. "
                + (e != null ? e.Name : "The Enclaves") + " have heard.\n\nThe line still runs, but not for the Jawa: no more "
                + "volunteers, no Foundry-grade frames in their stock, and their settlements no longer grow for you.",
                LetterDefOf.NegativeEvent, p);
        }

        public string Describe()
        {
            return "WORLD runs=" + LineRuns + " completed=" + LineCompleted + " setting=" + UnfinishedLineSettings.lineInWorldEnabled
                + " betrayed=" + betrayed + " standingDays=" + standingDays.ToString("0.0") + " regrowth=" + RegrowthFactor.ToString("0.00")
                + " heat=" + heat.ToString("0.0") + "/" + UnfinishedLineSettings.strikeHeatThreshold + " strikeReady=" + StrikeReady
                + " volunteers=" + volunteersArrived + "/" + UnfinishedLineSettings.volunteerCap + " watched=" + volunteers.Count
                + " nextVolunteerTick=" + nextVolunteerTick + " blocker=" + (VolunteerBlocker() ?? "none");
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref standingDays, "standingDays", 0f);
            Scribe_Values.Look(ref heat, "heat", 0f);
            Scribe_Values.Look(ref nextVolunteerTick, "nextVolunteerTick", -1);
            Scribe_Values.Look(ref volunteersArrived, "volunteersArrived", 0);
            Scribe_Values.Look(ref betrayed, "betrayed", false);
            Scribe_Collections.Look(ref volunteers, "volunteers", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (volunteers == null) volunteers = new List<Pawn>();
                volunteers.RemoveAll(p => p == null);
            }
        }
    }

    // ---------------------------------------------------------------- Foundry-grade stock

    public static class EnclaveFoundryStock
    {
        public const QualityCategory FoundryQuality = QualityCategory.Good;

        public static readonly string[] FrameDefs = { "RSW_DW_Part_Frame" };

        public static readonly string[] PartSetDefs =
        {
            "RSW_DW_Part_Leg", "RSW_DW_Part_Manipulator", "RSW_DW_Part_Sensor",
            "RSW_DW_Part_Motivator", "RSW_DW_Part_Servo", "RSW_DW_Part_PowerCell"
        };

        public static int AddTo(Faction makingFaction, List<Thing> outThings)
        {
            if (makingFaction == null || outThings == null || makingFaction != LineFactions.Enclaves) return 0;
            WorldComponent_RUT_EnclaveFoundry c = WorldComponent_RUT_EnclaveFoundry.Get;
            if (c == null || !c.LineRuns) return 0;
            int added = 0;
            for (int i = 0; i < UnfinishedLineSettings.stockFrames; i++)
            {
                added += AddAll(FrameDefs, outThings);
            }
            for (int i = 0; i < UnfinishedLineSettings.stockPartSets; i++)
            {
                added += AddAll(PartSetDefs, outThings);
            }
            return added;
        }

        private static int AddAll(string[] defNames, List<Thing> outThings)
        {
            int n = 0;
            foreach (string name in defNames)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (def == null) continue;
                Thing t = ThingMaker.MakeThing(def);
                t.TryGetComp<CompQuality>()?.SetQuality(FoundryQuality, ArtGenerationContext.Outsider);
                outThings.Add(t);
                n++;
            }
            return n;
        }
    }

    [HarmonyPatch(typeof(ThingSetMaker_TraderStock), "Generate", new[] { typeof(ThingSetMakerParams), typeof(List<Thing>) })]
    public static class ThingSetMaker_TraderStock_Generate_FoundryStock
    {
        public static void Postfix(ThingSetMakerParams parms, List<Thing> outThings)
        {
            EnclaveFoundryStock.AddTo(parms.makingFaction, outThings);
        }
    }

    // ---------------------------------------------------------------- regrowth

    [HarmonyPatch(typeof(SymbolResolver_Settlement), nameof(SymbolResolver_Settlement.Resolve))]
    public static class SymbolResolver_Settlement_Resolve_EnclaveRegrowth
    {
        public static void Prefix(ref ResolveParams rp)
        {
            if (rp.settlementPawnGroupPoints.HasValue || rp.faction == null || rp.settlementDontGeneratePawns == true) return;
            if (rp.faction != LineFactions.Enclaves) return;
            float f = WorldComponent_RUT_EnclaveFoundry.Get?.RegrowthFactor ?? 1f;
            if (f > 1f)
            {
                rp.settlementPawnGroupPoints = SymbolResolver_Settlement.DefaultPawnsPoints.RandomInRange * f;
            }
        }
    }

    // ---------------------------------------------------------------- the Empire's Foundry strikes

    /// <summary>RUT_FoundryStrike: an ordinary enemy raid by the strike faction (the Empire when it is hostile, as in
    /// First Light), possible only once line heat reaches the threshold, weighted by how far past it the heat runs.
    /// It comes to your colony: where the line stands (UNFINISHED_LINE_SITE_CHOICE_1) is not built yet.</summary>
    public class IncidentWorker_RUT_FoundryStrike : IncidentWorker_RaidEnemy
    {
        public override float ChanceFactorNow(IIncidentTarget target)
        {
            WorldComponent_RUT_EnclaveFoundry c = WorldComponent_RUT_EnclaveFoundry.Get;
            if (c == null || !c.StrikeReady) return 0f;
            return Mathf.Clamp(c.heat / Mathf.Max(1f, UnfinishedLineSettings.strikeHeatThreshold), 0f, 3f);
        }

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            WorldComponent_RUT_EnclaveFoundry c = WorldComponent_RUT_EnclaveFoundry.Get;
            if (c == null || !c.StrikeReady) return false;
            if (QuestNode_RUT_FirstLightSetup.StrikeFaction() == null) return false;
            return base.CanFireNowSub(parms);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Faction f = QuestNode_RUT_FirstLightSetup.StrikeFaction();
            if (f == null) return false;
            parms.faction = f;
            if (parms.customLetterText.NullOrEmpty())
            {
                parms.customLetterText = "{BASETEXT}\n\nThe Enclaves' line has been running hot, and someone has been counting the frames. "
                    + "This is a Foundry strike: they have come for the people who helped build it.";
            }
            if (!base.TryExecuteWorker(parms)) return false;
            WorldComponent_RUT_EnclaveFoundry c = WorldComponent_RUT_EnclaveFoundry.Get;
            if (c != null) c.heat = 0f;
            return true;
        }
    }

    // ---------------------------------------------------------------- the volunteer quest's one verb

    /// <summary>Registers the volunteer(s) with the foundry watch on its signal (the quest's acceptance by default).</summary>
    public class QuestPart_RUT_LineVolunteers : QuestPart
    {
        public string inSignal;
        public List<Pawn> pawns = new List<Pawn>();

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal) return;
            WorldComponent_RUT_EnclaveFoundry c = WorldComponent_RUT_EnclaveFoundry.Get;
            if (c == null) return;
            foreach (Pawn p in pawns)
            {
                c.RegisterVolunteer(p);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Collections.Look(ref pawns, "pawns", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (pawns == null) pawns = new List<Pawn>();
                pawns.RemoveAll(p => p == null);
            }
        }
    }

    public class QuestNode_RUT_LineVolunteers : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        public SlateRef<IEnumerable<Pawn>> pawns;

        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestPart_RUT_LineVolunteers part = new QuestPart_RUT_LineVolunteers
            {
                inSignal = QuestGenUtility.HardcodedSignalWithQuestID(inSignal.GetValue(slate)) ?? slate.Get<string>("inSignal")
            };
            IEnumerable<Pawn> ps = pawns.GetValue(slate);
            if (ps != null) part.pawns.AddRange(ps.Where(p => p != null));
            QuestGen.quest.AddPart(part);
        }
    }

    // ---------------------------------------------------------------- proofs and dev actions

    public static class UnfinishedLineWorldProof
    {
        /// <summary>jawa/static_call. "state" | "stand" (dev: mark the line completed) | "stock" | "heat N" | "volunteer"
        /// | "betray" (dev: bolt-free betrayal, flips the flag only).</summary>
        public static string ProofWorld(string action)
        {
            WorldComponent_RUT_EnclaveFoundry c = WorldComponent_RUT_EnclaveFoundry.Get;
            if (c == null) return "NO WORLD COMPONENT";
            string a = (action ?? "state").Trim();
            if (a == "stand")
            {
                GameComponent_RUT_UnfinishedLine.Get?.SetFlag("lineCompleted");
                return c.Describe();
            }
            if (a.StartsWith("heat"))
            {
                if (float.TryParse(a.Substring(4).Trim(), out float h)) c.heat = h;
                return c.Describe();
            }
            if (a == "volunteer")
            {
                string why = c.VolunteerBlocker() ?? c.TryOfferVolunteer();
                return (why == null ? "VOLUNTEER OFFERED | " : "VOLUNTEER REFUSED: " + why + " | ") + c.Describe();
            }
            if (a == "betray")
            {
                c.betrayed = true;
                return c.Describe();
            }
            if (a == "stock")
            {
                Faction e = LineFactions.Enclaves;
                TraderKindDef td = e?.def.baseTraderKinds?.FirstOrDefault() ?? e?.def.caravanTraderKinds?.FirstOrDefault();
                if (td == null) return "STOCK no Enclave trader kind";
                List<Thing> things = ThingSetMakerDefOf.TraderStock.root.Generate(new ThingSetMakerParams { traderDef = td, makingFaction = e });
                HashSet<string> foundry = new HashSet<string>(EnclaveFoundryStock.FrameDefs.Concat(EnclaveFoundryStock.PartSetDefs));
                List<Thing> f = things.Where(t => foundry.Contains(t.def.defName)).ToList();
                int good = f.Count(t => t.TryGetComp<CompQuality>()?.Quality == EnclaveFoundryStock.FoundryQuality);
                int heads = things.Count(t => t.def.defName.StartsWith("RSW_DW_Head_"));
                return "STOCK " + td.defName + " total " + things.Count + " foundry " + f.Count + " good " + good + " heads " + heads
                    + " | " + c.Describe();
            }
            return c.Describe();
        }

        [DebugAction("Quests", "Unfinished Line: the line runs in the world now", allowedGameStates = AllowedGameStates.Playing)]
        private static void DebugStand()
        {
            Messages.Message(ProofWorld("stand"), MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Quests", "Unfinished Line: offer a line volunteer now", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DebugVolunteer()
        {
            Messages.Message(ProofWorld("volunteer"), MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Quests", "Unfinished Line: line heat to strike threshold", allowedGameStates = AllowedGameStates.Playing)]
        private static void DebugHeat()
        {
            Messages.Message(ProofWorld("heat " + UnfinishedLineSettings.strikeHeatThreshold), MessageTypeDefOf.NeutralEvent, false);
        }
    }
}
