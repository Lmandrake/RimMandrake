using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LanternDeeps
{
    // ════════════════════════════════════════════════════════════════════
    // LANTERNDEEPS_HYDROCARBON_WAVE3_BUILD_1 (split from LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1): hush, sipper,
    // tapper, pooler. Concepts: design/Jawa/worldbuilding/biomes/rosters/lantern_deeps_repopulation_proposals.md
    // §1, §4, §6, §7 (owner: all twelve admitted, every one hydrocarbon).
    //
    //  RM_CompHush            the hush is unseen on an unlit cell: it carries vanilla HediffComp_Invisibility
    //                         (RM_HushUnseen, the Revenant machinery: undrawn AND untargetable) and is made visible
    //                         when the ground under it is lit (GroundGlowAt >= litThreshold), when hurt (vanilla
    //                         disruption), or when it strikes. From unlit natural ground it lunges at anything that
    //                         walks within lungeRange (vanilla AttackMelee). No Harmony: the proposal's "Harmony on
    //                         draw + targeting" is exactly what HediffComp_Invisibility already does, and every DLC
    //                         is assumed present. Placed 1-2 per new Deep by RM_GenStep_Hush, never rostered.
    //  RM_CompSipper +        sippers hop toward the brightest lit glower within reach; RM_MapComponent_Sippers
    //  RM_MapComponent_       counts the sippers within 1.5 cells of every lit glower each pass and shrinks that
    //  Sippers                glower by cellsPerSipper per sipper (floor 25%), restoring it as they leave. It reads
    //                         the radius someone else set (the aurora's x1.75) as the new base, so the two never
    //                         fight. Breeding + cap: RM_CompVerminBreeder + RM_VerminPressureExtension (XML).
    //  RM_CompTapper          wild: seeks the nearest charged CompPowerBattery and drains it (DrawPower) while
    //                         beside it. Tame: never drains; charges itself while RM_DeepAurora is active and pours
    //                         that charge into any battery beside it (AddEnergy).
    //  RM_CompPooler          seeks the warmest thing: a loose fire, else the hottest working heater, else a
    //                         warm-blooded pawn. Beside a fire: Fire.Destroy. Beside a fuelled heater: the fuel is
    //                         spent at once (it goes out flat); beside a powered heater: CompHeatPusher.enabled is held
    //                         false while it stays (restored when it leaves or dies). Beside a warm pawn:
    //                         Hypothermia climbs fast. A tame pooler only hunts fires (the fire brigade). Fire never
    //                         hurts it (Flame/Burn absorbed, attached fire put out). Hurt, it lets go for a while.
    // ════════════════════════════════════════════════════════════════════

    internal static class Wave3Util
    {
        public static bool IsHydrocarbon(ThingDef d)
        {
            return d?.modExtensions != null && d.modExtensions.Any(e => e != null && e.GetType().Name == "RM_HydrocarbonBloodExtension");
        }

        // A standable cell at or beside c, for walking up to a building or a fire.
        public static IntVec3 Approach(Map map, IntVec3 c, IntVec3 from)
        {
            if (c.Standable(map)) return c;
            IntVec3 best = IntVec3.Invalid;
            float bestD = float.MaxValue;
            foreach (IntVec3 a in GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)))
            {
                if (!a.InBounds(map) || !a.Standable(map)) continue;
                float d = a.DistanceToSquared(from);
                if (d < bestD) { bestD = d; best = a; }
            }
            return best;
        }

        public static void GoTo(Pawn pawn, IntVec3 cell)
        {
            if (!cell.IsValid || pawn.Position == cell) return;
            if (pawn.CurJobDef == JobDefOf.Goto && pawn.CurJob.targetA.Cell == cell) return;
            if (!pawn.CanReach(cell, PathEndMode.OnCell, Danger.Deadly)) return;
            Job job = JobMaker.MakeJob(JobDefOf.Goto, cell);
            job.expiryInterval = 1200;
            pawn.jobs.StartJob(job, JobCondition.InterruptOptional, resumeCurJobAfterwards: false);
        }

        public static bool Busy(Pawn pawn)
        {
            return pawn.Downed || pawn.Dead || !pawn.Awake() || pawn.InMentalState || pawn.CurJobDef == JobDefOf.AttackMelee
                || pawn.CurJobDef == JobDefOf.PredatorHunt || pawn.CurJobDef == JobDefOf.Ingest;
        }
    }

    // ── Hush ─────────────────────────────────────────────────────────────

    public class RM_CompProperties_Hush : CompProperties
    {
        public HediffDef unseenHediff;
        public float litThreshold = 0.3f;
        public float lungeRange = 2f;
        public int checkInterval = 30;
        public int lungeCooldownTicks = 900;

        public RM_CompProperties_Hush() { compClass = typeof(RM_CompHush); }
    }

    public class RM_CompHush : ThingComp
    {
        private int lastLungeTick = -999999;
        private RM_CompProperties_Hush Props => (RM_CompProperties_Hush)props;
        private Pawn Pawn => parent as Pawn;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastLungeTick, "lastLungeTick", -999999);
        }

        public override void CompTick()
        {
            Pawn p = Pawn;
            if (p == null || !p.Spawned || p.Dead || !p.IsHashIntervalTick(Props.checkInterval)) return;
            Evaluate(p);
        }

        public bool Lit(Pawn p)
        {
            return p.Map.glowGrid.GroundGlowAt(p.Position) >= Props.litThreshold;
        }

        // Natural ground (no built floor) counts as the fungal floor of the Deep.
        public static bool NaturalGround(Map map, IntVec3 c)
        {
            TerrainDef t = c.GetTerrain(map);
            return t != null && !t.layerable && !t.BuildableByPlayer;
        }

        /// <summary>One look: returns "hidden", "visible" or "lunge".</summary>
        public string Evaluate(Pawn p)
        {
            if (!LanternDeepsSettings.hushHidingEnabled || p.Downed || p.Faction == Faction.OfPlayer)
            {
                SetHidden(p, false);
                return "visible";
            }
            bool dark = !Lit(p);
            if (dark && NaturalGround(p.Map, p.Position) && Find.TickManager.TicksGame - lastLungeTick >= Props.lungeCooldownTicks)
            {
                Pawn prey = FindPrey(p);
                if (prey != null)
                {
                    SetHidden(p, false);
                    lastLungeTick = Find.TickManager.TicksGame;
                    Job job = JobMaker.MakeJob(JobDefOf.AttackMelee, prey);
                    job.locomotionUrgency = LocomotionUrgency.Sprint;
                    job.expiryInterval = 600;
                    job.killIncappedTarget = false;
                    p.jobs.StartJob(job, JobCondition.InterruptForced, resumeCurJobAfterwards: false, cancelBusyStances: true);
                    return "lunge";
                }
            }
            bool striking = p.CurJobDef == JobDefOf.AttackMelee;
            SetHidden(p, dark && !striking);
            return dark && !striking ? "hidden" : "visible";
        }

        private Pawn FindPrey(Pawn p)
        {
            IReadOnlyList<Pawn> all = p.Map.mapPawns.AllPawnsSpawned;
            Pawn best = null;
            float bestSq = Props.lungeRange * Props.lungeRange + 0.01f;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn c = all[i];
                if (c == p || c.Dead || c.Downed || c.def == p.def || c.RaceProps.IsMechanoid || !c.RaceProps.IsFlesh) continue;
                float d = (c.Position - p.Position).LengthHorizontalSquared;
                if (d <= bestSq) { bestSq = d; best = c; }
            }
            return best;
        }

        public void SetHidden(Pawn p, bool hidden)
        {
            if (Props.unseenHediff == null) return;
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(Props.unseenHediff);
            if (hidden && h == null)
            {
                p.health.AddHediff(Props.unseenHediff);   // HediffComp_Invisibility.CompPostPostAdd -> BecomeInvisible(instant)
            }
            else if (!hidden && h != null)
            {
                p.GetInvisibilityComp()?.BecomeVisible(instant: true);
                p.health.RemoveHediff(h);
            }
        }

        public bool Hidden => Pawn != null && Props.unseenHediff != null && Pawn.health.hediffSet.HasHediff(Props.unseenHediff);
    }

    public class RM_GenStep_Hush : GenStep
    {
        public PawnKindDef kind;
        public IntRange count = new IntRange(1, 2);

        public override int SeedPart => 518236011;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (LanternDeepsSettings.hushHidingEnabled) Place(map, kind, count.RandomInRange);
        }

        // Unlit natural ground, away from the edge; prefer cells with a plant on them (the fungal floor).
        public static string Place(Map map, PawnKindDef kind, int n)
        {
            if (kind == null) return "no kind";
            int placed = 0;
            for (int k = 0; k < n; k++)
            {
                IntVec3 best = IntVec3.Invalid;
                for (int i = 0; i < 400; i++)
                {
                    IntVec3 c = CellFinder.RandomCell(map);
                    if (!c.Standable(map) || c.DistanceToEdge(map) < 6 || !RM_CompHush.NaturalGround(map, c)) continue;
                    if (map.glowGrid.GroundGlowAt(c) >= 0.3f) continue;
                    best = c;
                    if (c.GetPlant(map) != null) break;
                }
                if (!best.IsValid) continue;
                GenSpawn.Spawn(PawnGenerator.GeneratePawn(kind), best, map);
                placed++;
            }
            return "placed hush " + placed + "/" + n;
        }
    }

    // ── Sipper ───────────────────────────────────────────────────────────

    public class RM_CompProperties_Sipper : CompProperties
    {
        public float seekRadius = 30f;
        public int checkInterval = 250;

        public RM_CompProperties_Sipper() { compClass = typeof(RM_CompSipper); }
    }

    public class RM_CompSipper : ThingComp
    {
        private RM_CompProperties_Sipper Props => (RM_CompProperties_Sipper)props;

        public override void CompTick()
        {
            Pawn p = parent as Pawn;
            if (p == null || !p.Spawned || !p.IsHashIntervalTick(Props.checkInterval)) return;
            if (!LanternDeepsSettings.sipperDrinkingEnabled || p.Faction != null || Wave3Util.Busy(p)) return;
            CompGlower g = RM_MapComponent_Sippers.BrightestNear(p.Map, p.Position, Props.seekRadius);
            if (g == null) return;
            if (p.Position.InHorDistOf(g.parent.Position, 1.5f)) return;   // arrived: sit still
            Wave3Util.GoTo(p, Wave3Util.Approach(p.Map, g.parent.Position, p.Position));
        }
    }

    public class RM_MapComponent_Sippers : MapComponent
    {
        public const string SipperDef = "RM_Sipper";
        private const int Interval = 300;
        private static readonly FieldInfo LitGlowersField = typeof(GlowGrid).GetField("litGlowers", BindingFlags.Instance | BindingFlags.NonPublic);

        // The radius ledger (what we wrote, how much we took, when to give it back) lives in RM_SipperLedgerKernel.cs.
        private readonly SipperLedger<CompGlower> ledger = new SipperLedger<CompGlower>();
        private ThingDef sipperDef;

        public RM_MapComponent_Sippers(Map map) : base(map) { }

        public int DrunkCount => ledger.DrunkCount;

        public static IEnumerable<CompGlower> LitGlowers(Map map)
        {
            var set = LitGlowersField?.GetValue(map.glowGrid) as HashSet<CompGlower>;
            if (set == null) return Enumerable.Empty<CompGlower>();
            return set.Where(g => g?.parent != null && g.parent.Spawned && g.parent.Map == map && !(g.parent is Pawn)).ToList();
        }

        public static CompGlower BrightestNear(Map map, IntVec3 from, float radius)
        {
            CompGlower best = null;
            float bestR = 0f;
            float r2 = radius * radius;
            foreach (CompGlower g in LitGlowers(map))
            {
                if ((g.parent.Position - from).LengthHorizontalSquared > r2) continue;
                if (g.GlowRadius > bestR) { bestR = g.GlowRadius; best = g; }
            }
            return best;
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % Interval == 0) Pass();
        }

        public int Pass()
        {
            if (sipperDef == null) sipperDef = DefDatabase<ThingDef>.GetNamedSilentFail(SipperDef);
            List<Thing> sippers = sipperDef == null ? new List<Thing>() : map.listerThings.ThingsOfDef(sipperDef);
            var counts = new Dictionary<CompGlower, int>();
            if (LanternDeepsSettings.sipperDrinkingEnabled && sippers.Count > 0)
            {
                foreach (CompGlower g in LitGlowers(map))
                {
                    int n = 0;
                    IntVec3 at = g.parent.Position;
                    for (int i = 0; i < sippers.Count; i++)
                    {
                        if (sippers[i] is Pawn s && !s.Dead && s.Faction == null && s.Position.InHorDistOf(at, 1.5f)) n++;
                    }
                    if (n > 0) counts[g] = n;
                }
            }
            return ledger.Pass(counts, LanternDeepsSettings.sipperCellsPerSipper,
                g => g.GlowRadius, (g, r) => g.GlowRadius = r,
                g => g.parent != null && g.parent.Spawned, g => g.Glows, g => g.ForceRegister(map));
        }
    }

    // ── Tapper ───────────────────────────────────────────────────────────

    public class RM_CompProperties_Tapper : CompProperties
    {
        public float seekRadius = 40f;
        public float drainPerDay = 600f;       // Wd per wild tapper beside a battery
        public float chargePerDay = 1200f;     // Wd a tame tapper takes in while the aurora storms
        public float capacity = 300f;          // Wd a tame tapper can hold
        public GameConditionDef aurora;
        public int checkInterval = 250;

        public RM_CompProperties_Tapper() { compClass = typeof(RM_CompTapper); }
    }

    public class RM_CompTapper : ThingComp
    {
        public float charge;
        private RM_CompProperties_Tapper Props => (RM_CompProperties_Tapper)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref charge, "charge", 0f);
        }

        public override string CompInspectStringExtra()
        {
            Pawn p = parent as Pawn;
            if (p == null || p.Faction != Faction.OfPlayer) return null;
            return "Stored charge: " + charge.ToString("0") + " / " + Props.capacity.ToString("0") + " Wd";
        }

        public override void CompTick()
        {
            Pawn p = parent as Pawn;
            if (p == null || !p.Spawned || p.Dead || !p.IsHashIntervalTick(Props.checkInterval)) return;
            if (!LanternDeepsSettings.tapperEnabled) return;
            Tick(p, Props.checkInterval);
        }

        public static IEnumerable<CompPowerBattery> Batteries(Map map)
        {
            List<Building> b = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < b.Count; i++)
            {
                CompPowerBattery bat = b[i].TryGetComp<CompPowerBattery>();
                if (bat != null) yield return bat;
            }
        }

        private static CompPowerBattery Beside(Pawn p)
        {
            foreach (CompPowerBattery bat in Batteries(p.Map))
            {
                if (bat.parent.OccupiedRect().ExpandedBy(1).Contains(p.Position)) return bat;
            }
            return null;
        }

        /// <summary>One pass over `ticks`: returns what happened, for the proof.</summary>
        public string Tick(Pawn p, int ticks)
        {
            Map map = p.Map;
            if (p.Faction == Faction.OfPlayer)
            {
                if (Props.aurora != null && map.gameConditionManager.ConditionIsActive(Props.aurora))
                    charge = Mathf.Min(Props.capacity, charge + Props.chargePerDay * ticks / 60000f);
                CompPowerBattery bat = Beside(p);
                if (bat != null && charge > 0f)
                {
                    float give = Mathf.Min(charge, bat.AmountCanAccept);
                    if (give > 0f) { bat.AddEnergy(give); charge -= give; return "gave " + give.ToString("0.0"); }
                }
                return "tame charge=" + charge.ToString("0.0");
            }
            if (p.Faction != null || Wave3Util.Busy(p)) return "busy";
            CompPowerBattery here = Beside(p);
            if (here != null && here.StoredEnergy > 0f)
            {
                float take = Mathf.Min(here.StoredEnergy, Props.drainPerDay * ticks / 60000f);
                here.DrawPower(take);
                return "drained " + take.ToString("0.00");
            }
            CompPowerBattery target = null;
            float best = Props.seekRadius * Props.seekRadius;
            foreach (CompPowerBattery bat in Batteries(map))
            {
                if (bat.StoredEnergy <= 1f) continue;
                float d = (bat.parent.Position - p.Position).LengthHorizontalSquared;
                if (d < best) { best = d; target = bat; }
            }
            if (target == null) return "nothing to drink";
            Wave3Util.GoTo(p, Wave3Util.Approach(map, target.parent.Position, p.Position));
            return "seeking " + target.parent.LabelShort;
        }
    }

    // ── Pooler ───────────────────────────────────────────────────────────

    public class RM_CompProperties_Pooler : CompProperties
    {
        public float seekRadius = 40f;
        public float pawnSeekRadius = 14f;
        public float hypothermiaPerCheck = 0.03f;
        public int letGoTicks = 2500;
        public int checkInterval = 250;

        public RM_CompProperties_Pooler() { compClass = typeof(RM_CompPooler); }
    }

    public class RM_CompPooler : ThingComp
    {
        private Thing smothered;              // a powered heater held off while it sits there
        private int letGoUntil = -1;
        private RM_CompProperties_Pooler Props => (RM_CompProperties_Pooler)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref smothered, "smothered");
            Scribe_Values.Look(ref letGoUntil, "letGoUntil", -1);
        }

        public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            absorbed = dinfo.Def == DamageDefOf.Flame || dinfo.Def == DamageDefOf.Burn;
            if (!absorbed && dinfo.Amount > 0f)
            {
                letGoUntil = Find.TickManager.TicksGame + Props.letGoTicks;   // pushed off
                Release();
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            Release();
        }

        private void Release()
        {
            if (smothered != null)
            {
                CompHeatPusher h = smothered.TryGetComp<CompHeatPusher>();
                if (h != null) h.enabled = true;
                smothered = null;
            }
        }

        public override void CompTick()
        {
            Pawn p = parent as Pawn;
            if (p == null || !p.Spawned || p.Dead) return;
            if (p.IsHashIntervalTick(60) && p.IsBurning())
            {
                p.GetAttachment(ThingDefOf.Fire)?.Destroy();
            }
            if (!p.IsHashIntervalTick(Props.checkInterval)) return;
            if (!LanternDeepsSettings.poolerSmotherEnabled) { Release(); return; }
            Tick(p);
        }

        private static bool WarmBlooded(Pawn c, Pawn self)
        {
            return c != self && !c.Dead && c.RaceProps.IsFlesh && !Wave3Util.IsHydrocarbon(c.def);
        }

        public string Tick(Pawn p)
        {
            Map map = p.Map;
            bool tame = p.Faction == Faction.OfPlayer;
            if (smothered != null && (!smothered.Spawned || !p.Position.InHorDistOf(smothered.Position, 1.9f))) Release();
            if (Find.TickManager.TicksGame < letGoUntil || Wave3Util.Busy(p)) return "resting";

            // 1. loose fires (a tame one only ever hunts these)
            Fire fire = null;
            float best = Props.seekRadius * Props.seekRadius;
            List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < fires.Count; i++)
            {
                if (!(fires[i] is Fire f) || f.parent != null) continue;
                float d = (f.Position - p.Position).LengthHorizontalSquared;
                if (d < best) { best = d; fire = f; }
            }
            if (fire != null)
            {
                if (p.Position.InHorDistOf(fire.Position, 1.5f)) { fire.Destroy(); return "put out a fire"; }
                Wave3Util.GoTo(p, Wave3Util.Approach(map, fire.Position, p.Position));
                return "seeking fire";
            }
            if (tame) return "no fire";

            // 2. the hottest working heater
            Building heater = null;
            float hottest = 0f;
            List<Building> bld = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < bld.Count; i++)
            {
                CompHeatPusher h = bld[i].TryGetComp<CompHeatPusher>();
                if (h == null || h.Props.heatPerSecond <= 0f) continue;
                bool held = bld[i] == smothered;
                if (!held && !h.ShouldPushHeatNow) continue;
                if (!bld[i].Position.InHorDistOf(p.Position, Props.seekRadius)) continue;
                float score = h.Props.heatPerSecond - bld[i].Position.DistanceTo(p.Position) * 0.01f;
                if (score > hottest) { hottest = score; heater = bld[i]; }
            }
            if (heater != null)
            {
                if (p.Position.InHorDistOf(heater.Position, 1.9f))
                {
                    CompRefuelable fuel = heater.TryGetComp<CompRefuelable>();
                    if (fuel != null && fuel.HasFuel)
                    {
                        fuel.ConsumeFuel(fuel.Fuel);
                        return "drowned " + heater.LabelShort;
                    }
                    CompHeatPusher h = heater.TryGetComp<CompHeatPusher>();
                    if (smothered != heater) { Release(); smothered = heater; }
                    if (h != null) h.enabled = false;
                    return "smothering " + heater.LabelShort;
                }
                Wave3Util.GoTo(p, Wave3Util.Approach(map, heater.Position, p.Position));
                return "seeking " + heater.LabelShort;
            }

            // 3. a warm-blooded pawn
            Pawn warm = null;
            float bestP = Props.pawnSeekRadius * Props.pawnSeekRadius;
            IReadOnlyList<Pawn> all = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                if (!WarmBlooded(all[i], p)) continue;
                float d = (all[i].Position - p.Position).LengthHorizontalSquared;
                if (d < bestP) { bestP = d; warm = all[i]; }
            }
            if (warm == null) return "nothing warm";
            if (p.Position.InHorDistOf(warm.Position, 1.5f))
            {
                HealthUtility.AdjustSeverity(warm, HediffDefOf.Hypothermia, Props.hypothermiaPerCheck);
                return "chilling " + warm.LabelShort;
            }
            Wave3Util.GoTo(p, warm.Position);
            return "seeking " + warm.LabelShort;
        }
    }

    // ── jawa/static_call proofs (validation.py, hydrocarbon_wave3) ───────────

    public static class RM_HydrocarbonWave3Proof
    {
        private static Pawn SpawnAt(string kind, IntVec3 c, Map map, Faction f = null)
        {
            PawnKindDef k = DefDatabase<PawnKindDef>.GetNamedSilentFail(kind);
            if (k == null) return null;
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(k, f));
            GenSpawn.Spawn(p, c, map);
            return p;
        }

        private static IntVec3 OpenCell(Map map, System.Func<IntVec3, bool> extra = null)
        {
            CellFinder.TryFindRandomCellNear(map.Center, map, 30, c => c.Standable(map) && c.GetFirstPawn(map) == null && (extra == null || extra(c)), out IntVec3 cell);
            return cell;
        }

        // Spawns a hush on an unlit cell, reports hidden-or-not, then a pawn beside it and reports lunge.
        public static string ProofHush(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "no map";
            IntVec3 c = OpenCell(map, x => map.glowGrid.GroundGlowAt(x) < 0.3f && RM_CompHush.NaturalGround(map, x));
            if (!c.IsValid) return "no unlit natural cell";
            Pawn h = SpawnAt("RM_Hush", c, map);
            var comp = h?.TryGetComp<RM_CompHush>();
            if (comp == null) return "no hush";
            string first = comp.Evaluate(h);
            bool hidden = comp.Hidden;
            IntVec3 near = GenAdj.CellsAdjacent8Way(h).FirstOrDefault(x => x.InBounds(map) && x.Standable(map));
            Pawn prey = near.IsValid ? SpawnAt("Muffalo", near, map) : null;
            string second = prey == null ? "no prey cell" : comp.Evaluate(h);
            return "first=" + first + " hidden=" + hidden + " second=" + second + " job=" + h.CurJobDef?.defName;
        }

        // Spawns 10 sippers on a lit glower's cell, runs one drain pass, reports the radius before/after.
        public static string ProofSipper(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "no map";
            CompGlower g = RM_MapComponent_Sippers.LitGlowers(map).OrderByDescending(x => x.GlowRadius).FirstOrDefault();
            if (g == null) return "no lit glower";
            float before = g.GlowRadius;
            for (int i = 0; i < 10; i++)
            {
                if (CellFinder.TryFindRandomCellNear(g.parent.Position, map, 1, x => x.Standable(map), out IntVec3 c)) SpawnAt("RM_Sipper", c, map);
            }
            int changed = map.GetComponent<RM_MapComponent_Sippers>()?.Pass() ?? -1;
            return "glower=" + g.parent.LabelShort + " before=" + before.ToString("0.00") + " after=" + g.GlowRadius.ToString("0.00") + " changed=" + changed;
        }

        // Spawns a wild tapper beside the first colony battery and runs a day's worth of one pass.
        public static string ProofTapper(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "no map";
            CompPowerBattery bat = RM_CompTapper.Batteries(map).FirstOrDefault();
            if (bat == null) return "no colony battery";
            IntVec3 c = Wave3Util.Approach(map, bat.parent.Position, bat.parent.Position + IntVec3.South * 2);
            Pawn t = SpawnAt("RM_Tapper", c, map);
            var comp = t?.TryGetComp<RM_CompTapper>();
            if (comp == null) return "no tapper";
            float before = bat.StoredEnergy;
            string r = comp.Tick(t, 60000);
            return "result=" + r + " before=" + before.ToString("0.0") + " after=" + bat.StoredEnergy.ToString("0.0");
        }

        // Starts a fire, spawns a pooler beside it, runs one pass; reports whether the fire is gone and the pooler unburnt.
        public static string ProofPooler(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "no map";
            IntVec3 c = OpenCell(map);
            if (!c.IsValid) return "no cell";
            FireUtility.TryStartFireIn(c, map, 0.5f, null);
            Fire f = c.GetFirstThing<Fire>(map);
            IntVec3 near = GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)).FirstOrDefault(x => x.InBounds(map) && x.Standable(map));
            Pawn p = SpawnAt("RM_Pooler", near, map);
            var comp = p?.TryGetComp<RM_CompPooler>();
            if (comp == null) return "no pooler";
            string r = comp.Tick(p);
            float hp = p.health.summaryHealth.SummaryHealthPercent;
            p.TakeDamage(new DamageInfo(DamageDefOf.Flame, 10f));
            return "fireStarted=" + (f != null) + " result=" + r + " fireLeft=" + (c.GetFirstThing<Fire>(map) != null)
                + " flameHurt=" + (p.health.summaryHealth.SummaryHealthPercent < hp - 0.001f);
        }
    }
}
