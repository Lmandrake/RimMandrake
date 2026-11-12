using System.Collections.Generic;
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
    // read the Mod Settings toggles, hand a manhunter pack's race to QuestNode_PawnsKilled, and set a gift down by
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

    /// <summary>Stores the race of a PawnKindDef already on the slate (QuestNode_ManhunterPack leaves the pack's kind in
    /// animalKindDef; QuestNode_PawnsKilled wants a race ThingDef, and a SlateRef cannot read a member).</summary>
    public class RUT_QuestNode_GetRaceOfKind : QuestNode
    {
        public SlateRef<PawnKindDef> kind;

        [NoTranslate]
        public SlateRef<string> storeAs;

        // QuestNode_ManhunterPack sets animalKindDef only in RunInt, never in its TestRun, so at test time the kind is
        // simply not there yet: that is not a refusal (refusing would make the quest ungeneratable).
        protected override bool TestRunInt(Slate slate)
        {
            return kind.GetValue(slate) == null || SetVar(slate);
        }

        protected override void RunInt()
        {
            SetVar(QuestGen.slate);
        }

        private bool SetVar(Slate slate)
        {
            PawnKindDef k = kind.GetValue(slate);
            if (k?.race == null) return false;
            slate.Set(storeAs.GetValue(slate), k.race);
            return true;
        }
    }
}
