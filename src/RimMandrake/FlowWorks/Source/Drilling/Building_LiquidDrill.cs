using LudeonTK;
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

		/// <summary>TANK_CONTENTS_SALVAGE_ON_DECONSTRUCT (C2-F5): extracted units not yet poured go back into the deposit, never
		/// deleted with the drill. A minified drill keeps them (despawned, not destroyed).</summary>
		public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
		{
			if (Spawned && pendingUnits > 0f && mode != DestroyMode.WillReplace)
			{
				Map.GetComponent<RM_MapComponent_SubsurfaceLiquid>()?.ReturnUnits(pendingUnits);
				pendingUnits = 0f;
			}
			base.Destroy(mode);
		}

		/// <summary>The cell this drill pours into — the one cell its
		/// footprint faces, so rotating the drill at placement chooses the
		/// outlet the same way a turret's rotation chooses its facing.</summary>
		public IntVec3 OutletCell => OutletFor(Position, Rotation, def.size);

		/// <summary>The cell just past the footprint's facing edge. Position +
		/// FacingCell is only outside the footprint for a 1x1: for the 2x2
		/// RM_LiquidDrill it lands INSIDE the drill in every rotation
		/// (GenAdj.AdjustForRotation), so the drill poured under itself.</summary>
		public static IntVec3 OutletFor(IntVec3 pos, Rot4 rot, IntVec2 size)
		{
			CellRect r = GenAdj.OccupiedRect(pos, rot, size);
			switch (rot.AsInt)
			{
				case 0: return new IntVec3(pos.x, 0, r.maxZ + 1);
				case 1: return new IntVec3(r.maxX + 1, 0, pos.z);
				case 2: return new IntVec3(pos.x, 0, r.minZ - 1);
				default: return new IntVec3(r.minX - 1, 0, pos.z);
			}
		}

		private RM_DrillSurveyMath.Block lastBlock;

		/// <summary>BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY: the first condition that keeps this drill from pouring, read fresh
		/// from the map. The tick, the inspect line and the overhead icon all use this one answer.</summary>
		public RM_DrillSurveyMath.Block CurrentBlock()
		{
			RM_DrillSurveyMath.State st = new RM_DrillSurveyMath.State();
			st.settingOn = RimMandrakeFlowWorksSettings.liquidDrillingEnabled;
			CompFlickable flick = GetComp<CompFlickable>();
			st.switchedOn = flick == null || flick.SwitchIsOn;
			CompPowerTrader power = GetComp<CompPowerTrader>();
			st.needsPower = Ext.requiresPower && power != null;
			st.powered = power == null || power.PowerOn;
			RM_MapComponent_SubsurfaceLiquid survey = Map != null ? Map.GetComponent<RM_MapComponent_SubsurfaceLiquid>() : null;
			RM_MapComponent_Excavation excavation = Map != null ? Map.GetComponent<RM_MapComponent_Excavation>() : null;
			st.surveyed = survey != null && survey.Surveyed && excavation != null;
			st.hasYield = survey != null && survey.HasYield;
			st.reserve = survey != null ? survey.ReserveRemaining : 0f;
			FluidDef canalFluid = st.hasYield && survey.YieldedLiquid != null ? survey.YieldedLiquid.canalFluid : null;
			st.hasCanalForm = canalFluid != null;
			st.fluidAllowed = canalFluid == null || RimMandrakeFlowWorksSettings.FluidAllowed(canalFluid);
			if (excavation != null && canalFluid != null)
			{
				IntVec3 outlet = OutletCell;
				st.outletDug = excavation.IsExcavated(outlet);
				if (st.outletDug)
				{
					FluidDef outletFluid = excavation.FluidAt(outlet);
					st.outletOtherLiquid = excavation.FillAt(outlet) > 0 && outletFluid != null && outletFluid != canalFluid;
					st.outletBrimming = excavation.DepthAt(outlet) - excavation.FillAt(outlet) <= 0;
				}
			}
			return RM_DrillSurveyMath.WhyNot(st);
		}

		/// <summary>The sentence for a block (empty for None).</summary>
		public string BlockText(RM_DrillSurveyMath.Block block)
		{
			if (block == RM_DrillSurveyMath.Block.None)
			{
				return "RM_DrillWhy_None".Translate();
			}
			string key = "RM_DrillWhy_" + block;
			RM_MapComponent_SubsurfaceLiquid survey = Map != null ? Map.GetComponent<RM_MapComponent_SubsurfaceLiquid>() : null;
			RM_MapComponent_Excavation excavation = Map != null ? Map.GetComponent<RM_MapComponent_Excavation>() : null;
			string cell = OutletCell.x + "," + OutletCell.z;
			switch (block)
			{
				case RM_DrillSurveyMath.Block.LiquidDisabledInSettings:
					return key.Translate(survey?.YieldedLiquid != null ? survey.YieldedLiquid.LabelCap.ToString() : "?");
				case RM_DrillSurveyMath.Block.OutletNotDug:
				case RM_DrillSurveyMath.Block.OutletBrimming:
					return key.Translate(cell);
				case RM_DrillSurveyMath.Block.OutletOtherLiquid:
					return key.Translate(cell, excavation?.FluidAt(OutletCell) != null ? excavation.FluidAt(OutletCell).LabelCap.ToString() : "?");
				default:
					return key.Translate();
			}
		}

		public override void DynamicDrawPhaseAt(DrawPhase phase, Vector3 drawLoc, bool flip = false)
		{
			base.DynamicDrawPhaseAt(phase, drawLoc, flip);
			// Vanilla draws the power-off and no-power icons itself; any other reason gets the question mark.
			if (phase == DrawPhase.Draw && Spawned && lastBlock != RM_DrillSurveyMath.Block.None
				&& lastBlock != RM_DrillSurveyMath.Block.SwitchedOff && lastBlock != RM_DrillSurveyMath.Block.Unpowered
				&& lastBlock != RM_DrillSurveyMath.Block.OutletBrimming)
			{
				Map.overlayDrawer.DrawOverlay(this, OverlayTypes.QuestionMark);
			}
		}

		public override void TickRare()
		{
			base.TickRare();
			CompPowerTrader power = GetComp<CompPowerTrader>();
			CompFlickable flick = GetComp<CompFlickable>();
			if (power != null)
			{
				// Switched off (here or in Mod Settings), the drill draws nothing (the setting's promise), as the pump does.
				bool on = RimMandrakeFlowWorksSettings.liquidDrillingEnabled && (flick == null || flick.SwitchIsOn);
				power.PowerOutput = on ? -power.Props.PowerConsumption : 0f;
			}
			lastBlock = CurrentBlock();
			if (lastBlock != RM_DrillSurveyMath.Block.None && lastBlock != RM_DrillSurveyMath.Block.OutletBrimming)
			{
				return;
			}

			RM_MapComponent_SubsurfaceLiquid survey = Map.GetComponent<RM_MapComponent_SubsurfaceLiquid>();
			RM_MapComponent_Excavation excavation = Map.GetComponent<RM_MapComponent_Excavation>();
			FluidDef canalFluid = survey.YieldedLiquid.canalFluid;
			IntVec3 outlet = OutletCell;

			byte depth = excavation.DepthAt(outlet);
			byte fill = excavation.FillAt(outlet);
			int room = depth - fill;
			if (room <= 0)
			{
				// Backed up: the outlet is already brimming. The reserve is
				// not spent for liquid with nowhere to go, matching the
				// engine's own "a failed transfer must not move liquid"
				// discipline (RM_MapComponent_Excavation.PickDonor). P4: it is still pressing on the outlet, so the
				// outlet stays a flow-order input (PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD).
				excavation.NoteDriverBackedUp(outlet);
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
			// A refused fill (fluid disabled in settings, or a foreign liquid in the outlet) keeps
			// the extracted units pending instead of discarding them (GPT FlowWorks review #5).
			if (excavation.TrySetDriverFill(outlet, fill + levels, canalFluid))
			{
				pendingUnits -= levels * unitPerLevel;
			}
		}

		public override string GetInspectString()
		{
			string baseString = base.GetInspectString();
			string status;
			RM_MapComponent_SubsurfaceLiquid survey = Map != null ? Map.GetComponent<RM_MapComponent_SubsurfaceLiquid>() : null;
			status = survey == null ? "RM_SubsurfaceUnsurveyed".Translate().ToString() : survey.StatusReport();
			if (Spawned)
			{
				status += "\n" + BlockText(CurrentBlock());
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
			// DRILL_PLACEMENT_ENFORCE_NO_DRY_HOLES (owner card 2026-10-22 "Refuse on empty survey"): nothing to pour, no drill
			RM_MapComponent_SubsurfaceLiquid survey = map.GetComponent<RM_MapComponent_SubsurfaceLiquid>();
			if (survey != null)
			{
				switch (RM_DrillSurveyMath.Placement(survey.Surveyed, survey.HasYield, survey.ReserveRemaining))
				{
					case RM_DrillSurveyMath.Verdict.NoYield:
						return "RM_DrillPlaceNoYield".Translate();
					case RM_DrillSurveyMath.Verdict.Spent:
						return "RM_DrillPlaceSpent".Translate();
				}
			}
			RM_MapComponent_Excavation engine = map.GetComponent<RM_MapComponent_Excavation>();
			IntVec3 outlet = Building_LiquidDrill.OutletFor(loc, rot, (checkingDef as ThingDef)?.size ?? IntVec2.One);
			if (engine == null || !engine.IsExcavated(outlet))
			{
				return "RM_DrillNeedsOutlet".Translate();
			}
			return true;
		}

		/// <summary>DRILL_SURVEY_EXPLAIN_BEFORE_STEEL_IS_SPENT (UX review 2026-10-22): every map is surveyed when it loads
		/// (RM_MapComponent_SubsurfaceLiquid.FinalizeInit), so the answer exists before anything is built. Show it beside the
		/// mouse while placing, instead of only on a finished drill.</summary>
		public override void DrawPlaceMouseAttachments(float curX, ref float curY, BuildableDef def, IntVec3 center, Rot4 rot)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_SubsurfaceLiquid survey = map?.GetComponent<RM_MapComponent_SubsurfaceLiquid>();
			Color was = GUI.color;
			if (survey == null || !survey.Surveyed)
			{
				DrawTextLine(curX, ref curY, "RM_SubsurfaceUnsurveyed".Translate());
			}
			else if (!survey.HasYield || survey.ReserveRemaining <= 0f)
			{
				GUI.color = ColorLibrary.RedReadable;
				DrawTextLine(curX, ref curY, survey.HasYield ? "RM_DrillPlaceSpent".Translate().ToString() : "RM_DrillPlaceNoYield".Translate().ToString());
			}
			else
			{
				DrawTextLine(curX, ref curY, survey.StatusReport());
			}
			if (!RimMandrakeFlowWorksSettings.liquidDrillingEnabled)
			{
				GUI.color = ColorLibrary.RedReadable;
				DrawTextLine(curX, ref curY, "RM_DrillPlaceOff".Translate());
			}
			GUI.color = was;
		}
	}

	/// <summary>BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY: god-mode actions to give a map a subsurface yield to test with.</summary>
	public static class RM_DrillDebug
	{
		private const string CAT = "RMFlowWorks";
		public const float DebugReserveUnits = 5000f;

		[DebugAction(CAT, "Give this map a subsurface yield...", allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void GiveYield()
		{
			RM_MapComponent_SubsurfaceLiquid survey = Find.CurrentMap?.GetComponent<RM_MapComponent_SubsurfaceLiquid>();
			if (survey == null)
			{
				Messages.Message("RM_DebugNoSurvey".Translate(), MessageTypeDefOf.RejectInput, false);
				return;
			}
			System.Collections.Generic.List<LiquidDef> liquids = new System.Collections.Generic.List<LiquidDef>();
			foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
			{
				if (l.canalFluid != null) liquids.Add(l);
			}
			System.Collections.Generic.List<DebugMenuOption> list = new System.Collections.Generic.List<DebugMenuOption>();
			foreach (LiquidDef l in RM_DrillDebugOrder(liquids))
			{
				LiquidDef pick = l;
				list.Add(new DebugMenuOption(pick.defName, DebugMenuOptionMode.Action, delegate
				{
					survey.DebugSetYield(pick, DebugReserveUnits);
					Log.Message("[RMFlowWorksDebug] subsurface yield set: " + pick.defName + ", " + DebugReserveUnits + " fill-units");
				}));
			}
			Find.WindowStack.Add(new Dialog_DebugOptionListLister(list));
		}

		/// <summary>Water first (the default pick), then the rest by name.</summary>
		private static System.Collections.Generic.IEnumerable<LiquidDef> RM_DrillDebugOrder(System.Collections.Generic.List<LiquidDef> liquids)
		{
			liquids.Sort((a, b) =>
			{
				int ra = a.defName == "RM_Liquid_FreshWater" ? 0 : 1;
				int rb = b.defName == "RM_Liquid_FreshWater" ? 0 : 1;
				return ra != rb ? ra.CompareTo(rb) : string.CompareOrdinal(a.defName, b.defName);
			});
			return liquids;
		}

		[DebugAction(CAT, "Clear subsurface yield", allowedGameStates = AllowedGameStates.PlayingOnMap)]
		private static void ClearYield()
		{
			Find.CurrentMap?.GetComponent<RM_MapComponent_SubsurfaceLiquid>()?.DebugClearYield();
			Log.Message("[RMFlowWorksDebug] subsurface yield cleared");
		}
	}
}
