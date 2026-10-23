using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Scarlands
{
    // WARSCAR_GEIGER_CHOIR_1. The Warscar soundscape: tetchik tick (tempo from glower + tetchik density), wind on metal
    // (silent during RM_Settling), the projector hum and the pool boil. (The tetchik jar, a carried pollution counter with a caravan
    // warning, was CUT 2026-10-23 by the fluff review.)
    // Deviation from the spec's "ride RM_MapComponent_ProximitySoundscape": that component cannot scale on wind or
    // go silent for a named condition and is tag-driven; this is its own component, same shape as Stillsand's
    // RM_MapComponent_SandListening. Source groups are DATA (RM_GeigerChoirDef). Tags work on pawns because tetchik
    // are counted through ListerThings.ThingsOfDef, which includes pawns.
    public class RM_GeigerChoirDef : Def
    {
        public List<string> tickPlants = new List<string>();
        public List<string> tickCreatures = new List<string>();
        public List<string> windMetal = new List<string>();
        public List<string> hum = new List<string>();
        public List<string> boil = new List<string>();

        public static RM_GeigerChoirDef Get() { return DefDatabase<RM_GeigerChoirDef>.GetNamedSilentFail("RM_GeigerChoir"); }

        public static List<ThingDef> Resolve(List<string> names)
        {
            List<ThingDef> r = new List<ThingDef>();
            if (names == null) return r;
            for (int i = 0; i < names.Count; i++)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(names[i]);
                if (d != null) r.Add(d);
            }
            return r;
        }
    }

    [DefOf]
    public static class RM_ChoirDefOf
    {
        public static SoundDef RM_GeigerTick;
        public static SoundDef RM_WindOnMetal;
        public static SoundDef RM_ProjectorHum;
        public static SoundDef RM_PoolBoil;
        static RM_ChoirDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_ChoirDefOf)); }
    }

    public class RM_MapComponent_GeigerChoir : MapComponent
    {
        private const int RefreshInterval = 30;
        private const int ClickInterval = 6;
        private const float TickRadius = 14f;

        private Sustainer wind, hum, boil;
        private Thing windSrc, humSrc, boilSrc;
        private readonly List<IntVec3> clickCells = new List<IntVec3>();
        private float density;

        // Readouts for live validation (state reads, not a sound hunt).
        public float TickDensity { get { return density; } }
        public bool WindSustainerActive { get { return wind != null && !wind.Ended; } }
        public bool HumSustainerActive { get { return hum != null && !hum.Ended; } }
        public bool BoilSustainerActive { get { return boil != null && !boil.Ended; } }

        public RM_MapComponent_GeigerChoir(Map map) : base(map) { }

        public static bool Silenced(Map map, IntVec3 cell)
        {
            if (!RM_WarscarSettings.chotrixEnabled) return false;   // the silence ring is a chotrix effect
            List<CompChotrix> all = CompChotrix.All;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn p = all[i].Pawn;
                if (p == null || !p.Spawned || p.Dead || p.Map != map) continue;
                float r = all[i].SilenceRadius;
                if ((p.Position - cell).LengthHorizontalSquared <= r * r) return true;
            }
            return false;
        }

        public static float ClickChance(float dens)
        {
            float cap = RM_WarscarSettings.choirReducedRepetition ? 0.12f : 0.45f;
            return Mathf.Clamp(dens * 0.012f * RM_WarscarSettings.choirTickDensity, 0f, cap);
        }

        private float TickVolume(float dens)
        {
            float v = Mathf.Clamp(0.3f + dens / 30f, 0.3f, 1f);
            return Mathf.Min(v, RM_WarscarSettings.choirTickVolumeCeiling) * RM_WarscarSettings.choirVolume;
        }

        public override void MapComponentTick()
        {
            if (!RM_WarscarSettings.choirEnabled || Find.CurrentMap != map)
            {
                EndAll();
                return;
            }
            int now = Find.TickManager.TicksGame;
            IntVec3 listener = Find.CameraDriver.MapPosition;
            if (now % RefreshInterval == 0) Refresh(listener);
            // The engine ends a sustainer on its own (e.g. its source thing despawned) between Refreshes;
            // maintaining an ended one logs "Tried to maintain ended sustainer", so drop it and let Refresh re-spawn.
            if (wind != null && wind.Ended) { wind = null; windSrc = null; }
            if (hum != null && hum.Ended) { hum = null; humSrc = null; }
            if (boil != null && boil.Ended) { boil = null; boilSrc = null; }
            if (wind != null) { wind.Maintain(); wind.externalParams["Wind"] = map.windManager.WindSpeed; wind.externalParams["Vol"] = RM_WarscarSettings.choirVolume; }
            if (hum != null) { hum.Maintain(); hum.externalParams["Vol"] = RM_WarscarSettings.choirVolume; }
            if (boil != null) { boil.Maintain(); boil.externalParams["Vol"] = RM_WarscarSettings.choirVolume; }
            if (now % ClickInterval == 0) Click(now);
        }

        private void Refresh(IntVec3 listener)
        {
            RM_GeigerChoirDef cfg = RM_GeigerChoirDef.Get();
            if (cfg == null) return;
            // Tick density around the listener: glower plants count 1, tetchik 3.
            density = 0f;
            clickCells.Clear();
            float r2 = TickRadius * TickRadius;
            List<ThingDef> plants = RM_GeigerChoirDef.Resolve(cfg.tickPlants);
            for (int i = 0; i < plants.Count; i++)
            {
                List<Thing> l = map.listerThings.ThingsOfDef(plants[i]);
                for (int k = 0; k < l.Count; k++)
                {
                    if ((l[k].Position - listener).LengthHorizontalSquared > r2) continue;
                    density += 1f;
                    if (clickCells.Count < 64) clickCells.Add(l[k].Position);
                }
            }
            List<ThingDef> bugs = RM_GeigerChoirDef.Resolve(cfg.tickCreatures);
            for (int i = 0; i < bugs.Count; i++)
            {
                List<Thing> l = map.listerThings.ThingsOfDef(bugs[i]);
                for (int k = 0; k < l.Count; k++)
                {
                    if ((l[k].Position - listener).LengthHorizontalSquared > r2) continue;
                    density += 3f;
                    if (clickCells.Count < 64) clickCells.Add(l[k].Position);
                }
            }
            bool settling = RM_SettlingDefOf.RM_Settling != null && map.gameConditionManager.ConditionIsActive(RM_SettlingDefOf.RM_Settling);
            bool windOn = RM_WarscarSettings.choirWindEnabled && !settling;
            Layer(ref wind, ref windSrc, windOn ? RM_GeigerChoirDef.Resolve(cfg.windMetal) : null, listener, 30f, RM_ChoirDefOf.RM_WindOnMetal, false);
            Layer(ref hum, ref humSrc, RM_GeigerChoirDef.Resolve(cfg.hum), listener, 40f, RM_ChoirDefOf.RM_ProjectorHum, true);
            Layer(ref boil, ref boilSrc, RM_GeigerChoirDef.Resolve(cfg.boil), listener, 28f, RM_ChoirDefOf.RM_PoolBoil, false);
        }

        // A screen or ring hums only while it is live (powered and switched on; a dead ring only once woken).
        private static bool Humming(Thing t)
        {
            RM_CompAerosolScreen sc = (t as ThingWithComps)?.GetComp<RM_CompAerosolScreen>();
            return sc == null || sc.IsScreenLive;
        }

        // Keeps one sustainer on the nearest source of a layer within range; null defs = layer off.
        private void Layer(ref Sustainer s, ref Thing src, List<ThingDef> defs, IntVec3 listener, float range, SoundDef sound, bool liveOnly)
        {
            Thing best = null;
            if (defs != null && sound != null)
            {
                float bd = range * range;
                for (int i = 0; i < defs.Count; i++)
                {
                    List<Thing> l = map.listerThings.ThingsOfDef(defs[i]);
                    for (int k = 0; k < l.Count; k++)
                    {
                        if (liveOnly && !Humming(l[k])) continue;
                        float d = (l[k].Position - listener).LengthHorizontalSquared;
                        if (d < bd) { bd = d; best = l[k]; }
                    }
                }
            }
            if (best == null)
            {
                if (s != null && !s.Ended) s.End();
                s = null; src = null;
                return;
            }
            if (s != null && !s.Ended && src != null && src.Spawned && (!liveOnly || Humming(src)) && (best == src || (src.Position - listener).LengthHorizontalSquared <= (best.Position - listener).LengthHorizontalSquared + 16f)) return;
            if (s != null && !s.Ended) s.End();
            src = best;
            s = sound.TrySpawnSustainer(SoundInfo.InMap(best, MaintenanceType.PerTick));
        }

        private void Click(int now)
        {
            float vol = RM_WarscarSettings.choirVolume;
            if (vol <= 0f) return;
            if (clickCells.Count > 0 && Rand.Chance(ClickChance(density)))
            {
                IntVec3 c = clickCells.RandomElement();
                if (!Silenced(map, c)) Play(c, TickVolume(density));
            }
        }

        private void Play(IntVec3 cell, float volume)
        {
            if (RM_ChoirDefOf.RM_GeigerTick == null) return;
            SoundInfo info = SoundInfo.InMap(new TargetInfo(cell, map));
            info.volumeFactor = volume;
            if (RM_WarscarSettings.choirReducedRepetition) info.pitchFactor = Rand.Range(0.9f, 1.1f);
            RM_ChoirDefOf.RM_GeigerTick.PlayOneShot(info);
        }

        private void EndAll()
        {
            if (wind != null && !wind.Ended) wind.End();
            if (hum != null && !hum.Ended) hum.End();
            if (boil != null && !boil.Ended) boil.End();
            wind = hum = boil = null; windSrc = humSrc = boilSrc = null;
        }

        public override void MapRemoved() { EndAll(); base.MapRemoved(); }
    }
}
