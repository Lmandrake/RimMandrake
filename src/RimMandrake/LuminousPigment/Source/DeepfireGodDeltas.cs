using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_GOD_BRIDGE_DELTAS_1, spec §5.2 / §10 step 10: the coat, worn,
    // statue and sold rows of the god-delta table. Every delta goes through
    // NinefoldDeltaBridge (reflection; Ninefold absent = silent no-op, and
    // the godsReact setting gates it there).
    //
    //   first coat, building/floor/item   every god +Like, the trio +Adore,
    //                                     Ishko -Ishko            (deepfire.coat)
    //   first coat, apparel/weapon        as above, Ishko -Adore  (deepfire.worn)
    //   first coat, a god's statue        that god +Statue (Ishko's own idol:
    //                                     Ishko -Statue); every other god
    //                                     +Like, Ishko -Ishko     (deepfire.statue)
    //   a deal that sells/gifts deepfire  Mob'Unloo +Adore, once per deal
    //                                                             (deepfire.sold)
    //
    // "First coat" is the same event DeepfireFirstCoatBonus uses
    // (CompDeepfire.AddCoat with coats 0 and bonusApplied false), so stripping
    // and re-coating a thing never re-fires it. Floor cells fire when a cell
    // goes 0 -> 1 coats.
    //
    // Spec §5.2 anti-pinning rule: after godDeltaDiminishAfter first-coat
    // events on the same def (ThingDef, or the floor's TerrainDef) in one
    // game, every delta of that event shrinks to DiminishedMagnitude, sign
    // kept. The count lives in GameComponent_Deepfire (Scribed).
    //
    // Not built here: spec §5.2's "coated god-statue destroyed" row (it is
    // not in this item's Build list).
    public static class DeepfireGodDeltas
    {
        public const string Ishko = "Ishko";
        public const string MobUnloo = "MobUnloo";

        // Spec §5 ruling (card 2): "the trade/craft trio -- Mob'Unloo, Rekko,
        // Zizzik -- adore it".
        public static readonly string[] Trio = { "MobUnloo", "Rekko", "Zizzik" };

        // Spec §5.2: "coats on the same def after the first ten per game
        // decay to +1".
        public const float DiminishedMagnitude = 1f;

        public const string ReasonCoat = "deepfire.coat";
        public const string ReasonWorn = "deepfire.worn";
        public const string ReasonStatue = "deepfire.statue";
        public const string ReasonSold = "deepfire.sold";

        public const string DeepfireDefName = "RM_Deepfire";

        private const string ThingKeyPrefix = "thing:";
        private const string FloorKeyPrefix = "floor:";

        public static string KeyFor(ThingDef def) => ThingKeyPrefix + def.defName;
        public static string KeyFor(TerrainDef def) => FloorKeyPrefix + def.defName;

        // The god a statue def is tagged with (spec §5.3), or null when the
        // def carries no RM_DeepfireGodExtension / names no real god.
        public static string StatueGodOf(Thing thing)
        {
            string god = thing?.def?.GetModExtension<DeepfireGodExtension>()?.god;
            return NinefoldDeltaBridge.IsGod(god) ? god : null;
        }

        public static bool IsWornClass(Thing thing)
        {
            return thing.def.IsApparel || thing.def.IsWeapon;
        }

        // CompDeepfire.AddCoat, first coat only.
        public static void OnFirstCoat(Thing thing)
        {
            if (thing == null || !NinefoldDeltaBridge.Available) return;
            string statueGod = StatueGodOf(thing);
            Dictionary<string, float> table;
            string reason;
            if (statueGod != null)
            {
                table = StatueTable(statueGod);
                reason = ReasonStatue;
            }
            else if (IsWornClass(thing))
            {
                table = CoatTable(LuminousPigmentSettings.godDeltaAdore);
                reason = ReasonWorn;
            }
            else
            {
                table = CoatTable(LuminousPigmentSettings.godDeltaIshko);
                reason = ReasonCoat;
            }
            Deliver(table, KeyFor(thing.def), reason);
        }

        // MapComponent_DeepfireLights.AddFloorCoat, cell going 0 -> 1.
        public static void OnFirstFloorCoat(TerrainDef floor)
        {
            if (floor == null || !NinefoldDeltaBridge.Available) return;
            Deliver(CoatTable(LuminousPigmentSettings.godDeltaIshko), KeyFor(floor), ReasonCoat);
        }

        public static void OnDeepfireSold()
        {
            NinefoldDeltaBridge.ApplyDelta(MobUnloo, LuminousPigmentSettings.godDeltaAdore, ReasonSold);
        }

        // Every god +Like, the trio +Adore, Ishko -ishkoPenalty.
        public static Dictionary<string, float> CoatTable(float ishkoPenalty)
        {
            return RM_DeepfireRules.CoatTable(NinefoldDeltaBridge.GodNames, Trio, Ishko, ishkoPenalty,
                LuminousPigmentSettings.godDeltaAdore, LuminousPigmentSettings.godDeltaLike);
        }

        // Spec §5.2: "that god +Large; all other gods +Small; Ishko's own
        // idol: Ishko -Large". Ishko keeps his standing dislike on another
        // god's idol (the §5 ruling: "Ishko dislikes it").
        public static Dictionary<string, float> StatueTable(string statueGod)
        {
            return RM_DeepfireRules.StatueTable(NinefoldDeltaBridge.GodNames, statueGod, Ishko, LuminousPigmentSettings.godDeltaStatue,
                LuminousPigmentSettings.godDeltaIshko, LuminousPigmentSettings.godDeltaLike);
        }

        private static void Deliver(Dictionary<string, float> table, string defKey, string reason)
        {
            int prior = GameComponent_Deepfire.NoteGodCoatEvent(defKey);
            foreach (KeyValuePair<string, float> kv in table)
            {
                float amount = kv.Value;
                if (amount == 0f) continue;
                amount = RM_DeepfireRules.Diminish(amount, prior, LuminousPigmentSettings.godDeltaDiminishAfter, DiminishedMagnitude);
                NinefoldDeltaBridge.ApplyDelta(kv.Key, amount, reason);
            }
        }

        // A deepfire good: the pigment itself, or anything carrying at least
        // one coat (minified furniture looked through).
        public static bool IsDeepfireGood(Thing thing)
        {
            Thing inner = thing?.GetInnerIfMinified();
            if (inner == null) return false;
            if (inner.def.defName == DeepfireDefName) return true;
            CompDeepfire comp = inner.TryGetComp<CompDeepfire>();
            return comp != null && comp.coats > 0;
        }

        // True when the deal moves at least one deepfire good from the colony
        // to the trader (a sale, or a gift in gift mode). Walks thingsColony
        // in list order up to the count, exactly the order
        // TransferableUtility.TransferNoSplit hands them over (RimSage
        // RimWorld/TransferableUtility.cs), so a mixed stack of coated and
        // plain things credits only what actually leaves.
        public static bool DealSellsDeepfire(List<Tradeable> tradeables)
        {
            if (tradeables == null) return false;
            foreach (Tradeable t in tradeables)
            {
                if (t == null || t.ActionToDo != TradeAction.PlayerSells) continue;
                int left = t.CountToTransferToDestination;
                foreach (Thing thing in t.thingsColony)
                {
                    if (left <= 0) break;
                    if (IsDeepfireGood(thing)) return true;
                    left -= thing.stackCount;
                }
            }
            return false;
        }
    }

    // Spec §5.2 "sold or gifted ... via a small postfix beside Ninefold's own
    // Patch_TradeCompleted". TradeDeal.TryExecute (RimSage RimWorld/
    // TradeDeal.cs) is the one choke point for both trade and gift mode;
    // ResolveTrade empties the counts and Reset() clears the list, so the
    // deal is read in the PREFIX and paid in the postfix only when it
    // really went through (__result && actuallyTraded -- Ninefold's own
    // gate).
    [HarmonyPatch(typeof(TradeDeal), nameof(TradeDeal.TryExecute))]
    [RimMandrake.Shared.PatchFeature("Deepfire gods react", typeof(LuminousPigmentSettings), "godsReact")]
    public static class Patch_TradeDeal_DeepfireSold
    {
        [HarmonyPrefix]
        public static void Prefix(List<Tradeable> ___tradeables, out bool __state)
        {
            __state = LuminousPigmentSettings.godsReact && DeepfireGodDeltas.DealSellsDeepfire(___tradeables);
        }

        [HarmonyPostfix]
        public static void Postfix(bool __result, bool actuallyTraded, bool __state)
        {
            if (__state && __result && actuallyTraded) DeepfireGodDeltas.OnDeepfireSold();
        }
    }
}
