using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.HugeThings
{
    [DefOf]
    public static class HugeThingsDefOf
    {
        public static ThingDef RM_HugeTrunkBlocker;

        static HugeThingsDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(HugeThingsDefOf));
        }
    }

    /// <summary>
    /// The opt-in surface other mods call (the titan half of this mod does, for every race it tiers). Idempotent, and
    /// must run at startup - before any map loads - because vanilla files a Thing into the
    /// WithCustomRectForSelector lister group by its def's flag at the moment the Thing registers.
    /// </summary>
    public static class HugeThingsApi
    {
        public static void OptInPlant(ThingDef def, RM_HugePlantExtension ext = null)
        {
            if (def?.plant == null) return;
            if (def.GetModExtension<RM_HugePlantExtension>() == null)
            {
                if (def.modExtensions == null) def.modExtensions = new List<DefModExtension>();
                def.modExtensions.Add(ext ?? new RM_HugePlantExtension());
            }
            if (def.comps == null) def.comps = new List<CompProperties>();
            if (!def.comps.Any(c => c.compClass == typeof(CompHugeFootprint)))
            {
                def.comps.Add(new CompProperties_HugeFootprint());
            }
            def.hasCustomRectForSelector = true;
            ValidateRenderer(def);
        }

        /// <summary>
        /// The footprint replays vanilla Plant.Print's single-mesh branch (GPT review #7, #11). Anything else keeps the
        /// whole-quad selection but blocks nothing, with one error naming why: a multi-mesh plant, a thingClass that
        /// overrides Print, or a drawSize.x != 1 (the measurement frame assumes the quad's bottom is the root's south edge).
        /// </summary>
        public static void ValidateRenderer(ThingDef def)
        {
            RM_HugePlantExtension ext = def.GetModExtension<RM_HugePlantExtension>();
            if (ext == null) return;
            string why = null;
            if (def.plant.maxMeshCount != 1) why = "maxMeshCount " + def.plant.maxMeshCount + " (Plant.Print's multi-mesh branch)";
            else if (def.thingClass == null || !typeof(Plant).IsAssignableFrom(def.thingClass)) why = "thingClass is not a Plant";
            else if (AccessTools.Method(def.thingClass, "Print", new[] { typeof(SectionLayer) })?.DeclaringType != typeof(Plant))
                why = "thingClass " + def.thingClass.Name + " overrides Plant.Print";
            else if (ext.variants.Count > 0 && (def.graphicData?.drawSize.x ?? 1f) != 1f)
                why = "graphicData.drawSize.x " + def.graphicData.drawSize.x + " != 1";
            else if (ext.variants.Count > 0 && ext.measuredSize > 0f
                     && System.Math.Abs(ext.measuredSize - def.plant.visualSizeRange.max * (def.graphicData?.drawSize.x ?? 1f)) > 0.01f)
                why = "measuredSize " + ext.measuredSize + " != drawSize.x * visualMax (resized since measuring: rerun the tool)";
            if (why == null) why = Extensions_DataProblem(def, ext);   // A3.12: data the planner must never see
            ext.blockingSupported = why == null;
            if (why != null)
                Log.Error("[RimMandrake.HugeThings] " + def.defName + ": " + why + " -- it gets selection only, no ground footprint.");
            // Owner ruling 2026-10-07 21:08: art that touches the ground only in its own cell makes that cell solid. Verified
            // 1.6: PathGrid blocks a cell for ANY thing whose def is Impassable (not only edifices); cutting and harvesting use
            // PathEndMode.Touch (WorkGiver_PlantsCut, WorkGiver_GrowerHarvest, JobDriver_PlantWork), which reaches an
            // impassable 1x1 target from an adjacent open cell (TouchPathEndModeUtility.AddAllowedAdjacentRegions); a plant
            // never wipes anything on spawn (GenSpawn.SpawningWipes returns false for a Plant). Read at startup, so toggling
            // the footprint setting affects these plants after a restart.
            List<int> counts = new List<int>();
            foreach (HugePlantVariant v in ext.variants) counts.Add(v?.contact?.Count ?? 0);
            if (RootRule.RootImpassable(RM_HugeThingsSettings.PlantTrunkActive, ext.blockingSupported, counts))
            {
                def.passability = Traversability.Impassable;
                ext.rootImpassable = true;
            }
        }

        /// <summary>PLANT_FOOTPRINT_HARDENING_1 (A3.12): the extension's ConfigErrors, plus the def's own drawSize and visualSizeRange
        /// bounds, consulted at runtime: any problem turns blocking off for the def (selection only), so the planner never
        /// gets an unbounded window.</summary>
        private static string Extensions_DataProblem(ThingDef def, RM_HugePlantExtension ext)
        {
            foreach (string e in ext.ConfigErrors()) return e;
            float dx = def.graphicData?.drawSize.x ?? 1f;
            FloatRange vs = def.plant.visualSizeRange;
            if (!(dx > 0f && dx <= RM_HugePlantExtension.MaxDrawExtent)) return "graphicData.drawSize.x " + dx + " is not in (0, " + RM_HugePlantExtension.MaxDrawExtent + "]";
            if (!(vs.min > 0f && vs.max >= vs.min && vs.max * dx <= RM_HugePlantExtension.MaxDrawExtent))
                return "plant.visualSizeRange " + vs + " (x drawSize " + dx + ") is not a positive range within " + RM_HugePlantExtension.MaxDrawExtent;
            return null;
        }

        public static void OptInPawn(ThingDef def, RM_HugePawnExtension ext = null)
        {
            if (def?.race == null) return;
            if (def.GetModExtension<RM_HugePawnExtension>() == null)
            {
                if (def.modExtensions == null) def.modExtensions = new List<DefModExtension>();
                def.modExtensions.Add(ext ?? new RM_HugePawnExtension());
            }
            def.hasCustomRectForSelector = true;
        }

        /// <summary>The hitbox a huge pawn is clicked by right now, or null for "no bigger than vanilla".</summary>
        public static CellRect? PawnHitbox(Pawn pawn)
        {
            RM_HugePawnExtension ext = pawn?.def.GetModExtension<RM_HugePawnExtension>();
            if (ext == null || !pawn.Spawned || !RM_HugeThingsSettings.PawnHitboxActive) return null;
            Vector2 drawn = ActiveDrawSize(pawn);
            CellRect foot = pawn.OccupiedRect();   // Large Pawns' square when it is loaded, else one cell
            return FootprintMath.PawnHitbox(drawn.x, drawn.y, ext.hitboxFraction, RM_HugeThingsSettings.pawnHitboxScale, foot, pawn.DrawPos.ToIntVec3());
        }

        /// <summary>PLANT_INTERACTION_GUARDS_1 (C3.3): the drawSize of the graphic 1.6 PawnRenderNode_AnimalPart.GraphicFor actually
        /// draws (alternate graphic, else femaleGraphicData for a female, else bodyGraphicData), never smaller than the body's.</summary>
        public static Vector2 ActiveDrawSize(Pawn pawn)
        {
            PawnKindLifeStage stage = pawn.ageTracker?.CurKindLifeStage;
            Vector2 body = stage?.bodyGraphicData?.drawSize ?? Vector2.one;
            Vector2? active = null;
            try
            {
                if (stage?.bodyGraphicData != null && pawn.TryGetAlternate(out AlternateGraphic ag, out int _) && ag != null)
                    active = ag.GetGraphic(stage.bodyGraphicData.Graphic)?.drawSize;
                else if (pawn.gender == Gender.Female && stage?.femaleGraphicData != null)
                    active = stage.femaleGraphicData.drawSize;
            }
            catch (System.Exception e)
            {
                Log.ErrorOnce("[RimMandrake.HugeThings] could not resolve " + pawn + "'s drawn graphic; hitbox uses the body graphic: " + e,
                              pawn.def.shortHash ^ 0x4b17);
            }
            HitboxDraw.Pick(body.x, body.y, active.HasValue, active?.x ?? 0f, active?.y ?? 0f, out float x, out float y);
            return new Vector2(x, y);
        }

        public static CellRect Union(CellRect a, CellRect b) => FootprintMath.Union(a, b);
    }

    /// <summary>
    /// Clicking anywhere on a huge thing selects it. Vanilla already selects any Thing whose
    /// CustomRectForSelector contains the clicked cell (GenUI.ThingsUnderMouse) and draws the selection
    /// brackets around that rect (SelectionDrawer); Plant and Pawn simply never supply one. This postfix
    /// supplies it for opted-in defs only. Priority.Last so it widens, never narrows, Large Pawns' square.
    /// </summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.CustomRectForSelector), MethodType.Getter)]
    public static class Patch_Thing_CustomRectForSelector
    {
        [HarmonyPriority(Priority.Last)]
        public static void Postfix(Thing __instance, ref CellRect? __result)
        {
            if (!__instance.def.hasCustomRectForSelector) return;
            if (__instance is Plant plant)
            {
                CompHugeFootprint comp = plant.GetComp<CompHugeFootprint>();
                CellRect? r = comp?.SelectRect();
                if (r.HasValue) __result = __result.HasValue ? HugeThingsApi.Union(r.Value, __result.Value) : r;   // widen, never narrow
                return;
            }
            if (__instance is Pawn pawn)
            {
                CellRect? r = HugeThingsApi.PawnHitbox(pawn);
                if (r.HasValue) __result = __result.HasValue ? HugeThingsApi.Union(r.Value, __result.Value) : r;
            }
        }
    }

    /// <summary>PLANT_FOOTPRINT_HARDENING_1 (A3.8): the growth check runs after Plant.TickLong has added this period's growth.</summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.TickLong))]
    public static class Patch_Plant_TickLong
    {
        public static void Postfix(Plant __instance)
        {
            if (!__instance.def.hasCustomRectForSelector || !__instance.Spawned) return;
            __instance.GetComp<CompHugeFootprint>()?.Notify_PlantTickedLong();
        }
    }

    /// <summary>GenUI.ThingsUnderMouse adds a plant twice when its root cell is clicked (once as a cell thing, once through
    /// its custom rect: the duplicate check looks only at the close-pawn list). Drop repeats, keeping the first, so click
    /// cycling reaches everything underneath exactly once (GPT review #12).</summary>
    [HarmonyPatch(typeof(GenUI), nameof(GenUI.ThingsUnderMouse))]
    public static class Patch_GenUI_ThingsUnderMouse
    {
        // PLANT_FOOTPRINT_HARDENING_1 (A2.6 / C2.8 / D2.5): nothing to do while neither click feature is on, and no allocation for a
        // short list (the usual case): an in-place O(n^2) pass keeps the first of each repeat.
        private static HashSet<Thing> seen;

        public static void Postfix(List<Thing> __result)
        {
            if (__result == null || __result.Count < 2) return;
            if (!RM_HugeThingsSettings.PlantSelectionActive && !RM_HugeThingsSettings.PawnHitboxActive) return;
            int n = __result.Count;
            if (n <= 16)
            {
                int w = 0;
                for (int i = 0; i < n; i++)
                {
                    Thing t = __result[i];
                    bool dup = false;
                    for (int j = 0; j < w; j++) if (__result[j] == t) { dup = true; break; }
                    if (!dup) __result[w++] = t;
                }
                if (w < n) __result.RemoveRange(w, n - w);
                return;
            }
            if (seen == null) seen = new HashSet<Thing>();
            seen.Clear();
            int k = 0;
            for (int i = 0; i < n; i++)
            {
                Thing t = __result[i];
                if (seen.Add(t)) __result[k++] = t;
            }
            if (k < n) __result.RemoveRange(k, n - k);
            seen.Clear();
        }
    }

    /// <summary>A blocker must not carve zones (GPT review #3, verified 1.6: Thing.SpawnSetup -> !CanOverlapZones ->
    /// ZoneManager.Notify_NoZoneOverlapThingSpawned removes the cells and splits the zone, and removing the blocker never
    /// gives them back). The zone keeps the cell; vanilla already refuses to store into it (StoreUtility.NoStorageBlockersIn:
    /// an impassable non-item) or sow it (PlantUtility: BlocksPlanting).</summary>
    [HarmonyPatch(typeof(ZoneManager), "Notify_NoZoneOverlapThingSpawned")]
    public static class Patch_ZoneManager_NoZoneOverlap
    {
        public static bool Prefix(Thing thing) => !(thing is Building_TrunkBlocker);
    }

    /// <summary>Harvest changes growth without despawning: re-take the footprint now, not 2000 ticks later (GPT #14).</summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.PlantCollected))]
    public static class Patch_Plant_PlantCollected
    {
        public static void Postfix(Plant __instance)
        {
            CompHugeFootprint c = __instance.GetComp<CompHugeFootprint>();
            if (c != null && __instance.Spawned) __instance.Map.GetComponent<MapComponent_HugeFootprints>()?.MarkDirty(c);
        }
    }

    /// <summary>
    /// An explosion over a giant's trunk cells hits the giant ONCE (owner ruling 2026-10-07 20:38): the blast's own
    /// damagedThings list (DamageWorker.ExplosionDamageThing, verified 1.6) is the dedup, so a trunk cell is redirected to
    /// its plant, and the plant is skipped if the blast already hit it (through another cell or its root).
    /// DamageWorker_Vaporize overrides this method but calls base, so it is covered too.
    /// </summary>
    [HarmonyPatch(typeof(DamageWorker), "ExplosionDamageThing")]
    public static class Patch_DamageWorker_ExplosionDamageThing
    {
        public static bool Prefix(ref Thing t, List<Thing> damagedThings, List<Thing> ignoredThings)
        {
            if (!(t is Building_TrunkBlocker b)) return true;
            // PLANT_INTERACTION_GUARDS_1 (C3.10): an ignored blocker stays ignored; vanilla would have skipped it, and after the
            // swap below it would test the plant instead.
            if (ignoredThings != null && ignoredThings.Contains(b)) return false;
            if (!damagedThings.Contains(b)) damagedThings.Add(b);
            if (!RM_HugeThingsSettings.PlantTrunkDamageActive) return false;   // Mod Settings: the trunk soaks the blast
            Plant p = b.owner;
            if (p == null || p.Destroyed || !p.Spawned || damagedThings.Contains(p)) return false;
            t = p;
            return true;
        }
    }

    /// <summary>
    /// Gravship landing (GPT review #15; policy set by the coordinator 2026-10-07): a landing that clears any cell holding a
    /// giant's blocker or root removes that giant, so no plant survives outside the ship with half a footprint and no
    /// blocker regrows into the ship. Verified 1.6: GravshipPlacementUtility.ClearArea clears cell by cell.
    /// </summary>
    [HarmonyPatch(typeof(GravshipPlacementUtility), nameof(GravshipPlacementUtility.ClearArea))]
    public static class Patch_Gravship_ClearArea
    {
        public static void Prefix(Map map, IntVec3 root, HashSet<IntVec3> clearCells)
        {
            MapComponent_HugeFootprints mc = map?.GetComponent<MapComponent_HugeFootprints>();
            if (mc == null || clearCells == null || mc.Count == 0) return;
            List<IntVec3> cells = new List<IntVec3>(clearCells.Count);
            foreach (IntVec3 c in clearCells) cells.Add(root + c);
            foreach (Plant p in mc.OwnersAt(cells))
            {
                if (!p.Destroyed) p.Destroy(DestroyMode.Vanish);
            }
        }
    }

    [StaticConstructorOnStartup]
    public static class HugeThingsStartup
    {
        public const string HarmonyId = "mandrake.rm.hugethings";

        static HugeThingsStartup()
        {
            PatchNamespace(new Harmony(HarmonyId), typeof(HugeThingsStartup).Namespace);
            // after every [StaticConstructorOnStartup] (the titan half patches from its own cctor)
            LongEventHandler.ExecuteWhenFinished(AssertPatchedOnce);
            int plants = 0, pawns = 0;
            foreach (ThingDef td in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (td.plant != null && td.GetModExtension<RM_HugePlantExtension>() != null)
                {
                    HugeThingsApi.OptInPlant(td);
                    plants++;
                }
                if (td.race != null && td.GetModExtension<RM_HugePawnExtension>() != null)
                {
                    HugeThingsApi.OptInPawn(td);
                    pawns++;
                }
            }
            Log.Message("[RimMandrake.HugeThings] ready: " + plants + " huge plants, " + pawns + " huge pawn races.");
        }

        /// <summary>The assembly holds two halves (giant plants and pawns here, titans in RimMandrake.TitanicCreatures), each with
        /// its own Harmony id: PatchAll on the assembly from both would patch every method twice. This is PatchAll restricted to
        /// one namespace (Harmony's PatchAll is exactly CreateClassProcessor(type).Patch() over the assembly's types).</summary>
        /// <summary>PLANT_FOOTPRINT_HARDENING_1 (C4.9 / D2.1): the namespaces PatchNamespace is called with. A [HarmonyPatch] class in
        /// any other namespace (e.g. moved into a sub-namespace) would silently never load; AssertPatchedOnce reports it.</summary>
        public static readonly string[] PatchedNamespaces = { "RimMandrake.HugeThings", "RimMandrake.TitanicCreatures" };
        private static readonly Dictionary<System.Type, int> applied = new Dictionary<System.Type, int>();

        /// <summary>Every [HarmonyPatch] class in this assembly applied exactly once; errors name each one that was not.</summary>
        public static void AssertPatchedOnce()
        {
            int bad = 0;
            foreach (System.Type t in AccessTools.GetTypesFromAssembly(typeof(HugeThingsStartup).Assembly))
            {
                if (!t.IsDefined(typeof(HarmonyPatch), false)) continue;
                int n = applied.TryGetValue(t, out int c) ? c : 0;
                if (n == 1) continue;
                bad++;
                Log.Error("[RimMandrake.HugeThings] patch class " + t.FullName + " was applied " + n + " times (want exactly 1)" +
                          (System.Array.IndexOf(PatchedNamespaces, t.Namespace) < 0 ? ": its namespace is not one PatchNamespace covers" : ""));
            }
            if (bad == 0) Log.Message("[RimMandrake.HugeThings] all " + applied.Count + " patch classes applied exactly once.");
        }

        public static int PatchNamespace(Harmony harmony, string ns)
        {
            int n = 0;
            foreach (System.Type t in AccessTools.GetTypesFromAssembly(typeof(HugeThingsStartup).Assembly))
            {
                if (t.Namespace != ns) continue;
                // Only [HarmonyPatch] classes. PatchClassProcessor runs any method named Prepare/Cleanup/TargetMethod on the
                // type it is given, so a JobDriver subclass (instance Cleanup(JobCondition)) threw TargetException and killed
                // the titanic cctor before InjectWakeComps ran (HUGETHINGS_TITANIC_CCTOR_THROWS_1).
                if (!t.IsDefined(typeof(HarmonyPatch), false)) continue;
                harmony.CreateClassProcessor(t).Patch();
                applied[t] = (applied.TryGetValue(t, out int c) ? c : 0) + 1;
                n++;
            }
            return n;
        }
    }
}
