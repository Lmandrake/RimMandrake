using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §3.1-§3.3, §10 step 5. Injected into every qualifying ThingDef by
    // CompInjector_Deepfire.cs (Dub's Paint Shop's PaintableDefsInit pattern
    // the spec names) — never added by hand in a def's own XML.
    public class CompProperties_Deepfire : CompProperties
    {
        public CompProperties_Deepfire()
        {
            compClass = typeof(CompDeepfire);
        }
    }

    public class CompDeepfire : ThingComp
    {
        public const int MaxCoats = 3;

        public int coats;

        // DEEPFIRE_FIRSTCOAT_BONUS_1, spec §3.5: "Applied once, on the first
        // coat only... Scribed so removal-and-reapply cannot farm it."
        // RemoveAllCoats() below deliberately does NOT reset this -- the
        // quality bump it gates (DeepfireFirstCoatBonus.Apply) is permanent
        // and cumulative, unlike the Beauty StatPart bonus (RM_StatPart_Deepfire),
        // which is stateless and re-derives from `coats > 0` every time it's
        // asked for, so it needs no flag of its own.
        public bool bonusApplied;

        public CompProperties_Deepfire Props => (CompProperties_Deepfire)props;

        // DEEPFIRE_MOD_SETTINGS_1, spec §7 "maxCoats ... the slider cannot
        // exceed it": MaxCoats (3) is the architecture ceiling (CoatRadius/
        // CoatIntensity are sized for it); LuminousPigmentSettings.maxCoats
        // is a runtime cap that can only ever lower it, never raise it.
        public bool CanAddCoat => RM_DeepfireRules.CanAddCoat(coats, MaxCoats, LuminousPigmentSettings.maxCoats);

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            RefreshLight();
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            MapComponent_DeepfireLights.Get(map)?.DeregisterThingLight(parent);
            base.PostDeSpawn(map, mode);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref coats, "deepfireCoats", 0);
            Scribe_Values.Look(ref bonusApplied, "deepfireBonusApplied", false);
        }

        // ThingWithComps.Notify_ColorChanged() (Verse/ThingWithComps.cs)
        // already calls this on every comp whenever a Building's paint or a
        // CompColorable's colour changes -- vanilla dye, Dub's Paint Shop,
        // Character Editor and Self Dyeing all end there (spec §3.1), so no
        // Harmony patch is needed for "paint it afterwards -> glow follows".
        public override void Notify_ColorChanged()
        {
            base.Notify_ColorChanged();
            RefreshLight();
        }

        // DEEPFIRE_WORN_GLOW_1, spec §3.4: worn/equipped gear lights its
        // wearer through ONE per-pawn proxy (MapComponent_DeepfireLights.Worn.cs).
        // ThingWithComps forwards Notify_Equipped/Unequipped to every comp for
        // both apparel (Pawn_ApparelTracker) and equipment
        // (Pawn_EquipmentTracker) -- RimSage Verse/ThingWithComps.cs. The item
        // itself is despawned while worn, so its own thing-light is already
        // gone via PostDeSpawn.
        public override void Notify_Equipped(Pawn pawn)
        {
            base.Notify_Equipped(pawn);
            if (coats > 0) MapComponent_DeepfireLights.MarkWornDirty(pawn);
        }

        public override void Notify_Unequipped(Pawn pawn)
        {
            base.Notify_Unequipped(pawn);
            if (coats > 0) MapComponent_DeepfireLights.MarkWornDirty(pawn);
        }

        public override void Notify_WearerDied()
        {
            base.Notify_WearerDied();
            if (coats > 0) MapComponent_DeepfireLights.MarkWornDirty(WornGlowUtility.WearerOf(parent));
        }

        private void RefreshWearer()
        {
            Pawn wearer = WornGlowUtility.WearerOf(parent);
            if (wearer != null) MapComponent_DeepfireLights.MarkWornDirty(wearer);
        }

        public void AddCoat()
        {
            if (!CanAddCoat) return;

            bool firstCoat = RM_DeepfireRules.IsFirstCoat(coats, bonusApplied);

            // DEEPFIRE_FIRSTCOAT_BONUS_1, spec §3.5: "Stacks split before the
            // bump (AllowStackWith needs equal quality)." The quality bump
            // is cumulative, so bumping a stacked art item's shared Thing
            // would either bump the whole stack at once or desync it from
            // CompQuality.AllowStackWith. Split one unit off, place it
            // (so it is Spawned before its own AddCoat runs and can light
            // normally), and let its own fresh CompDeepfire (stackCount 1,
            // coats 0, bonusApplied false) take the coat instead -- the rest
            // of the original stack is untouched. In practice every
            // CompArt/CompQuality def this mod's injector targets ships
            // stackLimit 1 already, so this branch is a defensive guard, not
            // an expected path.
            if (firstCoat && parent.stackCount > 1 && DeepfireFirstCoatBonus.IsArtItem(parent))
            {
                Thing split = parent.SplitOff(1);
                if (parent.Spawned && parent.Map != null)
                {
                    GenPlace.TryPlaceThing(split, parent.Position, parent.Map, ThingPlaceMode.Near);
                }
                split.TryGetComp<CompDeepfire>()?.AddCoat();
                return;
            }

            coats++;
            RefreshLight();

            if (firstCoat)
            {
                DeepfireFirstCoatBonus.Apply(parent);
                bonusApplied = true;
                // DEEPFIRE_GOD_BRIDGE_DELTAS_1, spec §5.2: the gods react to
                // the act, once per thing (the same bonusApplied latch).
                DeepfireGodDeltas.OnFirstCoat(parent);
            }
        }

        // Spec §3.3: "clears coats (no refund)". bonusApplied is untouched
        // (see its own comment) -- stripping the coating never un-bumps an
        // art item's quality, and never re-arms the one-time bump either.
        public void RemoveAllCoats()
        {
            if (coats == 0) return;
            coats = 0;
            RefreshLight();
        }

        public void RefreshLight()
        {
            if (parent == null) return;
            if (!parent.Spawned)
            {
                RefreshWearer(); // worn/equipped: the wearer's proxy carries it
                return;
            }
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(parent.Map);
            if (mc == null) return;

            if (coats <= 0)
            {
                mc.DeregisterThingLight(parent);
                return;
            }

            Color color = DeepfireColorUtility.GlowColorFor(parent.DrawColor, coats);
            float radius = DeepfireColorUtility.RadiusForCoats(coats);
            mc.RegisterThingLight(parent, color, radius);
        }
    }
}
