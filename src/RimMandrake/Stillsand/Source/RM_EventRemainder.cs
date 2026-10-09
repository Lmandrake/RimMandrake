using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_EVENT_CREATURES_REMAINDER_1 — the generic RM-tier machinery for the three
    // pieces whose canon data lives elsewhere (Q11a: this assembly names no canon creature):
    //
    //   §3 the horn      RM_CompUseEffect_Horn + RM_HornExtension. A usable item (the RSW
    //                    krayt horn is the shipped consumer; its sound, recipe and answer
    //                    incident are XML in SWBestiary / UtinniPatches). Blowing it routs
    //                    smaller predators and tribal raiders in a radius, then rolls the
    //                    Mod Settings answer chance to queue the extension's incident
    //                    (Find.Storyteller.incidentQueue) and LOGS the roll.
    //   §2 the den quest RM_QuestNode_GetCaveDen finds a player map whose precious cave is
    //                    a given row with its giant still inside, and RM_QuestNode_ClaimCaveDen
    //                    marks the den cleared when the quest says so. The QuestScriptDef is
    //                    RUT_KraytDenQuest (UtinniPatches).
    //   §4 loud draws    RM_LoudDrawExtension: things that call a leviathan like a drill does
    //                    (a landing or landed shuttle, patched on in RM_LoudDraws.xml).
    // ════════════════════════════════════════════════════════════════════

    // ── §3 the horn ───────────────────────────────────────────────────

    public class RM_HornExtension : DefModExtension
    {
        /// <summary>IncidentDef defName queued when a blow is answered. Added by the tier that owns it.</summary>
        public string answerIncident;

        /// <summary>Cells around the user whose smaller predators and tribal raiders are routed.</summary>
        public float radius = 30f;

        /// <summary>A predator at or under this body size is routed. Giants are not.</summary>
        public float maxRoutBodySize = 3f;

        /// <summary>Ticks before the same horn can be blown again.</summary>
        public int cooldownTicks = 15000;

        /// <summary>The answer arrives this long after a hit.</summary>
        public IntRange answerDelayTicks = new IntRange(2500, 7500);

        /// <summary>The queued incident keeps retrying for this long if it cannot fire at once.</summary>
        public int answerRetryTicks = 15000;
    }

    public static class RM_HornUtility
    {
        /// <summary>Routs every eligible pawn within radius of the user; returns how many.</summary>
        public static int Rout(Pawn user, RM_HornExtension ext)
        {
            Map map = user.Map;
            int routed = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
            {
                if (p == user || p.Dead || p.Downed || p.Faction == Faction.OfPlayer || p.InMentalState
                    || p.mindState == null || (p.Position - user.Position).LengthHorizontal > ext.radius)
                {
                    continue;
                }
                bool smallPredator = p.RaceProps.Animal && p.RaceProps.predator && p.BodySize <= ext.maxRoutBodySize;
                bool tribalRaider = p.RaceProps.Humanlike && p.Faction != null && p.Faction.HostileTo(Faction.OfPlayer)
                    && (int)p.Faction.def.techLevel <= (int)TechLevel.Neolithic;
                if (!(smallPredator || tribalRaider))
                {
                    continue;
                }
                if (p.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.PanicFlee, "krayt horn", forced: true))
                {
                    routed++;
                }
            }
            return routed;
        }

        /// <summary>Rolls the answer chance, logs the roll, queues the incident on a hit. Returns the roll line.</summary>
        public static string RollAnswer(Map map, RM_HornExtension ext, int routed, out bool answered)
        {
            float chance = Mathf.Clamp01(RM_StillsandEventsSettings.hornAnswerChance);
            float roll = Rand.Value;
            answered = roll < chance;
            IncidentDef inc = ext.answerIncident.NullOrEmpty() ? null : DefDatabase<IncidentDef>.GetNamedSilentFail(ext.answerIncident);
            string outcome;
            if (!answered)
            {
                outcome = "silence";
            }
            else if (inc == null)
            {
                outcome = "answered, but no answer incident is loaded";
                answered = false;
            }
            else
            {
                IncidentParms parms = StorytellerUtility.DefaultParmsNow(inc.category, map);
                parms.target = map;
                int when = Find.TickManager.TicksGame + ext.answerDelayTicks.RandomInRange;
                Find.Storyteller.incidentQueue.Add(inc, when, parms, ext.answerRetryTicks);
                outcome = "ANSWERED: " + inc.defName + " queued";
            }
            string line = "[Stillsand] krayt horn answer roll " + roll.ToString("F3") + " vs chance " + chance.ToString("F2")
                          + ": " + outcome + " (routed " + routed + ")";
            Log.Message(line);
            return line;
        }
    }

    public class RM_CompUseEffect_Horn : CompUseEffect
    {
        private int lastBlowTick = -999999;
        private string lastRoll;

        private RM_HornExtension Ext => parent.def.GetModExtension<RM_HornExtension>() ?? new RM_HornExtension();

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastBlowTick, "rmHornLastBlow", -999999);
            Scribe_Values.Look(ref lastRoll, "rmHornLastRoll");
        }

        public override AcceptanceReport CanBeUsedBy(Pawn p)
        {
            if (!RM_StillsandEventsSettings.hornEnabled)
            {
                return "The horn is switched off in Mod Settings.";
            }
            int wait = lastBlowTick + Ext.cooldownTicks - Find.TickManager.TicksGame;
            if (wait > 0)
            {
                return "Still ringing: blow it again in " + wait.ToStringTicksToPeriod() + ".";
            }
            return base.CanBeUsedBy(p);
        }

        public override void DoEffect(Pawn usedBy)
        {
            base.DoEffect(usedBy);
            if (usedBy?.Map == null || !RM_StillsandEventsSettings.hornEnabled)
            {
                return;
            }
            lastBlowTick = Find.TickManager.TicksGame;
            int routed = RM_HornUtility.Rout(usedBy, Ext);
            lastRoll = RM_HornUtility.RollAnswer(usedBy.Map, Ext, routed, out _);
            Messages.Message("The horn rolls out over the dunes. " + routed + " creature" + (routed == 1 ? "" : "s") + " broke and ran.",
                usedBy, MessageTypeDefOf.NeutralEvent, false);
        }

        public override string CompInspectStringExtra()
        {
            return lastRoll.NullOrEmpty() ? null : "Last blow: " + lastRoll.Replace("[Stillsand] krayt horn ", "");
        }
    }

    // ── §4 loud draws ─────────────────────────────────────────────────

    /// <summary>On a ThingDef: it calls a sand leviathan the way a working deep drill does.</summary>
    public class RM_LoudDrawExtension : DefModExtension
    {
        public string label = "a loud thing";
    }

    public static class RM_LoudDraws
    {
        private static List<ThingDef> loudDefs;

        /// <summary>The first spawned thing on the map whose def carries RM_LoudDrawExtension, or null.</summary>
        public static Thing First(Map map)
        {
            if (loudDefs == null)
            {
                // Resolved once: the def set is fixed after load (belt SS-1).
                loudDefs = new List<ThingDef>();
                List<ThingDef> all = DefDatabase<ThingDef>.AllDefsListForReading;
                for (int i = 0; i < all.Count; i++)
                {
                    if (all[i].GetModExtension<RM_LoudDrawExtension>() != null)
                    {
                        loudDefs.Add(all[i]);
                    }
                }
            }
            List<ThingDef> defs = loudDefs;
            for (int i = 0; i < defs.Count; i++)
            {
                List<Thing> things = map.listerThings.ThingsOfDef(defs[i]);
                for (int j = 0; j < things.Count; j++)
                {
                    if (things[j].Spawned)
                    {
                        return things[j];
                    }
                }
            }
            return null;
        }
    }

    // ── §2 the den quest ──────────────────────────────────────────────

    /// <summary>Quest node: finds a player home map whose precious cave is `caveRow` and whose giant
    /// (`pawnKind`) is still alive inside it. Fails the quest's selection (TestRunInt false) otherwise,
    /// and when the Mod Settings toggle is off. Stores the map, the pawn and the den cell on the slate.</summary>
    public class RM_QuestNode_GetCaveDen : QuestNode
    {
        [NoTranslate] public SlateRef<string> caveRow;
        [NoTranslate] public SlateRef<string> pawnKind;
        [NoTranslate] public SlateRef<string> storeMapAs;
        [NoTranslate] public SlateRef<string> storePawnAs;
        [NoTranslate] public SlateRef<string> storeCellAs;
        [NoTranslate] public SlateRef<string> storeCompassAs;

        public static bool TryFindDen(string row, string kind, out Map map, out Pawn pawn, out RM_MapComponent_PreciousCave comp)
        {
            map = null;
            pawn = null;
            comp = null;
            if (row.NullOrEmpty() || kind.NullOrEmpty())
            {
                return false;
            }
            foreach (Map m in Find.Maps)
            {
                RM_MapComponent_PreciousCave c = m.IsPlayerHome ? RM_MapComponent_PreciousCave.For(m) : null;
                if (c == null || !c.hasCave || c.denCleared || c.rowDefName != row)
                {
                    continue;
                }
                Pawn found = m.mapPawns.AllPawnsSpawned.FirstOrDefault(p => !p.Dead && p.Faction == null
                    && p.kindDef != null && p.kindDef.defName == kind);
                if (found != null)
                {
                    map = m;
                    pawn = found;
                    comp = c;
                    return true;
                }
            }
            return false;
        }

        private void Store(Slate slate, Map map, Pawn pawn, RM_MapComponent_PreciousCave comp)
        {
            slate.Set(storeMapAs.GetValue(slate) ?? "map", map);
            slate.Set(storePawnAs.GetValue(slate) ?? "denPawn", pawn);
            slate.Set(storeCellAs.GetValue(slate) ?? "denCell", pawn.Position);
            slate.Set(storeCompassAs.GetValue(slate) ?? "denCompass", comp.compassWord.NullOrEmpty() ? "desert" : comp.compassWord);
        }

        protected override bool TestRunInt(Slate slate)
        {
            if (!RM_StillsandEventsSettings.denQuestEnabled
                || !TryFindDen(caveRow.GetValue(slate), pawnKind.GetValue(slate), out Map map, out Pawn pawn, out RM_MapComponent_PreciousCave comp))
            {
                return false;
            }
            Store(slate, map, pawn, comp);
            return true;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            if (TryFindDen(caveRow.GetValue(slate), pawnKind.GetValue(slate), out Map map, out Pawn pawn, out RM_MapComponent_PreciousCave comp))
            {
                Store(slate, map, pawn, comp);
            }
        }
    }

    /// <summary>Quest node: on `inSignal`, the den is cleared; it stops being held and becomes a precious
    /// cave (preservation resumes), with a letter.</summary>
    public class RM_QuestNode_ClaimCaveDen : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        public SlateRef<Map> map;
        public SlateRef<string> letterLabel;
        public SlateRef<string> letterText;

        protected override bool TestRunInt(Slate slate)
        {
            return true;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            Map m = map.GetValue(slate);
            if (m == null)
            {
                return;
            }
            RM_QuestPart_CaveDenCleared part = new RM_QuestPart_CaveDenCleared
            {
                inSignal = QuestGenUtility.HardcodedSignalWithQuestID(inSignal.GetValue(slate)) ?? slate.Get<string>("inSignal"),
                mapParent = m.Parent,
                letterLabel = letterLabel.GetValue(slate),
                letterText = letterText.GetValue(slate),
            };
            QuestGen.quest.AddPart(part);
        }
    }

    public class RM_QuestPart_CaveDenCleared : QuestPart
    {
        public string inSignal;
        public MapParent mapParent;
        public string letterLabel;
        public string letterText;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal || mapParent == null || !mapParent.HasMap)
            {
                return;
            }
            RM_MapComponent_PreciousCave comp = RM_MapComponent_PreciousCave.For(mapParent.Map);
            if (comp == null)
            {
                return;
            }
            comp.denCleared = true;
            Find.LetterStack.ReceiveLetter(letterLabel.NullOrEmpty() ? "The den is cleared" : letterLabel,
                letterText.NullOrEmpty() ? "The den is empty. The cave is yours." : letterText,
                LetterDefOf.PositiveEvent,
                comp.lookCell.IsValid ? new LookTargets(new TargetInfo(comp.lookCell, mapParent.Map)) : LookTargets.Invalid);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_References.Look(ref mapParent, "mapParent");
            Scribe_Values.Look(ref letterLabel, "letterLabel");
            Scribe_Values.Look(ref letterText, "letterText");
        }
    }
}
