using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.LongShade
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_SHADE_EXTRAS_1 — the admitted small ideas (owner card 2026-10-08).
    //
    //   LONGSHADE_TOLLOK_TICKS_1   RM_MapComponent_Tollok: an animal or colonist that sits long in WILD deep shade
    //                              (no roof, no shade gear over it) picks up RM_TollokInfestation. Built shade is clean.
    //   LONGSHADE_LURE_AWNING_1    RM_CompLureAwning: the awning's shade comes from the shade-gear comp already on the
    //                              def; this comp is the toggle (off = ordinary furniture) and the inspect line.
    //   LONGSHADE_STAMPEDE_ROOF_1  IncidentWorker_RM_ShadeStampede + RM_MapComponent_Stampede: an overheated herd
    //                              bolts for the roofed part of the home area and runs until it has cooled.
    //   LONGSHADE_EMPTY_PATCH_WARNING_1 reuses the clean-patch tell (RM_GenStep_CleanPatches); nothing new here.
    //
    // Verse-free decisions live in Kernel/RM_ShadeExtrasKernel.cs. Every number is PROVISIONAL.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ShadeExtrasTuning
    {
        public const string BiomeDefName = "RM_LongShade";
        public const int ScanTicks = 250;
        // tollok
        public const float DeepShade = 0.7f;
        public const int DwellThresholdTicks = 2500;      // one hour sitting still
        public const float GainPerScan = 0.04f;
        // lure awning
        public const float ShelterShade = 0.5f;
        public const float LureRadius = 12f;
        // stampede
        public const int MinHerd = 6;
        public const float MinOverheatedFraction = 0.5f;
        public const float HerdRadius = 25f;
        public const int MaxStampedeTicks = 6000;
        public const int ReissueTicks = 120;

        public static bool OnLongShade(Map map)
        {
            return map != null && map.Biome != null && map.Biome.defName == BiomeDefName;
        }

        public static bool Overheated(Pawn p)
        {
            if (p == null || !p.Spawned || p.Dead) return false;
            return p.AmbientTemperature > p.SafeTemperatureRange().max;
        }
    }

    [DefOf]
    public static class RM_ShadeExtrasDefOf
    {
        public static HediffDef RM_TollokInfestation;

        static RM_ShadeExtrasDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ShadeExtrasDefOf));
        }
    }

    // ───────────────────────────── tollok ticks (F2) ─────────────────────────────
    public class RM_MapComponent_Tollok : MapComponent
    {
        private readonly Dictionary<int, int> dwell = new Dictionary<int, int>();
        private readonly Dictionary<int, IntVec3> last = new Dictionary<int, IntVec3>();

        public RM_MapComponent_Tollok(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % RM_ShadeExtrasTuning.ScanTicks != 0) return;
            if (!RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.tollokTicksEnabled
                || !RM_ShadeExtrasTuning.OnLongShade(map) || RM_ShadeExtrasDefOf.RM_TollokInfestation == null) return;
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            if (grid == null) return;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.RaceProps == null || (!p.RaceProps.Animal && !p.RaceProps.Humanlike)) continue;
                int id = p.thingIDNumber;
                IntVec3 pos = p.Position;
                bool still = last.TryGetValue(id, out IntVec3 was) && was == pos;
                last[id] = pos;
                bool wild = RM_LongShadeKernel.WildDeepShade(grid.ShadeAt(pos), grid.RoofShadeAt(pos),
                    grid.GearShadeAt(pos), RM_ShadeExtrasTuning.DeepShade);
                dwell.TryGetValue(id, out int d);
                d = RM_LongShadeKernel.TollokDwell(d, still && wild, RM_ShadeExtrasTuning.ScanTicks);
                dwell[id] = d;
                Hediff h = p.health.hediffSet.GetFirstHediffOfDef(RM_ShadeExtrasDefOf.RM_TollokInfestation);
                float gain = RM_LongShadeKernel.TollokGain(d, RM_ShadeExtrasTuning.DwellThresholdTicks,
                    RM_ShadeExtrasTuning.GainPerScan, h?.Severity ?? 0f);
                if (gain <= 0f) continue;
                if (h == null)
                {
                    h = HediffMaker.MakeHediff(RM_ShadeExtrasDefOf.RM_TollokInfestation, p);
                    h.Severity = gain;
                    p.health.AddHediff(h);
                }
                else
                {
                    h.Severity += gain;
                }
            }
            if (Find.TickManager.TicksGame % (RM_ShadeExtrasTuning.ScanTicks * 40) == 0) Prune();
        }

        private void Prune()
        {
            List<int> gone = new List<int>();
            foreach (int id in last.Keys)
            {
                bool alive = false;
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int i = 0; i < pawns.Count && !alive; i++) alive = pawns[i].thingIDNumber == id;
                if (!alive) gone.Add(id);
            }
            for (int i = 0; i < gone.Count; i++) { last.Remove(gone[i]); dwell.Remove(gone[i]); }
        }
    }

    // ───────────────────────────── lure awning (N4) ─────────────────────────────
    public class CompProperties_RM_LureAwning : CompProperties
    {
        public CompProperties_RM_LureAwning() { compClass = typeof(RM_CompLureAwning); }
    }

    public class RM_CompLureAwning : ThingComp
    {
        private bool registeredOff;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            // the shade-gear comp re-registers the awning on every spawn, so the next rare tick must re-evaluate the toggle
            registeredOff = false;
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (parent.Map == null) return;
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(parent.Map);
            if (grid == null) return;
            bool on = RM_LongShadeSettings.modEnabled && RM_LongShadeSettings.lureAwningEnabled;
            if (!on && !registeredOff) { grid.UnregisterGear(parent); registeredOff = true; }
            else if (on && registeredOff) { grid.RegisterGear(parent); registeredOff = false; }
        }

        public override string CompInspectStringExtra()
        {
            if (parent.Map == null) return null;
            if (!RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.lureAwningEnabled) return "Lure awning switched off in Mod Settings.";
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(parent.Map);
            if (grid == null) return null;
            List<float> shades = new List<float>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, RM_ShadeExtrasTuning.LureRadius, true))
            {
                if (!c.InBounds(parent.Map)) continue;
                List<Thing> things = c.GetThingList(parent.Map);
                for (int i = 0; i < things.Count; i++)
                {
                    Pawn p = things[i] as Pawn;
                    if (p != null && p.RaceProps.Animal && p.Faction == null) shades.Add(grid.ShadeAt(c));
                }
            }
            return "Game sheltering nearby: " + RM_LongShadeKernel.ShelterCount(shades, RM_ShadeExtrasTuning.ShelterShade);
        }
    }

    // ───────────────────────────── stampede for your roof (F3) ─────────────────────────────
    public class RM_MapComponent_Stampede : MapComponent
    {
        private readonly List<Pawn> runners = new List<Pawn>();
        private int startTick = -1;
        private IntVec3 target = IntVec3.Invalid;

        public RM_MapComponent_Stampede(Map map) : base(map) { }

        public bool Running => runners.Count > 0;

        public void Begin(List<Pawn> herd, IntVec3 roofCell)
        {
            runners.Clear();
            runners.AddRange(herd);
            target = roofCell;
            startTick = Find.TickManager.TicksGame;
            Issue();
        }

        private void Issue()
        {
            for (int i = 0; i < runners.Count; i++)
            {
                Pawn p = runners[i];
                if (p == null || !p.Spawned || p.Dead || p.Downed) continue;
                Job job = JobMaker.MakeJob(JobDefOf.Goto, target);
                job.locomotionUrgency = LocomotionUrgency.Sprint;
                job.canBashDoors = true;
                job.canBashFences = true;
                job.expiryInterval = 600;
                p.jobs.StartJob(job, JobCondition.InterruptForced, null, false, true);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.Saving) runnersSave = new List<Pawn>(runners);
            Scribe_Collections.Look(ref runnersSave, "runners", LookMode.Reference);
            Scribe_Values.Look(ref startTick, "startTick", -1);
            Scribe_Values.Look(ref target, "target", IntVec3.Invalid);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                runners.Clear();
                if (runnersSave != null) runners.AddRange(runnersSave);
                runners.RemoveAll(x => x == null);
            }
        }

        private List<Pawn> runnersSave;

        public override void MapComponentTick()
        {
            if (runners.Count == 0 || Find.TickManager.TicksGame % RM_ShadeExtrasTuning.ReissueTicks != 0) return;
            int since = Find.TickManager.TicksGame - startTick;
            bool reissue = false;
            for (int i = runners.Count - 1; i >= 0; i--)
            {
                Pawn p = runners[i];
                bool still = p != null && p.Spawned && !p.Dead && RM_ShadeExtrasTuning.Overheated(p);
                if (!RM_LongShadeKernel.StampedeContinues(still, since, RM_ShadeExtrasTuning.MaxStampedeTicks))
                {
                    runners.RemoveAt(i);
                    continue;
                }
                if (p.CurJob == null || p.CurJob.def != JobDefOf.Goto) reissue = true;
            }
            if (reissue) Issue();
        }
    }

    public class IncidentWorker_RM_ShadeStampede : IncidentWorker
    {
        private static List<Pawn> FindHerd(Map map)
        {
            List<Pawn> animals = new List<Pawn>();
            IReadOnlyList<Pawn> all = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn p = all[i];
                if (p.Faction == null && p.RaceProps.Animal && p.RaceProps.herdAnimal && !p.Dead && !p.Downed) animals.Add(p);
            }
            List<Pawn> best = null;
            for (int i = 0; i < animals.Count; i++)
            {
                List<Pawn> near = animals.FindAll(a => a.def == animals[i].def
                    && a.Position.InHorDistOf(animals[i].Position, RM_ShadeExtrasTuning.HerdRadius));
                int hot = near.FindAll(RM_ShadeExtrasTuning.Overheated).Count;
                if (RM_LongShadeKernel.StampedeReady(near.Count, hot, RM_ShadeExtrasTuning.MinHerd, RM_ShadeExtrasTuning.MinOverheatedFraction)
                    && (best == null || near.Count > best.Count))
                {
                    best = near;
                }
            }
            return best;
        }

        private static IntVec3 FindRoof(Map map)
        {
            Area home = map.areaManager.Home;
            List<IntVec3> cells = new List<IntVec3>();
            foreach (IntVec3 c in home.ActiveCells)
            {
                if (c.Roofed(map) && c.Standable(map)) cells.Add(c);
            }
            return cells.Count == 0 ? IntVec3.Invalid : cells.RandomElement();
        }

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (map == null || !RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.stampedeEnabled
                || !RM_ShadeExtrasTuning.OnLongShade(map)) return false;
            RM_MapComponent_Stampede st = map.GetComponent<RM_MapComponent_Stampede>();
            return st != null && !st.Running && FindRoof(map).IsValid && FindHerd(map) != null;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            List<Pawn> herd = FindHerd(map);
            IntVec3 roof = FindRoof(map);
            if (herd == null || !roof.IsValid) return false;
            map.GetComponent<RM_MapComponent_Stampede>().Begin(herd, roof);
            SendStandardLetter("An overheated herd is bolting for your roof",
                "A herd caught out in the open has found every shadow full and is running for the biggest shade it can see: your base. "
                + "They are panicked and will go through fences and into barns. They will not leave until they have cooled.",
                LetterDefOf.ThreatSmall, parms, herd[0]);
            return true;
        }
    }

    // ───────────────────────────── harrok (W2) ─────────────────────────────
    /// <summary>The harrok stands still in the open as a pole; whatever rests in the strip its shadow lays is under its mouth.</summary>
    public class CompProperties_RM_HarrokAmbush : CompProperties
    {
        public float shadowLengthCells = 6f;   // PROVISIONAL
        public float shadowHalfWidth = 0.9f;   // PROVISIONAL
        public float maxPreyBodySize = 1.5f;   // PROVISIONAL
        public int cooldownTicks = 900;        // PROVISIONAL
        public FloatRange strikeDamageRange = new FloatRange(12f, 20f);
        public int lieStillTicks = 2500;
        public CompProperties_RM_HarrokAmbush() { compClass = typeof(RM_CompHarrokAmbush); }
    }

    public class RM_CompHarrokAmbush : ThingComp
    {
        private int lastStrike = -999999;
        private CompProperties_RM_HarrokAmbush Props => (CompProperties_RM_HarrokAmbush)props;

        public override void CompTick()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Faction != null) return;
            if (!RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.harrokEnabled) return;
            if (pawn.IsHashIntervalTick(60)) Scan(pawn);
        }

        private void Scan(Pawn pawn)
        {
            Map map = pawn.Map;
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            if (grid == null) return;
            Vector2 dir = grid.SunShadowDirection;
            if (dir.sqrMagnitude < 0.0001f) return;
            dir.Normalize();
            // stand still like a pole: an idle wander becomes a long wait
            JobDef cur = pawn.CurJob?.def;
            if (cur == JobDefOf.GotoWander || cur == JobDefOf.Wait_Wander)
            {
                Job wait = JobMaker.MakeJob(JobDefOf.Wait);
                wait.expiryInterval = Props.lieStillTicks;
                wait.checkOverrideOnExpire = true;
                pawn.jobs.StartJob(wait, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
            }
            int now = Find.TickManager.TicksGame;
            int reach = Mathf.CeilToInt(Props.shadowLengthCells + Props.shadowHalfWidth);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, reach, true))
            {
                if (!c.InBounds(map)) continue;
                if (!RM_LongShadeKernel.InShadowStrip(c.x - pawn.Position.x, c.z - pawn.Position.z, dir.x, dir.y,
                        Props.shadowLengthCells, Props.shadowHalfWidth)) continue;
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    Pawn prey = things[i] as Pawn;
                    if (prey == null || prey == pawn || prey.Dead) continue;
                    bool resting = prey.pather == null || !prey.pather.MovingNow || prey.Downed;
                    if (!RM_LongShadeKernel.HarrokCanStrike(resting, prey.BodySize, Props.maxPreyBodySize, now, lastStrike, Props.cooldownTicks)) continue;
                    lastStrike = now;
                    float amount = Props.strikeDamageRange.RandomInRange;
                    prey.TakeDamage(new DamageInfo(DamageDefOf.Stab, amount, 0.2f, -1f, pawn));
                    if (prey.Faction == Faction.OfPlayer)
                    {
                        Messages.Message("A harrok's shadow fell across " + prey.LabelShort + ", and the harrok struck.", prey, MessageTypeDefOf.NegativeEvent);
                    }
                    return;
                }
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastStrike, "rmHarrokLastStrike", -999999);
        }
    }

    // ───────────────────────────── Jawa return (I5) ─────────────────────────────
    /// <summary>Which factions may come for the hull (def-name prefixes), and how long the tow takes. Set on the IncidentDef (the campaign tier names the clan).</summary>
    public class RM_HullTowExtension : DefModExtension
    {
        public List<string> factionPrefixes = new List<string>();
        public int arrivalPawns = 3;
        public int towTicks = 15000;      // PROVISIONAL: about a quarter day after they arrive
        public int maxLooseItems = 0;     // PROVISIONAL
        public int hullWidth = 25;        // dead_crawler.txt FOOTPRINT 25x9
        public int hullHeight = 9;
    }

    /// <summary>Remembers where the road's dead crawler lies, whether anyone has been inside, and the tow.</summary>
    public class RM_MapComponent_CrawlerHull : MapComponent
    {
        public IntVec3 hullCenter = IntVec3.Invalid;
        public int width = 25, height = 9;
        private bool entered;
        private int towStartTick = -1;
        private bool towed;
        private int towTicks = 15000;

        public RM_MapComponent_CrawlerHull(Map map) : base(map) { }

        public bool HasHull => hullCenter.IsValid && !towed;
        public bool ClanComing => towStartTick >= 0 && !towed;

        public void SetHull(IntVec3 center, int w, int h)
        {
            hullCenter = center; width = w; height = h; entered = false; towStartTick = -1; towed = false;
        }

        public bool InHull(IntVec3 c)
        {
            return hullCenter.IsValid && RM_LongShadeKernel.InHullRect(c.x, c.z, hullCenter.x, hullCenter.z, width, height);
        }

        private IEnumerable<IntVec3> HullCells()
        {
            CellRect r = new CellRect(hullCenter.x - width / 2, hullCenter.z - height / 2, width, height);
            foreach (IntVec3 c in r) if (c.InBounds(map)) yield return c;
        }

        public bool Looted(int maxItems)
        {
            if (!HasHull) return false;
            int hostiles = 0, items = 0;
            foreach (IntVec3 c in HullCells())
            {
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    Pawn p = things[i] as Pawn;
                    if (p != null && p.HostileTo(Faction.OfPlayer) && !p.Dead) hostiles++;
                    else if (things[i].def.category == ThingCategory.Item && things[i].def.EverHaulable) items++;
                }
            }
            return RM_LongShadeKernel.HullLooted(entered, hostiles, items, maxItems);
        }

        public void ClanArrived(int towTicksForThisClan) { towStartTick = Find.TickManager.TicksGame; towTicks = towTicksForThisClan; }

        public override void MapComponentTick()
        {
            if (!hullCenter.IsValid || towed || Find.TickManager.TicksGame % RM_ShadeExtrasTuning.ScanTicks != 0) return;
            if (!entered)
            {
                foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
                {
                    if (InHull(p.Position)) { entered = true; break; }
                }
            }
            if (RM_LongShadeKernel.TowDone(towStartTick, Find.TickManager.TicksGame, towTicks)) Tow();
        }

        private void Tow()
        {
            towed = true;
            int removed = 0;
            foreach (IntVec3 c in HullCells())
            {
                List<Thing> things = new List<Thing>(c.GetThingList(map));
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (t.def.category == ThingCategory.Building && t.Faction == null
                        && !(t.def.building != null && t.def.building.isNaturalRock))
                    {
                        t.Destroy(DestroyMode.Vanish);
                        removed++;
                    }
                }
                if (Rand.Chance(0.15f)) FleckMaker.ThrowDustPuffThick(c.ToVector3Shifted(), map, 3f, new Color(0.8f, 0.7f, 0.5f));
            }
            RM_MapComponent_ShadeGrid.For(map)?.Recompute();
            Messages.Message("The clan has towed the dead sandcrawler away. Its shadow went with it, and everything that lived in its lee is looking for the next one.",
                new TargetInfo(hullCenter, map), MessageTypeDefOf.NeutralEvent);
            Log.Message("[RM LongShade] Jawa return: hull towed, " + removed + " buildings removed");
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref hullCenter, "hullCenter", IntVec3.Invalid);
            Scribe_Values.Look(ref width, "hullWidth", 25);
            Scribe_Values.Look(ref height, "hullHeight", 9);
            Scribe_Values.Look(ref entered, "hullEntered", false);
            Scribe_Values.Look(ref towStartTick, "towStartTick", -1);
            Scribe_Values.Look(ref towed, "hullTowed", false);
            Scribe_Values.Look(ref towTicks, "towTicks", 15000);
        }
    }

    public class IncidentWorker_RM_HullTow : IncidentWorker
    {
        private RM_HullTowExtension Ext => def.GetModExtension<RM_HullTowExtension>();

        private Faction FindClan()
        {
            RM_HullTowExtension ext = Ext;
            if (ext == null) return null;
            foreach (Faction f in Find.FactionManager.AllFactionsVisible)
            {
                if (f.IsPlayer || f.defeated || f.HostileTo(Faction.OfPlayer) || f.def.defName == null) continue;
                for (int i = 0; i < ext.factionPrefixes.Count; i++)
                {
                    if (f.def.defName.StartsWith(ext.factionPrefixes[i])) return f;
                }
            }
            return null;
        }

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (map == null || !RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.jawaReturnEnabled
                || !RM_ShadeExtrasTuning.OnLongShade(map) || Ext == null) return false;
            RM_MapComponent_CrawlerHull hull = map.GetComponent<RM_MapComponent_CrawlerHull>();
            return hull != null && hull.HasHull && !hull.ClanComing && hull.Looted(Ext.maxLooseItems) && FindClan() != null;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            RM_MapComponent_CrawlerHull hull = map.GetComponent<RM_MapComponent_CrawlerHull>();
            Faction clan = FindClan();
            if (hull == null || clan == null) return false;
            // find the entry cell BEFORE generating pawns: a failed find afterwards would leave them unspawned in the world pawn pool
            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Friendly)) return false;
            PawnGroupMakerParms gp = new PawnGroupMakerParms
            {
                groupKind = PawnGroupKindDefOf.Peaceful,
                tile = map.Tile,
                faction = clan,
                points = Mathf.Max(200f, 120f * Ext.arrivalPawns),
            };
            List<Pawn> pawns = PawnGroupMakerUtility.GeneratePawns(gp, false).ToList();
            if (pawns.Count == 0) return false;
            for (int i = 0; i < pawns.Count; i++)
            {
                IntVec3 c = CellFinder.RandomClosewalkCellNear(entry, map, 4);
                GenSpawn.Spawn(pawns[i], c, map);
            }
            LordMaker.MakeNewLord(clan, new LordJob_VisitColony(clan, hull.hullCenter), map, pawns);
            hull.ClanArrived(Ext.towTicks);
            SendStandardLetter("A clan has come for the crawler",
                "A clan of scavengers has walked in from the edge of the map. The dead sandcrawler was theirs once, and now that it has been picked clean they mean to tow it away. "
                + "Its shadow is the biggest on the map and it will leave with the hull. Everything sheltering in its lee will have to find another.",
                LetterDefOf.NeutralEvent, parms, pawns[0]);
            return true;
        }
    }
}
