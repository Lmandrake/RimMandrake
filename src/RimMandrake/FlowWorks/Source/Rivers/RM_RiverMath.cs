using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Rivers
{
	/// <summary>
	/// SURFACE_RIVER_WEIRS_1 (River Works slice 1) — the current's arithmetic, Verse-free so
	/// selftest_riverworks.py can check it without the game.
	///
	/// Lanes and cadences are the sea's (TerminalBiomes' channel current) on purpose: the owner
	/// ruled 2026-10-03 that surface rivers shove "aggressively like the undersea flows".
	/// Centre (chest-deep moving water) = 45 ticks/cell, inescapable; Margin (shallow moving
	/// water) = 90. A live flood promotes Margin to Centre and halves Centre.
	/// </summary>
	public static class RM_RiverMath
	{
		public const int LaneNone = 0;

		public const int LaneMargin = 1;

		public const int LaneCentre = 2;

		/// <summary>Eight compass steps, index 0 = east, counter-clockwise (x, z).</summary>
		public static readonly int[] StepX = { 1, 1, 0, -1, -1, -1, 0, 1 };

		public static readonly int[] StepZ = { 0, 1, 1, 1, 0, -1, -1, -1 };

		/// <summary>Below this flow-vector length a cell has no current. Vanilla's vectors are
		/// ~2 long on river cells (TileMutatorWorker_River samples every 2 cells) and exactly 0
		/// off them.</summary>
		public const float MinFlow = 0.1f;

		/// <summary>Quantise a flow vector to a compass index 0..7, or -1 for no current.</summary>
		public static int Quantise(float dx, float dz)
		{
			if (float.IsNaN(dx) || float.IsNaN(dz) || dx * dx + dz * dz < MinFlow * MinFlow)
			{
				return -1;
			}
			double deg = Math.Atan2(dz, dx) * 180.0 / Math.PI;
			int sector = (int)Math.Round(deg / 45.0);
			return ((sector % 8) + 8) % 8;
		}

		/// <summary>PROVISIONAL: how much harder a river shoves for its size (owner card 1:
		/// "bigger rivers shove harder"). Vanilla widthOnMap: creek 4, river 6, large 14, huge 30.
		/// (width/6)^0.75 clamped 0.5..2.5 -> creek 0.74, river 1.0, large 1.89, huge 2.5.</summary>
		public static float SizeFactor(float widthOnMap)
		{
			if (!(widthOnMap > 0f))
			{
				return 1f;
			}
			float f = (float)Math.Pow(widthOnMap / 6f, 0.75);
			return f < 0.5f ? 0.5f : (f > 2.5f ? 2.5f : f);
		}

		/// <summary>Ticks until the next one-cell shove.</summary>
		public static int Cadence(int lane, bool surge, bool isPawn, float strength, float sizeFactor,
			int centreTicks, int marginTicks, float itemFactor)
		{
			if (lane == LaneNone)
			{
				return int.MaxValue;
			}
			bool centre = lane == LaneCentre || surge;
			float ticks = centre ? centreTicks : marginTicks;
			if (surge && lane == LaneCentre)
			{
				ticks /= 2f;
			}
			if (!isPawn)
			{
				ticks *= itemFactor > 0f ? itemFactor : 1f;
			}
			float div = Math.Max(0.05f, strength) * Math.Max(0.05f, sizeFactor);
			int t = (int)Math.Round(ticks / div);
			return Math.Max(1, t);
		}

		/// <summary>A weir's slack pool drops one lane: Centre -> Margin, Margin -> none.</summary>
		public static int PoolLane(int lane)
		{
			return lane == LaneCentre ? LaneMargin : LaneNone;
		}

		/// <summary>Signed distance of offset (dx, dz) along compass direction dir (positive =
		/// downstream). Orders a breach's stake cascade.</summary>
		public static float DownstreamDistance(int dx, int dz, int dir)
		{
			float ux = StepX[dir];
			float uz = StepZ[dir];
			float len = (float)Math.Sqrt(ux * ux + uz * uz);
			return (dx * ux + dz * uz) / len;
		}

		/// <summary>Effective Centre behaviour (inescapable, hazards apply).</summary>
		public static bool BehavesAsCentre(int lane, bool surge)
		{
			return lane == LaneCentre || (surge && lane == LaneMargin);
		}

		// ── Mod Settings gates (RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED) ─────
		// Each Rivers toggle's decision, Verse-free, so the SelfTest can flip the setting and require the
		// outcome to change (SelfTest/RiverSwitchFlipChecks.cs also requires each call site to pass the setting).

		/// <summary>The surface current runs (master switch + current switch).</summary>
		public static bool CurrentOn(bool riverWorksEnabled, bool surfaceCurrentEnabled)
		{
			return riverWorksEnabled && surfaceCurrentEnabled;
		}

		/// <summary>The bank works run (master switch + works switch).</summary>
		public static bool WorksOn(bool riverWorksEnabled, bool bankWorksEnabled)
		{
			return riverWorksEnabled && bankWorksEnabled;
		}

		/// <summary>A live flood makes the river fiercer only when the surge setting is on.</summary>
		public static bool Surges(bool floodSurgeEnabled, bool floodActive)
		{
			return floodSurgeEnabled && floodActive;
		}

		/// <summary>Which vanilla floods count as a flood for the surge (design §3.6).</summary>
		public static bool FloodCounts(bool countSeasonalFloods, bool seasonalPresent,
			bool countTorrentialRainFloods, bool torrentialPresent)
		{
			return (countSeasonalFloods && seasonalPresent) || (countTorrentialRainFloods && torrentialPresent);
		}

		/// <summary>The river-size factor the cadence uses: the river's own, or 1 when size scaling is off.</summary>
		public static float EffectiveSizeFactor(bool scaleWithRiverSize, float sizeFactor)
		{
			return scaleWithRiverSize ? sizeFactor : 1f;
		}

		/// <summary>Design §3.1, who the current may carry, before the ford/arrest test. Never buildings,
		/// fliers or river-native races. The player's own humanlikes (and prisoners/guests) always; animals
		/// only with carryAnimals; strangers' humanlikes only with carryStrangers; items and corpses only
		/// with carryItems.</summary>
		public static bool CarriedKind(bool isBuilding, bool isPawn, bool flying, bool riverNative, bool players,
			bool animal, bool carryAnimals, bool carryStrangers, bool carryItems)
		{
			if (isBuilding)
			{
				return false;
			}
			if (!isPawn)
			{
				return carryItems;
			}
			if (flying || riverNative)
			{
				return false;
			}
			if (animal)
			{
				return carryAnimals;
			}
			return players || carryStrangers;
		}

		/// <summary>Bruise/drop rolls happen only on a shove that behaves as the fast lane, with hazards on.</summary>
		public static bool HazardsApply(bool behavesAsCentre, bool crossingHazardsEnabled)
		{
			return behavesAsCentre && crossingHazardsEnabled;
		}

		/// <summary>The extra perceived path cost undrafted pawns see on a river terrain: fast lane, edge lane,
		/// or 0 when avoidance (or the current, or the master switch) is off.</summary>
		public static int AvoidanceCost(bool riverWorksEnabled, bool surfaceCurrentEnabled, bool pathfinderAvoidsCurrents,
			bool fastLane, int extraFastLane, int extraEdgeLane)
		{
			if (!(riverWorksEnabled && surfaceCurrentEnabled && pathfinderAvoidsCurrents))
			{
				return 0;
			}
			return fastLane ? extraFastLane : extraEdgeLane;
		}

		/// <summary>A weir's drift roll chance per catch, or -1 when drift catching is off (no roll at all).</summary>
		public static float DriftRollChance(bool weirCatchesDrift, float weirDriftChance)
		{
			if (!weirCatchesDrift)
			{
				return -1f;
			}
			return weirDriftChance < 0f ? 0f : (weirDriftChance > 1f ? 1f : weirDriftChance);
		}

		/// <summary>A breach's stake cascade: the snap order (cells) of a stake at offset (dx, dz) from the
		/// weir, nearest-downstream first; -1 for a stake upstream of the weir (the breach does not reach it).
		/// With no flow direction (dir &lt; 0) the plain distance orders it.</summary>
		public static float StakeSnapOrder(int dx, int dz, int dir)
		{
			if (dir < 0)
			{
				return (float)Math.Sqrt(dx * dx + dz * dz);
			}
			float order = DownstreamDistance(dx, dz, dir);
			if (order < -1f)
			{
				return -1f;
			}
			return order < 0f ? 0f : order;
		}

		/// <summary>WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE: a neighbour is upstream when the step from it onto the cell
		/// points along the local flow within ~67.5 degrees (cos 67.5 = 0.383). A purely lateral or downstream
		/// neighbour never qualifies, so the walk cannot turn back on itself or cross the river.</summary>
		public const float UpstreamMinCos = 0.38f;

		/// <summary>One upstream step from (x, z): the in-flow neighbour (dirAt &gt;= 0) whose step onto (x, z) best
		/// aligns with the local flow, the sum of the unit vectors of the cell's own direction (when it has one) and
		/// the neighbour's. Returns the index 0..7 into StepX/StepZ of the offset to that neighbour, or -1.
		/// The old rule wanted a neighbour whose QUANTISED direction stepped exactly onto the cell (else the cell
		/// straight behind it): on a bank-edge lane where the 8-way quantisation of vanilla's along-river flow
		/// rarely lines up that way, and the cell behind is often bank, it found nothing and the weir pooled 0
		/// cells. `skip` rejects a neighbour (the walk's own path).</summary>
		public static int UpstreamStep(int x, int z, Func<int, int, int> dirAt, Func<int, int, bool> skip = null)
		{
			int curDir = dirAt(x, z);
			int best = -1;
			double bestScore = UpstreamMinCos;
			for (int i = 0; i < 8; i++)
			{
				int nx = x + StepX[i];
				int nz = z + StepZ[i];
				int d = dirAt(nx, nz);
				if (d < 0 || (skip != null && skip(nx, nz)))
				{
					continue;
				}
				double fx = UnitX(d);
				double fz = UnitZ(d);
				if (curDir >= 0)
				{
					fx += UnitX(curDir);
					fz += UnitZ(curDir);
				}
				double fl = Math.Sqrt(fx * fx + fz * fz);
				if (fl < 1e-6)
				{
					continue; // opposed directions: no local flow to be upstream of
				}
				// the step from the neighbour onto the cell is -(StepX[i], StepZ[i])
				double score = (-StepX[i] * fx - StepZ[i] * fz) / (fl * Math.Sqrt(StepX[i] * StepX[i] + StepZ[i] * StepZ[i]));
				if (score >= bestScore + 1e-9 || (best < 0 && score >= bestScore))
				{
					best = i;
					bestScore = score;
				}
			}
			return best;
		}

		/// <summary>The weir's slack-pool spine: up to `length` cells walked upstream from (x0, z0) by UpstreamStep,
		/// never revisiting a cell. Calls visit(x, z) for each spine cell (not the start). Returns the steps taken.</summary>
		public static int UpstreamWalk(int x0, int z0, int length, Func<int, int, int> dirAt, Action<int, int> visit)
		{
			HashSet<long> path = new HashSet<long> { Key(x0, z0) };
			int x = x0;
			int z = z0;
			int k = 0;
			for (; k < length; k++)
			{
				int i = UpstreamStep(x, z, dirAt, (nx, nz) => path.Contains(Key(nx, nz)));
				if (i < 0)
				{
					break;
				}
				x += StepX[i];
				z += StepZ[i];
				path.Add(Key(x, z));
				visit(x, z);
			}
			return k;
		}

		private static long Key(int x, int z) => ((long)x << 32) ^ (uint)z;

		private static double UnitX(int dir) => (dir & 1) == 0 ? StepX[dir] : StepX[dir] * 0.70710678;

		private static double UnitZ(int dir) => (dir & 1) == 0 ? StepZ[dir] : StepZ[dir] * 0.70710678;

		/// <summary>P10 (WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST): the breach wash's per-stack rule, Verse-free so the
		/// SelfTest can drive the drop-failed path with fake things. Each live held stack is despawned and placed
		/// near the strand cell; when placement fails and the stack still exists it is respawned where it sat
		/// (never orphaned unspawned). A partial merge into strand stacks before the failure still counts as moved.
		/// Returns how many stacks moved.</summary>
		public static int WashHeld<T, P>(IList<T> held, Func<T, bool> live, Func<T, P> position, Func<T, int> stack,
			Action<T> despawn, Func<T, bool> tryPlace, Func<T, bool> destroyed, Action<T, P> respawn)
		{
			int moved = 0;
			for (int i = 0; i < held.Count; i++)
			{
				T t = held[i];
				if (!live(t))
				{
					continue;
				}
				P from = position(t);
				int before = stack(t);
				despawn(t);
				if (tryPlace(t))
				{
					moved++;
				}
				else if (!destroyed(t))
				{
					respawn(t, from);
					if (stack(t) < before)
					{
						moved++;
					}
				}
			}
			return moved;
		}
}
}
