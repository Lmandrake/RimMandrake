using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_FIRSTCOAT_BONUS_1, spec §3.5 "everything else": walls,
    // furniture, apparel, weapons -- not art items (CompArt present; those
    // get DeepfireFirstCoatBonus's quality bump instead) and not floors
    // (terrain has no comps to hang a StatPart off; the floor bonus is
    // DEEPFIRE_FLOOR_PAINT_1's own Harmony postfixes on BeautyUtility.CellBeauty
    // / RoomStatWorker_Beauty.GetScore). XML-patched onto
    // StatDefOf.Beauty/parts (Patches/DeepfireBeautyStatPart.xml) via
    // PatchOperationAdd, which appends -- so this runs AFTER vanilla's own
    // StatPart_Quality and StatPart_ContentsBeauty in RimWorld/StatWorker.cs
    // FinalizeValue's part loop, meaning `val` at the top of TransformValue
    // ("baseBeauty") already has quality scaling folded in. That matches the
    // spec's own worked example: a Good-quality steel bed (beauty ~6 WITH
    // quality already applied) gets +3 + 0.25*6 = +4.5, not 0.25 of the
    // unscaled base.
    //
    // Stateless by design: reads CompDeepfire.coats live off the thing every
    // time the stat is computed, so "remove + reapply does not re-bump"
    // holds for free -- there is nothing to accumulate, TransformValue just
    // recomputes the same additive bonus from the thing's current coat
    // state on every call.
    public class RM_StatPart_Deepfire : StatPart
    {
        // XML-declared defaults (Patches/DeepfireBeautyStatPart.xml), kept
        // for schema validity -- DEEPFIRE_MOD_SETTINGS_1 reads the live
        // LuminousPigmentSettings.beautyFlat/beautyPct/beautySizeCap in
        // BonusFor below instead of these fields, so a settings change takes
        // effect immediately with no def rewrite.
        public float beautyFlat = DeepfirePaintDefaults.FirstCoatBeautyFlat;
        public float beautyPct = DeepfirePaintDefaults.FirstCoatBeautyPct;

        // Best-effort cache of the baseBeauty TransformValue last saw for a
        // given Thing, purely so ExplanationPart (called by
        // RimWorld/StatWorker.cs GetAdditionalOffsetsAndFactorsExplanation
        // with a StatRequest only -- no running `val`) can show the same
        // number the stat card's total was built from, instead of treating
        // baseBeauty as 0. The stat card always calls StatWorker.GetValue
        // (which runs TransformValue for every part, including this one)
        // immediately before asking for the explanation text, so the cache
        // is fresh by the time it is read. ConditionalWeakTable so a
        // destroyed/GC'd Thing never leaks an entry.
        private static readonly ConditionalWeakTable<Thing, object> lastBaseValue = new ConditionalWeakTable<Thing, object>();

        public override void TransformValue(StatRequest req, ref float val)
        {
            if (!Applies(req)) return;
            if (req.Thing != null)
            {
                lastBaseValue.Remove(req.Thing);
                lastBaseValue.Add(req.Thing, val);
            }
            val += BonusFor(req.Thing, val);
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (!Applies(req)) return null;
            float baseBeauty = 0f;
            if (req.Thing != null && lastBaseValue.TryGetValue(req.Thing, out object boxed)) baseBeauty = (float)boxed;
            float bonus = BonusFor(req.Thing, baseBeauty);
            return "Deepfire lacquer: +" + bonus.ToString("0.##");
        }

        private float BonusFor(Thing thing, float baseBeauty)
        {
            int area = thing != null ? System.Math.Max(1, thing.def.size.x * thing.def.size.z) : 1;
            float sizeFactor = Mathf.Min(area, LuminousPigmentSettings.beautySizeCap);
            return LuminousPigmentSettings.beautyFlat * sizeFactor + LuminousPigmentSettings.beautyPct * baseBeauty;
        }

        private static bool Applies(StatRequest req)
        {
            Thing thing = req.Thing;
            if (thing == null) return false;
            CompDeepfire comp = thing.TryGetComp<CompDeepfire>();
            if (comp == null || comp.coats <= 0) return false;
            if (DeepfireFirstCoatBonus.IsArtItem(thing)) return false; // art items: quality bump instead, not this
            return true;
        }
    }
}
