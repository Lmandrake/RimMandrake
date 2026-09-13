using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD_MECHANICS_1 S2 spike (scald_kit_spec.md "the steam-catch").
    // Generic vent/geyser-locked resource comp: crib of RimWorld/
    // CompPowerPlantSteam.cs (verified, decompile) — that comp finds its
    // Building_SteamGeyser via `parent.Map.thingGrid.ThingAt(parent.Position,
    // ThingDefOf.SteamGeyser)` every CompTick and only sprays while a geyser
    // is actually under it (never errors when the placement guard is somehow
    // bypassed). This comp follows the same "look under yourself, do nothing
    // if absent" shape rather than caching a reference that could go stale
    // across a save/load or a griefed deconstruct-and-rebuild.
    //
    // requiredThingAtPosition defaults to ThingDefOf.SteamGeyser so this
    // compiles and is usable standalone before S4's RUT_ScaldVent (an
    // INVENTED non-buildable spawned variant) exists; S4's build repoints it
    // per-building via XML the day that def ships. Real placement gating is
    // the PlaceWorker's job (crib PlaceWorker_OnSteamGeyser, confirmed real
    // — RimWorld/PlaceWorker_OnSteamGeyser.cs) in the ThingDef XML; this comp
    // only refuses to PRODUCE off its required thing, defense in depth for
    // the case a colonist somehow deconstructs the vent from under a built
    // condenser without deconstructing the condenser too.
    //
    // Ban 1 patrol (never potable): this comp has no bill, no ingredient
    // input, and no recipe — it manufactures `outputDef` from nothing but
    // standing on the named vent, exactly the "free, endless distilled
    // water" the sheet describes for S2. It is not itself a drink route;
    // whether its output stacks are drinkable is `outputDef`'s own property,
    // decided by owner card 2 (item-water v1 default).
    public class CompProperties_ResourceCondenser : CompProperties
    {
        /// <summary>What one cycle yields. v1 default per card 2: item water
        /// (e.g. WaterPurified/whatever the liquid-types roster ships as the
        /// item-water stack); the DBH pipe-network variant is a Mod Settings
        /// toggle owed to the full build, not this comp.</summary>
        public ThingDef outputDef;

        /// <summary>Stack size produced per completed cycle. INVENTED,
        /// kit-spec starting value: 25 water units/day equivalent.</summary>
        public int outputCountPerCycle = 25;

        /// <summary>Ticks per production cycle. INVENTED default: one day
        /// (60000 ticks), matching the "25 units/day" framing above.</summary>
        public int cycleTicks = 60000;

        /// <summary>The vent/geyser ThingDef this condenser must sit on to
        /// produce at all — mirrors CompPowerPlantSteam's ThingDefOf.SteamGeyser
        /// lookup. Defaults to vanilla SteamGeyser; S4 repoints to
        /// RUT_ScaldVent once that def ships.</summary>
        public ThingDef requiredThingAtPosition = ThingDefOf.SteamGeyser;

        public CompProperties_ResourceCondenser()
        {
            compClass = typeof(RM_CompResourceCondenser);
        }
    }

    public class RM_CompResourceCondenser : ThingComp
    {
        private int ticksSinceCycleStart;

        public CompProperties_ResourceCondenser Props => (CompProperties_ResourceCondenser)props;

        // True only while the required vent/geyser is actually under this
        // building right now — re-checked every tick like CompPowerPlantSteam
        // rather than cached, so a deconstructed vent silently stops
        // production instead of erroring.
        public bool OnRequiredVent
        {
            get
            {
                Map map = parent.Map;
                if (map == null || Props.requiredThingAtPosition == null)
                {
                    return false;
                }
                Thing thing = map.thingGrid.ThingAt(parent.Position, Props.requiredThingAtPosition);
                return thing != null;
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!OnRequiredVent)
            {
                ticksSinceCycleStart = 0; // no free progress banked while off-vent
                return;
            }

            ticksSinceCycleStart++;
            if (ticksSinceCycleStart < Props.cycleTicks)
            {
                return;
            }

            ticksSinceCycleStart = 0;
            ProduceCycle();
        }

        private void ProduceCycle()
        {
            if (Props.outputDef == null || parent.Map == null)
            {
                return;
            }
            Thing output = ThingMaker.MakeThing(Props.outputDef);
            output.stackCount = Props.outputCountPerCycle;
            GenPlace.TryPlaceThing(output, parent.Position, parent.Map, ThingPlaceMode.Near);
        }

        public override string CompInspectStringExtra()
        {
            if (!OnRequiredVent)
            {
                return "RM_CondenserOffVent".Translate();
            }
            float progress = Props.cycleTicks > 0 ? (float)ticksSinceCycleStart / Props.cycleTicks : 0f;
            return "RM_CondenserProgress".Translate() + ": " + progress.ToStringPercent();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksSinceCycleStart, "ticksSinceCycleStart", 0);
        }
    }
}
