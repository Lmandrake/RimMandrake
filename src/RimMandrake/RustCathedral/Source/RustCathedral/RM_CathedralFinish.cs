using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.RustCathedral
{
	// RUSTCATHEDRAL_BASE_FINISH_BUILD_1 parts 3 and 5 -- the living coolant eel's placement and wander, and the
	// cooked strays. Both GenSteps self-gate to RM_RustCathedral (the wall GenSteps' gate) and are added to
	// MapCommonBase by Patches/RM_CathedralFinish_MapGenPatch.xml, so they no-op on every other biome.

	/// <summary>Places living coolant eels on standable water cells at map generation. The eel is NOT in the
	/// biome's wildAnimals: the vanilla spawner places an animal on any walkable cell that reaches the map edge,
	/// which for a water-locked animal means dry plate it can never leave (RM_CompWaterLocked would pin it there).</summary>
	public class RM_GenStep_CoolantEels : GenStep
	{
		public const string CathedralBiomeDefName = "RM_RustCathedral";

		public PawnKindDef pawnKind;

		public override int SeedPart => 1784450317;

		public static bool IsEelCell(IntVec3 c, Map map)
		{
			if (!c.InBounds(map) || !c.Standable(map))
			{
				return false;
			}
			TerrainDef t = c.GetTerrain(map);
			return t != null && t.IsWater;
		}

		public override void Generate(Map map, GenStepParams parms)
		{
			if (!RM_RustCathedralSettings.coolantEelsEnabled || RM_RustCathedralSettings.coolantEelCount <= 0)
			{
				return;
			}
			if (map.Biome == null || map.Biome.defName != CathedralBiomeDefName || pawnKind == null)
			{
				return;
			}
			List<IntVec3> water = new List<IntVec3>();
			foreach (IntVec3 c in map.AllCells)
			{
				if (IsEelCell(c, map))
				{
					water.Add(c);
				}
			}
			if (water.Count == 0)
			{
				return; // a dry map: the eels live in the canals, so there are none
			}
			int n = Mathf.Min(RM_RustCathedralSettings.coolantEelCount, water.Count);
			for (int i = 0; i < n; i++)
			{
				IntVec3 cell = water.RandomElement();
				Pawn eel = PawnGenerator.GeneratePawn(pawnKind, null);
				GenSpawn.Spawn(eel, cell, map, WipeMode.Vanish);
			}
		}
	}

	/// <summary>Wanders only to water cells (vanilla JobGiver_Wander's own per-instance destination hook). The
	/// eel circles: the root is where it is now.</summary>
	public class RM_JobGiver_WaterWander : JobGiver_Wander
	{
		public RM_JobGiver_WaterWander()
		{
			wanderRadius = 7f;
			ticksBetweenWandersRange = new IntRange(60, 240);
			wanderDestValidator = (pawn, cell, root) => RM_GenStep_CoolantEels.IsEelCell(cell, pawn.Map);
		}

		protected override IntVec3 GetWanderRoot(Pawn pawn)
		{
			return pawn.Position;
		}
	}

	/// <summary>Scatters a handful of desiccated animal corpses near the map edges at generation. Kinds come from
	/// the neighbouring biomes' rosters (ordinary animals only, never humanlike, never mechanoid); each dies with
	/// scaria in its hediff set. Never a live spawn (sheet ban 7).</summary>
	public class RM_GenStep_CathedralStrays : GenStep
	{
		public const string CathedralBiomeDefName = "RM_RustCathedral";

		public List<string> sourceBiomes = new List<string>();

		public List<PawnKindDef> fallbackKinds = new List<PawnKindDef>();

		public int edgeBand = 8;

		public override int SeedPart => 902277361;

		public static bool IsStrayKind(PawnKindDef k)
		{
			return k?.race?.race != null && k.RaceProps.Animal && !k.RaceProps.Humanlike && !k.RaceProps.IsMechanoid
				&& !k.RaceProps.Dryad && k.race.race.corpseDef != null;
		}

		public List<PawnKindDef> Kinds()
		{
			List<PawnKindDef> kinds = new List<PawnKindDef>();
			for (int i = 0; i < sourceBiomes.Count; i++)
			{
				BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail(sourceBiomes[i]);
				if (b == null)
				{
					continue;
				}
				foreach (PawnKindDef k in b.AllWildAnimals)
				{
					if (IsStrayKind(k) && !kinds.Contains(k))
					{
						kinds.Add(k);
					}
				}
			}
			if (kinds.Count == 0)
			{
				for (int i = 0; i < fallbackKinds.Count; i++)
				{
					if (IsStrayKind(fallbackKinds[i]))
					{
						kinds.Add(fallbackKinds[i]);
					}
				}
			}
			return kinds;
		}

		public static bool InEdgeBand(IntVec3 c, Map map, int band)
		{
			return c.x < band || c.z < band || c.x >= map.Size.x - band || c.z >= map.Size.z - band;
		}

		public override void Generate(Map map, GenStepParams parms)
		{
			if (!RM_RustCathedralSettings.straysEnabled || RM_RustCathedralSettings.strayCount <= 0)
			{
				return;
			}
			if (map.Biome == null || map.Biome.defName != CathedralBiomeDefName)
			{
				return;
			}
			List<PawnKindDef> kinds = Kinds();
			if (kinds.Count == 0)
			{
				return;
			}
			HediffDef scaria = DefDatabase<HediffDef>.GetNamedSilentFail("Scaria");
			for (int i = 0; i < RM_RustCathedralSettings.strayCount; i++)
			{
				if (!CellFinder.TryFindRandomCellNear(map.Center, map, Mathf.Max(map.Size.x, map.Size.z),
						c => InEdgeBand(c, map, edgeBand) && c.Standable(map) && !c.GetTerrain(map).IsWater, out IntVec3 cell))
				{
					continue;
				}
				Pawn p = PawnGenerator.GeneratePawn(kinds.RandomElement(), null);
				if (scaria != null)
				{
					p.health.AddHediff(scaria);
				}
				if (!p.Dead)
				{
					p.Kill(null);
				}
				Corpse corpse = p.Corpse;
				if (corpse == null)
				{
					continue;
				}
				corpse.GetComp<CompRottable>()?.RotImmediately(RotStage.Dessicated);
				GenSpawn.Spawn(corpse, cell, map, WipeMode.Vanish);
			}
		}
	}
}
