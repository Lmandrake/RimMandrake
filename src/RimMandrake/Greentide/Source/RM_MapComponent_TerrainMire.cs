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

			if (ext != null && !ext.IsImmune(pawn))
			{
				if (existing == null)
				{
					existing = HediffMaker.MakeHediff(RM_DefOf.RM_Mired, pawn);
					pawn.health.AddHediff(existing);
				}
				bool stuck = existing.Severity >= ext.stuckThreshold;
				if (stuck && Rand.Chance(ext.selfStruggleChancePerCheck * 0.1f))
				{
					// Even stuck pawns make token, glacial progress alone —
					// RM_WorkGiver_FreeMired is the real way out, not the only way.
					existing.Severity = System.Math.Max(0f, existing.Severity - ext.mireSeverityPerTick);
				}
				else if (!stuck && Rand.Chance(ext.selfStruggleChancePerCheck))
				{
					existing.Severity = System.Math.Max(0f, existing.Severity - ext.mireSeverityPerTick * 0.5f);
				}
				else
				{
					existing.Severity = System.Math.Min(1f, existing.Severity + ext.mireSeverityPerTick);
				}
			}
			else if (existing != null)
			{
				float decay = ext?.mireDecayPerTick ?? 0.02f;
				existing.Severity -= decay;
				if (existing.Severity <= 0f)
				{
					pawn.health.RemoveHediff(existing);
				}
			}
		}
	}
}
