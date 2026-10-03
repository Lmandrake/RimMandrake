using System.Collections.Generic;
using System.Linq;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // SHRUBLAND_TREE_GUARDIAN_1 — the bark-wardens of a sweetline tree.
    //
    // Design: design/Jawa/worldbuilding/biomes/leaningscrub_sweetline_guardian_activation_2026-10-02.md
    // (shape A, "resident sleeper"), creature in sweetline_guardian_spec.md. Owner rulings
    // 2026-10-03 (question cards, LEANINGSCRUB_SWEETLINE_GUARDIAN_1 ledger notes):
    //   walk-up is NOT hostile (they watch you, visibly);
    //   harvesting wakes them GRADUALLY (stirring, restless, then the drop ~halfway);
    //   a disturbed tree forgives in ~5 days (a setting);
    //   wardens are visible, asleep against the trunk, "Roosting in the crown of <tree>".
    //
    // Pieces:
    //   RM_CompGuardianRoost   on the TREE. Spawns and refills its wardens, owns the
    //                          disturbance meter (0..1), its warning stages and the bar
    //                          gizmo, adds damage harm. Plants only TickLong, so all its
    //                          timekeeping rides CompTickLong.
    //   RM_CompRoostGuardian   on the WARDEN. Normal-ticks (it is a pawn), every 250 ticks:
    //                          watches for plant work at the trunk (the harvest is invisible
    //                          to damage hooks), raises the watching sign, keeps a sleeper
    //                          asleep, leashes a watchful one, re-homes once a day when its
    //                          tree is gone, and goes inert when tamed or switched off.
    //   RM_CompGuardianDormant vanilla CompCanBeDormant with our own inspect line.
    //   RM_Plant_Guarded       the tree's thingClass: the only harvest seam is
    //                          Plant.PlantCollected (non-destroying on this tree).
    // The rage itself is the kit's RM_MentalState_ScopedAggression (hostile to ONE pawn,
    // never a faction flip, ends when that pawn is 18 cells from the trunk).
    //
    // Assumptions recorded by the builder (no ruling either way): the mechanism lives in
    // this mod, not the kit, because its settings are this mod's "Named sweetline trees"
    // group (item criteria) and the tree comp is this mod's; refill is 30-60 days
    // (activation doc §6 "reconcile": against an 84-day wool regrow). No ThinkTree insert:
    // a sleeper that the animal think tree wakes is put back to sleep by the warden's own
    // 250-tick check (doc §2's fallback, done without a think-tree def).
    // ════════════════════════════════════════════════════════════════════

    public static class RM_SweetlineGuardianRules
    {
        public const float StirringAt = 0.3f;
        public const float RestlessAt = 0.6f;

        public static bool On =>
            RM_WindCalendar.On(RM_LeaningScrubSettings.sweetlineStationsEnabled)
            && RM_LeaningScrubSettings.sweetlineGuardiansEnabled;

        /// <summary>A pawn whose acts count as harm, or who can be watched: tool-users and up.</summary>
        public static bool IsPerson(Pawn p)
        {
            return p != null && p.RaceProps != null && p.RaceProps.intelligence >= Intelligence.ToolUser;
        }

        public static int StageOf(float meter)
        {
            if (meter >= 1f)
            {
                return 3;
            }
            if (meter >= RestlessAt)
            {
                return 2;
            }
            if (meter >= StirringAt)
            {
                return 1;
            }
            return 0;
        }

        public static string StageLabel(int stage)
        {
            switch (stage)
            {
                case 1: return "stirring";
                case 2: return "restless";
                case 3: return "awake";
                default: return "calm";
            }
        }
    }

    // ── the tree's thingClass ───────────────────────────────────────────
    public class RM_Plant_Guarded : Plant
    {
        public override void PlantCollected(Pawn by, PlantDestructionMode plantDestructionMode)
        {
            this.TryGetComp<RM_CompGuardianRoost>()?.Notify_Harvested(by);
            base.PlantCollected(by, plantDestructionMode);
        }
    }

    // ── the roost, on the tree ──────────────────────────────────────────
    public class RM_CompProperties_GuardianRoost : CompProperties
    {
        public PawnKindDef guardianKind;
        public IntRange count = new IntRange(2, 3);
        public FloatRange respawnDays = new FloatRange(30f, 60f);
        public float spawnRadius = 3f;
        public float disengageRadius = 18f;
        public int rageDurationTicks = 2500;
        public int rageCooldownTicks = 600;
        public MentalStateDef rageState;
        /// <summary>Meter gained per 250 ticks of plant work at the trunk (x the harvest setting).</summary>
        public float workDisturbance = 0.10f;
        /// <summary>Meter gained when a harvest completes (x the harvest setting).</summary>
        public float harvestDisturbance = 0.25f;
        /// <summary>Meter gained per point of violent damage.</summary>
        public float damageDisturbancePerPoint = 0.05f;
        /// <summary>Opt-in proximity setting only: meter per 250 ticks a person lingers within watchRadius.</summary>
        public float lingerDisturbance = 0.02f;
        public float watchRadius = 9f;
        public float rehomeRadius = 60f;

        public RM_CompProperties_GuardianRoost()
        {
            compClass = typeof(RM_CompGuardianRoost);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (guardianKind == null)
            {
                yield return "RM_CompProperties_GuardianRoost has no guardianKind.";
            }
            if (rageState == null)
            {
                yield return "RM_CompProperties_GuardianRoost has no rageState.";
            }
        }
    }

    public class RM_CompGuardianRoost : ThingComp
    {
        private List<Pawn> guardians = new List<Pawn>();
        private int targetCount = -1;
        private float disturbance;
        private int stage;
        private Pawn lastHarmer;
        private int nextRefillTick = -1;
        private int lastRageTick = -999999;
        private bool watchful;

        public RM_CompProperties_GuardianRoost Props => (RM_CompProperties_GuardianRoost)props;

        public float Disturbance => disturbance;

        public bool Watchful => watchful;

        public IReadOnlyList<Pawn> Guardians => guardians;

        private string TreeName =>
            parent.TryGetComp<RM_CompSweetlineStation>()?.TreeName ?? parent.LabelShort;

        public int Complement
        {
            get
            {
                if (targetCount < 0)
                {
                    targetCount = Props.count.RandomInRange;
                }
                return Mathf.Min(targetCount, Mathf.Max(0, RM_LeaningScrubSettings.sweetlineGuardianMaxPerTree));
            }
        }

        public bool HasVacancy => LiveCount() < Complement;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (respawningAfterLoad || !RM_SweetlineGuardianRules.On)
            {
                return;
            }
            int want = Complement;
            for (int i = LiveCount(); i < want; i++)
            {
                SpawnOne(false);
            }
            ScheduleRefill();
        }

        private void ScheduleRefill()
        {
            nextRefillTick = Find.TickManager.TicksGame + (int)(Props.respawnDays.RandomInRange * GenDate.TicksPerDay);
        }

        public int LiveCount()
        {
            Prune();
            return guardians.Count;
        }

        private void Prune()
        {
            for (int i = guardians.Count - 1; i >= 0; i--)
            {
                Pawn p = guardians[i];
                if (p == null || p.Dead || p.Destroyed || p.Faction != null
                    || p.MapHeld != parent.MapHeld
                    || p.TryGetComp<RM_CompRoostGuardian>()?.homeTree != parent)
                {
                    guardians.RemoveAt(i);
                }
            }
        }

        private void SpawnOne(bool remembered)
        {
            Map map = parent.Map;
            if (map == null || Props.guardianKind == null)
            {
                return;
            }
            if (!CellFinder.TryFindRandomCellNear(parent.Position, map, Mathf.Max(1, Mathf.CeilToInt(Props.spawnRadius)),
                    c => c.Standable(map) && !c.Fogged(map), out IntVec3 cell))
            {
                return;
            }
            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                Props.guardianKind,
                faction: null,
                context: PawnGenerationContext.NonPlayer,
                forceGenerateNewPawn: true,
                allowDowned: false,
                canGeneratePawnRelations: false,
                allowFood: false,
                allowAddictions: false,
                fixedBiologicalAge: Props.guardianKind.RaceProps.lifeStageAges.Last().minAge + Rand.Range(0.5f, 3f)));
            GenSpawn.Spawn(pawn, cell, map);
            Bind(pawn);
            if (!watchful)
            {
                pawn.TryGetComp<CompCanBeDormant>()?.ToSleep();
            }
            if (remembered)
            {
                parent.TryGetComp<RM_CompSweetlineStation>()?.Remember("a bark-warden has taken up the crown.");
            }
        }

        public void Bind(Pawn pawn)
        {
            RM_CompRoostGuardian g = pawn.TryGetComp<RM_CompRoostGuardian>();
            if (g == null)
            {
                return;
            }
            g.homeTree = parent;
            if (!guardians.Contains(pawn))
            {
                guardians.Add(pawn);
            }
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            if (!parent.Spawned)
            {
                return;
            }
            Prune();
            if (!RM_SweetlineGuardianRules.On)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;

            // Forgiveness: drain while nobody is raging. 2000 ticks per Long tick.
            if (!AnyRaging() && disturbance > 0f)
            {
                float perDay = 1f / Mathf.Max(0.5f, RM_LeaningScrubSettings.sweetlineForgivenessDays);
                disturbance = Mathf.Max(0f, disturbance - perDay * (2000f / GenDate.TicksPerDay));
                stage = Mathf.Min(stage, RM_SweetlineGuardianRules.StageOf(disturbance));
            }

            if (watchful && !AnyRaging() && disturbance < RM_SweetlineGuardianRules.StirringAt)
            {
                Reroost();
            }

            if (nextRefillTick < 0)
            {
                ScheduleRefill();
            }
            else if (now >= nextRefillTick)
            {
                ScheduleRefill();
                if (guardians.Count < Complement && !OtherRoostTooClose())
                {
                    SpawnOne(true);
                }
            }
        }

        // Spec §9.11: two roosts within the watch radius would double a visitor's trouble; the
        // later tree's slots stay empty.
        private bool OtherRoostTooClose()
        {
            foreach (Thing t in parent.Map.listerThings.ThingsOfDef(parent.def))
            {
                if (t != parent && t.Position.InHorDistOf(parent.Position, Props.watchRadius) && t.thingIDNumber < parent.thingIDNumber)
                {
                    return true;
                }
            }
            return false;
        }

        private bool AnyRaging()
        {
            foreach (Pawn p in guardians)
            {
                if (p != null && p.Spawned && p.MentalStateDef == Props.rageState)
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>The first live, spawned warden does the trunk-watching, so the meter fills once per check, not once per warden.</summary>
        public bool IsLead(Pawn pawn)
        {
            foreach (Pawn p in guardians)
            {
                if (p != null && p.Spawned && !p.Dead)
                {
                    return p == pawn;
                }
            }
            return false;
        }

        public void Notify_Harvested(Pawn by)
        {
            AddDisturbance(Props.harvestDisturbance * RM_LeaningScrubSettings.sweetlineHarvestDisturbance, by);
        }

        public void Notify_WorkTick(Pawn worker)
        {
            AddDisturbance(Props.workDisturbance * RM_LeaningScrubSettings.sweetlineHarvestDisturbance, worker);
        }

        public void Notify_Lingering(Pawn p)
        {
            AddDisturbance(Props.lingerDisturbance, p);
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (totalDamageDealt <= 0f || dinfo.Def == null || !dinfo.Def.ExternalViolenceFor(parent))
            {
                return;
            }
            Pawn by = dinfo.Instigator as Pawn;
            if (by != null && !RM_SweetlineGuardianRules.IsPerson(by))
            {
                return; // animals, including tamed ones, never count (activation doc §3)
            }
            AddDisturbance(totalDamageDealt * Props.damageDisturbancePerPoint, by);
        }

        public void AddDisturbance(float amount, Pawn by)
        {
            if (amount <= 0f || !parent.Spawned || !RM_SweetlineGuardianRules.On || LiveCount() == 0)
            {
                return;
            }
            if (by != null)
            {
                lastHarmer = by;
            }
            disturbance = Mathf.Min(1f, disturbance + amount);
            int newStage = RM_SweetlineGuardianRules.StageOf(disturbance);
            if (newStage > stage)
            {
                stage = newStage;
                Announce(newStage, by);
            }
            if (disturbance >= 1f)
            {
                TryDrop(by);
            }
        }

        private void Announce(int newStage, Pawn by)
        {
            string tree = TreeName;
            switch (newStage)
            {
                case 1:
                    Messages.Message("The bark-wardens of " + tree + " are stirring. Whoever is working the tree should stop.",
                        parent, MessageTypeDefOf.CautionInput, false);
                    break;
                case 2:
                    Messages.Message("The bark-wardens of " + tree + " are about to drop.",
                        parent, MessageTypeDefOf.ThreatSmall, false);
                    break;
            }
            FleckMaker.ThrowMetaIcon(parent.Position, parent.Map, FleckDefOf.IncapIcon);
        }

        private void TryDrop(Pawn target)
        {
            int now = Find.TickManager.TicksGame;
            if (now - lastRageTick < Props.rageCooldownTicks)
            {
                return;
            }
            lastRageTick = now;
            watchful = true;
            int dropped = 0;
            foreach (Pawn p in guardians.ToArray())
            {
                if (p == null || !p.Spawned || p.Dead || p.Downed)
                {
                    continue;
                }
                p.TryGetComp<CompCanBeDormant>()?.WakeUp();
                if (target == null || !target.Spawned || target.Dead || target.Map != parent.Map)
                {
                    continue; // fire with no instigator: they wake watchful and attack no one
                }
                if (p.MentalStateDef == Props.rageState)
                {
                    continue;
                }
                bool started = p.mindState.mentalStateHandler.TryStartMentalState(
                    Props.rageState,
                    target.LabelShortCap + " harmed " + TreeName + ".",
                    forced: true,
                    forceWake: true,
                    causedByMood: false,
                    otherPawn: target);
                if (started && p.MentalState is RM_MentalState_ScopedAggression state)
                {
                    state.anchorCell = parent.Position;
                    state.disengageRadius = Props.disengageRadius;
                    state.forceRecoverAfterTicks = Props.rageDurationTicks;
                    dropped++;
                }
            }
            RM_CompSweetlineStation station = parent.TryGetComp<RM_CompSweetlineStation>();
            if (dropped > 0)
            {
                Messages.Message("The bark-wardens of " + TreeName + " drop on " + target.LabelShort + ".",
                    new LookTargets(target), MessageTypeDefOf.ThreatBig, true);
                station?.Remember("its bark-wardens dropped on " + target.LabelShort + ".");
            }
            else
            {
                Messages.Message("The bark-wardens of " + TreeName + " are awake and watchful.",
                    parent, MessageTypeDefOf.ThreatSmall, false);
                station?.Remember("its bark-wardens woke, with no one to blame.");
            }
        }

        private void Reroost()
        {
            watchful = false;
            bool any = false;
            foreach (Pawn p in guardians)
            {
                if (p != null && p.Spawned && !p.Dead && !p.Downed && p.MentalState == null)
                {
                    p.TryGetComp<CompCanBeDormant>()?.ToSleep();
                    any = true;
                }
            }
            if (any)
            {
                Messages.Message("The bark-wardens of " + TreeName + " climb back into the crown.",
                    parent, MessageTypeDefOf.NeutralEvent, false);
                parent.TryGetComp<RM_CompSweetlineStation>()?.Remember("its bark-wardens settled again.");
            }
        }

        /// <summary>Settings switched off: every warden wakes and is an ordinary wild animal (never despawned).</summary>
        public void ReleaseAll(string why)
        {
            Prune();
            foreach (Pawn p in guardians.ToArray())
            {
                RM_CompRoostGuardian g = p.TryGetComp<RM_CompRoostGuardian>();
                if (g != null)
                {
                    g.homeTree = null;
                }
                p.TryGetComp<CompCanBeDormant>()?.WakeUp();
            }
            if (guardians.Count > 0 && why != null && parent.MapHeld != null)
            {
                Messages.Message(why, new LookTargets(guardians), MessageTypeDefOf.NeutralEvent, false);
            }
            guardians.Clear();
            watchful = false;
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            if (guardians.Count > 0 && previousMap != null)
            {
                ReleaseAll("The bark-wardens of " + TreeName + " have lost their tree.");
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_SweetlineGuardianRules.On)
            {
                return null;
            }
            int n = LiveCount();
            if (n == 0)
            {
                return "No bark-wardens roost here now.";
            }
            string state = watchful && disturbance < 1f ? "watchful" : RM_SweetlineGuardianRules.StageLabel(stage);
            return "Bark-wardens roost here (" + n + "). " + state.CapitalizeFirst() + ".";
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (RM_SweetlineGuardianRules.On && LiveCount() > 0)
            {
                yield return new RM_Gizmo_Disturbance(this);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref guardians, "rmRoostGuardians", LookMode.Reference);
            Scribe_Values.Look(ref targetCount, "rmRoostTarget", -1);
            Scribe_Values.Look(ref disturbance, "rmRoostDisturbance", 0f);
            Scribe_Values.Look(ref stage, "rmRoostStage", 0);
            Scribe_References.Look(ref lastHarmer, "rmRoostLastHarmer");
            Scribe_Values.Look(ref nextRefillTick, "rmRoostNextRefill", -1);
            Scribe_Values.Look(ref lastRageTick, "rmRoostLastRage", -999999);
            Scribe_Values.Look(ref watchful, "rmRoostWatchful", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (guardians == null)
                {
                    guardians = new List<Pawn>();
                }
                guardians.RemoveAll(p => p == null);
            }
        }
    }

    // ── the disturbance bar on the tree ─────────────────────────────────
    [StaticConstructorOnStartup]
    public class RM_Gizmo_Disturbance : Gizmo
    {
        private static readonly Texture2D FillTex = SolidColorMaterials.NewSolidColorTexture(new Color(0.75f, 0.35f, 0.2f));
        private static readonly Texture2D BgTex = SolidColorMaterials.NewSolidColorTexture(new Color(0.12f, 0.1f, 0.08f));
        private readonly RM_CompGuardianRoost roost;

        public RM_Gizmo_Disturbance(RM_CompGuardianRoost roost)
        {
            this.roost = roost;
            Order = -90f;
        }

        public override float GetWidth(float maxWidth)
        {
            return 160f;
        }

        public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
        {
            Rect rect = new Rect(topLeft.x, topLeft.y, GetWidth(maxWidth), Height);
            Widgets.DrawWindowBackground(rect);
            Rect inner = rect.ContractedBy(6f);
            Text.Font = GameFont.Tiny;
            Text.Anchor = TextAnchor.UpperLeft;
            Widgets.Label(new Rect(inner.x, inner.y, inner.width, 20f), "Bark-wardens");
            Rect bar = new Rect(inner.x, inner.y + 22f, inner.width, 18f);
            Widgets.FillableBar(bar, roost.Disturbance, FillTex, BgTex, true);
            foreach (float mark in new[] { RM_SweetlineGuardianRules.StirringAt, RM_SweetlineGuardianRules.RestlessAt })
            {
                float x = bar.x + bar.width * mark;
                Widgets.DrawLineVertical(x, bar.y, bar.height);
            }
            string state = roost.Watchful && roost.Disturbance < 1f
                ? "watchful"
                : RM_SweetlineGuardianRules.StageLabel(RM_SweetlineGuardianRules.StageOf(roost.Disturbance));
            Widgets.Label(new Rect(inner.x, inner.y + 44f, inner.width, 20f),
                "Disturbed " + (roost.Disturbance * 100f).ToString("0") + "% - " + state);
            Text.Font = GameFont.Small;
            TooltipHandler.TipRegion(rect,
                "How disturbed this tree's bark-wardens are. Working the tree (harvest or cut) and wounding it fill the bar; "
                + "at 30% they stir, at 60% they turn restless, and full they drop on whoever did it. "
                + "Walking past only makes them watch. The bar drains over a few days.");
            return new GizmoResult(GizmoState.Clear);
        }
    }

    // ── the warden's dormancy, with our own inspect line ────────────────
    public class RM_CompGuardianDormant : CompCanBeDormant
    {
        public override string CompInspectStringExtra()
        {
            return null; // RM_CompRoostGuardian writes the warden's whole state line
        }
    }

    // ── the warden ──────────────────────────────────────────────────────
    public class RM_CompProperties_RoostGuardian : CompProperties
    {
        public int checkInterval = 250;
        public float leashRadius = 6f;

        public RM_CompProperties_RoostGuardian()
        {
            compClass = typeof(RM_CompRoostGuardian);
        }
    }

    public class RM_CompRoostGuardian : ThingComp
    {
        public Thing homeTree;
        private int nextRehomeTick = -1;
        private Pawn watching;
        private int lastWatchTextTick = -999999;

        public RM_CompProperties_RoostGuardian Props => (RM_CompProperties_RoostGuardian)props;

        private Pawn Pawn => parent as Pawn;

        private RM_CompGuardianRoost Roost => homeTree?.TryGetComp<RM_CompGuardianRoost>();

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(Props.checkInterval))
            {
                return;
            }
            Pawn pawn = Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead)
            {
                return;
            }
            if (pawn.Faction != null || !RM_SweetlineGuardianRules.On)
            {
                // Tamed, or switched off: an ordinary animal. Wake a sleeper so it is never stuck.
                if (homeTree != null)
                {
                    homeTree = null;
                    pawn.TryGetComp<CompCanBeDormant>()?.WakeUp();
                }
                return;
            }
            if (homeTree == null || homeTree.Destroyed || !homeTree.Spawned || homeTree.Map != pawn.Map)
            {
                if (homeTree != null)
                {
                    homeTree = null;
                    pawn.TryGetComp<CompCanBeDormant>()?.WakeUp();
                }
                TryRehome(pawn);
                return;
            }
            RM_CompGuardianRoost roost = Roost;
            if (roost == null)
            {
                homeTree = null;
                return;
            }
            if (roost.IsLead(pawn))
            {
                WatchTheTrunk(pawn, roost);
            }
            if (pawn.MentalState != null || pawn.Downed)
            {
                return;
            }
            CompCanBeDormant dormant = pawn.TryGetComp<CompCanBeDormant>();
            if (!roost.Watchful)
            {
                // Keep a roosting warden roosting: the animal think tree may pick it up off its
                // sleep job (UNMEASURED for a lordless wild animal) — put it back.
                if (dormant != null && dormant.Awake)
                {
                    if (!pawn.Position.InHorDistOf(homeTree.Position, Props.leashRadius))
                    {
                        Leash(pawn);
                    }
                    else
                    {
                        dormant.ToSleep();
                    }
                }
            }
            else if (!pawn.Position.InHorDistOf(homeTree.Position, Props.leashRadius) && pawn.CurJobDef != JobDefOf.Goto)
            {
                Leash(pawn);
            }
        }

        private void Leash(Pawn pawn)
        {
            if (CellFinder.TryFindRandomCellNear(homeTree.Position, pawn.Map, 3, c => c.Standable(pawn.Map), out IntVec3 cell))
            {
                Job job = JobMaker.MakeJob(JobDefOf.Goto, cell);
                job.locomotionUrgency = LocomotionUrgency.Walk;
                pawn.jobs.StartJob(job, JobCondition.InterruptForced);
            }
        }

        // The lead warden watches for plant work at the trunk (the meter) and for people nearby
        // (the watching sign; the meter too, only under the opt-in proximity setting).
        private void WatchTheTrunk(Pawn self, RM_CompGuardianRoost roost)
        {
            Map map = self.Map;
            IntVec3 trunk = homeTree.Position;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(homeTree))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i] is Pawn worker && RM_SweetlineGuardianRules.IsPerson(worker)
                        && worker.jobs?.curDriver is JobDriver_PlantWork
                        && worker.CurJob != null && worker.CurJob.targetA.Thing == homeTree)
                    {
                        roost.Notify_WorkTick(worker);
                    }
                }
            }

            Pawn nearest = null;
            float best = float.MaxValue;
            float r = roost.Props.watchRadius;
            IReadOnlyList<Pawn> all = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn p = all[i];
                if (!RM_SweetlineGuardianRules.IsPerson(p) || p.Dead || p.Downed)
                {
                    continue;
                }
                float d = (p.Position - trunk).LengthHorizontalSquared;
                if (d <= r * r && d < best)
                {
                    best = d;
                    nearest = p;
                }
            }
            watching = nearest;
            if (nearest == null)
            {
                return;
            }
            if (RM_LeaningScrubSettings.sweetlineProximityCharge)
            {
                roost.Notify_Lingering(nearest);
            }
            int now = Find.TickManager.TicksGame;
            if (now - lastWatchTextTick > 1250)
            {
                lastWatchTextTick = now;
                MoteMaker.ThrowText(self.DrawPos + new Vector3(0f, 0f, 0.6f), map, "watching", new Color(0.85f, 0.8f, 0.65f), 2.5f);
            }
        }

        private void TryRehome(Pawn pawn)
        {
            int now = Find.TickManager.TicksGame;
            if (now < nextRehomeTick)
            {
                return;
            }
            nextRehomeTick = now + GenDate.TicksPerDay;
            RM_CompGuardianRoost bestRoost = null;
            float best = float.MaxValue;
            foreach (Thing t in pawn.Map.listerThings.AllThings)
            {
                RM_CompGuardianRoost r = t is Plant ? t.TryGetComp<RM_CompGuardianRoost>() : null;
                if (r == null || r.Props.guardianKind?.race != pawn.def || !r.HasVacancy)
                {
                    continue;
                }
                float d = (t.Position - pawn.Position).LengthHorizontalSquared;
                if (d <= r.Props.rehomeRadius * r.Props.rehomeRadius && d < best)
                {
                    best = d;
                    bestRoost = r;
                }
            }
            if (bestRoost != null)
            {
                bestRoost.Bind(pawn);
            }
        }

        public override string CompInspectStringExtra()
        {
            Pawn pawn = Pawn;
            if (pawn == null || homeTree == null || !RM_SweetlineGuardianRules.On)
            {
                return null;
            }
            string tree = homeTree.TryGetComp<RM_CompSweetlineStation>()?.TreeName ?? homeTree.LabelShort;
            CompCanBeDormant dormant = pawn.TryGetComp<CompCanBeDormant>();
            if (dormant != null && !dormant.Awake)
            {
                return "Roosting in the crown of " + tree + "."
                    + (watching != null && watching.Spawned ? " Watching " + watching.LabelShort + "." : "");
            }
            if (pawn.MentalState != null)
            {
                return "Defending " + tree + ".";
            }
            return "Watchful, near " + tree + ".";
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref homeTree, "rmHomeTree");
            Scribe_Values.Look(ref nextRehomeTick, "rmNextRehome", -1);
        }
    }
}
