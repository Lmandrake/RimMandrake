using System.Collections.Generic;
using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1 (M8, churnmud mire half). Every
	/// CheckIntervalTicks, scans every spawned pawn on the map: standing on a
	/// terrain carrying RM_MireExtension (and not immune) escalates RM_Mired;
	/// standing anywhere else decays it back to zero and removes it. Purely
	/// interval-driven — no per-pawn ticker, safe on a map with zero churnmud.
	/// </summary>
	public class RM_MapComponent_TerrainMire : MapComponent
	{
		private const int CheckIntervalTicks = 60;

		public RM_MapComponent_TerrainMire(Map map)
			: base(map)
		{
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (!RM_GreentideSettings.mireEnabled)
			{
				return; // MOD_OPTIONS_RETROFIT_1: master toggle, all-off degrades to a no-op
			}
			if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
			{
				return;
			}
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				ProcessPawn(pawns[i]);
			}
		}

		private void ProcessPawn(Pawn pawn)
		{
			if (pawn?.health == null || pawn.Dead)
			{
				return;
			}
			TerrainDef terrain = pawn.Position.GetTerrain(map);
			RM_MireExtension ext = terrain?.GetModExtension<RM_MireExtension>();
			Hediff existing = pawn.health.hediffSet.GetFirstHediffOfDef(RM_DefOf.RM_Mired);
			bool onMire = ext != null && !ext.IsImmune(pawn);
			if (!onMire && existing == null)
			{
				return;
			}
			if (onMire && existing == null)
			{
				existing = HediffMaker.MakeHediff(RM_DefOf.RM_Mired, pawn);
				pawn.health.AddHediff(existing);
			}
			// MOD_OPTIONS_RETROFIT_1: mireSeverityMultiplier scales the whole XML-authored per-terrain rate uniformly (never the
			// terrain's own field) so the ruled v1 default (1.0x) is unchanged. A stuck pawn makes token, glacial progress alone -
			// RM_WorkGiver_FreeMired is the real way out, not the only way.
			RM_MireKernel.Outcome o = RM_MireKernel.Step(onMire, true, existing.Severity, ext?.mireSeverityPerTick ?? 0f,
				RM_GreentideSettings.mireSeverityMultiplier, ext?.selfStruggleChancePerCheck ?? 0f, ext?.stuckThreshold ?? 1f,
				ext?.mireDecayPerTick ?? 0.02f, ext != null, p => Rand.Chance(p), out float severity);
			existing.Severity = severity;
			if (o == RM_MireKernel.Outcome.Remove)
			{
				pawn.health.RemoveHediff(existing);
			}
		}
	}
}
