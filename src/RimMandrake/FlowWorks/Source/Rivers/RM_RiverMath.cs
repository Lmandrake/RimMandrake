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
			return AlignedStep(x, z, dirAt(x, z), -1, dirAt, skip);
		}

		/// <summary>WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME: UpstreamStep's mirror. One downstream step from (x, z): the in-flow
		/// neighbour whose step FROM the cell best aligns (within ~67.5 degrees) with the local flow, the sum of the unit
		/// vectors of the cell's own direction (when it has one) and the neighbour's. Returns the index into StepX/StepZ,
		/// or -1.</summary>
		public static int DownstreamStep(int x, int z, Func<int, int, int> dirAt, Func<int, int, bool> skip = null)
		{
			return AlignedStep(x, z, dirAt(x, z), 1, dirAt, skip);
		}

		/// <summary>sign -1: the step from the neighbour onto the cell runs with the flow (upstream neighbour);
		/// sign +1: the step from the cell onto the neighbour runs with the flow (downstream neighbour).</summary>
		private static int AlignedStep(int x, int z, int curDir, int sign, Func<int, int, int> dirAt, Func<int, int, bool> skip)
		{
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
					continue; // opposed directions: no local flow to follow either way
				}
				// upstream: the step from the neighbour onto the cell is -(StepX[i], StepZ[i]); downstream: +(StepX[i], StepZ[i])
				double score = sign * (StepX[i] * fx + StepZ[i] * fz) / (fl * Math.Sqrt(StepX[i] * StepX[i] + StepZ[i] * StepZ[i]));
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

		/// <summary>The breach wash's run: up to `length` cells walked DOWNSTREAM from (x0, z0) by DownstreamStep, never
		/// revisiting a cell. Calls visit(x, z) for each cell (not the start); ends at (x, z). Returns the steps taken.</summary>
		public static int DownstreamWalk(int x0, int z0, int length, Func<int, int, int> dirAt, out int x, out int z,
			Action<int, int> visit = null)
		{
			HashSet<long> path = new HashSet<long> { Key(x0, z0) };
			x = x0;
			z = z0;
			int k = 0;
			for (; k < length; k++)
			{
				int i = DownstreamStep(x, z, dirAt, (nx, nz) => path.Contains(Key(nx, nz)));
				if (i < 0)
				{
					break;
				}
				x += StepX[i];
				z += StepZ[i];
				path.Add(Key(x, z));
				visit?.Invoke(x, z);
			}
			return k;
		}

		/// <summary>How far past the weir's held-catch radius the strand cell must lie, so a Near placement that
		/// spills onto the strand's 8 neighbours (at most ~1.42 cells) still lands outside it.</summary>
		public const float WashStrandMargin = 1.5f;

		/// <summary>How far from the walk's end the strand search looks.</summary>
		public const int WashSearchRadius = 10;

		private static readonly int[][] WashOffsets = BuildWashOffsets();

		private static int[][] BuildWashOffsets()
		{
			List<int[]> o = new List<int[]>();
			int r = WashSearchRadius;
			for (int dx = -r; dx <= r; dx++)
				for (int dz = -r; dz <= r; dz++)
					if (dx * dx + dz * dz <= r * r)
						o.Add(new[] { dx, dz });
			// nearest first; ties broken by a fixed order so the strand is deterministic
			o.Sort((a, b) =>
			{
				int c = (a[0] * a[0] + a[1] * a[1]).CompareTo(b[0] * b[0] + b[1] * b[1]);
				if (c != 0) return c;
				c = a[0].CompareTo(b[0]);
				return c != 0 ? c : a[1].CompareTo(b[1]);
			});
			return o.ToArray();
		}

		/// <summary>WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME (owner ruling 4: the held catch rides the current a few cells and
		/// strands on the nearest bank). The catch is walked `steps` cells downstream from the wet cell (DownstreamWalk),
		/// then strands on the nearest standable no-flow cell to the walk's end that lies OUTSIDE the weir's held disc
		/// (farther than heldRadius + WashStrandMargin from the weir at (weirX, weirZ)) and downstream of the weir, within
		/// 45 degrees of the wet cell's flow (along &gt;= across, along &gt;= 1); failing that, any cell outside the disc.
		/// Before this, the walk followed the quantised direction blindly and stopped at the first cell with none (live
		/// 2026-10-12: one cell, next to the weir), and nothing kept the strand out of the disc, so HeldCatch() still
		/// counted every stack. Near placement spilling past the strand's own neighbours (all occupied) can still land
		/// a stack closer; the margin covers only the first ring.
		/// False when the wet cell has no flow or nothing in reach qualifies.</summary>
		public static bool WashStrand(int wetX, int wetZ, int weirX, int weirZ, int steps, float heldRadius,
			Func<int, int, int> dirAt, Func<int, int, bool> standable, out int sx, out int sz)
		{
			sx = sz = 0;
			int flowDir = dirAt(wetX, wetZ);
			if (flowDir < 0)
			{
				return false;
			}
			DownstreamWalk(wetX, wetZ, Math.Max(0, steps), dirAt, out int ex, out int ez);
			float minD = heldRadius + WashStrandMargin;
			float minD2 = minD * minD;
			bool haveAny = false;
			int ax = 0, az = 0;
			for (int i = 0; i < WashOffsets.Length; i++)
			{
				int cx = ex + WashOffsets[i][0];
				int cz = ez + WashOffsets[i][1];
				int dx = cx - weirX;
				int dz = cz - weirZ;
				if (dx * dx + dz * dz <= minD2 || dirAt(cx, cz) >= 0 || !standable(cx, cz))
				{
					continue;
				}
				float along = DownstreamDistance(dx, dz, flowDir);
				float across = Math.Abs(DownstreamDistance(dx, dz, (flowDir + 2) % 8));
				if (along >= 1f && along >= across)
				{
					sx = cx;
					sz = cz;
					return true;
				}
				if (!haveAny)
				{
					haveAny = true;
					ax = cx;
					az = cz;
				}
			}
			sx = ax;
			sz = az;
			return haveAny;
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

		// ── RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS (owner 2026-10-16, by card: "Weirs join into one continuous wall") ──
		// A weir section is 1x2. The first section straddles the bank (one moving-water cell, one solid); a further section
		// may stand wholly in moving water when it continues a run end-to-end along the same axis, so a chain of sections
		// spans the river bank to bank. Verse-free so WeirPoolChecks can drive it.

		/// <summary>Placement rule: a bank straddler (1 water + 1 bank) always; an all-water section only when it continues a
		/// run (a weir, blueprint or frame on the same axis touches one of its ends).</summary>
		public static bool WeirPlacementOk(int waterCells, int bankCells, bool continuesRun)
		{
			if (waterCells == 1 && bankCells == 1)
			{
				return true;
			}
			return waterCells == 2 && bankCells == 0 && continuesRun;
		}

		/// <summary>The joined run holding <paramref name="start"/>: every section reachable through end-to-end neighbours
		/// (breadth-first, start first), capped at <paramref name="cap"/> sections.</summary>
		public static List<T> WeirRun<T>(T start, Func<T, IEnumerable<T>> neighbours, int cap)
		{
			List<T> run = new List<T> { start };
			HashSet<T> seen = new HashSet<T> { start };
			for (int i = 0; i < run.Count && run.Count < cap; i++)
			{
				foreach (T n in neighbours(run[i]))
				{
					if (n != null && seen.Add(n))
					{
						run.Add(n);
						if (run.Count >= cap)
						{
							break;
						}
					}
				}
			}
			return run;
		}

		/// <summary>The run's head - the one section that rolls the catch and holds it on its bank end: the lowest id among
		/// bank-anchored sections, else the lowest id (a run cut off from both banks still catches once).</summary>
		public static T WeirRunHead<T>(IList<T> run, Func<T, bool> anchored, Func<T, int> id)
		{
			T best = default(T);
			bool bestAnchored = false;
			int bestId = int.MaxValue;
			for (int i = 0; i < run.Count; i++)
			{
				bool a = anchored(run[i]);
				int k = id(run[i]);
				if ((a && !bestAnchored) || (a == bestAnchored && k < bestId))
				{
					best = run[i];
					bestAnchored = a;
					bestId = k;
				}
			}
			return best;
		}

		/// <summary>The run's slack pool stands only while every section holds: one breached or broken section is a gap,
		/// and a gap leaks (the stake-line's rule).</summary>
		public static bool WeirRunHolds(IList<bool> sectionSound)
		{
			for (int i = 0; i < sectionSound.Count; i++)
			{
				if (!sectionSound[i])
				{
					return false;
				}
			}
			return sectionSound.Count > 0;
		}

		/// <summary>The art's facing (Rot4 int: 0 N, 1 E, 2 S, 3 W) from the section's axis and the current at its wet end:
		/// the downstream side carries the spill face. Horizontal wall (E/W rotation, runs along x): downstream south shows
		/// the spill face to the camera (East art), downstream north shows the upstream boards (West art). Vertical wall
		/// (N/S rotation): downstream east = North art, west = South art. A current running along the wall, or none, keeps
		/// <paramref name="placedRot"/>.</summary>
		public static int WeirArtRot(int placedRot, int flowDir)
		{
			bool horizontal = (placedRot & 1) == 1;
			if (flowDir < 0 || flowDir > 7)
			{
				return placedRot;
			}
			if (horizontal)
			{
				int dz = StepZ[flowDir];
				return dz < 0 ? 1 : dz > 0 ? 3 : placedRot;
			}
			int dx = StepX[flowDir];
			return dx > 0 ? 0 : dx < 0 ? 2 : placedRot;
		}

		// ── weir review 2026-10-23 (WEIR_CATCH_FIX_NO_FREE_FISH, WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID) ──

		/// <summary>The weir's intake: every in-current cell (dirAt &gt;= 0) outside the wall whose one flow step lands on a
		/// wall cell - exactly where the surface carry stops a drifting thing (a weir cell is not standable). Distinct cells,
		/// in wall order. Owner 2026-10-23: "they should just capture anything floating downstream."</summary>
		public static List<int[]> WeirIntakeCells(List<int[]> wall, Func<int, int, int> dirAt)
		{
			HashSet<long> onWall = new HashSet<long>();
			for (int i = 0; i < wall.Count; i++)
			{
				onWall.Add(CellKey(wall[i][0], wall[i][1]));
			}
			HashSet<long> seen = new HashSet<long>();
			List<int[]> intake = new List<int[]>();
			for (int i = 0; i < wall.Count; i++)
			{
				for (int d = 0; d < 8; d++)
				{
					int nx = wall[i][0] + StepX[d], nz = wall[i][1] + StepZ[d];
					long key = CellKey(nx, nz);
					if (onWall.Contains(key) || seen.Contains(key))
					{
						continue;
					}
					int f = dirAt(nx, nz);
					if (f < 0 || f > 7 || !onWall.Contains(CellKey(nx + StepX[f], nz + StepZ[f])))
					{
						continue;
					}
					seen.Add(key);
					intake.Add(new[] { nx, nz });
				}
			}
			return intake;
		}

		private static long CellKey(int x, int z) => ((long)x << 32) ^ (uint)z;

		/// <summary>How many items a weir may lift onto its bank now: the room under the cap, never more than offered.</summary>
		public static int WeirCaptureBudget(int held, int cap, int offered)
		{
			int room = cap - held;
			if (room <= 0 || offered <= 0)
			{
				return 0;
			}
			return offered < room ? offered : room;
		}

		/// <summary>The downstream side of a wall (unit step dx, dz, perpendicular to it) when the current at its wet end
		/// crosses it; false when the current runs along the wall or there is none - then no water falls over it and no
		/// white water is drawn. Agrees with <see cref="WeirArtRot"/>'s spill face.</summary>
		public static bool WeirFoamStep(int placedRot, int flowDir, out int dx, out int dz)
		{
			dx = 0;
			dz = 0;
			if (flowDir < 0 || flowDir > 7)
			{
				return false;
			}
			if ((placedRot & 1) == 1)
			{
				dz = StepZ[flowDir];
			}
			else
			{
				dx = StepX[flowDir];
			}
			return dx != 0 || dz != 0;
		}

		/// <summary>The world step to the white water's IMAGE-LEFT side (the frames' _a end) when it falls along (dx, dz): the
		/// frames are drawn crest-up falling south and turned about the vertical, so image-left is west falling south, south
		/// falling east, north falling west, east falling north.</summary>
		public static void WeirFoamLeft(int dx, int dz, out int lx, out int lz)
		{
			// image-left is west at rest (falling south); turning the fall turns it with it: (dx, dz) -> (dz, -dx)
			lx = dz;
			lz = -dx;
		}

		/// <summary>Which end variant to draw: "" when foam continues on both sides, _a / _b when the image-left / -right side
		/// has none beside it, _ab for a lone cell.</summary>
		public static string WeirFoamSuffix(bool leftContinues, bool rightContinues)
		{
			return leftContinues ? (rightContinues ? "" : "_b") : (rightContinues ? "_a" : "_ab");
		}

		/// <summary>How the white water reads at one wet section: opacity, flip-book speed and how far downstream it reaches
		/// (cells). Scaled to the flow: margin water light and slow, the centre full, a flood brighter, faster, further.</summary>
		public struct WeirFoamLook
		{
			public float alpha;
			public float fps;
			public float length;
		}

		public static WeirFoamLook WeirFoam(int lane, bool surge)
		{
			if (lane == LaneNone)
			{
				return new WeirFoamLook { alpha = 0f, fps = 0f, length = 0f };
			}
			if (surge)
			{
				return new WeirFoamLook { alpha = 1f, fps = 14f, length = 1.5f };
			}
			return lane == LaneCentre
				? new WeirFoamLook { alpha = 0.9f, fps = 10f, length = 1f }
				: new WeirFoamLook { alpha = 0.6f, fps = 7f, length = 1f };
		}

		/// <summary>The flip-book frame at real time <paramref name="seconds"/>, looping over <paramref name="frames"/>;
		/// <paramref name="phase"/> (a thing id) puts neighbouring weirs out of step.</summary>
		public static int WeirFoamFrame(float seconds, float fps, int frames, int phase)
		{
			if (frames <= 0)
			{
				return 0;
			}
			if (seconds < 0f) seconds = 0f;
			if (fps < 0f) fps = 0f;
			long n = (long)(seconds * fps + 1e-4f) + (phase & 0x7fffffff);
			return (int)(n % frames);
		}

		// ── owner by card 2026-10-23 07:19: occasional flotsam; weirs auto-rotate across the current ──

		/// <summary>Where a river comes onto the map: in-current edge cells whose upstream neighbour (one step against their
		/// flow) lies off the map. Flotsam enters only here.</summary>
		public static List<int[]> RiverEntryCells(int width, int height, Func<int, int, int> dirAt)
		{
			List<int[]> cells = new List<int[]>();
			for (int x = 0; x < width; x++)
			{
				for (int z = 0; z < height; z++)
				{
					if (x != 0 && z != 0 && x != width - 1 && z != height - 1)
					{
						continue;
					}
					int d = dirAt(x, z);
					if (d < 0 || d > 7)
					{
						continue;
					}
					int ux = x - StepX[d], uz = z - StepZ[d];
					if (ux < 0 || uz < 0 || ux >= width || uz >= height)
					{
						cells.Add(new[] { x, z });
					}
				}
			}
			return cells;
		}

		/// <summary>Chance a flotsam roll spawns one piece, per roll every <paramref name="intervalTicks"/>, for a rate of
		/// <paramref name="perDay"/> pieces a day (60000 ticks); -1 when flotsam is off (no roll at all).</summary>
		public static float FlotsamRollChance(bool enabled, float perDay, int intervalTicks)
		{
			if (!enabled)
			{
				return -1f;
			}
			float c = perDay * intervalTicks / 60000f;
			return c < 0f ? 0f : (c > 1f ? 1f : c);
		}

		/// <summary>A carried thing that reaches the map edge: river flotsam floats on off the map (no clutter); anything
		/// else stops there as before (pawns keep their own washOffMapEdge rule).</summary>
		public static bool FlotsamLeavesAtEdge(bool isPawn, bool isFlotsam)
		{
			return !isPawn && isFlotsam;
		}

		/// <summary>The ferry rope strip between two post centres (a, b) in map x/z: its centre, length and the PrintPlane
		/// rot (degrees) that turns the plane's long +x axis from a to b (PrintPlane maps +x to (cos(-rot), sin(-rot))).</summary>
		public static void RopePlane(float ax, float az, float bx, float bz, out float cx, out float cz, out float length, out float rotDeg)
		{
			float dx = bx - ax, dz = bz - az;
			cx = (ax + bx) * 0.5f;
			cz = (az + bz) * 0.5f;
			length = (float)Math.Sqrt(dx * dx + dz * dz);
			rotDeg = (float)(-Math.Atan2(dz, dx) * 180.0 / Math.PI);
		}

		/// <summary>Rotations to try for a weir so its wall crosses the current: the placed one when it already crosses (or
		/// the flow is diagonal, or there is none); otherwise the two rotations of the other axis, nearest first.</summary>
		public static List<int> WeirCrossCandidates(int placedRot, int flowDir)
		{
			List<int> r = new List<int>(2);
			if (flowDir < 0 || flowDir > 7 || WeirFoamStep(placedRot, flowDir, out _, out _))
			{
				r.Add(placedRot);
				return r;
			}
			r.Add((placedRot + 1) % 4);
			r.Add((placedRot + 3) % 4);
			return r;
		}

		// ── bank-works art (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fixes 8 and 10; owner card 2026-10-17: "Commission REVIEW.md
		//    items 3,4,6,7,8,9,10 in four styles; judged in game"). Sizes in cells; art_source/RiverWorks/compose.py mirrors them.

		/// <summary>The stake post's draw size (square) and how far it sits north of its cell centre, so its footing lands on
		/// the ridge line rather than below it.</summary>
		public const float StakePostSize = 0.8f;

		public const float StakePostLift = 0.18f;

		/// <summary>Levee span art: east-west 128x48 px, north-south 64x128 px, at 128 px a cell.</summary>
		public static readonly float[] StakeRidgeHSize = { 1f, 48f / 128f };

		public static readonly float[] StakeRidgeVSize = { 64f / 128f, 1f };

		/// <summary>Does the stake at (x, z) draw the levee span toward (x+dx, z+dz)? Only east (1,0) and north (0,1) spans,
		/// and only when that neighbour is a stake: each touching pair is drawn once, by its west/south member.</summary>
		public static bool StakeOwnsRidge(int x, int z, int dx, int dz, Func<int, int, bool> isStake)
		{
			bool east = dx == 1 && dz == 0, north = dx == 0 && dz == 1;
			return (east || north) && isStake(x + dx, z + dz);
		}

		/// <summary>The silt-trap's sediment wedge: none without a current (flowDir -1). Otherwise its centre offset from the
		/// trap's centre (cells), the clockwise turn of the art (tip drawn up/north) so the tip points UPSTREAM, and its
		/// scale: 0.55 new, growing with every cell richened, full (1) at five or once clogged.</summary>
		public static bool SiltWedge(int flowDir, int richenedCells, bool clogged, out float offX, out float offZ, out float angleCw, out float scale)
		{
			offX = offZ = angleCw = 0f;
			scale = 0f;
			if (flowDir < 0 || flowDir > 7)
			{
				return false;
			}
			int up = (flowDir + 4) % 8;
			float t = clogged ? 1f : Math.Min(1f, Math.Max(0, richenedCells) / 5f);
			scale = 0.55f + 0.45f * t;
			double rad = up * 45.0 * Math.PI / 180.0;
			double ux = Math.Cos(rad), uz = Math.Sin(rad);
			offX = (float)(Math.Abs(ux) < 1e-9 ? 0.0 : ux * 0.55 * scale);
			offZ = (float)(Math.Abs(uz) < 1e-9 ? 0.0 : uz * 0.55 * scale);
			angleCw = (float)(((90 - up * 45) % 360 + 360) % 360);
			return true;
		}
}
}
