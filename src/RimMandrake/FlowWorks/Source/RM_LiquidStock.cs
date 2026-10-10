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
		/// number the sentinel already answers.</summary>
		private const int MaxBodyCells = 4000;

		/// <summary>Used only when a body forms with no active FluidDef at all —
		/// the same 5 the field defaults to, so a def-less map still gets §5's
		/// budget rather than a capacity of zero.</summary>
		private const float DefaultCanalCellsPerSourceCell = 5f;

		private List<RM_LiquidBody> bodies = new List<RM_LiquidBody>();

		private int nextBodyId = 1;

		/// <summary>Derived, never scribed: cell index to body id, rebuilt from
		/// <see cref="bodies"/> on load.</summary>
		private readonly Dictionary<int, int> cellToBody = new Dictionary<int, int>();

		private readonly Dictionary<int, RM_LiquidBody> byId = new Dictionary<int, RM_LiquidBody>();

		private readonly List<int> fillQueue = new List<int>();
		private readonly List<int> fillFound = new List<int>();

		private readonly HashSet<int> fillSeen = new HashSet<int>();

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
		/// classifying it on first contact. Returns null when the cell is not a
		/// natural source at all.
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
			int ownedId = RM_FlowKernel.CollectBody(sizeX, map.Size.z, map.cellIndices.CellToIndex(seed),
				i => owner.IsSourceCell(map.cellIndices.IndexToCell(i)),
				i => cellToBody.TryGetValue(i, out int id) && byId.ContainsKey(id) ? id : -1,
				MaxBodyCells, fillFound, fillQueue, fillSeen, out bool touchesEdge, out bool truncated,
				i => (RM_FluidIdentity.FluidOfTerrain(map.terrainGrid.TerrainAt(i)) ?? RimMandrakeFlowWorks_DefOf.RM_Fluid_Water) == seedFluid);
			if (ownedId >= 0)
			{
				for (int f = 0; f < fillFound.Count; f++)
				{
					cellToBody[fillFound[f]] = ownedId;
				}
				return byId[ownedId];
			}
			List<IntVec3> found = new List<IntVec3>(fillFound.Count);
			for (int f = 0; f < fillFound.Count; f++)
			{
				found.Add(map.cellIndices.IndexToCell(fillFound[f]));
			}
			RM_LiquidBody body = new RM_LiquidBody(nextBodyId++);
			body.cells = found;
			body.truncated = truncated;
			// Ruling 16: edge contact AND a minimum size. Both, and only here.
			body.limitless = RM_StockMath.IsLimitless(
				RimMandrakeFlowWorksSettings.stickyLimitlessEnabled,
				truncated,
				touchesEdge,
				found.Count,
				RimMandrakeFlowWorksSettings.MinLimitlessBodyCells);
			body.fluid = RM_FluidIdentity.FluidOfTerrain(map.terrainGrid.TerrainAt(seed)) ?? RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;
			// LIQUID_BODY_FLUID_IDENTITY_1 step 3: capacity is the body's OWN fluid's, never the map's.
			FluidDef fluid = body.fluid;
			body.capacity = RM_StockMath.BodyCapacity(
				found.Count,
				fluid != null ? fluid.canalCellsPerSourceCell : DefaultCanalCellsPerSourceCell,
				fluid != null ? fluid.volumePerTile : 1f,
				RimMandrakeFlowWorksSettings.sourceBudgetMultiplier);
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

		// ── the 5:1 budget in use ─────────────────────────────────────────

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
			body.stock -= units;
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
			body.stock += taken;
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
					Recede(map, body, fluid, owner);
					Restore(map, body, owner);
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

		/// <summary>Give up cells from the OUTSIDE IN while the stock no longer
		/// covers the footprint. Order (§5): fewest same-body wet neighbours
		/// first, tie-broken by greatest distance from the centroid, then by
		/// cell index — fully deterministic, so the order survives a save and is
		/// identical on every machine. That thins the body from its shallow edge.
		///
		/// LIQUID_RECESSION_TOPOLOGY_1: neighbours are counted within THIS body
		/// only (another body or fluid touching it no longer props a cell up), a
		/// cell whose removal would split the body is passed over (a local 3x3
		/// test, then a bounded whole-body check, see <see cref="PickRecedeCell"/>),
		/// and the live set and neighbour counts are built once per pulse and
		/// updated per removal instead of rescanning the footprint ×8 each time.</summary>
		private void Recede(Map map, RM_LiquidBody body, FluidDef fluid, RM_MapComponent_Excavation owner)
		{
			float perCell = body.PerCellVolume;
			if (perCell <= 0f)
			{
				return;
			}
			int supported = RM_StockMath.SupportedCellsKeepingLast(body.stock, perCell, RimMandrakeFlowWorksSettings.recedeKeepsLastCell);
			if (body.ActiveCellCount <= supported)
			{
				return;
			}
			IntVec3 centroid = Centroid(body);   // body.cells is fixed for the whole loop: compute once
			Dictionary<IntVec3, int> live = new Dictionary<IntVec3, int>(body.cells.Count);
			for (int i = 0; i < body.cells.Count; i++)
			{
				IntVec3 c = body.cells[i];
				if (owner.IsSourceCell(c))
				{
					live[c] = 0;   // already receded, dug into or filled in cells are not live
				}
			}
			List<IntVec3> keys = new List<IntVec3>(live.Keys);
			for (int i = 0; i < keys.Count; i++)
			{
				int n = 0;
				for (int d = 0; d < 8; d++)
				{
					if (live.ContainsKey(keys[i] + GenAdj.AdjacentCells[d]))
					{
						n++;
					}
				}
				live[keys[i]] = n;
			}
			// POND_RECESSION_STRANDS_CHANNEL_1: cells with a dug cardinal neighbour feed the flow (RM_FlowKernel
			// draws donors over cardinals only) and recede last. Excavation does not change inside this loop.
			HashSet<IntVec3> outflow = null;
			if (RimMandrakeFlowWorksSettings.recedeSparesOutflow)
			{
				for (int i = 0; i < keys.Count; i++)
				{
					for (int d = 0; d < 4; d++)
					{
						if (owner.IsExcavated(keys[i] + GenAdj.CardinalDirections[d]))
						{
							if (outflow == null) outflow = new HashSet<IntVec3>();
							outflow.Add(keys[i]);
							break;
						}
					}
				}
			}
			int guard = 0;
			while (body.ActiveCellCount > supported && body.ActiveCellCount > 0 && guard++ < 64)
			{
				IntVec3 pick = PickRecedeCell(map, body, live, centroid, outflow);
				if (!pick.IsValid)
				{
					return;
				}
				// 🔴 ONLY record a cell as receded when the terrain write actually
				// happened. DryNaturalCell declines when the fluid authors no
				// recededTerrain, and the cell then stays natural liquid — so
				// recording it anyway would let PickRecedeCell choose the SAME
				// cell on the next iteration and every pulse after, duplicating
				// it in `receded` without bound, under-counting ActiveCellCount
				// and growing the save forever. Stop instead: nothing this pulse
				// can shed a cell, and a body that cannot recede is a missing
				// visual, not a runaway list.
				if (!owner.DryNaturalCell(pick, fluid))
				{
					return;
				}
				body.receded.Add(pick);
				live.Remove(pick);
				for (int d = 0; d < 8; d++)
				{
					IntVec3 n = pick + GenAdj.AdjacentCells[d];
					if (live.TryGetValue(n, out int cnt))
					{
						live[n] = cnt - 1;
					}
				}
			}
		}

		// Ring order N, NE, E, SE, S, SW, W, NW — RM_StockMath.LocalRemovalKeepsConnected's bit order.
		private static readonly IntVec3[] RingOffsets =
		{
			new IntVec3(0, 0, 1), new IntVec3(1, 0, 1), new IntVec3(1, 0, 0), new IntVec3(1, 0, -1),
			new IntVec3(0, 0, -1), new IntVec3(-1, 0, -1), new IntVec3(-1, 0, 0), new IntVec3(-1, 0, 1),
		};

		private const int GlobalSplitChecks = 4;

		private IntVec3 PickRecedeCell(Map map, RM_LiquidBody body, Dictionary<IntVec3, int> live, IntVec3 centroid,
			HashSet<IntVec3> outflow)
		{
			IntVec3 best = IntVec3.Invalid;
			bool bestOutflow = true;
			int bestNeighbours = int.MaxValue;
			int bestDist = -1;
			int bestIndex = int.MaxValue;
			List<IntVec3> unsafeLocal = null;
			foreach (KeyValuePair<IntVec3, int> kv in live)
			{
				IntVec3 c = kv.Key;
				int dist = (c - centroid).LengthHorizontalSquared;
				int idx = map.cellIndices.CellToIndex(c);
				bool feeds = outflow != null && outflow.Contains(c);
				if (!RM_StockMath.PrefersCandidate(feeds, kv.Value, dist, idx, bestOutflow, bestNeighbours, bestDist, bestIndex))
				{
					continue;
				}
				if (!RM_StockMath.LocalRemovalKeepsConnected(RingMask(live, c)))
				{
					if (unsafeLocal == null) unsafeLocal = new List<IntVec3>();
					unsafeLocal.Add(c);
					continue;
				}
				bestOutflow = feeds;
				bestNeighbours = kv.Value;
				bestDist = dist;
				bestIndex = idx;
				best = c;
			}
			if (best.IsValid || unsafeLocal == null)
			{
				return best;
			}
			// Every candidate failed the local test (a one-wide ring or snake): a local split can still
			// close around a longer path, so check a few of the best candidates against the whole body.
			unsafeLocal.Sort((a, b) =>
			{
				int ia = map.cellIndices.CellToIndex(a), ib = map.cellIndices.CellToIndex(b);
				bool oa = outflow != null && outflow.Contains(a), ob = outflow != null && outflow.Contains(b);
				if (RM_StockMath.PrefersCandidate(oa, live[a], (a - centroid).LengthHorizontalSquared, ia,
					ob, live[b], (b - centroid).LengthHorizontalSquared, ib)) return -1;
				return a == b ? 0 : 1;
			});
			int before = ComponentCount(live, IntVec3.Invalid);
			for (int i = 0; i < unsafeLocal.Count && i < GlobalSplitChecks; i++)
			{
				if (ComponentCount(live, unsafeLocal[i]) <= before)
				{
					return unsafeLocal[i];
				}
			}
			// Nothing sheds without a split this pulse: hold the shape rather than fragment it.
			return IntVec3.Invalid;
		}

		private static int RingMask(Dictionary<IntVec3, int> live, IntVec3 c)
		{
			int mask = 0;
			for (int k = 0; k < 8; k++)
			{
				if (live.ContainsKey(c + RingOffsets[k]))
				{
					mask |= 1 << k;
				}
			}
			return mask;
		}

		/// <summary>8-way components of the live set with <paramref name="without"/> left out.</summary>
		private static int ComponentCount(Dictionary<IntVec3, int> live, IntVec3 without)
		{
			HashSet<IntVec3> seen = new HashSet<IntVec3>();
			Queue<IntVec3> q = new Queue<IntVec3>();
			int comps = 0;
			foreach (IntVec3 s in live.Keys)
			{
				if (s == without || seen.Contains(s))
				{
					continue;
				}
				comps++;
				seen.Add(s);
				q.Enqueue(s);
				while (q.Count > 0)
				{
					IntVec3 c = q.Dequeue();
					for (int d = 0; d < 8; d++)
					{
						IntVec3 n = c + GenAdj.AdjacentCells[d];
						if (n != without && live.ContainsKey(n) && seen.Add(n))
						{
							q.Enqueue(n);
						}
					}
				}
			}
			return comps;
		}

		/// <summary>Refill puts cells back in REVERSE order, so the body breathes
		/// through the same edge it gave up rather than reappearing somewhere
		/// new. The original terrain comes back with it — the recorded one, not
		/// a guess — which is the whole reason recession is allowed to write
		/// terrain at all.</summary>
		private void Restore(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			float perCell = body.PerCellVolume;
			if (perCell <= 0f)
			{
				return;
			}
			int supported = RM_StockMath.SupportedCellsKeepingLast(body.stock, perCell, RimMandrakeFlowWorksSettings.recedeKeepsLastCell);
			int guard = 0;
			while (body.receded.Count > 0 && body.ActiveCellCount < supported && guard++ < 64)
			{
				IntVec3 c = body.receded[body.receded.Count - 1];
				body.receded.RemoveAt(body.receded.Count - 1);
				// A receded cell dug since it dried belongs to the excavation now: refilling the lake must not write
				// water terrain over a cut whose D is nonzero (GPT FlowWorks review #3). The original-terrain record
				// stays with the excavation, so filling the cut in later restores the lake's own terrain.
				if (owner.IsExcavated(c))
				{
					continue;
				}
				owner.RestoreOriginalTerrain(c);
			}
		}

		private static IntVec3 Centroid(RM_LiquidBody body)
		{
			if (body.cells.Count == 0)
			{
				return IntVec3.Invalid;
			}
			long x = 0;
			long z = 0;
			for (int i = 0; i < body.cells.Count; i++)
			{
				x += body.cells[i].x;
				z += body.cells[i].z;
			}
			return new IntVec3((int)(x / body.cells.Count), 0, (int)(z / body.cells.Count));
		}
	}
}
