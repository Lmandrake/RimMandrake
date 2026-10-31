// FLOOD_WITNESS_EVENT_1: the quest-facing half of the production arm-the-flood verb (RM_MapComponent_CanyonFlood.ArmFlood).
// The flood-witness quest (design/Jawa/quests/flood_witness_invitation_quest.md §6, "dependency contract") arms the canyon's
// chime-and-flood cycle on the site map when that map generates, never on accept; the map does not exist at quest generation,
// so the node stores the site (a MapParent) and the part looks its map up when inSignal arrives. Every pacing, terrain, damage
// and audio rule stays the map component's.
//
//   <li Class="RimMandrake.CrackedLands.RM_QuestNode_ArmCanyonFlood">
//     <inSignal>site.MapGenerated</inSignal>
//     <mapParent>$site</mapParent>
//     <wallInHours>32</wallInHours>
//     <outSignalArmed>FloodArmed</outSignalArmed>        (optional)
//     <outSignalRefused>FloodRefused</outSignalRefused>  (optional)
//   </li>
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.CrackedLands
{
    public class RM_QuestPart_ArmCanyonFlood : QuestPart
    {
        public string inSignal;
        public string outSignalArmed;
        public string outSignalRefused;
        public MapParent mapParent;
        public int wallInTicks;
        public bool fired;

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (fired || inSignal.NullOrEmpty() || signal.tag != inSignal)
            {
                return;
            }
            fired = true;
            string result = Arm();
            bool ok = result.StartsWith("OK");
            string line = "[CrackedLands] quest " + (quest != null ? quest.id.ToString() : "?") + " arm canyon flood: " + result;
            if (ok)
            {
                Log.Message(line);
            }
            else
            {
                Log.Warning(line);
            }
            string outSignal = ok ? outSignalArmed : outSignalRefused;
            if (!outSignal.NullOrEmpty())
            {
                Find.SignalManager.SendSignal(new Signal(outSignal, signal.args));
            }
        }

        private string Arm()
        {
            if (mapParent == null || !mapParent.HasMap)
            {
                return "REFUSED: the quest's map parent has no map (" + (mapParent?.Label ?? "null") + ")";
            }
            RM_MapComponent_CanyonFlood flood = mapParent.Map.GetComponent<RM_MapComponent_CanyonFlood>();
            if (flood == null)
            {
                return "REFUSED: no canyon flood component on " + mapParent.Map;
            }
            return flood.ArmFlood(wallInTicks);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref outSignalArmed, "outSignalArmed");
            Scribe_Values.Look(ref outSignalRefused, "outSignalRefused");
            Scribe_References.Look(ref mapParent, "mapParent");
            Scribe_Values.Look(ref wallInTicks, "wallInTicks", 0);
            Scribe_Values.Look(ref fired, "fired", false);
        }
    }

    public class RM_QuestNode_ArmCanyonFlood : QuestNode
    {
        [NoTranslate] public SlateRef<string> inSignal;
        [NoTranslate] public SlateRef<string> outSignalArmed;
        [NoTranslate] public SlateRef<string> outSignalRefused;
        public SlateRef<MapParent> mapParent;
        public SlateRef<float> wallInHours;

        protected override bool TestRunInt(Slate slate)
        {
            return mapParent.GetValue(slate) != null;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            string inSig = inSignal.GetValue(slate);
            QuestGen.quest.AddPart(new RM_QuestPart_ArmCanyonFlood
            {
                inSignal = inSig.NullOrEmpty() ? slate.Get<string>("inSignal") : QuestGenUtility.HardcodedSignalWithQuestID(inSig),
                outSignalArmed = SignalTag(outSignalArmed.GetValue(slate)),
                outSignalRefused = SignalTag(outSignalRefused.GetValue(slate)),
                mapParent = mapParent.GetValue(slate),
                wallInTicks = RM_FloodKernel.HoursToTicks(wallInHours.GetValue(slate)),
            });
        }

        private static string SignalTag(string tag)
        {
            return tag.NullOrEmpty() ? null : QuestGenUtility.HardcodedSignalWithQuestID(tag);
        }
    }
}
