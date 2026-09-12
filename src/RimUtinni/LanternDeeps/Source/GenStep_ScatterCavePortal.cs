using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
	// LANTERN_DEEPS_INJECTION_1: RUT_LanternDeepEmergence must scatter only onto
	// the three host biomes the design doc rules ≤ -40°C (the_lantern_deeps.md
	// "Injection rule"). GenStepDef has no biome field and vanilla ships no
	// ScattererValidator_Biome (confirmed absent), so the filter lives here,
	// mirroring how Biomes! Caverns' own BMT_CrystalsGenerator self-gates.
	//
	// chancePerMap is a tuning knob, not a ruling: the design doc says a Deep
	// mouth exists somewhere on the qualifying biomes, not how densely. 0.08
	// (8% of qualifying maps) is FOUNDRY's placeholder pick pending the owner's
	// actual density call at the assignment sitting.
	public class GenStep_ScatterCavePortal : GenStep_ScatterGroup
	{
		private static readonly HashSet<string> AllowedBiomeDefNames = new HashSet<string>
		{
			"BiomeGRimond",
			"RUT_NightsideIce",
			"RUT_PropaneLake",
		};

		public float chancePerMap = 0.08f;

		public override void Generate(Map map, GenStepParams parms)
		{
			if (!LanternDeepsSettings.emergenceEnabled)
			{
				return;
			}
			if (map.Biome == null || !AllowedBiomeDefNames.Contains(map.Biome.defName))
			{
				return;
			}
			if (!Rand.Chance(Mathf.Clamp01(chancePerMap * LanternDeepsSettings.emergenceChanceMultiplier)))
			{
				return;
			}
			base.Generate(map, parms);
		}
	}
}
