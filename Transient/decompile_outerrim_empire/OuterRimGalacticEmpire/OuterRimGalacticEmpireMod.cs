using System;
using System.IO;
using System.Reflection;
using HarmonyLib;
using TabulaRasa;
using UnityEngine;
using Verse;

namespace OuterRimGalacticEmpire;

public class OuterRimGalacticEmpireMod : Mod
{
	public static OuterRimGalacticEmpireMod mod;

	public static OuterRimGalacticEmpireSettings settings;

	public Vector2 optionsScrollPosition;

	public float optionsViewRectHeight;

	internal static string VersionDir => Path.Combine(((Mod)mod).Content.ModMetaData.RootDir.FullName, "Version.txt");

	public static string CurrentVersion { get; private set; }

	public OuterRimGalacticEmpireMod(ModContentPack content)
		: base(content)
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		mod = this;
		settings = ((Mod)this).GetSettings<OuterRimGalacticEmpireSettings>();
		Version version = Assembly.GetExecutingAssembly().GetName().Version;
		CurrentVersion = $"{version.Major}.{version.Minor}.{version.Build}";
		Log.Message(ColoredText.Colorize(":: Outer Rim - Galactic Empire :: ", Color.cyan) + CurrentVersion + " ::");
		if (Prefs.DevMode)
		{
			File.WriteAllText(VersionDir, CurrentVersion);
		}
		new Harmony("Neronix17.OuterRim.GalacticEmpire").PatchAll(Assembly.GetExecutingAssembly());
	}

	public void DoOptionsCategoryContents(Listing_Standard listing)
	{
		((Listing)listing).GapLine(12f);
		SettingsUtil.Note(listing, "Galactic Empire", (GameFont)2);
		((Listing)listing).GapLine(12f);
		if (ModLister.GetActiveModWithIdentifier("Neronix17.OuterRim.GalacticDiversity", false) != null)
		{
			listing.CheckboxLabeled("Enable Wookiee Slaves", ref settings.enableWookieeSlaves, "If enabled, Imperial settlements will typically include a handful of Wookiee slaves, and rare Imperial raids of Wookiee slaves equipped with shoddy ill fitting equipment will show up.", 0f, 1f);
			((Listing)listing).GapLine(12f);
		}
	}
}
