using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Utinni.EggReckoning
{
	/// <summary>
	/// WEBWORK_EGG_RECKONING_QUEST_1, §3: "one quest part: at the night tick
	/// after a completed plant, spawn one hostile RM_Ollathrix at the egg's
	/// cell, despawn the egg, wake the room." Also carries §2d's "egg found
	/// before hatch" per-hour discovery roll, since the design's own table lists
	/// it as part of this same staged wait.
	///
	/// Enabled by inSignalEnable=EggPlanted (RM_QuestNode_EggPlantWatcher's own
	/// outSignalPlanted), so it only starts waiting once the plant has actually
	/// landed undetected.
	///
	/// Juvenile age: RM_Ollathrix's own lifeStageAges puts AnimalJuvenile at
	/// [0.2, 0.4) of lifeExpectancy (14y) = [2.8y, 5.6y) — fixedBiologicalAgeYears
	/// defaults to 4.0y, the INVENTED midpoint, disclosed in this mod's About.xml
	/// and in RUT_Reckoning.xml's own header. No new PawnKindDef (§0 ruling 2) —
	/// same RM_Ollathrix kind, just a fixed age, the same
	/// PawnGenerationRequest.FixedBiologicalAge mechanism vanilla itself uses for
	/// young-animal incidents.
	///
	/// Hostility: PawnGenerator.GeneratePawn with faction=null (no owner) then
	/// TryStartMentalState(ManhunterPermanent) is the exact pattern
	/// IncidentWorker_AggressiveAnimals.cs and Scripts_ItemPodThreat.xml's own
	/// manhunter-pack reward-threat quest already use for "a real, spawned,
	/// hostile-to-everyone animal" — not invented, confirmed by reading both
	/// live this session.
	///
	/// Discovery-before-hatch and the night window are both real per-tick reads
	/// (GenLocalDate.HourOfDay, Rand.Chance) rather than a single dice roll at
	/// plant time, so a save/reload mid-wait resumes correctly with no extra
	/// Scribe state beyond lastHourChecked.
	/// </summary>
	public class RM_QuestPart_EggHatch : QuestPartActivable
	{
		public MapParent site;

		public string outSignalHatched;

		public string outSignalFoundBeforeHatch;

		public float fixedBiologicalAgeYears = 4f;

		public float discoveryChancePerHour = 0.03f;

		public int nightStartHour = 23;

		public int nightEndHour = 2;

		private int lastHourChecked = -1;

		private static ThingDef eggDefCached;

		private static PawnKindDef ollathrixKindCached;

		private static ThingDef EggDef
		{
			get
			{
				if (eggDefCached == null)
				{
					eggDefCached = DefDatabase<ThingDef>.GetNamedSilentFail("RM_OllathrixEgg");
				}
				return eggDefCached;
			}
		}

		private static PawnKindDef OllathrixKind
		{
			get
			{
				if (ollathrixKindCached == null)
				{
					ollathrixKindCached = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Ollathrix");
				}
				return ollathrixKindCached;
			}
		}

		public override IEnumerable<GlobalTargetInfo> QuestLookTargets
		{
			get
			{
				foreach (GlobalTargetInfo t in base.QuestLookTargets)
				{
					yield return t;
				}
				if (site != null)
				{
					yield return site;
				}
			}
		}

		public override void QuestPartTick()
		{
			base.QuestPartTick();
			if (site == null || !site.HasMap)
			{
				return;
			}
			Map map = site.Map;
			int hour = GenLocalDate.HourOfDay(map);
			if (hour == lastHourChecked)
			{
				return;
			}
			lastHourChecked = hour;

			if (Rand.Chance(discoveryChancePerHour))
			{
				FinishFoundBeforeHatch(map);
				return;
			}
			if (InNightWindow(hour))
			{
				DoHatch(map);
			}
		}

		private bool InNightWindow(int hour)
		{
			if (nightStartHour <= nightEndHour)
			{
				return hour >= nightStartHour && hour < nightEndHour;
			}
			// wraps midnight, e.g. 23 -> 2
			return hour >= nightStartHour || hour < nightEndHour;
		}

		private Thing FindEgg(Map map)
		{
			ThingDef eggDef = EggDef;
			if (eggDef == null)
			{
				return null;
			}
			List<Thing> eggs = map.listerThings.ThingsOfDef(eggDef);
			for (int i = 0; i < eggs.Count; i++)
			{
				if (eggs[i] != null && eggs[i].Spawned)
				{
					return eggs[i];
				}
			}
			return null;
		}

		private void FinishFoundBeforeHatch(Map map)
		{
			Thing egg = FindEgg(map);
			egg?.Destroy();
			SendAndComplete(outSignalFoundBeforeHatch);
		}

		private void DoHatch(Map map)
		{
			Thing egg = FindEgg(map);
			IntVec3 cell = egg != null ? egg.Position : (site.HasMap ? map.Center : IntVec3.Invalid);
			egg?.Destroy();

			PawnKindDef kind = OllathrixKind;
			if (kind != null && cell.IsValid && cell.InBounds(map))
			{
				PawnGenerationRequest request = new PawnGenerationRequest(
					kind,
					faction: null,
					context: PawnGenerationContext.NonPlayer,
					tile: map.Tile,
					forceGenerateNewPawn: true,
					allowDowned: false,
					canGeneratePawnRelations: false,
					mustBeCapableOfViolence: true,
					fixedBiologicalAge: fixedBiologicalAgeYears,
					fixedChronologicalAge: fixedBiologicalAgeYears);
				Pawn spider = PawnGenerator.GeneratePawn(request);
				if (spider != null)
				{
					IntVec3 spawnCell = cell.Standable(map) ? cell : CellFinder.RandomClosewalkCellNear(cell, map, 3);
					GenSpawn.Spawn(spider, spawnCell, map);
					spider.mindState?.mentalStateHandler?.TryStartMentalState(MentalStateDefOf.ManhunterPermanent);
				}
			}

			SendAndComplete(outSignalHatched);
		}

		private void SendAndComplete(string signal)
		{
			if (!signal.NullOrEmpty())
			{
				Find.SignalManager.SendSignal(new Signal(signal));
			}
			Complete();
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_References.Look(ref site, "site");
			Scribe_Values.Look(ref outSignalHatched, "outSignalHatched");
			Scribe_Values.Look(ref outSignalFoundBeforeHatch, "outSignalFoundBeforeHatch");
			Scribe_Values.Look(ref fixedBiologicalAgeYears, "fixedBiologicalAgeYears", 4f);
			Scribe_Values.Look(ref discoveryChancePerHour, "discoveryChancePerHour", 0.03f);
			Scribe_Values.Look(ref nightStartHour, "nightStartHour", 23);
			Scribe_Values.Look(ref nightEndHour, "nightEndHour", 2);
			Scribe_Values.Look(ref lastHourChecked, "lastHourChecked", -1);
		}
	}
}
