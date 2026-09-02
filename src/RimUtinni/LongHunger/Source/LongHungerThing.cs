// RUT_LongHunger - the VAST-tier dune leviathan, SANDWORM_MYTHOS_BUILD_1.
//
// Shape follows design/Jawa/worldbuilding/setting_physics.md Part 5's ruled VAST
// template (world object, no <race>, quest-gated, not a wildlife-table spawn) and
// borrows the DESIGN of chezhou.creature.sandworm (LEVIATHANS:SANDWORM) per
// research/Jawa/sandworm_krayt_survey_2026-09-02.md - not its C#, which is
// Workshop-only/closed. This is original code.
//
// v1 deliberate simplification vs the reference: single-cell entity with a large
// drawSize/explosion radius, not a separate multi-tile SandWorm_HitProxy body.
// The reference's HitProxy geometry needs live tuning this pass has no bridge for;
// tracked as a named v2 improvement in the item file, not silently dropped.
//
// API citations (RimSage, decompiled 1.6): GenExplosion.DoExplosion(Verse/GenExplosion.cs),
// Building/ThingWithComps lifecycle (Verse/Thing.cs, Verse/ThingWithComps.cs).
using RimWorld;
using System.Collections.Generic;
using Verse;

namespace LongHunger
{
    public class LongHungerThing : Building
    {
        // Ticks between tremor pulses (~600 ticks = 14 in-game minutes) and total
        // surfaced lifetime (~2500 ticks = 1 in-game hour) before it submerges.
        private const int PulseIntervalTicks = 600;
        private const int SurfacedDurationTicks = 2500;
        private const float EruptionRadius = 4.5f;
        private const float PulseRadius = 3f;
        private const int EruptionDamage = 90;
        private const int PulseDamage = 45;

        private int ticksSinceSpawn = 0;
        private int nextPulseAt = PulseIntervalTicks;

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            if (!respawningAfterLoad)
            {
                // The eruption itself - the moment it breaks the surface.
                GenExplosion.DoExplosion(
                    center: Position,
                    map: map,
                    radius: EruptionRadius,
                    damType: DamageDefOf.Bomb,
                    instigator: this,
                    damAmount: EruptionDamage,
                    chanceToStartFire: 0f,
                    doVisualEffects: true,
                    doSoundEffects: true
                );
            }
        }

        protected override void Tick()
        {
            base.Tick();
            if (!Spawned)
            {
                return;
            }
            ticksSinceSpawn++;

            if (ticksSinceSpawn >= nextPulseAt && ticksSinceSpawn < SurfacedDurationTicks)
            {
                // A thrashing tremor, smaller than the initial eruption - gives
                // pawns near it a real reason to move away, not just a one-shot hit.
                GenExplosion.DoExplosion(
                    center: Position,
                    map: Map,
                    radius: PulseRadius,
                    damType: DamageDefOf.Bomb,
                    instigator: this,
                    damAmount: PulseDamage,
                    chanceToStartFire: 0f,
                    doVisualEffects: true,
                    doSoundEffects: true
                );
                nextPulseAt += PulseIntervalTicks;
            }

            if (ticksSinceSpawn >= SurfacedDurationTicks)
            {
                Submerge();
            }
        }

        // Dives back under the sand. Drops the swallowed-salvage cache it has been
        // hoarding for centuries - the scavenging-economy tie-in this item's own
        // design note asks for, and the in-fiction reason the Dunes tile mutator's
        // stripped-bare tiles (no ruins, no junk - see ASHKARR_WORLD_DEFINITION.md
        // SS13.1) read empty: nothing left behind because the Long Hunger already
        // took it.
        private void Submerge()
        {
            if (!Spawned)
            {
                return;
            }
            Map map = Map;
            IntVec3 dropCell = Position;
            Destroy(DestroyMode.Vanish);

            List<Thing> loot = ThingSetMakerDefOf.Reward_ItemsStandard.root.Generate(new ThingSetMakerParams
            {
                totalMarketValueRange = new FloatRange(600f, 1400f),
            });
            foreach (Thing item in loot)
            {
                GenPlace.TryPlaceThing(item, dropCell, map, ThingPlaceMode.Near);
            }
        }
    }
}
