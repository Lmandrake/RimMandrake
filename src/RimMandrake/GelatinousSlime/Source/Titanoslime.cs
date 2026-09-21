using System;
using System.Collections.Generic;
using System.Reflection;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // RM_CompProperties_Engulfer — the tuning surface of the titanoslime.
    //
    // TITANOSLIME_SLIME_BIOME_1, design/RimMandrake/RM_titanoslime_spec.md.
    // Everything here is XML-tunable so the first live look can retune the
    // creature without a rebuild. Every number is [INVENTED] per spec §2/§4.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_Engulfer : CompProperties
    {
        /// <summary>absorbedMass needed to REACH each stage above the first.
        /// Four entries for five stages (spec §2.3).</summary>
        public List<float> stageThresholds = new List<float> { 4f, 12f, 28f, 60f };

        /// <summary>Hysteresis: a stage is lost only this far below the
        /// threshold that gained it, so one shed cannot flip a stage twice.</summary>
        public float stageHysteresis = 1f;

        /// <summary>Hard ceiling on absorbedMass, so a colossus can lose a
        /// fight's worth of mass before dropping a stage.</summary>
        public float massCap = 80f;

        /// <summary>Prey gate: prey.BodySize must be at or below this fraction
        /// of the slime's own BodySize. "Nearly any size" is earned by growing.</summary>
        public float preyBodySizeFraction = 0.5f;

        /// <summary>One held thing per this much of the slime's BodySize
        /// (floored, minimum 1): 1 / 2 / 4 / 6 / 10 across the ladder.</summary>
        public float bodySizePerHeldThing = 4f;

        /// <summary>Digestion time in SECONDS by prey BodySize. A colonist
        /// (0.7-1.0) gets roughly 75 s — about 1.8 in-game hours, a real
        /// rescue window against a stage-1 and a hard one against a stage-4.</summary>
        public SimpleCurve bodySizeDigestTimeCurve = new SimpleCurve
        {
            new CurvePoint(0.2f, 20f),
            new CurvePoint(1f, 75f),
            new CurvePoint(2.5f, 150f),
            new CurvePoint(5f, 240f),
            new CurvePoint(10f, 400f)
        };

        /// <summary>AcidBurn dealt to a pawn released alive, by seconds held.</summary>
        public SimpleCurve timeDamageCurve = new SimpleCurve
        {
            new CurvePoint(0f, 4f),
            new CurvePoint(60f, 24f),
            new CurvePoint(150f, 45f)
        };

        /// <summary>absorbedMass gained per point of nutrition eaten the
        /// ordinary way (corpses, raw slime, slime-grass).</summary>
        public float massPerNutrition = 0.25f;

        /// <summary>absorbedMass lost per day while starving.</summary>
        public float massLostPerDayStarving = 1f;

        /// <summary>absorbedMass lost per day while off slime terrain, after
        /// a full day away.</summary>
        public float massLostPerDayDry = 0.5f;

        /// <summary>How far the slime may be from slime terrain and still
        /// count as "on the body".</summary>
        public int slimeTerrainSearchRadius = 3;

        /// <summary>Extra terrains that count as the body. The mod's own
        /// terrains are found by the RM_SlimeTerrain tag; this list is how the
        /// campaign layer adds its own (AB_* and friends) without code.</summary>
        public List<TerrainDef> extraSlimeTerrains = new List<TerrainDef>();

        /// <summary>Damage taken, as a fraction of MaxHitPoints, between
        /// shedding one gelatid (spec §3.4).</summary>
        public float shedDamageFraction = 0.12f;

        /// <summary>absorbedMass lost per gelatid shed.</summary>
        public float massPerShed = 1f;

        /// <summary>PawnKind shed when cut. Resolved by name so a mod list
        /// without the gelatid simply sheds nothing.</summary>
        public string shedPawnKind = "RM_Gelatid";

        /// <summary>Wild-spawn starting mass table: weight, then mass.
        /// Stages 4-5 are only ever EARNED on the player's map.</summary>
        public List<float> spawnMassWeights = new List<float> { 0.6f, 0.3f, 0.1f };
        public List<float> spawnMassValues = new List<float> { 0f, 4f, 12f };

        public RM_CompProperties_Engulfer()
        {
            compClass = typeof(RM_CompEngulfer);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (stageThresholds == null || stageThresholds.Count < 1)
            {
                yield return "RM_CompProperties_Engulfer needs at least one stage threshold.";
            }
            if (parentDef != null && parentDef.race != null && parentDef.race.lifeStageAges != null
                && stageThresholds != null
                && parentDef.race.lifeStageAges.Count != stageThresholds.Count + 1)
            {
                yield return "RM_CompProperties_Engulfer: " + (stageThresholds.Count + 1)
                             + " stages implied by stageThresholds but the race declares "
                             + parentDef.race.lifeStageAges.Count + " lifeStageAges.";
            }
            if (bodySizePerHeldThing <= 0f)
            {
                yield return "RM_CompProperties_Engulfer bodySizePerHeldThing must be > 0.";
            }
            if (preyBodySizeFraction <= 0f)
            {
                yield return "RM_CompProperties_Engulfer preyBodySizeFraction must be > 0.";
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // RM_CompEngulfer — growth and the swallow, in one comp, with no Harmony
    // and no DLC def anywhere in it.
    //
    // GROWTH (spec §2). Pawn.BodySize is
    // ageTracker.CurLifeStage.bodySizeFactor * RaceProps.baseBodySize — a
    // computed property, not a settable field (MEASURED, Verse/Pawn.cs). The
    // route taken is therefore to move the STAGE, not the size:
    // Pawn_AgeTracker.LockCurrentLifeStageIndex(int) is public and its
    // lockedLifeStageIndex is scribed (MEASURED, Verse/Pawn_AgeTracker.cs:504),
    // and while locked AgeTickInterval returns early, so no birthday, no
    // natural growth and no age-reversal demand ever fires. Locking the index
    // moves mass, health, melee damage, hunger, the sprite's drawSize, the
    // Titanic Creatures tier and the Large Pawns footprint together, because
    // all six read BodySize or the kind life-stage.
    //
    // THE SWALLOW (spec §4). The hold is vanilla CompDevourer's shape
    // verbatim — despawn into a ThingOwner with LookMode.Deep and
    // removeContentsIfDestroyed false, Scribe_Deep, drop on downed or killed —
    // because that is the save-safe shape. What is NOT carried over: the
    // Anomaly job, the Anomaly animation, the Anomaly ability, the single-slot
    // limit and the "release alive" ending.
    //
    // 🔴 NOTHING HERE MAY HARD-REFERENCE AN ANOMALY DEF. That is the reason
    // this class exists at all instead of a CompProperties_Devourer on the
    // race; JobDefOf.DevourerDigest, AnimationDefOf.DevourerDigesting and
    // AbilityDefOf.ConsumeLeap_Devourer are all Defs/Anomaly/ content and a
    // base-game load would fail on them.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompEngulfer : ThingComp, IThingHolder
    {
        private const int TickInterval = 120;
        private const int RecordPollInterval = 250;
        private const int DecayInterval = 2500;

        private ThingOwner<Thing> innerContainer;

        // Parallel to innerContainer's contents, keyed by thingIDNumber rather
        // than by index, because things leave the container from the middle.
        private List<int> heldIds = new List<int>();
        private List<int> heldTicks = new List<int>();
        private List<int> heldDigestTicks = new List<int>();
        private List<bool> heldWasDrafted = new List<bool>();

        private float absorbedMass;
        private float lastNutritionEaten = -1f;
        private int ticksOffSlime;
        private float damageSinceShed;
        private int highestStageAnnounced = -1;
        private int ticksUntilRound;
        private int ticksUntilRecordPoll;
        private int ticksUntilDecay;

        public RM_CompProperties_Engulfer Props { get { return (RM_CompProperties_Engulfer)props; } }

        public Pawn Pawn { get { return parent as Pawn; } }

        public float AbsorbedMass { get { return absorbedMass; } }

        public int HeldCount { get { return innerContainer == null ? 0 : innerContainer.Count; } }

        public RM_CompEngulfer()
        {
            innerContainer = new ThingOwner<Thing>(this, LookMode.Deep, false);
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public ThingOwner GetDirectlyHeldThings()
        {
            return innerContainer;
        }

        // ── stage arithmetic ────────────────────────────────────────────

        private int MaxStageIndex
        {
            get
            {
                int declared = Props.stageThresholds.Count; // last index
                int fromSettings = Mathf.Clamp(SlimeSettings.titanoslimeMaxStage, 1, declared + 1) - 1;
                return Mathf.Min(declared, fromSettings);
            }
        }

        /// <summary>Stage index (0-based) for a mass, starting from the
        /// current one so the hysteresis band has something to hold onto.</summary>
        private int StageFor(float mass, int current)
        {
            List<float> up = Props.stageThresholds;
            int stage = Mathf.Clamp(current, 0, up.Count);
            while (stage < MaxStageIndex && mass >= up[stage])
            {
                stage++;
            }
            while (stage > 0 && mass < up[stage - 1] - Props.stageHysteresis)
            {
                stage--;
            }
            return Mathf.Min(stage, MaxStageIndex);
        }

        /// <summary>The one place the life stage is written. Everything that
        /// changes absorbedMass calls this afterwards.</summary>
        private void ApplyStage(bool announce)
        {
            Pawn self = Pawn;
            if (self == null || self.ageTracker == null)
            {
                return;
            }
            absorbedMass = Mathf.Clamp(absorbedMass, 0f, Props.massCap);
            int current = self.ageTracker.CurLifeStageIndex;
            int target = StageFor(absorbedMass, current);
            if (target != current)
            {
                // RecalculateLifeStageIndex (called from inside this) already
                // does SetAllGraphicsDirty, Notify_LifeStageStarted and
                // AddAndRemoveDynamicComponents — MEASURED. Nothing else here.
                self.ageTracker.LockCurrentLifeStageIndex(target);
            }
            else if (self.ageTracker.CurLifeStageIndex != target)
            {
                self.ageTracker.LockCurrentLifeStageIndex(target);
            }

            if (announce && target > highestStageAnnounced && target > 0 && self.Spawned)
            {
                highestStageAnnounced = target;
                string label = self.ageTracker.CurLifeStage != null
                    ? self.ageTracker.CurLifeStage.label
                    : "titanoslime";
                if (target >= 3)
                {
                    Find.LetterStack.ReceiveLetter(
                        "A " + label,
                        "The titanoslime has grown again. It is now a " + label
                        + " — a hill of jelly that can swallow most things that walk.",
                        LetterDefOf.ThreatBig,
                        new TargetInfo(self.Position, self.Map));
                }
                else
                {
                    Messages.Message("The titanoslime has grown. It is now a " + label + ".",
                                     self, MessageTypeDefOf.ThreatSmall, false);
                }
            }
            if (target < highestStageAnnounced)
            {
                highestStageAnnounced = target;
            }
        }

        /// <summary>Called by every growth source. Respects the growth toggle.</summary>
        private void AddMass(float delta)
        {
            if (!SlimeSettings.titanoslimeGrows)
            {
                return;
            }
            if (delta < 0f && !SlimeSettings.titanoslimeReversible)
            {
                return;
            }
            absorbedMass = Mathf.Clamp(absorbedMass + delta, 0f, Props.massCap);
            ApplyStage(delta > 0f);
        }

        // ── lifecycle ───────────────────────────────────────────────────

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            Pawn self = Pawn;
            if (self == null)
            {
                return;
            }

            if (!respawningAfterLoad && lastNutritionEaten < 0f)
            {
                absorbedMass = RollStartingMass();
                highestStageAnnounced = StageFor(absorbedMass, 0);
            }
            if (self.records != null && RecordDefOf.NutritionEaten != null)
            {
                lastNutritionEaten = self.records.GetValue(RecordDefOf.NutritionEaten);
            }
            else
            {
                lastNutritionEaten = 0f;
            }
            // Locks the stage before the first tick, so PawnGenerator's random
            // age never decides how big a titanoslime is.
            ApplyStage(false);
        }

        private float RollStartingMass()
        {
            List<float> w = Props.spawnMassWeights;
            List<float> v = Props.spawnMassValues;
            if (w == null || v == null || w.Count == 0 || w.Count != v.Count)
            {
                return 0f;
            }
            float total = 0f;
            for (int i = 0; i < w.Count; i++)
            {
                total += w[i];
            }
            if (total <= 0f)
            {
                return 0f;
            }
            float roll = Rand.Value * total;
            for (int i = 0; i < w.Count; i++)
            {
                roll -= w[i];
                if (roll <= 0f)
                {
                    return v[i];
                }
            }
            return v[v.Count - 1];
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref absorbedMass, "absorbedMass", 0f);
            Scribe_Values.Look(ref lastNutritionEaten, "lastNutritionEaten", -1f);
            Scribe_Values.Look(ref ticksOffSlime, "ticksOffSlime", 0);
            Scribe_Values.Look(ref damageSinceShed, "damageSinceShed", 0f);
            Scribe_Values.Look(ref highestStageAnnounced, "highestStageAnnounced", -1);
            Scribe_Collections.Look(ref heldIds, "heldIds", LookMode.Value);
            Scribe_Collections.Look(ref heldTicks, "heldTicks", LookMode.Value);
            Scribe_Collections.Look(ref heldDigestTicks, "heldDigestTicks", LookMode.Value);
            Scribe_Collections.Look(ref heldWasDrafted, "heldWasDrafted", LookMode.Value);
            Scribe_Deep.Look(ref innerContainer, "innerContainer", this);

            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (heldIds == null) heldIds = new List<int>();
                if (heldTicks == null) heldTicks = new List<int>();
                if (heldDigestTicks == null) heldDigestTicks = new List<int>();
                if (heldWasDrafted == null) heldWasDrafted = new List<bool>();
                if (innerContainer == null)
                {
                    innerContainer = new ThingOwner<Thing>(this, LookMode.Deep, false);
                }
                // The same guard vanilla's CompDevourer carries: a container
                // that came back flagged to destroy its contents would delete
                // a swallowed colonist on the slime's death.
                if (innerContainer.removeContentsIfDestroyed)
                {
                    innerContainer.removeContentsIfDestroyed = false;
                }
            }
        }

        // ── the gate and the swallow ────────────────────────────────────

        public int Capacity
        {
            get
            {
                Pawn self = Pawn;
                if (self == null)
                {
                    return 1;
                }
                return Mathf.Max(1, Mathf.FloorToInt(self.BodySize / Props.bodySizePerHeldThing));
            }
        }

        public bool CanEngulf(Pawn p)
        {
            if (!SlimeSettings.titanoslimeEngulfs)
            {
                return false;
            }
            Pawn self = Pawn;
            if (self == null || p == null || p == self || !self.Spawned || self.Dead || self.Downed)
            {
                return false;
            }
            if (!p.Spawned || p.Dead)
            {
                return false;
            }
            // Mechanoids are slammed, never swallowed — nothing to read.
            if (p.RaceProps == null || !p.RaceProps.IsFlesh)
            {
                return false;
            }
            if (p.BodySize > self.BodySize * Props.preyBodySizeFraction)
            {
                return false;
            }
            if (innerContainer.Count >= Capacity)
            {
                return false;
            }
            if (p.ParentHolder is RM_CompEngulfer)
            {
                return false;
            }
            // A colossus may absorb a young one; equals cannot eat each other.
            if (p.def == self.def && p.BodySize >= self.BodySize)
            {
                return false;
            }
            return true;
        }

        public void Engulf(Pawn p)
        {
            Pawn self = Pawn;
            if (self == null || p == null || !p.Spawned)
            {
                return;
            }

            // The Devourer's trick, MEASURED: tell the victim's lord it took
            // damage so a raid reacts to one of its own vanishing.
            DamageInfo notice = new DamageInfo(DamageDefOf.AcidBurn, 99f, 0f, -1f, self);
            Lord lord = p.GetLord();
            if (lord != null)
            {
                lord.Notify_PawnDamaged(p, notice);
            }

            bool wasDrafted = p.drafter != null && p.drafter.Drafted;
            int digest = Mathf.CeilToInt(Props.bodySizeDigestTimeCurve.Evaluate(p.BodySize) * 60f);

            p.DeSpawn();
            if (!innerContainer.TryAdd(p))
            {
                // Put it back rather than losing a pawn into nowhere.
                if (self.Map != null)
                {
                    GenSpawn.Spawn(p, self.Position, self.Map);
                }
                return;
            }

            heldIds.Add(p.thingIDNumber);
            heldTicks.Add(0);
            heldDigestTicks.Add(Mathf.Max(60, digest));
            heldWasDrafted.Add(wasDrafted);

            if (self.needs != null && self.needs.food != null)
            {
                self.needs.food.CurLevel = self.needs.food.MaxLevel;
            }

            if (p.Faction == Faction.OfPlayer)
            {
                Messages.Message(p.LabelShortCap + " was swallowed whole by the titanoslime. "
                                 + "Down it before it finishes.",
                                 self, MessageTypeDefOf.NegativeEvent, false);
            }
        }

        private int IndexOf(Thing t)
        {
            if (t == null)
            {
                return -1;
            }
            return heldIds.IndexOf(t.thingIDNumber);
        }

        private void ForgetAt(int idx)
        {
            if (idx < 0 || idx >= heldIds.Count)
            {
                return;
            }
            heldIds.RemoveAt(idx);
            if (idx < heldTicks.Count) heldTicks.RemoveAt(idx);
            if (idx < heldDigestTicks.Count) heldDigestTicks.RemoveAt(idx);
            if (idx < heldWasDrafted.Count) heldWasDrafted.RemoveAt(idx);
        }

        // ── the tick ────────────────────────────────────────────────────

        public override void CompTick()
        {
            base.CompTick();
            Pawn self = Pawn;
            if (self == null)
            {
                return;
            }

            try
            {
                TickRecordPoll(self);
                TickDecay(self);

                ticksUntilRound--;
                if (ticksUntilRound > 0)
                {
                    return;
                }
                ticksUntilRound = TickInterval;
                TickHeld(self);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.GelatinousSlime] titanoslime tick: " + e.Message, 0x51A13);
            }
        }

        // Ordinary eating. 🔑 NO INGESTION HOOK: the vanilla NutritionEaten
        // record is incremented by every ingestion path and is scribed, so
        // polling its delta catches grazing, corpse-eating and raw slime alike
        // without patching Toils_Ingest or JobDriver_Ingest.
        private void TickRecordPoll(Pawn self)
        {
            ticksUntilRecordPoll--;
            if (ticksUntilRecordPoll > 0)
            {
                return;
            }
            ticksUntilRecordPoll = RecordPollInterval;

            if (self.records == null || RecordDefOf.NutritionEaten == null)
            {
                return;
            }
            float now = self.records.GetValue(RecordDefOf.NutritionEaten);
            if (lastNutritionEaten < 0f)
            {
                lastNutritionEaten = now;
                return;
            }
            float delta = now - lastNutritionEaten;
            lastNutritionEaten = now;
            if (delta > 0f)
            {
                AddMass(delta * Props.massPerNutrition);
            }
        }

        // Starving and dry ground both take mass back. This is what makes the
        // ladder run in both directions — spec §11 answer 4, growth reversible.
        private void TickDecay(Pawn self)
        {
            ticksUntilDecay--;
            if (ticksUntilDecay > 0)
            {
                return;
            }
            ticksUntilDecay = DecayInterval;

            if (!self.Spawned || self.Dead)
            {
                return;
            }

            if (OnSlime(self))
            {
                ticksOffSlime = 0;
            }
            else
            {
                ticksOffSlime += DecayInterval;
            }

            float perInterval = (float)DecayInterval / 60000f;
            float loss = 0f;
            if (self.needs != null && self.needs.food != null
                && self.needs.food.CurCategory == HungerCategory.Starving)
            {
                loss += Props.massLostPerDayStarving * perInterval;
            }
            if (ticksOffSlime >= 60000)
            {
                loss += Props.massLostPerDayDry * perInterval;
            }
            if (loss > 0f)
            {
                AddMass(-loss);
            }
        }

        private bool OnSlime(Pawn self)
        {
            Map map = self.Map;
            if (map == null)
            {
                return true; // no map, no dry ground; never punish an unspawned slime
            }
            int r = Mathf.Max(0, Props.slimeTerrainSearchRadius);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(self.Position, r, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                TerrainDef t = c.GetTerrain(map);
                if (t == null)
                {
                    continue;
                }
                if (t.HasTag(SlimeDefs.SlimeTerrainTag))
                {
                    return true;
                }
                if (Props.extraSlimeTerrains != null && Props.extraSlimeTerrains.Contains(t))
                {
                    return true;
                }
            }
            return false;
        }

        // Struggle, burst-out and the digestion clock. Held things do not
        // tick (the container is not a map), so a swallowed colonist neither
        // starves nor bleeds out inside: the acid on exit is the whole cost.
        private void TickHeld(Pawn self)
        {
            if (innerContainer.Count == 0)
            {
                return;
            }

            List<Thing> snapshot = new List<Thing>(innerContainer.InnerListForReading);
            for (int i = 0; i < snapshot.Count; i++)
            {
                Pawn held = snapshot[i] as Pawn;
                if (held == null)
                {
                    continue;
                }
                int idx = IndexOf(held);
                if (idx < 0)
                {
                    // Came back from a save without its clock; give it one.
                    heldIds.Add(held.thingIDNumber);
                    heldTicks.Add(0);
                    heldDigestTicks.Add(Mathf.Max(60,
                        Mathf.CeilToInt(Props.bodySizeDigestTimeCurve.Evaluate(held.BodySize) * 60f)));
                    heldWasDrafted.Add(false);
                    idx = heldIds.Count - 1;
                }

                if (held.Dead)
                {
                    Absorb(held, idx);
                    continue;
                }

                heldTicks[idx] = heldTicks[idx] + TickInterval;

                if (!SlimeSettings.titanoslimeEngulfs)
                {
                    // The setting was turned off mid-hold: give everyone back.
                    Release(held, idx, self.MapHeld);
                    continue;
                }

                if (!held.Downed)
                {
                    Struggle(self, held);
                    if (self.Dead || self.Downed)
                    {
                        return; // Notify_Downed/Notify_Killed handles the rest
                    }
                    if (TryBurstOut(self, held, idx))
                    {
                        continue;
                    }
                }

                if (heldTicks[idx] >= heldDigestTicks[idx])
                {
                    Absorb(held, idx);
                }
            }
        }

        private void Struggle(Pawn self, Pawn held)
        {
            float amount;
            if (held.RaceProps != null && held.RaceProps.Humanlike)
            {
                int melee = 0;
                if (held.skills != null)
                {
                    melee = held.skills.GetSkill(SkillDefOf.Melee).Level;
                }
                amount = 2f + melee / 4f;
            }
            else
            {
                amount = 2f * held.BodySize;
            }
            BodyPartRecord core = self.RaceProps != null && self.RaceProps.body != null
                ? self.RaceProps.body.corePart
                : null;
            self.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount, 1f, -1f, held, core));
        }

        private bool TryBurstOut(Pawn self, Pawn held, int idx)
        {
            float chance = Mathf.Clamp((held.BodySize / Mathf.Max(0.01f, self.BodySize) - 0.15f) * 0.25f,
                                       0f, 0.10f);
            if (!Rand.Chance(chance))
            {
                return false;
            }
            Release(held, idx, self.MapHeld);
            return true;
        }

        // ── the two endings ─────────────────────────────────────────────

        /// <summary>Drops a held thing onto the map, the Devourer's own
        /// fallback chain. Returns the pawn, still alive, or null.</summary>
        private Pawn DropOut(Thing t, Map map)
        {
            if (t == null)
            {
                return null;
            }
            Pawn self = Pawn;
            IntVec3 pos = self != null ? self.PositionHeld : IntVec3.Invalid;
            if (map == null || !pos.IsValid)
            {
                return null;
            }
            Thing result;
            if (!innerContainer.TryDrop(t, pos, map, ThingPlaceMode.Near, out result))
            {
                IntVec3 fallback;
                Map m = map;
                if (!RCellFinder.TryFindRandomCellNearWith(pos, delegate(IntVec3 c) { return c.Standable(m); },
                                                           map, out fallback, 1))
                {
                    return null;
                }
                result = GenSpawn.Spawn(innerContainer.Take(t), fallback, map);
            }
            Corpse asCorpse = result as Corpse;
            if (asCorpse != null)
            {
                return asCorpse.InnerPawn;
            }
            return result as Pawn;
        }

        /// <summary>Alive out: stunned, acid-burned, slimified. Downed slime,
        /// dead slime, a burst-out, or the setting turned off.</summary>
        private void Release(Thing t, int idx, Map map)
        {
            Pawn self = Pawn;
            int seconds = (idx >= 0 && idx < heldTicks.Count) ? heldTicks[idx] / 60 : 0;
            bool wasDrafted = (idx >= 0 && idx < heldWasDrafted.Count) && heldWasDrafted[idx];
            Pawn freed = DropOut(t, map);
            ForgetAt(idx);
            if (freed == null)
            {
                return;
            }

            if (freed.stances != null && freed.stances.stunner != null)
            {
                freed.stances.stunner.StunFor(60, self, false, false);
            }
            if (freed.drafter != null)
            {
                freed.drafter.Drafted = wasDrafted;
            }

            if (!freed.Dead)
            {
                DamageInfo acid = new DamageInfo(DamageDefOf.AcidBurn,
                                                 Props.timeDamageCurve.Evaluate(seconds),
                                                 0f, -1f, self);
                acid.SetApplyAllDamage(true);
                freed.TakeDamage(acid);
            }

            // It was INSIDE the body. Stage 1 of the ladder no longer
            // self-reverses at 0.15, so the mod's own clock is now running on
            // anyone rescued — unless they are resistant by identity.
            if (!freed.Dead && !SlimeUtility.IsResistant(freed) && SlimeDefs.Slimification != null)
            {
                if (!freed.health.hediffSet.HasHediff(SlimeDefs.Slimification))
                {
                    freed.health.AddHediff(SlimeDefs.Slimification);
                }
                Hediff h = freed.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification);
                if (h != null)
                {
                    h.Severity = Mathf.Min(1f, h.Severity + 0.15f);
                }
            }

            if (freed.Faction == Faction.OfPlayer)
            {
                string msg = (self != null && self.Dead)
                    ? freed.LabelShortCap + " emerged from the titanoslime's remains."
                    : freed.LabelShortCap + " emerged from the titanoslime.";
                Messages.Message(msg, freed, MessageTypeDefOf.NeutralEvent, false);
            }
        }

        /// <summary>Finished reading: killed, gear regurgitated, no corpse,
        /// mass gained. Spec §4.4 and owner default 1 — digestion IS lethal.</summary>
        private void Absorb(Thing t, int idx)
        {
            Pawn self = Pawn;
            Map map = self != null ? self.MapHeld : null;
            IntVec3 pos = self != null ? self.PositionHeld : IntVec3.Invalid;
            float bodySize = 1f;
            Pawn held = t as Pawn;
            if (held != null)
            {
                bodySize = held.BodySize;
            }

            Pawn victim = DropOut(t, map);
            ForgetAt(idx);
            if (victim == null)
            {
                AddMass(bodySize);
                return;
            }

            bool wasPlayers = victim.Faction == Faction.OfPlayer;
            string name = victim.LabelShortCap;

            // The plasteel armour is not digestible; the reader is.
            if (victim.apparel != null)
            {
                victim.apparel.DropAll(victim.PositionHeld, false);
            }
            if (victim.equipment != null)
            {
                victim.equipment.DropAllEquipment(victim.PositionHeld, false);
            }

            if (!victim.Dead)
            {
                victim.Kill(new DamageInfo(DamageDefOf.AcidBurn, 9999f, 0f, -1f, self));
            }
            Corpse corpse = victim.Corpse;
            if (corpse != null && !corpse.Destroyed)
            {
                if (map == null)
                {
                    map = corpse.MapHeld;
                    pos = corpse.PositionHeld;
                }
                corpse.Destroy();
            }

            if (map != null && pos.IsValid && pos.InBounds(map) && SlimeDefs.SlimeSmear != null)
            {
                FilthMaker.TryMakeFilth(pos, map, SlimeDefs.SlimeSmear, 2);
            }

            AddMass(bodySize);
            if (self != null && self.needs != null && self.needs.food != null)
            {
                self.needs.food.CurLevel = self.needs.food.MaxLevel;
            }

            if (wasPlayers)
            {
                Find.LetterStack.ReceiveLetter(
                    "Absorbed",
                    name + " was absorbed by the titanoslime. There is nothing to bury.",
                    LetterDefOf.Death,
                    (map != null && pos.IsValid) ? new TargetInfo(pos, map) : TargetInfo.Invalid);
            }
        }

        public void ReleaseAll(Map map)
        {
            if (innerContainer == null || innerContainer.Count == 0)
            {
                return;
            }
            List<Thing> snapshot = new List<Thing>(innerContainer.InnerListForReading);
            for (int i = 0; i < snapshot.Count; i++)
            {
                Release(snapshot[i], IndexOf(snapshot[i]), map);
            }
        }

        public override void Notify_Downed()
        {
            base.Notify_Downed();
            Pawn self = Pawn;
            ReleaseAll(self != null ? self.MapHeld : null);
        }

        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);
            // 🔑 RUNS BEFORE THE TITANIC CORPSE-SITE CONVERSION. Notify_Killed
            // fires on the pawn's own death; the Titanic Creatures corpse-site
            // patch acts on the CORPSE afterwards, so everything held is on the
            // map before the corpse becomes a building.
            ReleaseAll(prevMap);
        }

        // ── shedding ────────────────────────────────────────────────────

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (!SlimeSettings.titanoslimeSheds || totalDamageDealt <= 0f)
            {
                return;
            }
            Pawn self = Pawn;
            if (self == null || !self.Spawned || self.Dead || self.Map == null)
            {
                return;
            }
            if (self.ageTracker == null || self.ageTracker.CurLifeStageIndex < 1)
            {
                return; // stage 1 has nothing spare to lose
            }

            float maxHp = self.health != null ? self.health.summaryHealth.SummaryHealthPercent : 1f;
            float hpPool = self.RaceProps != null ? self.RaceProps.baseHealthScale * 40f : 40f;
            damageSinceShed += totalDamageDealt;
            float perShed = Mathf.Max(1f, hpPool * Props.shedDamageFraction);
            if (damageSinceShed < perShed)
            {
                return;
            }
            damageSinceShed = 0f;

            // Don't spawn clutter on the drop: the fight is nearly won.
            if (innerContainer.Count > 0 && maxHp < 0.25f)
            {
                return;
            }

            ShedOne(self);
            AddMass(-Props.massPerShed);
        }

        private void ShedOne(Pawn self)
        {
            if (Props.shedPawnKind.NullOrEmpty())
            {
                return;
            }
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(Props.shedPawnKind);
            if (kind == null)
            {
                return; // a mod list without the gelatid simply sheds nothing
            }
            IntVec3 cell;
            Map map = self.Map;
            if (!CellFinder.TryFindRandomCellNear(self.Position, map, 2,
                    delegate(IntVec3 c) { return c.Standable(map); }, out cell))
            {
                return;
            }
            Pawn shed = PawnGenerator.GeneratePawn(kind, null);
            GenSpawn.Spawn(shed, cell, map, Rot4.Random);
            if (SlimeDefs.SlimeSmear != null)
            {
                FilthMaker.TryMakeFilth(cell, map, SlimeDefs.SlimeSmear, 1);
            }
        }

        // ── player surface ──────────────────────────────────────────────

        public override string CompInspectStringExtra()
        {
            Pawn self = Pawn;
            if (self == null || self.ageTracker == null)
            {
                return null;
            }
            StringBuilder sb = new StringBuilder();
            int stage = self.ageTracker.CurLifeStageIndex;
            int stages = Props.stageThresholds.Count + 1;
            string label = self.ageTracker.CurLifeStage != null
                ? self.ageTracker.CurLifeStage.label : "titanoslime";
            sb.Append("Stage " + (stage + 1) + " of " + stages + " — " + label);
            if (stage < MaxStageIndex && stage < Props.stageThresholds.Count)
            {
                sb.Append(" · mass " + absorbedMass.ToString("0.0")
                          + " / " + Props.stageThresholds[stage].ToString("0") + " to grow");
            }
            else
            {
                sb.Append(" · mass " + absorbedMass.ToString("0.0"));
            }

            List<Thing> contents = innerContainer.InnerListForReading;
            for (int i = 0; i < contents.Count; i++)
            {
                int idx = IndexOf(contents[i]);
                if (idx < 0)
                {
                    continue;
                }
                int left = Mathf.Max(0, heldDigestTicks[idx] - heldTicks[idx]) / 60;
                sb.AppendLine();
                sb.Append("Digesting " + contents[i].LabelShortCap + ": " + left + " s left");
            }
            if (Prefs.DevMode)
            {
                sb.AppendLine();
                sb.Append("(dev) absorbedMass " + absorbedMass.ToString("0.00")
                          + ", capacity " + Capacity + ", offSlime " + ticksOffSlime);
            }
            return sb.ToString();
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (!DebugSettings.ShowDevGizmos)
            {
                yield break;
            }
            yield return new Command_Action
            {
                defaultLabel = "DEV: +6 absorbed mass",
                action = delegate
                {
                    absorbedMass = Mathf.Clamp(absorbedMass + 6f, 0f, Props.massCap);
                    ApplyStage(true);
                }
            };
            yield return new Command_Action
            {
                defaultLabel = "DEV: -6 absorbed mass",
                action = delegate
                {
                    absorbedMass = Mathf.Clamp(absorbedMass - 6f, 0f, Props.massCap);
                    ApplyStage(false);
                }
            };
            yield return new Command_Action
            {
                defaultLabel = "DEV: release held",
                action = delegate { ReleaseAll(Pawn != null ? Pawn.MapHeld : null); }
            };
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // TitanoslimeSpawnTuning — the rarity slider, applied to the LOADED defs.
    //
    // 🔑 NO HARMONY AND NO PATCHOPERATION. BiomeDef.wildAnimals is a private
    // List<BiomeAnimalRecord> and its commonality lookup is memoised in a
    // private [Unsaved] dictionary (MEASURED, RimWorld/BiomeDef.cs), so the
    // slider edits the list by reflection and clears the memo. That is a
    // plain field write on a def this mod already ships a line in — it patches
    // no engine method and breaks nothing if the field is ever renamed,
    // because every step is guarded and a failure leaves the shipped
    // commonality standing.
    //
    // ⚠️ THE BASE COMMONALITY IS REMEMBERED ON FIRST TOUCH. Multiplying the
    // live value would compound every time the settings window closes.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class TitanoslimeSpawnTuning
    {
        private const string TitanoslimeKind = "RM_Titanoslime";

        private static readonly Dictionary<BiomeAnimalRecord, float> baseCommonality =
            new Dictionary<BiomeAnimalRecord, float>();

        private static FieldInfo wildAnimalsField;
        private static FieldInfo commonalityCacheField;
        private static bool reflectionFailed;

        static TitanoslimeSpawnTuning()
        {
            Apply();
        }

        public static void Apply()
        {
            if (reflectionFailed)
            {
                return;
            }
            try
            {
                if (wildAnimalsField == null)
                {
                    wildAnimalsField = typeof(BiomeDef).GetField(
                        "wildAnimals", BindingFlags.Instance | BindingFlags.NonPublic);
                    commonalityCacheField = typeof(BiomeDef).GetField(
                        "cachedAnimalCommonalities", BindingFlags.Instance | BindingFlags.NonPublic);
                }
                if (wildAnimalsField == null)
                {
                    reflectionFailed = true;
                    Log.WarningOnce("[RimMandrake.GelatinousSlime] BiomeDef.wildAnimals not found; "
                                    + "the titanoslime rarity slider is inert and the shipped "
                                    + "commonality stands.", 0x51A14);
                    return;
                }

                float factor = Mathf.Max(0f, SlimeSettings.titanoslimeSpawnFactor);
                List<BiomeDef> biomes = DefDatabase<BiomeDef>.AllDefsListForReading;
                for (int i = 0; i < biomes.Count; i++)
                {
                    List<BiomeAnimalRecord> records =
                        wildAnimalsField.GetValue(biomes[i]) as List<BiomeAnimalRecord>;
                    if (records == null)
                    {
                        continue;
                    }
                    bool touched = false;
                    for (int j = 0; j < records.Count; j++)
                    {
                        BiomeAnimalRecord rec = records[j];
                        if (rec == null || rec.animal == null || rec.animal.defName != TitanoslimeKind)
                        {
                            continue;
                        }
                        float baseValue;
                        if (!baseCommonality.TryGetValue(rec, out baseValue))
                        {
                            baseValue = rec.commonality;
                            baseCommonality[rec] = baseValue;
                        }
                        rec.commonality = baseValue * factor;
                        touched = true;
                    }
                    if (touched && commonalityCacheField != null)
                    {
                        commonalityCacheField.SetValue(biomes[i], null);
                    }
                }
            }
            catch (Exception e)
            {
                reflectionFailed = true;
                Log.WarningOnce("[RimMandrake.GelatinousSlime] titanoslime rarity slider could not "
                                + "be applied: " + e.Message, 0x51A15);
            }
        }
    }
}
