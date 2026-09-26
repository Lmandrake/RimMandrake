using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.Utinni.EggReckoning
{
	/// <summary>
	/// WEBWORK_EGG_RECKONING_QUEST_1, §3. Builds and adds RM_QuestPart_EggHatch,
	/// same SlateRef/HardcodedSignalWithQuestID shape as
	/// RM_QuestNode_EggPlantWatcher and Core's own QuestNode_Delay.
	/// </summary>
	public class RM_QuestNode_EggHatch : QuestNode
	{
		[NoTranslate]
		public SlateRef<MapParent> site;

		[NoTranslate]
		public SlateRef<string> inSignalEnable;

		[NoTranslate]
		public SlateRef<string> outSignalHatched;

		[NoTranslate]
		public SlateRef<string> outSignalFoundBeforeHatch;

		public SlateRef<float?> fixedBiologicalAgeYears;

		public SlateRef<float?> discoveryChancePerHour;

		public SlateRef<int?> nightStartHour;

		public SlateRef<int?> nightEndHour;

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

			RM_QuestPart_EggHatch part = new RM_QuestPart_EggHatch
			{
				site = siteValue,
				outSignalHatched = QuestGenUtility.HardcodedSignalWithQuestID(outSignalHatched.GetValue(slate)),
				outSignalFoundBeforeHatch = QuestGenUtility.HardcodedSignalWithQuestID(outSignalFoundBeforeHatch.GetValue(slate)),
				inSignalEnable = QuestGenUtility.HardcodedSignalWithQuestID(inSignalEnable.GetValue(slate)) ?? slate.Get<string>("inSignal")
			};

			float? age = fixedBiologicalAgeYears.GetValue(slate);
			if (age.HasValue)
			{
				part.fixedBiologicalAgeYears = age.Value;
			}
			float? chance = discoveryChancePerHour.GetValue(slate);
			if (chance.HasValue)
			{
				part.discoveryChancePerHour = chance.Value;
			}
			int? startHour = nightStartHour.GetValue(slate);
			if (startHour.HasValue)
			{
				part.nightStartHour = startHour.Value;
			}
			int? endHour = nightEndHour.GetValue(slate);
			if (endHour.HasValue)
			{
				part.nightEndHour = endHour.Value;
			}

			QuestGen.quest.AddPart(part);
		}
	}
}
