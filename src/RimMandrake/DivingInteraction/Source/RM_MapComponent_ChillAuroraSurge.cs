using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_AURORA_SURGE_1 — aurora surge storms: floor weather you can
    // harvest.
    //
    // Owner, card pick (2026-09-27 sitting): "When the electrojet spikes,
    // the spike reaches the floor as weather: every Iliss lights up, the
    // Skyharps sing loud, and arcs walk across the conductive frost."
    //
    // SCOPE: RM_ChillFireGate.IsChillSeabedMap(map) only, same identity
    // check every sibling Chill mechanism this session uses.
    //
    // ── WHY A THRESHOLD-ON-INTENSITY, NOT A VANILLA WeatherDef ──
    // A vanilla WeatherDef is picked by the map's own weather-commonality
    // machinery — a system built for "which of several ambient weathers is
    // the sky doing right now" on an ordinary sky map. The Chill seabed
    // has no sky (IsPocketMap, RM_ChillFireGate's own header) and already
    // has exactly ONE thing that determines its "weather": the surface
    // aurora's strength, already read, smoothed and exposed by
    // RM_MapComponent_ChillDrownedAurora.CurrentAuroraIntensity. Layering
    // a second, independent weather-picker on top of that single input
    // would just be two systems answering the same question, with its own
    // disconnected commonality/duration tuning. A GameCondition fares no
    // better — per RM_MapComponent_ChillDrownedAurora's own header it
    // cannot even be registered on this map without allowUnderground, and
    // even then can only DARKEN a map's SkyTarget, never drive gameplay
    // state like power output or damage. ⇒ "Surge" is a MAP-STATE bool
    // this component derives by thresholding that same smoothed intensity
    // — the cleanest shape given what CHILL_FLOOR_LIGHT_1 already built.
    //
    // HYSTERESIS: starts once intensity clears SurgeStartThreshold (0.7,
    // the number the ruling itself names), ends only once intensity falls
    // below the lower SurgeEndThreshold (0.6) — cheap insurance against a
    // state that flips every rescan right at the boundary, same shape
    // RM_MapComponent_ChillGardenDefense's own tiered cooldowns exist for,
    // even though CurrentAuroraIntensity is already smoothed (MoveTowards,
    // 0.04/rescan) and unlikely to oscillate on its own.
    //
    // WHAT THIS COMPONENT OWNS:
    //   1. IsSurgeActive / SurgeStrength — the public hook
    //      RM_CompPowerPlantAuroraSurge (deliverable 2, its own file)
    //      reads. SurgeStrength is InverseLerp'd from SurgeStartThreshold,
    //      so it is 0 right at the threshold and 1 at full aurora
    //      intensity — no discontinuous jump the instant a surge begins.
    //   3. Shock risk (deliverable 3) — ScanShockRisk(), a slower-cadence
    //      sweep of every unroofed pawn on this map (excluding the two
    //      current-adapted natives, RM_Iliss and RM_Tarnn — this is their
    //      own weather, not a hazard to them) that rolls a chance of an
    //      ElectricalBurn arc hit, the same damage idiom
    //      RM_MapComponent_ChillGardenDefense's own header already
    //      justifies (DamageWorker_AddInjury workerClass — cannot ignite
    //      anything, compatible with CHILL_FIRE_BAN_1) — tuned harder than
    //      that item's Tier1 sting (this is a whole-map storm, not a
    //      localized punishment), plus a real chance to stagger a caught
    //      pawn via StunHandler.StunFor directly (the same call every
    //      vanilla stun effect uses) rather than relying on TakeDamage's
    //      own auto-stun, which ElectricalBurn does not qualify for
    //      (DamageDef.causeStun is false on it) — "hits/stuns" therefore
    //      reads as two explicit, independently-rolled effects.
    //   4. Creature/plant dressing (deliverable 4) — periodic
    //      ThrowLightningGlow flecks at live RM_Iliss ("every Iliss lights
    //      up") and, camera-sampled like RM_MapComponent_ChillBoilShroud's
    //      own bounded fleck idiom, at visible RM_Skyharp plants ("the
    //      Skyharps sing loud" — read conservatively here as a VISUAL
    //      shimmer flag; a real sound pass is explicitly a future ambience
    //      item's job per CHILL_FLOOR_LIGHT_1's own deferred-sound note,
    //      and this file builds no new sound system to fake it — a future
    //      audio item should hang its SoundDef off IsSurgeActive exactly
    //      the way this dressing does). Plus a general ambient arc fleck
    //      sampled across unroofed camera-visible cells — "arcs walk
    //      across the conductive frost" — same cost-bounded, cosmetic-
    //      only, Find.CurrentMap-gated shape BoilShroud already
    //      established, reused rather than reinvented.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ChillAuroraSurge : MapComponent
    {
        private const string IlissDefName = "RM_Iliss";
        private const string TarnnDefName = "RM_Tarnn";
        private const string SkyharpDefName = "RM_Skyharp";

        private const float SurgeStartThreshold = 0.7f;
        private const float SurgeEndThreshold = 0.6f;

        private const int StateRescanIntervalTicks = 60;
        private const int DressingIntervalTicks = 90;
        private const int ShockCheckIntervalTicks = 250; // CompTickRare's own cadence

        // Expected time-to-first-hit for a pawn standing still and exposed:
        // ~250/0.45 ticks ≈ 9-10 real seconds — enough of a beat to notice
        // the letter and react before the first arc lands. A single hit
        // (9-20, avg ~14.5) is worse than Garden Defense's Tier1 sting
        // (6-14 per hit) as the item asks, but several such hits are
        // needed before a healthy pawn is in real danger — "a competent
        // player has a real window to retreat indoors."
        private const float ShockChancePerCheck = 0.45f;
        private const float ShockDamageMin = 9f;
        private const float ShockDamageMax = 20f;
        private const float ShockStunChance = 0.3f;
        private const int ShockStunTicks = 90; // ~1.5s stagger, not a lockdown

        private const int SamplesPerDressingTick = 4;
        private const float IlissGlowChance = 0.5f;
        private const float SkyharpShimmerChance = 0.12f;
        private const float AmbientArcChance = 0.10f;

        private static ThingDef skyharpDefCache;
        private static bool skyharpLookupDone;

        private bool isChillSeabed;
        private bool surgeActive;

        private int ticksUntilStateRescan = 1;
        private int ticksUntilDressing = 1;
        private int ticksUntilShockCheck = 1;

        public RM_MapComponent_ChillAuroraSurge(Map map) : base(map)
        {
        }

        private bool Active => isChillSeabed
            && RM_DivingSettings.masterEnabled
            && RM_DivingSettings.chillAuroraSurgeEnabled;

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            isChillSeabed = RM_ChillFireGate.IsChillSeabedMap(map);
        }

        /// <summary>
        /// CHILL_AURORA_SURGE_1's own hook — true only on the Chill seabed,
        /// only while the mechanic is enabled, only while the surface
        /// aurora has been above SurgeStartThreshold and has not yet
        /// fallen back below SurgeEndThreshold. Safe to call unconditionally
        /// off-map or with the mechanic disabled — both simply read false.
        /// </summary>
        public bool IsSurgeActive => Active && surgeActive;

        /// <summary>
        /// RM_CompPowerPlantAuroraSurge's own read: 0 whenever IsSurgeActive
        /// is false, otherwise how far above the surge threshold the
        /// surface aurora currently sits, 0 (just crossed) .. 1 (full
        /// intensity). Never a step at the threshold.
        /// </summary>
        public float SurgeStrength
        {
            get
            {
                if (!IsSurgeActive)
                {
                    return 0f;
                }
                RM_MapComponent_ChillDrownedAurora aurora = map.GetComponent<RM_MapComponent_ChillDrownedAurora>();
                float intensity = aurora?.CurrentAuroraIntensity ?? 0f;
                return Mathf.InverseLerp(SurgeStartThreshold, 1f, intensity);
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!isChillSeabed)
            {
                return; // every other map in the game: one bool check, nothing else
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillAuroraSurgeEnabled)
            {
                surgeActive = false; // frozen off while disabled — no stray letters/hits from a toggled-off surge
                return;
            }

            if (--ticksUntilStateRescan <= 0)
            {
                ticksUntilStateRescan = StateRescanIntervalTicks;
                UpdateSurgeState();
            }

            if (!surgeActive)
            {
                return; // no dressing, no risk to roll, while quiet
            }

            if (--ticksUntilDressing <= 0)
            {
                ticksUntilDressing = DressingIntervalTicks;
                ThrowDressingFlecks();
            }

            if (--ticksUntilShockCheck <= 0)
            {
                ticksUntilShockCheck = ShockCheckIntervalTicks;
                ScanShockRisk();
            }
        }

        private void UpdateSurgeState()
        {
            RM_MapComponent_ChillDrownedAurora aurora = map.GetComponent<RM_MapComponent_ChillDrownedAurora>();
            float intensity = aurora?.CurrentAuroraIntensity ?? 0f;

            if (!surgeActive && intensity > SurgeStartThreshold)
            {
                surgeActive = true;
                ticksUntilDressing = 1;
                ticksUntilShockCheck = 1;
                Find.LetterStack.ReceiveLetter(
                    "RM_ChillAuroraSurge_StartLabel".Translate(),
                    "RM_ChillAuroraSurge_StartText".Translate(),
                    LetterDefOf.ThreatSmall, new TargetInfo(map.Center, map));
            }
            else if (surgeActive && intensity < SurgeEndThreshold)
            {
                surgeActive = false;
                Messages.Message("RM_ChillAuroraSurge_End".Translate(), MessageTypeDefOf.SituationResolved, false);
            }
        }

        // ---- deliverable 3: risk. ----
        private void ScanShockRisk()
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || p.Downed || !p.Spawned)
                {
                    continue;
                }
                if (p.def.defName == IlissDefName || p.def.defName == TarnnDefName)
                {
                    continue; // native to the current — this is their weather, not a hazard
                }
                if (p.Position.Roofed(map))
                {
                    continue; // "harvest or hide" — indoors is genuinely safe
                }
                if (!Rand.Chance(ShockChancePerCheck))
                {
                    continue;
                }
                ShockPawn(p);
            }
        }

        private void ShockPawn(Pawn p)
        {
            Vector3 loc = p.Position.ToVector3Shifted();
            FleckMaker.ThrowLightningGlow(loc, map, 1.3f);
            FleckMaker.ThrowMicroSparks(loc, map);

            float dmg = Rand.Range(ShockDamageMin, ShockDamageMax);
            p.TakeDamage(new DamageInfo(DamageDefOf.ElectricalBurn, dmg));

            if (!p.Dead && !p.Downed && Rand.Chance(ShockStunChance))
            {
                p.stances?.stunner?.StunFor(ShockStunTicks, null, false, true);
            }

            if (PawnUtility.ShouldSendNotificationAbout(p))
            {
                Messages.Message(
                    "RM_ChillAuroraSurge_ShockHit".Translate(p.LabelShortCap),
                    p, MessageTypeDefOf.NegativeEvent, false);
            }
        }

        // ---- deliverable 4: dressing. ----
        private void ThrowDressingFlecks()
        {
            if (map != Find.CurrentMap)
            {
                return; // cosmetic-only; a fleck the player cannot see is waste (BoilShroud's own rule)
            }
            CameraDriver camera = Find.CameraDriver;
            if (camera == null)
            {
                return;
            }
            CellRect view = camera.CurrentViewRect;
            view.ClipInsideMap(map);
            if (view.Width <= 0 || view.Height <= 0)
            {
                return;
            }

            ThrowIlissGlow();
            ThrowSkyharpShimmer(view);
            ThrowAmbientArcs(view);
        }

        private void ThrowIlissGlow()
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || !p.Spawned || p.def.defName != IlissDefName)
                {
                    continue;
                }
                if (p.Position.Fogged(map) || !Rand.Chance(IlissGlowChance))
                {
                    continue;
                }
                FleckMaker.ThrowLightningGlow(p.Position.ToVector3Shifted(), map, 0.9f);
            }
        }

        private void ThrowSkyharpShimmer(CellRect view)
        {
            ThingDef skyharpDef = SkyharpDef;
            if (skyharpDef == null)
            {
                return; // def failed to resolve (mod load order); nothing to fleck, nothing to crash
            }
            List<Thing> skyharps = map.listerThings.ThingsOfDef(skyharpDef);
            if (skyharps.Count == 0)
            {
                return;
            }
            for (int i = 0; i < SamplesPerDressingTick; i++)
            {
                Thing plant = skyharps[Rand.Range(0, skyharps.Count)];
                if (plant == null || !plant.Spawned || !view.Contains(plant.Position) || plant.Position.Fogged(map))
                {
                    continue;
                }
                if (!Rand.Chance(SkyharpShimmerChance))
                {
                    continue;
                }
                FleckMaker.ThrowLightningGlow(plant.Position.ToVector3Shifted(), map, 0.6f);
            }
        }

        private void ThrowAmbientArcs(CellRect view)
        {
            for (int i = 0; i < SamplesPerDressingTick; i++)
            {
                IntVec3 cell = new IntVec3(
                    Rand.RangeInclusive(view.minX, view.maxX), 0,
                    Rand.RangeInclusive(view.minZ, view.maxZ));
                if (!cell.InBounds(map) || cell.Roofed(map) || cell.Fogged(map) || !Rand.Chance(AmbientArcChance))
                {
                    continue;
                }
                FleckMaker.ThrowMicroSparks(cell.ToVector3Shifted(), map);
            }
        }

        private static ThingDef SkyharpDef
        {
            get
            {
                if (!skyharpLookupDone)
                {
                    skyharpLookupDone = true;
                    skyharpDefCache = DefDatabase<ThingDef>.GetNamedSilentFail(SkyharpDefName);
                }
                return skyharpDefCache;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref surgeActive, "surgeActive", false);
        }
    }
}
