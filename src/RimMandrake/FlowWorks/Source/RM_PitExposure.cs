using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_TEMPERATURE_SOFTENING_1, redesigned 2026-10-11: "exposed to the elements" on vanilla's own temperature path
	/// (design/RimMandrake/pit_exposure_to_the_elements_2026-10-11.md; owner ruling 17, and both cards at 17:25).
	///   1. Exposure: every 250 ticks a spawned pawn on an unroofed, uncovered D=4 cell carries the flat RM_PitExposure
	///      marker hediff; off such a cell it is removed. Its one stage's statOffsets narrow the comfortable range
	///      (ComfyTemperatureMin +n, ComfyTemperatureMax -n; n = Mod Setting pitExposureNarrowing, owner Q1 8 °C), so
	///      vanilla's own Heatstroke and Hypothermia givers start n degrees sooner. There is no other harm and no second
	///      kind of heat: mild weather does nothing, and heatstroke needs real heat (none at night).
	///      HediffComp_PitExposureMarker removes it wherever Tick cannot: off the map, or with the setting off.
	///   2. Resistance: a colony prisoner loses guest resistance only while the elements actually hurt (owner Q2):
	///      Heatstroke or Hypothermia present, or the pawn outside its (narrowed) safe range (RM_PitExposureMath.ElementsHurting).
	///   3. RM_ExposedPrisoner memory for free colonists whose ideoligion minds refused beggars (the Charity
	///      precepts' own structure — FeelsForExposedPrisoners); psychopaths nullify it by trait. The mood
	///      number (-3, 1 day) is PROVISIONAL and goes to the owner. It follows the exposure, not the hurt.
	///   4. Coupling: postfix on RoomTempTracker.NoRoofEqualizationTempChangePerInterval scales the step for a room that is
	///      mostly dug D=4 cells. KEPT until a live check shows it redundant (an exposed cell is unroofed, and vanilla gives
	///      outdoor temperature to any room 25% unroofed or touching the edge): the design's deletion is owed to that check.
	/// </summary>
	public static class RM_PitExposure
	{
		public const int IntervalTicks = 250;

		public static bool IsExposed(Map map, RM_MapComponent_Excavation eng, Pawn p)
		{
			IntVec3 c = p.Position;
			// PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE: down a pit (a person-band pocket at any depth, V6), not "dug 2 m"
			return RM_PitRooms.IsPitFloor(map, eng, c) && !map.roofGrid.Roofed(c);
		}

		/// <summary>
		/// Owner, 2026-09-17: <i>"it should hit compassionate folks like when you turn beggars away and ignore
		/// psychopaths or "hard" morality cultures. Borrow their structure and piggyback, so we don't end up
		/// making a whole new moral axis."</i> MEASURED (SUPERDEEP_SEAM_MEASURE_1 item 6): refusing beggars hurts
		/// exactly the members of an ideoligion holding a Charity precept whose PreceptComp_KnowsMemoryThought
		/// listens for CharityRefused_Beggars (Charity_Worthwhile / _Important / _Essential); an ideoligion
		/// without one does not care. This reads that same fact, so the two can never disagree — no precept
		/// is named here and no new axis exists. Psychopaths are nulled by the ThoughtDef's nullifyingTraits.
		/// </summary>
		public static bool FeelsForExposedPrisoners(Pawn colonist)
		{
			if (!ModsConfig.IdeologyActive || colonist?.Ideo == null)
			{
				return true;
			}
			Ideo ideo = colonist.Ideo;
			if (charityCache.TryGetValue(ideo, out CharityEntry e) && e.tick == Find.TickManager.TicksGame)
			{
				return e.cares;
			}
			bool cares = false;
			List<Precept> precepts = ideo.PreceptsListForReading;
			for (int i = 0; i < precepts.Count && !cares; i++)
			{
				List<PreceptComp> comps = precepts[i].def.comps;
				if (comps == null)
				{
					continue;
				}
				for (int j = 0; j < comps.Count; j++)
				{
					if (comps[j] is PreceptComp_KnowsMemoryThought k && k.eventDef != null
						&& k.eventDef.defName == BeggarRefusalEvent)
					{
						cares = true;
						break;
					}
				}
			}
			if (charityCache.Count > 64)
			{
				charityCache.Clear();   // a per-tick cache keyed by Ideo objects: every reload adds a game's worth of dead ones
			}
			charityCache[ideo] = new CharityEntry { tick = Find.TickManager.TicksGame, cares = cares };
			return cares;
		}

		/// <summary>Vanilla Ideology's HistoryEventDef (Precepts_Charity.xml).</summary>
		public const string BeggarRefusalEvent = "CharityRefused_Beggars";

		private struct CharityEntry
		{
			public int tick;
			public bool cares;
		}

		private static readonly Dictionary<Ideo, CharityEntry> charityCache = new Dictionary<Ideo, CharityEntry>();

		/// <summary>Writes the narrowing setting into the marker's stage (+n on ComfyTemperatureMin, -n on ComfyTemperatureMax).
		/// Cheap, so Tick runs it every interval and a changed setting reaches every exposed pawn within 250 ticks.</summary>
		public static void ApplyNarrowing(HediffDef def)
		{
			List<StatModifier> offsets = def?.stages != null && def.stages.Count > 0 ? def.stages[0].statOffsets : null;
			if (offsets == null)
			{
				return;
			}
			float n = RM_PitExposureMath.Narrowing(RimMandrakeFlowWorksSettings.pitExposureNarrowing);
			for (int i = 0; i < offsets.Count; i++)
			{
				if (offsets[i].stat == StatDefOf.ComfyTemperatureMin)
				{
					offsets[i].value = n;
				}
				else if (offsets[i].stat == StatDefOf.ComfyTemperatureMax)
				{
					offsets[i].value = -n;
				}
			}
		}

		/// <summary>Owner Q2: Heatstroke or Hypothermia present, or the pawn outside its safe range (so one is building).</summary>
		public static bool ElementsHurting(Pawn p)
		{
			bool hediff = p.health.hediffSet.HasHediff(HediffDefOf.Heatstroke) || p.health.hediffSet.HasHediff(HediffDefOf.Hypothermia);
			FloatRange safe = p.SafeTemperatureRange();
			return RM_PitExposureMath.ElementsHurting(hediff, p.AmbientTemperature, safe.min, safe.max);
		}

		public static void Tick(Map map, RM_MapComponent_Excavation eng)
		{
			if (!RimMandrakeFlowWorksSettings.pitExposureEnabled || Find.TickManager.TicksGame % IntervalTicks != 0)
			{
				return;
			}
			HediffDef def = RimMandrakeFlowWorks_DefOf.RM_PitExposure;
			ApplyNarrowing(def);
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			List<Pawn> exposedPrisoners = null;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p.health == null || p.Dead)
				{
					continue;
				}
				bool exposed = IsExposed(map, eng, p);
				Hediff h = def != null ? p.health.hediffSet.GetFirstHediffOfDef(def) : null;
				if (exposed && h == null && def != null)
				{
					p.health.AddHediff(def);
				}
				else if (!exposed && h != null)
				{
					p.health.RemoveHediff(h);
				}
				if (!exposed || !p.IsPrisonerOfColony || p.guest == null)
				{
					continue;
				}
				(exposedPrisoners ?? (exposedPrisoners = new List<Pawn>())).Add(p);
				if (ElementsHurting(p))
				{
					p.guest.resistance = RM_PitExposureMath.NextResistance(p.guest.resistance,
						RimMandrakeFlowWorksSettings.pitResistanceLossMultiplier);
				}
			}
			if (exposedPrisoners != null && RimMandrakeFlowWorksDefs.RM_ExposedPrisoner != null)
			{
				foreach (Pawn colonist in map.mapPawns.FreeColonistsSpawned)
				{
					if (colonist.needs?.mood == null || !FeelsForExposedPrisoners(colonist))
					{
						continue;
					}
					for (int i = 0; i < exposedPrisoners.Count; i++)
					{
						colonist.needs.mood.thoughts.memories.TryGainMemory(RimMandrakeFlowWorksDefs.RM_ExposedPrisoner, exposedPrisoners[i]);
					}
				}
			}
		}
	}

	/// <summary>
	/// The exposure marker's removal wherever <see cref="RM_PitExposure.Tick"/> cannot reach the pawn: the setting is off
	/// (Tick returns at once), or the pawn is not spawned (a caravan, a transport pod, a world pawn). Presence is binary,
	/// so it simply goes (the comp list is rebuilt from the def on load, so saves that held the old recovery comp load
	/// clean). A spawned pawn with the setting on is left to Tick.
	/// </summary>
	public class HediffComp_PitExposureMarker : HediffComp
	{
		public override bool CompShouldRemove => base.CompShouldRemove || !RimMandrakeFlowWorksSettings.pitExposureEnabled || !Pawn.Spawned;
	}

	public class HediffCompProperties_PitExposureMarker : HediffCompProperties
	{
		public HediffCompProperties_PitExposureMarker()
		{
			compClass = typeof(HediffComp_PitExposureMarker);
		}
	}

	[DefOf]
	public static class RimMandrakeFlowWorksDefs
	{
		public static ThoughtDef RM_ExposedPrisoner;

		static RimMandrakeFlowWorksDefs()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RimMandrakeFlowWorksDefs));
		}
	}

	[HarmonyPatch(typeof(RoomTempTracker), "NoRoofEqualizationTempChangePerInterval")]
	[RimMandrake.Shared.PatchFeature("Open-pit exposure", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitExposureEnabled")]
	public static class RM_Patch_PitRoomCoupling
	{
		private static readonly AccessTools.FieldRef<RoomTempTracker, Room> roomField =
			AccessTools.FieldRefAccess<RoomTempTracker, Room>("room");

		public static void Postfix(RoomTempTracker __instance, ref float __result)
		{
			if (__result == 0f || !RimMandrakeFlowWorksSettings.pitExposureEnabled)
			{
				return;
			}
			Room room = roomField(__instance);
			Map map = room?.Map;
			RM_MapComponent_Excavation eng = RM_SuperdeepShooting.EngineFor(map);
			if (!RM_PitRooms.AnyPitFloor(eng))
			{
				return;
			}
			// Room.Cells is an iterator in 1.6: size-gate on CellCount before walking,
			// never copy the room into a list (this runs every 120 ticks per room).
			int total = room.CellCount;
			if (total == 0 || total > 400)
			{
				return;
			}
			int deep = 0;
			foreach (IntVec3 c in room.Cells)
			{
				if (RM_PitRooms.IsPitFloor(map, eng, c))   // PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE: the pit-room test, not D 4
				{
					deep++;
				}
			}
			if (RM_PitExposureMath.IsPitRoom(deep, total))
			{
				__result *= RM_PitExposureMath.Coupling(RimMandrakeFlowWorksSettings.pitTemperatureCoupling);
			}
		}
	}
}
