using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks.Drilling
{
	/// <summary>
	/// MANY_WATERS_DRILL_BUILDINGS_1 — the fourth acquisition route: "you can
	/// drill it, on the right maps, with custom buildings" (design doc §3
	/// ruling 3). Raises whatever RM_MapComponent_SubsurfaceLiquid says this
	/// map's subsurface holds into an adjacent excavated cell, one of the
	/// engine's own driver-API writes (RM_MapComponent_Excavation
	/// .TrySetDriverFill) — the same public surface a flood-driver client
	/// uses (CANYON_FLOOD_ERASES_CANALS_1's §8 boundary), never a new fluid
	/// path of its own.
	///
	/// 🔴 NOT A SOURCE (ruling 34). This never forms or credits an
	/// RM_LiquidBody; it spends RM_MapComponent_SubsurfaceLiquid's own,
	/// separate, non-refilling reserve straight into the grid.
	///
	/// 🔑 Fluid identity (LIQUID_BODY_FLUID_IDENTITY_1): the drill produces when its outlet is dry (it claims
	/// the cell for its canal fluid) or already holds that fluid; an outlet holding another fluid is refused,
	/// because fluids never mix. The old "one ActiveFluid per map" limitation is gone.
	/// </summary>
	public class Building_LiquidDrill : Building
	{
		/// <summary>Fill-units pulled from the reserve but not yet placed
		/// into the grid because the outlet cell did not have room for a
		/// whole level's worth yet. Carried between cycles so a slow drill on
		/// a thick liquid does not round its own output down to zero forever
		/// — the same accumulator shape RM_MapComponent_Excavation.ApplyRain
		/// uses for light rain.</summary>
		private float pendingUnits;

		private static readonly RM_LiquidDrillExtension DefaultExtension = new RM_LiquidDrillExtension();

		private RM_LiquidDrillExtension Ext => def.GetModExtension<RM_LiquidDrillExtension>() ?? DefaultExtension;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref pendingUnits, "RM_drillPendingUnits", 0f);
		}

		/// <summary>The cell this drill pours into — the one cell its
		/// footprint faces, so rotating the drill at placement chooses the
		/// outlet the same way a turret's rotation chooses its facing.</summary>
		public IntVec3 OutletCell => Position + Rotation.FacingCell;

		public override void TickRare()
		{
			base.TickRare();
			if (!RimMandrakeFlowWorksSettings.liquidDrillingEnabled)
			{
				return;
			}
			if (Ext.requiresPower)
			{
				CompPowerTrader power = GetComp<CompPowerTrader>();
				if (power != null && !power.PowerOn)
				{
					return;
				}
			}

			RM_MapComponent_SubsurfaceLiquid survey = Map.GetComponent<RM_MapComponent_SubsurfaceLiquid>();
			RM_MapComponent_Excavation excavation = Map.GetComponent<RM_MapComponent_Excavation>();
			if (survey == null || excavation == null || !survey.HasYield)
			{
				return;
			}

			LiquidDef liquid = survey.YieldedLiquid;
			FluidDef canalFluid = liquid != null ? liquid.canalFluid : null;
			if (canalFluid == null)
			{
				// This liquid has no canal form to feed at all: the reserve is NOT spent.
				return;
			}

			IntVec3 outlet = OutletCell;
			if (!excavation.IsExcavated(outlet))
			{
				return;
			}
			if (excavation.FillAt(outlet) > 0 && excavation.FluidAt(outlet) != canalFluid)
			{
				// Fluids never mix (LIQUID_BODY_FLUID_IDENTITY_1): the outlet already holds another liquid, so the
				// reserve is not spent. A dry outlet is claimed by this drill's fluid.
				return;
			}

			byte depth = excavation.DepthAt(outlet);
			byte fill = excavation.FillAt(outlet);
			int room = depth - fill;
			if (room <= 0)
			{
				// Backed up: the outlet is already brimming. The reserve is
				// not spent for liquid with nowhere to go, matching the
				// engine's own "a failed transfer must not move liquid"
				// discipline (RM_MapComponent_Excavation.PickDonor).
				return;
			}

			float unitPerLevel = canalFluid.volumePerTile > 0f ? canalFluid.volumePerTile : 1f;
			float roomUnits = room * unitPerLevel;
			if (pendingUnits < roomUnits)
			{
				float wantUnits = Mathf.Max(0f,
					Mathf.Min(roomUnits - pendingUnits,
						RimMandrakeFlowWorksSettings.DrillUnitsPerCycle * Mathf.Max(0f, Ext.unitsPerCycleMultiplier)));
				if (wantUnits > 0f)
				{
					pendingUnits += survey.TryExtract(wantUnits);
				}
			}

			int levels = Mathf.Min(room, Mathf.FloorToInt(pendingUnits / unitPerLevel));
			if (levels <= 0)
			{
				return;
			}
			pendingUnits -= levels * unitPerLevel;
			excavation.TrySetDriverFill(outlet, fill + levels, canalFluid);
		}

		public override string GetInspectString()
		{
			string baseString = base.GetInspectString();
			string status;
			RM_MapComponent_SubsurfaceLiquid survey = Map != null ? Map.GetComponent<RM_MapComponent_SubsurfaceLiquid>() : null;
			if (survey == null)
			{
				status = "RM_SubsurfaceUnsurveyed".Translate();
			}
			else
			{
				status = survey.StatusReport();
				if (survey.HasYield)
				{
					RM_MapComponent_Excavation excavation = Map.GetComponent<RM_MapComponent_Excavation>();
					if (excavation != null && !excavation.IsExcavated(OutletCell))
					{
						status += "\n" + "RM_DrillNeedsOutlet".Translate();
					}
					FluidDef canalFluid = survey.YieldedLiquid != null ? survey.YieldedLiquid.canalFluid : null;
					if (canalFluid == null)
					{
						status += "\n" + "RM_DrillLiquidHasNoCanalForm".Translate();
					}
					else if (excavation != null && excavation.FillAt(OutletCell) > 0
						&& excavation.FluidAt(OutletCell) != null && excavation.FluidAt(OutletCell) != canalFluid)
					{
						status += "\n" + "RM_DrillLiquidMismatch".Translate(excavation.FluidAt(OutletCell).LabelCap);
					}
				}
			}
			return string.IsNullOrEmpty(baseString) ? status : baseString + "\n" + status;
		}
	}

	/// <summary>A drill that pours nowhere is a button that lies — same
	/// reasoning as PlaceWorker_LadderOnExcavation, checked against the
	/// OUTLET cell (the footprint-facing neighbour), not the drill's own
	/// footprint, because that is the cell it actually writes to.</summary>
	public class PlaceWorker_DrillNeedsExcavatedOutlet : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
			Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			if (map == null)
			{
				return true;
			}
			RM_MapComponent_Excavation engine = map.GetComponent<RM_MapComponent_Excavation>();
			IntVec3 outlet = loc + rot.FacingCell;
			if (engine == null || !engine.IsExcavated(outlet))
			{
				return "RM_DrillNeedsOutlet".Translate();
			}
			return true;
		}
	}
}
