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
	///
	/// FEVER_WOOD_MECHANICS_1 F2 reuses this class from
	/// RimMandrake.EnvironmentalHazards via TriggerHush rather than the
	/// PredatorHunt path above — a mirror-break event has no carrying pawn
	/// to key off. mandrake.rm.environmentalhazards depends on
	/// mandrake.rm.creaturebehaviors (About.xml) the same way
	/// mandrake.rm.shipvermin already does for its own cross-reference.
	/// </summary>
	public class RM_MapComponent_SilenceCue : MapComponent
	{
		private const int CheckIntervalTicks = 60;

		/// <summary>MAP_SILENCE_SINGLE_OWNER_1: the one place that decides whether this map is quiet. Callers register a
		/// named reason (AddReason/RemoveReason); sound comes back only when the last reason leaves.</summary>
		public const string ReasonPredatorHunt = "predatorHunt";
		public const string ReasonExternal = "external";

		private readonly Dictionary<string, int> reasons = new Dictionary<string, int>();
		// legacy save fields (pre-FV-3): read once, folded into reasons
		private bool hushed;
		private int hushEndTick = -1;

		public bool IsHushed => reasons.Count > 0;

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
			if (RM_SilenceReasons.Expire(reasons, Find.TickManager.TicksGame))
			{
				Restore();
			}
			if (!reasons.ContainsKey(ReasonPredatorHunt))
			{
				ScanForTrigger();
			}
		}

		/// <summary>
		/// FEVER_WOOD_MECHANICS_1 F2 external trigger. A sibling mod (a
		/// biome kit that reuses this cue for its own "everything goes
		/// silent to watch" beat, per the_fever_wood.md §9) hushes the map
		/// from an event with no PredatorHunt pawn involved — this is that
		/// public entry point, closing the gap the F2 spike's own header
		/// named ("no public API for 'hush now' from an unrelated event").
		/// Same mod-option gate as the predator-triggered path, so turning
		/// the cue off in Mod Settings silences both callers. If already
		/// hushed, extends the window to the later of the two ends rather
		/// than restarting it (an overlapping trigger should not shorten an
		/// existing hush).
		/// </summary>
		public void TriggerHush(int durationTicks)
		{
			if (!RM_CreatureBehaviorsSettings.silenceCueEnabled)
			{
				return; // mod option: silence cue disabled
			}
			bool wasHushed = IsHushed;
			AddReason(ReasonExternal, Find.TickManager.TicksGame + durationTicks);
			if (!wasHushed)
			{
				Messages.Message("RM_Greentide_SilenceCue".Translate(), MessageTypeDefOf.ThreatBig, historical: false);
			}
		}

		/// <summary>
		/// MAP_SILENCE_SINGLE_OWNER_1 (FV-3): register a reason for this map to be quiet. endTick is a game tick, or
		/// RM_SilenceReasons.Indefinite to hold until RemoveReason(key). Ends the biome's ambient sustainers if this is
		/// the first reason; a later reason never shortens an earlier one under the same key. Not gated by the
		/// silence-cue setting: callers gate their own trigger. Returns true when this call started the hush.
		/// </summary>
		public bool AddReason(string key, int endTick)
		{
			bool started = RM_SilenceReasons.Add(reasons, key, endTick);
			if (started)
			{
				EndAmbientSustainers();
			}
			return started;
		}

		/// <summary>Withdraws a reason. Ambient sound is restored only when no other reason is still holding the map quiet.</summary>
		public void RemoveReason(string key)
		{
			if (RM_SilenceReasons.Remove(reasons, key))
			{
				Restore();
			}
		}

		private void ScanForTrigger()
		{
			if (!RM_CreatureBehaviorsSettings.silenceCueEnabled)
			{
				return; // mod option: predator-hunt silence cue disabled
			}
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
					bool wasHushed = IsHushed;
					AddReason(ReasonPredatorHunt, Find.TickManager.TicksGame + ext.hushDurationTicks);
					if (!wasHushed)
					{
						Messages.Message("RM_Greentide_SilenceCue".Translate(), MessageTypeDefOf.ThreatBig, historical: false);
					}
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

		private void EndAmbientSustainers()
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
		}

		private void Restore()
		{
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
			// Only timed reasons are saved: an Indefinite one (the FeverWood sentinel) re-registers itself when its limb respawns on load.
			List<string> keys = null;
			List<int> ends = null;
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				keys = new List<string>();
				ends = new List<int>();
				foreach (KeyValuePair<string, int> kv in reasons)
				{
					if (kv.Value != RM_SilenceReasons.Indefinite)
					{
						keys.Add(kv.Key);
						ends.Add(kv.Value);
					}
				}
			}
			Scribe_Collections.Look(ref keys, "reasonKeys", LookMode.Value);
			Scribe_Collections.Look(ref ends, "reasonEnds", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				reasons.Clear();
				if (keys != null && ends != null)
				{
					for (int i = 0; i < keys.Count && i < ends.Count; i++)
					{
						reasons[keys[i]] = ends[i];
					}
				}
				if (hushed && reasons.Count == 0)
				{
					reasons[ReasonPredatorHunt] = hushEndTick;
				}
				hushed = false;
				hushEndTick = -1;
			}
		}
	}
}
