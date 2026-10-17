using System;

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
	}
}
