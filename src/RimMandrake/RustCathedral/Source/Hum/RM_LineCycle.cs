using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.RustCathedral.Hum
{
	// RUSTCATHEDRAL_BASE_FINISH_BUILD_1 part 1 -- the line-cycle. Sheet §3: "a mile of machinery turning over in
	// its sleep, and every living thing on the plateau stops until it passes".
	//
	// ⛔ Ban 1: nothing here explains the mind or the hum. The only player text is the one message, which names
	// what was felt and never why.
	//
	// Shape: the IncidentDef (category Misc, baseChance 0 so the storyteller never picks it on its own) is the one
	// entry point for a firing, from the MTB roll below or a dev/debug trigger. The roll itself lives in this map
	// component because the MTB is a Mod Settings value, which a def's baseChance cannot be. One roll lasts
	// 60..120 s of game time (3600..7200 ticks at 1x), travelling along one map axis; a pawn stands still from the
	// start until the roll front passes its own coordinate.
	public static class RM_LineCycleMath
	{
		/// <summary>Front coordinate (in cells along the travel axis, 0 = the start edge) at elapsed ticks.</summary>
		public static float FrontAt(int elapsed, int duration, int axisLength)
		{
			if (duration <= 0)
			{
				return axisLength + 1f;
			}
			return Mathf.Clamp01((float)elapsed / duration) * (axisLength + 2f) - 1f;
		}

		/// <summary>Elapsed tick at which the front reaches coordinate c (0 = the start edge).</summary>
		public static int PassTick(float c, int duration, int axisLength)
		{
			return Mathf.CeilToInt(duration * (c + 1f) / (axisLength + 2f));
		}

		/// <summary>A cell's coordinate measured from the edge the roll starts at.</summary>
		public static int Coord(IntVec3 cell, bool alongX, bool reversed, IntVec3 size)
		{
			int len = alongX ? size.x : size.z;
			int raw = alongX ? cell.x : cell.z;
			return reversed ? len - 1 - raw : raw;
		}
	}

	public class RM_IncidentWorker_LineCycle : IncidentWorker
	{
		public const string TargetBiomeDefName = "RM_RustCathedral";

		protected override bool CanFireNowSub(IncidentParms parms)
		{
			if (!base.CanFireNowSub(parms) || !RustCathedralHumSettings.lineCycleEnabled)
			{
				return false;
			}
			Map map = parms.target as Map;
			if (map?.Biome == null || map.Biome.defName != TargetBiomeDefName)
			{
				return false;
			}
			RM_MapComponent_LineCycle comp = map.GetComponent<RM_MapComponent_LineCycle>();
			return comp != null && !comp.Active;
		}

		protected override bool TryExecuteWorker(IncidentParms parms)
		{
			Map map = parms.target as Map;
			RM_MapComponent_LineCycle comp = map?.GetComponent<RM_MapComponent_LineCycle>();
			if (comp == null || comp.Active)
			{
				return false;
			}
			comp.Begin();
			Messages.Message("Something turned over under the plate.", MessageTypeDefOf.NeutralEvent, historical: true);
			return true;
		}
	}

	public class RM_MapComponent_LineCycle : MapComponent
	{
		public const int SweepInterval = 30;

		private const int MinDurationTicks = 3600;

		private int startTick = -1;
		private int durationTicks;
		private bool alongX;
		private bool reversed;

		private Sustainer roll;

		private static JobDef stillDef;
		private static ThoughtDef feltDef;
		private static SoundDef rollDef;
		private static IncidentDef incidentDef;

		private static readonly AccessTools.FieldRef<Sustainer, GameObject> RootObject =
			AccessTools.FieldRefAccess<Sustainer, GameObject>("worldRootObject");

		public RM_MapComponent_LineCycle(Map map)
			: base(map)
		{
		}

		public bool Active => startTick >= 0;

		public int Elapsed => Active ? Find.TickManager.TicksGame - startTick : -1;

		public int DurationTicks => durationTicks;

		private int AxisLength => alongX ? map.Size.x : map.Size.z;

		private static JobDef StillDef => stillDef ?? (stillDef = DefDatabase<JobDef>.GetNamedSilentFail("RM_Job_LineCycleStill"));

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref startTick, "startTick", -1);
			Scribe_Values.Look(ref durationTicks, "durationTicks", 0);
			Scribe_Values.Look(ref alongX, "alongX", false);
			Scribe_Values.Look(ref reversed, "reversed", false);
		}

		public override void MapRemoved()
		{
			base.MapRemoved();
			EndSound();
		}

		/// <summary>Starts a roll. Duration from Mod Settings (seconds of game time, 60 ticks each).</summary>
		public void Begin()
		{
			float lo = Mathf.Max(1f, RustCathedralHumSettings.lineCycleMinSeconds);
			float hi = Mathf.Max(lo, RustCathedralHumSettings.lineCycleMaxSeconds);
			durationTicks = Mathf.Max(MinDurationTicks, Mathf.RoundToInt(Rand.Range(lo, hi) * 60f));
			alongX = Rand.Bool;
			reversed = Rand.Bool;
			startTick = Find.TickManager.TicksGame;
			RM_MapComponent_BiomeAttitude.SetLineCycleDrop(map, true);
			Sweep();
		}

		public override void MapComponentTick()
		{
			if (!Active)
			{
				MaybeRoll();
				return;
			}
			if (!RustCathedralHumSettings.lineCycleEnabled)
			{
				Finish(givesThought: false);
				return;
			}
			if (roll != null && !roll.Ended)
			{
				roll.Maintain();
			}
			int elapsed = Elapsed;
			if (elapsed >= durationTicks)
			{
				Finish(givesThought: true);
				return;
			}
			if (elapsed % SweepInterval == 0)
			{
				Sweep();
			}
		}

		private void MaybeRoll()
		{
			if (!RustCathedralHumSettings.lineCycleEnabled || !map.IsHashIntervalTick(250))
			{
				return;
			}
			if (map.Biome == null || map.Biome.defName != RM_IncidentWorker_LineCycle.TargetBiomeDefName)
			{
				return;
			}
			if (!Rand.MTBEventOccurs(Mathf.Max(0.1f, RustCathedralHumSettings.lineCycleMtbDays), GenDate.TicksPerDay, 250f))
			{
				return;
			}
			IncidentDef def = incidentDef ?? (incidentDef = DefDatabase<IncidentDef>.GetNamedSilentFail("RM_LineCycle"));
			if (def == null)
			{
				return;
			}
			IncidentParms parms = StorytellerUtility.DefaultParmsNow(def.category, map);
			if (def.Worker.CanFireNow(parms))
			{
				def.Worker.TryExecute(parms);
			}
		}

		/// <summary>True when this pawn is one the roll stops: alive, awake, spawned, not a colonist, not a hostile
		/// mechanoid, not drafted.</summary>
		public static bool Stops(Pawn p)
		{
			if (p == null || !p.Spawned || p.Dead || p.Downed || p.jobs == null || p.IsColonist || p.Drafted)
			{
				return false;
			}
			if (p.RaceProps.IsMechanoid && p.HostileTo(Faction.OfPlayer))
			{
				return false;
			}
			return p.Awake();
		}

		private void Sweep()
		{
			JobDef still = StillDef;
			int elapsed = Elapsed;
			float front = RM_LineCycleMath.FrontAt(elapsed, durationTicks, AxisLength);
			UpdateSound(front);
			ThrowDust(front);
			if (still == null)
			{
				return;
			}
			List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (!Stops(p))
				{
					continue;
				}
				int c = RM_LineCycleMath.Coord(p.Position, alongX, reversed, map.Size);
				int pass = RM_LineCycleMath.PassTick(c, durationTicks, AxisLength);
				int remaining = pass - elapsed;
				if (remaining <= 0 || p.CurJobDef == still)
				{
					continue;
				}
				Job job = JobMaker.MakeJob(still);
				job.expiryInterval = remaining + SweepInterval;
				job.checkOverrideOnExpire = true;
				p.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: false);
			}
		}

		private void Finish(bool givesThought)
		{
			startTick = -1;
			EndSound();
			RM_MapComponent_BiomeAttitude.SetLineCycleDrop(map, false);
			if (!givesThought)
			{
				return;
			}
			ThoughtDef felt = feltDef ?? (feltDef = DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_FeltTheGroundTurn"));
			if (felt == null)
			{
				return;
			}
			List<Pawn> colonists = map.mapPawns.FreeColonistsSpawned;
			for (int i = 0; i < colonists.Count; i++)
			{
				colonists[i].needs?.mood?.thoughts?.memories?.TryGainMemory(felt);
			}
		}

		private IntVec3 FrontCell(float front)
		{
			int c = Mathf.Clamp(Mathf.RoundToInt(front), 0, AxisLength - 1);
			int raw = reversed ? AxisLength - 1 - c : c;
			return alongX ? new IntVec3(raw, 0, map.Size.z / 2) : new IntVec3(map.Size.x / 2, 0, raw);
		}

		private void UpdateSound(float front)
		{
			IntVec3 cell = FrontCell(front);
			if (roll == null || roll.Ended)
			{
				rollDef = rollDef ?? DefDatabase<SoundDef>.GetNamedSilentFail("RM_LineCycleRoll");
				roll = rollDef?.TrySpawnSustainer(SoundInfo.InMap(new TargetInfo(cell, map), MaintenanceType.PerTick));
				return;
			}
			// A cell-target sustainer never re-reads its position (Sustainer.UpdateRootObjectPosition runs only for a
			// Thing maker), so the roll is moved by hand: same game object, new spot, no restart click.
			GameObject root = RootObject(roll);
			if (root != null)
			{
				root.transform.position = cell.ToVector3ShiftedWithAltitude(0f);
			}
		}

		private void EndSound()
		{
			if (roll != null && !roll.Ended)
			{
				roll.End();
			}
			roll = null;
		}

		private void ThrowDust(float front)
		{
			if (front < 0f || front >= AxisLength)
			{
				return;
			}
			int c = Mathf.RoundToInt(front);
			int raw = reversed ? AxisLength - 1 - c : c;
			int across = alongX ? map.Size.z : map.Size.x;
			for (int j = Rand.Range(0, 6); j < across; j += 6)
			{
				IntVec3 cell = alongX ? new IntVec3(raw, 0, j) : new IntVec3(j, 0, raw);
				if (cell.InBounds(map) && !cell.Fogged(map))
				{
					FleckMaker.ThrowDustPuffThick(cell.ToVector3Shifted(), map, 0.8f, new Color(0.55f, 0.4f, 0.3f));
				}
			}
		}

		// ---- proof hooks (debug [Tool]s / jawa/static_call) ----

		/// <summary>"LINECYCLE active A | elapsed E/D | stopped S/eligible N" for the current map.</summary>
		public static string ProofState()
		{
			Map m = Find.CurrentMap;
			RM_MapComponent_LineCycle comp = m?.GetComponent<RM_MapComponent_LineCycle>();
			if (comp == null)
			{
				return "REFUSED: no current map";
			}
			int stopped = 0, eligible = 0;
			foreach (Pawn p in m.mapPawns.AllPawnsSpawned)
			{
				if (Stops(p))
				{
					eligible++;
					if (p.CurJobDef == StillDef)
					{
						stopped++;
					}
				}
			}
			return "LINECYCLE active " + comp.Active + " | elapsed " + comp.Elapsed + "/" + comp.durationTicks
				+ " | stopped " + stopped + "/eligible " + eligible + " | band " + RM_MapComponent_BiomeAttitude.GetBand(m);
		}
	}
}
