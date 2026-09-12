using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// MOD_OPTIONS_RETROFIT_1 — the named trigger case: "the Greentide standalone
	/// mod must let a player enable individual special contents (the Greatbole,
	/// sinking mud/churnmud, etc.) in OTHER biomes without inserting the whole
	/// biome." Greatbole does not exist yet (About.xml). Buried caches need no
	/// gate here — RM_MapComponent_MudSwallow already fires off the terrain
	/// extension alone, wherever RM_Churnmud exists. This component is what
	/// gets RM_Churnmud terrain itself onto a map whose biome is NOT Greentide.
	///
	/// Mirrors RM_Greentide_Biome.xml's own trick
	/// (&lt;mudTerrain&gt;RM_Churnmud&lt;/mudTerrain&gt;, see that file's comment):
	/// vanilla map generation already paints ordinary TerrainDefOf.Mud in every
	/// biome wherever ground is wet enough. Repainting that Mud to RM_Churnmud
	/// once, right after generation, reproduces the same hazard anywhere the
	/// player opts in via Mod Settings — no custom genstep, no engine patch.
	///
	/// WORLDGEN-AFFECTING, runs exactly once per map (tracked by `applied`,
	/// saved): a map generated before the setting was turned on is never
	/// retroactively touched, and a map generated after Greentide's own map
	/// (biome RM_Greentide) is skipped entirely — that hazard is already native
	/// there via <mudTerrain>.
	/// </summary>
	public class RM_MapComponent_CrossBiomeChurnmud : MapComponent
	{
		private bool applied;

		public RM_MapComponent_CrossBiomeChurnmud(Map map)
			: base(map)
		{
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref applied, "rmCrossBiomeChurnmudApplied", false);
		}

		public override void FinalizeInit()
		{
			base.FinalizeInit();
			if (applied)
			{
				return;
			}
			// Exactly once, regardless of outcome below — a settings flip after
			// this map already exists must never retroactively repaint it.
			applied = true;

			if (!RM_GreentideSettings.crossBiomeEnabled)
			{
				return;
			}
			BiomeDef biome = map.Biome;
			if (!RM_GreentideSettings.AppliesToBiome(biome))
			{
				return;
			}

			TerrainDef churnmud = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Churnmud");
			if (churnmud == null)
			{
				return; // silent-fail precedent (SlimeDefs, RM_DefOf callers) — never a hard error over a missing def
			}

			float coverage = Mathf.Clamp01(RM_GreentideSettings.crossBiomeCoverage);
			if (coverage <= 0f)
			{
				return;
			}

			int converted = 0;
			foreach (IntVec3 cell in map.AllCells)
			{
				if (map.terrainGrid.TerrainAt(cell) != TerrainDefOf.Mud)
				{
					continue;
				}
				if (coverage < 1f && Rand.Value > coverage)
				{
					continue;
				}
				map.terrainGrid.SetTerrain(cell, churnmud);
				converted++;
			}
			if (converted > 0)
			{
				Log.Message("[Greentide] cross-biome opt-in converted " + converted
					+ " Mud cell(s) to RM_Churnmud on a " + biome.defName
					+ " map (coverage " + coverage.ToString("0.00") + ").");
			}
		}
	}
}
