using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PropaneLakeMechanics
{
	public class PropaneLakeMechanicsMod : Mod
	{
		public static PropaneLakeMechanicsSettings Settings;

		public PropaneLakeMechanicsMod(ModContentPack content) : base(content)
		{
			Settings = GetSettings<PropaneLakeMechanicsSettings>();
			new Harmony("mandrake.rut.propanelakemechanics").PatchAll();
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			Settings.DoSettingsWindowContents(inRect);
		}

		public override string SettingsCategory()
		{
			return "RimMandrake: Utinni — Propane Lake Mechanics";
		}
	}
}
