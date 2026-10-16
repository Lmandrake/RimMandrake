using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS (owner 2026-10-16; approved by card the same day: material colour
    /// on the TRIM only, body keeps its painted style, liquid shows in the masked window). A bottle, bucket or barrel wears
    /// one of the four looks as a vanilla ThingStyleDef (Defs/LiquidTypes/ThingDefs/RM_LiquidContainerStyles.xml), stored
    /// per thing by CompStyleable. The look is chosen on the crafting bill (Patch_ContainerBill_StyleButton; vanilla
    /// Toils_Recipe hands bill.style to the product), defaults from the faction's tech when nobody chose
    /// (RM_CompContainerStyle), and rides every chain step (MakeContainer -> CarryStyle). Rules: RM_ContainerStyleMath.</summary>
    public static class RM_ContainerStyles
    {
        private static readonly Dictionary<string, ThingStyleDef> cache = new Dictionary<string, ThingStyleDef>();

        public static string SizeOf(ThingDef def)
        {
            RM_BottledLiquidExtension ext = def?.GetModExtension<RM_BottledLiquidExtension>();
            return ext == null ? null : ext.size.ToString();
        }

        public static bool IsContainer(ThingDef def) => def != null && def.HasComp(typeof(RM_CompContainerStyle));

        /// <summary>The ThingStyleDef for this container def in this look, or null (not a container, unknown look).</summary>
        public static ThingStyleDef StyleFor(ThingDef def, string look)
        {
            string size = SizeOf(def);
            if (size == null || !RM_ContainerStyleMath.IsLook(look))
            {
                return null;
            }
            string name = RM_ContainerStyleMath.StyleDefName(size, look);
            if (!cache.TryGetValue(name, out ThingStyleDef sd))
            {
                sd = DefDatabase<ThingStyleDef>.GetNamedSilentFail(name);
                cache[name] = sd;
            }
            return sd;
        }

        public static string LookOf(Thing t) => RM_ContainerStyleMath.LookOfStyleDefName(t?.StyleDef?.defName);

        public static string LookForFaction(Faction f) =>
            RM_ContainerStyleMath.LookForTech(f?.def?.techLevel.ToString());

        /// <summary>Give an unstyled container its faction's default look. True when it wrote one.</summary>
        public static bool ApplyDefault(Thing t, Faction f)
        {
            if (t == null || t.StyleDef != null || !IsContainer(t.def))
            {
                return false;
            }
            ThingStyleDef sd = StyleFor(t.def, LookForFaction(f));
            if (sd == null)
            {
                return false;
            }
            t.StyleDef = sd;
            return true;
        }

        /// <summary>A chain step (fill, drink, wash, pour, revert) keeps the look: the new container wears the same look in
        /// its own size's style. An unstyled source leaves the new one to its default.</summary>
        public static void CarryStyle(Thing from, Thing made)
        {
            string look = LookOf(from);
            if (look == null || made == null)
            {
                return;
            }
            ThingStyleDef sd = StyleFor(made.def, look);
            if (sd != null)
            {
                made.StyleDef = sd;
            }
        }
    }

    /// <summary>A container's two tint channels. DrawColor (mask red, the liquid window) comes from
    /// RM_CompContainerMaterial.ForceColor; this adds DrawColorTwo (mask green, the trim) = the material's colour, so a
    /// steel bottle's cap is steel and a wooden barrel's hoops are wood while the painted body never changes.</summary>
    public class RM_LiquidContainer : ThingWithComps
    {
        public override Color DrawColorTwo
        {
            get
            {
                if (Stuff != null)
                {
                    return def.GetColorForStuff(Stuff);
                }
                return base.DrawColorTwo;
            }
        }
    }

    /// <summary>The look's lifecycle on one container: never merge two looks into one stack, keep the look when a stack is
    /// split, and give anything nobody styled its faction's look (trader stock by the trader's faction; anything that
    /// appears on a map by the faction that owns the map, else the thing's own faction).</summary>
    public class RM_CompContainerStyle : ThingComp
    {
        public override bool AllowStackWith(Thing other) =>
            RM_ContainerStyleMath.MayStack(RM_ContainerStyles.LookOf(parent), RM_ContainerStyles.LookOf(other));

        public override void PostSplitOff(Thing piece)
        {
            base.PostSplitOff(piece);
            if (piece != null && piece != parent && parent.StyleDef != null)
            {
                piece.StyleDef = parent.StyleDef;
            }
        }

        public override void PostPostGeneratedForTrader(TraderKindDef trader, PlanetTile forTile, Faction forFaction)
        {
            base.PostPostGeneratedForTrader(trader, forTile, forFaction);
            RM_ContainerStyles.ApplyDefault(parent, forFaction);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (parent.StyleDef == null)
            {
                Faction f = parent.Faction ?? parent.Map?.ParentFaction ?? Faction.OfPlayerSilentFail;
                RM_ContainerStyles.ApplyDefault(parent, f);
            }
        }
    }

    /// <summary>The Style button on a container crafting bill. Vanilla only offers a bill style in classic ideoligion mode
    /// and only for ideoligion style categories, which list none of ours, so the button is ours: it writes bill.style and
    /// clears globalStyle, and vanilla Toils_Recipe.FinishRecipeAndStartStoringProduct hands that style to the product.
    /// Drawn at the bottom of the bill dialog's left column (vanilla's own style button, classic mode only, sits above it).</summary>
    [RimMandrake.Shared.PatchFeature("Container style button on crafting bills")]
    [HarmonyPatch(typeof(Dialog_BillConfig), nameof(Dialog_BillConfig.DoWindowContents))]
    internal static class Patch_ContainerBill_StyleButton
    {
        private static readonly AccessTools.FieldRef<Dialog_BillConfig, Bill_Production> billRef =
            AccessTools.FieldRefAccess<Dialog_BillConfig, Bill_Production>("bill");

        internal static string ButtonLabel(Bill_Production bill)
        {
            string look = RM_ContainerStyleMath.LookOfStyleDefName(bill.globalStyle ? null : bill.style?.defName);
            return "Style: " + (look ?? "faction default");
        }

        internal static List<FloatMenuOption> Menu(Bill_Production bill, ThingDef product)
        {
            var opts = new List<FloatMenuOption>
            {
                new FloatMenuOption("faction default (by tech level)", () =>
                {
                    bill.style = null;
                    bill.globalStyle = true;
                    bill.graphicIndexOverride = null;
                })
            };
            foreach (string look in RM_ContainerStyleMath.Looks)
            {
                ThingStyleDef sd = RM_ContainerStyles.StyleFor(product, look);
                if (sd == null)
                {
                    continue;
                }
                string l = look;
                opts.Add(new FloatMenuOption(l.ToLower(), () =>
                {
                    bill.style = sd;
                    bill.globalStyle = false;
                    bill.graphicIndexOverride = null;
                }, sd.UIIcon, Color.white));
            }
            return opts;
        }

        private static void Postfix(Dialog_BillConfig __instance, Rect inRect)
        {
            Bill_Production bill = billRef(__instance);
            ThingDef product = bill?.recipe?.ProducedThingDef;
            if (product == null || !RM_ContainerStyles.IsContainer(product))
            {
                return;
            }
            float width = (int)((inRect.width - 34f) / 3f);
            Rect r = new Rect(inRect.x, inRect.yMax - 34f, width, 30f);
            if (Widgets.ButtonText(r, ButtonLabel(bill)))
            {
                Find.WindowStack.Add(new FloatMenu(Menu(bill, product)));
            }
            TooltipHandler.TipRegion(r, "Which of the four looks these containers are made in: scrapper, industrial, "
                + "modern or futuristic. The material still colours the cap, handle or hoops; the liquid shows in the window.");
        }
    }
}
