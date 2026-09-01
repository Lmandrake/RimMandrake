using System.Collections.Generic;
using System.IO;
using Verse;

namespace FactionLoadout.Util;

[HotSwappable]
public static class IO
{
	public static string SaveDataPath => Path.Combine(GenFilePaths.ConfigFolderPath, "TotalControlData");

	public static bool DeleteFile(string filePath)
	{
		if (File.Exists(filePath))
		{
			File.Delete(filePath);
			return true;
		}
		return false;
	}

	public static void SaveToFile(IExposable item, string filePath)
	{
		FileInfo fileInfo = new FileInfo(filePath);
		if (!fileInfo.Directory.Exists)
		{
			fileInfo.Directory.Create();
		}
		Scribe.saver.InitSaving(filePath, "FactionEditData");
		item.ExposeData();
		Scribe.saver.FinalizeSaving();
	}

	public static void LoadFromFile(IExposable item, string filePath)
	{
		Scribe.loader.InitLoading(filePath);
		Scribe.loader.EnterNode("FactionEditData");
		item.ExposeData();
		Scribe.loader.FinalizeLoading();
	}

	public static IEnumerable<FileInfo> ListXmlFiles(string directory)
	{
		DirectoryInfo directoryInfo = new DirectoryInfo(directory);
		if (!directoryInfo.Exists)
		{
			yield break;
		}
		foreach (FileInfo item in directoryInfo.EnumerateFiles("*.xml", SearchOption.TopDirectoryOnly))
		{
			yield return item;
		}
	}
}
