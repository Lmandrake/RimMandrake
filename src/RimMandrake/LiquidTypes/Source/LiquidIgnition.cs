using RimWorld;
using Verse;

namespace RimMandrake.LiquidTypes
{
    // LIQUID_TYPES_SPIKES_1, Spike C (body ignition) — a PROTOTYPE, sized
    // M-L per §8 and explicitly not brought to full production here. Proves
    // the mechanism and the API surface; has never run inside a live game.
    //
    // The hard constraint this exists to satisfy, verbatim from
    // design/Jawa/worldbuilding/the_propane_lakes.md hard ban #4: NO
    // IGNITION WITHOUT A THERMAL OR ELECTRICAL TRIGGER. Two facts read
    // directly from RimWorld/Fire.cs and RimWorld/FireUtility.cs (rimsage)
    // decide the whole shape of this system:
    //
    //   1. Vanilla's OWN fire spread (Fire.TrySpread, on a fireSize > 1
    //      Fire that already exists) rolls FireUtility.ChanceToStartFireIn
    //      on nearby cells purely from TerrainDef.Flammable() —
    //      GetStatValueAbstract(StatDefOf.Flammability) off <statBases> —
    //      with NO trigger check at all. If a propane terrain shipped a
    //      real Flammability stat, vanilla would spontaneously ignite it on
    //      its own schedule. That is exactly the hard ban's violation, so
    //      the propane TerrainDef must ship Flammability at/near 0 (its
    //      AB_PropaneLake donor already has no combustion behavior at all —
    //      §2 of the design doc) and RM_LiquidProperties.flammable is
    //      therefore NOT wired to the native stat. The trigger check lives
    //      here instead, in code we control.
    //
    //   2. Fire.DoComplexCalcs() checks
    //      `!base.Position.GetTerrain(base.Map).extinguishesFire` before it
    //      will do ANYTHING — burn, spread, or even keep existing. The
    //      donor AB_PropaneLake ships extinguishesFire=true (§2: "a propane
    //      sea that puts fires out"). A Fire spawned on unpatched
    //      AB_PropaneLake self-destroys the same tick via that guard's
    //      `if (flammabilityMax < 0.01f) { Destroy(); return; }` path.
    //      CONSEQUENCE FOR §7 (the RUT layer): the compat patch that
    //      flips extinguishesFire=false on AB_PropaneLake is a hard
    //      PREREQUISITE for ignition to be possible at all, not a
    //      cosmetic nicety — confirmed by reading the guard, not assumed.
    //
    // What this class does: a MapComponent scanning terrain cells whose
    // RM_LiquidProperties.flammable is true, on the same coarse interval as
    // LiquidCorrosionMapComponent, checking their 8 neighbours
    // (GenAdj.CardinalDirections/eight-way) for an existing Fire Thing
    // (ThingDefOf.Fire) or a thing mid-explosion. Only on a hit does it call
    // FireUtility.TryStartFireIn — vanilla's own real ignition entry point,
    // never a hand-rolled Fire spawn — which then rides vanilla's own
    // TrySpread() for propagation across contiguous flammable cells, same
    // as any other fire once it exists.
    //
    // NOT built here (owed, explicitly, not silently skipped):
    //   - The propane TerrainDef itself and its extinguishesFire=false
    //     compat patch (§7, RUT layer, its own build item).
    //   - The "explosion nearby" half of the trigger (only the adjacent-Fire
    //     half is implemented) — needs a hook into DamageWorker_AddInjury's
    //     explosion path or GenExplosion, not attempted in a spike.
    //   - Any live/quicktest observation. This has never ticked in a
    //     running game; the two facts above are read from source, not
    //     measured from a burn.
    public class LiquidIgnitionMapComponent : MapComponent
    {
        private const int TickInterval = 250;

        public LiquidIgnitionMapComponent(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (map.IsHashIntervalTick(TickInterval))
            {
                ScanForIgnition();
            }
        }

        private void ScanForIgnition()
        {
            // Spike-sized scan: the map's spawned Fire things, not every
            // flammable-liquid cell on the map (which would need a cached
            // liquid-cell index this spike does not build). Proves the
            // trigger-gated call shape; a production version indexes
            // flammable liquid cells instead of walking existing fires.
            var fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < fires.Count; i++)
            {
                Thing fire = fires[i];
                if (fire == null || !fire.Spawned)
                {
                    continue;
                }

                foreach (IntVec3 adj in GenAdj.CellsAdjacent8Way(fire))
                {
                    if (!adj.InBounds(map))
                    {
                        continue;
                    }

                    TerrainDef terrain = adj.GetTerrain(map);
                    RM_LiquidProperties props = terrain?.GetModExtension<RM_LiquidProperties>();
                    if (props == null || !props.flammable)
                    {
                        continue;
                    }

                    // The trigger-gate itself: this cell only ignites
                    // because a real Fire Thing already exists adjacent to
                    // it, satisfying hard ban #4. TryStartFireIn still
                    // rolls its own flammability-chance curve internally
                    // (FireUtility.ChanceToStartFireIn) — we are not
                    // bypassing that, only supplying the trigger vanilla's
                    // own spread logic would never supply on a
                    // near-zero-Flammability terrain.
                    FireUtility.TryStartFireIn(adj, map, 0.4f, fire);
                }
            }
        }
    }
}
