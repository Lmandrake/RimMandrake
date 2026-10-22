using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_FILL_EFFECTS_1: what the fluid in a cell does to the pawn standing in it. No "water / oiled / poison
	/// pit" def exists — every effect comes from the CELL's fluid (fluidGrid, LIQUID_BODY_FLUID_IDENTITY_1).
	/// - DROWNING (PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE, owner R7, form V2): the liquid covers the creature's head
	///   (over 0.9 H standing, 0.2 H lying down; H by size band, RM_RelativeRulesMath.HeightByBand), at ANY depth of hole,
	///   any fluid, unless it keeps its head up (RM_Drowning.KeepsHeadUp: a swimmer today; P12's hook) or, standing, has a
	///   step it can climb into water under its head. RM_PitDrowning recovers on its own once the pawn is out.
	/// - POISON: a fluid with <c>toxicPerDayAtBrim</c> &gt; 0 adds vanilla ToxicBuildup keyed to fill, at any
	///   depth, reduced by ToxicEnvironmentResistance.
	/// - OIL: burns. That is Phase 6's RM_LiquidFire, which already knows the occupant (a D=4 occupant always
	///   catches, ruling 22); nothing here.
	/// Rates PROVISIONAL (RM_FillEffectMath).
	/// </summary>
	public static class RM_PitFillEffects
	{
		public static bool IsSwimmer(Pawn p)
		{
			return p.ageTracker?.CurKindLifeStage?.swimmingGraphicData != null;
		}

		public static void Tick(Map map, RM_MapComponent_Excavation ex)
		{
			if (Find.TickManager.TicksGame % RM_FillEffectMath.IntervalTicks != 0)
			{
				return;
			}
			bool drown = RimMandrakeFlowWorksSettings.pitDrowningEnabled;
			bool poison = RimMandrakeFlowWorksSettings.poisonFillEnabled;
			if (!drown && !poison)
			{
				return;
			}
			HediffDef drowning = RimMandrakeFlowWorks_DefOf.RM_PitDrowning;
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p.health == null || p.Dead)
				{
					continue;
				}
				IntVec3 c = p.Position;
				if (!ex.IsExcavated(c))
				{
					// CANAL_OVERFLOW stage 2: spilled water standing on undug ground is read the same way (water only today, so
					// drowning only: a pawn lying in a deep walled-in pool; ice is not water to drown in)
					if (drown && drowning != null && Sheet.RM_SheetSettings.pawnEffectsEnabled)
					{
						int sdl = Sheet.RM_MapComponent_Sheet.StandingDlAt(map, c);
						float sm = sdl / (float)RM_LevelSolve.U * RM_Volume.MetresPerNotch;
						float sadd = sdl > 0 ? RM_Drowning.PerCheck(map, ex, p, c, sm) : 0f;
						if (sadd > 0f)
						{
							HealthUtility.AdjustSeverity(p, drowning, sadd);
							if (!Swimming.RM_SwimWater.On)
							{
								Swimming.RM_Swim.DrownMessage(p);
							}
						}
					}
					continue;
				}
				// LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD: the liquid in notches from the cell's DECILITRES (a part-notch counts: a
				// 4.5 cm sheet is 0.09 of a notch), never whole notches only
				float fill = ex.WaterDlAt(c) / (float)RM_LevelSolve.U;
				if (fill <= 0f)
				{
					continue;
				}
				// An intact cover is ground (same predicate as RM_PitExposure / RM_PitPathing / the shooting
				// patch): a pawn walking on it is not immersed in the fill beneath (GPT FlowWorks review #4).
				// SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP: on a grate the fill splashes up (toxin at half the rate, never drowning);
				// a pawn in the floor band under a deck is in the fill
				float share = Pits.RM_GrateEffects.SplashShare(Pits.RM_SpanUtility.DeckAt(map, c), p);
				if (share <= 0f)
				{
					continue;
				}
				int depth = ex.DepthAt(c);
				FluidDef fluid = ex.FluidAt(c) ?? ex.ActiveFluid;
				bool flying = p.Flying;
				if (drown && drowning != null && share >= 1f)
				{
					float add = RM_Drowning.PerCheck(map, ex, p, c, ex.WaterMetresAt(c));
					if (add > 0f)
					{
						HealthUtility.AdjustSeverity(p, drowning, add);
						// The readable sign (no-vanishing rule): RM_Swim.Tick sends "X is drowning." for dug cells too, but it skips
						// every pawn while deep swimming is switched off, so with swimming off this pass sends it itself.
						if (!Swimming.RM_SwimWater.On)
						{
							Swimming.RM_Swim.DrownMessage(p);
						}
					}
				}
				if (poison && fluid != null && fluid.toxicPerDayAtBrim > 0f && HediffDefOf.ToxicBuildup != null)
				{
					float res = p.GetStatValue(StatDefOf.ToxicEnvironmentResistance);
					float add = share * RM_FillEffectMath.ToxinPerCheck(fill, depth, fluid.toxicPerDayAtBrim, res, flying);
					if (add > 0f)
					{
						HealthUtility.AdjustSeverity(p, HediffDefOf.ToxicBuildup, add);
					}
				}
			}
		}

		/// <summary>static_call surface: "x,z" -&gt; the drowning verdict for the first pawn on that cell:
		/// "DROWN id H=1.75 lying=b water=2.10 under=b headUp=b exit=b perCheck=0.0417".</summary>
		public static string ProofDrown(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			string[] a = (arg ?? "").Split(',');
			if (ex == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
			{
				return "REFUSED: arg must be x,z on a map with the excavation component";
			}
			IntVec3 c = new IntVec3(x, 0, z);
			if (!c.InBounds(map))
			{
				return "REFUSED: out of bounds";
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (t is Pawn p)
				{
					float w = ex.WaterMetresAt(c);
					return "DROWN " + p.ThingID + " H=" + RM_Drowning.HeightOf(p).ToString("0.00") + " lying=" + RM_Drowning.Lying(p)
						+ " water=" + w.ToString("0.00") + " under=" + RM_Drowning.HeadUnder(p, w) + " headUp=" + RM_Drowning.KeepsHeadUp(p, c, w)
						+ " exit=" + RM_Drowning.ExitInReach(map, ex, p, c) + " perCheck=" + RM_Drowning.PerCheck(map, ex, p, c, w).ToString("0.0000");
				}
			}
			return "REFUSED: no pawn at " + c;
		}

		/// <summary>static_call surface: "" -&gt; per-pawn report of every pawn standing in liquid (cell, D, F,
		/// fluid, swimmer, drowning and toxic severities) — the census the first script reads per cell by fluid.</summary>
		public static string ProofReport(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null) return "REFUSED: no excavation component on the current map";
			var rows = new List<string>();
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				IntVec3 c = p.Position;
				if (!ex.IsExcavated(c) || ex.WaterDlAt(c) <= 0) continue;
				Hediff d = RimMandrakeFlowWorks_DefOf.RM_PitDrowning != null
					? p.health?.hediffSet.GetFirstHediffOfDef(RimMandrakeFlowWorks_DefOf.RM_PitDrowning) : null;
				Hediff t = p.health?.hediffSet.GetFirstHediffOfDef(HediffDefOf.ToxicBuildup);
				rows.Add(p.ThingID + "@" + c.x + "," + c.z + " D=" + ex.DepthAt(c) + " F=" + ex.FillAt(c)
					+ " fluid=" + (ex.FluidAt(c)?.defName ?? "none") + " swimmer=" + IsSwimmer(p)
					+ " drown=" + (d?.Severity ?? 0f).ToString("F3") + " tox=" + (t?.Severity ?? 0f).ToString("F3")
					+ " burning=" + ex.LiquidFire.IsBurning(map, c));
			}
			return "FILLFX " + rows.Count + " | " + string.Join(" | ", rows);
		}
	}

	/// <summary>
	/// PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE (owner R7, 2026-10-17 by card; form V2, veto-able): THE drowning rule, one rule for
	/// pits and (P12, DEEP_WATER_BUILD_SWIM_OR_SINK, owner R12) lakes. Drowning follows the WATER against the creature's height,
	/// never the hole: "one litre in a 7 m pit cannot drown its occupant", and 2 m of water in any hole drowns a standing person
	/// (a brimming 1.5 m pocket reaches a person's chest, and drowns one lying down).
	///
	/// P12 HOOK. <see cref="keepsHeadUp"/> is the one place swimming plugs in. Its default answers "a swimmer" (the kind's
	/// swimming graphic, vanilla 1.6's marker); Swimming.RM_SwimWater's static constructor (DEEP_WATER_BUILD_SWIM_OR_SINK)
	/// replaces it with the swim rule (who swims, exhaustion, apparel and weight, the liquid) and Swimming.RM_Swim.Tick calls
	/// <see cref="PerCheck"/> for pawns in natural deep water too; the head test, the lying test, the exit-in-reach test and
	/// the rate stay here, so pits and lakes can never drown by two rules.
	/// </summary>
	public static class RM_Drowning
	{
		/// <summary>P12's hook: does this pawn keep its head above <paramref name="waterMetres"/> of water on cell c? Default: a
		/// swimmer does (it treads water). Must be cheap (called per wet pawn every 250 ticks).</summary>
		public static System.Func<Pawn, IntVec3, float, bool> keepsHeadUp = (p, c, w) => RM_PitFillEffects.IsSwimmer(p);

		public static bool KeepsHeadUp(Pawn p, IntVec3 c, float waterMetres)
		{
			try
			{
				return keepsHeadUp != null && keepsHeadUp(p, c, waterMetres);
			}
			catch (System.Exception e)
			{
				Log.ErrorOnce("[FlowWorks] drowning keepsHeadUp hook threw: " + e.Message, 0x5D7A11);
				return RM_PitFillEffects.IsSwimmer(p);
			}
		}

		/// <summary>The creature's height H in metres: its climb size band (no climber/leaper bonus; the "creature height"
		/// multiplier applies), so one size system serves climbing and water.</summary>
		public static float HeightOf(Pawn p)
		{
			int band = RM_PitTrapMath.ClimbLimit(p?.BodySize ?? 1f, 0, RimMandrakeFlowWorksSettings.pitClimbAbilityMultiplier);
			return RM_RelativeRulesMath.HeightMetres(band);
		}

		/// <summary>Lying down: downed, or any posture but standing (asleep, in bed).</summary>
		public static bool Lying(Pawn p)
		{
			return p.Downed || p.GetPosture() != PawnPosture.Standing;
		}

		public static bool HeadUnder(Pawn p, float waterMetres)
		{
			return RM_RelativeRulesMath.HeadUnder(waterMetres, HeightOf(p), Lying(p),
				RimMandrakeFlowWorksSettings.pitDrowningHeadFraction, RimMandrakeFlowWorksSettings.pitDrowningLyingFraction);
		}

		/// <summary>A cardinal neighbour this pawn can step to (within its climb limit, or by a ramp or a ladder it may use) whose
		/// water is under its head standing. A downed pawn reaches nothing (PerCheck ignores this for lying pawns).</summary>
		public static bool ExitInReach(Map map, RM_MapComponent_Excavation eng, Pawn p, IntVec3 c)
		{
			int fromD = RM_SuperdeepTrap.StepDepthAt(map, eng, c);
			int k = RM_PocketGrid.ClimbLimitOf(p);
			float h = HeightOf(p);
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = c + GenAdj.CardinalDirections[i];
				if (!n.InBounds(map) || !n.Walkable(map))
				{
					continue;
				}
				int toD = RM_SuperdeepTrap.StepDepthAt(map, eng, n);
				bool joined = RM_ClimbJoins.ForPawn(map, eng, c, n, fromD, toD, p, out _, out _);
				// DEEP_WATER_BUILD_SWIM_OR_SINK: natural water counts too (a deep lake square beside you is not footing).
				float w = Swimming.RM_SwimWater.WaterMetresAt(map, eng, n);
				if (RM_RelativeRulesMath.ExitInReach(fromD, toD, k, joined, w, h, RimMandrakeFlowWorksSettings.pitDrowningHeadFraction))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Severity of RM_PitDrowning to add this check (250 ticks) for pawn p standing in waterMetres of liquid on c.</summary>
		public static float PerCheck(Map map, RM_MapComponent_Excavation eng, Pawn p, IntVec3 c, float waterMetres)
		{
			if (p == null || !(waterMetres > 0f) || p.Flying || !HeadUnder(p, waterMetres))
			{
				return 0f;
			}
			bool lying = Lying(p);
			bool headUp = KeepsHeadUp(p, c, waterMetres);
			bool exit = !lying && !headUp && ExitInReach(map, eng, p, c);
			return RM_RelativeRulesMath.DrowningPerCheck(true, lying, headUp, false, exit,
				RimMandrakeFlowWorksSettings.pitDrowningRateMultiplier);
		}
	}
}
