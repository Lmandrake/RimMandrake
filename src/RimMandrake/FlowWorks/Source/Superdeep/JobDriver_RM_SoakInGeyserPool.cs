using System.Linq;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB: soak in a geyser pool (target A the geyser, B the cell). Standalone
	/// Hot Spring's soak, its numbers copied as our own: 3000 ticks, comfort from the cell, rest at 1.111, Meditative joy at
	/// x1.4 (none for prisoners), a sleep Z and a healing cross now and then, the "hot pool" hediff while in and "after the hot
	/// pool" after. One change: the bather sits UP (standing posture), never lies face up as in the mod, because FlowWorks'
	/// drowning reads a lying pawn by its lying height and would drown it in a pool it can stand in. When the soak ends: the
	/// afterglow, vanilla's HotSpring memory (owner by card 2026-11-12) and the liquid's own bath cost (FluidDef.bathCost).
	/// </summary>
	public class JobDriver_RM_SoakInGeyserPool : JobDriver
	{
		public bool soaking;
		private int soakedTicks;

		private Building_SteamGeyser Geyser => job.targetA.Thing as Building_SteamGeyser;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref soaking, "soaking");
			Scribe_Values.Look(ref soakedTicks, "soakedTicks");
		}

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, RM_GeyserTubMath.MaxBathers, 0, null, errorOnFailed)
				&& pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			this.FailOn(() => !RM_GeyserPit.PoolOpen(Geyser, out _));
			yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
			Toil soak = ToilMaker.MakeToil("RM_SoakInGeyserPool");
			soak.defaultCompleteMode = ToilCompleteMode.Delay;
			soak.defaultDuration = RM_GeyserTubMath.SoakTicks;
			soak.initAction = () =>
			{
				soaking = true;
				pawn.pather.StopDead();
				RM_GeyserPit.ApplyHealing();
				HediffDef after = DefDatabase<HediffDef>.GetNamedSilentFail("RM_HotPoolAfterglow");
				Hediff old = after == null ? null : pawn.health.hediffSet.GetFirstHediffOfDef(after);
				if (old != null)
				{
					pawn.health.RemoveHediff(old);
				}
				HediffDef soakDef = DefDatabase<HediffDef>.GetNamedSilentFail("RM_HotPoolSoak");
				if (soakDef != null && !pawn.health.hediffSet.HasHediff(soakDef))
				{
					pawn.health.AddHediff(soakDef);
				}
				pawn.Drawer?.renderer?.SetAllGraphicsDirty();
			};
			soak.tickAction = () =>
			{
				soakedTicks++;
				pawn.GainComfortFromCellIfPossible(1);
				pawn.needs?.rest?.TickResting(RM_GeyserTubMath.RestEffectiveness);
				if (!pawn.IsPrisoner && pawn.needs?.joy != null)
				{
					pawn.needs.joy.GainJoy(RM_GeyserTubMath.JoyGainFactor * job.def.joyGainRate * 0.36f / 2500f, job.def.joyKind);
				}
				if (pawn.IsHashIntervalTick(100) && !pawn.Position.Fogged(pawn.Map))
				{
					if (pawn.health.hediffSet.GetNaturallyHealingInjuredParts().Any())
					{
						FleckMaker.ThrowMetaIcon(pawn.Position, pawn.Map, FleckDefOf.HealingCross);
					}
					else if (pawn.needs?.rest != null && pawn.needs.rest.CurLevelPercentage < 0.3f)
					{
						FleckMaker.ThrowMetaIcon(pawn.Position, pawn.Map, FleckDefOf.SleepZ);
					}
				}
			};
			soak.AddFinishAction(OutOfThePool);
			soak.handlingFacing = false;
			yield return soak;
		}

		/// <summary>Out: the soak hediff goes; a soak at least half done earns the afterglow and the memory; any soak at all pays
		/// the liquid's cost.</summary>
		private void OutOfThePool()
		{
			if (!soaking)
			{
				return;
			}
			soaking = false;
			pawn.Drawer?.renderer?.SetAllGraphicsDirty();
			HediffDef soakDef = DefDatabase<HediffDef>.GetNamedSilentFail("RM_HotPoolSoak");
			Hediff h = soakDef == null ? null : pawn.health.hediffSet.GetFirstHediffOfDef(soakDef);
			if (h != null)
			{
				pawn.health.RemoveHediff(h);
			}
			if (pawn.Dead || !pawn.Spawned)
			{
				return;
			}
			if (soakedTicks * 2 >= RM_GeyserTubMath.SoakTicks)
			{
				HediffDef after = DefDatabase<HediffDef>.GetNamedSilentFail("RM_HotPoolAfterglow");
				if (RM_GeyserPitSettings.geyserPoolAfterglowEnabled && after != null)
				{
					pawn.health.AddHediff(after);
				}
				ThoughtDef hot = DefDatabase<ThoughtDef>.GetNamedSilentFail("HotSpring");
				if (RM_GeyserPitSettings.geyserPoolMoodEnabled && hot != null && pawn.needs?.mood?.thoughts?.memories != null)
				{
					Thought_Memory m = (Thought_Memory)ThoughtMaker.MakeThought(hot);
					m.moodPowerFactor = RM_GeyserPitSettings.geyserPoolMoodFactor;
					pawn.needs.mood.thoughts.memories.TryGainMemory(m);
				}
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(pawn.Map);
			FluidDef f = eng == null ? null : RM_GeyserPit.FluidOn(pawn.Map, eng, job.targetB.Cell);
			if (soakedTicks > 0)
			{
				PayCost(f?.bathCost);
			}
		}

		private void PayCost(RM_BathCost cost)
		{
			if (cost == null)
			{
				return;
			}
			if (RM_GeyserPitSettings.geyserBathFilthEnabled && cost.filth != null && cost.filthCount > 0)
			{
				FilthMaker.TryMakeFilth(pawn.Position, pawn.Map, cost.filth, cost.filthCount);
			}
			if (RM_GeyserPitSettings.geyserBathMoodCostEnabled && cost.thought != null)
			{
				pawn.needs?.mood?.thoughts?.memories?.TryGainMemory(cost.thought);
			}
			if (RM_GeyserPitSettings.geyserBathSlipEnabled && cost.slipStunTicks > 0 && pawn.stances?.stunner != null)
			{
				pawn.stances.stunner.StunFor(cost.slipStunTicks, null, false);
			}
		}

		public override string GetReport()
		{
			return soaking ? "soaking in the hot pool." : base.GetReport();
		}
	}

	/// <summary>Recreation: the nearest open geyser pool with a free cell this pawn can reach.</summary>
	public class JoyGiver_RM_SoakInGeyserPool : JoyGiver
	{
		public override Job TryGiveJob(Pawn pawn)
		{
			return RM_GeyserPitSettings.geyserPoolEnabled && RM_GeyserPit.On ? SoakJob(pawn, null, def.jobDef) : null;
		}

		/// <summary>A soak job for <paramref name="pawn"/> at <paramref name="only"/> (or the nearest open pool), else null.</summary>
		public static Job SoakJob(Pawn pawn, Building_SteamGeyser only, JobDef jobDef)
		{
			if (!RM_GeyserPit.MaySoak(pawn) || jobDef == null)
			{
				return null;
			}
			RM_MapComponent_GeyserPits pits = RM_GeyserPit.PitsOf(pawn.Map);
			if (pits == null)
			{
				return null;
			}
			Building_SteamGeyser best = null;
			IntVec3 bestCell = IntVec3.Invalid;
			float bestD = float.MaxValue;
			foreach (Building_SteamGeyser g in pits.Geysers)
			{
				if ((only != null && g != only) || g == null || !g.Spawned || !RM_GeyserPit.PoolOpen(g, out RM_GeyserPit.State s)
					|| !pawn.CanReserve(g, RM_GeyserTubMath.MaxBathers, 0))
				{
					continue;
				}
				IntVec3 c = RM_GeyserPit.FreeSoakCell(g, s, pawn);
				float d = c.IsValid ? (c - pawn.Position).LengthHorizontalSquared : float.MaxValue;
				if (d < bestD)
				{
					best = g;
					bestCell = c;
					bestD = d;
				}
			}
			return best == null ? null : JobMaker.MakeJob(jobDef, best, bestCell);
		}
	}

	/// <summary>Right-click a geyser pool: "Soak in the hot pool" (how a sick colonist is sent).</summary>
	public class FloatMenuOptionProvider_RM_GeyserPool : FloatMenuOptionProvider
	{
		protected override bool Drafted => true;
		protected override bool Undrafted => true;
		protected override bool Multiselect => false;

		protected override bool AppliesInt(FloatMenuContext context) => RM_GeyserPit.On && RM_GeyserPitSettings.geyserPoolEnabled;

		public override IEnumerable<FloatMenuOption> GetOptionsFor(Thing clickedThing, FloatMenuContext context)
		{
			Pawn p = context.FirstSelectedPawn;
			if (!(clickedThing is Building_SteamGeyser g) || p == null || p.Faction != Faction.OfPlayer || !p.RaceProps.Humanlike
				|| !RM_GeyserPit.PoolOpen(g, out _))
			{
				yield break;
			}
			JobDef jd = DefDatabase<JobDef>.GetNamedSilentFail("RM_SoakInGeyserPool");
			Job j = JoyGiver_RM_SoakInGeyserPool.SoakJob(p, g, jd);
			if (j == null)
			{
				yield return new FloatMenuOption("Soak in the hot pool (no free spot this pawn can reach and stand in)", null);
				yield break;
			}
			yield return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption("Soak in the hot pool", () =>
			{
				j.playerForced = true;
				p.jobs.TryTakeOrderedJob(j, JobTag.Misc);
			}), p, g);
		}
	}
}
