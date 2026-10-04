// BLUEDESERT_MECHANICS_BUILD_1 §5 — the living soundscape: the ossivel choir
// with its silence alarm, and the virr fields the wind plays.
//
// Audio ruling 2026-10-03 (owner: "Just use vanilla until we get around to
// sound work"): both voices are vanilla SoundDefs referenced by name, never
// retuned clips. Choir = Ideology RitualSustainer_Christian (a sustained
// choral loop, sustain=True); virr = Core Ambient_Wind_Desolate (a thin
// high-altitude wind loop). The virr's pitchFactor is the ruled MECHANIC, not
// a retint: the description promises "the pitch climbs as the charge inside
// ripens", so a keen ear hears which field is close to dangerous.
//
// The choir (the stub hookup point on RM_Ossivel in RM_BlueDesertFauna.xml):
// a sustainer keyed to pack presence (>= MinSingers awake ossivels on the map)
// that STOPS when any pawn bigger than IntruderBodySize comes within
// SilenceRadius of a singer, and stays stopped SilenceHoldTicks after the last
// intruder leaves ("you have until the echo dies"). The silence is the alarm:
// nothing else plays.
//
// Numbers marked PROVISIONAL are first guesses (owner ruling 2026-10-03:
// provisional first-guess numbers allowed, marked as such).
//
// Gates: masterEnabled && ossivelChoirEnabled; masterEnabled && virrSongEnabled.
// Proof hook (bridge jawa/static_call): RM_BlueDesertSoundProof.ProofChoir /
// ProofVirr, used by validation.py chain "soundscape".

using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.BlueDesert
{
    public class RM_MapComponent_BlueDesertSoundscape : MapComponent
    {
        public const string OssivelDefName = "RM_Ossivel";
        public const string VirrDefName = "RM_Virr";
        public const string ChoirSoundDefName = "RitualSustainer_Christian";
        public const string VirrSoundDefName = "Ambient_Wind_Desolate";

        public const int ScanIntervalTicks = 250;
        public const int MinSingers = 3;                    // PROVISIONAL
        public const float SilenceRadius = 15f;             // PROVISIONAL
        public const float IntruderBodySize = 1.0f;         // the stub's "above bodySize ~1.0"
        public const int SilenceHoldTicks = 900;            // PROVISIONAL (~15 s at 1x)
        public const float VirrMinWind = 0.5f;              // PROVISIONAL
        public const float VirrListenRadius = 30f;          // PROVISIONAL
        public const float VirrPitchMin = 0.85f;            // PROVISIONAL
        public const float VirrPitchMax = 1.35f;            // PROVISIONAL
        public const float VirrRepositionCells = 10f;

        // State, readable by the proof hook (and a debugger).
        public bool ChoirSinging { get; private set; }
        public bool ChoirSilenced { get; private set; }
        public int SingerCount { get; private set; }
        public int silencedUntilTick = -1;
        public bool VirrSinging { get; private set; }
        public float VirrPitch { get; private set; } = 1f;

        private Sustainer choir;
        private IntVec3 choirAt = IntVec3.Invalid;
        private Sustainer virr;
        private IntVec3 virrAt = IntVec3.Invalid;

        private static ThingDef ossivelDef, virrDef;
        private static SoundDef choirSound, virrSound;
        private static bool resolved;

        public RM_MapComponent_BlueDesertSoundscape(Map map) : base(map) { }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            ossivelDef = DefDatabase<ThingDef>.GetNamedSilentFail(OssivelDefName);
            virrDef = DefDatabase<ThingDef>.GetNamedSilentFail(VirrDefName);
            choirSound = DefDatabase<SoundDef>.GetNamedSilentFail(ChoirSoundDefName);
            virrSound = DefDatabase<SoundDef>.GetNamedSilentFail(VirrSoundDefName);
        }

        public static bool ChoirGate => RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.ossivelChoirEnabled;
        public static bool VirrGate => RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.virrSongEnabled;

        public override void MapComponentTick()
        {
            if (map.IsHashIntervalTick(ScanIntervalTicks))
            {
                Rescan(Find.TickManager.TicksGame, playSound: true);
            }
            if (choir != null && !choir.Ended) choir.Maintain();
            if (virr != null && !virr.Ended) virr.Maintain();
        }

        /// <summary>One evaluation of both voices. Public so the proof hook can
        /// drive it on a synthetic clock without waiting game time.</summary>
        public void Rescan(int now, bool playSound)
        {
            Resolve();
            ScanChoir(now);
            ScanVirr();
            if (!playSound) return;
            UpdateChoirSustainer();
            UpdateVirrSustainer();
        }

        private void ScanChoir(int now)
        {
            SingerCount = 0;
            ChoirSilenced = false;
            if (!ChoirGate || ossivelDef == null)
            {
                ChoirSinging = false;
                return;
            }
            List<Pawn> singers = new List<Pawn>();
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.def == ossivelDef && !p.Dead && !p.Downed && !(p.CurJob != null && p.CurJob.def == JobDefOf.LayDown))
                    singers.Add(p);
            }
            SingerCount = singers.Count;
            bool intruder = false;
            for (int i = 0; i < pawns.Count && !intruder; i++)
            {
                Pawn p = pawns[i];
                if (p.def == ossivelDef || p.Dead || p.BodySize <= IntruderBodySize) continue;
                for (int j = 0; j < singers.Count; j++)
                {
                    if (p.Position.InHorDistOf(singers[j].Position, SilenceRadius))
                    {
                        intruder = true;
                        break;
                    }
                }
            }
            if (intruder) silencedUntilTick = now + SilenceHoldTicks;
            ChoirSilenced = SingerCount >= MinSingers && now < silencedUntilTick;
            ChoirSinging = SingerCount >= MinSingers && !ChoirSilenced;
            if (ChoirSinging)
            {
                IntVec3 sum = IntVec3.Zero;
                foreach (Pawn s in singers) sum += s.Position;
                choirTarget = new IntVec3(sum.x / singers.Count, 0, sum.z / singers.Count);
            }
        }

        private IntVec3 choirTarget = IntVec3.Invalid;
        private IntVec3 virrTarget = IntVec3.Invalid;

        private void ScanVirr()
        {
            VirrSinging = false;
            if (!VirrGate || virrDef == null || map.windManager.WindSpeed < VirrMinWind) return;
            IntVec3 ear = map == Find.CurrentMap ? Find.CameraDriver.MapPosition : map.Center;
            Plant best = null;
            float bestDist = VirrListenRadius * VirrListenRadius;
            List<Thing> virrs = map.listerThings.ThingsOfDef(virrDef);
            for (int i = 0; i < virrs.Count; i++)
            {
                float d = (virrs[i].Position - ear).LengthHorizontalSquared;
                if (d <= bestDist)
                {
                    bestDist = d;
                    best = virrs[i] as Plant;
                }
            }
            if (best == null) return;
            VirrSinging = true;
            // "the pitch climbs as the charge inside ripens": growth is the ripening.
            VirrPitch = Mathf.Lerp(VirrPitchMin, VirrPitchMax, Mathf.Clamp01(best.Growth));
            virrTarget = best.Position;
        }

        private void UpdateChoirSustainer()
        {
            if (!ChoirSinging || choirSound == null)
            {
                EndChoir();
                return;
            }
            if (choir == null || choir.Ended || !choirAt.InHorDistOf(choirTarget, VirrRepositionCells))
            {
                EndChoir();
                choirAt = choirTarget;
                choir = choirSound.TrySpawnSustainer(SoundInfo.InMap(new TargetInfo(choirAt, map), MaintenanceType.PerTick));
            }
        }

        private void UpdateVirrSustainer()
        {
            if (!VirrSinging || virrSound == null)
            {
                EndVirr();
                return;
            }
            if (virr == null || virr.Ended || !virrAt.InHorDistOf(virrTarget, VirrRepositionCells))
            {
                EndVirr();
                virrAt = virrTarget;
                SoundInfo info = SoundInfo.InMap(new TargetInfo(virrAt, map), MaintenanceType.PerTick);
                info.pitchFactor = VirrPitch;
                virr = virrSound.TrySpawnSustainer(info);
            }
        }

        private void EndChoir()
        {
            if (choir != null && !choir.Ended) choir.End();
            choir = null;
        }

        private void EndVirr()
        {
            if (virr != null && !virr.Ended) virr.End();
            virr = null;
        }

        public override void MapRemoved()
        {
            EndChoir();
            EndVirr();
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref silencedUntilTick, "silencedUntilTick", -1);
        }
    }

    // Proof hooks for jawa/static_call. Each spawns real pawns/plants on the
    // current map, runs the SHIPPED Rescan on a synthetic clock with sound off,
    // reads the state, destroys everything it made and restores settings.
    public static class RM_BlueDesertSoundProof
    {
        private static IntVec3 FindSpot(Map map)
        {
            foreach (IntVec3 c in map.AllCells)
            {
                if (c.x < 40 || c.z < 40 || c.x > map.Size.x - 40 || c.z > map.Size.z - 40) continue;
                if (c.x % 7 != 0 || c.z % 7 != 0) continue;
                bool ok = true;
                foreach (IntVec3 o in GenRadial.RadialCellsAround(c, 20f, true))
                {
                    if (!o.InBounds(map) || !o.Standable(map) || o.GetFirstPawn(map) != null) { ok = false; break; }
                }
                if (ok) return c;
            }
            return IntVec3.Invalid;
        }

        /// <summary>"on": 4 ossivels alone sing; a muffalo (body 2.4) 5 cells
        /// away silences them; it leaves and they stay silent until the hold
        /// expires, then sing again. "off" (toggle false): never sing.</summary>
        public static string ProofChoir(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            var comp = map.GetComponent<RM_MapComponent_BlueDesertSoundscape>();
            if (comp == null) return "FAIL: RM_MapComponent_BlueDesertSoundscape not on the map";
            PawnKindDef oss = DefDatabase<PawnKindDef>.GetNamedSilentFail(RM_MapComponent_BlueDesertSoundscape.OssivelDefName);
            PawnKindDef big = DefDatabase<PawnKindDef>.GetNamedSilentFail("Muffalo");
            if (oss == null || big == null) return "UNMEASURED: RM_Ossivel / Muffalo pawnkind not loaded";
            bool on = mode != "off";
            bool savedMaster = RM_BlueDesertSettings.masterEnabled, savedChoir = RM_BlueDesertSettings.ossivelChoirEnabled;
            int savedHold = comp.silencedUntilTick;
            var made = new List<Pawn>();
            try
            {
                RM_BlueDesertSettings.masterEnabled = true;
                RM_BlueDesertSettings.ossivelChoirEnabled = on;
                // Any pre-existing big pawn near the spot would poison the read: FindSpot demands an empty 20-cell disc.
                IntVec3 spot = FindSpot(map);
                if (!spot.IsValid) return "UNMEASURED: no empty standable 20-cell disc on this map";
                for (int i = 0; i < 4; i++)
                {
                    Pawn p = PawnGenerator.GeneratePawn(oss);
                    GenSpawn.Spawn(p, spot + new IntVec3(i, 0, 0), map);
                    made.Add(p);
                }
                comp.silencedUntilTick = -1;
                int now = Find.TickManager.TicksGame;
                comp.Rescan(now, playSound: false);
                bool alone = comp.ChoirSinging;
                int singers = comp.SingerCount;
                Pawn m = PawnGenerator.GeneratePawn(big);
                GenSpawn.Spawn(m, spot + new IntVec3(0, 0, 5), map);
                made.Add(m);
                comp.Rescan(now + 1, playSound: false);
                bool near = comp.ChoirSinging, silenced = comp.ChoirSilenced;
                m.DeSpawn();
                comp.Rescan(now + 2, playSound: false);
                bool echo = comp.ChoirSinging;
                comp.Rescan(now + 2 + RM_MapComponent_BlueDesertSoundscape.SilenceHoldTicks + 1, playSound: false);
                bool after = comp.ChoirSinging;
                string st = string.Format("singers={0} alone={1} intruder={2}/silenced={3} echo={4} after_hold={5}",
                    singers, alone, near, silenced, echo, after);
                if (on)
                {
                    if (singers < 4) return "UNMEASURED: only " + singers + " of 4 spawned ossivels counted (asleep?) " + st;
                    if (!alone) return "FAIL: a lone pack of 4 does not sing " + st;
                    if (near || !silenced) return "FAIL: a muffalo 5 cells away did not silence the choir " + st;
                    if (echo) return "FAIL: the choir resumed the moment the intruder left (no echo hold) " + st;
                    if (!after) return "FAIL: the choir never resumed after the hold " + st;
                    return "PASS " + st;
                }
                if (alone || near || echo || after) return "FAIL: ossivelChoirEnabled off but the choir sang " + st;
                return "PASS off " + st;
            }
            finally
            {
                foreach (Pawn p in made) { if (!p.Destroyed) p.Destroy(); }
                RM_BlueDesertSettings.masterEnabled = savedMaster;
                RM_BlueDesertSettings.ossivelChoirEnabled = savedChoir;
                comp.silencedUntilTick = savedHold;
                comp.Rescan(Find.TickManager.TicksGame, playSound: true);
            }
        }

        /// <summary>"on": a virr at the camera sings in wind, with a higher pitch
        /// at full growth than as a seedling, and is silent in still air.
        /// "off" (toggle false): never sings.</summary>
        public static string ProofVirr(string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            var comp = map.GetComponent<RM_MapComponent_BlueDesertSoundscape>();
            if (comp == null) return "FAIL: RM_MapComponent_BlueDesertSoundscape not on the map";
            ThingDef virrDef = DefDatabase<ThingDef>.GetNamedSilentFail(RM_MapComponent_BlueDesertSoundscape.VirrDefName);
            if (virrDef == null) return "UNMEASURED: RM_Virr not loaded";
            bool on = mode != "off";
            bool savedMaster = RM_BlueDesertSettings.masterEnabled, savedVirr = RM_BlueDesertSettings.virrSongEnabled;
            Plant plant = null;
            try
            {
                RM_BlueDesertSettings.masterEnabled = true;
                RM_BlueDesertSettings.virrSongEnabled = on;
                IntVec3 ear = Find.CameraDriver.MapPosition;
                if (map.listerThings.ThingsOfDef(virrDef).Count > 0)
                    return "UNMEASURED: wild virr already on the map would mask the planted one";
                IntVec3 cell = IntVec3.Invalid;
                foreach (IntVec3 c in GenRadial.RadialCellsAround(ear, 8f, true))
                {
                    if (c.InBounds(map) && c.Standable(map) && c.GetPlant(map) == null && c.GetEdifice(map) == null) { cell = c; break; }
                }
                if (!cell.IsValid) return "UNMEASURED: no free cell within 8 of the camera";
                plant = (Plant)GenSpawn.Spawn(virrDef, cell, map);
                float wind = map.windManager.WindSpeed;
                if (wind < RM_MapComponent_BlueDesertSoundscape.VirrMinWind)
                    return "UNMEASURED: wind " + wind.ToString("0.00") + " below the singing threshold; rerun in wind (lock a drift weather)";
                plant.Growth = 0.05f;
                comp.Rescan(Find.TickManager.TicksGame, playSound: false);
                bool youngSings = comp.VirrSinging;
                float youngPitch = comp.VirrPitch;
                plant.Growth = 1f;
                comp.Rescan(Find.TickManager.TicksGame, playSound: false);
                bool ripeSings = comp.VirrSinging;
                float ripePitch = comp.VirrPitch;
                string st = string.Format("wind={0:0.00} young={1}@{2:0.00} ripe={3}@{4:0.00}", wind, youngSings, youngPitch, ripeSings, ripePitch);
                if (on)
                {
                    if (!youngSings || !ripeSings) return "FAIL: a virr at the camera in wind does not sing " + st;
                    if (ripePitch <= youngPitch) return "FAIL: pitch does not climb with ripeness " + st;
                    return "PASS " + st;
                }
                if (youngSings || ripeSings) return "FAIL: virrSongEnabled off but the virr sang " + st;
                return "PASS off " + st;
            }
            finally
            {
                if (plant != null && !plant.Destroyed) plant.Destroy(DestroyMode.Vanish);
                RM_BlueDesertSettings.masterEnabled = savedMaster;
                RM_BlueDesertSettings.virrSongEnabled = savedVirr;
                comp.Rescan(Find.TickManager.TicksGame, playSound: true);
            }
        }
    }
}
