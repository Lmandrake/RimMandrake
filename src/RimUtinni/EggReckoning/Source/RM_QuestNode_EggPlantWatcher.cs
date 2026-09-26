using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.EggReckoning
{
	/// <summary>
	/// WEBWORK_EGG_RECKONING_QUEST_1, §2b. Builds and adds
	/// RM_QuestPart_EggPlantWatcher, following the exact same
	/// SlateRef-in/QuestGenUtility.HardcodedSignalWithQuestID/AddPart shape
	/// Core's own QuestNode_Delay uses (Source/RimWorld/QuestGen/
	/// QuestNode_Delay.cs, read in full this session) so the emitted signal
	/// names are namespaced per-quest the same way every other custom or stock
	/// signal in this def is.
	/// </summary>
	public class RM_QuestNode_EggPlantWatcher : QuestNode
	{
		[NoTranslate]
		public SlateRef<MapParent> site;

		[NoTranslate]
		public SlateRef<string> inSignalEnable;

		[NoTranslate]
		public SlateRef<string> outSignalPlanted;

		[NoTranslate]
		public SlateRef<string> outSignalDiscovered;

		protected override bool TestRunInt(Slate slate)
		{
			return true;
		}

		protected override void RunInt()
		{
			Slate slate = QuestGen.slate;
			MapParent siteValue = site.GetValue(slate);
			if (siteValue == null)
			{
				return;
			}

			RM_QuestPart_EggPlantWatcher part = new RM_QuestPart_EggPlantWatcher
			{
				site = siteValue,
				outSignalPlanted = QuestGenUtility.HardcodedSignalWithQuestID(outSignalPlanted.GetValue(slate)),
				outSignalDiscovered = QuestGenUtility.HardcodedSignalWithQuestID(outSignalDiscovered.GetValue(slate)),
				inSignalEnable = QuestGenUtility.HardcodedSignalWithQuestID(inSignalEnable.GetValue(slate)) ?? slate.Get<string>("inSignal")
			};
			QuestGen.quest.AddPart(part);
		}
	}
}
