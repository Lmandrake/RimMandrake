using System.Collections.Generic;
using RimWorld;
using UnityEngine;
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

		private List<RM_LiquidBody> bodies = new List<RM_LiquidBody>();

		private int nextBodyId = 1;

		/// <summary>Derived, never scribed: cell index to body id, rebuilt from
		/// <see cref="bodies"/> on load.</summary>
		private readonly Dictionary<int, int> cellToBody = new Dictionary<int, int>();

		private readonly Dictionary<int, RM_LiquidBody> byId = new Dictionary<int, RM_LiquidBody>();

		private readonly List<IntVec3> fillQueue = new List<IntVec3>();

		private readonly HashSet<IntVec3> fillSeen = new HashSet<IntVec3>();

		public IReadOnlyList<RM_LiquidBody> Bodies => bodies;

		public void ExposeData()
		{
			Scribe_Collections.Look(ref bodies, "RM_liquidBodies", LookMode.Deep);
			Scribe_Values.Look(ref nextBodyId, "RM_nextLiquidBodyId", 1);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && bodies == null)
			{
				bodies = new List<RM_LiquidBody>();
			}
		}

		/// <summary>Rebuild the derived indices. Called from the owner's
		/// FinalizeInit, after the grids exist.</summary>
		public void RebuildIndex(Map map)
		{
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
			fillQueue.Clear();
			fillSeen.Clear();
			List<IntVec3> found = new List<IntVec3>();
			fillQueue.Add(seed);
			fillSeen.Add(seed);
			bool touchesEdge = false;
			bool truncated = false;
			int head = 0;
			while (head < fillQueue.Count)
			{
				IntVec3 c = fillQueue[head++];
				found.Add(c);
				if (c.OnEdge(map))
				{
					touchesEdge = true;
				}
				if (found.Count >= MaxBodyCells)
				{
					truncated = true;
					break;
				}
				for (int i = 0; i < 8; i++)
				{
					IntVec3 n = c + GenAdj.AdjacentCells[i];
					if (!n.InBounds(map) || fillSeen.Contains(n))
					{
						continue;
					}
					fillSeen.Add(n);
					if (owner.IsSourceCell(n))
					{
						fillQueue.Add(n);
					}
				}
			}

			RM_LiquidBody body = new RM_LiquidBody(nextBodyId++);
			body.cells = found;
			body.truncated = truncated;
			// Ruling 16: edge contact AND a minimum size. Both, and only here.
			body.limitless = RimMandrakeFlowWorksSettings.stickyLimitlessEnabled
				&& (truncated || (touchesEdge && found.Count >= RimMandrakeFlowWorksSettings.MinLimitlessBodyCells));
			FluidDef fluid = owner.ActiveFluid;
			float perCell = fluid != null
				? fluid.canalCellsPerSourceCell * fluid.volumePerTile
				: 5f;
			perCell *= RimMandrakeFlowWorksSettings.sourceBudgetMultiplier;
			if (perCell < 0.01f)
			{
				perCell = 0.01f;
			}
			body.capacity = found.Count * perCell;
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
			FluidDef fluid = owner.ActiveFluid;
			float unit = fluid != null ? fluid.volumePerTile : 1f;
			return body.limitless || body.stock >= unit;
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
			if (body.stock < units)
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
			if (body.limitless)
			{
				return units;
			}
			float room = body.capacity - body.stock;
			if (room <= 0f)
			{
				return 0f;
			}
			float taken = Mathf.Min(room, units);
			body.stock += taken;
			return taken;
		}

		// ── recession and refill, once per pulse ──────────────────────────

		public void Pulse(Map map, RM_MapComponent_Excavation owner, int pulseTicks)
		{
			if (bodies.Count == 0)
			{
				return;
			}
			FluidDef fluid = owner.ActiveFluid;
			for (int b = 0; b < bodies.Count; b++)
			{
				RM_LiquidBody body = bodies[b];
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
			float perDay = oozePerDay * body.cells.Count * (1f + rainFactor * rainRate)
				* SeasonFactor(map) * RimMandrakeFlowWorksSettings.refillRateMultiplier;
			// Proportional to footprint on purpose (§5's formula): a one-cell
			// seep regains fill-units slowest in absolute terms, which is what a
			// player watching a small pond actually sees.
			float gained = perDay * (pulseTicks / (float)GenDate.TicksPerDay);
			body.stock = Mathf.Min(body.capacity, body.stock + gained);
		}

		/// <summary>Ruling 2's season term. Desert-world shaped: the wet seasons
		/// carry the refill and high summer barely moves it.</summary>
		private static float SeasonFactor(Map map)
		{
			switch (GenLocalDate.Season(map))
			{
				case Season.Spring: return 1.25f;
				case Season.Summer: return 0.5f;
				case Season.Fall: return 1f;
				case Season.Winter: return 0.75f;
				case Season.PermanentSummer: return 0.5f;
				case Season.PermanentWinter: return 0.75f;
				default: return 1f;
			}
		}

		/// <summary>Give up cells from the OUTSIDE IN while the stock no longer
		/// covers the footprint. Order (§5): fewest same-body wet neighbours
		/// first, tie-broken by greatest distance from the centroid, then by
		/// cell index — fully deterministic, so the order survives a save and is
		/// identical on every machine. That thins the body from its shallow edge
		/// and never fragments it.</summary>
		private void Recede(Map map, RM_LiquidBody body, FluidDef fluid, RM_MapComponent_Excavation owner)
		{
			float perCell = body.PerCellVolume;
			if (perCell <= 0f)
			{
				return;
			}
			int supported = Mathf.FloorToInt(body.stock / perCell);
			int guard = 0;
			while (body.ActiveCellCount > supported && body.ActiveCellCount > 0 && guard++ < 64)
			{
				IntVec3 pick = PickRecedeCell(map, body, owner);
				if (!pick.IsValid)
				{
					return;
				}
				owner.DryNaturalCell(pick, fluid);
				body.receded.Add(pick);
			}
		}

		private IntVec3 PickRecedeCell(Map map, RM_LiquidBody body, RM_MapComponent_Excavation owner)
		{
			IntVec3 centroid = Centroid(body);
			IntVec3 best = IntVec3.Invalid;
			int bestNeighbours = int.MaxValue;
			int bestDist = -1;
			int bestIndex = int.MaxValue;
			for (int i = 0; i < body.cells.Count; i++)
			{
				IntVec3 c = body.cells[i];
				if (!owner.IsSourceCell(c))
				{
					continue; // already receded, or dug into, or filled in
				}
				int neighbours = 0;
				for (int d = 0; d < 8; d++)
				{
					IntVec3 n = c + GenAdj.AdjacentCells[d];
					if (n.InBounds(map) && owner.IsSourceCell(n))
					{
						neighbours++;
					}
				}
				int dist = (c - centroid).LengthHorizontalSquared;
				int idx = map.cellIndices.CellToIndex(c);
				if (neighbours < bestNeighbours
					|| (neighbours == bestNeighbours && dist > bestDist)
					|| (neighbours == bestNeighbours && dist == bestDist && idx < bestIndex))
				{
					bestNeighbours = neighbours;
					bestDist = dist;
					bestIndex = idx;
					best = c;
				}
			}
			return best;
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
			int supported = Mathf.FloorToInt(body.stock / perCell);
			int guard = 0;
			while (body.receded.Count > 0 && body.ActiveCellCount < supported && guard++ < 64)
			{
				IntVec3 c = body.receded[body.receded.Count - 1];
				body.receded.RemoveAt(body.receded.Count - 1);
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
