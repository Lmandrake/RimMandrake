using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_FILL_EFFECTS_1: what the fluid in a cell does to the pawn standing in it. No "water / oiled / poison
	/// pit" def exists — every effect comes from the CELL's fluid (fluidGrid, LIQUID_BODY_FLUID_IDENTITY_1).
	/// - DROWNING: F &gt; 0 at D = 4 (a pit is only a superdeep cell), any fluid, non-swimmers only. Swimmer =
	///   the pawn's kind life stage carries a swimming graphic (1.6's own swimmer marker). RM_PitDrowning
	///   recovers on its own once the pawn is out (its severityPerDay comp).
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
					continue;
				}
				int fill = ex.FillAt(c);
				if (fill <= 0)
				{
					continue;
				}
				int depth = ex.DepthAt(c);
				FluidDef fluid = ex.FluidAt(c) ?? ex.ActiveFluid;
				bool flying = p.Flying;
				if (drown && drowning != null)
				{
					float add = RM_FillEffectMath.DrowningPerCheck(fill, depth, ex.IsSuperdeepExcavation(c),
						IsSwimmer(p), flying, RimMandrakeFlowWorksSettings.pitDrowningRateMultiplier);
					if (add > 0f)
					{
						HealthUtility.AdjustSeverity(p, drowning, add);
					}
				}
				if (poison && fluid != null && fluid.toxicPerDayAtBrim > 0f && HediffDefOf.ToxicBuildup != null)
				{
					float res = p.GetStatValue(StatDefOf.ToxicEnvironmentResistance);
					float add = RM_FillEffectMath.ToxinPerCheck(fill, depth, fluid.toxicPerDayAtBrim, res, flying);
					if (add > 0f)
					{
						HealthUtility.AdjustSeverity(p, HediffDefOf.ToxicBuildup, add);
					}
				}
			}
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
				if (!ex.IsExcavated(c) || ex.FillAt(c) == 0) continue;
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
}
