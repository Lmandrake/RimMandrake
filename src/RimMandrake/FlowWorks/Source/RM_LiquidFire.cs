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
	///   into the source body ("they will also light their source"), bounded by sourceFireReach cells. A front
	///   detonation's own Flame blast inherits the front's reach, but a vanilla Fire that blast starts on land lights
	///   the source cells beside it through the ignition hook at 0 hops, so a blast near a shore can restart the
	///   reach there once per blast.
	/// - BURN: ruling 7, a rate: one notch (0.5 m) a day for every burning square, canal or pond alike (unified depth
	///   spec §5.6, D3; LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD), taken in decilitres so a thin sheet burns away in a fraction of
	///   a day (a DETONATING liquid's canal cell is instead consumed whole on the first pulse after it lights, ruling 13).
	///   A pond still outlasts a canal (the squares not burning share their water), a limitless source burns forever,
	///   and a moat piped from a larger body burns as long as inflow beats the burn. Burned liquid is GONE (the second disclosed exit, beside overflow):
	///   counted in <see cref="BurnedLevelsTotal"/>, debited outside the pulse's conservation ledger.
	/// - EFFECT: pawns in the burning cell catch fire; one held in a D=4 pit always does (ruling 22).
	/// - SPENT: a canal cell that burns dry is left scorched (ash) — the `canal_spent_after_burn` bar.
	/// - EXPLOSIONS: a flame or bomb blast lights burnable liquid in every cell it touches, Fire or no Fire
	///   (DamageWorker.ExplosionAffectCell postfix). A firefoam blast (Extinguish) smothers instead.
	/// - PUTTING IT OUT: a firefoam blast (popper, Extinguish damage) puts a burning cell out; foam lying on a cell
	///   would also keep it from relighting, but fill terrains are water-tagged and take no filth, so in practice
	///   it is the blast that acts. Rain on an unroofed burning cell has a chance each check to douse it (oil and tar float, so
	///   rain is slow, never instant; a neighbour still alight can relight it). Neither marks the cell spent.
	/// - FUEL FIRES (CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL, owner by card 2026-10-15; numbers in RM_FuelFireMath):
	///   chemfuel is an INFERNO — the front runs a cell every couple of ticks, the flame is drawn large, each lit cell pushes
	///   eight times the heat, sets fire to burnable things within ~3 cells, and the channel burns down a level every 5 s.
	///   Astrofuel DETONATES — lighting any cell walks the whole connected astrofuel body and schedules it: every cell
	///   emptied ring by ring (1 tick a ring), vanilla Bomb blasts at anchors ~3 cells apart, a heat wave, then a stagger
	///   and a throw for whoever stood in a blast. Per-tick budgets (cells emptied, blasts started) keep a huge body from
	///   freezing a tick; the schedule is saved. Both raise <see cref="RM_FuelFireEvents"/> for other layers (Utinni).
	/// NOT built (owed): bespoke burning-liquid and scorched-channel art (the flame is vanilla's fire graphic,
	/// the scorch is vanilla ash).
	/// </summary>
	public class RM_LiquidFire : IExposable
	{
		private const int CheckInterval = RM_FireMath.FireCheckIntervalTicks;
		private const int EffectEvery = 2;          // effects every 2nd check = 60 ticks
		private const int MaxDetonationsPerCheck = 8;

		private Dictionary<int, int> burning = new Dictionary<int, int>();   // cell index -> burn accumulator
		private Dictionary<int, int> hopsOf = new Dictionary<int, int>();    // cell index -> source hops
		// The burn accumulator of a cell that went out UNSPENT because its level flowed away (fluid gone, not burned):
		// the level that moved carries it into the cell it lands in. Without this a lone burning level hopping between
		// equal cells of a sourceless channel restarted its clock on every hop and never burned out (live 2026-10-05:
		// a 6-cell tar run held 3 cells alight at 7,000 ticks with the burn cut to 1,200 ticks a level). Saved since
		// LIQUID_FIRE_MEND_COVER_AND_SAVE (C4-F1), so a load does not restart a moving level's clock.
		// LIQUID_FIRE_QUEUE_ORIGIN_1: a carried accumulator now remembers WHEN it was left and WHICH liquid, so a
		// later, unrelated ignition near the spot (or of another liquid) does not inherit stale burn progress.
		// LIQUID_FIRE_MEND_COVER_AND_SAVE (C4-F1): the carried progress and each burning cell's fluid are saved, so a load
		// neither restarts a moving level's clock nor lets a null fluid match any liquid.
		private Dictionary<int, int> carriedAcc = new Dictionary<int, int>();
		private Dictionary<int, int> carriedTick = new Dictionary<int, int>();
		private Dictionary<int, FluidDef> carriedFluid = new Dictionary<int, FluidDef>();
		private Dictionary<int, FluidDef> burningFluid = new Dictionary<int, FluidDef>();
		private List<int> carriedAccKeys, carriedAccValues, carriedTickKeys, carriedTickValues, carriedFluidKeys, burningFluidKeys;
		private List<FluidDef> carriedFluidValues, burningFluidValues;
		// PROVISIONAL (auto-decided 2026-10-09, LIQUID_FIRE_QUEUE_ORIGIN_1): carried burn progress expires after 600 ticks.
		private const int CarriedExpiryTicks = 600;
		// LIQUID_FIRE_QUEUE_ORIGIN_1: the front's own detonations: the source hops the lighting cell had, so the async
		// Explosion's cells inherit the front's reach instead of restarting at 0. C4-F9: keyed by the Explosion's thing id
		// (an unrelated later blast at the same centre is a direct ignition, not the front's).
		private readonly Dictionary<int, int> blastHops = new Dictionary<int, int>();
		private readonly Dictionary<int, bool> blastFromSource = new Dictionary<int, bool>();
		private readonly Dictionary<int, int> blastTick = new Dictionary<int, int>();
		private const int BlastMemoryTicks = 300;
		// LIQUID_FIRE_QUEUE_ORIGIN_1: the pending front is keyed by cell, so an earlier offer for an already-pending
		// cell (a direct flame beside a slow fuse) advances it in O(1). Saved as the three legacy lists.
		private Dictionary<int, int> pendDueOf = new Dictionary<int, int>();
		private Dictionary<int, int> pendHopsOf = new Dictionary<int, int>();
		private List<int> pendCell = new List<int>();
		private List<int> pendDue = new List<int>();
		private List<int> pendHops = new List<int>();
		private float burnedLevelsTotal;
		private int nextCheckTick = -1;
		// CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL: the astrofuel detonation schedule, sorted by tick. Kind 0 empties a cell, 1 starts a
		// blast (radius in detRadius), 2 throws and staggers pawns around a blast that has landed. detonating = cells planned
		// and not yet emptied (TryQueue skips them, so a blast of the same body never re-plans it).
		private List<int> detTick = new List<int>();
		private List<int> detCell = new List<int>();
		private List<int> detKind = new List<int>();
		private List<float> detRadius = new List<float>();
		private readonly HashSet<int> detonating = new HashSet<int>();
		private int detonationsStarted;
		private float detonatedCells;
		private bool largeInfernoAnnounced;
		private int checkCount;

		private List<int> burningKeys;
		private List<int> burningValues;
		private List<int> hopsKeys;
		private List<int> hopsValues;
		private readonly List<int> scratch = new List<int>();
		private readonly List<int> dueScratch = new List<int>();

		public int BurningCount => burning.Count;
		public int DetonationPendingCount => detTick.Count;
		public int DetonationsStarted => detonationsStarted;
		public float DetonatedCells => detonatedCells;

		/// <summary>How a burnable fluid burns under today's settings (RM_FuelFireMath.Classify).</summary>
		public static RM_FuelBurn BurnOf(FluidDef f)
		{
			if (f == null)
			{
				return RM_FuelBurn.Ordinary;
			}
			return RM_FuelFireMath.Classify(f.fireKind == RM_FluidFireKind.Inferno, f.fireKind == RM_FluidFireKind.Detonation,
				RimMandrakeFlowWorksSettings.chemfuelInfernoEnabled, RimMandrakeFlowWorksSettings.astrofuelDetonationEnabled);
		}

		/// <summary>The front's speed multiplier into a cell of <paramref name="f"/>: an inferno also takes the chemfuel spread dial.</summary>
		private static float FrontSpeedFor(FluidDef f)
		{
			return BurnOf(f) == RM_FuelBurn.Inferno
				? RM_FuelFireMath.InfernoFrontSpeed(RimMandrakeFlowWorksSettings.fireFrontSpeedMultiplier, RimMandrakeFlowWorksSettings.chemfuelSpreadSpeed)
				: RimMandrakeFlowWorksSettings.fireFrontSpeedMultiplier;
		}
		public int PendingCount => pendDueOf.Count;
		public float BurnedLevelsTotal => burnedLevelsTotal;
		public bool IsBurning(Map map, IntVec3 c) => c.InBounds(map) && burning.ContainsKey(map.cellIndices.CellToIndex(c));

		public void ExposeData()
		{
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				pendCell.Clear(); pendDue.Clear(); pendHops.Clear();
				foreach (KeyValuePair<int, int> kv in pendDueOf)
				{
					pendCell.Add(kv.Key); pendDue.Add(kv.Value); pendHops.Add(pendHopsOf.TryGetValue(kv.Key, out int hh) ? hh : 0);
				}
			}
			Scribe_Collections.Look(ref burning, "burning", LookMode.Value, LookMode.Value, ref burningKeys, ref burningValues);
			Scribe_Collections.Look(ref hopsOf, "hops", LookMode.Value, LookMode.Value, ref hopsKeys, ref hopsValues);
			Scribe_Collections.Look(ref pendCell, "pendCell", LookMode.Value);
			Scribe_Collections.Look(ref pendDue, "pendDue", LookMode.Value);
			Scribe_Collections.Look(ref pendHops, "pendHops", LookMode.Value);
			Scribe_Values.Look(ref burnedLevelsTotal, "burnedLevelsTotal", 0f);
			Scribe_Values.Look(ref nextCheckTick, "nextCheckTick", -1);
			Scribe_Collections.Look(ref carriedAcc, "carriedAcc", LookMode.Value, LookMode.Value, ref carriedAccKeys, ref carriedAccValues);
			Scribe_Collections.Look(ref carriedTick, "carriedTick", LookMode.Value, LookMode.Value, ref carriedTickKeys, ref carriedTickValues);
			Scribe_Collections.Look(ref carriedFluid, "carriedFluid", LookMode.Value, LookMode.Def, ref carriedFluidKeys, ref carriedFluidValues);
			Scribe_Collections.Look(ref burningFluid, "burningFluid", LookMode.Value, LookMode.Def, ref burningFluidKeys, ref burningFluidValues);
			Scribe_Collections.Look(ref detTick, "detTick", LookMode.Value);
			Scribe_Collections.Look(ref detCell, "detCell", LookMode.Value);
			Scribe_Collections.Look(ref detKind, "detKind", LookMode.Value);
			Scribe_Collections.Look(ref detRadius, "detRadius", LookMode.Value);
			Scribe_Values.Look(ref detonationsStarted, "detonationsStarted", 0);
			Scribe_Values.Look(ref detonatedCells, "detonatedCells", 0f);
			Scribe_Values.Look(ref largeInfernoAnnounced, "largeInfernoAnnounced", false);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (detTick == null || detCell == null || detKind == null || detRadius == null || detTick.Count != detCell.Count
					|| detTick.Count != detKind.Count || detTick.Count != detRadius.Count)
				{
					detTick = new List<int>(); detCell = new List<int>(); detKind = new List<int>(); detRadius = new List<float>();
				}
				detonating.Clear();
				for (int k = 0; k < detCell.Count; k++)
				{
					if (detKind[k] == 0) detonating.Add(detCell[k]);
				}
				if (burning == null) burning = new Dictionary<int, int>();
				if (hopsOf == null) hopsOf = new Dictionary<int, int>();
				if (carriedAcc == null) carriedAcc = new Dictionary<int, int>();
				if (carriedTick == null) carriedTick = new Dictionary<int, int>();
				if (carriedFluid == null) carriedFluid = new Dictionary<int, FluidDef>();
				if (burningFluid == null) burningFluid = new Dictionary<int, FluidDef>();
				if (pendCell == null || pendDue == null || pendHops == null
					|| pendCell.Count != pendDue.Count || pendCell.Count != pendHops.Count)
				{
					pendCell = new List<int>(); pendDue = new List<int>(); pendHops = new List<int>();
				}
				pendDueOf.Clear(); pendHopsOf.Clear();
				for (int k = 0; k < pendCell.Count; k++)
				{
					OfferPending(pendCell[k], pendDue[k], pendHops[k]);
				}
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
				if (ex.WaterDlAt(c) > 0)   // a thin sheet (no whole notch) burns too
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
			if (burning.ContainsKey(i) || detonating.Contains(i))
			{
				return;
			}
			if (pendDueOf.ContainsKey(i))
			{
				OfferPending(i, due, hops);   // already validated when first queued; an earlier offer advances it
				return;
			}
			if (BurnableFluidAt(map, ex, c) == null || IsSmothered(map, c))
			{
				return;
			}
			OfferPending(i, due, hops);
		}

		/// <summary>Keep the earliest due for a cell, and the smallest hops (the nearer origin binds reach).</summary>
		private void OfferPending(int i, int due, int hops)
		{
			if (pendDueOf.TryGetValue(i, out int oldDue))
			{
				if (due < oldDue) pendDueOf[i] = due;
				if (hops < pendHopsOf[i]) pendHopsOf[i] = hops;
				return;
			}
			pendDueOf[i] = due;
			pendHopsOf[i] = hops;
		}

		private void RemovePending(int i)
		{
			pendDueOf.Remove(i);
			pendHopsOf.Remove(i);
		}

		// ── the per-tick-interval walk ────────────────────────────────────

		public void Tick(Map map, RM_MapComponent_Excavation ex)
		{
			int now = Find.TickManager.TicksGame;
			// the detonation runs every tick (1 tick a ring), not on the 30-tick check
			if (detTick.Count > 0)
			{
				RunDetonation(map, ex, now);
			}
			if (now < nextCheckTick)
			{
				return;
			}
			nextCheckTick = now + CheckInterval;
			PruneMemory(now);
			if (burning.Count == 0 && pendDueOf.Count == 0)
			{
				largeInfernoAnnounced = false;   // nothing alight: the next big chemfuel blaze is announced again
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
		/// due + one step. Chained in one pass, so an inferno (a step of a couple of ticks) crosses many cells per
		/// check while a fuse crosses at most one. A detonating cell instead schedules its whole body (StartDetonation).</summary>
		private void AdvanceFront(Map map, RM_MapComponent_Excavation ex, int now)
		{
			int detonations = 0;
			int guard = 0;
			bool progressed = true;
			while (progressed && guard++ < 10000)
			{
				progressed = false;
				dueScratch.Clear();
				foreach (KeyValuePair<int, int> kv in pendDueOf)
				{
					if (kv.Value <= now)
					{
						dueScratch.Add(kv.Key);
					}
				}
				// deterministic order: earliest due first, then cell index
				dueScratch.Sort((a, b) => pendDueOf[a] != pendDueOf[b] ? pendDueOf[a].CompareTo(pendDueOf[b]) : a.CompareTo(b));
				for (int k = 0; k < dueScratch.Count; k++)
				{
					int i = dueScratch[k];
					if (!pendDueOf.TryGetValue(i, out int due))
					{
						continue;
					}
					int hops = pendHopsOf[i];
					RemovePending(i);
					IntVec3 c = map.cellIndices.IndexToCell(i);
					FluidDef fluid = BurnableFluidAt(map, ex, c);
					// Foam laid after the cell was queued cancels the queued light (GPT FlowWorks review #14).
					if (fluid == null || burning.ContainsKey(i) || IsSmothered(map, c))
					{
						continue;
					}
					progressed = true;
					RM_FuelBurn kind = BurnOf(fluid);
					if (kind == RM_FuelBurn.Detonation && ex.IsExcavated(c))
					{
						// CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL: the whole connected body is scheduled at once; its blasts light
						// whatever burns beside it, so no front leaves this cell. Past the per-check cap of new bodies, the
						// cell waits a tick.
						if (detonations >= MaxDetonationsPerCheck)
						{
							OfferPending(i, now + 1, hops);
							continue;
						}
						detonations++;
						StartDetonation(map, ex, c, now);
						continue;
					}
					Ignite(map, c, i, hops, fluid, now);
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
						TryQueue(map, ex, n, RM_FireMath.FrontDue(due, nf.fireFrontTicksPerCell, FrontSpeedFor(nf)), nh);
					}
				}
			}
		}

		private void Ignite(Map map, IntVec3 c, int i, int hops, FluidDef fluid, int now)
		{
			int acc = TakeCarried(i, fluid, now);
			for (int d = 0; d < 4; d++)
			{
				IntVec3 n = c + GenAdj.CardinalDirections[d];
				if (n.InBounds(map))
				{
					int a = TakeCarried(map.cellIndices.CellToIndex(n), fluid, now);
					if (a > acc) acc = a;
				}
			}
			burning[i] = acc;
			hopsOf[i] = hops;
			burningFluid[i] = fluid;
			EnsureFlame(map, c, fluid);
		}

		/// <summary>Drop cells that no longer hold burnable liquid, keep each flame drawn, re-offer neighbours that
		/// became wet since (a channel refilled beside a fire catches), and apply heat and harm.</summary>
		private void Maintain(Map map, RM_MapComponent_Excavation ex, bool effects)
		{
			scratch.Clear();
			scratch.AddRange(burning.Keys);
			int now = Find.TickManager.TicksGame;
			int infernoCells = 0;
			haloTries = 0;
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
					if (fluid == null && burning.TryGetValue(i, out int moving))
					{
						carriedAcc[i] = moving;
						carriedTick[i] = now;
						carriedFluid[i] = burningFluid.TryGetValue(i, out FluidDef bf) ? bf : null;
					}
					Extinguish(map, c, i, false);
					continue;
				}
				EnsureFlame(map, c, fluid);
				RM_FuelBurn kind = BurnOf(fluid);
				if (kind == RM_FuelBurn.Inferno)
				{
					infernoCells++;
				}
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
						TryQueue(map, ex, n, RM_FireMath.FrontDue(now, nf.fireFrontTicksPerCell, FrontSpeedFor(nf)), nh);
					}
				}
				if (effects)
				{
					if (kind == RM_FuelBurn.Inferno)
					{
						ApplyInfernoEffects(map, ex, c);
					}
					else
					{
						ApplyEffects(map, ex, c);
					}
				}
			}
			// the "large fire" signal fires once per blaze: re-armed only when no chemfuel is left alight
			if (infernoCells >= RM_FuelFireMath.LargeInfernoCells && !largeInfernoAnnounced)
			{
				largeInfernoAnnounced = true;
				RM_FuelFireEvents.RaiseLargeChemfuelFire(map, map.cellIndices.IndexToCell(scratch[0]), infernoCells);
			}
			else if (infernoCells == 0)
			{
				largeInfernoAnnounced = false;
			}
		}

		private int haloTries;

		/// <summary>An inferno cell's effects check (60 ticks): eight times the heat, the pawn in it almost surely alight and
		/// those beside it often, and a few tries at setting fire to burnable things within the halo radius. The tries are
		/// capped per check over the whole map (RM_FuelFireMath.InfernoHaloTriesPerCheck).</summary>
		private void ApplyInfernoEffects(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			float intensity = RimMandrakeFlowWorksSettings.chemfuelIntensity;
			GenTemperature.PushHeat(c, map, RM_FuelFireMath.InfernoHeatPerCheck(intensity));
			// PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE: trapped in the burning pit = down a pit (RM_PitRooms.IsPitFloor: a person-band
			// pocket at any depth), never "dug 2 m"; an intact cover is ground, so its occupant is never trapped
			bool heldInPit = RM_PitRooms.IsPitFloor(map, ex, c);
			List<Thing> things = map.thingGrid.ThingsListAt(c);
			for (int t = things.Count - 1; t >= 0; t--)
			{
				if (things[t] is Pawn p && !p.Dead && !p.Flying
					&& Rand.Chance(heldInPit ? 1f : RM_FuelFireMath.InfernoAttachInCell))
				{
					p.TryAttachFire(heldInPit ? 1f : 0.6f, null);
				}
			}
			for (int d = 0; d < 8; d++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[d];
				if (!n.InBounds(map))
				{
					continue;
				}
				List<Thing> beside = map.thingGrid.ThingsListAt(n);
				for (int t = beside.Count - 1; t >= 0; t--)
				{
					if (beside[t] is Pawn p && !p.Dead && !p.Flying && Rand.Chance(RM_FuelFireMath.InfernoAttachBeside))
					{
						p.TryAttachFire(0.3f, null);
					}
				}
			}
			float radius = RM_FuelFireMath.InfernoIgniteRadius(intensity);
			int cellsInRadius = GenRadial.NumCellsInRadius(radius);
			float size = RM_FuelFireMath.InfernoSpawnedFireSize(intensity);
			for (int k = 0; k < RM_FuelFireMath.InfernoHaloTriesPerCell && haloTries < RM_FuelFireMath.InfernoHaloTriesPerCheck; k++)
			{
				haloTries++;
				IntVec3 n = c + GenRadial.RadialPattern[Rand.Range(1, cellsInRadius)];
				if (!n.InBounds(map) || BurnableFluidAt(map, ex, n) != null)
				{
					continue;
				}
				FireUtility.TryStartFireIn(n, map, size, null);
			}
		}

		private void ApplyEffects(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			// PROVISIONAL heat: about what a vanilla full-size fire pushes over the same time.
			GenTemperature.PushHeat(c, map, 60f);
			// PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE: down a pit at any depth (RM_PitRooms.IsPitFloor), never "dug 2 m". C4-F7: a pawn
			// on an intact cover is above the pit, not trapped in it (IsPitFloor already reads a covered square as ground); a flyer
			// is above the fire.
			bool heldInPit = RM_PitRooms.IsPitFloor(map, ex, c);
			List<Thing> things = map.thingGrid.ThingsListAt(c);
			for (int t = things.Count - 1; t >= 0; t--)
			{
				if (things[t] is Pawn p && !p.Dead && Rand.Chance(RM_FireMath.AttachChance(heldInPit, false, p.Flying)))
				{
					p.TryAttachFire(heldInPit ? 1f : 0.4f, null);
				}
			}
		}

		/// <summary>Ruling 7, run once per flow pulse BEFORE the components resolve (so the burn never reads as a
		/// ledger leak): every burning square loses one notch a day, canal or pond (one rate, D3), in decilitres when
		/// exact-level water is on (a 4.5 cm sheet burns; it never had a whole notch to lose).</summary>
		public void BurnPulse(Map map, RM_MapComponent_Excavation ex, int pulseTicks)
		{
			if (burning.Count == 0 || !RimMandrakeFlowWorksSettings.canalFireEnabled)
			{
				return;
			}
			int notchTicks = RM_FireMath.TicksPerCanalLevel(RimMandrakeFlowWorksSettings.burnDaysPerNotch);
			bool exact = RM_MapComponent_Excavation.LevelExact;
			int U = RM_LevelSolve.U;
			scratch.Clear();
			scratch.AddRange(burning.Keys);
			for (int k = 0; k < scratch.Count; k++)
			{
				int i = scratch[k];
				IntVec3 c = map.cellIndices.IndexToCell(i);
				int acc = burning[i];
				if (ex.IsExcavated(c))
				{
					// Ruling 13 (2026-09-16): a detonating liquid "does not burn down a tier a day — it is consumed at once"
					// (since the owner's card of 2026-10-15 that is astrofuel; chemfuel is an inferno). A detonating cell
					// is normally emptied by its detonation schedule; one lit another way (a source-cell light, a setting
					// switched mid-burn) burns ALL its liquid on the first pulse after it lights, here, before the
					// components resolve, like every other burn.
					FluidDef lit = BurnableFluidAt(map, ex, c);
					RM_FuelBurn litKind = BurnOf(lit);
					if (lit != null && litKind == RM_FuelBurn.Detonation)
					{
						long all = ex.BurnOffDl(c, ex.WaterDlAt(c));
						burnedLevelsTotal += all / (float)U;
						Extinguish(map, c, i, true);
						continue;
					}
					// P8: only a liquid that burns NOW is consumed (lit was read above, after any refill). An inferno burns
					// down in seconds (RM_FuelFireMath.InfernoTicksPerLevel), not a notch a day.
					int levelTicks = litKind == RM_FuelBurn.Inferno && lit != null
						? RM_FuelFireMath.InfernoTicksPerLevelAt(RimMandrakeFlowWorksSettings.chemfuelBurnRate) : notchTicks;
					if (exact)
					{
						long dl = RM_FireMath.CanalDlToBurn(lit != null, ref acc, pulseTicks, levelTicks, U);
						burning[i] = acc;
						long took = dl > 0 ? ex.BurnOffDl(c, dl) : 0;
						burnedLevelsTotal += took / (float)U;
						if (ex.WaterDlAt(c) <= 0)
						{
							Extinguish(map, c, i, true);
						}
						continue;
					}
					int levels = RM_FireMath.CanalLevelsToBurn(lit != null, ref acc, pulseTicks, levelTicks);
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
					// a source square costs its body at the SAME rate (D3), in stock units (a notch of the body = its level
					// unit, 1 for every shipped liquid), so a sub-notch debit is exact to the decilitre
					long dl = RM_FireMath.DlDue(ref acc, pulseTicks, notchTicks, U);
					burning[i] = acc;
					if (dl <= 0)
					{
						continue;
					}
					RM_LiquidBody body = ex.Stock.BodyAt(map, c, ex);
					float unit = body?.fluid != null ? body.fluid.volumePerTile : 1f;
					if (!ex.Stock.TryDebit(map, c, unit * dl / U, ex))
					{
						Extinguish(map, c, i, false);
						continue;
					}
					if (body != null && !body.limitless)
					{
						burnedLevelsTotal += dl / (float)U;
					}
				}
			}
		}

		// ── astrofuel: the detonation ─────────────────────────────────────

		private readonly List<int> bfsRing = new List<int>();
		private readonly List<int> bfsCell = new List<int>();

		/// <summary>Walk the connected astrofuel body from <paramref name="origin"/> (4-way, excavated cells whose liquid detonates,
		/// at most RM_FuelFireMath.MaxDetonationCells) and merge its schedule into the queue. Returns the cells planned.</summary>
		public int StartDetonation(Map map, RM_MapComponent_Excavation ex, IntVec3 origin, int now)
		{
			bfsRing.Clear();
			bfsCell.Clear();
			int o = map.cellIndices.CellToIndex(origin);
			if (detonating.Contains(o))
			{
				return 0;
			}
			HashSet<int> seen = new HashSet<int> { o };
			bfsCell.Add(o);
			bfsRing.Add(0);
			for (int head = 0; head < bfsCell.Count && bfsCell.Count < RM_FuelFireMath.MaxDetonationCells; head++)
			{
				IntVec3 c = map.cellIndices.IndexToCell(bfsCell[head]);
				for (int d = 0; d < 4 && bfsCell.Count < RM_FuelFireMath.MaxDetonationCells; d++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[d];
					if (!n.InBounds(map))
					{
						continue;
					}
					int ni = map.cellIndices.CellToIndex(n);
					if (seen.Contains(ni) || detonating.Contains(ni) || !ex.IsExcavated(n)
						|| BurnOf(BurnableFluidAt(map, ex, n)) != RM_FuelBurn.Detonation)
					{
						continue;
					}
					seen.Add(ni);
					bfsCell.Add(ni);
					bfsRing.Add(bfsRing[head] + 1);
				}
			}
			int count = bfsCell.Count;
			int[] ring = bfsRing.ToArray(), xs = new int[count], zs = new int[count], consume = new int[count], blast = new int[count];
			for (int k = 0; k < count; k++)
			{
				IntVec3 c = map.cellIndices.IndexToCell(bfsCell[k]);
				xs[k] = c.x;
				zs[k] = c.z;
			}
			int spacing = RM_FuelFireMath.PlanDetonation(ring, xs, zs, RM_FuelFireMath.DetonationTicksPerRing,
				RM_FuelFireMath.MaxCellsConsumedPerTick, RM_FuelFireMath.MaxBlastsPerTick, RM_FuelFireMath.MaxBlastsPerDetonation,
				RM_FuelFireMath.BaseBlastSpacing, consume, blast);
			float radius = RM_FuelFireMath.BlastRadiusFor(RimMandrakeFlowWorksSettings.astrofuelBlastScale, spacing);
			List<int> t = new List<int>(count * 2), cl = new List<int>(count * 2), kd = new List<int>(count * 2);
			List<float> rd = new List<float>(count * 2);
			for (int k = 0; k < count; k++)
			{
				detonating.Add(bfsCell[k]);
				RemovePending(bfsCell[k]);
				t.Add(now + consume[k]); cl.Add(bfsCell[k]); kd.Add(0); rd.Add(0f);
				if (blast[k] >= 0)
				{
					t.Add(now + blast[k]); cl.Add(bfsCell[k]); kd.Add(1); rd.Add(radius);
					t.Add(now + blast[k] + RM_FuelFireMath.KnockbackDelayTicks); cl.Add(bfsCell[k]); kd.Add(2); rd.Add(radius);
				}
			}
			MergeSchedule(t, cl, kd, rd);
			detonationsStarted++;
			RM_FuelFireEvents.RaiseAstrofuelDetonation(map, origin, count);
			return count;
		}

		/// <summary>Sort a new schedule by tick (stable) and merge it into the queue, which stays sorted by tick.</summary>
		private void MergeSchedule(List<int> t, List<int> cl, List<int> kd, List<float> rd)
		{
			int[] order = new int[t.Count];
			for (int k = 0; k < order.Length; k++) order[k] = k;
			System.Array.Sort(order, (a, b) => t[a] != t[b] ? t[a].CompareTo(t[b]) : a.CompareTo(b));
			List<int> nt = new List<int>(detTick.Count + t.Count), nc = new List<int>(nt.Capacity), nk = new List<int>(nt.Capacity);
			List<float> nr = new List<float>(nt.Capacity);
			int i = 0, j = 0;
			while (i < detTick.Count || j < order.Length)
			{
				if (j >= order.Length || (i < detTick.Count && detTick[i] <= t[order[j]]))
				{
					nt.Add(detTick[i]); nc.Add(detCell[i]); nk.Add(detKind[i]); nr.Add(detRadius[i]); i++;
				}
				else
				{
					int o = order[j++];
					nt.Add(t[o]); nc.Add(cl[o]); nk.Add(kd[o]); nr.Add(rd[o]);
				}
			}
			detTick = nt; detCell = nc; detKind = nk; detRadius = nr;
		}

		/// <summary>Every tick while a detonation is queued: run what is due, inside the per-tick budgets (what does not fit
		/// waits for the next tick, so concurrent bodies never stack into one frozen tick).</summary>
		private void RunDetonation(Map map, RM_MapComponent_Excavation ex, int now)
		{
			// fire off, or detonation switched off mid-chain: the rest of the schedule drops (its cells keep their fuel and
			// burn however the settings now say, if anything lights them)
			if (!RimMandrakeFlowWorksSettings.canalFireEnabled || !RimMandrakeFlowWorksSettings.astrofuelDetonationEnabled)
			{
				detTick.Clear(); detCell.Clear(); detKind.Clear(); detRadius.Clear(); detonating.Clear();
				return;
			}
			int done = 0, cells = 0, blasts = 0, sounds = 0;
			float scale = RimMandrakeFlowWorksSettings.astrofuelBlastScale;
			for (; done < detTick.Count && detTick[done] <= now; done++)
			{
				int kind = detKind[done];
				if ((kind == 0 && cells >= RM_FuelFireMath.MaxCellsConsumedPerTick) || (kind == 1 && blasts >= RM_FuelFireMath.MaxBlastsPerTick))
				{
					break;   // the rest of the due entries keep their place and run next tick
				}
				int i = detCell[done];
				IntVec3 c = map.cellIndices.IndexToCell(i);
				if (kind == 0)
				{
					cells++;
					ConsumeDetonatedCell(map, ex, c, i, scale, cells);
				}
				else if (kind == 1)
				{
					blasts++;
					// a sound for every third blast: a chain of 200 must not stack 200 sounds
					bool sound = sounds++ % 3 == 0;
					GenExplosion.DoExplosion(c, map, detRadius[done], DamageDefOf.Bomb, null,
						RM_FuelFireMath.BlastDamage(DamageDefOf.Bomb.defaultDamage, scale), chanceToStartFire: 0.4f,
						doSoundEffects: sound, screenShakeFactor: sound ? 1f : 0.3f);
					// the chain's own blast: a pond it reaches lights at most sourceFireReach from its centre
					int boom = NewestExplosionAt(map, c);
					if (boom >= 0)
					{
						blastHops[boom] = 0;
						blastFromSource[boom] = false;
						blastTick[boom] = now;
					}
				}
				else
				{
					Shove(map, ex, c, detRadius[done]);
				}
			}
			if (done > 0)
			{
				detTick.RemoveRange(0, done); detCell.RemoveRange(0, done); detKind.RemoveRange(0, done); detRadius.RemoveRange(0, done);
			}
		}

		private void ConsumeDetonatedCell(Map map, RM_MapComponent_Excavation ex, IntVec3 c, int i, float scale, int nth)
		{
			detonating.Remove(i);
			if (BurnOf(BurnableFluidAt(map, ex, c)) == RM_FuelBurn.Detonation)
			{
				// the whole cell, a part-notch included (a thin astrofuel sheet is consumed too)
				burnedLevelsTotal += ex.BurnOffDl(c, ex.WaterDlAt(c)) / (float)RM_LevelSolve.U;
			}
			detonatedCells += 1f;
			if (burning.ContainsKey(i))
			{
				Extinguish(map, c, i, false);
			}
			FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_Ash, 1);
			// heat on every 4th cell, four times over, so a wide body is not 400 room lookups a tick
			if (nth % 4 == 0)
			{
				GenTemperature.PushHeat(c, map, 4f * RM_FuelFireMath.DetonationHeatPerCell(scale));
			}
			if (nth % 2 == 0)
			{
				FleckMaker.ThrowFireGlow(c.ToVector3Shifted(), map, 2.5f);
			}
		}

		/// <summary>The shockwave a few ticks after a blast landed: whoever still stands within its radius is staggered and
		/// thrown up to KnockbackCells away from it (vanilla's stun flyer). Nobody held in a superdeep pit, nobody flying,
		/// at most KnockbackPerBlast pawns.</summary>
		private static readonly List<Pawn> shoveScratch = new List<Pawn>();

		private static void Shove(Map map, RM_MapComponent_Excavation ex, IntVec3 center, float radius)
		{
			// gather first: a flyer despawns its pawn, which must not happen while the thing grid is being walked
			shoveScratch.Clear();
			foreach (Thing t in GenRadial.RadialDistinctThingsAround(center, map, radius, true))
			{
				if (shoveScratch.Count >= RM_FuelFireMath.KnockbackPerBlast)
				{
					break;
				}
				if (t is Pawn p && p.Spawned && !p.Dead && !p.Flying && !RM_PitRooms.IsPitFloor(map, ex, p.Position))
				{
					shoveScratch.Add(p);
				}
			}
			foreach (Pawn p in shoveScratch)
			{
				if (!p.Spawned || p.Dead)
				{
					continue;
				}
				p.stances?.stagger?.StaggerFor(RM_FuelFireMath.StaggerTicks);
				if (p.Downed)
				{
					continue;
				}
				IntVec3 dest = ThrowDestination(map, center, p.Position);
				ThingDef flyerDef = ThingDefOf.PawnFlyer_Stun ?? ThingDefOf.PawnFlyer;
				if (!dest.IsValid || dest == p.Position || flyerDef == null)
				{
					continue;
				}
				PawnFlyer flyer = PawnFlyer.MakeFlyer(flyerDef, p, dest, null, null);
				if (flyer != null)
				{
					GenSpawn.Spawn(flyer, dest, map);
				}
			}
			shoveScratch.Clear();   // static: never hold a pawn past the call (nor into the next game)
		}

		/// <summary>The farthest standable cell (up to KnockbackCells) straight away from the blast, in line of sight.</summary>
		private static IntVec3 ThrowDestination(Map map, IntVec3 center, IntVec3 from)
		{
			float dx = from.x - center.x, dz = from.z - center.z;
			float len = (float)System.Math.Sqrt(dx * dx + dz * dz);
			if (len < 0.01f)
			{
				IntVec3 r = GenAdj.CardinalDirections[Rand.Range(0, 4)];
				dx = r.x; dz = r.z; len = 1f;
			}
			IntVec3 best = IntVec3.Invalid;
			for (int k = 1; k <= RM_FuelFireMath.KnockbackCells; k++)
			{
				IntVec3 c = new IntVec3(from.x + (int)System.Math.Round(dx / len * k), 0, from.z + (int)System.Math.Round(dz / len * k));
				if (!c.InBounds(map) || !c.Standable(map) || !GenSight.LineOfSight(from, c, map, true))
				{
					break;
				}
				best = c;
			}
			return best;
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
			NotifyExplosionAt(map, ex, c, dam, IntVec3.Invalid);
		}

		public void NotifyExplosionAt(Map map, RM_MapComponent_Excavation ex, IntVec3 c, DamageDef dam, IntVec3 center)
		{
			NotifyExplosionAt(map, ex, c, dam, center, -1);
		}

		/// <summary>C4-F9: the newest Explosion thing at <paramref name="c"/> (the one DoExplosion just spawned), by thing id; -1
		/// when none is listed.</summary>
		private static int NewestExplosionAt(Map map, IntVec3 c)
		{
			List<Thing> l = map.listerThings.ThingsOfDef(ThingDefOf.Explosion);
			for (int k = l.Count - 1; k >= 0; k--)
			{
				if (l[k].Position == c)
				{
					return l[k].thingIDNumber;
				}
			}
			return -1;
		}

		public void NotifyExplosionAt(Map map, RM_MapComponent_Excavation ex, IntVec3 c, DamageDef dam, IntVec3 center, int explosionId)
		{
			if (dam == null || !c.InBounds(map))
			{
				return;
			}
			if (dam == DamageDefOf.Extinguish)
			{
				// foamSmothersLiquidFireEnabled gates BOTH foam routes; the popper's blast ignored it until 2026-10-05
				if (!RimMandrakeFlowWorksSettings.foamSmothersLiquidFireEnabled)
				{
					return;
				}
				int i = map.cellIndices.CellToIndex(c);
				if (burning.ContainsKey(i))
				{
					Extinguish(map, c, i, false);
				}
				// a foam blast also cancels a light still travelling toward this cell (GPT FlowWorks review #14)
				RemovePending(i);
				return;
			}
			if (!RimMandrakeFlowWorksSettings.canalFireEnabled || !RimMandrakeFlowWorksSettings.explosionIgnitesLiquidEnabled
				|| !RM_FireMath.ExplosionIgnites(dam.defName))
			{
				return;
			}
			int blastHopsHere = 0;
			if (center.IsValid && center.InBounds(map))
			{
				// LIQUID_FIRE_QUEUE_ORIGIN_1: a blast the front itself set off carries the front's source hops; a
				// source cell reached through it counts its distance from the blast, and past sourceFireReach it
				// does not light. Any other blast is a direct ignition, hops 0, as before.
				if (explosionId >= 0 && blastHops.TryGetValue(explosionId, out int bh) && ex.IsSourceCell(c))
				{
					int dist = System.Math.Max(System.Math.Abs(c.x - center.x), System.Math.Abs(c.z - center.z));
					blastHopsHere = (blastFromSource[explosionId] ? bh : 0) + System.Math.Max(1, dist);
					if (!RM_FireMath.SourceHopAllowed(blastHopsHere, RimMandrakeFlowWorksSettings.SourceFireReach))
					{
						return;
					}
				}
			}
			TryQueue(map, ex, c, Find.TickManager.TicksGame, blastHopsHere);
		}

		private void PruneMemory(int now)
		{
			if (blastTick.Count > 0)
			{
				scratch.Clear();
				foreach (KeyValuePair<int, int> kv in blastTick)
				{
					if (now - kv.Value > BlastMemoryTicks) scratch.Add(kv.Key);
				}
				foreach (int k in scratch)
				{
					blastTick.Remove(k); blastHops.Remove(k); blastFromSource.Remove(k);
				}
			}
			if (carriedTick.Count > 0)
			{
				scratch.Clear();
				foreach (KeyValuePair<int, int> kv in carriedTick)
				{
					if (now - kv.Value > CarriedExpiryTicks) scratch.Add(kv.Key);
				}
				foreach (int k in scratch)
				{
					carriedTick.Remove(k); carriedAcc.Remove(k); carriedFluid.Remove(k);
				}
			}
		}

		// ── flames ────────────────────────────────────────────────────────

		private static ThingDef FlameFor(FluidDef fluid)
		{
			ThingDef big = RimMandrakeFlowWorks_DefOf.RM_LiquidFlame_Inferno;
			return BurnOf(fluid) == RM_FuelBurn.Inferno && big != null ? big : RimMandrakeFlowWorks_DefOf.RM_LiquidFlame;
		}

		/// <summary>The flame this cell's liquid wants, and only that one (a settings change swaps the big and small flame).</summary>
		private static void EnsureFlame(Map map, IntVec3 c, FluidDef fluid)
		{
			ThingDef def = FlameFor(fluid);
			if (def == null || map.thingGrid.ThingAt(c, def) != null)
			{
				return;
			}
			DestroyFlames(map, c);
			GenSpawn.Spawn(def, c, map);
		}

		private static void DestroyFlames(Map map, IntVec3 c)
		{
			DestroyFlame(map, c, RimMandrakeFlowWorks_DefOf.RM_LiquidFlame);
			DestroyFlame(map, c, RimMandrakeFlowWorks_DefOf.RM_LiquidFlame_Inferno);
		}

		private static void DestroyFlame(Map map, IntVec3 c, ThingDef def)
		{
			Thing flame = def != null ? map.thingGrid.ThingAt(c, def) : null;
			if (flame != null && flame.Spawned)
			{
				flame.Destroy();
			}
		}

		private int TakeCarried(int i, FluidDef fluid, int now)
		{
			if (carriedAcc.TryGetValue(i, out int a))
			{
				bool fresh = carriedTick.TryGetValue(i, out int t) && now - t <= CarriedExpiryTicks;
				bool same = !carriedFluid.TryGetValue(i, out FluidDef cf) || cf == null || cf == fluid;
				carriedAcc.Remove(i); carriedTick.Remove(i); carriedFluid.Remove(i);
				return fresh && same ? a : 0;
			}
			return 0;
		}

		private void Extinguish(Map map, IntVec3 c, int i, bool spent)
		{
			burning.Remove(i);
			hopsOf.Remove(i);
			burningFluid.Remove(i);
			DestroyFlames(map, c);
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
			pendCell.Clear(); pendDue.Clear(); pendHops.Clear(); pendDueOf.Clear(); pendHopsOf.Clear();
			carriedAcc.Clear(); carriedTick.Clear(); carriedFluid.Clear(); burningFluid.Clear();
			blastHops.Clear(); blastFromSource.Clear(); blastTick.Clear();
			detTick.Clear(); detCell.Clear(); detKind.Clear(); detRadius.Clear(); detonating.Clear();
		}

		public string Report()
		{
			return "FIRE burning " + burning.Count + " | front pending " + pendDueOf.Count
				+ " | burned levels " + burnedLevelsTotal.ToString("F0")
				+ " | detonations " + detonationsStarted + " cells " + detonatedCells.ToString("F0") + " queued " + detTick.Count;
		}

		/// <summary>LIQUID_FIRE_QUEUE_ORIGIN_1 A2 read: one cell's place in the fire. "FIRECELL x,z burning=b pending=b
		/// due=N hops=H now=T" (due/hops -1 when not pending).</summary>
		public string CellReport(Map map, IntVec3 c)
		{
			int i = map.cellIndices.CellToIndex(c);
			bool pending = pendDueOf.TryGetValue(i, out int due);
			int hops = pending && pendHopsOf.TryGetValue(i, out int h) ? h : -1;
			return "FIRECELL " + c.x + "," + c.z + " burning=" + burning.ContainsKey(i) + " pending=" + pending
				+ " due=" + (pending ? due : -1) + " hops=" + hops + " now=" + Find.TickManager.TicksGame;
		}

		/// <summary>LIQUID_FIRE_QUEUE_ORIGIN_1 A1 read: the SOURCE cells burning or pending, and how many lie farther
		/// (Chebyshev) than <paramref name="reach"/> from <paramref name="entry"/>, the cell where the front entered the body.
		/// "SPREAD from=x,z reach=R burningSource=n pendingSource=n far=n maxDist=d".</summary>
		public string SourceSpread(Map map, RM_MapComponent_Excavation ex, IntVec3 entry, int reach)
		{
			int burningSource = 0, pendingSource = 0, far = 0, maxDist = 0;
			foreach (int i in burning.Keys)
			{
				Spread(map, ex, i, entry, reach, ref burningSource, ref far, ref maxDist);
			}
			foreach (int i in pendDueOf.Keys)
			{
				Spread(map, ex, i, entry, reach, ref pendingSource, ref far, ref maxDist);
			}
			return "SPREAD from=" + entry.x + "," + entry.z + " reach=" + reach + " burningSource=" + burningSource
				+ " pendingSource=" + pendingSource + " far=" + far + " maxDist=" + maxDist;
		}

		private static void Spread(Map map, RM_MapComponent_Excavation ex, int i, IntVec3 entry, int reach, ref int n,
			ref int far, ref int maxDist)
		{
			IntVec3 c = map.cellIndices.IndexToCell(i);
			if (!ex.IsSourceCell(c))
			{
				return;
			}
			n++;
			int d = System.Math.Max(System.Math.Abs(c.x - entry.x), System.Math.Abs(c.z - entry.z));
			if (d > maxDist) maxDist = d;
			if (d > reach) far++;
		}

		/// <summary>The pending front as "cell:due:hops" sorted by cell, for comparing a save round trip.</summary>
		public string PendingSnapshot()
		{
			List<int> keys = new List<int>(pendDueOf.Keys);
			keys.Sort();
			System.Text.StringBuilder sb = new System.Text.StringBuilder();
			foreach (int k in keys)
			{
				sb.Append(k).Append(':').Append(pendDueOf[k]).Append(':').Append(pendHopsOf.TryGetValue(k, out int h) ? h : 0).Append(';');
			}
			return sb.ToString();
		}
	}

	/// <summary>The trigger: any vanilla Fire that spawns (not a reload) offers its cell and neighbours.</summary>
	[HarmonyPatch(typeof(Fire), nameof(Fire.SpawnSetup))]
	[RimMandrake.Shared.PatchFeature("Burning liquid", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "canalFireEnabled")]
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
	[RimMandrake.Shared.PatchFeature("Explosions light burnable liquid", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "explosionIgnitesLiquidEnabled")]
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
			if (ex == null || (ex.LiquidFire.BurningCount == 0 && ex.LiquidFire.PendingCount == 0
				&& explosion.damType == DamageDefOf.Extinguish))
			{
				return;
			}
			ex.LiquidFire.NotifyExplosionAt(map, ex, c, explosion.damType, explosion.Position, explosion.thingIDNumber);
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

		private static bool Cell(Map map, string s, out IntVec3 c)
		{
			c = IntVec3.Invalid;
			string[] p = (s ?? "").Split(',');
			if (p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z))
			{
				return false;
			}
			c = new IntVec3(x, 0, z);
			return map != null && c.InBounds(map);
		}

		/// <summary>LIQUID_FIRE_QUEUE_ORIGIN_1 A2: "x,z" -> RM_LiquidFire.CellReport.</summary>
		public static string ProofCell(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null) return "REFUSED: no excavation component on the current map";
			if (!Cell(map, arg, out IntVec3 c)) return "REFUSED: arg must be x,z on the current map";
			return ex.LiquidFire.CellReport(map, c);
		}

		/// <summary>WRITES. LIQUID_FIRE_QUEUE_ORIGIN_1 A2, the dropped torch: "x,z" spawns a small vanilla Fire there, so
		/// the shipping Fire.SpawnSetup hook (RM_Patch_FireLightsLiquid) offers the cell and its 8 neighbours. The Fire
		/// may burn out at once on bare ground; the offer is made on spawn. "TORCH x,z fire=b".</summary>
		public static string ProofTorch(string arg)
		{
			Map map = Find.CurrentMap;
			if (!Cell(map, arg, out IntVec3 c)) return "REFUSED: arg must be x,z on the current map";
			Fire fire = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
			fire.fireSize = 0.1f;
			GenSpawn.Spawn(fire, c, map, Rot4.North);
			return "TORCH " + c.x + "," + c.z + " fire=" + fire.Spawned;
		}

		/// <summary>LIQUID_FIRE_QUEUE_ORIGIN_1 A1: "x,z;R" -> RM_LiquidFire.SourceSpread from the entry cell x,z.</summary>
		public static string ProofSourceSpread(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null) return "REFUSED: no excavation component on the current map";
			string[] a = (arg ?? "").Split(';');
			if (a.Length != 2 || !Cell(map, a[0], out IntVec3 c) || !int.TryParse(a[1], out int reach))
				return "REFUSED: arg must be x,z;R on the current map";
			return ex.LiquidFire.SourceSpread(map, ex, c, reach);
		}

		/// <summary>LIQUID_FIRE_QUEUE_ORIGIN_1 A3, the save half without a game reload: the current map's RM_LiquidFire
		/// is written through Scribe (its own ExposeData, as a save does) to a temp file and read back into a fresh
		/// instance (LoadingVars + PostLoadInit, as a load does); the live instance is never replaced. "ROUNDTRIP pending=n
		/// restored=n same=b", or "REFUSED"/"error: ...".</summary>
		public static string ProofFrontRoundTrip(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null) return "REFUSED: no excavation component on the current map";
			if (Scribe.mode != LoadSaveMode.Inactive) return "REFUSED: Scribe is busy (" + Scribe.mode + ")";
			RM_LiquidFire live = ex.LiquidFire;
			string before = live.PendingSnapshot();
			string path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "rm_liquidfire_roundtrip.xml");
			RM_LiquidFire copy = null;
			try
			{
				Scribe.saver.InitSaving(path, "LiquidFireRoundTrip");
				try { Scribe_Deep.Look(ref live, "RM_liquidFire"); }
				finally { Scribe.saver.FinalizeSaving(); }
				Scribe.loader.InitLoading(path);
				try { Scribe_Deep.Look(ref copy, "RM_liquidFire"); }
				finally { Scribe.loader.FinalizeLoading(); }
			}
			catch (System.Exception e)
			{
				Scribe.ForceStop();
				return "error: " + e.Message;
			}
			finally
			{
				try { System.IO.File.Delete(path); } catch { }
			}
			if (copy == null) return "error: nothing loaded back";
			return "ROUNDTRIP pending=" + live.PendingCount + " restored=" + copy.PendingCount
				+ " same=" + (before == copy.PendingSnapshot());
		}
	}

	/// <summary>CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL: what the fuel fires announce to other layers. RimUtinni listens (a raid comes to
	/// look); FlowWorks itself never acts on them. Handlers run inside the tick that raised them; one that throws is logged
	/// once and never stops the fire.</summary>
	public static class RM_FuelFireEvents
	{
		/// <summary>An astrofuel body went up: (map, where it was lit, cells planned).</summary>
		public static event System.Action<Map, IntVec3, int> AstrofuelDetonated;

		/// <summary>A chemfuel fire reached RM_FuelFireMath.LargeInfernoCells lit cells: (map, a lit cell, lit cells). Once per blaze.</summary>
		public static event System.Action<Map, IntVec3, int> LargeChemfuelFire;

		internal static void RaiseAstrofuelDetonation(Map map, IntVec3 at, int cells) => Raise(AstrofuelDetonated, map, at, cells);

		internal static void RaiseLargeChemfuelFire(Map map, IntVec3 at, int cells) => Raise(LargeChemfuelFire, map, at, cells);

		private static void Raise(System.Action<Map, IntVec3, int> handlers, Map map, IntVec3 at, int cells)
		{
			if (handlers == null)
			{
				return;
			}
			foreach (System.Delegate d in handlers.GetInvocationList())
			{
				try
				{
					((System.Action<Map, IntVec3, int>)d)(map, at, cells);
				}
				catch (System.Exception e)
				{
					Log.ErrorOnce("[FlowWorks] a fuel-fire listener threw: " + e, d.Method.GetHashCode() ^ 0x5F17E);
				}
			}
		}
	}
}
