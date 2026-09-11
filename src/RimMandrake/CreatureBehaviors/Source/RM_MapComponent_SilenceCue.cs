using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1. Any pawn carrying RM_SilenceAuraExtension
	/// that starts a PredatorHunt job within triggerRadius of a free colonist
	/// hushes this map's BIOME ambient sustainers (Biome.soundsAmbient) for
	/// hushDurationTicks, then restores them.
	///
	/// Route verified against RimSage source (Verse/Sound/Sustainer.cs,
	/// SustainerManager.cs, RimWorld/AmbientSoundManager.cs): neither Sustainer
	/// nor SustainerManager exposes a partial volume-ramp, so this ends the
	/// matching sustainers outright (may pop audibly — an accepted honest
	/// trade the kit spec itself names) and lets AmbientSoundManager's own
	/// map-switch recreation route bring them back rather than re-deriving
	/// that logic here. Deliberately scoped to soundsAmbient only, never
	/// EndAllInMap — this is a hush of the biome's ambience, not the map's
	/// weather or machinery sound.
	/// </summary>
	public class RM_MapComponent_SilenceCue : MapComponent
	{
		private const int CheckIntervalTicks = 60;

		private bool hushed;
		private int hushEndTick = -1;

		public RM_MapComponent_SilenceCue(Map map)
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
			if (hushed)
			{
				if (Find.TickManager.TicksGame >= hushEndTick)
				{
					Restore();
				}
				return;
			}
			ScanForTrigger();
		}

		private void ScanForTrigger()
		{
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn pawn = pawns[i];
				RM_SilenceAuraExtension ext = pawn.def?.GetModExtension<RM_SilenceAuraExtension>();
				if (ext == null || pawn.CurJob == null || pawn.CurJob.def != JobDefOf.PredatorHunt)
				{
					continue;
				}
				if (NearAnyColonist(pawn, ext.triggerRadius))
				{
					Hush(ext.hushDurationTicks);
					return;
				}
			}
		}

		private bool NearAnyColonist(Pawn predator, float radius)
		{
			List<Pawn> colonists = map.mapPawns.FreeColonistsSpawned;
			float radiusSq = radius * radius;
			for (int i = 0; i < colonists.Count; i++)
			{
				if ((colonists[i].Position - predator.Position).LengthHorizontalSquared <= radiusSq)
				{
					return true;
				}
			}
			return false;
		}

		private void Hush(int durationTicks)
		{
			List<SoundDef> ambient = map.Biome?.soundsAmbient;
			if (ambient.NullOrEmpty())
			{
				return;
			}
			List<Sustainer> all = Find.SoundRoot.sustainerManager.AllSustainers;
			for (int i = all.Count - 1; i >= 0; i--)
			{
				Sustainer s = all[i];
				if (s.info.Maker.Map == map && ambient.Contains(s.def) && !s.Ended)
				{
					s.End();
				}
			}
			hushed = true;
			hushEndTick = Find.TickManager.TicksGame + durationTicks;
			Messages.Message("RM_Greentide_SilenceCue".Translate(), MessageTypeDefOf.ThreatBig, historical: false);
		}

		private void Restore()
		{
			hushed = false;
			hushEndTick = -1;
			if (Find.CurrentMap == map)
			{
				AmbientSoundManager.Notify_SwitchedMap();
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref hushed, "hushed", false);
			Scribe_Values.Look(ref hushEndTick, "hushEndTick", -1);
		}
	}
}
