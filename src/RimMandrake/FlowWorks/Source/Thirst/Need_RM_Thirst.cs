using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>FlowWorks' own thirst (design §2; Own mode only). Falls 0.8 / day at 1x (empty in 1.25 days), faster in heat
	/// (vanilla ambient temperature against the pawn's ComfyTemperatureMax: "one kind of heat"), x1.3 at hard labour, x0.5
	/// asleep. At zero, RM_Dehydration rises 0.30 / day and kills at 1.0; above 0.3 it heals 0.6 / day. The numbers live in
	/// RM_ThirstMath (selftested). A pawn never dies of thirst without a readable sign: the hediff names the cause.</summary>
	public class Need_RM_Thirst : Need
	{
		private static HashSet<JobDef> hardLabour;

		public Need_RM_Thirst(Pawn pawn) : base(pawn)
		{
			threshPercents = new List<float> { RM_ThirstMath.ParchedBelow, RM_ThirstMath.ThirstyBelow };
		}

		public int Category => RM_ThirstMath.Category(CurLevel);

		public override int GUIChangeArrow => IsFrozen || !RM_ThirstProvider.OursLive ? 0 : -1;

		public override bool ShowOnNeedList => base.ShowOnNeedList && RM_ThirstProvider.OursLive;

		public override void SetInitialLevel()
		{
			CurLevelPercentage = RM_ThirstMath.InitialLevel;
		}

		public float FallPerDayNow
		{
			get
			{
				float heat = 1f;
				if (RM_ThirstSettings.thirstHeatScaling)
				{
					heat = RM_ThirstMath.HeatFactor(pawn.AmbientTemperature, pawn.GetStatValue(StatDefOf.ComfyTemperatureMax),
						true);
				}
				return RM_ThirstMath.FallPerDay(RM_ThirstSettings.RateMultiplier, heat, IsHardLabour(pawn), !pawn.Awake());
			}
		}

		public override void NeedInterval()
		{
			if (!RM_ThirstProvider.OursLive || IsFrozen)
			{
				return;
			}
			CurLevel -= RM_ThirstMath.FallPerInterval(FallPerDayNow);
			float delta = RM_ThirstMath.DehydrationDelta(CurLevel, RM_ThirstMath.NeedIntervalTicks);
			if (delta != 0f)
			{
				HealthUtility.AdjustSeverity(pawn, RM_ThirstDefOf.RM_Dehydration, delta);
			}
		}

		public override string GetTipString()
		{
			string s = base.GetTipString();
			if (RM_ThirstProvider.OursLive && !IsFrozen)
			{
				s += "\n\n" + "Falling " + (FallPerDayNow * 100f).ToString("F0") + "% a day right now.";
			}
			return s;
		}

		private static bool IsHardLabour(Pawn p)
		{
			JobDef cur = p.CurJobDef;
			if (cur == null)
			{
				return false;
			}
			if (hardLabour == null)
			{
				hardLabour = new HashSet<JobDef>
				{
					JobDefOf.Mine, JobDefOf.FinishFrame, JobDefOf.Deconstruct, JobDefOf.HaulToCell, JobDefOf.HaulToContainer,
					JobDefOf.BuildRoof, JobDefOf.RemoveFloor, JobDefOf.SmoothFloor,
					RimMandrakeFlowWorks_DefOf.RM_DigCanalJob, RimMandrakeFlowWorks_DefOf.RM_FillInCanalJob,
				};
				hardLabour.Remove(null);
			}
			return hardLabour.Contains(cur);
		}
	}

	/// <summary>The need-level mood thoughts (design §2, the shape of vanilla Hungry): Thirsty -4, Parched -10, Dehydrated
	/// -18. One worker per ThoughtDef; each reads the live RM_Thirst category. No positive thought for plain water.</summary>
	public abstract class ThoughtWorker_RM_ThirstBase : ThoughtWorker
	{
		protected abstract int WantCategory { get; }

		protected override ThoughtState CurrentStateInternal(Pawn p)
		{
			if (!RM_ThirstProvider.OursLive || p.needs == null)
			{
				return ThoughtState.Inactive;
			}
			Need_RM_Thirst need = p.needs.TryGetNeed(RM_ThirstDefOf.RM_Thirst) as Need_RM_Thirst;
			if (need == null)
			{
				return ThoughtState.Inactive;
			}
			return need.Category == WantCategory ? ThoughtState.ActiveAtStage(0) : ThoughtState.Inactive;
		}
	}

	public class ThoughtWorker_RM_Thirsty : ThoughtWorker_RM_ThirstBase
	{
		protected override int WantCategory => 1;
	}

	public class ThoughtWorker_RM_Parched : ThoughtWorker_RM_ThirstBase
	{
		protected override int WantCategory => 2;
	}

	public class ThoughtWorker_RM_Dehydrated : ThoughtWorker_RM_ThirstBase
	{
		protected override int WantCategory => 3;
	}
}
