using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F5 spike (forge_kit_spec.md "the Contagion die-off
    // ring"). Generic spread-then-die comp: a thing pushes a handful of
    // copies of itself into nearby cells over a window, then dies wherever
    // it stands, optionally leaving a "dead" marker (filth or a ground-cover
    // ThingDef) behind. Explicitly reusable beyond the Forge — the spec's
    // own cross-flow note: "if a shared creep system lands later,
    // RUT_DyingCreep becomes its client" of the_contagion.md's kit, not the
    // other way round, so this comp stays generic rather than Forge-coded.
    //
    // Per-instance model, not a MapComponent coordinator: XML <li
    // Class="...CompProperties_ScriptedDieOff"> on the shared ThingDef gives
    // every spawned copy its OWN comp instance, so "spread N cells over M
    // hours, dead by hour X" is each instance's own countdown — no
    // map-wide tracker needed for an S-effort spike. A denser/coordinated
    // ring shape is the full build's call if the per-instance fan-out reads
    // too even in a live quicktest.
    //
    // The F5 ban edge (kit spec ❓5, resolved this pass): RimWorld/
    // PlantProperties.cs carries no "reproduces" field at all in the live
    // 1.6/Odyssey decompile — plant spread is driven entirely by
    // RimWorld/WildPlantSpawner.cs reading RimWorld/BiomeDef.cs's own
    // `wildPlants` commonality dict (BiomeDef.CommonalityOfPlant →
    // WildPlantSpawner.GetCommonalityOfPlant, both verified), which returns
    // 0 for any ThingDef absent from that dict. So "no reproduction" for
    // RUT_DyingCreep is enforced by simply never listing it in any
    // BiomeDef's wildPlants — not a field this comp or its ThingDef needs
    // to carry — and this comp's own scripted spread (below) is the ONLY
    // way copies appear, exactly the sheet's "physics as def structure."
    public class CompProperties_ScriptedDieOff : CompProperties
    {
        /// <summary>How many spread attempts this instance makes before it
        /// stops pushing new copies (an attempt can still fail a cell check
        /// and land nothing). INVENTED, F5 spec range: 6-10.</summary>
        public IntRange spreadAttemptCountRange = new IntRange(6, 10);

        /// <summary>Cell radius a spread attempt can land in, around this
        /// instance's own position. INVENTED.</summary>
        public float spreadRadius = 3f;

        /// <summary>In-game hours from spawn over which the spread attempts
        /// are spaced out (evenly). INVENTED, F5 spec: 4 hours.</summary>
        public float spreadDurationHours = 4f;

        /// <summary>In-game hours from spawn until this instance dies
        /// outright, spread budget spent or not. INVENTED, F5 spec:
        /// "dead by hour 8."</summary>
        public float lifetimeHours = 8f;

        /// <summary>What this instance spreads. Null (default) means "my
        /// own def" — clones itself outward, each new copy starting its own
        /// independent countdown. A future consumer (e.g. a shared
        /// creep-spread system) can point this at a different ThingDef.</summary>
        public ThingDef spreadThingDef;

        /// <summary>Left behind at this instance's own cell on death.
        /// Null = leaves nothing. "RUT_DeadCreep" in the concrete F5
        /// build.</summary>
        public ThingDef deadThingDef;

        /// <summary>True (default): deadThingDef is spawned as filth via
        /// FilthMaker — walkable ground cover, no plant/harvest fields
        /// possible on filth at all. False: spawned as an ordinary Thing
        /// via GenSpawn (e.g. a non-filth ground-cover ThingDef).</summary>
        public bool deadThingIsFilth = true;

        public CompProperties_ScriptedDieOff()
        {
            compClass = typeof(RM_CompScriptedDieOff);
        }
    }

    public class RM_CompScriptedDieOff : ThingComp
    {
        // 1 in-game hour = 2500 ticks (60000 ticks/day ÷ 24), the same
        // conversion this mod's own weather/window tuning already uses.
        private const float TicksPerHour = 2500f;

        private int ticksSinceSpawn;
        private int spreadAttemptsTarget = -1;
        private int spreadAttemptsDone;
        private int nextSpreadTick;
        private bool dead;

        public CompProperties_ScriptedDieOff Props => (CompProperties_ScriptedDieOff)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (spreadAttemptsTarget < 0)
            {
                spreadAttemptsTarget = Mathf.Max(0, Props.spreadAttemptCountRange.RandomInRange);
                ScheduleNextSpread();
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (dead || parent.Map == null)
            {
                return;
            }

            ticksSinceSpawn++;

            int lifetimeTicks = Mathf.Max(1, Mathf.RoundToInt(Props.lifetimeHours * TicksPerHour));
            if (ticksSinceSpawn >= lifetimeTicks)
            {
                DieNow();
                return;
            }

            if (spreadAttemptsDone < spreadAttemptsTarget && ticksSinceSpawn >= nextSpreadTick)
            {
                TrySpreadOnce();
                spreadAttemptsDone++;
                ScheduleNextSpread();
            }
        }

        private void ScheduleNextSpread()
        {
            int spreadDurationTicks = Mathf.Max(1, Mathf.RoundToInt(Props.spreadDurationHours * TicksPerHour));
            int step = Mathf.Max(1, spreadDurationTicks / Mathf.Max(1, spreadAttemptsTarget));
            nextSpreadTick = ticksSinceSpawn + step;
        }

        private void TrySpreadOnce()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return;
            }
            ThingDef spreadDef = Props.spreadThingDef ?? parent.def;

            bool CellOk(IntVec3 c)
            {
                if (!c.InBounds(map) || !c.Walkable(map))
                {
                    return false;
                }
                if (spreadDef.category == ThingCategory.Plant)
                {
                    return spreadDef.CanEverPlantAt(c, map, canWipePlantsExceptTree: false, checkMapTemperature: false);
                }
                return true;
            }

            if (GenRadial.RadialCellsAround(parent.Position, Props.spreadRadius, useCenter: false)
                .TryRandomElement(CellOk, out IntVec3 cell))
            {
                GenSpawn.Spawn(spreadDef, cell, map);
            }
        }

        private void DieNow()
        {
            dead = true;
            Map map = parent.Map;
            IntVec3 cell = parent.Position;
            if (Props.deadThingDef != null && map != null)
            {
                if (Props.deadThingIsFilth)
                {
                    FilthMaker.TryMakeFilth(cell, map, Props.deadThingDef);
                }
                else
                {
                    GenSpawn.Spawn(Props.deadThingDef, cell, map);
                }
            }
            parent.Destroy();
        }

        public override string CompInspectStringExtra()
        {
            if (dead)
            {
                return null;
            }
            int lifetimeTicks = Mathf.Max(1, Mathf.RoundToInt(Props.lifetimeHours * TicksPerHour));
            float frac = Mathf.Clamp01((float)ticksSinceSpawn / lifetimeTicks);
            return "RM_DieOffProgress".Translate() + ": " + frac.ToStringPercent();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksSinceSpawn, "dieOffTicksSinceSpawn", 0);
            Scribe_Values.Look(ref spreadAttemptsTarget, "dieOffSpreadTarget", -1);
            Scribe_Values.Look(ref spreadAttemptsDone, "dieOffSpreadDone", 0);
            Scribe_Values.Look(ref nextSpreadTick, "dieOffNextSpreadTick", 0);
            Scribe_Values.Look(ref dead, "dieOffDead", false);
        }
    }
}
