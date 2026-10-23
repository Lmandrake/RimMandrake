using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
    // Owner ruling 2026-10-06 23:34 (typed): "I actually don't mind very small amounts of Shokkweave appearing in the
    // stock of the Wildsteam faction, and even more rare ones in the Hutt's." The material is vanilla Hyperweave,
    // which the free Webwork mod (mandrake.rm.webwork) relabels "thrixweave" and strips from traders by setting its
    // tradeability to Sellable, so every vanilla StockGenerator refuses it (TraderCanSell() false). This generator is
    // the campaign route back: it names Hyperweave itself, rolls `chance` per stock generation and builds the Thing
    // directly, so the strip stays intact for every other trader.
    //
    // Ported unchanged in behaviour from mandrake.rut.shokkweaveeconomy (StockGenerator_RareShokkweave) when that mod
    // was cut (owner, Biome card 5 by card, 2026-10-22). Pure roll and clamp: RUT_RareThrixweaveKernel, below.
    public class RUT_StockGenerator_RareThrixweave : StockGenerator
    {
        public float chance = 0.1f;

        public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(RUT_RareThrixweaveKernel.WeaveDefName);
            if (def == null || !RUT_RareThrixweaveKernel.Stocks(chance, Rand.Value))
            {
                yield break;
            }
            int count = RUT_RareThrixweaveKernel.Count(RandomCountOf(def), def.stackLimit);
            if (count <= 0)
            {
                yield break;
            }
            Thing t = ThingMaker.MakeThing(def);
            t.stackCount = count;
            yield return t;
        }

        public override bool HandlesThingDef(ThingDef thingDef)
        {
            return thingDef != null && RUT_RareThrixweaveKernel.Handles(thingDef.defName);
        }

        public override Tradeability TradeabilityFor(ThingDef thingDef)
        {
            return HandlesThingDef(thingDef) ? Tradeability.All : Tradeability.None;
        }
    }

    // Engine-free decisions of RUT_StockGenerator_RareThrixweave, so a selftest can drive them without the game.
    public static class RUT_RareThrixweaveKernel
    {
        public const string WeaveDefName = "Hyperweave";

        // A stock roll succeeds when the uniform draw lands strictly below the chance (Rand.Value is [0,1)).
        public static bool Stocks(float chance, float roll)
        {
            return roll < chance;
        }

        public static int Count(int rolled, int stackLimit)
        {
            return System.Math.Min(rolled, stackLimit);
        }

        public static bool Handles(string defName)
        {
            return defName == WeaveDefName;
        }
    }
}
