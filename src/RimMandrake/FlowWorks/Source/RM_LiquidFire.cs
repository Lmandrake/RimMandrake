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
	/// - BURN: ruling 7, a rate on the tier ladder: one canal fill level per day (a DETONATING liquid's canal
	///   cell is instead consumed whole on the first pulse after it lights, ruling 13); a source cell costs its body one
	///   level per five days, so a limitless source burns forever and a moat piped from a larger body burns as
	///   long as inflow beats the burn. Burned liquid is GONE (the second disclosed exit, beside overflow):
	///   counted in <see cref="BurnedLevelsTotal"/>, debited outside the pulse's conservation ledger.
	/// - EFFECT: pawns in the burning cell catch fire; one held in a D=4 pit always does (ruling 22).
	/// - SPENT: a canal cell that burns dry is left scorched (ash) — the `canal_spent_after_burn` bar.
	/// - EXPLOSIONS: a flame or bomb blast lights burnable liquid in every cell it touches, Fire or no Fire
	///   (DamageWorker.ExplosionAffectCell postfix). A firefoam blast (Extinguish) smothers instead.
	/// - PUTTING IT OUT: a firefoam blast (popper, Extinguish damage) puts a burning cell out; foam lying on a cell
	///   would also keep it from relighting, but fill terrains are water-tagged and take no filth, so in practice
	///   it is the blast that acts. Rain on an unroofed burning cell has a chance each check to douse it (oil and tar float, so
	///   rain is slow, never instant; a neighbour still alight can relight it). Neither marks the cell spent.
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
		// a 6-cell tar run held 3 cells alight at 7,000 ticks with the burn cut to 1,200 ticks a level). Not saved: on
		// load a moving level restarts its clock once, as before.
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
		private int checkCount;

		private List<int> burningKeys;
		private List<int> burningValues;
		private List<int> hopsKeys;
		private List<int> hopsValues;
		private readonly List<int> scratch = new List<int>();
		private readonly List<int> dueScratch = new List<int>();

		public int BurningCount => burning.Count;
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
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
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
			if (burning.ContainsKey(i))
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
			if (now < nextCheckTick)
			{
				return;
			}
			nextCheckTick = now + CheckInterval;
			PruneMemory(now);
			if (burning.Count == 0 && pendDueOf.Count == 0)
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
					Ignite(map, c, i, hops, fluid, now);
					progressed = true;
					if (fluid.fireKind == RM_FluidFireKind.Detonation && detonations < MaxDetonationsPerCheck
						&& ((c.x + c.z) % 3 == 0))
					{
						// PROVISIONAL: one blast per ~3 cells of front, capped per check, driven from here (Phase 6:
						// "drive them centrally; do not spawn a Thing per cell").
						detonations++;
						GenExplosion.DoExplosion(c, map, 1.9f, DamageDefOf.Flame, null);
						int boom = NewestExplosionAt(map, c);
						if (boom >= 0)
						{
							blastHops[boom] = hops;
							blastFromSource[boom] = ex.IsSourceCell(c);
							blastTick[boom] = now;
						}
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
					if (fluid == null && burning.TryGetValue(i, out int moving))
					{
						carriedAcc[i] = moving;
						carriedTick[i] = now;
						carriedFluid[i] = burningFluid.TryGetValue(i, out FluidDef bf) ? bf : null;
					}
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
			// C4-F7: a pawn on an intact cover is above the pit, not trapped in it; a flyer is above the fire
			bool onCover = heldInPit && Pits.RM_PitCoverUtility.CoverAt(map, c) != null;
			List<Thing> things = map.thingGrid.ThingsListAt(c);
			for (int t = things.Count - 1; t >= 0; t--)
			{
				if (things[t] is Pawn p && !p.Dead && Rand.Chance(RM_FireMath.AttachChance(heldInPit, onCover, p.Flying)))
				{
					p.TryAttachFire(heldInPit && !onCover ? 1f : 0.4f, null);
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
					// Ruling 13 (2026-09-16): "astrofuel and chemfuel detonate" — a detonating liquid "does not burn down a
					// tier a day — it is consumed at once". So a lit detonating canal cell burns ALL its levels on the
					// first pulse after it lights (here, before the components resolve, like every other burn).
					FluidDef lit = BurnableFluidAt(map, ex, c);
					if (lit != null && lit.fireKind == RM_FluidFireKind.Detonation)
					{
						int guardLv = 0;
						while (ex.FillAt(c) > 0 && guardLv++ < 16)
						{
							if (!ex.BurnOffLevel(c))
							{
								break;
							}
							burnedLevelsTotal += 1f;
						}
						if (ex.FillAt(c) == 0)
						{
							Extinguish(map, c, i, true);
						}
						continue;
					}
					// P8: only a liquid that burns NOW is consumed (lit was read above, after any refill).
					int levels = RM_FireMath.CanalLevelsToBurn(lit != null, ref acc, pulseTicks, canalTicks);
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

		private static void EnsureFlame(Map map, IntVec3 c)
		{
			ThingDef def = RimMandrakeFlowWorks_DefOf.RM_LiquidFlame;
			if (def == null || map.thingGrid.ThingAt(c, def) != null)
			{
				return;
			}
			GenSpawn.Spawn(def, c, map);
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
			pendCell.Clear(); pendDue.Clear(); pendHops.Clear(); pendDueOf.Clear(); pendHopsOf.Clear();
			carriedAcc.Clear(); carriedTick.Clear(); carriedFluid.Clear(); burningFluid.Clear();
			blastHops.Clear(); blastFromSource.Clear(); blastTick.Clear();
		}

		public string Report()
		{
			return "FIRE burning " + burning.Count + " | front pending " + pendDueOf.Count
				+ " | burned levels " + burnedLevelsTotal.ToString("F0");
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
}
