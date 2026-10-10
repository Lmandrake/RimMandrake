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
			RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rut.propanelakemechanics"), typeof(PropaneLakeMechanicsMod).Assembly, "RimMandrake.Utinni.PropaneLakeMechanics");
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			Settings.DoWindowContents(inRect);
		}

		public override string SettingsCategory()
		{
			return "RimMandrake: Utinni — Propane Lake Mechanics";
		}
	}
}
