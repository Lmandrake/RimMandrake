using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Sounds;

public class QuestPart_ForcedMusic : QuestPart
{
	public string inSignalEnable;

	public string inSignalDisable;

	public List<SongDef> possibleSongs;

	public int priority;

	public override void Notify_QuestSignalReceived(Signal signal)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		((QuestPart)this).Notify_QuestSignalReceived(signal);
		if (signal.tag == inSignalEnable)
		{
			foreach (SongDef possibleSong in possibleSongs)
			{
				ForcedMusicManager.ForceSong(possibleSong, priority);
			}
		}
		if (!(signal.tag == inSignalDisable))
		{
			return;
		}
		foreach (SongDef possibleSong2 in possibleSongs)
		{
			ForcedMusicManager.EndSong(possibleSong2);
		}
	}

	public override void Cleanup()
	{
		((QuestPart)this).Cleanup();
		foreach (SongDef possibleSong in possibleSongs)
		{
			ForcedMusicManager.EndSong(possibleSong);
		}
	}

	public override void ExposeData()
	{
		((QuestPart)this).ExposeData();
		Scribe_Values.Look<string>(ref inSignalEnable, "inSignalEnable", (string)null, false);
		Scribe_Values.Look<string>(ref inSignalDisable, "inSignalDisable", (string)null, false);
		Scribe_Values.Look<int>(ref priority, "priority", 0, false);
		Scribe_Collections.Look<SongDef>(ref possibleSongs, "possibleSongs", (LookMode)4, Array.Empty<object>());
	}
}
