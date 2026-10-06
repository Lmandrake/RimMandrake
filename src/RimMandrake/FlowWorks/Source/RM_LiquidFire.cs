using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_BUILD_PROGRAM_1 Phase 6 — FIRE on the depth/fill primitive (mod definition §12, rulings 7 and 22).
	///
	/// The excavation component owns ignition state, burn duration and the travelling front; vanilla Fire is
	/// only the trigger. A burning cell carries one non-ticking <c>RM_LiquidFlame</c> purely for the look, so a
	/// 200-cell moat alight is one bounded walk here, never 200 ticking Things (§12's "option to avoid").
	///
	/// - IGNITION: any vanilla Fire spawning on or next to a burnable liquid cell (a torch, a burning raider
	///   walking in, a molotov) lights it — the Fire.SpawnSetup hook below. Liquid terrain itself keeps
	///   Flammability ~0 (the propane hard ban: no ignition without a thermal trigger), so nothing self-lights.
	/// - FRONT: one travelling front for every burnable liquid. FluidDef.fireKind says CreepingFuse or Detonation
	///   and fireFrontTicksPerCell is the speed; a player can outrun a fuse. The front runs back along the liquid
	///   into the source body ("they will also light their source"), bounded by sourceFireReach cells.
	/// - BURN: ruling 7, a rate on the tier ladder: one canal fill level per day; a source cell costs its body one
	///   level per five days, so a limitless source burns forever and a moat piped from a larger body burns as
	///   long as inflow beats the burn. Burned liquid is GONE (the second disclosed exit, beside overflow):
	///   counted in <see cref="BurnedLevelsTotal"/>, debited outside the pulse's conservation ledger.
	/// - EFFECT: pawns in the burning cell catch fire; one held in a D=4 pit always does (ruling 22).
	/// - SPENT: a canal cell that burns dry is left scorched (ash) — the `canal_spent_after_burn` bar.
	/// - EXPLOSIONS: a flame or bomb blast lights burnable liquid in every cell it touches, Fire or no Fire
	///   (DamageWorker.ExplosionAffectCell postfix). A firefoam blast (Extinguish) smothers instead.
	/// - PUTTING IT OUT: firefoam on a burning cell smothers it, and while the foam lies there the cell cannot
	///   relight. Rain on an unroofed burning cell has a chance each check to douse it (oil and tar float, so
	///   rain is slow, never instant; a neighbour still alight can relight it). Neither marks the cell spent.
	/// NOT built (owed): bespoke burning-liquid and scorched-channel art (the flame is vanilla's fire graphic,
	/// the scorch is vanilla ash).
	/// </summary>
	public class RM_LiquidFire : IExposable
	{
		private const int CheckInterval = 30;
		private const int EffectEvery = 2;          // effects every 2nd check = 60 ticks
		private const int MaxDetonationsPerCheck = 8;

		private Dictionary<int, int> burning = new Dictionary<int, int>();   // cell index -> burn accumulator
		private Dictionary<int, int> hopsOf = new Dictionary<int, int>();    // cell index -> source hops
		private List<int> pendCell = new List<int>();
		private List<int> pendDue = new List<int>();
		private List<int> pendHops = new List<int>();
		private float burnedLevelsTotal;
		private int nextCheckTick = -1;
		private int checkCount;

		private List<int> burningKeys;
		private List<int> burningValues;
		private List<int> hopsKeys;
		private List<int> hopsValues;
		private readonly List<int> scratch = new List<int>();
		private readonly HashSet<int> pendingSet = new HashSet<int>();

		public int BurningCount => burning.Count;
		public int PendingCount => pendCell.Count;
		public float BurnedLevelsTotal => burnedLevelsTotal;
		public bool IsBurning(Map map, IntVec3 c) => c.InBounds(map) && burning.ContainsKey(map.cellIndices.CellToIndex(c));

		public void ExposeData()
		{
			Scribe_Collections.Look(ref burning, "burning", LookMode.Value, LookMode.Value, ref burningKeys, ref burningValues);
			Scribe_Collections.Look(ref hopsOf, "hops", LookMode.Value, LookMode.Value, ref hopsKeys, ref hopsValues);
			Scribe_Collections.Look(ref pendCell, "pendCell", LookMode.Value);
			Scribe_Collections.Look(ref pendDue, "pendDue", LookMode.Value);
			Scribe_Collections.Look(ref pendHops, "pendHops", LookMode.Value);
			Scribe_Values.Look(ref burnedLevelsTotal, "burnedLevelsTotal", 0f);
			Scribe_Values.Look(ref nextCheckTick, "nextCheckTick", -1);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (burning == null) burning = new Dictionary<int, int>();
				if (hopsOf == null) hopsOf = new Dictionary<int, int>();
				if (pendCell == null || pendDue == null || pendHops == null
					|| pendCell.Count != pendDue.Count || pendCell.Count != pendHops.Count)
				{
					pendCell = new List<int>(); pendDue = new List<int>(); pendHops = new List<int>();
				}
				pendingSet.Clear();
				foreach (int i in pendCell) pendingSet.Add(i);
			}
		}

		// ── what can burn ─────────────────────────────────────────────────

		/// <summary>The burnable fluid standing on a cell, or null: an excavated cell's own fluid while F &gt; 0,
		/// a natural source's body fluid.</summary>
		public static FluidDef BurnableFluidAt(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return null;
			}
			FluidDef f = null;
			if (ex.IsExcavated(c))
			{
				if (ex.FillAt(c) > 0)
				{
					f = ex.FluidAt(c) ?? ex.ActiveFluid;
				}
			}
			else if (ex.IsSourceCell(c))
			{
				f = ex.Stock.BodyAt(map, c, ex)?.fluid;
			}
			return f != null && f.fireKind != RM_FluidFireKind.None ? f : null;
		}

		// ── ignition ──────────────────────────────────────────────────────

		/// <summary>A vanilla Fire appeared at <paramref name="at"/>: light any burnable liquid on it or around it.</summary>
		public void NotifyFireAt(Map map, RM_MapComponent_Excavation ex, IntVec3 at)
		{
			if (!RimMandrakeFlowWorksSettings.canalFireEnabled)
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(new TargetInfo(at, map)))
			{
				TryQueue(map, ex, c, now, 0);
			}
			TryQueue(map, ex, at, now, 0);
		}

		/// <summary>Light one cell now (debug / bridge). Returns false when nothing burnable stands there.</summary>
		public bool IgniteNow(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			if (!RimMandrakeFlowWorksSettings.canalFireEnabled || BurnableFluidAt(map, ex, c) == null)
			{
				return false;
			}
			TryQueue(map, ex, c, Find.TickManager.TicksGame, 0);
			nextCheckTick = -1;
			Tick(map, ex);
			return true;
		}

		private void TryQueue(Map map, RM_MapComponent_Excavation ex, IntVec3 c, int due, int hops)
		{
			if (!c.InBounds(map))
			{
				return;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (burning.ContainsKey(i) || pendingSet.Contains(i) || BurnableFluidAt(map, ex, c) == null
				|| IsSmothered(map, c))
			{
				return;
			}
			pendCell.Add(i); pendDue.Add(due); pendHops.Add(hops);
			pendingSet.Add(i);
		}

		// ── the per-tick-interval walk ────────────────────────────────────

		public void Tick(Map map, RM_MapComponent_Excavation ex)
		{
			int now = Find.TickManager.TicksGame;
			if (now < nextCheckTick)
			{
				return;
			}
			nextCheckTick = now + CheckInterval;
			if (burning.Count == 0 && pendCell.Count == 0)
			{
				return;
			}
			if (!RimMandrakeFlowWorksSettings.canalFireEnabled)
			{
				ExtinguishAll(map);
				return;
			}
			AdvanceFront(map, ex, now);
			checkCount++;
			Maintain(map, ex, checkCount % EffectEvery == 0);
		}

		/// <summary>Light every queued cell whose time has come; each lit cell queues its wet neighbours at
		/// due + one step. Chained in one pass, so a detonation (a step of a few ticks) crosses many cells per
		/// check while a fuse crosses at most one.</summary>
		private void AdvanceFront(Map map, RM_MapComponent_Excavation ex, int now)
		{
			int detonations = 0;
			int guard = 0;
			bool progressed = true;
			while (progressed && guard++ < 10000)
			{
				progressed = false;
				for (int k = 0; k < pendCell.Count; k++)
				{
					if (pendDue[k] > now)
					{
						continue;
					}
					int i = pendCell[k], due = pendDue[k], hops = pendHops[k];
					pendCell.RemoveAt(k); pendDue.RemoveAt(k); pendHops.RemoveAt(k);
					pendingSet.Remove(i);
					k--;
					IntVec3 c = map.cellIndices.IndexToCell(i);
					FluidDef fluid = BurnableFluidAt(map, ex, c);
					if (fluid == null || burning.ContainsKey(i))
					{
						continue;
					}
					Ignite(map, c, i, hops);
					progressed = true;
					if (fluid.fireKind == RM_FluidFireKind.Detonation && detonations < MaxDetonationsPerCheck
						&& ((c.x + c.z) % 3 == 0))
					{
						// PROVISIONAL: one blast per ~3 cells of front, capped per check, driven from here (Phase 6:
						// "drive them centrally; do not spawn a Thing per cell").
						detonations++;
						GenExplosion.DoExplosion(c, map, 1.9f, DamageDefOf.Flame, null);
					}
					bool cIsSource = ex.IsSourceCell(c);
					for (int d = 0; d < 4; d++)
					{
						IntVec3 n = c + GenAdj.CardinalDirections[d];
						if (!n.InBounds(map))
						{
							continue;
						}
						int nh = RM_FireMath.SourceHopsFor(cIsSource, hops, ex.IsSourceCell(n));
						if (!RM_FireMath.SourceHopAllowed(nh, RimMandrakeFlowWorksSettings.SourceFireReach))
						{
							continue;
						}
						FluidDef nf = BurnableFluidAt(map, ex, n);
						if (nf == null)
						{
							continue;
						}
						TryQueue(map, ex, n, RM_FireMath.FrontDue(due, nf.fireFrontTicksPerCell,
							RimMandrakeFlowWorksSettings.fireFrontSpeedMultiplier), nh);
					}
				}
			}
		}

		private void Ignite(Map map, IntVec3 c, int i, int hops)
		{
			burning[i] = 0;
			hopsOf[i] = hops;
			EnsureFlame(map, c);
		}

		/// <summary>Drop cells that no longer hold burnable liquid, keep each flame drawn, re-offer neighbours that
		/// became wet since (a channel refilled beside a fire catches), and apply heat and harm.</summary>
		private void Maintain(Map map, RM_MapComponent_Excavation ex, bool effects)
		{
			scratch.Clear();
			scratch.AddRange(burning.Keys);
			int now = Find.TickManager.TicksGame;
			for (int k = 0; k < scratch.Count; k++)
			{
				int i = scratch[k];
				IntVec3 c = map.cellIndices.IndexToCell(i);
				FluidDef fluid = BurnableFluidAt(map, ex, c);
				// Foam lying on a burning cell puts it out (and TryQueue keeps it out while the foam lies); rain on an
				// open cell has its chance once per effects check (60 ticks). Both were written and never called
				// until 2026-10-05: foam only stopped a NEW light, and RainDouses had no caller at all.
				if (fluid == null || IsSmothered(map, c) || (effects && RainDouses(map, c)))
				{
					Extinguish(map, c, i, false);
					continue;
				}
				EnsureFlame(map, c);
				int hops = hopsOf.TryGetValue(i, out int h) ? h : 0;
				bool cIsSource = ex.IsSourceCell(c);
				for (int d = 0; d < 4; d++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[d];
					if (!n.InBounds(map))
					{
						continue;
					}
					int nh = RM_FireMath.SourceHopsFor(cIsSource, hops, ex.IsSourceCell(n));
					if (!RM_FireMath.SourceHopAllowed(nh, RimMandrakeFlowWorksSettings.SourceFireReach))
					{
						continue;
					}
					FluidDef nf = BurnableFluidAt(map, ex, n);
					if (nf != null)
					{
						TryQueue(map, ex, n, RM_FireMath.FrontDue(now, nf.fireFrontTicksPerCell,
							RimMandrakeFlowWorksSettings.fireFrontSpeedMultiplier), nh);
					}
				}
				if (effects)
				{
					ApplyEffects(map, ex, c);
				}
			}
		}

		private void ApplyEffects(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			// PROVISIONAL heat: about what a vanilla full-size fire pushes over the same time.
			GenTemperature.PushHeat(c, map, 60f);
			bool heldInPit = ex.IsSuperdeepExcavation(c);
			List<Thing> things = map.thingGrid.ThingsListAt(c);
			for (int t = things.Count - 1; t >= 0; t--)
			{
				if (things[t] is Pawn p && !p.Dead && Rand.Chance(RM_FireMath.AttachChance(heldInPit)))
				{
					p.TryAttachFire(heldInPit ? 1f : 0.4f, null);
				}
			}
		}

		/// <summary>Ruling 7, run once per flow pulse BEFORE the components resolve (so the burn never reads as a
		/// ledger leak): canal cells lose a level per day; source cells debit their body a level per five days.</summary>
		public void BurnPulse(Map map, RM_MapComponent_Excavation ex, int pulseTicks)
		{
			if (burning.Count == 0 || !RimMandrakeFlowWorksSettings.canalFireEnabled)
			{
				return;
			}
			int canalTicks = RM_FireMath.TicksPerCanalLevel(RimMandrakeFlowWorksSettings.canalBurnDaysPerLevel);
			int sourceTicks = RM_FireMath.TicksPerSourceLevel(RimMandrakeFlowWorksSettings.sourceBurnDaysPerLevel);
			scratch.Clear();
			scratch.AddRange(burning.Keys);
			for (int k = 0; k < scratch.Count; k++)
			{
				int i = scratch[k];
				IntVec3 c = map.cellIndices.IndexToCell(i);
				int acc = burning[i];
				if (ex.IsExcavated(c))
				{
					int levels = RM_FireMath.LevelsDue(ref acc, pulseTicks, canalTicks);
					burning[i] = acc;
					for (int l = 0; l < levels; l++)
					{
						if (ex.BurnOffLevel(c))
						{
							burnedLevelsTotal += 1f;
						}
						if (ex.FillAt(c) == 0)
						{
							Extinguish(map, c, i, true);
							break;
						}
					}
				}
				else
				{
					int levels = RM_FireMath.LevelsDue(ref acc, pulseTicks, sourceTicks);
					burning[i] = acc;
					RM_LiquidBody body = ex.Stock.BodyAt(map, c, ex);
					float unit = body?.fluid != null ? body.fluid.volumePerTile : 1f;
					for (int l = 0; l < levels; l++)
					{
						if (!ex.Stock.TryDebit(map, c, unit, ex))
						{
							Extinguish(map, c, i, false);
							break;
						}
						if (body != null && !body.limitless)
						{
							burnedLevelsTotal += 1f;
						}
					}
				}
			}
		}

		// ── putting it out ────────────────────────────────────────────────

		/// <summary>Firefoam lying on the cell: the fire is out and stays out while the foam is there.</summary>
		public static bool IsSmothered(Map map, IntVec3 c)
		{
			return RimMandrakeFlowWorksSettings.foamSmothersLiquidFireEnabled && ThingDefOf.Filth_FireFoam != null
				&& c.InBounds(map) && c.GetFirstThing(map, ThingDefOf.Filth_FireFoam) != null;
		}

		/// <summary>Rain on an open cell: a chance per effects check (every 60 ticks) scaled by the rain rate.
		/// PROVISIONAL 0.03 at full rain ≈ a heavy downpour douses a cell in about half an hour.</summary>
		private static bool RainDouses(Map map, IntVec3 c)
		{
			if (!RimMandrakeFlowWorksSettings.rainDousesLiquidFireEnabled || map.roofGrid.Roofed(c))
			{
				return false;
			}
			float rain = map.weatherManager.RainRate;
			return rain > 0.01f && Rand.Chance(RM_FireMath.RainDouseChance(rain));
		}

		/// <summary>An explosion touched <paramref name="c"/>: smother (firefoam) or light (flame, bomb).</summary>
		public void NotifyExplosionAt(Map map, RM_MapComponent_Excavation ex, IntVec3 c, DamageDef dam)
		{
			if (dam == null || !c.InBounds(map))
			{
				return;
			}
			if (dam == DamageDefOf.Extinguish)
			{
				int i = map.cellIndices.CellToIndex(c);
				if (burning.ContainsKey(i))
				{
					Extinguish(map, c, i, false);
				}
				return;
			}
			if (!RimMandrakeFlowWorksSettings.canalFireEnabled || !RimMandrakeFlowWorksSettings.explosionIgnitesLiquidEnabled
				|| !RM_FireMath.ExplosionIgnites(dam.defName))
			{
				return;
			}
			TryQueue(map, ex, c, Find.TickManager.TicksGame, 0);
		}

		// ── flames ────────────────────────────────────────────────────────

		private static void EnsureFlame(Map map, IntVec3 c)
		{
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LiquidFlame;
			if (def == null || map.thingGrid.ThingAt(c, def) != null)
			{
				return;
			}
			GenSpawn.Spawn(def, c, map);
		}

		private void Extinguish(Map map, IntVec3 c, int i, bool spent)
		{
			burning.Remove(i);
			hopsOf.Remove(i);
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LiquidFlame;
			Thing flame = def != null ? map.thingGrid.ThingAt(c, def) : null;
			if (flame != null && flame.Spawned)
			{
				flame.Destroy();
			}
			if (spent)
			{
				// The canal_spent_after_burn bar: a channel that burned dry reads scorched, not merely dry.
				FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_Ash, 2);
			}
		}

		public void ExtinguishAll(Map map)
		{
			scratch.Clear();
			scratch.AddRange(burning.Keys);
			foreach (int i in scratch)
			{
				Extinguish(map, map.cellIndices.IndexToCell(i), i, false);
			}
			pendCell.Clear(); pendDue.Clear(); pendHops.Clear(); pendingSet.Clear();
		}

		public string Report()
		{
			return "FIRE burning " + burning.Count + " | front pending " + pendCell.Count
				+ " | burned levels " + burnedLevelsTotal.ToString("F0");
		}
	}

	/// <summary>The trigger: any vanilla Fire that spawns (not a reload) offers its cell and neighbours.</summary>
	[HarmonyPatch(typeof(Fire), nameof(Fire.SpawnSetup))]
	public static class RM_Patch_FireLightsLiquid
	{
		public static void Postfix(Fire __instance, Map map, bool respawningAfterLoad)
		{
			if (respawningAfterLoad || map == null || !RimMandrakeFlowWorksSettings.canalFireEnabled)
			{
				return;
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			ex?.LiquidFire.NotifyFireAt(map, ex, __instance.Position);
		}
	}

	/// <summary>Explosions: flame/bomb blasts light liquid in every cell they touch; firefoam smothers.</summary>
	[HarmonyPatch(typeof(DamageWorker), nameof(DamageWorker.ExplosionAffectCell))]
	public static class RM_Patch_ExplosionLightsLiquid
	{
		public static void Postfix(Explosion explosion, IntVec3 c)
		{
			Map map = explosion?.Map;
			if (map == null)
			{
				return;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (ex == null || (ex.LiquidFire.BurningCount == 0 && explosion.damType == DamageDefOf.Extinguish))
			{
				return;
			}
			ex.LiquidFire.NotifyExplosionAt(map, ex, c, explosion.damType);
		}
	}

	/// <summary>static_call surface for the bridge (one string param): "x,z" lights that cell; "" reports.</summary>
	public static class RM_LiquidFireProof
	{
		public static string ProofIgnite(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null) return "REFUSED: no excavation component on the current map";
			string[] p = (arg ?? "").Split(',');
			if (p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
				return "REFUSED: arg must be x,z";
			IntVec3 c = new IntVec3(x, 0, z);
			if (!ex.LiquidFire.IgniteNow(map, ex, c))
				return "REFUSED: fire off or nothing burnable at " + c + " (fluid " + (ex.FluidAt(c)?.defName ?? "none") + ", F=" + ex.FillAt(c) + ")";
			return "LIT " + c + " | " + ex.LiquidFire.Report();
		}

		public static string ProofReport(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			return ex == null ? "REFUSED: no excavation component on the current map" : ex.LiquidFire.Report();
		}
	}
}
