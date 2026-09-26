using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LanternDeeps
{
	// LANTERN_DEEPS_INJECTION_1: RM_LanternDeepEmergence scatters only onto
	// qualifying host biomes. GenStepDef has no biome field and vanilla ships no
	// ScattererValidator_Biome (confirmed absent), so the filter lives here,
	// mirroring how Biomes! Caverns' own BMT_CrystalsGenerator self-gates.
	// DEEP_ENTRANCE_BIOMES_SETTING_1: the qualifying set is
	// LanternDeepsSettings.entranceBiomes (Mod Settings, any biome selectable);
	// its default is the three biomes the design doc rules ≤ -40°C
	// (the_lantern_deeps.md "Injection rule"). Order matters and is relied on by
	// validation.py: the toggle is checked FIRST, then the biome, then the roll.
	//
	// chancePerMap is a tuning knob, not a ruling: the design doc says a Deep
	// mouth exists somewhere on the qualifying biomes, not how densely. 0.08
	// (8% of qualifying maps) is FOUNDRY's placeholder pick pending the owner's
	// actual density call at the assignment sitting.
	public class GenStep_ScatterCavePortal : GenStep_ScatterGroup
	{
		public float chancePerMap = 0.08f;

		public override void Generate(Map map, GenStepParams parms)
		{
			if (!LanternDeepsSettings.lanternDeepsEnabled)
			{
				return;
			}
			if (!LanternDeepsSettings.emergenceEnabled)
			{
				return;
			}
			if (!LanternDeepsSettings.IsEntranceBiome(map.Biome))
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
