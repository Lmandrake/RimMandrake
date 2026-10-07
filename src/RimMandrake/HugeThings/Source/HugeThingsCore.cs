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
    /// The opt-in surface other mods call (TitanicCreatures does, for every race it tiers). Idempotent, and
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
            if (ext == null || !pawn.Spawned || !RM_HugeThingsSettings.pawnHitboxEnabled) return null;
            Vector2 drawn = pawn.ageTracker?.CurKindLifeStage?.bodyGraphicData?.drawSize ?? Vector2.one;
            int w = FootprintMath.HitboxSide(drawn.x, ext.hitboxFraction, RM_HugeThingsSettings.pawnHitboxScale);
            int h = FootprintMath.HitboxSide(drawn.y, ext.hitboxFraction, RM_HugeThingsSettings.pawnHitboxScale);
            CellRect foot = pawn.OccupiedRect();   // Large Pawns' square when it is loaded, else one cell
            if (w <= foot.Width && h <= foot.Height)
            {
                return foot.Area > 1 ? foot : (CellRect?)null;
            }
            CellRect body = FootprintMath.CentredRect(pawn.DrawPos.ToIntVec3(), w, h);
            return Union(body, foot);
        }

        public static CellRect Union(CellRect a, CellRect b)
        {
            int minX = Mathf.Min(a.minX, b.minX), minZ = Mathf.Min(a.minZ, b.minZ);
            int maxX = Mathf.Max(a.maxX, b.maxX), maxZ = Mathf.Max(a.maxZ, b.maxZ);
            return new CellRect(minX, minZ, maxX - minX + 1, maxZ - minZ + 1);
        }
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
                if (r.HasValue) __result = r;
                return;
            }
            if (__instance is Pawn pawn)
            {
                CellRect? r = HugeThingsApi.PawnHitbox(pawn);
                if (r.HasValue) __result = __result.HasValue ? HugeThingsApi.Union(r.Value, __result.Value) : r;
            }
        }
    }

    [StaticConstructorOnStartup]
    public static class HugeThingsStartup
    {
        public const string HarmonyId = "mandrake.rm.hugethings";

        static HugeThingsStartup()
        {
            new Harmony(HarmonyId).PatchAll(typeof(HugeThingsStartup).Assembly);
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
    }
}
