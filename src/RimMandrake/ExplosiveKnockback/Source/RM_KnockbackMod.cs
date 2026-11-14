using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>Opt-in tag (plan step 2, dl_closed_means_hidden): put on a building def to make it a CLOSED container — goods
    /// on its cells are never thrown or blast-damaged, and the container itself is thrown whole. Storage whose def hides its
    /// contents (a `showContents` false field, LWM's Deep Storage) needs no tag. Never on a def that draws its contents
    /// (owner 2026-11-12: "Anything that draws its contents is open"): a shelf, a hopper, a drawing locker is open.</summary>
    public class RM_KnockbackClosedStorage : DefModExtension
    {
    }

    /// <summary>A DamageDef's throw strength (design §3.1). Bomb ships 1.0, Flame 0.5; EMP, Smoke, Extinguish and
    /// ToxGas ship an explicit 0. Any other harmful explosion throws at the unpatched-harmful percent (default 100).
    /// maxThrowCells: this blast's own maximum throw (cells); 0 = the global "Maximum throw distance".
    /// impactFactor: scales wall / pawn / door impact damage for this blast (0 = no impact: an arrest tool).
    /// creatureMassLimitOverride: replaces the global creature mass limit (kg) for this blast (0 = unset); a living pawn
    /// heavier than it stays, so the grav-ram's 216 throws a rhino (180 kg) and never a thrumbo (240).
    /// refDamage: on a DamageDef only, this type's reference damage for blast power (0 = unset: the def's defaultDamage);
    /// a blast of this type at refDamage throws at its plain force, twice that damage twice as hard.
    /// Lookup (design §2.1): the explosion's PROJECTILE ThingDef, then its WEAPON ThingDef, then its DamageDef; the first
    /// that carries this extension supplies the whole configuration.</summary>
    public class RM_KnockbackExtension : DefModExtension
    {
        public float force = 1f;
        public int maxThrowCells = 0;
        public float impactFactor = 1f;
        public float creatureMassLimitOverride = 0f;
        public float refDamage = 0f;

        public KbConfig ToConfig()
        {
            return new KbConfig { force = force, ownCap = maxThrowCells, impactFactor = impactFactor, massLimitOverride = creatureMassLimitOverride };
        }
    }

    [DefOf]
    public static class RM_KnockbackDefOf
    {
        public static ThingDef RM_PawnFlyer_Knockback;
        public static ThingDef RM_ThingFlyer_Knockback;

        static RM_KnockbackDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_KnockbackDefOf));
        }
    }

    /// <summary>Mod Settings (design §5). Defaults = the owner's rulings of 2026-10-06 (§11); all off = vanilla.
    /// Nothing here affects worldgen.</summary>
    public class RimMandrakeExplosiveKnockbackSettings : ModSettings
    {
        public static bool enabled = true;
        public static float strength = 1f;
        public static int maxThrowCells = 6;
        public static float ownCapScale = 1f;
        /// <summary>RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS (owner card 2026-11-11, d_c_which_blasts): any damaging explosion with no
        /// knockback extension throws at this percent. Harmless ones (harmsHealth false) never throw.</summary>
        public static float unpatchedHarmfulPercent = 100f;
        public static bool throwDowned = true;
        public static bool throwAnimals = true;
        public static bool throwMechanoids = true;
        /// <summary>Owner card 2026-11-13 ("Cutoff -> A mass limit"): a living pawn heavier than this many kg (the game's Mass
        /// stat: 60 kg x body size plus worn gear) is never thrown. 150 = the old body-size 2.5 line.</summary>
        public static float creatureMassLimit = 150f;
        /// <summary>Owner card 2026-11-13 ("Blast power -> Type x damage"): force x this explosion's damage / its damage type's
        /// reference damage. Off = force ignores damage (what shipped before).</summary>
        public static bool blastPowerFromDamage = true;
        /// <summary>The reference damage, as a percent of each damage type's own normal damage (Bomb 50, Flame 10). 100 = a
        /// blast at its type's normal damage throws exactly as before; 200 = it takes twice the damage to throw as far.</summary>
        public static float blastPowerRefPercent = 100f;
        public static bool throwItems = true;
        public static bool throwCorpses = true;
        public static float lightMassLimit = 75f;
        /// <summary>Owner ruling 2026-11-12 (RIMMANDRAKE_SPARE_THROWN_GOODS_SO_THEY_SCATTER): a stack the blast will throw
        /// takes only this percent of the blast's damage, so the player sees it scatter instead of vanish. 100 = vanilla.</summary>
        public static float thrownGoodsBlastDamagePercent = 25f;
        /// <summary>Same ruling, "worse damage if they then hit a solid object": a thrown stack stopped by a wall, door or
        /// the map edge takes this much Blunt damage per cell of throw it had left. 0 = off.</summary>
        public static float goodsWallImpactPerCell = 10f;
        /// <summary>RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD (owner sitting 2026-11-12 answer 5, "C, wild"): thrown goods fly an
        /// arc in a carrier (RM_ThingFlyer_Knockback), spinning, and rebound off walls. Off = the old instant move.</summary>
        public static bool flyingGoods = true;
        public static float goodsFlightSpeed = 14f;        // cells per second
        public static float goodsArcHeight = 1.2f;         // cells the arc's top is drawn above the ground line
        public static float goodsSpinDegPerTick = 18f;     // 18 = three turns a second
        public static bool goodsRebound = true;
        public static float goodsReboundKeepPercent = 70f; // of the cells left at the hit; rounded down, so a chain ends
        /// <summary>Owner ruling 2026-11-10/11 (RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED): open storage (shelves, hoppers,
        /// tables: anything that draws its contents) gives goods no cover; only a closed container keeps them. On = the old rule, every storage building keeps its goods.</summary>
        public static bool openStorageProtectsGoods = false;
        /// <summary>Owner, 2026-11-12 (RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE): "the whole crate/chest would go
        /// flying a bit, but their contents would remain inside and protected". A blast-hit 1x1 closed container at or under
        /// closedContainerMassLimit (its own mass plus what it holds) is thrown as ONE unit, shorter than loose goods by
        /// mass, its contents riding inside; anything else jolts in place. Contents take no blast damage either way.
        /// Off = containers stay put (contents still kept and protected).</summary>
        public static bool shoveClosedContainers = true;
        public static float closedContainerMassLimit = 250f;
        /// <summary>Vanilla's sealed crates (Building_Crate: ancient, hermetic, security crates) count as closed containers.</summary>
        public static bool vanillaCratesClosed = true;
        /// <summary>RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS (plan step 5, dl_heavy_threshold): a flying stack of at least
        /// heavyGoodsMinMass kg that reaches a person's cell hits them (heavyGoodsDamageMin..Max Blunt, a heavyGoodsStaggerTicks
        /// stun) and stops there; lighter goods fly past.</summary>
        public static bool heavyGoodsKnock = true;
        public static float heavyGoodsMinMass = 10f;
        public static float heavyGoodsDamageMin = 2f;
        public static float heavyGoodsDamageMax = 5f;
        public static int heavyGoodsStaggerTicks = 30;
        /// <summary>RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS (plan step 4): each cell of flammable gas that burns gives a small
        /// burst (radius gasBurstRadius): goods fly at most gasBurstGoodsCells, people are shoved one cell with no damage, at
        /// most once per gasPawnCooldownTicks, shield belts do not stop it, and nothing is damaged (so no pit cover breaks).</summary>
        public static bool gasChain = true;
        public static float gasBurstRadius = 1.9f;
        public static int gasBurstGoodsCells = 2;
        public static int gasPawnCooldownTicks = 120;
        public static bool sandbagsStopThrow = false;
        public static bool impactDamageEnabled = true;
        public static float impactDamagePerCell = 4f;
        public static int landingStunMin = 60;
        public static int landingStunMax = 120;
        public static bool doorsTakeDamage = true;
        public static bool throwIntoPits = true;
        public static bool debugDrawVectors = false;
        public static int recoveryWindowTicks = 120;
        public static bool shieldsAbsorbThrow = true;
        public static float shieldDebitPerForce = 10f;

        /// <summary>Per-request kernel settings for one blast's configuration (never mutates the shared settings).</summary>
        public static KbSettings Kernel(KbConfig c)
        {
            return KbLookup.Apply(Kernel(), c, maxThrowCells, ownCapScale);
        }

        public static KbSettings Kernel(int ownCap = 0)
        {
            return new KbSettings
            {
                globalMultiplier = strength,
                maxCells = RM_KnockbackMath.CapFor(ownCap, maxThrowCells, ownCapScale),
                creatureMassLimit = creatureMassLimit,
                lightMassLimit = lightMassLimit,
                impactEnabled = impactDamageEnabled,
                impactPerCell = impactDamagePerCell,
                sandbagsStop = sandbagsStopThrow,
                intoPits = throwIntoPits,
            };
        }

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref strength, "strength", 1f);
            Scribe_Values.Look(ref maxThrowCells, "maxThrowCells", 6);
            Scribe_Values.Look(ref ownCapScale, "ownCapScale", 1f);
            Scribe_Values.Look(ref unpatchedHarmfulPercent, "unpatchedHarmfulPercent", 100f);
            Scribe_Values.Look(ref throwDowned, "throwDowned", true);
            Scribe_Values.Look(ref throwAnimals, "throwAnimals", true);
            Scribe_Values.Look(ref throwMechanoids, "throwMechanoids", true);
            Scribe_Values.Look(ref creatureMassLimit, "creatureMassLimit", 150f);
            Scribe_Values.Look(ref blastPowerFromDamage, "blastPowerFromDamage", true);
            Scribe_Values.Look(ref blastPowerRefPercent, "blastPowerRefPercent", 100f);
            Scribe_Values.Look(ref throwItems, "throwItems", true);
            Scribe_Values.Look(ref throwCorpses, "throwCorpses", true);
            Scribe_Values.Look(ref lightMassLimit, "lightMassLimit", 75f);
            Scribe_Values.Look(ref thrownGoodsBlastDamagePercent, "thrownGoodsBlastDamagePercent", 25f);
            Scribe_Values.Look(ref goodsWallImpactPerCell, "goodsWallImpactPerCell", 10f);
            Scribe_Values.Look(ref flyingGoods, "flyingGoods", true);
            Scribe_Values.Look(ref goodsFlightSpeed, "goodsFlightSpeed", 14f);
            Scribe_Values.Look(ref goodsArcHeight, "goodsArcHeight", 1.2f);
            Scribe_Values.Look(ref goodsSpinDegPerTick, "goodsSpinDegPerTick", 18f);
            Scribe_Values.Look(ref goodsRebound, "goodsRebound", true);
            Scribe_Values.Look(ref goodsReboundKeepPercent, "goodsReboundKeepPercent", 70f);
            Scribe_Values.Look(ref openStorageProtectsGoods, "openStorageProtectsGoods", false);
            Scribe_Values.Look(ref shoveClosedContainers, "shoveClosedContainers", true);
            Scribe_Values.Look(ref closedContainerMassLimit, "closedContainerMassLimit", 250f);
            Scribe_Values.Look(ref vanillaCratesClosed, "vanillaCratesClosed", true);
            Scribe_Values.Look(ref heavyGoodsKnock, "heavyGoodsKnock", true);
            Scribe_Values.Look(ref heavyGoodsMinMass, "heavyGoodsMinMass", 10f);
            Scribe_Values.Look(ref heavyGoodsDamageMin, "heavyGoodsDamageMin", 2f);
            Scribe_Values.Look(ref heavyGoodsDamageMax, "heavyGoodsDamageMax", 5f);
            Scribe_Values.Look(ref heavyGoodsStaggerTicks, "heavyGoodsStaggerTicks", 30);
            Scribe_Values.Look(ref gasChain, "gasChain", true);
            Scribe_Values.Look(ref gasBurstRadius, "gasBurstRadius", 1.9f);
            Scribe_Values.Look(ref gasBurstGoodsCells, "gasBurstGoodsCells", 2);
            Scribe_Values.Look(ref gasPawnCooldownTicks, "gasPawnCooldownTicks", 120);
            Scribe_Values.Look(ref sandbagsStopThrow, "sandbagsStopThrow", false);
            Scribe_Values.Look(ref impactDamageEnabled, "impactDamageEnabled", true);
            Scribe_Values.Look(ref impactDamagePerCell, "impactDamagePerCell", 4f);
            Scribe_Values.Look(ref landingStunMin, "landingStunMin", 60);
            Scribe_Values.Look(ref landingStunMax, "landingStunMax", 120);
            Scribe_Values.Look(ref doorsTakeDamage, "doorsTakeDamage", true);
            Scribe_Values.Look(ref throwIntoPits, "throwIntoPits", true);
            Scribe_Values.Look(ref debugDrawVectors, "debugDrawVectors", false);
            Scribe_Values.Look(ref recoveryWindowTicks, "recoveryWindowTicks", 120);
            Scribe_Values.Look(ref shieldsAbsorbThrow, "shieldsAbsorbThrow", true);
            Scribe_Values.Look(ref shieldDebitPerForce, "shieldDebitPerForce", 10f);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        private static Vector2 scroll;
        private static float settingsViewHeight = 1100f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 20f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Mod switch", RimMandrake.Shared.SettingScope.Now, new[] { "enabled" }))
            {
                list.CheckboxLabeled("Enable explosive knockback", ref enabled,
                    "Every blast throws pawns, items and corpses near it straight away from its centre. Off: vanilla.");
                list.GapLine();
            }

            if (Group(list, "Throw strength and range", RimMandrake.Shared.SettingScope.Now, new[] { "strength", "maxThrowCells", "ownCapScale", "unpatchedHarmfulPercent", "blastPowerFromDamage", "blastPowerRefPercent" }))
            {
                list.Label("Throw strength: " + strength.ToString("0.00")
                    + "x  (1.0 = a mortar shell beside a person throws them 3 cells)");
                strength = list.Slider(strength, 0f, 3f);
                list.Label("Maximum throw distance: " + maxThrowCells
                    + " cells  (blasts that do not set their own maximum: vanilla and most modded explosions)");
                maxThrowCells = (int)list.Slider(maxThrowCells, 1f, 10f);
                list.Label("Weapons that set their own maximum throw: " + ownCapScale.ToString("0.00")
                    + "x their maximum  (1.0 = as designed, e.g. grav-ram 10 cells, thump cannon 8)");
                ownCapScale = list.Slider(ownCapScale, 0.25f, 2f);
                list.Label("Explosions from other mods with no knockback setting throw at: "
                    + unpatchedHarmfulPercent.ToString("0") + "%");
                unpatchedHarmfulPercent = list.Slider(unpatchedHarmfulPercent, 0f, 100f);
                list.CheckboxLabeled("Bigger blasts throw harder", ref blastPowerFromDamage,
                    "On (the default): a blast's push is its type's strength times its damage over that type's normal damage, so a blast dealing twice the normal damage pushes twice as hard (still capped by the maximum throw). Vanilla grenades, mortars and IEDs all deal the normal 50 and throw as before. Off: damage does not change the push.");
                if (blastPowerFromDamage)
                {
                    list.Label("Normal damage for a full push: " + blastPowerRefPercent.ToString("0")
                        + "% of each damage type's own normal damage  (100% = Bomb 50, fire 10)");
                    blastPowerRefPercent = Mathf.Round(list.Slider(blastPowerRefPercent, 25f, 400f));
                }
                list.GapLine();
            }

            if (Group(list, "What gets thrown", RimMandrake.Shared.SettingScope.Now, new[] { "throwDowned", "throwAnimals", "throwMechanoids", "creatureMassLimit", "throwItems", "throwCorpses", "lightMassLimit", "thrownGoodsBlastDamagePercent", "goodsWallImpactPerCell", "openStorageProtectsGoods", "shoveClosedContainers", "closedContainerMassLimit", "vanillaCratesClosed", "heavyGoodsKnock", "heavyGoodsMinMass", "heavyGoodsDamageMin", "heavyGoodsDamageMax", "heavyGoodsStaggerTicks" }))
            {
                list.CheckboxLabeled("Throw downed pawns", ref throwDowned);
                list.CheckboxLabeled("Throw animals", ref throwAnimals);
                list.CheckboxLabeled("Throw mechanoids", ref throwMechanoids);
                list.Label("Creatures heavier than " + creatureMassLimit.ToString("0")
                    + " kg stay put  (150 kg: a muffalo, 144, flies; a rhino, 180, and a thrumbo, 240, do not)");
                creatureMassLimit = Mathf.Round(list.Slider(creatureMassLimit, 20f, 500f));
                list.CheckboxLabeled("Throw items", ref throwItems);
                list.CheckboxLabeled("Throw corpses", ref throwCorpses);
                list.Label("Items and corpses heavier than " + lightMassLimit.ToString("0") + " kg stay put");
                lightMassLimit = list.Slider(lightMassLimit, 5f, 200f);
                list.Label("Blast damage taken by goods that get thrown: " + thrownGoodsBlastDamagePercent.ToString("0") + "%  (100% = vanilla: fragile goods are destroyed instead of scattering)");
                thrownGoodsBlastDamagePercent = Mathf.Round(list.Slider(thrownGoodsBlastDamagePercent, 0f, 100f));
                list.Label("Thrown goods hitting a wall or door: " + goodsWallImpactPerCell.ToString("0") + " damage per cell of throw left  (0 = off)");
                goodsWallImpactPerCell = Mathf.Round(list.Slider(goodsWallImpactPerCell, 0f, 50f));
                list.CheckboxLabeled("Open shelves and tables protect their goods", ref openStorageProtectsGoods,
                    "Off (the default): goods on open storage fly like goods on the floor; only closed containers (storage that hides its contents, e.g. Deep Storage lockers) keep them. On: every storage building keeps its goods.");
                list.CheckboxLabeled("Blasts throw closed containers whole", ref shoveClosedContainers,
                    "On (the default): a small closed container (a sealed crate, a Deep Storage locker: storage that hides its contents) hit by a blast flies a little as one unit, shorter than loose goods because it is heavier, with its contents inside. Off: it stays put. Its contents never take blast damage either way.");
                list.Label("Closed containers heavier than " + closedContainerMassLimit.ToString("0") + " kg (with their contents) stay put");
                closedContainerMassLimit = Mathf.Round(list.Slider(closedContainerMassLimit, 20f, 1000f));
                list.CheckboxLabeled("Sealed crates count as closed containers", ref vanillaCratesClosed,
                    "On (the default): the game's sealed crates (ancient, hermetic and security crates) are closed containers.");
                list.CheckboxLabeled("Heavy flying goods knock people", ref heavyGoodsKnock,
                    "On (the default): a flying stack that weighs at least the limit below and reaches a person hits them lightly and staggers them, then drops there. Lighter goods fly past.");
                list.Label("Heavy means at least " + heavyGoodsMinMass.ToString("0") + " kg; the hit deals " + heavyGoodsDamageMin.ToString("0") + "-"
                    + heavyGoodsDamageMax.ToString("0") + " blunt and staggers for " + heavyGoodsStaggerTicks + " ticks");
                heavyGoodsMinMass = Mathf.Round(list.Slider(heavyGoodsMinMass, 1f, 75f));
                heavyGoodsDamageMin = Mathf.Round(list.Slider(heavyGoodsDamageMin, 0f, 20f));
                heavyGoodsDamageMax = Mathf.Max(heavyGoodsDamageMin, Mathf.Round(list.Slider(heavyGoodsDamageMax, 0f, 20f)));
                heavyGoodsStaggerTicks = (int)list.Slider(heavyGoodsStaggerTicks, 0f, 180f);
                list.GapLine();
            }

            if (Group(list, "Flying goods", RimMandrake.Shared.SettingScope.Now, new[] { "flyingGoods", "goodsFlightSpeed", "goodsArcHeight", "goodsSpinDegPerTick", "goodsRebound", "goodsReboundKeepPercent" }))
            {
                list.CheckboxLabeled("Thrown goods fly", ref flyingGoods,
                    "On (the default): a thrown stack flies an arc, spinning, and lands where the throw ends. Off: it moves there instantly.");
                list.Label("Flight speed: " + goodsFlightSpeed.ToString("0") + " cells a second");
                goodsFlightSpeed = Mathf.Round(list.Slider(goodsFlightSpeed, 4f, 40f));
                list.Label("Arc height: " + goodsArcHeight.ToString("0.0") + " cells");
                goodsArcHeight = Mathf.Round(list.Slider(goodsArcHeight, 0f, 3f) * 10f) / 10f;
                list.Label("Spin: " + goodsSpinDegPerTick.ToString("0") + " degrees a tick  (0 = no spin)");
                goodsSpinDegPerTick = Mathf.Round(list.Slider(goodsSpinDegPerTick, 0f, 60f));
                list.CheckboxLabeled("Thrown goods rebound off walls", ref goodsRebound,
                    "On (the default): a flying stack that hits a wall, door or the map edge bounces off and flies on with part of the throw it had left.");
                list.Label("Each rebound keeps " + goodsReboundKeepPercent.ToString("0") + "% of the throw left");
                goodsReboundKeepPercent = Mathf.Round(list.Slider(goodsReboundKeepPercent, 0f, 100f));
                list.GapLine();
            }

            if (Group(list, "Impact and landing", RimMandrake.Shared.SettingScope.Now, new[] { "sandbagsStopThrow", "impactDamageEnabled", "impactDamagePerCell", "landingStunMin", "landingStunMax", "recoveryWindowTicks", "doorsTakeDamage", "throwIntoPits" }))
            {
                list.CheckboxLabeled("Sandbags and barricades stop a throw", ref sandbagsStopThrow,
                    "Off (the default): people are thrown over sandbags and barricades.");
                list.CheckboxLabeled("Impact damage on hitting a wall or another pawn", ref impactDamageEnabled);
                list.Label("Impact damage per cell not travelled: " + impactDamagePerCell.ToString("0.0"));
                impactDamagePerCell = list.Slider(impactDamagePerCell, 0f, 15f);
                list.Label("Landing stun: " + landingStunMin + "-" + landingStunMax + " ticks");
                landingStunMin = (int)list.Slider(landingStunMin, 0f, 300f);
                landingStunMax = (int)list.Slider(landingStunMax, 0f, 300f);
                landingStunMax = Mathf.Max(landingStunMin, landingStunMax);
                list.Label("Recovery after a throw: " + recoveryWindowTicks
                    + " ticks after the landing stun ends before the same pawn can be thrown again  (0 = chain throws allowed)");
                recoveryWindowTicks = (int)list.Slider(recoveryWindowTicks, 0f, 600f);
                list.CheckboxLabeled("Doors take impact damage", ref doorsTakeDamage);
                list.CheckboxLabeled("Throw into FlowWorks pits", ref throwIntoPits,
                    "Off: an open pit stops a throw like a wall.");
                list.GapLine();
            }

            if (Group(list, "Burning gas", RimMandrake.Shared.SettingScope.Now, new[] { "gasChain", "gasBurstRadius", "gasBurstGoodsCells", "gasPawnCooldownTicks" }))
            {
                list.CheckboxLabeled("Flammable gas goes off clump by clump", ref gasChain,
                    "On (the default): each cell of flammable gas that catches fire (The Cauldron's vent gas) gives a small burst that scatters goods and shoves people one cell, with no damage. Off: the gas burns without bursts.");
                list.Label("Burst radius: " + gasBurstRadius.ToString("0.0") + " cells; goods fly at most " + gasBurstGoodsCells + " cells");
                gasBurstRadius = Mathf.Round(list.Slider(gasBurstRadius, 0.9f, 4f) * 10f) / 10f;
                gasBurstGoodsCells = (int)list.Slider(gasBurstGoodsCells, 1f, 6f);
                list.Label("A person is shoved by burning gas at most once every " + gasPawnCooldownTicks + " ticks  (120 = 2 seconds)");
                gasPawnCooldownTicks = (int)list.Slider(gasPawnCooldownTicks, 0f, 600f);
                list.GapLine();
            }

            if (Group(list, "Shield belts", RimMandrake.Shared.SettingScope.Now, new[] { "shieldsAbsorbThrow", "shieldDebitPerForce" }))
            {
                list.CheckboxLabeled("Shield belts absorb the throw", ref shieldsAbsorbThrow,
                    "On: a pawn whose shield absorbed the blast is not thrown, and the shield pays extra charge for it (a strong throw can pop it). Off: shields stop the wound, never the shove.");
                list.Label("Extra shield drain per point of throw force: " + shieldDebitPerForce.ToString("0")
                    + " damage-equivalents");
                shieldDebitPerForce = Mathf.Round(list.Slider(shieldDebitPerForce, 0f, 50f));
                list.GapLine();
            }

            if (Prefs.DevMode && Group(list, "Debug", RimMandrake.Shared.SettingScope.Now, new[] { "debugDrawVectors" }))
            {
                list.CheckboxLabeled("Debug: draw throw vectors", ref debugDrawVectors);
                list.GapLine();
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RimMandrakeExplosiveKnockbackSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RimMandrakeExplosiveKnockbackSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class RimMandrakeExplosiveKnockbackMod : Mod
    {
        public static RimMandrakeExplosiveKnockbackSettings Settings;

        public RimMandrakeExplosiveKnockbackMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<RimMandrakeExplosiveKnockbackSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.explosiveknockback"), typeof(RimMandrakeExplosiveKnockbackMod).Assembly, "RimMandrake.ExplosiveKnockback", "RimMandrake.ExplosiveKnockback");
            LongEventHandler.ExecuteWhenFinished(RM_KnockbackCompat.Init);
        }

        public override string SettingsCategory() => "RimMandrake: Explosive Knockback";

        public override void DoSettingsWindowContents(Rect inRect) => Settings.DoWindowContents(inRect);

        public static void Reset()
        {
            RimMandrakeExplosiveKnockbackSettings.enabled = true;
            RimMandrakeExplosiveKnockbackSettings.strength = 1f;
            RimMandrakeExplosiveKnockbackSettings.maxThrowCells = 6;
            RimMandrakeExplosiveKnockbackSettings.ownCapScale = 1f;
            RimMandrakeExplosiveKnockbackSettings.unpatchedHarmfulPercent = 100f;
            RimMandrakeExplosiveKnockbackSettings.throwDowned = true;
            RimMandrakeExplosiveKnockbackSettings.throwAnimals = true;
            RimMandrakeExplosiveKnockbackSettings.throwMechanoids = true;
            RimMandrakeExplosiveKnockbackSettings.creatureMassLimit = 150f;
            RimMandrakeExplosiveKnockbackSettings.blastPowerFromDamage = true;
            RimMandrakeExplosiveKnockbackSettings.blastPowerRefPercent = 100f;
            RimMandrakeExplosiveKnockbackSettings.throwItems = true;
            RimMandrakeExplosiveKnockbackSettings.throwCorpses = true;
            RimMandrakeExplosiveKnockbackSettings.lightMassLimit = 75f;
            RimMandrakeExplosiveKnockbackSettings.thrownGoodsBlastDamagePercent = 25f;
            RimMandrakeExplosiveKnockbackSettings.goodsWallImpactPerCell = 10f;
            RimMandrakeExplosiveKnockbackSettings.flyingGoods = true;
            RimMandrakeExplosiveKnockbackSettings.goodsFlightSpeed = 14f;
            RimMandrakeExplosiveKnockbackSettings.goodsArcHeight = 1.2f;
            RimMandrakeExplosiveKnockbackSettings.goodsSpinDegPerTick = 18f;
            RimMandrakeExplosiveKnockbackSettings.goodsRebound = true;
            RimMandrakeExplosiveKnockbackSettings.goodsReboundKeepPercent = 70f;
            RimMandrakeExplosiveKnockbackSettings.openStorageProtectsGoods = false;
            RimMandrakeExplosiveKnockbackSettings.shoveClosedContainers = true;
            RimMandrakeExplosiveKnockbackSettings.closedContainerMassLimit = 250f;
            RimMandrakeExplosiveKnockbackSettings.vanillaCratesClosed = true;
            RimMandrakeExplosiveKnockbackSettings.heavyGoodsKnock = true;
            RimMandrakeExplosiveKnockbackSettings.heavyGoodsMinMass = 10f;
            RimMandrakeExplosiveKnockbackSettings.heavyGoodsDamageMin = 2f;
            RimMandrakeExplosiveKnockbackSettings.heavyGoodsDamageMax = 5f;
            RimMandrakeExplosiveKnockbackSettings.heavyGoodsStaggerTicks = 30;
            RimMandrakeExplosiveKnockbackSettings.gasChain = true;
            RimMandrakeExplosiveKnockbackSettings.gasBurstRadius = 1.9f;
            RimMandrakeExplosiveKnockbackSettings.gasBurstGoodsCells = 2;
            RimMandrakeExplosiveKnockbackSettings.gasPawnCooldownTicks = 120;
            RimMandrakeExplosiveKnockbackSettings.sandbagsStopThrow = false;
            RimMandrakeExplosiveKnockbackSettings.impactDamageEnabled = true;
            RimMandrakeExplosiveKnockbackSettings.impactDamagePerCell = 4f;
            RimMandrakeExplosiveKnockbackSettings.landingStunMin = 60;
            RimMandrakeExplosiveKnockbackSettings.landingStunMax = 120;
            RimMandrakeExplosiveKnockbackSettings.doorsTakeDamage = true;
            RimMandrakeExplosiveKnockbackSettings.throwIntoPits = true;
            RimMandrakeExplosiveKnockbackSettings.debugDrawVectors = false;
            RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks = 120;
            RimMandrakeExplosiveKnockbackSettings.shieldsAbsorbThrow = true;
            RimMandrakeExplosiveKnockbackSettings.shieldDebitPerForce = 10f;
        }
    }
}
