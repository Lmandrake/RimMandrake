using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// Phase 4's stock model: the 5:1 budget, sticky-limitless classification,
	/// recession from the outside in, and refill from seepage, rain and season.
	///
	/// NOT A MapComponent, ON PURPOSE. Stock is debited at pulse boundaries by
	/// <see cref="RM_MapComponent_Excavation"/>'s own sort-and-overflow, and two
	/// MapComponents would tick in an order nothing guarantees — a debit could
	/// land before or after the flow that caused it depending on discovery
	/// order. One owner, one pulse, one ordering. The excavation component
	/// holds this object and scribes it inline.
	///
	/// EVERYTHING HERE IS PER PULSE. Pillar 2 is not negotiable: nothing in this
	/// file is reachable from a per-tick path.
	/// </summary>
	public class RM_LiquidStock : IExposable
	{
		/// <summary>A flood fill bigger than this is an ocean, not a pond. It is
		/// classified limitless on that basis and its footprint list is
		/// truncated — a 40,000-cell list in every save is a cost paid for a
		/// number the sentinel already answers.
		///
		/// POND_ELEVATION_BUILD_LAKES_RUN_DEEP (§9.3): only for a body that touches the map edge. A walk that hits this cap
		/// without touching the edge is walked again up to "drainableLakeMaxCells", and a complete inland body is a LIMITED,
		/// drainable lake however big.</summary>
		private const int MaxBodyCells = RM_BedMath.OceanWalkCells;

		private List<RM_LiquidBody> bodies = new List<RM_LiquidBody>();

		private int nextBodyId = 1;

		/// <summary>Derived, never scribed: cell index to body id, rebuilt from
		/// <see cref="bodies"/> on load.</summary>
		private readonly Dictionary<int, int> cellToBody = new Dictionary<int, int>();

		private readonly Dictionary<int, RM_LiquidBody> byId = new Dictionary<int, RM_LiquidBody>();

		private readonly List<int> fillQueue = new List<int>();
		private readonly List<int> fillFound = new List<int>();

		private readonly HashSet<int> fillSeen = new HashSet<int>();

		/// <summary>POND_ELEVATION_BUILD_LAKES_RUN_DEEP: the inland re-walk's own buffers (the first walk's result is kept
		/// when the re-walk finds an ocean after all).</summary>
		private readonly List<int> lakeFound = new List<int>();
		private readonly List<int> lakeQueue = new List<int>();
		private readonly HashSet<int> lakeSeen = new HashSet<int>();

		/// <summary>Derived scratch for recession (map-sized arrays, reused; never scribed).</summary>
		private readonly RM_RecessionSet recession = new RM_RecessionSet();
		private readonly List<int> footprintScratch = new List<int>();

		/// <summary>Set after a load; BodyAt rebuilds the index first so a saved body is never re-formed from terrain.</summary>
		private bool indexDirty;

		public IReadOnlyList<RM_LiquidBody> Bodies => bodies;

		public void ExposeData()
		{
			Scribe_Collections.Look(ref bodies, "RM_liquidBodies", LookMode.Deep);
			Scribe_Values.Look(ref nextBodyId, "RM_nextLiquidBodyId", 1);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				indexDirty = true;
				if (bodies == null)
				{
					bodies = new List<RM_LiquidBody>();
				}
			}
		}

		/// <summary>Rebuild the derived indices. Called from the owner's
		/// FinalizeInit, after the grids exist.</summary>
		public void RebuildIndex(Map map)
		{
			indexDirty = false;
			cellToBody.Clear();
			byId.Clear();
			for (int b = 0; b < bodies.Count; b++)
			{
				RM_LiquidBody body = bodies[b];
				byId[body.id] = body;
				for (int i = 0; i < body.cells.Count; i++)
				{
					IntVec3 c = body.cells[i];
					if (c.InBounds(map))
					{
						cellToBody[map.cellIndices.CellToIndex(c)] = body.id;
					}
				}
			}
		}

		// ── formation and classification (ruling 16) ──────────────────────

		/// <summary>The body owning a natural source cell, forming and
		/// classifying it on first contact. Returns null when the cell was never
		/// part of a natural body. A cell already indexed returns its body even
		/// after it receded or was dug: callers that need a wet cell check
		/// IsSourceCell first.
		///
		/// 🔴 CLASSIFIED ONCE. If a record already exists for this cell, it is
		/// returned untouched — no size re-check, no edge re-check, no
		/// hysteresis, and therefore no flicker in the strained graphic. That is
		/// the whole of ruling 16 and it is enforced by this early return.</summary>
		public RM_LiquidBody BodyAt(Map map, IntVec3 c, RM_MapComponent_Excavation owner)
		{
			if (!c.InBounds(map))
			{
				return null;
			}
			if (RM_StockMath.NeedsIndexRebuild(indexDirty, bodies.Count, cellToBody.Count))
			{
				RebuildIndex(map);
			}
			int idx = map.cellIndices.CellToIndex(c);
			int existing;
			if (cellToBody.TryGetValue(idx, out existing))
			{
				RM_LiquidBody found;
				return byId.TryGetValue(existing, out found) ? found : null;
			}
			if (!owner.IsSourceCell(c))
			{
				return null;
			}
			return FormBody(map, c, owner);
		}

		private RM_LiquidBody FormBody(Map map, IntVec3 seed, RM_MapComponent_Excavation owner)
		{
			// The 8-way footprint walk is RM_FlowKernel.CollectBody (Verse-free, so the selftest runs it).
			// A body truncated at MaxBodyCells leaves its far cells unindexed, so contact there would re-enter
			// FormBody and re-walk the owned cells into an overlapping duplicate body. Touching an owned cell
			// means this region IS that body: CollectBody stops and names it, and what was found is indexed to it.
			int sizeX = map.Size.x;
			FluidDef seedFluid = RM_FluidIdentity.FluidOfTerrain(map.terrainGrid.TerrainAt(seed)) ?? RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;
			Func<int, bool> isSource = i => owner.IsSourceCell(map.cellIndices.IndexToCell(i));
			Func<int, int> ownedBody = i => cellToBody.TryGetValue(i, out int id) && byId.ContainsKey(id) ? id : -1;
			Func<int, bool> sameFluid = i => (RM_FluidIdentity.FluidOfTerrain(map.terrainGrid.TerrainAt(i)) ?? RimMandrakeFlowWorks_DefOf.RM_Fluid_Water) == seedFluid;
			int ownedId = RM_FlowKernel.CollectBody(sizeX, map.Size.z, map.cellIndices.CellToIndex(seed), isSource, ownedBody,
				MaxBodyCells, fillFound, fillQueue, fillSeen, out bool touchesEdge, out bool truncated, sameFluid);
			// POND_ELEVATION_BUILD_LAKES_RUN_DEEP (§9.3): the ocean cap was hit inland. Walk on up to the drainable-lake cap; a
			// complete body that never touches the edge is a lake, kept whole and limited. Anything else keeps the first walk.
			int lakeCap = RimMandrakeFlowWorksSettings.DrainableLakeMaxCells;
			// FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES: with a map-edge setter, "touches the edge" means an edge that is not
			// sealed (a drain edge forces limitless below), here and for the lake walk, so a lake on sealed edges walks on
			// whole and comes out LIMITED. A body still bigger than the drainable-lake cap stays limitless (truncated).
			bool drainEdge = false;
			int[] edgeModes = MapControls.RM_MapControls.EdgeModes(map);
			if (edgeModes != null && ownedId < 0)
			{
				MapControls.RM_MapControls.BodyEdgeContact(map, edgeModes, fillFound, out touchesEdge, out drainEdge);
			}
			if (ownedId < 0 && truncated && !touchesEdge && lakeCap > MaxBodyCells)
			{
				int lakeOwned = RM_FlowKernel.CollectBody(sizeX, map.Size.z, map.cellIndices.CellToIndex(seed), isSource, ownedBody,
					lakeCap, lakeFound, lakeQueue, lakeSeen, out bool lakeEdge, out bool lakeTruncated, sameFluid);
				if (edgeModes != null && lakeOwned < 0)
				{
					MapControls.RM_MapControls.BodyEdgeContact(map, edgeModes, lakeFound, out lakeEdge, out bool lakeDrain);
					lakeEdge |= lakeDrain;
				}
				if (lakeOwned < 0 && !lakeEdge && !lakeTruncated)
				{
					fillFound.Clear();
					fillFound.AddRange(lakeFound);
					truncated = false;
				}
				lakeFound.Clear();
				lakeSeen.Clear();
			}
			if (ownedId >= 0)
			{
				RM_LiquidBody owned = byId[ownedId];
				for (int f = 0; f < fillFound.Count; f++)
				{
					// POND_RETURN_LEG_BUILD_WATER_GOES_HOME (GPT #19): a truncated body's far cells were indexed but never
					// saved, so every load re-walked them. Persist them in its footprint; a truncated body is limitless, so
					// its capacity is not touched. A limited body's footprint is fixed at formation (ruling 16).
					// POND_CAPACITY_FIX_DOUBLING_BED (C2-F7): with sticky-limitless off a truncated body is LIMITED; its far
					// squares hold real water, so they join with their bed's worth of capacity AND stock (never free cells).
					if (owned.truncated && !cellToBody.ContainsKey(fillFound[f]))
					{
						IntVec3 far = map.cellIndices.IndexToCell(fillFound[f]);
						owned.cells.Add(far);
						if (!owned.limitless)
						{
							float add = LevelUnitOf(owned, owner) * owner.BedLevelsAt(far);
							owned.capacity += add;
							owned.AddStock(add);
						}
					}
					cellToBody[fillFound[f]] = ownedId;
				}
				return owned;
			}
			List<IntVec3> found = new List<IntVec3>(fillFound.Count);
			for (int f = 0; f < fillFound.Count; f++)
			{
				found.Add(map.cellIndices.IndexToCell(fillFound[f]));
			}
			RM_LiquidBody body = new RM_LiquidBody(nextBodyId++);
			body.cells = found;
			body.truncated = truncated;
			// FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES: touchesEdge / drainEdge were ruled by the map-edge setter above (a sealed
			// edge is no off-map reservoir; a drain edge makes the body limitless).
			// Ruling 16: edge contact AND a minimum size. Both, and only here.
			body.limitless = drainEdge || RM_StockMath.IsLimitless(
				RimMandrakeFlowWorksSettings.stickyLimitlessEnabled,
				truncated,
				touchesEdge,
				found.Count,
				RimMandrakeFlowWorksSettings.MinLimitlessBodyCells);
			body.fluid = RM_FluidIdentity.FluidOfTerrain(map.terrainGrid.TerrainAt(seed)) ?? RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;
			// POND_ELEVATION_BUILD_LAKES_RUN_DEEP (§9.4): a drainable lake's deep middle runs deeper than 4, recorded once now
			// (before its capacity is summed), so reloads, recession and refill all read the same bowl.
			if (!body.limitless && RimMandrakeFlowWorksSettings.deepBedsEnabled)
			{
				RecordDeepBeds(map, fillFound, owner);
			}
			// LIQUID_BODY_FLUID_IDENTITY_1 step 3: capacity is the body's OWN fluid's, never the map's.
			// POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK: each square holds its own bed depth (shallow 2, deep 4).
			body.capacity = CapacityOf(body, owner);
			body.levelUnit = RM_BedMath.LevelUnit(body.capacity, BedSum(body, owner));
			body.stock = body.capacity;
			bodies.Add(body);
			byId[body.id] = body;
			for (int i = 0; i < found.Count; i++)
			{
				cellToBody[map.cellIndices.CellToIndex(found[i])] = body.id;
			}
			if (Prefs.DevMode)
			{
				Log.Message("[RimMandrake.FlowWorks] classified liquid body #" + body.id + ": "
					+ found.Count + " cells, " + (body.limitless ? "LIMITLESS" : "LIMITED")
					+ " (" + body.StockReport() + "). Classification is sticky — this never runs again "
					+ "for these cells.");
			}
			return body;
		}

		/// <summary>§9.4: write the bed of every footprint square deeper than the deep notch (RM_BedMath.BedDepths over the
		/// map's own water terrain). Shallow and shore squares keep the terrain rule, so a small pond records nothing.</summary>
		private static void RecordDeepBeds(Map map, List<int> footprint, RM_MapComponent_Excavation owner)
		{
			int[] beds = new int[footprint.Count];
			RM_BedMath.BedDepths(map.Size.x, map.Size.z, footprint,
				i => owner.BedLevelsAt(map.cellIndices.IndexToCell(i)) >= RM_Volume.LevelsPerSquare,
				RimMandrakeFlowWorksSettings.DeepBedCellsPerLevel, RimMandrakeFlowWorksSettings.DeepBedMaxDepth, beds);
			for (int k = 0; k < footprint.Count; k++)
			{
				if (beds[k] > RM_Volume.LevelsPerSquare)
				{
					owner.RecordBedDepth(footprint[k], beds[k]);
				}
			}
		}

		/// <summary>Σ bed levels over a body's footprint.</summary>
		public static int BedSum(RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			int sum = 0;
			for (int i = 0; i < body.cells.Count; i++)
			{
				sum += owner.BedLevelsAt(body.cells[i]);
			}
			return sum;
		}

		/// <summary>POND_CAPACITY_FIX_DOUBLING_BED: the body's level unit, derived once for a save from before the field
		/// (capacity ÷ beds while it has any; else the fluid × budget a new pond would get).</summary>
		public static float LevelUnitOf(RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			if (body.levelUnit > 0f)
			{
				return body.levelUnit;
			}
			float u = RM_BedMath.LevelUnit(body.capacity, BedSum(body, owner));
			if (!(u > 0f))
			{
				FluidDef f = body.fluid;
				u = (f != null ? f.volumePerTile : 1f) * RimMandrakeFlowWorksSettings.sourceBudgetMultiplier;
			}
			body.levelUnit = u;
			return u;
		}

		/// <summary>POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK: Σ bed levels over the footprint × the body's own fluid's
		/// volumePerTile × the budget slider. Used at formation and by the one-time volume-model migration.</summary>
		public static float CapacityOf(RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			int sum = 0;
			for (int i = 0; i < body.cells.Count; i++)
			{
				sum += owner.BedLevelsAt(body.cells[i]);
			}
			FluidDef fluid = body.fluid;
			return RM_Volume.BodyCapacity(sum, body.cells.Count, fluid != null ? fluid.volumePerTile : 1f,
				RimMandrakeFlowWorksSettings.sourceBudgetMultiplier);
		}

		/// <summary>§8.3: the one-time move of a save written under volume model 1 (5 levels a pond square) to model 2.
		/// Limited bodies get their capacity recomputed from the footprint and keep their fill fraction; limitless
		/// bodies are untouched. One log line per body. Returns how many bodies were rescaled.</summary>
		public int MigrateVolumeModel(RM_MapComponent_Excavation owner)
		{
			int n = 0;
			for (int b = 0; b < bodies.Count; b++)
			{
				RM_LiquidBody body = bodies[b];
				if (body.limitless)
				{
					continue;
				}
				float oldCap = body.capacity, oldStock = body.stock;
				float newCap = CapacityOf(body, owner);
				body.capacity = newCap;
				body.levelUnit = RM_BedMath.LevelUnit(newCap, BedSum(body, owner));
				body.stock = RM_Volume.MigratedStock(oldStock, oldCap, newCap);
				n++;
				Log.Message("[RimMandrake.FlowWorks] volume model 2: pond #" + body.id + " rescaled " + oldStock.ToString("F2")
					+ "/" + oldCap.ToString("F0") + " -> " + body.stock.ToString("F2") + "/" + newCap.ToString("F0") + " fill-units.");
			}
			return n;
		}

		/// <summary>The body a cell is indexed to, WITHOUT forming one (null when none). For callers that must not
		/// classify a lake as a side effect (the dig hook, the return leg's read-only check, the refill guard).</summary>
		public RM_LiquidBody IndexedBodyAt(Map map, IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return null;
			}
			if (RM_StockMath.NeedsIndexRebuild(indexDirty, bodies.Count, cellToBody.Count))
			{
				RebuildIndex(map);
			}
			return cellToBody.TryGetValue(map.cellIndices.CellToIndex(c), out int id) && byId.TryGetValue(id, out RM_LiquidBody b)
				? b : null;
		}

		public RM_LiquidBody BodyById(int id)
		{
			return byId.TryGetValue(id, out RM_LiquidBody b) ? b : null;
		}

		/// <summary>Owner ruling 6 (2026-10-12): digging a DRY bed square takes it out of the pond. The square leaves the
		/// footprint and the receded list, and the pond's capacity loses that square's bed × the body's level unit, so
		/// <see cref="ReattachBedCell"/> is the exact inverse in ANY order (POND_CAPACITY_FIX_DOUBLING_BED: a ratio of the old
		/// capacity could not survive the last square leaving). Returns the fill-units of stock that no longer fit (the
		/// caller discloses them; normally 0, because a receded square was unfunded).</summary>
		public float DetachBedCell(Map map, RM_LiquidBody body, IntVec3 c, RM_MapComponent_Excavation owner)
		{
			int idx = body.cells.IndexOf(c);
			if (idx < 0)
			{
				return 0f;
			}
			float unit = body.limitless ? 0f : LevelUnitOf(body, owner);
			body.cells.RemoveAt(idx);
			body.receded.Remove(c);
			cellToBody.Remove(map.cellIndices.CellToIndex(c));
			if (body.limitless)
			{
				return 0f;
			}
			body.capacity = RM_BedMath.CapacityForBeds(unit, BedSum(body, owner));
			float excess = body.stock > body.capacity ? body.stock - body.capacity : 0f;
			body.AddStock(-excess);
			return excess;
		}

		/// <summary>Ruling 6's other half: filling a dug bed square back in to the surface returns it to its pond, dry
		/// (receded, refillable by any inflow), with its capacity share back. Never writes water: the stock that would
		/// fill it has not been paid (the G5 bug this replaces).</summary>
		public void ReattachBedCell(Map map, RM_LiquidBody body, IntVec3 c, RM_MapComponent_Excavation owner)
		{
			if (body.cells.Contains(c))
			{
				return;
			}
			float unit = body.limitless ? 0f : LevelUnitOf(body, owner);
			body.cells.Add(c);
			body.receded.Add(c);
			cellToBody[map.cellIndices.CellToIndex(c)] = body.id;
			if (!body.limitless)
			{
				body.capacity = RM_BedMath.CapacityForBeds(unit, BedSum(body, owner));
			}
		}

		// ── the budget in use ─────────────────────────────────────────────

		/// <summary>May this source cell still hand liquid out? A limitless body
		/// always can. A limited one stops the moment its stock is spent, which
		/// is what makes a small pond a real constraint instead of a decoration.</summary>
		public bool CanSupply(Map map, IntVec3 c, RM_MapComponent_Excavation owner)
		{
			if (!RimMandrakeFlowWorksSettings.sourceBudgetEnabled)
			{
				return true;
			}
			RM_LiquidBody body = BodyAt(map, c, owner);
			if (body == null)
			{
				return true;
			}
			// Compared against the SAME unit TryDebit spends. A threshold of a
			// flat 1 would let a viscous liquid with volumePerTile above 1 pass
			// the check and then fail the debit, which reads as a source that
			// stutters rather than one that is empty.
			FluidDef fluid = body.fluid ?? owner.ActiveFluid;
			float unit = fluid != null ? fluid.volumePerTile : 1f;
			return RM_StockMath.CanSupply(body.limitless, body.stock, unit);
		}

		/// <summary>Spend from the body behind a source cell. Returns false when
		/// there was nothing to spend, in which case the caller must NOT move
		/// the liquid — a debit that fails and a transfer that happens anyway is
		/// exactly the silent leak the ledger exists to catch.</summary>
		public bool TryDebit(Map map, IntVec3 c, float units, RM_MapComponent_Excavation owner)
		{
			if (!RimMandrakeFlowWorksSettings.sourceBudgetEnabled)
			{
				return true;
			}
			RM_LiquidBody body = BodyAt(map, c, owner);
			if (body == null || body.limitless)
			{
				return true;
			}
			if (!RM_StockMath.CanDebit(body.limitless, body.stock, units))
			{
				return false;
			}
			body.AddStock(-units);
			return true;
		}

		/// <summary>Give liquid BACK to a body — the receiving half of fill-in
		/// displacement. A limited body accepts up to its capacity and no more;
		/// a limitless body accepts everything, because the reservoir it stands
		/// for is off-map and cannot be overfilled. Returns what was accepted.</summary>
		public float TryCredit(Map map, IntVec3 c, float units, RM_MapComponent_Excavation owner)
		{
			RM_LiquidBody body = BodyAt(map, c, owner);
			if (body == null)
			{
				return 0f;
			}
			float taken = RM_StockMath.CreditAccepted(body.limitless, body.stock, body.capacity, units);
			if (body.limitless)
			{
				return taken;
			}
			body.AddStock(taken);
			return taken;
		}

		/// <summary>Give back whole fill LEVELS — the displacement walk's half of
		/// <see cref="TryCredit"/> (§5, "Filling a canal back in"). Returns the
		/// number of levels accepted, which the caller subtracts from what it
		/// still has to place.
		///
		/// 🔑 WHY THIS EXISTS INSTEAD OF CALLING TryCredit DIRECTLY. The grids
		/// count levels and the stock counts fill-units, and one level is
		/// <paramref name="unitPerLevel"/> units — the very quantity the pulse
		/// debits per level poured out of a source. A walk that handed its level
		/// count to TryCredit would under-credit every liquid whose volumePerTile
		/// is not 1, and would then floor the float it got back, crediting the
		/// body a fraction of a level that no cell ever gave up. Deciding the
		/// whole-level count FIRST and crediting exactly that many levels' worth
		/// keeps both ledgers equal to the unit. The arithmetic is
		/// <see cref="RM_StockMath.CreditableLevels"/>; the credit itself still
		/// routes through TryCredit, so there is one place stock rises.</summary>
		public int CreditLevels(Map map, IntVec3 c, int levels, float unitPerLevel, RM_MapComponent_Excavation owner)
		{
			if (levels <= 0)
			{
				return 0;
			}
			RM_LiquidBody body = BodyAt(map, c, owner);
			if (body == null)
			{
				return 0;
			}
			int take = RM_StockMath.CreditableLevels(
				body.limitless, body.stock, body.capacity, levels, unitPerLevel);
			if (take <= 0)
			{
				return 0;
			}
			// By construction TryCredit accepts this whole amount, so the level
			// count above is what actually landed.
			TryCredit(map, c, take * unitPerLevel, owner);
			return take;
		}

		// ── recession and refill, once per pulse ──────────────────────────

		public void Pulse(Map map, RM_MapComponent_Excavation owner, int pulseTicks)
		{
			if (bodies.Count == 0)
			{
				return;
			}
			// POND_DEPTH §7: switch the pond picture model (migration on, re-lay back off) before any body runs.
			bool depthModelOn = SyncPondDepthModel(map, owner);
			owner.pondStageWritesLeft = RimMandrakeFlowWorksSettings.PondStageWritesPerPulse;
			// LIQUID_BODY_FLUID_IDENTITY_1 step 3: refill and recession read each body's own fluid;
			// ActiveFluid survives only as the default for a body a save left unstamped.
			for (int b = 0; b < bodies.Count; b++)
			{
				RM_LiquidBody body = bodies[b];
				FluidDef fluid = body.fluid ?? owner.ActiveFluid;
				if (body.limitless)
				{
					// Ruling 16's other half: a limitless body never runs down,
					// so it never recedes and never needs refilling. Question 9
					// of §13 ("should a limitless body ever visibly recede?")
					// is answered NO here, which is the simpler reading and the
					// only one consistent with sticky classification.
					continue;
				}
				if (RimMandrakeFlowWorksSettings.refillEnabled)
				{
					Refill(map, body, fluid, pulseTicks);
				}
				if (RimMandrakeFlowWorksSettings.recessionEnabled)
				{
					// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD: a still-water pond keeps one flat surface (StagePond) instead of
					// shedding whole squares; every other body (another liquid, moving water) keeps full-or-empty squares.
					bool depth = depthModelOn && DepthModelApplies(map, body, owner);
					// A full pond with nothing dried has nothing to shed or re-wet: skip its footprint scan (big lakes idle free).
					if (body.receded.Count == 0 && body.stock >= body.capacity && (!depth || !body.depthStaged))
					{
						continue;
					}
					if (depth)
					{
						StagePond(map, body, fluid, owner);
						continue;
					}
					BeginRecession(map, body, owner);
					Recede(map, body, fluid, owner);
					Restore(map, body, owner);
					recession.Clear();
				}
			}
		}

		private void Refill(Map map, RM_LiquidBody body, FluidDef fluid, int pulseTicks)
		{
			if (body.stock >= body.capacity)
			{
				return;
			}
			float oozePerDay = fluid != null ? fluid.groundOozePerSourceCellPerDay : 0.13f;
			float rainFactor = fluid != null ? fluid.rainRefillFactor : 3f;
			// Weather and season are READ from the engine, never guessed:
			// WeatherManager.RainRate (RimWorld/WeatherManager.cs:45) and
			// GenLocalDate.Season(Map) (RimWorld/GenLocalDate.cs:31).
			float rainRate = map.weatherManager != null ? map.weatherManager.RainRate : 0f;
			// Proportional to footprint on purpose (§5's formula): a one-cell
			// seep regains fill-units slowest in absolute terms, which is what a
			// player watching a small pond actually sees.
			float perDay = RM_StockMath.RefillPerDay(
				oozePerDay,
				body.cells.Count,
				rainFactor,
				rainRate,
				BandFor(GenLocalDate.Season(map)),
				RimMandrakeFlowWorksSettings.refillRateMultiplier);
			float gained = RM_StockMath.RefillForPulse(perDay, pulseTicks, GenDate.TicksPerDay);
			body.stock = RM_StockMath.ClampToCapacity(body.stock, gained, body.capacity);
		}

		/// <summary>Ruling 2's season term, mapped onto the Verse-free bands whose
		/// NUMBERS live in <see cref="RM_StockMath"/>. Desert-world shaped: the wet
		/// seasons carry the refill and high summer barely moves it. Only this
		/// switch touches the Verse <see cref="Season"/> enum, which is why it is
		/// here and the arithmetic is not.</summary>
		private static RM_StockMath.SeasonBand BandFor(Season season)
		{
			switch (season)
			{
				case Season.Spring: return RM_StockMath.SeasonBand.Wet;
				case Season.Summer: return RM_StockMath.SeasonBand.Dry;
				case Season.PermanentSummer: return RM_StockMath.SeasonBand.Dry;
				case Season.Winter: return RM_StockMath.SeasonBand.Cool;
				case Season.PermanentWinter: return RM_StockMath.SeasonBand.Cool;
				default: return RM_StockMath.SeasonBand.Neutral;
			}
		}

		/// <summary>POND_ELEVATION_BUILD_LAKES_RUN_DEEP: load this body's wet squares into the recession set for the pulse.
		/// With "deepBedsEnabled" on each square weighs its bed (the drawdown); off, every square weighs one, which is the old
		/// average-per-cell model exactly (all-off degrades to the previous behaviour).</summary>
		private void BeginRecession(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			footprintScratch.Clear();
			for (int i = 0; i < body.cells.Count; i++)
			{
				if (body.cells[i].InBounds(map))
				{
					footprintScratch.Add(map.cellIndices.CellToIndex(body.cells[i]));
				}
			}
			bool beds = RimMandrakeFlowWorksSettings.deepBedsEnabled;
			// POND_RECESSION_STRANDS_CHANNEL_1: cells with a dug cardinal neighbour feed the flow (RM_FlowKernel draws donors
			// over cardinals only) and recede last.
			Func<int, bool> feeds = null;
			if (RimMandrakeFlowWorksSettings.recedeSparesOutflow)
			{
				feeds = i =>
				{
					IntVec3 c = map.cellIndices.IndexToCell(i);
					for (int d = 0; d < 4; d++)
					{
						if (owner.IsExcavated(c + GenAdj.CardinalDirections[d]))
						{
							return true;
						}
					}
					return false;
				};
			}
			recession.Begin(map.Size.x, map.Size.z, footprintScratch,
				i => owner.IsSourceCell(map.cellIndices.IndexToCell(i)),
				beds ? (Func<int, int>)(i => owner.BedLevelsAt(map.cellIndices.IndexToCell(i))) : (i => 1),
				feeds);
		}

		/// <summary>POND_ELEVATION_BUILD_LAKES_RUN_DEEP proof surface (RM_NorthstarProofs.ProofDeepLake): this body's recession and
		/// restore exactly as a pulse runs them (no refill, so the stock the proof set stays put), round after round until
		/// the shape stops moving or 400 rounds. Returns the rounds run. Dev surface only.</summary>
		public int SettleRecession(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			FluidDef fluid = body.fluid ?? owner.ActiveFluid;
			int rounds = 0;
			while (rounds++ < 400)
			{
				int before = body.receded.Count;
				BeginRecession(map, body, owner);
				Recede(map, body, fluid, owner);
				Restore(map, body, owner);
				recession.Clear();
				if (body.receded.Count == before)
				{
					break;
				}
			}
			return rounds;
		}

		/// <summary>The fill-units one unit of recession weight is worth: a bed level (drawdown on), or one square's average
		/// share of the capacity (off, the old model).</summary>
		private float RecessionUnit(RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			return RimMandrakeFlowWorksSettings.deepBedsEnabled ? LevelUnitOf(body, owner) : body.PerCellVolume;
		}

		// ── POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (design/RimMandrake/pond_depth_design_2026-10-16.md) ─────────────

		/// <summary>§6: the depth model applies to a LIMITED body of still WATER only. Limitless bodies never run down (ruling
		/// 16); a current (River tag or MovingFluid, judged on the square's first recorded terrain) has no still-water picture;
		/// another liquid keeps full-or-empty squares until its stage looks are authored (OWED).</summary>
		public bool DepthModelApplies(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			if (body == null || body.limitless)
			{
				return false;
			}
			FluidDef f = body.fluid ?? owner.ActiveFluid;
			if (f != null && f != RimMandrakeFlowWorks_DefOf.RM_Fluid_Water)
			{
				return false;
			}
			if (body.depthExempt < 0)
			{
				body.depthExempt = 0;
				for (int i = 0; i < body.cells.Count && body.depthExempt == 0; i++)
				{
					IntVec3 c = body.cells[i];
					if (!c.InBounds(map))
					{
						continue;
					}
					TerrainDef t = owner.OriginalTerrainAt(c) ?? map.terrainGrid.BaseTerrainAt(c);
					if (t != null && IsMovingWater(t))
					{
						body.depthExempt = 1;
					}
				}
			}
			return body.depthExempt == 0;
		}

		private static TerrainAffordanceDef movingFluid;
		private static bool movingFluidLooked;

		private static bool IsMovingWater(TerrainDef t)
		{
			if (t.tags != null && t.tags.Contains("River"))
			{
				return true;
			}
			if (!movingFluidLooked)
			{
				movingFluidLooked = true;
				movingFluid = DefDatabase<TerrainAffordanceDef>.GetNamedSilentFail("MovingFluid");
			}
			return movingFluid != null && t.affordances != null && t.affordances.Contains(movingFluid);
		}

		// ── WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: the exact kernel's view of a body ─────────────────────────────

		/// <summary>The LIMITED body behind source cell <paramref name="c"/> (its id), or -1 when it never runs down: limitless,
		/// unformed, or the source budget off (a body that is never debited).</summary>
		public int LevelBodyOf(Map map, IntVec3 c, RM_MapComponent_Excavation owner)
		{
			if (!RimMandrakeFlowWorksSettings.sourceBudgetEnabled)
			{
				return -1;
			}
			RM_LiquidBody body = BodyAt(map, c, owner);
			return body == null || body.limitless ? -1 : body.id;
		}

		/// <summary>The body's water in decilitres of LEVELS (a level = 1,000 L in one square). Equal to stockDl when the body's
		/// level unit is 1 (every shipped liquid); otherwise converted, and exact only to the rounding.</summary>
		public long LevelStockDl(RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			if (body == null)
			{
				return 0;
			}
			float lu = LevelUnitOf(body, owner);
			return lu == 1f || !(lu > 0f) ? body.stockDl : (long)Math.Round(body.stockDl / (double)lu);
		}

		public void SetLevelStockDl(RM_LiquidBody body, long levelDl, RM_MapComponent_Excavation owner)
		{
			if (body == null)
			{
				return;
			}
			float lu = LevelUnitOf(body, owner);
			body.stockDl = lu == 1f || !(lu > 0f) ? levelDl : (long)Math.Round(levelDl * (double)lu);
			body.depthStaged = true;   // the surface moved: re-lay its picture
		}

		/// <summary>H[L] over the body's undug footprint (cached a pulse): the exact kernel's pond histogram.</summary>
		public int[] DepthHistogramOf(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			return body == null ? new int[1] : DepthHistogram(map, body, owner);
		}

		/// <summary>H[L] over the body's undug footprint, built at most once a pulse (the kernel asks per donor probe).</summary>
		private int[] DepthHistogram(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			long pulse = owner.PulseCount;
			if (body.depthHist != null && body.depthHistPulse == pulse)
			{
				return body.depthHist;
			}
			body.depthCells.Clear();
			body.depthBeds.Clear();
			for (int i = 0; i < body.cells.Count; i++)
			{
				IntVec3 c = body.cells[i];
				if (!c.InBounds(map) || owner.IsExcavated(c))
				{
					continue;
				}
				body.depthCells.Add(map.cellIndices.CellToIndex(c));
				body.depthBeds.Add(owner.BedLevelsAt(c));
			}
			body.depthHist = RM_PondDepthMath.Histogram(body.depthBeds);
			body.depthHistPulse = pulse;
			return body.depthHist;
		}

		/// <summary>D2: the drawdown s of the pond behind source cell <paramref name="c"/> (its surface is −s); 0 for a
		/// limitless body, another liquid, moving water, or a full pond — so the kernel's head rule is today's rule there.</summary>
		public int DrawdownAt(Map map, IntVec3 c, RM_MapComponent_Excavation owner)
		{
			RM_LiquidBody body = BodyAt(map, c, owner);
			if (body == null || !DepthModelApplies(map, body, owner) || body.stock >= body.capacity)
			{
				return 0;
			}
			int[] h = DepthHistogram(map, body, owner);
			RM_PondDepthMath.Drawdown(RM_BedMath.SupportedLevels(body.stock, LevelUnitOf(body, owner)), h, out int s, out _);
			return s;
		}

		/// <summary>The pond's surface for reports: s, r and the wet count (squares with w ≥ 1 in the picture).</summary>
		public void DepthReport(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner, out int s, out int r, out int wet)
		{
			int[] h = DepthHistogram(map, body, owner);
			RM_PondDepthMath.Drawdown(RM_BedMath.SupportedLevels(body.stock, LevelUnitOf(body, owner)), h, out s, out r);
			wet = (s < h.Length ? (s + 1 < h.Length ? h[s + 1] : 0) : 0) + r;
		}

		/// <summary>§7: model 0 ↔ 1. On (first pulse with "pondDepthEnabled"): every limited water body is marked to re-lay
		/// once (StagePond), the stock untouched. Off: every staged square goes back to its own water, mud times end, and
		/// the old shed/restore takes over from the same stock. Returns whether the depth model runs this pulse.</summary>
		private bool SyncPondDepthModel(Map map, RM_MapComponent_Excavation owner)
		{
			bool on = RimMandrakeFlowWorksSettings.pondDepthEnabled;
			if (on && owner.PondDepthModel == 0)
			{
				for (int b = 0; b < bodies.Count; b++)
				{
					bodies[b].depthStaged = true;
				}
				owner.PondDepthModel = 1;
				Log.Message("[RimMandrake.FlowWorks] pond depth model 0 -> 1: " + bodies.Count + " body(ies) re-laid as one flat surface on their next pulse; stocks unchanged.");
			}
			else if (!on && owner.PondDepthModel == 1)
			{
				int restored = 0;
				for (int b = 0; b < bodies.Count; b++)
				{
					RM_LiquidBody body = bodies[b];
					if (body.limitless)
					{
						continue;
					}
					for (int i = 0; i < body.cells.Count; i++)
					{
						IntVec3 c = body.cells[i];
						if (!c.InBounds(map) || owner.IsExcavated(c) || !owner.IsWaterNow(c))
						{
							continue;
						}
						TerrainDef first = owner.OriginalTerrainAt(c);
						if (first != null && first.IsWater && map.terrainGrid.BaseTerrainAt(c) != first
							&& owner.RestoreOriginalTerrain(c) == RM_RestoreResult.Restored)
						{
							restored++;
						}
					}
					body.depthStaged = true;
				}
				owner.ClearPondMud();
				owner.PondDepthModel = 0;
				Log.Message("[RimMandrake.FlowWorks] pond depth model 1 -> 0: " + restored + " part-depth square(s) laid back to their own water; the old full-or-empty recession takes over.");
			}
			return on;
		}

		/// <summary>§2-§5: lay one pond's picture from its stock. One flat surface s; every square of bed &gt; s shows bed − s
		/// levels (the r-patch one more), the stage terrain for that depth (§4); squares at or above the surface are mud
		/// for the mud time, then lakebed. Ruling 5: a dry square with a pawn or building waits (its band share goes to the
		/// next square; the stock is the truth and is never spent on the picture). Terrain writes are capped per pulse
		/// (pondStageWritesPerPulse); the rest catch up next pulse. The receded list is derived: the squares now dry.</summary>
		private void StagePond(Map map, RM_LiquidBody body, FluidDef fluid, RM_MapComponent_Excavation owner)
		{
			int[] h = DepthHistogram(map, body, owner);
			bool waits = RimMandrakeFlowWorksSettings.refillWaitsForOccupants;
			// WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (owner 2026-10-17, ruled exactly level): the pond's ONE exact surface from
			// its decilitres; every square shows the look for its own true metres of water (a flat 3x3 pond holding 26,000 L is
			// nine squares at 1.44 m, never 8 at 1.5 m and 1 at 1 m). Off: the whole-notch drawdown and its one part-level patch.
			bool exact = RimMandrakeFlowWorksSettings.levelExactEnabled;
			double surface = exact ? RM_LevelSolve.PondSurfaceHeight(h, LevelStockDl(body, owner)) : 0.0;
			int s = 0, r = 0;
			HashSet<int> patch = null;
			if (!exact)
			{
				int levels = RM_BedMath.SupportedLevels(body.stock, LevelUnitOf(body, owner));
				RM_PondDepthMath.Drawdown(levels, h, out s, out r);
				Func<int, bool> eligible = null;
				if (waits && r > 0)
				{
					eligible = i =>
					{
						IntVec3 c = map.cellIndices.IndexToCell(i);
						return owner.IsWaterNow(c) || !Occupied(map, c);
					};
				}
				patch = RM_PondDepthMath.PickPatch(map.Size.x, map.Size.z, body.depthCells, body.depthBeds, s, r, eligible);
			}
			int now = Find.TickManager != null ? Find.TickManager.TicksGame : 0;
			int mudTicks = RimMandrakeFlowWorksSettings.PondMudTicks;
			bool staged = false;
			for (int k = 0; k < body.depthCells.Count; k++)
			{
				int i = body.depthCells[k];
				IntVec3 c = map.cellIndices.IndexToCell(i);
				int bed = body.depthBeds[k];
				RM_PondDepthMath.Stage st;
				int w;
				if (exact)
				{
					double wd = RM_LevelSolve.PondSquareWater(bed, surface);
					w = wd >= 0.5 ? 1 : 0;
					st = RM_PondDepthMath.StageForExact(wd, bed);
				}
				else
				{
					w = RM_PondDepthMath.WaterAt(bed, s, patch.Contains(i));
					st = w > 0 ? RM_PondDepthMath.StageFor(w, bed, false) : RM_PondDepthMath.Stage.Mud;
				}
				bool wetNow = owner.IsWaterNow(c);
				TerrainDef cur = map.terrainGrid.BaseTerrainAt(c);
				if (w > 0)
				{
					TerrainDef want = owner.PondStageTerrain(c, st, fluid);
					if (want == null)
					{
						continue;   // no look for this stage on this map: leave the square as it is
					}
					if (cur != want)
					{
						if (owner.pondStageWritesLeft <= 0)
						{
							staged = true;
							continue;
						}
						// Ruling 5: water returning to a DRY square waits for pawns and buildings; items wash ashore.
						if (!wetNow && waits && !ClearForRefill(map, c, body, owner))
						{
							staged = true;
							continue;
						}
						owner.pondStageWritesLeft--;
						owner.StageNaturalCell(c, want);
					}
					if (st != RM_PondDepthMath.Stage.Original)
					{
						staged = true;
					}
				}
				else if (wetNow)
				{
					if (owner.pondStageWritesLeft <= 0)
					{
						staged = true;
						continue;
					}
					owner.pondStageWritesLeft--;
					if (!owner.MudNaturalCell(c, fluid, now))
					{
						// The liquid authors no receded terrain: the stock still ran down; only the look is missing.
						continue;
					}
					staged = true;
				}
				else if (owner.PondMudTimed(c))
				{
					if (owner.PondMudExpired(c, now, mudTicks) && owner.pondStageWritesLeft > 0)
					{
						owner.pondStageWritesLeft--;
						owner.CrackPondMud(c, fluid);
					}
					else
					{
						staged = true;   // mud still has time to run: keep visiting
					}
				}
			}
			// The receded list is DERIVED now: the footprint squares that are dry (kept in the save so a downgrade loads, §2).
			body.receded.Clear();
			for (int k = 0; k < body.depthCells.Count; k++)
			{
				IntVec3 c = map.cellIndices.IndexToCell(body.depthCells[k]);
				if (!owner.IsWaterNow(c))
				{
					body.receded.Add(c);
				}
			}
			body.depthStaged = staged;
		}

		private static bool Occupied(Map map, IntVec3 c)
		{
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				Thing t = things[i];
				if (t is Pawn || (t.def.category == ThingCategory.Building && !(t is Blueprint)))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Give up cells while the stock no longer covers the wet beds (POND_ELEVATION_BUILD_LAKES_RUN_DEEP §9.3: the
		/// SHALLOWEST bed first, so a lake drops off its rim and shelves to its deep middle), and within one bed depth from
		/// the OUTSIDE IN (§5): fewest same-body wet neighbours first, tie-broken by greatest distance from the centroid, then
		/// by cell index — fully deterministic, so the order survives a save and is identical on every machine.
		///
		/// LIQUID_RECESSION_TOPOLOGY_1: neighbours are counted within THIS body only (another body or fluid touching it no
		/// longer props a cell up), a cell whose removal would split the body is passed over (a local 3x3 test, then a
		/// bounded whole-body check, RM_RecessionSet.Pick), and the live set and neighbour counts are built once per pulse and
		/// updated per removal. Map-indexed arrays (RM_RecessionSet), so a 40,000-square lake costs one list pass per cell.</summary>
		private void Recede(Map map, RM_LiquidBody body, FluidDef fluid, RM_MapComponent_Excavation owner)
		{
			float unit = RecessionUnit(body, owner);
			if (!(unit > 0f))
			{
				return;
			}
			int supported = RM_BedMath.SupportedLevels(body.stock, unit);
			bool keepLast = RimMandrakeFlowWorksSettings.recedeKeepsLastCell;
			bool beds = RimMandrakeFlowWorksSettings.deepBedsEnabled;
			int guard = 0;
			// The live set, not ActiveCellCount: a dug-into or filled-in body cell is neither wet nor receded, and
			// counting it as active would shed one extra wet cell per cut.
			while (RM_BedMath.ShouldShed(recession.WetLevels, recession.Count, supported, body.stock, keepLast) && guard++ < 64)
			{
				int pick = recession.Pick(beds);
				if (pick < 0)
				{
					return;   // nothing sheds without a split this pulse: hold the shape rather than fragment it
				}
				IntVec3 c = map.cellIndices.IndexToCell(pick);
				// 🔴 ONLY record a cell as receded when the terrain write actually
				// happened. DryNaturalCell declines when the fluid authors no
				// recededTerrain, and the cell then stays natural liquid — so
				// recording it anyway would let the picker choose the SAME
				// cell on the next iteration and every pulse after, duplicating
				// it in `receded` without bound, under-counting ActiveCellCount
				// and growing the save forever. Stop instead: nothing this pulse
				// can shed a cell, and a body that cannot recede is a missing
				// visual, not a runaway list.
				if (!owner.DryNaturalCell(c, fluid))
				{
					return;
				}
				body.receded.Add(c);
				recession.Remove(pick);
			}
		}

		/// <summary>Refill puts cells back in REVERSE order, so the body breathes
		/// through the same edge it gave up rather than reappearing somewhere
		/// new. The original terrain comes back with it — the recorded one, not
		/// a guess — which is the whole reason recession is allowed to write
		/// terrain at all.
		///
		/// POND_RETURN_LEG_BUILD_WATER_GOES_HOME:
		/// - Refill guard (owner ruling 5, 2026-10-12: "water waits for people and buildings; items wash ashore"): a cell
		///   holding a pawn or a building is SKIPPED and requeued on top of the stack for the next pulse (GPT #12: never
		///   block the stack); items on it are moved to the nearest dry shore first.
		/// - Checked (GPT #11): a cell leaves the stack only after the terrain write is verified. A cell with no record
		///   can never be restored and is dropped with a warning; a write that did not take is requeued.</summary>
		private void Restore(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			float unit = RecessionUnit(body, owner);
			if (!(unit > 0f))
			{
				return;
			}
			int supported = RM_BedMath.SupportedLevels(body.stock, unit);
			bool keepLast = RimMandrakeFlowWorksSettings.recedeKeepsLastCell;
			bool beds = RimMandrakeFlowWorksSettings.deepBedsEnabled;
			// Count the WET cells and their beds, as Recede does (the recession set after its sheds): a cut body cell is
			// neither wet nor receded, and ActiveCellCount would count it, stopping the refill one cell short per cut.
			long wetLevels = recession.WetLevels;
			int wet = recession.Count;
			int guard = 0;
			List<IntVec3> waiting = null;
			// POND_ELEVATION_BUILD_LAKES_RUN_DEEP: LIFO, and a square re-wets only when its whole bed fits (RM_BedMath.CanRestore),
			// so refilled water always covers the squares it shows, and the pond comes back to its exact old shape.
			while (body.receded.Count > 0 && guard++ < 64)
			{
				IntVec3 c = body.receded[body.receded.Count - 1];
				int bed = beds ? owner.BedLevelsAt(c) : 1;
				if (!owner.IsExcavated(c) && !RM_BedMath.CanRestore(wetLevels, wet, bed, supported, body.stock, keepLast))
				{
					break;
				}
				body.receded.RemoveAt(body.receded.Count - 1);
				// A receded cell dug since it dried belongs to the excavation now: refilling the lake must not write
				// water terrain over a cut whose D is nonzero (GPT FlowWorks review #3). The original-terrain record
				// stays with the excavation, so filling the cut in later restores the lake's own terrain.
				if (owner.IsExcavated(c))
				{
					continue;
				}
				if (RimMandrakeFlowWorksSettings.refillWaitsForOccupants && !ClearForRefill(map, c, body, owner))
				{
					if (waiting == null) waiting = new List<IntVec3>();
					waiting.Add(c);
					continue;
				}
				RM_RestoreResult r = owner.RestoreOriginalTerrain(c);
				if (r == RM_RestoreResult.Restored)
				{
					wet++;
					wetLevels += bed;
				}
				else if (r == RM_RestoreResult.WriteFailed)
				{
					if (waiting == null) waiting = new List<IntVec3>();
					waiting.Add(c);
				}
				else
				{
					Log.WarningOnce("[RimMandrake.FlowWorks] pond #" + body.id + " cell " + c + " has no recorded water terrain and "
						+ "cannot refill; it leaves the refill stack.", 0x6F0D5E7 ^ body.id);
				}
			}
			if (waiting != null)
			{
				// Back on TOP, oldest-first order kept, so the same edge is retried first next pulse.
				for (int i = waiting.Count - 1; i >= 0; i--)
				{
					body.receded.Add(waiting[i]);
				}
			}
		}

		/// <summary>Ruling 5: may <paramref name="c"/> take its water back now? A pawn or a building (frames included; a
		/// blueprint is not a building) makes it wait. Items are washed to the nearest dry shore square that is not part
		/// of any pond; an item that cannot be placed stays and the cell waits.</summary>
		private bool ClearForRefill(Map map, IntVec3 c, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				Thing t = things[i];
				if (t is Pawn || (t.def.category == ThingCategory.Building && !(t is Blueprint)))
				{
					return false;
				}
			}
			List<Thing> items = null;
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def.category == ThingCategory.Item)
				{
					if (items == null) items = new List<Thing>();
					items.Add(things[i]);
				}
			}
			if (items == null)
			{
				return true;
			}
			Predicate<IntVec3> shore = x => x.InBounds(map) && x.Standable(map) && !x.GetTerrain(map).IsWater
				&& IndexedBodyAt(map, x) == null && !owner.IsExcavated(x);
			IntVec3 dry = IntVec3.Invalid;
			foreach (IntVec3 x in GenRadial.RadialCellsAround(c, 12f, false))
			{
				if (shore(x))
				{
					dry = x;
					break;
				}
			}
			if (!dry.IsValid)
			{
				return false;
			}
			for (int i = 0; i < items.Count; i++)
			{
				Thing item = items[i];
				item.DeSpawn();
				if (!GenPlace.TryPlaceThing(item, dry, map, ThingPlaceMode.Near, null, shore))
				{
					GenSpawn.Spawn(item, c, map);
					return false;
				}
			}
			return true;
		}
	}
}
