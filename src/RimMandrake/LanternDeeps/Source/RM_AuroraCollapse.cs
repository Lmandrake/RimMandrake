using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.LanternDeeps
{
    // ════════════════════════════════════════════════════════════════════
    // LANTERNDEEPS_AURORA_COLLAPSE_BUILD_1. Spec: lanterndeeps_bedazzle_review_2026-10-01.md §4 row 5;
    // the_lantern_deeps.md §3 ("a reconnection storm is a feast day") and the 2026-09-02 collapse
    // ruling (underground_caverns_deep_design.md collapse-hazard-tool, v1: "Regions of instability
    // should have animated bits of dust trailing down to warn the player, as well as some piled sand
    // accumulating below"; "natural caverns that grumble and moan").
    //
    //  1. RM_GameCondition_DeepAurora: the Deep's own condition while the aurora storms overhead
    //     (never the Nightside Ice's surface weather). Lanternstone glows wider, the Chorus rises
    //     (a louder RM_DeepChorus sustainer while the Deep is on screen), Cleavers quicken. Started
    //     by RM_MapComponent_DeepAurora: mirrors any surface condition whose defName names a
    //     reconnection storm or an aurora (none is built yet; NightsideIce owes it), else on its own
    //     MTB clock.
    //  2. The collapse with its warnings: a Harmony prefix on RoofCollapseBufferResolver holds every
    //     newly marked roof cell in a Deep for a warning window (vanilla collapses the same tick).
    //     During it: Anomaly's UndercaveCeilingDebris dust sheets falling, Filth_Sand piling below,
    //     the UndercaveRumble grumble and a message. When the window ends the roof falls if it is
    //     still unsupported; prop it (a column, a wall) and it holds and the groaning stops.
    //     Map generation's silent roof removal is never delayed.
    // ════════════════════════════════════════════════════════════════════

    public class RM_DeepAuroraExtension : DefModExtension
    {
        public List<ThingDef> brighten = new List<ThingDef>();
        public float glowMultiplier = 1.75f;
        public SoundDef chorus;
        public HediffDef quicken;
        public ThingDef quickenRace;
    }

    public class RM_GameCondition_DeepAurora : GameCondition
    {
        private Sustainer chorus;

        private RM_DeepAuroraExtension Ext => def.GetModExtension<RM_DeepAuroraExtension>();

        public override void GameConditionTick()
        {
            base.GameConditionTick();
            RM_DeepAuroraExtension ext = Ext;
            if (ext == null)
            {
                return;
            }
            List<Map> maps = AffectedMaps;
            if (Find.TickManager.TicksGame % 250 == 0)
            {
                foreach (Map m in maps)
                {
                    Apply(m, ext, true);
                }
            }
            Map cur = Find.CurrentMap;
            if (ext.chorus != null && cur != null && maps.Contains(cur))
            {
                if (chorus == null || chorus.Ended)
                {
                    chorus = ext.chorus.TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick));
                }
                chorus?.Maintain();
            }
            else
            {
                EndChorus();
            }
        }

        public override void End()
        {
            RM_DeepAuroraExtension ext = Ext;
            if (ext != null)
            {
                foreach (Map m in AffectedMaps)
                {
                    Apply(m, ext, false);
                }
            }
            EndChorus();
            base.End();
        }

        private void EndChorus()
        {
            if (chorus != null && !chorus.Ended)
            {
                chorus.End();
            }
            chorus = null;
        }

        // on: lanternstone at glowMultiplier x its own radius, Cleavers quickened. off: restored.
        public static int Apply(Map map, RM_DeepAuroraExtension ext, bool on)
        {
            int changed = 0;
            foreach (ThingDef d in ext.brighten)
            {
                foreach (Thing t in map.listerThings.ThingsOfDef(d))
                {
                    CompGlower g = t.TryGetComp<CompGlower>();
                    if (g == null)
                    {
                        continue;
                    }
                    float want = on ? g.Props.glowRadius * ext.glowMultiplier : g.Props.glowRadius;
                    if (System.Math.Abs(g.GlowRadius - want) > 0.01f)
                    {
                        g.GlowRadius = want;
                        if (g.Glows)
                        {
                            g.ForceRegister(map);
                        }
                        changed++;
                    }
                }
            }
            if (on && ext.quicken != null && ext.quickenRace != null)
            {
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
                {
                    if (p.def == ext.quickenRace && !p.Dead)
                    {
                        Hediff h = p.health.hediffSet.GetFirstHediffOfDef(ext.quicken);
                        if (h == null)
                        {
                            p.health.AddHediff(ext.quicken);
                        }
                        else
                        {
                            h.TryGetComp<HediffComp_Disappears>()?.ResetElapsedTicks();
                        }
                    }
                }
            }
            return changed;
        }

        public override void ExposeData()
        {
            base.ExposeData();
        }
    }

    public class RM_MapComponent_DeepAurora : CustomMapComponent
    {
        public const string ConditionDefName = "RM_DeepAurora";

        public RM_MapComponent_DeepAurora(Map map) : base(map)
        {
        }

        public static GameConditionDef Def => DefDatabase<GameConditionDef>.GetNamedSilentFail(ConditionDefName);

        public override void MapComponentTick()
        {
            if (!LanternDeepsSettings.auroraEnabled || !map.IsHashIntervalTick(GenDate.TicksPerHour))
            {
                return;
            }
            GameConditionDef def = Def;
            if (def == null || map.gameConditionManager.ConditionIsActive(def))
            {
                return;
            }
            GameCondition overhead = SurfaceStorm();
            if (overhead != null)
            {
                Start(overhead.TicksLeft > 0 ? overhead.TicksLeft : GenDate.TicksPerDay / 2);
            }
            else if (Rand.MTBEventOccurs(LanternDeepsSettings.auroraMtbDays, GenDate.TicksPerDay, GenDate.TicksPerHour))
            {
                Start(-1);
            }
        }

        // A reconnection storm or aurora condition active on any other map, or the world.
        private GameCondition SurfaceStorm()
        {
            IEnumerable<GameCondition> all = Find.World.gameConditionManager.ActiveConditions;
            foreach (Map m in Find.Maps)
            {
                if (m != map)
                {
                    all = all.Concat(m.gameConditionManager.ActiveConditions);
                }
            }
            return all.FirstOrDefault(c => c.def.defName != ConditionDefName
                && (c.def.defName.Contains("Reconnection") || c.def.defName.Contains("Aurora")));
        }

        public string Start(int duration)
        {
            GameConditionDef def = Def;
            if (def == null)
            {
                return "no def";
            }
            if (duration <= 0)
            {
                duration = (int)(GenDate.TicksPerDay * Rand.Range(0.4f, 0.8f));
            }
            GameCondition cond = GameConditionMaker.MakeCondition(def, duration);
            map.gameConditionManager.RegisterCondition(cond);
            Find.LetterStack.ReceiveLetter(def.LabelCap, "RM_DeepAuroraText".Translate(), LetterDefOf.PositiveEvent, new TargetInfo(map.Center, map));
            return "aurora for " + duration;
        }
    }

    // ── collapse with its warnings ─────────────────────────────────────────

    public class RM_MapComponent_DeepCollapse : CustomMapComponent
    {
        private Dictionary<IntVec3, int> due = new Dictionary<IntVec3, int>();
        private HashSet<IntVec3> released = new HashSet<IntVec3>();
        // cells brought down by force (a galuush blast): they fall when the warning ends, propped or not
        private HashSet<IntVec3> forced = new HashSet<IntVec3>();
        private List<IntVec3> tmpKeys;
        private List<int> tmpVals;

        public RM_MapComponent_DeepCollapse(Map map) : base(map)
        {
        }

        public int Pending => due.Count;

        public void MarkForced(IntVec3 c)
        {
            forced.Add(c);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref due, "due", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpVals);
            Scribe_Collections.Look(ref forced, "forced", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                due = due ?? new Dictionary<IntVec3, int>();
                forced = forced ?? new HashSet<IntVec3>();
            }
        }

        public static bool Applies(Map map)
        {
            return LanternDeepsSettings.collapseWarningsEnabled && map != null && map.Biome != null
                && map.Biome.defName == Patch_GateLanternstoneDeep.HomeBiomeDefName
                && MapGenerator.mapBeingGenerated != map && Current.ProgramState == ProgramState.Playing;
        }

        // Called by the prefix with vanilla's marked list: keeps released cells, holds new ones.
        public void Filter(List<IntVec3> marked)
        {
            int now = Find.TickManager.TicksGame;
            bool fresh = false;
            for (int i = marked.Count - 1; i >= 0; i--)
            {
                IntVec3 c = marked[i];
                if (released.Remove(c))
                {
                    continue;
                }
                if (!due.ContainsKey(c))
                {
                    due[c] = now + LanternDeepsSettings.collapseWarningTicks;
                    fresh = true;
                }
                marked.RemoveAt(i);
            }
            if (fresh)
            {
                Warn(true);
            }
        }

        public override void MapComponentTick()
        {
            if (due.Count == 0)
            {
                return;
            }
            if (!LanternDeepsSettings.collapseWarningsEnabled)
            {
                ReleaseAll();
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (map.IsHashIntervalTick(90))
            {
                Warn(false);
            }
            if (!map.IsHashIntervalTick(30))
            {
                return;
            }
            List<IntVec3> ripe = due.Where(kv => kv.Value <= now).Select(kv => kv.Key).ToList();
            if (ripe.Count > 0)
            {
                Resolve(ripe);
            }
        }

        public string Resolve(List<IntVec3> ripe)
        {
            int fell = 0, held = 0;
            foreach (IntVec3 c in ripe)
            {
                due.Remove(c);
                bool force = forced.Remove(c);
                if (c.Roofed(map) && (force || !Supported(c)))
                {
                    released.Add(c);
                    map.roofCollapseBuffer.MarkToCollapse(c);
                    fell++;
                }
                else
                {
                    held++;
                }
            }
            if (fell > 0)
            {
                map.roofCollapseBufferResolver.CollapseRoofsMarkedToCollapse();
            }
            else if (held > 0 && due.Count == 0)
            {
                Messages.Message("RM_DeepCollapseHeld".Translate(), new TargetInfo(ripe[0], map), MessageTypeDefOf.PositiveEvent);
            }
            return "fell=" + fell + " held=" + held;
        }

        private bool Supported(IntVec3 c)
        {
            return RoofCollapseUtility.WithinRangeOfRoofHolder(c, map) && RoofCollapseUtility.ConnectedToRoofHolder(c, map, true);
        }

        private void ReleaseAll()
        {
            List<IntVec3> all = due.Keys.ToList();
            foreach (IntVec3 c in all)
            {
                due[c] = 0;
            }
            Resolve(all);
        }

        // Dust trailing down, sand piling below, the grumble.
        private void Warn(bool start)
        {
            List<IntVec3> cells = due.Keys.ToList();
            EffecterDef debris = DefDatabase<EffecterDef>.GetNamedSilentFail("UndercaveCeilingDebris");
            ThingDef sand = DefDatabase<ThingDef>.GetNamedSilentFail("Filth_Sand");
            int n = start ? 3 : 1;
            foreach (IntVec3 c in cells.InRandomOrder().Take(n))
            {
                if (debris != null)
                {
                    debris.SpawnMaintained(c, map);
                }
                else
                {
                    FleckMaker.ThrowDustPuffThick(c.ToVector3Shifted(), map, 1.5f, UnityEngine.Color.gray);
                }
                if (sand != null && c.Walkable(map))
                {
                    FilthMaker.TryMakeFilth(c, map, sand);
                }
            }
            if (start || Rand.Chance(0.25f))
            {
                SoundDef rumble = DefDatabase<SoundDef>.GetNamedSilentFail("UndercaveRumble");
                if (rumble != null && Find.CurrentMap == map)
                {
                    rumble.PlayOneShotOnCamera(map);
                }
            }
            if (start && cells.Count > 0)
            {
                Messages.Message("RM_DeepCollapseWarning".Translate(), new TargetInfo(cells[0], map), MessageTypeDefOf.ThreatBig);
            }
        }

        public void ForceDueNow()
        {
            foreach (IntVec3 c in due.Keys.ToList())
            {
                due[c] = 0;
            }
        }
    }

    // Map generation's roof removal (removalMode) must never be delayed: this flag is up while
    // ProcessRoofHolderDespawned runs in that mode.
    [HarmonyPatch(typeof(RoofCollapseCellsFinder), nameof(RoofCollapseCellsFinder.ProcessRoofHolderDespawned))]
    public static class Patch_DeepCollapseRemovalMode
    {
        public static int depth;

        public static void Prefix(bool removalMode)
        {
            if (removalMode)
            {
                depth++;
            }
        }

        public static void Finalizer(bool removalMode)
        {
            if (removalMode && depth > 0)
            {
                depth--;
            }
        }
    }

    [HarmonyPatch(typeof(RoofCollapseBufferResolver), nameof(RoofCollapseBufferResolver.CollapseRoofsMarkedToCollapse))]
    public static class Patch_DeepCollapseWarning
    {
        public static bool Prefix(Map ___map)
        {
            if (Patch_DeepCollapseRemovalMode.depth > 0 || !RM_MapComponent_DeepCollapse.Applies(___map))
            {
                return true;
            }
            RM_MapComponent_DeepCollapse comp = ___map.GetComponent<RM_MapComponent_DeepCollapse>();
            if (comp == null)
            {
                return true;
            }
            List<IntVec3> marked = ___map.roofCollapseBuffer.CellsMarkedToCollapse;
            if (marked.Count == 0)
            {
                return true;
            }
            comp.Filter(marked);
            return marked.Count > 0;
        }
    }

    // jawa/static_call proofs (validation.py, aurora_collapse).
    public static class RM_AuroraCollapseProof
    {
        public static string ProofAurora(string unused)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_DeepAurora comp = map?.GetComponent<RM_MapComponent_DeepAurora>();
            GameConditionDef def = RM_MapComponent_DeepAurora.Def;
            if (comp == null || def == null)
            {
                return "no comp (only on a Deep) or def";
            }
            if (!map.gameConditionManager.ConditionIsActive(def))
            {
                comp.Start(GenDate.TicksPerHour * 6);
            }
            RM_DeepAuroraExtension ext = def.GetModExtension<RM_DeepAuroraExtension>();
            RM_GameCondition_DeepAurora.Apply(map, ext, true);
            CompGlower sample = ext.brighten.SelectMany(d => map.listerThings.ThingsOfDef(d)).Select(t => t.TryGetComp<CompGlower>())
                .FirstOrDefault(g => g != null);
            int quick = map.mapPawns.AllPawnsSpawned.Count(p => ext.quicken != null && p.health.hediffSet.HasHediff(ext.quicken));
            return "active=" + map.gameConditionManager.ConditionIsActive(def)
                + " glow=" + (sample == null ? "none" : sample.Props.glowRadius + "->" + sample.GlowRadius) + " quickened=" + quick;
        }

        // Marks one roofed open cell, runs the resolver: the roof must still be there (held for the
        // warning). Then forces the window over and reports fell/held.
        public static string ProofCollapse(string unused)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_DeepCollapse comp = map?.GetComponent<RM_MapComponent_DeepCollapse>();
            if (comp == null)
            {
                return "no comp (only on a Deep)";
            }
            if (!CellFinder.TryFindRandomCell(map, c => c.Roofed(map) && c.Standable(map) && c.GetFirstPawn(map) == null, out IntVec3 cell))
            {
                return "no roofed cell";
            }
            map.roofCollapseBuffer.MarkToCollapse(cell);
            map.roofCollapseBufferResolver.CollapseRoofsMarkedToCollapse();
            bool heldForWarning = cell.Roofed(map) && comp.Pending > 0;
            comp.ForceDueNow();
            string res = comp.Resolve(new List<IntVec3> { cell });
            return "heldForWarning=" + heldForWarning + " " + res + " roofNow=" + cell.Roofed(map) + " at " + cell;
        }
    }
}
