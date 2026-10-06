using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Machinery.Kits
{
	/// <summary>
	/// Hot releases (FORGE_CYCLE_MECHANICS_1 phase 3: "torrential boiling rain + FLOODING"). A kit releases a
	/// FlowWorks flood HOT: for <c>coolHours</c> after the release, a pawn standing in that fluid's fill within
	/// the release's reach is scalded (vanilla Burn, falling with the heat left), and the water steams — the
	/// readable sign. After it cools it is ordinary water and drains as any flood does. Generic: any kit, any
	/// fluid (a boiling spring, a geyser overflow, a scald-sea surge).
	/// Kit call: <see cref="Release"/> (spawns the flood too) or <see cref="MarkHot"/> (for a flood the kit
	/// already spawned). Mod Settings: RM_KitSettings.hotLiquidEnabled, hotLiquidBurnMultiplier.
	/// Numbers PROVISIONAL: 6 h to cool, 3 Burn per 250-tick check at full heat, nothing below quarter heat.
	/// </summary>
	public static class RM_HotLiquid
	{
		public const float DefaultCoolHours = 6f;
		public const float DefaultScald = 3f;

		/// <summary>Spawns a flood of <paramref name="fluid"/> worth <paramref name="tiles"/> cells at
		/// <paramref name="at"/> and marks it hot. Returns the flood, or null when it could not spawn.</summary>
		public static Flood_FlowWorks Release(Map map, IntVec3 at, FluidDef fluid, int tiles,
			float coolHours = DefaultCoolHours, float scald = DefaultScald)
		{
			ThingDef floodDef = RimMandrakeFlowWorks_DefOf.RM_FluidCanalFlood;
			if (map == null || fluid == null || floodDef == null || !at.InBounds(map) || tiles < 1)
			{
				return null;
			}
			Flood_FlowWorks flood = (Flood_FlowWorks)ThingMaker.MakeThing(floodDef);
			flood.Configure(fluid, tiles * Mathf.Max(0.0001f, fluid.volumePerTile));
			GenSpawn.Spawn(flood, at, map);
			MarkHot(map, at, fluid, tiles, coolHours, scald);
			return flood;
		}

		/// <summary>Marks the fill of <paramref name="fluid"/> around <paramref name="at"/> hot for
		/// <paramref name="coolHours"/>. Reach is the radius a <paramref name="tiles"/>-cell spread fills, plus slack.</summary>
		public static void MarkHot(Map map, IntVec3 at, FluidDef fluid, int tiles,
			float coolHours = DefaultCoolHours, float scald = DefaultScald)
		{
			if (map == null || fluid == null)
			{
				return;
			}
			float reach = Mathf.Min(GenRadial.MaxRadialPatternRadius - 1f, Mathf.Sqrt(Mathf.Max(1, tiles) / Mathf.PI) * 1.6f + 3f);
			map.GetComponent<RM_MapComponent_HotLiquid>()?.Add(at, fluid, reach,
				Mathf.RoundToInt(coolHours * GenDate.TicksPerHour), scald);
		}

		public static bool IsFillOf(TerrainDef t, FluidDef fluid)
		{
			return t != null && fluid != null && (t == fluid.floodTerrain || t == fluid.fillTerrainHalf
				|| t == fluid.fillTerrainBrim || t == fluid.fillTerrainSuperdeep);
		}
	}

	public class RM_HotPatch : IExposable
	{
		public IntVec3 center;
		public FluidDef fluid;
		public float reach;
		public int startTick;
		public int coolTicks;
		public float scald;

		public void ExposeData()
		{
			Scribe_Values.Look(ref center, "center");
			Scribe_Defs.Look(ref fluid, "fluid");
			Scribe_Values.Look(ref reach, "reach");
			Scribe_Values.Look(ref startTick, "startTick");
			Scribe_Values.Look(ref coolTicks, "coolTicks");
			Scribe_Values.Look(ref scald, "scald");
		}
	}

	public class RM_MapComponent_HotLiquid : MapComponent
	{
		private const int CheckInterval = 250;
		private List<RM_HotPatch> patches = new List<RM_HotPatch>();

		/// <summary>Report tokens for the live northstar read: scald hits dealt, steam puffs thrown.</summary>
		public int statScaldHits;
		public int statSteamPuffs;

		public int ActivePatches => patches.Count;

		public RM_MapComponent_HotLiquid(Map map) : base(map)
		{
		}

		public void Add(IntVec3 at, FluidDef fluid, float reach, int coolTicks, float scald)
		{
			patches.Add(new RM_HotPatch
			{
				center = at, fluid = fluid, reach = reach, startTick = Find.TickManager.TicksGame,
				coolTicks = coolTicks, scald = scald
			});
		}

		public override void MapComponentTick()
		{
			if (patches.Count == 0 || Find.TickManager.TicksGame % CheckInterval != 0)
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			for (int i = patches.Count - 1; i >= 0; i--)
			{
				RM_HotPatch p = patches[i];
				float heat = RM_KitMath.HeatFraction(now - p.startTick, p.coolTicks);
				if (heat <= 0f || p.fluid == null)
				{
					patches.RemoveAt(i);
					continue;
				}
				if (!RM_KitSettings.hotLiquidEnabled)
				{
					continue;
				}
				Steam(p, heat);
				int dmg = RM_KitMath.ScaldDamage(p.scald, heat, RM_KitSettings.hotLiquidBurnMultiplier);
				if (dmg <= 0)
				{
					continue;
				}
				IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
				for (int k = pawns.Count - 1; k >= 0; k--)
				{
					Pawn pawn = pawns[k];
					if (pawn.Dead || pawn.Flying || !pawn.Position.InHorDistOf(p.center, p.reach)
						|| !RM_HotLiquid.IsFillOf(map.terrainGrid.TempTerrainAt(pawn.Position), p.fluid))
					{
						continue;
					}
					pawn.TakeDamage(new DamageInfo(DamageDefOf.Burn, dmg));
					statScaldHits++;
				}
			}
		}

		private void Steam(RM_HotPatch p, float heat)
		{
			int puffs = Mathf.CeilToInt(3f * heat);
			for (int n = 0; n < puffs; n++)
			{
				IntVec3 c = p.center + GenRadial.RadialPattern[Rand.Range(0, GenRadial.NumCellsInRadius(p.reach))];
				if (c.InBounds(map) && RM_HotLiquid.IsFillOf(map.terrainGrid.TempTerrainAt(c), p.fluid))
				{
					FleckMaker.ThrowAirPuffUp(c.ToVector3Shifted(), map);
					statSteamPuffs++;
				}
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref patches, "RM_hotPatches", LookMode.Deep);
			Scribe_Values.Look(ref statScaldHits, "RM_hotScaldHits", 0);
			Scribe_Values.Look(ref statSteamPuffs, "RM_hotSteamPuffs", 0);
			if (patches == null)
			{
				patches = new List<RM_HotPatch>();
			}
		}
	}
}
