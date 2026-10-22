using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Sheet
{
	/// <summary>D5, widened by the owner 2026-10-22 (<i>"Build for all flowworks liquids."</i>): a spilled sheet of a burnable
	/// liquid (chemfuel, astrofuel, oil, tar, propane: FluidDef.fireKind) spreads like any spill and BURNS, behind its own
	/// setting (RM_SheetSettings.fuelSpillsBurnEnabled) and the canal-fire master (canalFireEnabled).
	///
	/// - IGNITION: a vanilla Fire spawning on or beside a burnable square (RM_Patch_FireLightsLiquid), a flame or bomb blast
	///   touching it (RM_Patch_ExplosionLightsLiquid), or a burning channel square beside it.
	/// - FRONT: one front for every burnable liquid, as the channels': a lit square lights its burnable N/E/S/W neighbours
	///   <c>fireFrontTicksPerCell</c> later (RM_FireMath.FrontDue; an inferno takes the chemfuel spread dial), and lights a
	///   burnable channel square beside it through the channel fire's front (RM_LiquidFire.OfferLight), so fire crosses both
	///   ways (the channel side: RM_LiquidFire.Maintain lights the spill beside a burning channel square).
	/// - BURN: the channels' rate, ruling 7 (a notch a day; an inferno a level every 5 s at burn rate 1); a detonating liquid
	///   (astrofuel, with its setting on) is consumed whole on the first check and flame-blasts (a few per check). Burned
	///   liquid is GONE, counted as "burned" in the sheet ledger (RM_SheetMath.Burn), never silent.
	/// - EFFECT: the channel's flame on the square (look only), pawns in it may catch fire, heat, and now and then a vanilla
	///   fire beside it (grass and things burn, and that fire lights more spill). A sheet of a liquid that does not burn puts
	///   fire out (RM_MapComponent_Sheet.Effects); a fuel sheet never does.
	/// NOT built: rain douses only channel fires (a burning sheet goes out when it burns dry or its switch goes off).</summary>
	public partial class RM_MapComponent_Sheet
	{
		private const int FireCheckTicks = 60;
		private const int MaxBlastsPerCheck = 3;
		private const float BlastRadius = 1.9f;

		private Dictionary<int, int> burnLit = new Dictionary<int, int>();  // square -> tick it lit
		private Dictionary<int, int> burnAcc = new Dictionary<int, int>();  // square -> burn accumulator (tick-dL remainder)
		private List<int> burnLitKeys, burnLitVals, burnAccKeys, burnAccVals;
		private readonly List<int> fireScratch = new List<int>();

		public int BurningCount => burnLit.Count;

		public bool IsBurning(IntVec3 c) => c.InBounds(map) && burnLit.ContainsKey(map.cellIndices.CellToIndex(c));

		private static bool FuelBurns => RM_SheetSettings.fuelSpillsBurnEnabled && RimMandrakeFlowWorksSettings.canalFireEnabled;

		/// <summary>The Fire.SpawnSetup hook: a fire on or beside a burnable spill lights it.</summary>
		public static void NotifyFireAt(Map map, IntVec3 at)
		{
			RM_MapComponent_Sheet s = Of(map);
			if (s == null || s.state == null || s.state.WetCount == 0 || !FuelBurns)
			{
				return;
			}
			s.TryLight(at);
			for (int d = 0; d < 8; d++)
			{
				s.TryLight(at + GenAdj.AdjacentCells[d]);
			}
		}

		/// <summary>Light the burnable spill on <paramref name="c"/> now. False: nothing burnable there, already alight, or the
		/// fuel-fire switch is off.</summary>
		public bool TryLight(IntVec3 c)
		{
			if (!FuelBurns || state == null || !c.InBounds(map))
			{
				return false;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (state.Dl[i] <= 0 || burnLit.ContainsKey(i) || !Burnable(FluidOf(state.Fluid[i])))
			{
				return false;
			}
			burnLit[i] = Find.TickManager.TicksGame;
			burnAcc[i] = 0;
			EnsureSheetFlame(c, FluidOf(state.Fluid[i]));
			return true;
		}

		private void PutOut(int i)
		{
			burnLit.Remove(i);
			burnAcc.Remove(i);
			IntVec3 c = map.cellIndices.IndexToCell(i);
			DestroySheetFlame(c, RimMandrakeFlowWorks_DefOf.RM_LiquidFlame);
			DestroySheetFlame(c, RimMandrakeFlowWorks_DefOf.RM_LiquidFlame_Inferno);
			map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Terrain);
		}

		private void EnsureSheetFlame(IntVec3 c, FluidDef f)
		{
			ThingDef big = RimMandrakeFlowWorks_DefOf.RM_LiquidFlame_Inferno;
			ThingDef def = RM_LiquidFire.BurnOf(f) == RM_FuelBurn.Inferno && big != null ? big : RimMandrakeFlowWorks_DefOf.RM_LiquidFlame;
			if (def == null || map.thingGrid.ThingAt(c, def) != null)
			{
				return;
			}
			GenSpawn.Spawn(def, c, map);
		}

		private void DestroySheetFlame(IntVec3 c, ThingDef def)
		{
			Thing flame = def != null ? map.thingGrid.ThingAt(c, def) : null;
			if (flame != null && flame.Spawned)
			{
				flame.Destroy();
			}
		}

		private void FireTick()
		{
			if (burnLit.Count == 0 || !map.IsHashIntervalTick(FireCheckTicks))
			{
				return;
			}
			fireScratch.Clear();
			fireScratch.AddRange(burnLit.Keys);
			if (!FuelBurns || state == null)
			{
				foreach (int i in fireScratch)
				{
					PutOut(i);
				}
				return;
			}
			fireScratch.Sort();
			int now = Find.TickManager.TicksGame;
			int blasts = 0;
			RM_MapComponent_Excavation e = Engine;
			int U = RM_LevelSolve.U;
			foreach (int i in fireScratch)
			{
				if (!burnLit.TryGetValue(i, out int lit))
				{
					continue;
				}
				FluidDef f = FluidOf(state.Fluid[i]);
				IntVec3 c = map.cellIndices.IndexToCell(i);
				if (state.Dl[i] <= 0 || !Burnable(f))
				{
					PutOut(i);
					continue;
				}
				RM_FuelBurn kind = RM_LiquidFire.BurnOf(f);
				// the front: burnable neighbours light fireFrontTicksPerCell after this square did
				float speed = kind == RM_FuelBurn.Inferno
					? RM_FuelFireMath.InfernoFrontSpeed(RimMandrakeFlowWorksSettings.fireFrontSpeedMultiplier, RimMandrakeFlowWorksSettings.chemfuelSpreadSpeed)
					: RimMandrakeFlowWorksSettings.fireFrontSpeedMultiplier;
				if (RM_SheetFluidMath.FrontReaches(lit, now, f.fireFrontTicksPerCell, speed))
				{
					for (int d = 0; d < 4; d++)
					{
						IntVec3 n = c + GenAdj.CardinalDirections[d];
						if (!n.InBounds(map))
						{
							continue;
						}
						if (!TryLight(n) && e != null && e.IsExcavated(n) && Burnable(e.FluidAt(n)) && !e.LiquidFire.IsBurning(map, n))
						{
							e.LiquidFire.OfferLight(map, e, n);   // queued, never a forced extra channel-fire Tick
						}
					}
				}
				// the burn
				int dl;
				if (kind == RM_FuelBurn.Detonation)
				{
					// GPT deep review 2026-10-22 #3: past the per-check blast cap the puddle is NOT consumed (it used to burn away
					// with no explosion); it stays lit and blows on a later check
					dl = 0;
					if (blasts < MaxBlastsPerCheck)
					{
						blasts++;
						dl = state.Dl[i];
						GenExplosion.DoExplosion(c, map, BlastRadius, DamageDefOf.Flame, null);
					}
				}
				else
				{
					// a spill burns down at its fuel's real pool-fire rate when the FluidDef gives one (fuel_spill_research.md);
					// the channel's rate otherwise
					int tpn = f.sheetBurnMmPerMinute > 0f
						? RM_SheetFluidMath.SheetBurnTicksPerNotch(f.sheetBurnMmPerMinute, RM_Volume.CentimetresPerNotch, GenDate.TicksPerHour,
							kind == RM_FuelBurn.Inferno ? RimMandrakeFlowWorksSettings.chemfuelBurnRate : 1f)
						: kind == RM_FuelBurn.Inferno
						? RM_FuelFireMath.InfernoTicksPerLevelAt(RimMandrakeFlowWorksSettings.chemfuelBurnRate)
						: RM_FireMath.TicksPerCanalLevel(RimMandrakeFlowWorksSettings.burnDaysPerNotch);
					burnAcc.TryGetValue(i, out int acc);
					dl = RM_SheetFluidMath.BurnDue(ref acc, FireCheckTicks, tpn, U);
					burnAcc[i] = acc;
				}
				if (dl > 0)
				{
					RM_SheetMath.Burn(state, i, dl);
				}
				if (state.Dl[i] <= 0)
				{
					PutOut(i);
					continue;
				}
				// effects
				GenTemperature.PushHeat(c, map, kind == RM_FuelBurn.Inferno ? RM_FuelFireMath.InfernoHeatPerCheck(RimMandrakeFlowWorksSettings.chemfuelIntensity) : 5f);
				List<Thing> here = map.thingGrid.ThingsListAt(c);
				for (int t = here.Count - 1; t >= 0; t--)
				{
					if (here[t] is Pawn p && !p.Dead && !p.Flying && Rand.Chance(kind == RM_FuelBurn.Inferno ? 0.6f : 0.3f))
					{
						p.TryAttachFire(0.4f, null);
					}
				}
				if (Rand.Chance(0.15f))
				{
					IntVec3 n = c + GenAdj.AdjacentCellsAndInside[Rand.Range(0, 9)];
					if (n.InBounds(map))
					{
						FireUtility.TryStartFireIn(n, map, 0.3f, null);
					}
				}
			}
		}

		private void ExposeFire()
		{
			Scribe_Collections.Look(ref burnLit, "RM_sheetBurnLit", LookMode.Value, LookMode.Value, ref burnLitKeys, ref burnLitVals);
			Scribe_Collections.Look(ref burnAcc, "RM_sheetBurnAcc", LookMode.Value, LookMode.Value, ref burnAccKeys, ref burnAccVals);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (burnLit == null)
				{
					burnLit = new Dictionary<int, int>();
				}
				if (burnAcc == null)
				{
					burnAcc = new Dictionary<int, int>();
				}
			}
		}
	}
}
