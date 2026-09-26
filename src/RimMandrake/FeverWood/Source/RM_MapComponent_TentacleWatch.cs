using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TENTACLE_BESTIARY_1. Per-map bookkeeping for the tentacle
    // bestiary: the ambient "1-2 limbs emerge" spawner, the pool cooldown/
    // respite clock the drive-off ladder writes to, the permanent-kill flag
    // ("killed permanently on this map" is per-map, not per-world — §2b),
    // the porter's forever-angered flag (§2a), and the sentinel-up counter
    // (§4's "chorus silent while it is up" — this only exposes the public
    // signal; the actual bird chorus is a separate, not-yet-built system,
    // same posture RM_MapComponent_SilenceCue's own F2 gap already has).
    //
    // Auto-attaches to EVERY map (Map.FillComponents() instantiates every
    // MapComponent subclass unconditionally — confirmed by
    // RUT_MapComponent_TheTenant's own header). Content-blind at the class
    // level: it no-ops on any map with no registered pool terrain
    // (RM_LurkingWaterExtension), so it costs nothing on a non-Fever-Wood
    // map — same "generic kit, not hardcoded to one biome" posture as
    // RM_GenStep_RootCauseways/RM_MapComponent_LivingRegrowth.
    //
    // 🔴 Does NOT decide how often the rare eye set-piece (Bloom) arrives —
    // that is this item's own explicitly-unset, do-not-guess tuning number
    // (design sheet §2b: "the single most important tuning number... unset
    // — nobody has chosen it"). Bloom gets a low, flagged-INVENTED ambient
    // weight below as a placeholder so the def is reachable at all, not a
    // real answer to the pressure-model question the sheet's own §6d
    // raises. The real trigger (base roll + pool size + provocation +
    // pressure + deliberate summon) is unbuilt; see this item's close note.
    public class RM_MapComponent_TentacleWatch : MapComponent
    {
        private struct LimbWeight
        {
            public readonly string defName;
            public readonly float weight;
            public LimbWeight(string defName, float weight)
            {
                this.defName = defName;
                this.weight = weight;
            }
        }

        private const int AmbientCheckIntervalTicks = 2500; // 1 in-game hour
        private const int PoolCacheRefreshTicks = 60000; // pools don't move; re-scan once a day

        private static readonly LimbWeight[] AmbientTable =
        {
            new LimbWeight("RM_Sekkulaath_Feeler", 40f),
            new LimbWeight("RM_Sekkulaath_Snare", 25f),
            new LimbWeight("RM_Sekkulaath_Lash", 20f),
            new LimbWeight("RM_Sekkulaath_Porter", 10f),
            new LimbWeight("RM_Sekkulaath_Sentinel", 8f),
            new LimbWeight("RM_Sekkulaath_Bloom", 2f),
        };

        private static readonly string[] AllLimbDefNames =
        {
            "RM_Sekkulaath_Feeler", "RM_Sekkulaath_Snare", "RM_Sekkulaath_Lash",
            "RM_Sekkulaath_Porter", "RM_Sekkulaath_Sentinel", "RM_Sekkulaath_Bloom",
        };

        private int blockedUntilTick;
        private bool permanentlyKilled;
        private bool porterAngeredForever;
        private int sentinelCount;

        private List<IntVec3> poolCellsCache;
        private int poolCacheBuiltTick = -999999;

        public bool PermanentlyKilled => permanentlyKilled;
        public bool ChorusSilenced => sentinelCount > 0;

        public RM_MapComponent_TentacleWatch(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (Find.TickManager.TicksGame % AmbientCheckIntervalTicks != 0)
            {
                return;
            }

            if (!RM_FeverWoodSettings.tentacleBestiaryEnabled || permanentlyKilled)
            {
                return;
            }

            if (Find.TickManager.TicksGame < blockedUntilTick)
            {
                return;
            }

            List<IntVec3> pools = PoolCells();
            if (pools.Count == 0)
            {
                return; // no registered water on this map — nothing to do
            }

            float mtb = UnityEngine.Mathf.Max(0.1f, RM_FeverWoodSettings.tentacleAmbientMtbHours);
            if (!Rand.MTBEventOccurs(mtb, 2500f, AmbientCheckIntervalTicks))
            {
                return;
            }

            SpawnEncounter(pools);
        }

        private void SpawnEncounter(List<IntVec3> pools)
        {
            IntVec3 seed = pools[Rand.Range(0, pools.Count)];
            int limbCount = Rand.Chance(0.3f) ? 2 : 1; // INVENTED: "one or two tentacles emerge"

            for (int i = 0; i < limbCount; i++)
            {
                ThingDef def = RollLimb();
                if (def == null)
                {
                    continue;
                }
                IntVec3 cell = i == 0 ? seed : RandomNearbyPoolCell(seed, pools);
                Thing thing = ThingMaker.MakeThing(def);
                GenSpawn.Spawn(thing, cell, map);
            }
        }

        private IntVec3 RandomNearbyPoolCell(IntVec3 seed, List<IntVec3> pools)
        {
            IntVec3 best = seed;
            float bestDistSq = float.MaxValue;
            for (int i = 0; i < pools.Count; i++)
            {
                if (pools[i] == seed)
                {
                    continue;
                }
                float distSq = (pools[i] - seed).LengthHorizontalSquared;
                if (distSq < bestDistSq)
                {
                    bestDistSq = distSq;
                    best = pools[i];
                }
            }
            return best;
        }

        private ThingDef RollLimb()
        {
            float total = 0f;
            for (int i = 0; i < AmbientTable.Length; i++)
            {
                if (porterAngeredForever && AmbientTable[i].defName == "RM_Sekkulaath_Porter")
                {
                    continue;
                }
                total += AmbientTable[i].weight;
            }
            if (total <= 0f)
            {
                return null;
            }

            float roll = Rand.Range(0f, total);
            for (int i = 0; i < AmbientTable.Length; i++)
            {
                if (porterAngeredForever && AmbientTable[i].defName == "RM_Sekkulaath_Porter")
                {
                    continue;
                }
                roll -= AmbientTable[i].weight;
                if (roll <= 0f)
                {
                    return DefDatabase<ThingDef>.GetNamedSilentFail(AmbientTable[i].defName);
                }
            }
            return null;
        }

        private List<IntVec3> PoolCells()
        {
            if (poolCellsCache != null && Find.TickManager.TicksGame - poolCacheBuiltTick < PoolCacheRefreshTicks)
            {
                return poolCellsCache;
            }

            poolCacheBuiltTick = Find.TickManager.TicksGame;
            poolCellsCache = new List<IntVec3>();

            RUT_MapComponent_TheTenant tenant = map.GetComponent<RUT_MapComponent_TheTenant>();
            if (tenant == null)
            {
                return poolCellsCache;
            }

            foreach (IntVec3 c in map.AllCells)
            {
                if (tenant.IsRegisteredWater(c))
                {
                    poolCellsCache.Add(c);
                }
            }
            return poolCellsCache;
        }

        // --- called by RM_CompTentacleLimb / RM_CompTentacleEye ---

        public void OnLimbRetreated(int cooldownTicks)
        {
            int until = Find.TickManager.TicksGame + cooldownTicks;
            if (until > blockedUntilTick)
            {
                blockedUntilTick = until;
            }
        }

        public void OnLimbSevered(int respiteTicks)
        {
            int until = Find.TickManager.TicksGame + respiteTicks;
            if (until > blockedUntilTick)
            {
                blockedUntilTick = until;
            }
        }

        public void OnPorterAttacked()
        {
            porterAngeredForever = true;
        }

        public void DriveOffAllLimbs(int ticks)
        {
            DespawnAllLimbs();
            int until = Find.TickManager.TicksGame + ticks;
            if (until > blockedUntilTick)
            {
                blockedUntilTick = until;
            }
            Messages.Message("Every tentacle in the Fever Wood withdraws beneath the water.",
                new TargetInfo(map.Center, map), MessageTypeDefOf.ThreatBig);
        }

        // FEVERWOOD_DIANOGA_PRISON_1: called by RM_CompEscapedCaptive when
        // an escaped tank occupant reaches registered water (§6m stage 2,
        // "if it reaches a pool it establishes"). Un-sets a prior permanent
        // kill on this map — the elder-being ambient system is guaranteed
        // live here again. See that class's own header for what this
        // deliberately does NOT build (a timed stage-3 maturation).
        public void Notify_SekkulaathInstalled()
        {
            permanentlyKilled = false;
        }

        public void KillPermanentlyOnThisMap()
        {
            DespawnAllLimbs();
            permanentlyKilled = true;
            Messages.Message("The great tentacled thing beneath the Fever Wood's pools has been driven off for good — on this ground, at least.",
                new TargetInfo(map.Center, map), MessageTypeDefOf.PositiveEvent);
        }

        private void DespawnAllLimbs()
        {
            for (int d = 0; d < AllLimbDefNames.Length; d++)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(AllLimbDefNames[d]);
                if (def == null)
                {
                    continue;
                }
                // Snapshot: ThingsOfDef returns the live list this map
                // maintains, and Destroy() mutates it mid-enumeration.
                List<Thing> matches = new List<Thing>(map.listerThings.ThingsOfDef(def));
                for (int i = 0; i < matches.Count; i++)
                {
                    if (matches[i].Spawned)
                    {
                        matches[i].Destroy(DestroyMode.Vanish);
                    }
                }
            }
        }

        public void Notify_SentinelUp()
        {
            sentinelCount++;
            if (sentinelCount == 1)
            {
                HushChorus();
            }
        }

        public void Notify_SentinelDown()
        {
            int previous = sentinelCount;
            sentinelCount = UnityEngine.Mathf.Max(0, sentinelCount - 1);
            if (previous > 0 && sentinelCount == 0)
            {
                RestoreChorus();
            }
        }

        /// <summary>
        /// FEVERWOOD_ALIEN_BIRD_CHORUS_1. "The crown goes quiet ONLY for the
        /// water" (fever_wood_deep_and_mud_2026-09-23.md §4/§6c, decision
        /// taken by question card) — a sentinel limb surfacing IS the "the
        /// thing below stirred" signal, so this ends the map's biome
        /// ambient sustainers directly (the crown's birds, RM_Chellow/
        /// RM_Murrelith/RM_Thavrik/RM_Skellick, are the cast that makes the
        /// crown loud enough for this to read as an event — see
        /// RM_FeverWoodBirds.xml). Same technique
        /// RM_MapComponent_SilenceCue (CreatureBehaviors) already uses for
        /// its own predator-hunt/mirror-break hushes — Sustainer/
        /// SustainerManager expose no partial volume-ramp, so this ends
        /// matching sustainers outright rather than fading them.
        /// Deliberately duplicated here rather than referenced
        /// cross-assembly: this class already owns sentinelCount, and this
        /// mod's csproj had no compile-time reference to
        /// mandrake.rm.creaturebehaviors as of this item, plus a second
        /// live FOUNDRY window held that exact file mid-edit for unrelated
        /// work (FEVERWOOD_SAP_SUCKER_GUILD_1/FEVERWOOD_ANT_HIVE_DUNGEON_1)
        /// at the same time this item was built — adding a reference would
        /// have meant committing their in-flight, unrelated changes too.
        /// ⚠️ Known accepted overlap: if SilenceCue's own hush is
        /// independently active on this map (e.g. a mirror-break beat)
        /// when the sentinel retreats, RestoreChorus()'s
        /// Notify_SwitchedMap() call can resume ambient sound slightly
        /// early. Narrow edge case — a mirror-break hush is a short beat,
        /// a sentinel's presence is comparatively long — same class of
        /// "accepted honest trade" SilenceCue's own header already
        /// documents for its own no-partial-volume-ramp limitation.
        /// </summary>
        private void HushChorus()
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
            Messages.Message("RM_FeverWood_ChorusFallsSilent".Translate(), new TargetInfo(map.Center, map), MessageTypeDefOf.ThreatBig, historical: false);
        }

        private void RestoreChorus()
        {
            if (Find.CurrentMap == map)
            {
                AmbientSoundManager.Notify_SwitchedMap();
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref blockedUntilTick, "blockedUntilTick", 0);
            Scribe_Values.Look(ref permanentlyKilled, "permanentlyKilled", false);
            Scribe_Values.Look(ref porterAngeredForever, "porterAngeredForever", false);
            // sentinelCount is deliberately NOT scribed: every spawned
            // sentinel's own RM_CompTentacleLimb.PostSpawnSetup re-registers
            // with Notify_SentinelUp() on load too (PostSpawnSetup fires for
            // respawningAfterLoad the same as a fresh spawn), so persisting
            // this counter as well would double-count every sentinel that
            // survives a save. Same "transient-safe to drop on load" posture
            // RUT_MapComponent_TheTenant's own drowningDeadline already has.
        }
    }
}
