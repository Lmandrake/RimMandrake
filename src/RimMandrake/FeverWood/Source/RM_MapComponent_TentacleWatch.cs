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
    // FEVERWOOD_TENTACLE_SETPIECE_TUNING_1, 2026-09-29: the eye no longer
    // spawns through the ordinary ambient roll at all (REPLACES, not
    // alongside — see below). Bloom is now exclusively the payload of the
    // "Great Emergence" — the distinct, rarer, bigger set-piece §2b row 3
    // describes ("a massive attack in a large pool with many tentacles and
    // the eye itself"). This is architecturally cleaner than layering a
    // second independent roll beside the ordinary one: the design sheet's
    // own ladder table (§2b) never lists "a lone eye sighting" as a tier at
    // all — only "ordinary" (1-2 limbs) and the grand set-piece exist — so
    // folding Bloom into the ordinary weighted table (the prior shipped
    // shape) was itself the mismatch this item was filed to fix, not a
    // baseline to preserve alongside the new event.
    //
    // Detection ("large pool + many limbs" — §6d's four-input pressure
    // model is explicitly NOT required by this item; this is the simpler
    // composed threshold it asks for instead): a pool cluster qualifies as
    // "large" once its registered cell count clears
    // tentacleGreatEmergencePoolSizeThreshold, and "many limbs" is read as
    // accumulated activity — encounterPressure increments by one on every
    // ORDINARY ambient encounter this map produces (§6d's own framing:
    // "every ordinary encounter at a pool is a deposit toward its big
    // one") and must clear tentacleGreatEmergencePressureThreshold before
    // the Great Emergence becomes eligible at all. Both numbers are
    // legible/telegraphed in the sense §6i requires fairness to come from
    // (pool size is visible terrain; activity is the player's own doing),
    // never a hidden colony-wealth or maturity check — none is added here,
    // per §6i's explicit "no protection" ruling standing unchanged.
    //
    // Frequency (owner ruling 2026-09-29, question card: "roughly the
    // CURRENT odds, ~1/50"): once eligible, each successful ordinary-roll
    // tick has a tentacleGreatEmergenceChance (default 0.02 = 1/50) chance
    // to escalate into the Great Emergence instead of an ordinary spawn —
    // same rough magnitude as the retired placeholder's 2-of-105 Bloom
    // weight (~1.9%), now gated on the real "big pool under pressure"
    // condition instead of a flat per-roll weight. Firing resets
    // encounterPressure to 0 (the deposit is spent), which is what stops
    // it re-firing every subsequent successful roll while a large pool
    // stays eligible.
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

        private const int AmbientCheckIntervalTicks = RM_BroodKernel.AmbientCheckIntervalTicks; // 1 in-game hour
        private const int PoolCacheRefreshTicks = 60000; // pools don't move; re-scan once a day

        // Bloom is deliberately absent — it is no longer an ordinary-roll
        // outcome (see class header, FEVERWOOD_TENTACLE_SETPIECE_TUNING_1).
        private static readonly LimbWeight[] AmbientTable =
        {
            new LimbWeight("RM_Sekkulaath_Feeler", 40f),
            new LimbWeight("RM_Sekkulaath_Snare", 25f),
            new LimbWeight("RM_Sekkulaath_Lash", 20f),
            new LimbWeight("RM_Sekkulaath_Porter", 10f),
            new LimbWeight("RM_Sekkulaath_Sentinel", 8f),
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
        private int encounterPressure; // FEVERWOOD_TENTACLE_SETPIECE_TUNING_1 — see class header

        // FEVERWOOD_BROOD_RANSOM_1: gifts owed for young returned to a pool here.
        private List<int> pendingGiftTicks = new List<int>();
        private List<IntVec3> pendingGiftCells = new List<IntVec3>();
        private List<int> pendingGiftRolls = new List<int>();
        private const int GiftCheckIntervalTicks = 250;

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

            if (pendingGiftTicks.Count > 0 && Find.TickManager.TicksGame % GiftCheckIntervalTicks == 0)
            {
                TickPendingGifts();
            }

            if (Find.TickManager.TicksGame % AmbientCheckIntervalTicks != 0)
            {
                return;
            }

            if (!RM_PoolKernel.AmbientOpen(RM_FeverWoodSettings.tentacleBestiaryEnabled, permanentlyKilled,
                    Find.TickManager.TicksGame, blockedUntilTick))
            {
                return;
            }

            List<IntVec3> pools = PoolCells();
            if (pools.Count == 0)
            {
                return; // no registered water on this map — nothing to do
            }

            if (!Rand.MTBEventOccurs(EffectiveAmbientMtbHours, 2500f, AmbientCheckIntervalTicks))
            {
                return;
            }

            if (RM_FeverWoodSettings.tentacleGreatEmergenceEnabled
                && GreatEmergenceEligible(pools)
                && Rand.Chance(RM_PoolKernel.GreatChance(RM_FeverWoodSettings.tentacleGreatEmergenceChance)))
            {
                SpawnGreatEmergence(pools);
                return;
            }

            SpawnEncounter(pools);
        }

        /// <summary>FEVERWOOD_BROOD_RANSOM_1: the ordinary ambient MTB divided
        /// by the world's boldness multiplier (1 when the brood ransom is off,
        /// so this is exactly the shipped MTB then).</summary>
        public float EffectiveAmbientMtbHours =>
            RM_BroodKernel.EffectiveAmbientMtbHours(RM_FeverWoodSettings.tentacleAmbientMtbHours, RM_WorldComponent_DeepYoung.BoldnessMultiplier);

        /// <summary>The computed per-check chance Rand.MTBEventOccurs uses for
        /// the ordinary emergence (checkDuration / (mtb * mtbUnit), capped at
        /// 1) — a state read, not a sampled count.</summary>
        public float EffectiveEmergenceChancePerCheck =>
            RM_BroodKernel.EmergenceChancePerCheck(EffectiveAmbientMtbHours);

        /// <summary>The young came home to a pool here: within the hour the
        /// deep sets down one great gift beside it.</summary>
        public void ScheduleDeepGift(IntVec3 pool, int rolls = 1)
        {
            pendingGiftTicks.Add(Find.TickManager.TicksGame + Rand.RangeInclusive(600, 2200)); // INVENTED: "within an hour"
            pendingGiftCells.Add(pool);
            pendingGiftRolls.Add(UnityEngine.Mathf.Max(1, rolls));
        }

        private void TickPendingGifts()
        {
            List<KeyValuePair<IntVec3, int>> due = RM_BroodKernel.CollectDue(pendingGiftTicks, pendingGiftCells, pendingGiftRolls,
                Find.TickManager.TicksGame);
            for (int i = 0; i < due.Count; i++)
            {
                if (RM_FeverWoodSettings.broodRansomEnabled)
                {
                    RM_DeepGift.Grant(map, due[i].Key, due[i].Value);
                }
            }
        }

        /// <summary>"Large pool + many limbs" detection — see class header
        /// for why this composed threshold, not §6d's full four-input
        /// model, is what this item builds.</summary>
        private bool GreatEmergenceEligible(List<IntVec3> pools)
        {
            return RM_PoolKernel.GreatEligible(pools.Count, RM_FeverWoodSettings.tentacleGreatEmergencePoolSizeThreshold,
                encounterPressure, RM_FeverWoodSettings.tentacleGreatEmergencePressureThreshold);
        }

        private void SpawnEncounter(List<IntVec3> pools)
        {
            SpawnEncounterAt(pools[Rand.Range(0, pools.Count)], pools);
        }

        private void SpawnEncounterAt(IntVec3 seed, List<IntVec3> pools)
        {
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

            encounterPressure = RM_PoolKernel.PressureAfter(encounterPressure, AmbientKind.Ordinary); // §6d: "every ordinary encounter... is a deposit toward its big one"
        }

        /// <summary>The distinct set-piece (§2b row 3, owner verbatim: "a
        /// massive attack in a large pool with many tentacles and the eye
        /// itself"). Spawns several ordinary limbs together with a Bloom at
        /// the same qualifying pool and announces it as a real Letter,
        /// deliberately louder than SpawnEncounter's silent ordinary
        /// spawns — "genuinely distinct, bigger, rarer, more dramatic"
        /// per the 2026-09-29 ruling. Consumes (resets) the accumulated
        /// pressure that made it eligible.</summary>
        private void SpawnGreatEmergence(List<IntVec3> pools)
        {
            IntVec3 seed = pools[Rand.Range(0, pools.Count)];

            int minLimbs = UnityEngine.Mathf.Max(1, RM_FeverWoodSettings.tentacleGreatEmergenceMinLimbs);
            int maxLimbs = UnityEngine.Mathf.Max(minLimbs, RM_FeverWoodSettings.tentacleGreatEmergenceMaxLimbs);
            int limbCount = Rand.RangeInclusive(minLimbs, maxLimbs);

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

            ThingDef bloomDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Sekkulaath_Bloom");
            if (bloomDef != null)
            {
                Thing bloom = ThingMaker.MakeThing(bloomDef);
                GenSpawn.Spawn(bloom, seed, map);
            }

            encounterPressure = RM_PoolKernel.PressureAfter(encounterPressure, AmbientKind.Great);

            Find.LetterStack.ReceiveLetter(
                "The Great Emergence",
                "The water at a large pool churns and breaks open — many tentacles rise together, and beneath them, exposed for one long moment, the eye itself. This is the strategic moment: driving off or killing the eye ends the whole attack. There is no protection here beyond what you can see coming.",
                LetterDefOf.ThreatBig, new TargetInfo(seed, map));
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
            float[] weights = new float[AmbientTable.Length];
            bool[] skipped = new bool[AmbientTable.Length];
            for (int i = 0; i < AmbientTable.Length; i++)
            {
                skipped[i] = porterAngeredForever && AmbientTable[i].defName == "RM_Sekkulaath_Porter";
                weights[i] = WeightOf(i);
            }
            float total = 0f;
            for (int i = 0; i < weights.Length; i++)
            {
                if (!skipped[i])
                {
                    total += weights[i];
                }
            }
            if (total <= 0f)
            {
                return null;
            }

            int pick = RM_BroodKernel.PickLimb(weights, skipped, Rand.Range(0f, total));
            return pick < 0 ? null : DefDatabase<ThingDef>.GetNamedSilentFail(AmbientTable[pick].defName);
        }

        /// <summary>FEVERWOOD_BROOD_RANSOM_1: the snare and lash weigh more
        /// the more young the world holds ("the snares grow bolder").</summary>
        private static float WeightOf(int i)
        {
            string d = AmbientTable[i].defName;
            bool grows = d == "RM_Sekkulaath_Snare" || d == "RM_Sekkulaath_Lash";
            return RM_BroodKernel.AmbientWeight(grows, AmbientTable[i].weight, grows ? RM_WorldComponent_DeepYoung.BoldnessMultiplier : 1f);
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
            blockedUntilTick = RM_PoolKernel.Extend(blockedUntilTick, RM_PoolKernel.Until(Find.TickManager.TicksGame, cooldownTicks));
        }

        public void OnLimbSevered(int respiteTicks)
        {
            blockedUntilTick = RM_PoolKernel.Extend(blockedUntilTick, RM_PoolKernel.Until(Find.TickManager.TicksGame, respiteTicks));
        }

        /// <summary>FEVERWOOD_OIL_BOIL_WEATHER_1: a burning pool edge wakes the deep. An ORDINARY emergence at the
        /// registered pool cell nearest `near` (never the plot-reserved Great Emergence), plus one extra encounter
        /// pressure. Respects the bestiary switch and a permanent kill; ignores the ambient cooldown (the fire is the
        /// trigger). Returns the number of limbs spawned.</summary>
        public int ForceEmergenceNear(IntVec3 near)
        {
            if (!RM_FeverWoodSettings.tentacleBestiaryEnabled || permanentlyKilled)
            {
                return 0;
            }
            List<IntVec3> pools = PoolCells();
            if (pools.Count == 0)
            {
                return 0;
            }
            IntVec3 seed = pools[0];
            for (int i = 1; i < pools.Count; i++)
            {
                if ((pools[i] - near).LengthHorizontalSquared < (seed - near).LengthHorizontalSquared)
                {
                    seed = pools[i];
                }
            }
            int before = CountLimbs();
            int pressureBefore = encounterPressure;
            SpawnEncounterAt(seed, pools);
            encounterPressure = RM_PoolKernel.PressureAfterForced(pressureBefore);
            return CountLimbs() - before;
        }

        private int CountLimbs()
        {
            int n = 0;
            foreach (string d in AllLimbDefNames)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(d);
                if (def != null)
                {
                    n += map.listerThings.ThingsOfDef(def).Count;
                }
            }
            return n;
        }

        public void OnPorterAttacked()
        {
            porterAngeredForever = true;
        }

        /// <summary>§6f/FEVERWOOD_TENTACLE_SETPIECE_TUNING_1: the Uranium
        /// free-tier suppression trigger. Reuses blockedUntilTick exactly
        /// like OnLimbRetreated/OnLimbSevered — "same shape as a sever's
        /// respite" per this item's own spec. That reuse is also the
        /// answer to §6f's open "does it harm the pool's other content"
        /// question: blockedUntilTick already gates the WHOLE ambient roll
        /// in MapComponentTick (both SpawnEncounter and
        /// SpawnGreatEmergence, which is the only place a Porter — and so
        /// RM_Corvath's treasure trickle — can spawn), so suppressing here
        /// silences hostile encounters and the treasure trickle equally:
        /// "the whole pool going quiet," not a selective effect. Called by
        /// RM_JobDriver_FoulPool once a carried RM_RadioactiveSuppressant
        /// charge is used at a registered pool cell.</summary>
        public void SuppressPoolWithRadioactiveMaterial(int ticks)
        {
            blockedUntilTick = RM_PoolKernel.Extend(blockedUntilTick, RM_PoolKernel.Until(Find.TickManager.TicksGame, ticks));
            Messages.Message(
                "The pool's water clouds and stills. Whatever lives beneath it is driven down by the fouling — no tentacles, and no trickle of scavenged goods, until the material diffuses away.",
                new TargetInfo(map.Center, map), MessageTypeDefOf.PositiveEvent);
        }

        public void DriveOffAllLimbs(int ticks)
        {
            DespawnAllLimbs();
            blockedUntilTick = RM_PoolKernel.Extend(blockedUntilTick, RM_PoolKernel.Until(Find.TickManager.TicksGame, ticks));
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
            sentinelCount = RM_PoolKernel.SentinelUp(sentinelCount, out bool hush);
            if (hush)
            {
                HushChorus();
            }
        }

        public void Notify_SentinelDown()
        {
            sentinelCount = RM_PoolKernel.SentinelDown(sentinelCount, out bool restore);
            if (restore)
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
            Scribe_Values.Look(ref encounterPressure, "encounterPressure", 0);
            Scribe_Collections.Look(ref pendingGiftTicks, "pendingGiftTicks", LookMode.Value);
            Scribe_Collections.Look(ref pendingGiftCells, "pendingGiftCells", LookMode.Value);
            Scribe_Collections.Look(ref pendingGiftRolls, "pendingGiftRolls", LookMode.Value);
            // mismatched tick/cell lists are dropped together; older save or mismatch: every pending gift rolls once
            RM_BroodKernel.RepairQueues(ref pendingGiftTicks, ref pendingGiftCells, ref pendingGiftRolls);
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
