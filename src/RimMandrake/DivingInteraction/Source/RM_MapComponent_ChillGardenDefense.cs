using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.DivingInteraction
{
    /// <summary>
    /// What kind of act against the Chill's seabed garden is being reported to
    /// RM_MapComponent_ChillGardenDefense.RegisterOffense. DrillAgitation is
    /// CHILL_WARLAB_ROUTES_1's own future hook and is routed to
    /// RegisterDrillAgitation internally — see that method's doc comment for
    /// why it can never escalate to the Tarnn wake.
    /// </summary>
    // ════════════════════════════════════════════════════════════════════
    // CHILL_GARDEN_DEFENSE_1 — the garden's tiered immune system.
    //
    // Owner, typed verbatim (2026-09-27): the seabed garden should feel
    // "delicate, entrancing, precious, shocking when it can actually defend
    // itself but quite overcomable." Card-ruled: tiered — Iliss first, then
    // Tarnn.
    //
    // SCOPE: RM_ChillFireGate.IsChillSeabedMap(map) only, same identity check
    // every sibling Chill mechanism uses (CHILL_FIRE_BAN_1/THERMAL_ENGINE_1/
    // HEATED_SUIT_1) — a bare biome-defName check cannot tell the seabed from
    // the surface Chill tile, both carry biome RM_TheChill.
    //
    // TWO SEPARATE ACCUMULATORS, ON PURPOSE:
    //   offenseScore    — fed by Harvest/Kill/HeatDamage. Can cross EITHER
    //                      tier threshold.
    //   agitationScore  — fed ONLY by RegisterDrillAgitation (the future
    //                      drilling item's hook). Can cross ONLY the Iliss
    //                      tier — there is no method call anywhere on that
    //                      path that can reach FireTier2Wake, so "drilling
    //                      escalates to a Tarnn wake" is not a tuning
    //                      mistake away, it is a method that does not exist.
    // Both accumulators reset to 0 the moment they cross a threshold and
    // fire — this is EDGE-TRIGGERED (one incident per crossing), not a
    // level trigger that refires every tick the score sits above the line;
    // each tier also carries its own real-time cooldown so a single burst of
    // offenses cannot double-fire in the same moment.
    //
    // CHILL_THERMAL_FOOTPRINTS_1, 2026-09-28: every threshold comparison
    // below goes through AdjustedThreshold(), which discounts the base
    // threshold by up to TrailThresholdDiscount at a cell RM_MapComponent_
    // ChillFootprints reports as heavily trailed — "a second visit finds
    // the first visit waiting." Additive only: a pristine cell (density 0)
    // gets the exact same threshold as before this item existed.
    //
    // WHY ElectricalBurn (RimWorld/DamageDefOf.cs, [MayRequireAnomaly] —
    // fine, CLAUDE.md: "assume all the DLCs") is the arc's damage type:
    // MEASURED off the decompiled engine (RimSage) — it is ParentName="Flame"
    // for its armor/hediff shape (BurnBase hediff, can scar) but its own
    // workerClass is DamageWorker_AddInjury, NOT DamageWorker_Flame, so
    // applying it directly (Thing.TakeDamage, never GenExplosion) can never
    // ignite anything — it is already vanilla's OWN idiom for "a punishing
    // electric zap with no fire risk" (Building_HoldingPlatform.Tick applies
    // it exactly this way for an attached electroharvester). That makes it
    // the one damage type that is simultaneously thematically exact
    // ("current-eels", "conductive frost") and provably compatible with
    // CHILL_FIRE_BAN_1's total ignition ban on this same map.
    //
    // WHY NO LIVE ILISS IS SPAWNED: the item's own text invites this choice
    // ("a lightweight standalone arc effect that doesn't require summoning/
    // spawning an actual Iliss pawn each time") — spawning a real pawn per
    // offense would need despawn bookkeeping, would count against the map's
    // animal-ecosystem cap, and buys nothing the direct effect doesn't
    // already deliver. The visual (FleckMaker.ThrowLightningGlow — the exact
    // call CompShield uses for a shield deflecting a hit, and
    // WeatherEvent_LightningStrike uses for an actual lightning bolt; no new
    // FleckDef) plus a direct DamageInfo(ElectricalBurn) IS "a literal
    // electric arc-discharge through the conductive frost around the
    // offender."
    //
    // TARNN WAKE — CompCanBeDormant IS the right mechanism, ADDED to
    // RM_Tarnn's ThingDef by this item (RM_TheChillFloorLife.xml): every
    // RM_Tarnn that will ever exist is spawned exclusively by
    // GenStep_SeaFloorFauna reading RM_TheChill's <wildAnimals> — MEASURED
    // off that GenStep's own header comment, a sea BiomeDef's <wildAnimals>
    // is never consulted by vanilla's ambient spawner at all, so this
    // GenStep (which runs ONLY when generating the seabed pocket map) is the
    // ONLY place a Tarnn is ever created. startsDormant/jobDormancy therefore
    // only ever affects pocket-map Tarnn, never a hypothetical surface one.
    // WakeUp() + forced ManhunterPermanent (not the recoverable Manhunter —
    // deterministic once-woken-stays-woken, same "already fought, now what"
    // shape as vanilla's own dormant ancient-danger mechanoids, which are
    // simply hostile forever once woken, never re-dormant) turns "several at
    // once" into a real, bounded fight. RM_CompTarnnRoused (added to the same
    // ThingDef) is what actually makes a woken Tarnn dangerous — see that
    // file for why the base def alone (MoveSpeed 0.3, melee power 1) cannot
    // supply "genuinely frightening" without it, and for the overcomable math.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ChillGardenDefense : MapComponent
    {
        private const string TarnnDefName = "RM_Tarnn";

        // ---- offense weights. A single kill or a single directed heat hit
        // crosses Tier1 (=Tier1Threshold) ALONE — the ruling lists them as
        // flat "first offenses," not something that needs repetition to
        // register. Harvesting is explicitly "past a threshold" in the
        // ruling's own wording, so its weight is deliberately small (about
        // 8 harvests to reach Tier1 by harvesting alone). ----

        // Weights, thresholds and cooldowns live in RM_GardenDefenseKernel (offline-fuzzed). Tier2 = 16 is "sustained":
        // roughly 4 kills/heat-hits, or a large mixed pattern.

        // CHILL_THERMAL_FOOTPRINTS_1, 2026-09-28. "A second visit finds the
        // first visit waiting" — a cell heavily marked by
        // RM_MapComponent_ChillFootprints (thermal footprints, trail
        // density 0..1) reads as more "known/disturbed," so all three
        // thresholds below are discounted proportionally to the trail
        // density AT THE OFFENSE CELL, up to this fraction at full
        // saturation (density 1). Density 0 (pristine ground, or the
        // footprint mechanism toggled off / map not Chill seabed) leaves
        // every threshold exactly as it was — purely additive, no existing
        // tuning changes for untouched ground.


        private const float Tier1ArcDamageMin = 6f;
        private const float Tier1ArcDamageMax = 14f;
        private const int Tier1ArcHits = 2; // ~12-28 total (avg ~20) across one arc event — stinging, not remotely lethal on its own

        private static readonly IntRange WakeCountRange = new IntRange(3, 5); // "several at once", "hard skirmish, NOT a raid"
        private const float WakeSearchRadius = 60f; // pocket maps run ~50x50 (GenStep_SeaFloorFauna's own comment); this reaches essentially the whole floor

        private bool isChillSeabed;

        private float offenseScore;
        private float escalationScore;
        private float agitationScore;

        private int tier1CooldownUntilTick = -1;
        private int tier2CooldownUntilTick = -1;
        private int agitationCooldownUntilTick = -1;

        public RM_MapComponent_ChillGardenDefense(Map map) : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            isChillSeabed = RM_ChillFireGate.IsChillSeabedMap(map);
        }

        private bool Active => isChillSeabed
            && RM_DivingSettings.masterEnabled
            && RM_DivingSettings.chillGardenDefenseEnabled;

        /// <summary>
        /// Report a harvest, a floor-life kill, or a directed-heat hit
        /// against the garden. offender may be null (e.g. an indirect kill);
        /// the arc simply has nobody to zap in that case, the accumulator
        /// still moves. Call this from wherever the act is actually
        /// detected — see Patch_ChillGardenDefense.cs for the two hooks this
        /// item wires (Plant.PlantCollected, Thing.PostApplyDamage).
        /// </summary>
        public void RegisterOffense(RM_GardenOffenseKind kind, Pawn offender, IntVec3 cell)
        {
            if (!Active)
            {
                return;
            }
            if (kind == RM_GardenOffenseKind.DrillAgitation)
            {
                RegisterDrillAgitation(cell, offender);
                return;
            }

            int now = Find.TickManager.TicksGame;
            RM_GardenDefenseKernel.State st = KernelState();
            RM_GardenDefenseKernel.Outcome outcome = RM_GardenDefenseKernel.Offense(ref st, kind, now, TrailDensity(cell));
            StoreKernelState(st);

            if (outcome == RM_GardenDefenseKernel.Outcome.Tier2Wake)
            {
                FireTier2Wake(cell);
            }
            else if (outcome == RM_GardenDefenseKernel.Outcome.Tier1Arc)
            {
                FireTier1Arc(cell, offender);
            }
        }

        /// <summary>
        /// CHILL_WARLAB_ROUTES_1's hook: register that drilling has agitated
        /// the garden at <paramref name="cell"/>. Card ruling on that item:
        /// "drilling agitates — arcs harass the work site, a thin scar
        /// remains, but no Tarnn wake and nothing permanent at scale."
        ///
        /// Hard-capped to the Iliss tier by CONSTRUCTION, not by tuning:
        /// this method reads and writes ONLY agitationScore, never
        /// offenseScore, and the only effect it can ever fire is
        /// FireTier1Arc. There is no threshold, multiplier or accumulation
        /// rate at which calling this wakes the Tarnn — that call simply
        /// does not exist on this path, no matter how many times or how
        /// fast a future drilling mechanism calls it.
        /// </summary>
        public void RegisterDrillAgitation(IntVec3 cell, Pawn operatorPawn = null)
        {
            if (!Active)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            RM_GardenDefenseKernel.State st = KernelState();
            bool fire = RM_GardenDefenseKernel.Agitation(ref st, now, TrailDensity(cell));
            StoreKernelState(st);
            if (fire)
            {
                FireTier1Arc(cell, operatorPawn);
            }
        }

        // CHILL_THERMAL_FOOTPRINTS_1's read hook: RM_MapComponent_
        // ChillFootprints.TrailDensityAt returns 0 whenever it has nothing
        // to say (off map, toggled off, no filth here yet), so this is
        // safe to call unconditionally and never needs its own Active
        // gate beyond the null-conditional lookup itself.
        private float TrailDensity(IntVec3 cell)
        {
            return map.GetComponent<RM_MapComponent_ChillFootprints>()?.TrailDensityAt(cell) ?? 0f;
        }

        private RM_GardenDefenseKernel.State KernelState()
        {
            return new RM_GardenDefenseKernel.State
            {
                offenseScore = offenseScore,
                escalationScore = escalationScore,
                agitationScore = agitationScore,
                tier1CooldownUntilTick = tier1CooldownUntilTick,
                tier2CooldownUntilTick = tier2CooldownUntilTick,
                agitationCooldownUntilTick = agitationCooldownUntilTick,
            };
        }

        private void StoreKernelState(RM_GardenDefenseKernel.State st)
        {
            offenseScore = st.offenseScore;
            escalationScore = st.escalationScore;
            agitationScore = st.agitationScore;
            tier1CooldownUntilTick = st.tier1CooldownUntilTick;
            tier2CooldownUntilTick = st.tier2CooldownUntilTick;
            agitationCooldownUntilTick = st.agitationCooldownUntilTick;
        }

        // ---- Tier 1: the Iliss arc. Stinging, eerie, survivable. ----
        private void FireTier1Arc(IntVec3 cell, Pawn offender)
        {
            if (map == null || !cell.IsValid || !cell.InBounds(map))
            {
                return;
            }

            Vector3 loc = cell.ToVector3Shifted();
            for (int i = 0; i < 3; i++)
            {
                FleckMaker.ThrowLightningGlow(loc, map, 1.6f);
            }
            FleckMaker.ThrowMicroSparks(loc, map);

            SoundDef zapSound = DefDatabase<SoundDef>.GetNamedSilentFail("EnergyShield_Broken");
            zapSound?.PlayOneShot(SoundInfo.InMap(new TargetInfo(cell, map)));

            if (offender == null || offender.Dead || !offender.Spawned || offender.Map != map)
            {
                return; // drilling with nobody standing there right now, or the offender already left — the light show still reads, nothing left to zap
            }

            for (int i = 0; i < Tier1ArcHits; i++)
            {
                float dmg = Rand.Range(Tier1ArcDamageMin, Tier1ArcDamageMax);
                offender.TakeDamage(new DamageInfo(DamageDefOf.ElectricalBurn, dmg));
            }

            if (PawnUtility.ShouldSendNotificationAbout(offender))
            {
                Messages.Message(
                    "RM_ChillGardenDefense_IlissArc".Translate(offender.LabelShortCap),
                    offender, MessageTypeDefOf.NegativeEvent, false);
            }
        }

        // ---- Tier 2: the Tarnn wake. Several at once, bounded, one-time
        // per crossing — see the class header for why CompCanBeDormant +
        // ManhunterPermanent is the mechanism and RM_CompTarnnRoused.cs for
        // why the wake is dangerous at all. ----
        private void FireTier2Wake(IntVec3 site)
        {
            List<Pawn> dormantTarnn = new List<Pawn>();
            IReadOnlyList<Pawn> allPawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < allPawns.Count; i++)
            {
                Pawn p = allPawns[i];
                if (p == null || p.Dead || p.def.defName != TarnnDefName)
                {
                    continue;
                }
                CompCanBeDormant dormant = p.TryGetComp<CompCanBeDormant>();
                if (dormant == null || dormant.Awake)
                {
                    continue;
                }
                if (p.Position.DistanceTo(site) > WakeSearchRadius)
                {
                    continue;
                }
                dormantTarnn.Add(p);
            }

            if (dormantTarnn.Count == 0)
            {
                return; // nothing left dormant on this map — the incident still happened (the caller already reset the score); there is simply no cast left to wake
            }

            // Nearest-first insertion sort — dormantTarnn is small (a whole
            // pocket map's Tarnn population, ecoSystemWeight 0.15), so this
            // is cheap and avoids pulling in System.Linq for one call site.
            for (int i = 1; i < dormantTarnn.Count; i++)
            {
                Pawn key = dormantTarnn[i];
                float keyDist = key.Position.DistanceTo(site);
                int j = i - 1;
                while (j >= 0 && dormantTarnn[j].Position.DistanceTo(site) > keyDist)
                {
                    dormantTarnn[j + 1] = dormantTarnn[j];
                    j--;
                }
                dormantTarnn[j + 1] = key;
            }

            int wakeCount = Mathf.Min(dormantTarnn.Count, WakeCountRange.RandomInRange);
            for (int i = 0; i < wakeCount; i++)
            {
                Pawn t = dormantTarnn[i];
                t.TryGetComp<CompCanBeDormant>()?.WakeUp();
                t.mindState?.mentalStateHandler?.TryStartMentalState(
                    MentalStateDefOf.ManhunterPermanent,
                    "RM_ChillGardenDefense_TarnnWokeReason".Translate(),
                    true, true);
                t.TryGetComp<RM_CompTarnnRoused>()?.Rouse();
                FleckMaker.ThrowLightningGlow(t.Position.ToVector3Shifted(), map, 2.4f);
            }

            Find.LetterStack.ReceiveLetter(
                "RM_ChillGardenDefense_TarnnWokeLabel".Translate(),
                "RM_ChillGardenDefense_TarnnWokeText".Translate(wakeCount),
                LetterDefOf.ThreatBig, new TargetInfo(site, map));
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref offenseScore, "offenseScore", 0f);
            Scribe_Values.Look(ref escalationScore, "escalationScore", 0f);
            Scribe_Values.Look(ref agitationScore, "agitationScore", 0f);
            Scribe_Values.Look(ref tier1CooldownUntilTick, "tier1CooldownUntilTick", -1);
            Scribe_Values.Look(ref tier2CooldownUntilTick, "tier2CooldownUntilTick", -1);
            Scribe_Values.Look(ref agitationCooldownUntilTick, "agitationCooldownUntilTick", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && escalationScore < offenseScore)
            {
                escalationScore = offenseScore; // old saves have no escalation pool; it can never be below the tier-1 pool
            }
        }
    }
}
