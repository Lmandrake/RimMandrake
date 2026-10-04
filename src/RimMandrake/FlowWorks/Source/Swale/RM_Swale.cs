using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	// ════════════════════════════════════════════════════════════════════════
	// RM_Swale — CRACKEDLANDS_MECHANICS_BUILD_1 §1 (the crown ruling, owner
	// sitting FLOODEDCANYON_BEDAZZLE_SITTING_1, 2026-09-28).
	//
	// A graded, perforated liner laid in an excavated cell. While the cell it
	// sits in carries WATER (a FlowWorks fill whose identity is RM_Fluid_Water,
	// or water terrain standing on it — which is how a seasonal flood fills it
	// for free), it slowly walks the cells around it up a fertility ladder
	// (sand -> soil -> rich soil by default). Bounded three ways, per the
	// item's own "Watch out" (or it terraforms the biome out of its premise):
	//   * CAP    — the ladder's top rung is the ceiling; a cell already there
	//              is never touched, and nothing off the ladder is ever touched;
	//   * RATE   — one rung on one cell per ticksPerStep of FED time;
	//   * FED    — no water in the swale's own cell, no progress, and progress
	//              does not bank while dry.
	// Terrain is written with TerrainGrid.SetTerrain on the base layer, the
	// same call the flood engine's recede uses for its own terrain swaps.
	//
	// PROVISIONAL (first-guess numbers, owner ruling 2026-10-03): radius 2.9
	// (the 1-2 ring), 60000 ticks (one day) of fed time per rung step, ladder
	// Sand -> Soil -> SoilRich. Tuned live later.
	//
	// NOT built here: the Utinni campaign lock ("locked until discovered in the
	// Cracked Lands, then travels with the ship"). Discovery is the first
	// completed survey, and the survey/cistern loop is not built yet — see
	// CRACKEDLANDS_SWALE_CAMPAIGN_LOCK_1.
	// ════════════════════════════════════════════════════════════════════════

	public class CompProperties_Swale : CompProperties
	{
		/// <summary>Fertility ladder, lowest rung first. Only base terrain ON
		/// this list is ever rewritten, and only one rung up.</summary>
		public List<TerrainDef> ladder = new List<TerrainDef>();

		/// <summary>PROVISIONAL. 2.9 = every cell within two of the swale.</summary>
		public float radius = 2.9f;

		/// <summary>PROVISIONAL. Fed ticks per one-rung step (before the
		/// Mod Settings rate multiplier).</summary>
		public int ticksPerStep = 60000;

		public CompProperties_Swale()
		{
			compClass = typeof(RM_CompSwale);
		}
	}

	public class RM_CompSwale : ThingComp
	{
		private float fedProgress;
		private int stepsTaken;

		public CompProperties_Swale Props => (CompProperties_Swale)props;

		public int StepsTaken => stepsTaken;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref fedProgress, "rmSwaleFedProgress", 0f);
			Scribe_Values.Look(ref stepsTaken, "rmSwaleStepsTaken", 0);
		}

		public override void CompTickRare()
		{
			base.CompTickRare();
			if (!RimMandrakeFlowWorksSettings.swaleEnabled || parent.Map == null)
			{
				return;
			}
			if (!RM_SwaleRules.IsFed(parent.Map, parent.Position))
			{
				return; // dry: nothing banks
			}
			fedProgress += GenTicks.TickRareInterval * RimMandrakeFlowWorksSettings.SwaleRateMultiplier;
			if (fedProgress < Props.ticksPerStep)
			{
				return;
			}
			fedProgress = 0f;
			if (RM_SwaleRules.TryStep(parent.Map, parent.Position, Props, out _, out _, out _))
			{
				stepsTaken++;
			}
		}

		public override string CompInspectStringExtra()
		{
			if (parent.Map == null)
			{
				return null;
			}
			if (!RimMandrakeFlowWorksSettings.swaleEnabled)
			{
				return "Swale: switched off in Mod Settings.";
			}
			bool fed = RM_SwaleRules.IsFed(parent.Map, parent.Position);
			return fed
				? "Swale: carrying water — " + (fedProgress / Props.ticksPerStep).ToStringPercent() + " toward the next soil step."
				: "Swale: dry. Nothing grows from a dry swale.";
		}
	}

	public static class RM_SwaleRules
	{
		/// <summary>Water, and only water: a FlowWorks fill whose recorded
		/// identity is RM_Fluid_Water, or water terrain standing on the cell
		/// (a flood or a natural source). Tar, slime, poisoned water and every
		/// other liquid feed nothing.</summary>
		public static bool IsFed(Map map, IntVec3 cell)
		{
			if (map == null || !cell.InBounds(map))
			{
				return false;
			}
			RM_MapComponent_Excavation engine = map.GetComponent<RM_MapComponent_Excavation>();
			FluidDef fluid = engine?.FluidAt(cell);
			if (engine != null && engine.FillAt(cell) > 0 && fluid != null)
			{
				return fluid.defName == "RM_Fluid_Water";
			}
			return IsWaterTerrain(map.terrainGrid.TerrainAt(cell));
		}

		public static bool IsWaterTerrain(TerrainDef t)
		{
			if (t == null || !t.IsWater)
			{
				return false;
			}
			// Vanilla's plain water family (WaterShallow, WaterMovingShallow,
			// WaterOceanShallow, WaterDeep, ...) and FlowWorks' own fill rungs.
			return t.defName.StartsWith("Water") || t.defName.StartsWith("RM_Fill_Water_");
		}

		/// <summary>The rung index of a terrain on the ladder, or -1.</summary>
		public static int Rung(CompProperties_Swale props, TerrainDef t)
		{
			return t == null ? -1 : props.ladder.IndexOf(t);
		}

		/// <summary>One rung on one cell: the lowest-rung eligible cell in the
		/// radius, nearest first. Eligible = in bounds, not the swale's own
		/// cell, not excavated, base terrain on the ladder BELOW the top rung.
		/// Returns false when every cell in reach is at the cap (or off it).</summary>
		public static bool TryStep(Map map, IntVec3 center, CompProperties_Swale props,
			out IntVec3 stepped, out TerrainDef from, out TerrainDef to)
		{
			stepped = IntVec3.Invalid;
			from = to = null;
			if (map == null || props == null || props.ladder.NullOrEmpty())
			{
				return false;
			}
			RM_MapComponent_Excavation engine = map.GetComponent<RM_MapComponent_Excavation>();
			int bestRung = int.MaxValue;
			float bestDist = float.MaxValue;
			foreach (IntVec3 c in GenRadial.RadialCellsAround(center, props.radius, false))
			{
				if (!c.InBounds(map) || (engine != null && engine.IsExcavated(c)))
				{
					continue;
				}
				int r = Rung(props, map.terrainGrid.BaseTerrainAt(c));
				if (r < 0 || r >= props.ladder.Count - 1)
				{
					continue; // off the ladder, or already at the cap
				}
				float d = c.DistanceToSquared(center);
				if (r < bestRung || (r == bestRung && d < bestDist))
				{
					bestRung = r;
					bestDist = d;
					stepped = c;
				}
			}
			if (!stepped.IsValid)
			{
				return false;
			}
			from = props.ladder[bestRung];
			to = props.ladder[bestRung + 1];
			map.terrainGrid.SetTerrain(stepped, to);
			return true;
		}

		/// <summary>Bridge proof (jawa/static_call): fire one step NOW on the
		/// swale at <paramref name="cell"/>, gated exactly as the tick is
		/// (Mod Settings switch, then fed). "STEP (x,z) A->B | fed True",
		/// "CAPPED | fed True", "DRY", "OFF" or "REFUSED: ...".</summary>
		public static string ProofStep(Map map, IntVec3 cell)
		{
			if (map == null)
			{
				return "REFUSED: no map";
			}
			Building b = cell.GetFirstBuilding(map);
			RM_CompSwale comp = b?.GetComp<RM_CompSwale>();
			if (comp == null)
			{
				return "REFUSED: no swale at " + cell;
			}
			if (!RimMandrakeFlowWorksSettings.swaleEnabled)
			{
				return "OFF";
			}
			if (!IsFed(map, cell))
			{
				return "DRY";
			}
			return TryStep(map, cell, comp.Props, out IntVec3 c, out TerrainDef f, out TerrainDef t)
				? "STEP (" + c.x + "," + c.z + ") " + f.defName + "->" + t.defName + " | fed True"
				: "CAPPED | fed True";
		}
	}

	public class PlaceWorker_SwaleOnExcavation : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
			Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			RM_MapComponent_Excavation engine = map?.GetComponent<RM_MapComponent_Excavation>();
			if (engine == null || !engine.IsExcavated(loc))
			{
				return "RMFlow_SwaleNeedsExcavation".Translate();
			}
			return true;
		}
	}
}
