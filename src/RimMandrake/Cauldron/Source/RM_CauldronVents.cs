using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_VENT_ENRICHMENT_HOOKS_1 — the vent, and the three things that hang on it.
    //
    // WHAT A VENT IS HERE. A 2x2 natural building (RM_CauldronVent, Building_SteamGeyser-shaped) that
    // CAULDRON_MECHANICS_BUILD_1 part 3 never got to build. It holds STATE, not gas: a temperament
    // (Stable | Leaking), the tick of its last blowout, a suppression meter and a silenced-until tick.
    // It emits air puffs scaled by output. There is NO gas, NO GasType and NO heat here: part 3 still
    // owns the flammable gas and the gap is stated, not papered over. Heat law: nothing in this file
    // adds heat or a hediff; the existing RM_VentMetalLoad is the only effect on pawns.
    //
    // Spawned at map generation on RM_Cauldron maps only (RM_MapComponent_CauldronVents). Maps made
    // before this existed have no vents and keep the old map-wide bloom exposure.
    //
    // THE FALTER NEEDS NO FOREKNOWLEDGE. The engine sets curWeather when a transition STARTS and
    // WeatherManager.TransitionLerpFactor ramps 0 -> 1. While the new weather is RM_VentBloom and the
    // lerp is below 1 every vent is hushed (falterOutput); the bloom's raised output starts at lerp 1.
    // Public API only. The tell is one weather transition long, not a day's notice.
    // ════════════════════════════════════════════════════════════════════
    public enum RM_VentTemperament { Stable, Leaking }

    public enum RM_VentHabitat { None, StableRing, ChronicLeak, RecentBlowout }

    public class RM_VentWeatherOutput
    {
        public WeatherDef weather;
        public float output = 1f;
    }

    public class RM_VentExtension : DefModExtension
    {
        public List<RM_VentWeatherOutput> weatherOutput = new List<RM_VentWeatherOutput>();
        public float defaultOutput = 1f;
        public float falterOutput = 0.1f;        // the hush before a bloom
        public WeatherDef bloomWeather;           // the weather whose onset is a blowout and whose lead-in is the falter
        public int recoverTicks = 60000;          // a silenced vent climbs back over this long
        public int recentBlowoutTicks = 600000;   // "recent" for the giant-toxic-flower habitat: 10 days
        public float suppressionNeeded = 6000f;   // drink-ticks to silence one
        public float suppressionDecayPerDay = 0.5f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (bloomWeather == null) yield return "RM_VentExtension has no bloomWeather";
            if (suppressionNeeded <= 0f) yield return "RM_VentExtension suppressionNeeded must be > 0";
        }
    }

    public class RM_Building_CauldronVent : Building
    {
        private const int NeverBlew = -900000000;

        public RM_VentTemperament temperament = RM_VentTemperament.Stable;
        public int lastBlowoutTick = NeverBlew;
        public float suppression;
        public int silencedUntil = -1;      // -1 = never silenced
        private bool bloomSeen;

        private RM_VentExtension Ext => def.GetModExtension<RM_VentExtension>();

        public bool IsSilenced => silencedUntil >= 0 && Find.TickManager.TicksGame < silencedUntil;

        // 0 while silenced, climbing to 1 over recoverTicks after; 1 for a vent never silenced.
        public float Recovery01
        {
            get
            {
                if (silencedUntil < 0) return 1f;
                int now = Find.TickManager.TicksGame;
                if (now < silencedUntil) return 0f;
                int span = Mathf.Max(1, Ext?.recoverTicks ?? 60000);
                return Mathf.Clamp01((now - silencedUntil) / (float)span);
            }
        }

        public static bool IsFaltering(Map map)
        {
            if (!RM_CauldronSettings.ventWeatherEnabled || map == null) return false;
            WeatherManager wm = map.weatherManager;
            RM_VentExtension ext = RM_CauldronDefOf.RM_CauldronVent?.GetModExtension<RM_VentExtension>();
            if (wm == null || ext == null || ext.bloomWeather == null) return false;
            return wm.curWeather == ext.bloomWeather && !Mathf.Approximately(wm.TransitionLerpFactor, 1f);
        }

        public static bool IsBlooming(Map map)
        {
            if (!RM_CauldronSettings.ventWeatherEnabled || map == null) return false;
            WeatherManager wm = map.weatherManager;
            RM_VentExtension ext = RM_CauldronDefOf.RM_CauldronVent?.GetModExtension<RM_VentExtension>();
            if (wm == null || ext == null || ext.bloomWeather == null) return false;
            return wm.curWeather == ext.bloomWeather && Mathf.Approximately(wm.TransitionLerpFactor, 1f);
        }

        public float WeatherMultiplier()
        {
            RM_VentExtension ext = Ext;
            if (ext == null || !RM_CauldronSettings.ventWeatherEnabled || Map == null) return 1f;
            if (IsFaltering(Map)) return ext.falterOutput;
            WeatherDef cur = Map.weatherManager?.curWeather;
            for (int i = 0; i < ext.weatherOutput.Count; i++)
                if (ext.weatherOutput[i].weather == cur) return ext.weatherOutput[i].output;
            return ext.defaultOutput;
        }

        // What the vent is doing right now: weather multiplier x recovery. 0 while silenced.
        public float Output => WeatherMultiplier() * Recovery01;

        public bool RecentlyBlewOut
        {
            get
            {
                int window = Ext?.recentBlowoutTicks ?? 600000;
                return Find.TickManager.TicksGame - lastBlowoutTick < window;
            }
        }

        public bool Matches(RM_VentHabitat h)
        {
            switch (h)
            {
                case RM_VentHabitat.StableRing: return temperament == RM_VentTemperament.Stable && !RecentlyBlewOut;
                case RM_VentHabitat.ChronicLeak: return temperament == RM_VentTemperament.Leaking;
                case RM_VentHabitat.RecentBlowout: return RecentlyBlewOut;
                default: return false;
            }
        }

        // A drinker adds `amount` of the 0..1 suppression meter. At 1 the vent falls silent for several days.
        public void Inhale(float amount)
        {
            if (IsSilenced || Ext == null) return;
            suppression += amount;
            if (suppression < 1f) return;
            suppression = 0f;
            float days = RM_CauldronSettings.ventSilenceDays * Rand.Range(0.85f, 1.15f);
            silencedUntil = Find.TickManager.TicksGame + Mathf.RoundToInt(days * 60000f);
            if (Map != null && Map.mapPawns.AnyColonistSpawned)
                Messages.Message("A vent has been drunk quiet.", new LookTargets(this), MessageTypeDefOf.NeutralEvent, false);
        }

        protected override void Tick()
        {
            base.Tick();
            int now = Find.TickManager.TicksGame;

            if (IsBlooming(Map))
            {
                if (!bloomSeen) { bloomSeen = true; lastBlowoutTick = now; }
            }
            else if (!IsFaltering(Map))
            {
                bloomSeen = false;
            }

            if (this.IsHashIntervalTick(250) && suppression > 0f && Ext != null)
                suppression = Mathf.Max(0f, suppression - 250f * Ext.suppressionDecayPerDay / 60000f);

            if (this.IsHashIntervalTick(20))
            {
                float o = Output;
                if (o > 0.05f && Rand.Chance(Mathf.Clamp01(o * 0.3f)))
                {
                    Vector3 p = DrawPos + new Vector3(Rand.Range(-0.6f, 0.6f), 0f, Rand.Range(-0.6f, 0.6f));
                    FleckMaker.ThrowAirPuffUp(p, Map);
                    if (o > 1.5f) FleckMaker.ThrowSmoke(p, Map, 1.2f);
                }
            }
        }

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder();
            string baseStr = base.GetInspectString();
            if (!baseStr.NullOrEmpty()) sb.AppendLine(baseStr);
            sb.AppendLine("Vent: " + (temperament == RM_VentTemperament.Leaking ? "chronic leak" : "stable"));
            string state;
            if (IsSilenced)
                state = "silenced (drunk quiet), " + ((silencedUntil - Find.TickManager.TicksGame).ToStringTicksToPeriod()) + " left";
            else if (Recovery01 < 1f)
                state = "recovering, " + Recovery01.ToStringPercent();
            else if (IsFaltering(Map))
                state = "faltering";
            else
                state = "breathing";
            sb.AppendLine("Vent state: " + state);
            sb.Append("Vent output: " + Output.ToString("0.00") + "x");
            if (suppression > 0.01f && !IsSilenced)
                sb.Append("  (drunk " + suppression.ToStringPercent() + " of the way quiet)");
            return sb.ToString();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref temperament, "rmVentTemperament", RM_VentTemperament.Stable);
            Scribe_Values.Look(ref lastBlowoutTick, "rmVentLastBlowout", NeverBlew);
            Scribe_Values.Look(ref suppression, "rmVentSuppression", 0f);
            Scribe_Values.Look(ref silencedUntil, "rmVentSilencedUntil", -1);
            Scribe_Values.Look(ref bloomSeen, "rmVentBloomSeen", false);
        }
    }

    // ── map side: generation, falter notice, exposure weight ─────────────
    public class RM_MapComponent_CauldronVents : MapComponent
    {
        private const float VentsPerCell = 1f / 14000f;   // a 250x250 map gets ~4-5
        private const int VentSpacing = 24;
        private const int StartClearRadius = 14;
        private const float ExposureNear = 8f;
        private const float ExposureFar = 45f;
        private const float ExposureFloor = 0.1f;

        private bool generated;
        private bool falterNotified;

        public RM_MapComponent_CauldronVents(Map map) : base(map) { }

        public List<Thing> Vents()
        {
            ThingDef d = RM_CauldronDefOf.RM_CauldronVent;
            return d == null ? new List<Thing>() : map.listerThings.ThingsOfDef(d);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref generated, "rmVentsGenerated", false);
            Scribe_Values.Look(ref falterNotified, "rmVentFalterNotified", false);
        }

        public override void MapGenerated()
        {
            EnsureGenerated();
        }

        // Idempotent: the gardens component calls this first because MapComponent order is not guaranteed.
        public void EnsureGenerated()
        {
            if (generated) return;
            generated = true;
            if (!RM_CauldronSettings.ventsEnabled) return;
            ThingDef def = RM_CauldronDefOf.RM_CauldronVent;
            if (def == null || map.Biome == null || map.Biome.defName != "RM_Cauldron") return;

            int want = Mathf.Clamp(Mathf.RoundToInt(map.Area * VentsPerCell * Rand.Range(0.8f, 1.3f)), 2, 8);
            var placed = new List<RM_Building_CauldronVent>();
            for (int attempt = 0; attempt < 600 && placed.Count < want; attempt++)
            {
                IntVec3 c = new IntVec3(Rand.RangeInclusive(8, map.Size.x - 8), 0, Rand.RangeInclusive(8, map.Size.z - 8));
                CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, def.size);
                if (!FootprintFree(rect)) continue;
                bool close = false;
                foreach (var p in placed)
                    if ((p.Position - c).LengthHorizontal < VentSpacing) { close = true; break; }
                if (close) continue;
                if (MapGenerator.PlayerStartSpot.IsValid && (MapGenerator.PlayerStartSpot - c).LengthHorizontal < StartClearRadius) continue;
                foreach (IntVec3 cell in rect) cell.GetPlant(map)?.Destroy();
                var vent = (RM_Building_CauldronVent)ThingMaker.MakeThing(def);
                vent.temperament = Rand.Chance(0.35f) ? RM_VentTemperament.Leaking : RM_VentTemperament.Stable;
                GenSpawn.Spawn(vent, c, map, Rot4.North);
                placed.Add(vent);
            }
            if (placed.Count >= 2)
            {
                // Every map shows both a stable vent and a chronic leak, and one that blew out lately.
                if (!placed.Exists(v => v.temperament == RM_VentTemperament.Leaking)) placed[placed.Count - 1].temperament = RM_VentTemperament.Leaking;
                if (!placed.Exists(v => v.temperament == RM_VentTemperament.Stable)) placed[0].temperament = RM_VentTemperament.Stable;
                placed[0].lastBlowoutTick = Find.TickManager.TicksGame - Rand.RangeInclusive(60000, 480000);
            }
        }

        private bool FootprintFree(CellRect rect)
        {
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map) || !c.Standable(map) || c.Roofed(map)) return false;
                TerrainDef t = c.GetTerrain(map);
                if (t == null || t.IsWater || t.passability != Traversability.Standable) return false;
                var things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    ThingCategory cat = things[i].def.category;
                    if (cat == ThingCategory.Building || cat == ThingCategory.Item || cat == ThingCategory.Pawn) return false;
                }
            }
            return true;
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % 60 != 0) return;
            bool faltering = RM_Building_CauldronVent.IsFaltering(map);
            if (!faltering) { falterNotified = false; return; }
            if (falterNotified || !RM_CauldronSettings.ventFalterMessage || !map.mapPawns.AnyColonistSpawned) return;
            List<Thing> vents = Vents();
            if (vents.Count == 0) return;
            falterNotified = true;
            Messages.Message("The vents have gone quiet. Something is building under the ground.",
                new LookTargets(vents[0]), MessageTypeDefOf.NeutralEvent, false);
        }

        // 1 = the old map-wide tax (no vents on this map, or the toggle is off). Otherwise the bloom's metal
        // load scales from full strength beside a live vent down to a 0.1 floor far from every one.
        // A silenced vent contributes its recovery fraction (0 while silenced).
        public static float ExposureWeight(Map map, IntVec3 at)
        {
            if (!RM_CauldronSettings.ventLocalExposureEnabled) return 1f;
            var comp = map.GetComponent<RM_MapComponent_CauldronVents>();
            if (comp == null) return 1f;
            List<Thing> vents = comp.Vents();
            if (vents.Count == 0) return 1f;
            float best = 0f;
            for (int i = 0; i < vents.Count; i++)
            {
                var v = vents[i] as RM_Building_CauldronVent;
                if (v == null) continue;
                float d = (v.Position - at).LengthHorizontal;
                float prox = d <= ExposureNear ? 1f : d >= ExposureFar ? 0f : 1f - (d - ExposureNear) / (ExposureFar - ExposureNear);
                best = Mathf.Max(best, prox * v.Recovery01);
            }
            return Mathf.Lerp(ExposureFloor, 1f, best);
        }
    }

    // ── vexxiss drinks a vent ─────────────────────────────────────────────
    public class RM_JobDriver_VexxissDrinkVent : JobDriver
    {
        public const int DrinkTicks = 900;

        public override bool TryMakePreToilReservations(bool errorOnFailed) { return true; }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil drink = new Toil();
            drink.defaultCompleteMode = ToilCompleteMode.Delay;
            drink.defaultDuration = DrinkTicks;
            drink.tickAction = () =>
            {
                var vent = job.targetA.Thing as RM_Building_CauldronVent;
                if (vent == null) return;
                float need = vent.def.GetModExtension<RM_VentExtension>()?.suppressionNeeded ?? 6000f;
                vent.Inhale(1f / need);
            };
            drink.AddEndCondition(() =>
            {
                var vent = job.targetA.Thing as RM_Building_CauldronVent;
                return (vent == null || vent.IsSilenced) ? JobCondition.Succeeded : JobCondition.Ongoing;
            });
            drink.AddFailCondition(() => !RM_CauldronSettings.vexxissDrinksVentsEnabled);
            yield return drink;
        }
    }
}
