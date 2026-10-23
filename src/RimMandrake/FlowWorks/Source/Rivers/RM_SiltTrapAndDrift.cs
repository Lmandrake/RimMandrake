using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>One terrain swap the silt-trap performs (design §3.4).</summary>
	public class RM_SiltSwap
	{
		public TerrainDef from;
		public TerrainDef to;
	}

	/// <summary>
	/// The silt-trap's swap table as data, on the RM_SiltTrap ThingDef. River Works ships the surface
	/// pairs; TerminalBiomes patches in its own sea pair (RM_BankSilt -> RM_BankSilt_Rich).
	/// </summary>
	public class RM_SiltSwapExtension : DefModExtension
	{
		public List<RM_SiltSwap> swaps = new List<RM_SiltSwap>();

		public TerrainDef RichFor(TerrainDef t)
		{
			for (int i = 0; i < swaps.Count; i++)
			{
				if (swaps[i].from == t)
				{
					return swaps[i].to;
				}
			}
			return null;
		}
	}

	/// <summary>
	/// The silt-trap (moved from TerminalBiomes, slice 2). While healthy it richens ONE swappable cell
	/// within r=3.5 per interval (PROVISIONAL, half a day); a nearby weir's breach reverts every cell
	/// it changed. "Dredge" is vanilla Repair: below 40 % HP it is clogged and stops richening.
	/// </summary>
	public class RM_Building_SiltTrap : Building
	{
		private const int WearIntervalTicks = 3000;
		private const float WorkingHpFraction = 0.4f;
		private const float RichenRadius = 3.5f;

		private List<IntVec3> richened = new List<IntVec3>();
		private List<TerrainDef> originals = new List<TerrainDef>();
		private int nextRichenTick = -1;
		private float wearDebt;

		protected override void Tick()
		{
			base.Tick();
			if (!RM_RiversSettings.WorksActive)
			{
				return;
			}
			if (this.IsHashIntervalTick(WearIntervalTicks) && HitPoints > 1)
			{
				wearDebt += RM_RiversSettings.wearRateMultiplier;
				int n = (int)wearDebt;
				if (n > 0)
				{
					wearDebt -= n;
					HitPoints = System.Math.Max(1, HitPoints - n);
				}
				if (Clogged != printedClogged)
				{
					Map.mapDrawer.MapMeshDirty(Position, MapMeshFlagDefOf.Things);   // wear or a repair crossed the clog line
				}
			}
			if (!RM_RiversSettings.siltRichening)
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			int interval = Mathf.Max(250, Mathf.RoundToInt(RM_RiversSettings.siltIntervalDays * 60000f));
			if (nextRichenTick < 0 || nextRichenTick > now + interval)
			{
				nextRichenTick = now + interval;
			}
			if (now >= nextRichenTick)
			{
				nextRichenTick = now + interval;
				if (HitPoints >= MaxHitPoints * WorkingHpFraction)
				{
					RichenOne();
				}
			}
		}

		/// <summary>Richen one cell. Public so the first script can force it. Returns the cell or Invalid.</summary>
		public IntVec3 RichenOne()
		{
			RM_SiltSwapExtension table = def.GetModExtension<RM_SiltSwapExtension>();
			if (Map == null || table == null)
			{
				return IntVec3.Invalid;
			}
			foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, RichenRadius, useCenter: false))
			{
				if (!c.InBounds(Map))
				{
					continue;
				}
				TerrainDef here = c.GetTerrain(Map);
				TerrainDef rich = table.RichFor(here);
				if (rich == null)
				{
					continue;
				}
				Map.terrainGrid.SetTerrain(c, rich);
				richened.Add(c);
				originals.Add(here);
				Map.mapDrawer.MapMeshDirty(Position, MapMeshFlagDefOf.Things);   // the silt wedge grows (Print)
				return c;
			}
			return IntVec3.Invalid;
		}

		/// <summary>Breach effect: every cell this trap richened reverts - unless the player has since
		/// built a floor over it (a cell not still carrying our terrain is not ours to overwrite).</summary>
		public void Clog()
		{
			if (Map == null)
			{
				return;
			}
			RM_SiltSwapExtension table = def.GetModExtension<RM_SiltSwapExtension>();
			for (int i = 0; i < richened.Count; i++)
			{
				IntVec3 c = richened[i];
				TerrainDef orig = i < originals.Count ? originals[i] : null;
				if (orig == null || !c.InBounds(Map))
				{
					continue;
				}
				TerrainDef rich = table?.RichFor(orig);
				if (rich == null || c.GetTerrain(Map) == rich)
				{
					Map.terrainGrid.SetTerrain(c, orig);
				}
			}
			richened.Clear();
			originals.Clear();
			Map.mapDrawer.MapMeshDirty(Position, MapMeshFlagDefOf.Things);
		}

		private bool Clogged => HitPoints < MaxHitPoints * WorkingHpFraction;

		private bool printedClogged;

		/// <summary>RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fix 10 (owner card 2026-10-17: "Commission REVIEW.md items
		/// 3,4,6,7,8,9,10 in four styles; judged in game"): under the baffle (its look; the waterline is in the art), a
		/// sediment wedge against the upstream face, tip pointing up the current found nearest the trap, growing with every
		/// cell it has richened and full once clogged (RM_RiverMath.SiltWedge). No current within reach: no wedge.</summary>
		public override void Print(SectionLayer layer)
		{
			printedClogged = Clogged;
			int flow = -1;
			RM_MapComponent_RiverCurrent cur = Map?.GetComponent<RM_MapComponent_RiverCurrent>();
			if (cur != null)
			{
				foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, WedgeSearchRadius, useCenter: true))
				{
					if (c.InBounds(Map) && (flow = cur.FlowDirAt(c)) >= 0)
					{
						break;
					}
				}
			}
			if (RM_RiverMath.SiltWedge(flow, richened.Count, printedClogged, out float ox, out float oz, out float ang, out float s))
			{
				Material wedge = RM_WeirArt.Mat(WedgeTex, ShaderDatabase.Transparent);
				if (wedge != null)
				{
					Vector3 at = this.TrueCenter() + new Vector3(ox, 0f, oz);
					at.y -= Altitudes.AltInc * 0.3f;   // on the ground, under the baffle
					Printer_Plane.PrintPlane(layer, at, new Vector2(1.1f * s, 1.1f * s), wedge, ang);
				}
			}
			base.Print(layer);
		}

		private const float WedgeSearchRadius = 2.9f;

		private const string WedgeTex = "RimMandrake/FlowWorks/Rivers/RM_SiltWedge";

		public int RichenedCount => richened.Count;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref richened, "richened", LookMode.Value);
			Scribe_Collections.Look(ref originals, "richenedFrom", LookMode.Def);
			Scribe_Values.Look(ref nextRichenTick, "nextRichenTick", -1);
			Scribe_Values.Look(ref wearDebt, "wearDebt", 0f);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				richened = richened ?? new List<IntVec3>();
				originals = originals ?? new List<TerrainDef>();
			}
		}
	}

	/// <summary>One thing a river can bring down into a weir.</summary>
	public class RM_RiverDriftEntry
	{
		public ThingDef thing;
		public float weight = 1f;
		public IntRange count = new IntRange(1, 1);
	}

	/// <summary>
	/// Owner card 2 (2026-10-03): a weir catches fish "plus drift, but the drift must be BIOME-RELEVANT
	/// items per biome, not generic wood". One def per biome group; any mod adds a def for its own
	/// biomes. Shipped tables are PROVISIONAL. Weir review 2026-10-23 (owner: "No auto fish capture"): the weir no longer
	/// rolls these out of nothing and nothing reads them now; kept as data for the open question of rivers carrying
	/// biome flotsam ONTO the map as real floating things (design/RimMandrake/weir_review_2026-10-23.md).
	/// </summary>
	public class RM_RiverDriftDef : Def
	{
		public List<BiomeDef> biomes = new List<BiomeDef>();
		public List<RM_RiverDriftEntry> drift = new List<RM_RiverDriftEntry>();

		public static RM_RiverDriftEntry RollFor(BiomeDef biome)
		{
			if (biome == null)
			{
				return null;
			}
			List<RM_RiverDriftEntry> pool = new List<RM_RiverDriftEntry>();
			List<RM_RiverDriftDef> all = DefDatabase<RM_RiverDriftDef>.AllDefsListForReading;
			for (int i = 0; i < all.Count; i++)
			{
				if (all[i].biomes != null && all[i].biomes.Contains(biome) && all[i].drift != null)
				{
					for (int j = 0; j < all[i].drift.Count; j++)
					{
						if (all[i].drift[j].thing != null && all[i].drift[j].weight > 0f)
						{
							pool.Add(all[i].drift[j]);
						}
					}
				}
			}
			return pool.Count == 0 ? null : pool.RandomElementByWeight(e => e.weight);
		}

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string e in base.ConfigErrors())
			{
				yield return e;
			}
			if (biomes.NullOrEmpty())
			{
				yield return "RM_RiverDriftDef names no biome";
			}
			if (drift.NullOrEmpty())
			{
				yield return "RM_RiverDriftDef has no drift entries";
			}
		}
	}
}
