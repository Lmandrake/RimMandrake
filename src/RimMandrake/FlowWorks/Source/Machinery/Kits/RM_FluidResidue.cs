using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery.Kits
{
	/// <summary>
	/// What a liquid leaves behind when its flood drains (SUMP_TAR_NASTINESS_1: "the tar gets on everything").
	/// Put on a FluidDef (Patches/Kits/RM_TarResidue.xml puts it on RM_Fluid_Tar). When a cell carrying one of
	/// that fluid's fill terrains loses it for good, the cell keeps <see cref="filth"/> with
	/// <see cref="chancePerCell"/>. A fill level changing (half → trace) is not a drain: the cell is re-checked
	/// on the next rare tick and only stains if the fluid is really gone.
	/// Mod Setting: RM_KitSettings.fluidResidueEnabled. chancePerCell PROVISIONAL.
	/// </summary>
	public class RM_FluidResidueExtension : DefModExtension
	{
		public ThingDef filth;
		public float chancePerCell = 0.35f;
		public int filthCount = 1;

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string e in base.ConfigErrors())
			{
				yield return e;
			}
			if (filth == null || filth.filth == null)
			{
				yield return "RM_FluidResidueExtension needs a filth ThingDef (one with <filth> properties).";
			}
		}
	}

	public static class RM_FluidResidue
	{
		private static Dictionary<TerrainDef, FluidDef> fillOwner;

		/// <summary>The residue-leaving fluid whose fill <paramref name="t"/> is, or null.</summary>
		public static FluidDef ResidueFluidOf(TerrainDef t)
		{
			if (t == null)
			{
				return null;
			}
			if (fillOwner == null)
			{
				fillOwner = new Dictionary<TerrainDef, FluidDef>();
				foreach (FluidDef f in DefDatabase<FluidDef>.AllDefsListForReading)
				{
					if (f.GetModExtension<RM_FluidResidueExtension>() == null)
					{
						continue;
					}
					foreach (TerrainDef fill in new[] { f.floodTerrain, f.fillTerrainHalf, f.fillTerrainBrim, f.fillTerrainSuperdeep })
					{
						if (fill != null && !fillOwner.ContainsKey(fill))
						{
							fillOwner[fill] = f;
						}
					}
				}
			}
			return fillOwner.TryGetValue(t, out FluidDef owner) ? owner : null;
		}
	}

	[HarmonyPatch(typeof(TerrainGrid), nameof(TerrainGrid.RemoveTempTerrain))]
	[RimMandrake.Shared.PatchFeature("Drained liquid leaves residue", typeof(RimMandrake.FlowWorks.Machinery.Kits.RM_KitSettings), "fluidResidueEnabled")]
	public static class RM_Patch_FluidResidueOnDrain
	{
		private static readonly AccessTools.FieldRef<TerrainGrid, Map> MapOf = AccessTools.FieldRefAccess<TerrainGrid, Map>("map");

		public static void Prefix(TerrainGrid __instance, IntVec3 c, out FluidDef __state)
		{
			__state = null;
			if (!RM_KitSettings.fluidResidueEnabled)
			{
				return;
			}
			__state = RM_FluidResidue.ResidueFluidOf(__instance.TempTerrainAt(c));
		}

		public static void Postfix(TerrainGrid __instance, IntVec3 c, FluidDef __state)
		{
			if (__state == null)
			{
				return;
			}
			MapOf(__instance)?.GetComponent<RM_MapComponent_FluidResidue>()?.Pending(c, __state);
		}
	}

	public class RM_MapComponent_FluidResidue : MapComponent
	{
		private readonly List<IntVec3> cells = new List<IntVec3>();
		private readonly List<FluidDef> fluids = new List<FluidDef>();

		/// <summary>Report token: cells stained by a drained flood.</summary>
		public int statResidueCells;

		public RM_MapComponent_FluidResidue(Map map) : base(map)
		{
		}

		public void Pending(IntVec3 c, FluidDef fluid)
		{
			cells.Add(c);
			fluids.Add(fluid);
		}

		public override void MapComponentTick()
		{
			if (cells.Count == 0 || Find.TickManager.TicksGame % 250 != 0)
			{
				return;
			}
			for (int i = 0; i < cells.Count; i++)
			{
				IntVec3 c = cells[i];
				FluidDef f = fluids[i];
				if (!c.InBounds(map) || RM_FluidResidue.ResidueFluidOf(map.terrainGrid.TempTerrainAt(c)) == f)
				{
					continue;  // refilled or only changed level: not a drain
				}
				RM_FluidResidueExtension ext = f.GetModExtension<RM_FluidResidueExtension>();
				if (ext?.filth != null && RM_KitMath.LeavesResidue(ext.chancePerCell, Rand.Value)
					&& FilthMaker.TryMakeFilth(c, map, ext.filth, ext.filthCount))
				{
					statResidueCells++;
				}
			}
			cells.Clear();
			fluids.Clear();
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref statResidueCells, "RM_residueCells", 0);
		}
	}
}
