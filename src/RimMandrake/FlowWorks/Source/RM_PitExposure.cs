using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_TEMPERATURE_SOFTENING_1. Letting a captive roast in an unroofed pit is a tactic that reads as cruel.
	///   1. Coupling: postfix on RoomTempTracker.NoRoofEqualizationTempChangePerInterval (SUPERDEEP_SEAM_MEASURE_1
	///      item 5) scales the step for a room that is mostly dug D=4 cells and unroofed. Vanilla Heatstroke /
	///      Hypothermia do the harm; nothing new is a "kind" of heat.
	///   2. Exposure: every 250 ticks a spawned pawn on an unroofed, uncovered D=4 cell gains RM_PitExposure
	///      severity; a colony prisoner also loses guest resistance (recruitment first). Two independent dials.
	///   3. RM_ExposedPrisoner memory for free colonists whose ideoligion minds refused beggars (the Charity
	///      precepts' own structure — FeelsForExposedPrisoners); psychopaths nullify it by trait. The mood
	///      number (-3, 1 day) is PROVISIONAL and goes to the owner.
	/// </summary>
	public static class RM_PitExposure
	{
		public const int IntervalTicks = 250;

		public static bool IsExposed(Map map, RM_MapComponent_Excavation eng, Pawn p)
		{
			IntVec3 c = p.Position;
			return eng.IsSuperdeepExcavation(c) && !map.roofGrid.Roofed(c) && !Pits.RM_PitCoverUtility.IsCovered(map, c);
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

		public static void Tick(Map map, RM_MapComponent_Excavation eng)
		{
			if (!RimMandrakeFlowWorksSettings.pitExposureEnabled || Find.TickManager.TicksGame % IntervalTicks != 0)
			{
				return;
			}
			HediffDef def = RimMandrakeFlowWorks_DefOf.RM_PitExposure;
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
				if (!exposed && h == null)
				{
					continue;
				}
				if (def != null)
				{
					if (h == null)
					{
						h = p.health.AddHediff(def);
					}
					h.Severity = RM_PitExposureMath.NextSeverity(h.Severity, exposed);
					if (!exposed && h.Severity <= 0f)
					{
						p.health.RemoveHediff(h);
					}
				}
				if (exposed && p.IsPrisonerOfColony && p.guest != null)
				{
					p.guest.resistance = RM_PitExposureMath.NextResistance(p.guest.resistance,
						RimMandrakeFlowWorksSettings.pitResistanceLossMultiplier);
					(exposedPrisoners ?? (exposedPrisoners = new List<Pawn>())).Add(p);
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
			if (eng == null || eng.SuperdeepCellCount == 0)
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
				if (eng.IsSuperdeepExcavation(c))
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
