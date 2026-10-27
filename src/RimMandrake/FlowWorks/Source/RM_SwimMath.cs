using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// DEEP_WATER_BUILD_SWIM_OR_SINK (plan P12; owner R12, 2026-10-17 by card: "pawns may swim in water 2 m or deeper").
	/// The Verse-free arithmetic of swimming: who swims, how fast, how long before exhaustion, what armour and carried weight
	/// cost, and what a path through deep water costs each kind of creature. Compiled into SelfTest. The Verse wiring is
	/// Swimming/RM_Swim.cs; drowning itself stays ONE rule (RM_RelativeRulesMath.DrowningPerCheck, P7's V2): swimming only
	/// answers its keepsHeadUp hook.
	///
	/// Vanilla has no swim-speed stat and no drowning (engine doc §1.1, MEASURED). Speed rides the path cost: a deep swim cell
	/// costs <see cref="DefaultSwimPathCost"/> in the path grid (wading chest-deep is 42, vanilla WaterDeep's unused 300), times
	/// the swimmer's own factor in Pawn_PathFollower.CostToMoveIntoCell. Creatures whose race or gene sets a waterCellCost
	/// keep vanilla's own override (PathFinderCostTuning.costWater): they are the aquatic and the strong swimmers.
	/// All numbers PROVISIONAL defaults, each a Mod Setting.
	/// </summary>
	public static class RM_SwimMath
	{
		public enum SwimClass
		{
			/// <summary>Sinks: mechanoids, and anyone too heavily loaded to stay up. Never routed through deep water.</summary>
			None = 0,
			/// <summary>Swims and tires (people; land animals, which also path around deep water unless no other route exists).</summary>
			Swimmer = 1,
			/// <summary>Race or gene sets a waterCellCost above 1, or a water-seeker: swims well, tires slowly, does not avoid water.</summary>
			Strong = 2,
			/// <summary>waterCellCost 1 or a swimming graphic: lives in water, never tires.</summary>
			Aquatic = 3,
		}

		/// <summary>Path-grid cost of one deep swim square (vanilla chest-deep wading is 42, so swimming is slower than wading).</summary>
		public const int DefaultSwimPathCost = 60;

		/// <summary>Hours an unencumbered healthy person swims before exhaustion.</summary>
		public const float DefaultEnduranceHours = 2f;

		/// <summary>Hours on footing (head clear) to recover from full exhaustion.</summary>
		public const float DefaultRecoveryHours = 1f;

		/// <summary>Endurance lost per unit of encumbrance (carried mass / carrying capacity): 1 - 1.25 x load.</summary>
		public const float DefaultWeightEndurancePenalty = 1.25f;

		/// <summary>Swim cost added per unit of encumbrance: cost x (1 + 1.5 x load).</summary>
		public const float DefaultWeightSlowdown = 1.5f;

		/// <summary>Extra path cost per deep square for a land animal (it walks around unless there is no other way).</summary>
		public const int DefaultAnimalAvoidCost = 3000;

		/// <summary>A strong swimmer lasts this many times longer.</summary>
		public const float StrongEnduranceFactor = 3f;

		/// <summary>Below this share of the base endurance a creature cannot stay up at all: it is a non-swimmer (sinks).</summary>
		public const float SinkBelowEnduranceFactor = 0.1f;

		/// <summary>A towed person (a rescuer carrying someone) counts as this much load, not the person's mass: lifesaving
		/// is hard, not impossible.</summary>
		public const float TowedPawnLoad = 0.5f;

		/// <summary>Exhaustion at which the swimmer is warned (and, undrafted or AI, turns for the nearest footing).</summary>
		public const float DefaultWarnAt = 0.7f;

		/// <summary>Exhaustion at which the head goes under (keepsHeadUp false): the one drowning rule then runs.</summary>
		public const float Exhausted = 1f;

		public const int TicksPerHour = 2500;

		public const int Blocked = 10000;

		/// <summary>Who swims. Flags come from the race and genes, never from the job's swimming flag (vanilla's Pawn.WaterCellCost
		/// answers 1 for anyone on a swim-joy job, which is not a property of the creature).</summary>
		public static SwimClass Classify(bool mechanoid, int? raceOrGeneWaterCellCost, bool swimmingGraphic, bool waterSeeker,
			bool humanlike, bool humanlikesSwim)
		{
			if (mechanoid)
			{
				return SwimClass.None;
			}
			if (swimmingGraphic || (raceOrGeneWaterCellCost.HasValue && raceOrGeneWaterCellCost.Value <= 1))
			{
				return SwimClass.Aquatic;
			}
			if (raceOrGeneWaterCellCost.HasValue || waterSeeker)
			{
				return SwimClass.Strong;
			}
			if (humanlike && !humanlikesSwim)
			{
				return SwimClass.None;
			}
			return SwimClass.Swimmer;
		}

		/// <summary>Load as a share of carrying capacity: gear and inventory mass, plus the thing carried (a carried pawn counts as
		/// <see cref="TowedPawnLoad"/>). 0 when the capacity is unknown.</summary>
		public static float Load(float gearAndInventoryKg, float carriedThingKg, bool carryingPawn, float capacityKg)
		{
			if (!(capacityKg > 0f))
			{
				return carryingPawn ? TowedPawnLoad : 0f;
			}
			float load = Math.Max(0f, gearAndInventoryKg) / capacityKg;
			load += carryingPawn ? TowedPawnLoad : Math.Max(0f, carriedThingKg) / capacityKg;
			return load;
		}

		/// <summary>Body-size factor on endurance: sqrt(size), clamped 0.5..2 (a person 1, a rat 0.5, a thrumbo 2).</summary>
		public static float SizeFactor(float bodySize)
		{
			float f = (float)Math.Sqrt(Math.Max(0f, bodySize));
			return f < 0.5f ? 0.5f : (f > 2f ? 2f : f);
		}

		/// <summary>Endurance factor on the base hours: Moving capacity (capped 1.5) x size x weight. 0 for a non-swimmer;
		/// +infinity for the aquatic.</summary>
		public static float EnduranceFactor(SwimClass cls, float moving, float bodySize, float load, float weightPenalty)
		{
			if (cls == SwimClass.None)
			{
				return 0f;
			}
			if (cls == SwimClass.Aquatic)
			{
				return float.PositiveInfinity;
			}
			float m = moving < 0f ? 0f : (moving > 1.5f ? 1.5f : moving);
			float w = 1f - Math.Max(0f, weightPenalty) * Math.Max(0f, load);
			if (w < 0f)
			{
				w = 0f;
			}
			float f = m * SizeFactor(bodySize) * w * (cls == SwimClass.Strong ? StrongEnduranceFactor : 1f);
			return f;
		}

		/// <summary>The class after load: a swimmer whose endurance falls under <see cref="SinkBelowEnduranceFactor"/> sinks.</summary>
		public static SwimClass Effective(SwimClass cls, float enduranceFactor)
		{
			if ((cls == SwimClass.Swimmer || cls == SwimClass.Strong) && enduranceFactor < SinkBelowEnduranceFactor)
			{
				return SwimClass.None;
			}
			return cls;
		}

		/// <summary>SUSPENSION_TOWER_DIAGNOSE_UNSUPPLIED_IN_POOL: a hauler swimming material out to a build site keeps at least
		/// this share of its base endurance (well above <see cref="SinkBelowEnduranceFactor"/>): it swims there and back
		/// without sinking, in more trips. Run8: a colonist picking up 75 steel (37.5 kg on a 35 kg capacity) sank (class
		/// None), so no delivery to a tower in the middle of a flooded cut ever started.</summary>
		public const float SwimCarryEnduranceFloor = 0.5f;

		/// <summary>The most a creature may carry (kg, on top of its gear) and keep <paramref name="floor"/> of its endurance
		/// (<see cref="EnduranceFactor"/> inverted on the carried part of <see cref="Load"/>). 0 for a non-swimmer or when even
		/// empty-handed it is under the floor; +infinity for the aquatic, with no capacity (Load ignores mass) or no weight
		/// penalty while above the floor.</summary>
		public static float MaxSwimCarryKg(SwimClass natural, float moving, float bodySize, float gearKg, float capacityKg,
			float weightPenalty, float floor)
		{
			if (natural == SwimClass.None)
			{
				return 0f;
			}
			if (natural == SwimClass.Aquatic || !(capacityKg > 0f))
			{
				return float.PositiveInfinity;
			}
			float m = moving < 0f ? 0f : (moving > 1.5f ? 1.5f : moving);
			float full = m * SizeFactor(bodySize) * (natural == SwimClass.Strong ? StrongEnduranceFactor : 1f);
			if (!(full > 0f) || full < floor)
			{
				return 0f;
			}
			if (!(weightPenalty > 0f))
			{
				return float.PositiveInfinity;
			}
			float maxLoad = (1f - floor / full) / weightPenalty;
			return Math.Max(0f, maxLoad * capacityKg - Math.Max(0f, gearKg));
		}

		/// <summary>How many of <paramref name="wanted"/> units of <paramref name="unitKg"/> each fit under
		/// <paramref name="maxKg"/> (<see cref="MaxSwimCarryKg"/>); <paramref name="wanted"/> when mass does not bind. 0 means
		/// not even one unit can be swum out.</summary>
		public static int SwimCarryCount(int wanted, float unitKg, float maxKg)
		{
			if (wanted <= 0 || !(unitKg > 0f) || float.IsPositiveInfinity(maxKg))
			{
				return wanted;
			}
			int fits = (int)Math.Floor(maxKg / unitKg + 1e-4f);
			return fits < wanted ? Math.Max(0, fits) : wanted;
		}

		/// <summary>Swim speed as a cost multiplier on the swim cell (1 = the shipped swim cost): load slows, weak Moving slows.
		/// The aquatic and strong keep their vanilla waterCellCost and pay x1.</summary>
		public static float CostFactor(SwimClass cls, float moving, float load, float weightSlowdown)
		{
			if (cls == SwimClass.Aquatic || cls == SwimClass.Strong)
			{
				return 1f;
			}
			float m = moving < 0.2f ? 0.2f : (moving > 1.5f ? 1.5f : moving);
			return (1f + Math.Max(0f, weightSlowdown) * Math.Max(0f, load)) / m;
		}

		/// <summary>Exhaustion added per check while swimming (head under standing, not aquatic): checkTicks / endurance ticks.</summary>
		public static float ExhaustionPerCheck(float enduranceFactor, float baseHours, int checkTicks)
		{
			if (float.IsPositiveInfinity(enduranceFactor))
			{
				return 0f;
			}
			float ticks = enduranceFactor * Math.Max(0.01f, baseHours) * TicksPerHour;
			if (!(ticks > 0f))
			{
				return Exhausted;   // sinks at once
			}
			return checkTicks / ticks;
		}

		/// <summary>Exhaustion shed per check on footing (head clear): full recovery in recoveryHours.</summary>
		public static float RecoveryPerCheck(float recoveryHours, int checkTicks)
		{
			return checkTicks / (Math.Max(0.01f, recoveryHours) * TicksPerHour);
		}

		/// <summary>The keepsHeadUp answer (RM_Drowning's P12 hook): in a swimmable liquid, the aquatic always, a swimmer until
		/// exhausted; a non-swimmer never; nobody in oil, slime, tar, propane, boiling water or brine.</summary>
		public static bool KeepsHeadUp(SwimClass cls, float exhaustion, bool liquidSwimmable)
		{
			if (!liquidSwimmable || cls == SwimClass.None)
			{
				return false;
			}
			return cls == SwimClass.Aquatic || exhaustion < Exhausted;
		}

		/// <summary>Swimming = standing (not lying) in water over the head: the cells where exhaustion runs.</summary>
		public static bool IsSwimming(float waterMetres, float heightMetres, bool lying, float headFraction)
		{
			return !lying && RM_RelativeRulesMath.HeadUnder(waterMetres, heightMetres, false, headFraction);
		}

		/// <summary>DRAFTED_SWIMMER_FIX_PIT_BOTTOM_ROW / DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS / SWIM_DEPTH_FIX_TWO_METRES_WALKED (owner
		/// 2026-10-24: "if I draft him he is no longer swimming"; "Water 5.0 ... Shown walking, not swimming, no wave effects";
		/// "water 2.0 is traversible as walking, and I would have expected swimming"). Vanilla draws the swim pose (head only,
		/// no shadow, ripples) only while a joy-swim job says so (Pawn.Swimming = CurJob.swimming), so a drafted pawn, or one on
		/// any other job, walked through water over its head. The pose is now the SAME rule that runs swim exhaustion
		/// (RM_Swim.Tick): swimming on, not flying, not on a deck, a swimmable liquid, standing in water over its head
		/// (<see cref="IsSwimming"/>). Vanilla's own joy-swim pose is never taken away.</summary>
		public static bool SwimPose(bool vanillaSwimming, bool swimOn, bool flying, bool onDeck, float waterMetres, bool liquidSwimmable,
			float heightMetres, bool lying, float headFraction)
		{
			if (vanillaSwimming)
			{
				return true;
			}
			return swimOn && !flying && !onDeck && liquidSwimmable && waterMetres > 0f
				&& IsSwimming(waterMetres, heightMetres, lying, headFraction);
		}

		/// <summary>Game hours a swimmer lasts: the stated table.</summary>
		public static float EnduranceHours(float enduranceFactor, float baseHours)
		{
			return float.IsPositiveInfinity(enduranceFactor) ? float.PositiveInfinity : enduranceFactor * baseHours;
		}

		/// <summary>Path-planning offset a deep swim cell adds for this creature on top of the grid's own swim cost: blocked for a
		/// non-swimmer (and anyone when swimming is off), the avoid cost for a land animal, 0 otherwise.</summary>
		public static int PlanOffset(SwimClass cls, bool animal, bool animalsAvoid, int avoidCost)
		{
			if (cls == SwimClass.None)
			{
				return Blocked;
			}
			if (animal && cls == SwimClass.Swimmer && animalsAvoid)
			{
				return Math.Max(0, Math.Min(Blocked - 1, avoidCost));
			}
			return 0;
		}

		/// <summary>The full planning cost of a cell for the SelfTest grid planner (and the doc): land cost on land; on a deep
		/// cell the swim cost plus <see cref="PlanOffset"/> (>= Blocked = impassable).</summary>
		public static int PlanCellCost(bool deep, int landCost, int swimCost, int offset)
		{
			if (!deep)
			{
				return landCost;
			}
			if (offset >= Blocked)
			{
				return Blocked;
			}
			return swimCost + offset;
		}

		/// <summary>Owner R12: "pawns may swim in water 2 m or deeper", dug or natural.</summary>
		public const double SwimMinWaterMetres = 2.0;

		/// <summary>SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER (live day 3: a brim-full dug 3 m reservoir read deepCell=False,
		/// CanReach false): the depth the climb rule judges a DUG square at when it holds swimmable water 2 m or deeper. A
		/// swimmer floats at the surface, so the step is measured to the water surface, not the floor: hole notches minus the
		/// whole notches of water (a part-notch never lifts the surface, so the answer never reads shallower than the truth).
		/// -1 = not a swim square (swimming off, a liquid that is never swum, a dry pit, water under 2 m): the hole's own pit
		/// rules stand. A brim-full reservoir answers 0 (level with the ground); a 3.5 m sheer pit with 2 m of water answers 3
		/// (1.5 m of wall above the surface: still a pit for a person, K = 2).</summary>
		public static int DugSwimClimbDepth(bool swimOn, bool liquidSwimmable, int holeNotches, double waterMetres, int wholeWaterNotches)
		{
			return SurfaceClimbDepth(swimOn, liquidSwimmable, holeNotches, waterMetres, wholeWaterNotches, SwimMinWaterMetres);
		}

		/// <summary>WATERED_PIT_FIX_NO_WAY_IN — the least dug water the climb rule judges at its SURFACE: the ChestDeep rung
		/// (RM_WaterChestDeepStill, 3 notches). Owner 2026-10-24: "for water 1.5m in a 1.5m pit, there is 'no way in.' ... it
		/// should be traversible as swimming if walking is no longer allowed." Chest-deep water carries a pawn up to its surface,
		/// so a brim-full 1.5 m pit is level with the ground; the SWIM set (path cost, non-swimmer closure, swim pose by depth)
		/// stays at <see cref="SwimMinWaterMetres"/>.</summary>
		public const double WadeLiftMinWaterMetres = 1.5;

		/// <summary>The climb depth of a dug square holding <see cref="WadeLiftMinWaterMetres"/> or more of swimmable water:
		/// the hole minus its whole notches of water (as <see cref="DugSwimClimbDepth"/>); -1 = the pit rules stand.</summary>
		public static int DugWadeLiftDepth(bool swimOn, bool liquidSwimmable, int holeNotches, double waterMetres, int wholeWaterNotches)
		{
			return SurfaceClimbDepth(swimOn, liquidSwimmable, holeNotches, waterMetres, wholeWaterNotches, WadeLiftMinWaterMetres);
		}

		private static int SurfaceClimbDepth(bool swimOn, bool liquidSwimmable, int holeNotches, double waterMetres, int wholeWaterNotches,
			double minMetres)
		{
			if (!swimOn || !liquidSwimmable || holeNotches <= 0 || waterMetres < minMetres - 1e-6)
			{
				return -1;
			}
			int s = holeNotches - Math.Max(0, wholeWaterNotches);
			return s < 0 ? 0 : s;
		}

		/// <summary>DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS — the depth a FLOATING pawn is drawn at in a hole of
		/// <paramref name="hollowDepth"/> notches holding <paramref name="wholeWaterNotches"/> whole notches of water: the water's
		/// surface, never below the floor nor above the ground. A brim-full 5 m pit draws its swimmer at ground level (sink 0),
		/// not on the floor 5 m down (the owner saw her "jump" in and walk the bottom).</summary>
		public static int SurfaceDrawDepth(int hollowDepth, int wholeWaterNotches)
		{
			if (hollowDepth <= 0)
			{
				return 0;
			}
			int s = hollowDepth - Math.Max(0, wholeWaterNotches);
			return s < 0 ? 0 : s;
		}

		/// <summary>The climb depth of a dug square: its hole, or the swim surface when it is a swim square
		/// (<see cref="DugSwimClimbDepth"/> &gt;= 0), whichever is shallower.</summary>
		public static int ClimbDepthWithSwim(int hollowDepth, int swimClimbDepth)
		{
			return swimClimbDepth >= 0 && swimClimbDepth < hollowDepth ? swimClimbDepth : hollowDepth;
		}
		// ── DUG_SWIM_REFRESH_SHRINK_HASH_SETS: the dug swim squares on flat per-cell arrays ─────────────────────────────

		/// <summary>One dug square's swim code, as RM_MapComponent_Excavation.RefreshDugSwim has always derived it: -1 = the pit
		/// rules stand (no water, or under chest-deep); else climb depth * 2, low bit set when the square is SWUM (2 m+ of a
		/// swimmable liquid). <paramref name="hole"/>: the dug depth in notches; <paramref name="dl"/>: decilitres of liquid.</summary>
		public static int DugSwimCode(bool swimmable, int hole, long dl)
		{
			if (dl <= 0)
			{
				return -1;
			}
			double metres = RM_LevelSolve.Metres(dl);
			int whole = (int)(dl / RM_LevelSolve.U);
			int s = DugSwimClimbDepth(true, swimmable, hole, metres, whole);
			// WATERED_PIT_FIX_NO_WAY_IN: chest-deep (1.5 m) water already lifts the climb to its surface; only 2 m+ is SWUM
			int lift = s >= 0 ? s : DugWadeLiftDepth(true, swimmable, hole, metres, whole);
			return lift >= 0 ? lift * 2 + (s >= 0 ? 1 : 0) : -1;
		}

		/// <summary>DUG_SWIM_REFRESH_SHRINK_HASH_SETS (r13 exprof: RefreshDugSwim 4.8 ms a call, every 60 ticks per map): the
		/// derived dug swim squares, kept on a flat per-cell array instead of a Dictionary of climb depths, a HashSet of swum
		/// squares and a Dictionary of fresh codes rebuilt and compared through hashing every refresh. A refresh is
		/// <see cref="Begin"/>, one <see cref="Put"/> per square with a code (each square at most once), then
		/// <see cref="End"/>, which lists the squares whose code moved (new, changed or gone) and publishes the fresh set only
		/// when one did. Owner: the map's main-thread tick (as the dictionaries were).</summary>
		public sealed class DugSwimSet
		{
			private int[] code = new int[0];       // code + 1 per square; 0 = not a dug swim/lift square
			private int[] fresh = new int[0];      // this refresh's code + 1; zero again after End
			private List<int> cells = new List<int>();
			private List<int> freshCells = new List<int>();

			/// <summary>Squares with a code (the old swimClimb.Count).</summary>
			public int Count => cells.Count;

			/// <summary>Squares that are swum (the old swimCells.Count).</summary>
			public int SwimCount { get; private set; }

			/// <summary>The squares with a code, in ascending index order. Read only; replaced by the next End that moves.</summary>
			public List<int> Cells => cells;

			/// <summary>The climb depth of square i (the old swimClimb[i]); false when it has none.</summary>
			public bool TryClimb(int i, out int climb)
			{
				int c = (uint)i < (uint)code.Length ? code[i] : 0;
				climb = (c - 1) >> 1;
				return c != 0;
			}

			/// <summary>Square i is swum (the old swimCells.Contains(i)).</summary>
			public bool IsSwim(int i)
			{
				int c = (uint)i < (uint)code.Length ? code[i] : 0;
				return c != 0 && ((c - 1) & 1) == 1;
			}

			public void Begin(int n)
			{
				if (code.Length != n)
				{
					// a map's grid never changes size; kept total for the selftest and a first refresh
					var grown = new int[n];
					var kept = new List<int>();
					foreach (int i in cells)
					{
						if (i < n)
						{
							grown[i] = code[i];
							kept.Add(i);
						}
					}
					code = grown;
					cells = kept;
					fresh = new int[n];
				}
				freshCells.Clear();
			}

			public void Put(int i, int value)
			{
				fresh[i] = value + 1;
				freshCells.Add(i);
			}

			/// <summary>Fills <paramref name="changed"/> (cleared first) with every square whose code moved: the fresh squares
			/// in Put order, then the squares that lost their code in the old set's order. Publishes the fresh set when any
			/// moved. Returns changed.Count.</summary>
			public int End(List<int> changed)
			{
				changed.Clear();
				foreach (int i in freshCells)
				{
					if (code[i] != fresh[i])
					{
						changed.Add(i);
					}
				}
				foreach (int i in cells)
				{
					if (fresh[i] == 0)
					{
						changed.Add(i);
					}
				}
				if (changed.Count > 0)
				{
					foreach (int i in cells)
					{
						code[i] = 0;
					}
					int swim = 0;
					foreach (int i in freshCells)
					{
						code[i] = fresh[i];
						swim += (fresh[i] - 1) & 1;
					}
					SwimCount = swim;
					List<int> was = cells;
					cells = freshCells;
					freshCells = was;
					foreach (int i in cells)
					{
						fresh[i] = 0;
					}
				}
				else
				{
					foreach (int i in freshCells)
					{
						fresh[i] = 0;
					}
				}
				freshCells.Clear();
				return changed.Count;
			}
		}
	}

	/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES r15 fix 2: when RM_SwimPathing's deep-water grids must be rebuilt, and
	/// whether a rebuild may re-read only the squares that moved. r15 measured every swim-version move re-reading all 105,625
	/// squares (VersionOf 64 ms over 23 moves, about 2.8 ms each), though the dug-swim refresh, the commonest writer, names the
	/// few squares it changed. Writers that name their squares (<see cref="BumpCells"/>) keep the pending set exact; any
	/// writer that does not (<see cref="Bump"/>: terrain changes, decks, drawbridges, settings) makes the next build a full
	/// re-read, as before. Verse-free so SelfTest proves the patched grid equal to a full re-read on every build.</summary>
	public sealed class RM_SwimGridPlan
	{
		private readonly HashSet<int> pending = new HashSet<int>();
		private readonly List<int> order = new List<int>();
		private bool exact;   // pending names every square that may have moved since the last build

		/// <summary>Moves with every writer (the stamp RM_WallReach reads; a peek, never a rebuild).</summary>
		public int Version { get; private set; }

		public int BuiltVersion { get; private set; } = -2;

		public bool Due => BuiltVersion != Version;

		/// <summary>Squares named since the last build (meaningful only while the set is exact).</summary>
		public int PendingCount => exact ? order.Count : -1;

		/// <summary>A writer that does not say which squares moved: the next build re-reads every square.</summary>
		public void Bump()
		{
			Version++;
			exact = false;
			pending.Clear();
			order.Clear();
		}

		/// <summary>A writer that names every square it may have moved.</summary>
		public void BumpCells(IReadOnlyList<int> cells)
		{
			Version++;
			if (!exact)
			{
				return;
			}
			for (int i = 0; i < cells.Count; i++)
			{
				if (pending.Add(cells[i]))
				{
					order.Add(cells[i]);
				}
			}
		}

		/// <summary>One named square (SWIMGRID_FULL_SHRINK_FILL_FLIP_BUMPS: a terrain write names the square it changed), the same
		/// as <see cref="BumpCells"/> with a list of one, without the list.</summary>
		public void BumpCell(int cell)
		{
			Version++;
			if (exact && pending.Add(cell))
			{
				order.Add(cell);
			}
		}

		/// <summary>Marks the grids built at <see cref="Version"/>. Returns the squares to re-read (in the order named), or null
		/// when every square must be re-read: a writer did not name its squares, more than <paramref name="maxPatch"/> were
		/// named, the caller refuses a patch (<paramref name="canPatch"/>: no earlier build, a setting moved, a periodic full
		/// re-read is due), or this is the first build.</summary>
		public List<int> Take(int maxPatch, bool canPatch)
		{
			List<int> patch = exact && canPatch && order.Count <= maxPatch ? new List<int>(order) : null;
			BuiltVersion = Version;
			pending.Clear();
			order.Clear();
			exact = true;
			return patch;
		}
	}
}
