using System.Collections.Generic;
using System.Linq;
using RimWorld.Planet;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.CathedralPass
{
    // CATHEDRAL_MISSION_BOON_OFFERS_1 — the in-game half of the Cathedral's favours (arc spec §3 bullet 3).
    //
    // WHEN a mission or a boon is offered is decided out of game, by the GM blackboard
    // (src/RimMandrake/Utils/gm_blackboard_shadow.py, compute_cathedral_offers): missions at TOLERATED+, boons at
    // VOUCHED, each boon only while Imperial Heat is under its own heatCeiling, both closed by a go-dark flip. The
    // blackboard fires these defs through jawa/storyteller_fire; every one is baseChance 0 / rootSelectionWeight 0,
    // so the storyteller never rolls them on its own. What lives here is only what an XML-only def cannot do:
    // read the Mod Settings toggles, finish a mission only when its own pack is dead, and set a gift down by
    // the ship with its letter. No Harmony, no LLM, nothing that names the Cathedral.

    /// <summary>A GiveQuest incident for one RUT_CathedralAssailantMission_* quest, gated on the missions toggle.</summary>
    public class IncidentWorker_GiveQuest_CathedralMission : IncidentWorker_GiveQuest
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            return CathedralPassSettings.cathedralMissionsEnabled && base.CanFireNowSub(parms);
        }
    }

    /// <summary>What a gravtech boon leaves by the ship, the Imperial Heat above which the blackboard withholds it, and
    /// how long before it may come again. The game never reads heatCeiling or reofferDays (Heat and cadence live only in
    /// the blackboard); they sit on the def so each number has one home, read by
    /// gm_blackboard_shadow.load_cathedral_offer_catalogue.</summary>
    public class RUT_CathedralBoonExtension : DefModExtension
    {
        public List<ThingDefCountClass> gifts = new List<ThingDefCountClass>();
        public float heatCeiling = 10f;
        public float reofferDays = 15f;   // blackboard-only too: the least time before the same gift comes again
        public float quietDays = 0f;      // blackboard-only too: game days since the last kyber sale before it may come
    }

    /// <summary>A gravtech boon: the extension's gifts are set down at the ship's trade drop spot, unannounced, with the
    /// def's own letterLabel/letterText. Fires only on a player home map, only with the boons toggle on.</summary>
    public class IncidentWorker_CathedralBoon : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!CathedralPassSettings.cathedralBoonsEnabled) return false;
            Map map = parms.target as Map;
            RUT_CathedralBoonExtension ext = def.GetModExtension<RUT_CathedralBoonExtension>();
            return map != null && map.IsPlayerHome && ext != null && ext.gifts.Count > 0;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            RUT_CathedralBoonExtension ext = def.GetModExtension<RUT_CathedralBoonExtension>();
            IntVec3 spot = DropCellFinder.TradeDropSpot(map);
            var placed = new List<Thing>();
            foreach (ThingDefCountClass gift in ext.gifts)
            {
                int left = gift.count;
                while (left > 0)
                {
                    Thing thing = ThingMaker.MakeThing(gift.thingDef, gift.thingDef.MadeFromStuff ? GenStuff.DefaultStuffFor(gift.thingDef) : null);
                    thing.stackCount = System.Math.Min(left, thing.def.stackLimit);
                    left -= thing.stackCount;
                    if (GenPlace.TryPlaceThing(thing, spot, map, ThingPlaceMode.Near, out Thing result))
                        placed.Add(result);
                }
            }
            if (placed.Count == 0) return false;
            SendStandardLetter(parms, new LookTargets(placed));
            return true;
        }
    }

    /// <summary>Adds a RUT_QuestPart_PackDown for the pack QuestNode_ManhunterPack spawned under the same quest tag.
    /// Replaces vanilla QuestNode_PawnsKilled, which counts ANY pawn of the pack's race the colony kills: slaughtering
    /// your own tame animals of that race finished the mission while the pack still roamed (found 2026-11-11).</summary>
    public class RUT_QuestNode_PackDown : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignalEnable;
        [NoTranslate] public SlateRef<string> tag;
        [NoTranslate] public SlateRef<string> outSignalPackDown;
        [NoTranslate] public SlateRef<string> outSignalPackLost;

        protected override bool TestRunInt(Slate slate)
        {
            return slate.Exists("map") && !tag.GetValue(slate).NullOrEmpty();
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            var part = new RUT_QuestPart_PackDown
            {
                inSignalEnable = QuestGenUtility.HardcodedSignalWithQuestID(inSignalEnable.GetValue(slate)) ?? slate.Get<string>("inSignal"),
                questTag = QuestGenUtility.HardcodedTargetQuestTagWithQuestID(tag.GetValue(slate)),
                mapParent = slate.Get<Map>("map").Parent,
                outSignalPackLost = QuestGenUtility.HardcodedSignalWithQuestID(outSignalPackLost.GetValue(slate)),
            };
            if (!outSignalPackDown.GetValue(slate).NullOrEmpty())
                part.outSignalsCompleted.Add(QuestGenUtility.HardcodedSignalWithQuestID(outSignalPackDown.GetValue(slate)));
            QuestGen.quest.AddPart(part);
        }
    }

    /// <summary>Completes when every pawn that carried the quest's pack tag is dead. Sends outSignalPackLost instead if
    /// the pack never reaches the map within PackArrivalTicks, or if the last living pack animal is off the map (it
    /// walked off) or the colony's own (tamed): none of those is a kill, so none earns the mission.</summary>
    public class RUT_QuestPart_PackDown : QuestPartActivable
    {
        public const int PackArrivalTicks = 2 * GenDate.TicksPerDay;
        public string questTag;
        public MapParent mapParent;
        public string outSignalPackLost;
        private List<Pawn> pack = new List<Pawn>();

        public override string DescriptionPart
        {
            get
            {
                if (State != QuestPartState.Enabled || pack.Count == 0) return null;
                return "Animals gone wrong not yet down: " + pack.Count(p => p != null && !p.Dead) + " / " + pack.Count;
            }
        }

        // Keep the pack's pawns (dead ones too) out of world-pawn GC while the part runs: the list holds them by
        // reference, and a discarded pawn reloads as a "Could not resolve reference" warning (WorldPawnGC).
        public override bool QuestPartReserves(Pawn p)
        {
            return State == QuestPartState.Enabled && pack.Contains(p);
        }

        // An ended quest no longer reserves anything, so world-pawn GC may still discard a pack animal later (one that
        // walked off, or whose corpse is gone); drop it from the list then, or the save holds a dead reference.
        public override void Notify_PawnDiscarded(Pawn pawn)
        {
            base.Notify_PawnDiscarded(pawn);
            pack.Remove(pawn);
        }

        public override void QuestPartTick()
        {
            base.QuestPartTick();
            if (Find.TickManager.TicksGame % 250 != 0) return;
            Map map = mapParent?.Map;
            if (map == null) return;   // map.MapRemoved ends the quest in XML
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
                if (p.questTags != null && p.questTags.Contains(questTag) && !pack.Contains(p))
                    pack.Add(p);
            if (pack.Count == 0)
            {
                if (Find.TickManager.TicksGame - enableTick > PackArrivalTicks) Lost();
                return;
            }
            // MapHeld, not Map: a downed pack animal being carried is still here, not gone
            if (pack.Any(p => p != null && !p.Dead && p.Faction != Faction.OfPlayer && p.MapHeld == map)) return;
            if (pack.All(p => p == null || p.Dead)) Complete();
            else Lost();   // one walked off alive, or now belongs to the colony: either way it was not culled
        }

        private void Lost()
        {
            if (!outSignalPackLost.NullOrEmpty()) Find.SignalManager.SendSignal(new Signal(outSignalPackLost));
            Disable();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref questTag, "questTag");
            Scribe_References.Look(ref mapParent, "mapParent");
            Scribe_Values.Look(ref outSignalPackLost, "outSignalPackLost");
            Scribe_Collections.Look(ref pack, "pack", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && pack == null) pack = new List<Pawn>();
        }
    }
}
