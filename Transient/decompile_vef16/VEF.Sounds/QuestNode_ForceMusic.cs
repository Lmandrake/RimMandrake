using System.Collections.Generic;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace VEF.Sounds;

public class QuestNode_ForceMusic : QuestNode
{
	public SlateRef<string> inSignalEnable;

	public SlateRef<string> inSignalDisable;

	public SlateRef<List<SongDef>> possibleSongs;

	public SlateRef<int> priority;

	public QuestNode_ForceMusic()
	{
		ForcedMusicManager.ApplyPatches();
	}

	protected override void RunInt()
	{
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		Slate slate = QuestGen.slate;
		QuestGen.quest.AddPart((QuestPart)(object)new QuestPart_ForcedMusic
		{
			inSignalEnable = (QuestGenUtility.HardcodedSignalWithQuestID(inSignalEnable.GetValue(slate)) ?? slate.Get<string>("inSignal", (string)null, false)),
			inSignalDisable = QuestGenUtility.HardcodedSignalWithQuestID(inSignalDisable.GetValue(slate)),
			possibleSongs = possibleSongs.GetValue(slate),
			priority = priority.GetValue(slate),
			signalListenMode = (SignalListenMode)4
		});
	}

	protected override bool TestRunInt(Slate slate)
	{
		return true;
	}
}
