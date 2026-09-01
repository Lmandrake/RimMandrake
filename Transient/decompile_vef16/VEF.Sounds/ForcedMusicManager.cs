using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using LudeonTK;
using RimWorld;
using Verse;

namespace VEF.Sounds;

public class ForcedMusicManager : GameComponent
{
	public class ForcedSongsBox : IExposable
	{
		public HashSet<SongDef> forcedSongs;

		public ForcedSongsBox()
		{
		}

		public ForcedSongsBox(HashSet<SongDef> forcedSongs)
		{
			this.forcedSongs = forcedSongs;
		}

		public void ExposeData()
		{
			Scribe_Collections.Look<SongDef>(ref forcedSongs, "forcedSongs", (LookMode)4);
		}

		public void Deconstruct(out HashSet<SongDef> item, out int length)
		{
			item = forcedSongs;
			length = forcedSongs.Count;
		}
	}

	private static readonly FieldRef<MusicManagerPlay, SongDef> currentSong = AccessTools.FieldRefAccess<MusicManagerPlay, SongDef>("currentSong");

	private static readonly FieldRef<MusicManagerPlay, bool> songWasForced = AccessTools.FieldRefAccess<MusicManagerPlay, bool>("songWasForced");

	private static bool patchesApplied;

	private int currentPriority = -1;

	private HashSet<SongDef> forcedSongs = new HashSet<SongDef>();

	private Dictionary<int, ForcedSongsBox> prioritySongs = new Dictionary<int, ForcedSongsBox>();

	public static ForcedMusicManager Instance;

	public int Priority => currentPriority;

	public IEnumerable<SongDef> Songs => forcedSongs;

	public IReadOnlyDictionary<int, ForcedSongsBox> AllSongs => prioritySongs;

	public ForcedMusicManager(Game game)
	{
		Instance = this;
	}

	public static void ApplyPatches()
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Expected O, but got Unknown
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Expected O, but got Unknown
		if (!patchesApplied)
		{
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(MusicManagerPlay), "ChooseNextSong", (Type[])null, (Type[])null), new HarmonyMethod(typeof(ForcedMusicManager), "ChooseNextSong_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.PropertyGetter(typeof(MusicManagerPlay), "DangerMusicMode"), new HarmonyMethod(typeof(ForcedMusicManager), "DangerMusicMode_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
			patchesApplied = true;
		}
	}

	public static void ForceSong(SongDef def, int priority)
	{
		ForcedSongsBox value;
		if (Instance.forcedSongs.Count == 0)
		{
			ForceStopMusic();
			Instance.forcedSongs.Add(def);
			Instance.currentPriority = priority;
		}
		else if (priority == Instance.currentPriority)
		{
			Instance.forcedSongs.Add(def);
		}
		else if (priority > Instance.currentPriority)
		{
			ForceStopMusic();
			Instance.prioritySongs.Add(Instance.currentPriority, new ForcedSongsBox(Instance.forcedSongs));
			Instance.forcedSongs = new HashSet<SongDef> { def };
			Instance.currentPriority = priority;
		}
		else if (Instance.prioritySongs.TryGetValue(priority, out value))
		{
			value.forcedSongs.Add(def);
			Instance.prioritySongs[priority] = value;
		}
		else
		{
			Instance.prioritySongs.Add(priority, new ForcedSongsBox(new HashSet<SongDef> { def }));
		}
	}

	public static void EndSong(SongDef def)
	{
		int num = default(int);
		ForcedSongsBox forcedSongsBox = default(ForcedSongsBox);
		if (Instance.forcedSongs.Remove(def))
		{
			if (currentSong.Invoke(Find.MusicManagerPlay) == def)
			{
				ForceStopMusic();
			}
			if (Instance.forcedSongs.Count == 0)
			{
				if (Instance.prioritySongs.Any())
				{
					GenCollection.Deconstruct<int, ForcedSongsBox>(GenCollection.MaxBy<KeyValuePair<int, ForcedSongsBox>, int>((IEnumerable<KeyValuePair<int, ForcedSongsBox>>)Instance.prioritySongs, (Func<KeyValuePair<int, ForcedSongsBox>, int>)((KeyValuePair<int, ForcedSongsBox> kv) => kv.Key)), ref num, ref forcedSongsBox);
					int key = num;
					ForcedSongsBox forcedSongsBox2 = forcedSongsBox;
					Instance.currentPriority = key;
					Instance.forcedSongs = forcedSongsBox2.forcedSongs;
					Instance.prioritySongs.Remove(key);
				}
				else
				{
					Instance.currentPriority = -1;
				}
			}
		}
		foreach (KeyValuePair<int, ForcedSongsBox> prioritySong in Instance.prioritySongs)
		{
			GenCollection.Deconstruct<int, ForcedSongsBox>(prioritySong, ref num, ref forcedSongsBox);
			forcedSongsBox.Deconstruct(out var item, out var _);
			item.Remove(def);
		}
		GenCollection.RemoveAll<int, ForcedSongsBox>(Instance.prioritySongs, (Predicate<KeyValuePair<int, ForcedSongsBox>>)((KeyValuePair<int, ForcedSongsBox> kv) => kv.Value.forcedSongs.Count == 0));
	}

	private static void ForceStopMusic()
	{
		songWasForced.Invoke(Find.MusicManagerPlay) = false;
		Find.MusicManagerPlay.ForceFadeoutAndSilenceFor(1f, 1f, false);
	}

	public static bool ChooseNextSong_Prefix(ref SongDef __result, MusicManagerPlay __instance)
	{
		SongDef val = default(SongDef);
		if (GenCollection.TryRandomElement<SongDef>(Instance.forcedSongs, ref val))
		{
			__result = val;
			songWasForced.Invoke(__instance) = true;
			return false;
		}
		return true;
	}

	public static bool DangerMusicMode_Prefix(ref bool __result)
	{
		if (Instance.forcedSongs.Count > 0)
		{
			__result = true;
			return false;
		}
		return true;
	}

	public override void ExposeData()
	{
		Scribe_Values.Look<int>(ref currentPriority, "currentPriority", 0, false);
		Scribe_Collections.Look<SongDef>(ref forcedSongs, "forcedSongs", (LookMode)4);
		Scribe_Collections.Look<int, ForcedSongsBox>(ref prioritySongs, "prioritySongs", (LookMode)1, (LookMode)2);
	}

	[DebugAction("Music", "End forced music", false, false, false, false, false, 0, false)]
	public static void StopAll()
	{
		Instance.currentPriority = -1;
		Instance.forcedSongs.Clear();
		Instance.prioritySongs.Clear();
		ForceStopMusic();
	}
}
