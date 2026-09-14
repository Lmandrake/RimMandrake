using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S1 build pass (sump_kit_spec.md "the poured moat +
    // command ignition"). Generic by construction, same posture as
    // RM_CompFloodIgniter: any future short-lived "burning wall" content
    // reuses this unchanged, not just the Sump's RUT_TarBlaze.
    //
    // Resolves this item's own spike-pass finding (SUMP_MECHANICS_1.md,
    // "spike pass" > "Engine ground-truth" #1): a plain Thing gets NONE of
    // vanilla's Fire-specific pathfinding avoidance bonus
    // (Verse.AI/PathGrid.cs:179-204 only matches the runtime type
    // RimWorld.Fire). This pass's own build decision — recorded here, not
    // just in the item file — is to NOT subclass Fire: RUT_TarBlaze instead
    // carries `passability Impassable` directly on its ThingDef (confirmed,
    // decompile, PathGrid.cs:140-156 — the general per-Thing cost/
    // impassability check runs for ANY spawned Thing regardless of runtime
    // type or category, not just the Fire-specific perceivedStatic branch)
    // plus `pathfinderDangerous true` (Verse/ThingDef.cs:175, consumed by
    // Verse/PersistentDangerSource.cs and Verse/PathFinderMapData.cs:111 —
    // a SECOND, independent, fully generic engine hook that marks a cell as
    // pathfinder-dangerous for the smarter long-range search; note vanilla
    // Fire itself does not even set this flag, so this is a stronger
    // avoidance signal than real fire gets, matching the sheet's own "a
    // wall of flame nothing crosses" framing better than Fire's own
    // avoid-if-possible behavior would). Both fields are plain XML on
    // RUT_TarBlaze's own ThingDef — no C# needed for the block itself,
    // exactly as the spike pass's own finding said. This class is ONLY the
    // lifecycle: start the gas release, count down, convert the terrain,
    // self-destruct.
    //
    // Also resolves this item's other open question ("confirm this
    // conversion is automatic via the terrain's own burnedDef mechanism, or
    // whether RUT_TarBlaze needs to trigger it explicitly"): it is NOT
    // automatic. The automatic burnedDef swap vanilla flammable floors get
    // comes from Fire.TryBurnFloor calling TerrainGrid.Notify_TerrainBurned
    // (RimWorld/Fire.cs:320-326) — a method that only runs on a real Fire
    // instance's own tick. RUT_TarBlaze is not a Fire, so nothing calls it
    // automatically; this comp calls TerrainGrid.Notify_TerrainBurned
    // (verified signature, Verse/TerrainGrid.cs:599) itself on expiry.
    public class CompProperties_TimedTerrainBurn : CompProperties
    {
        /// <summary>INVENTED (spec S1: "12-24 in-game hours"; 2500 ticks per
        /// in-game hour, so 30000-60000 ticks).</summary>
        public IntRange durationTicksRange = new IntRange(30000, 60000);

        /// <summary>On spawn, call StartRelease() on a sibling
        /// CompReleaseGas (vanilla's own comp never auto-starts itself —
        /// confirmed, RimWorld/CompReleaseGas.cs, `started` defaults false
        /// and only StartRelease() sets it true). Generic escape hatch for
        /// a future user with no gas comp at all.</summary>
        public bool autoStartReleaseGas = true;

        /// <summary>On expiry, convert the parent's own cell via
        /// TerrainGrid.Notify_TerrainBurned (see class header — this is the
        /// explicit trigger a non-Fire burning Thing needs).</summary>
        public bool convertTerrainOnExpiry = true;

        public bool destroyOnExpiry = true;

        /// <summary>If true, this instance registers with the map's
        /// RM_MapComponent_ThresholdSmokeColumn while alive — the spec's own
        /// "distant column... while >= N blaze cells live" cosmetic (S1,
        /// INVENTED N=20; see that class).</summary>
        public bool marksColumnSource = false;

        public CompProperties_TimedTerrainBurn()
        {
            compClass = typeof(RM_CompTimedTerrainBurn);
        }
    }

    public class RM_CompTimedTerrainBurn : ThingComp
    {
        private int ticksRemaining = -1;

        public CompProperties_TimedTerrainBurn Props => (CompProperties_TimedTerrainBurn)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);

            if (!respawningAfterLoad)
            {
                ticksRemaining = Props.durationTicksRange.RandomInRange;
            }

            if (Props.autoStartReleaseGas)
            {
                parent.GetComp<CompReleaseGas>()?.StartRelease();
            }

            if (Props.marksColumnSource && parent.Map != null)
            {
                parent.Map.GetComponent<RM_MapComponent_ThresholdSmokeColumn>()
                    ?.Notify_SourceSpawned(parent);
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            if (Props.marksColumnSource)
            {
                map?.GetComponent<RM_MapComponent_ThresholdSmokeColumn>()
                    ?.Notify_SourceDespawned(parent);
            }
            base.PostDeSpawn(map, mode);
        }

        public override void CompTick()
        {
            base.CompTick();
            if (ticksRemaining < 0 || !parent.Spawned)
            {
                return;
            }
            ticksRemaining--;
            if (ticksRemaining <= 0)
            {
                Expire();
            }
        }

        private void Expire()
        {
            // Disable further ticking before anything else: destroying the
            // parent already stops CompTick from firing again, but a
            // destroyOnExpiry=false user (deliberately kept alive after its
            // burn — e.g. a spent-but-still-standing variant) would
            // otherwise re-enter Expire() every tick forever, since
            // ticksRemaining stays <= 0 once it crosses zero.
            ticksRemaining = -1;

            if (Props.convertTerrainOnExpiry && parent.Spawned)
            {
                parent.Map.terrainGrid.Notify_TerrainBurned(parent.Position);
            }
            if (Props.destroyOnExpiry && parent.Spawned)
            {
                parent.Destroy();
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksRemaining, "ticksRemaining", -1);
        }

        public override string CompInspectStringExtra()
        {
            if (ticksRemaining < 0)
            {
                return null;
            }
            return "RM_TarBlazeBurnsFor".Translate(ticksRemaining.ToStringTicksToPeriod());
        }
    }
}
