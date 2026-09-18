using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ROT_DECAY_HARVEST_1 ("the gut digests"). Opt-in per biome via
    // RM_AcceleratedRotExtension (see that file's own header) on the
    // BiomeDef; inert everywhere else, same "harmless no-op absent the
    // extension" idiom every other biome-scoped mechanism in this assembly
    // uses.
    //
    // CompRottable's real shape (verified via ilspycmd against the live
    // Assembly-CSharp.dll, 2026-09-18 — RimSage does not connect from this
    // laptop/WSL session): `RotProgress` IS a public get/set float property
    // (RimWorld/CompRottable.cs). Vanilla's own CompRottable.TickInterval
    // adds `GenTemperature.RotRateAtTemperature(ambientTemp) * delta` to it
    // on ITS OWN schedule (every tick if tickerType Normal, every 250 ticks
    // if Rare) and separately owns the stage-transition consequences
    // (destroy-on-rotten, rot-stink gas, rot damage). This component does
    // NOT reimplement any of that: it only adds the EXTRA progress a
    // multiplier implies, using the same rate formula, and leaves vanilla's
    // own tick to notice the new Stage and act on it (worst case one
    // TickInterval's-worth of lag, negligible against ×12/×20).
    public class RM_MapComponent_AcceleratedRot : MapComponent
    {
        private const int TickInterval = 250;

        // Rough odds a given outdoor filth thing thins by one point on any
        // one sweep. INVENTED (the spec asks for "slow" thinning, no number
        // given) — at this chance and TickInterval, an average filth (usually
        // dropped at thickness 1) is gone within a few in-game hours of
        // standing in the open, "vanishes here, not survives" without being
        // instant.
        private const float FilthThinChancePerSweep = 0.15f;

        // BENCH's own note on this item: "card 2 may adjust the exposure
        // predicate — build the predicate as one swappable method." This is
        // that method: everything above (the tick loop, the filth sweep)
        // calls ONLY this delegate to ask "is this thing exposed to
        // acceleration", never re-derives the walled+roofed test itself. A
        // future card swaps the predicate here and nothing else changes.
        // Default: vanilla's own "does this cell's room use outdoor
        // temperature" test (Verse.GridsUtility.UsesOutdoorTemperature),
        // which already IS "not enclosed in a walled+roofed room" — the same
        // signal that decides whether a room can hold a stable temperature
        // at all.
        public static Func<Thing, bool> IsExposedToAcceleration = DefaultIsExposed;

        public RM_MapComponent_AcceleratedRot(Map map)
            : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_EnvironmentalHazardsSettings.acceleratedRotEnabled)
            {
                return;
            }

            if (map.Biome?.GetModExtension<RM_AcceleratedRotExtension>() == null)
            {
                return;
            }

            int tick = Find.TickManager.TicksGame;
            if (tick % TickInterval != 0)
            {
                return;
            }

            AccelerateRot();
            ThinOutdoorFilth();
        }

        private void AccelerateRot()
        {
            List<Thing> things = map.listerThings.AllThings;
            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (!(t is ThingWithComps twc))
                {
                    continue;
                }

                CompRottable rot = twc.TryGetComp<CompRottable>();
                if (rot == null || !rot.Active)
                {
                    continue;
                }

                if (!IsExposedToAcceleration(t))
                {
                    continue;
                }

                float multiplier = (t is Corpse)
                    ? RM_EnvironmentalHazardsSettings.acceleratedRotCorpseMultiplier
                    : RM_EnvironmentalHazardsSettings.acceleratedRotItemMultiplier;
                float extra = multiplier - 1f; // vanilla's own tick already supplies the base ×1
                if (extra <= 0f)
                {
                    continue;
                }

                float rate = GenTemperature.RotRateAtTemperature(t.AmbientTemperature);
                if (rate <= 0f)
                {
                    continue; // frozen — nothing to accelerate
                }

                rot.RotProgress += rate * extra * TickInterval;
            }
        }

        private void ThinOutdoorFilth()
        {
            List<Thing> filthThings = map.listerThings.ThingsInGroup(ThingRequestGroup.Filth);
            for (int i = filthThings.Count - 1; i >= 0; i--)
            {
                if (!(filthThings[i] is Filth filth))
                {
                    continue;
                }

                if (!IsExposedToAcceleration(filth))
                {
                    continue;
                }

                if (Rand.Chance(FilthThinChancePerSweep))
                {
                    filth.ThinFilth(); // destroys itself once thickness hits 0 — vanilla's own method
                }
            }
        }

        private static bool DefaultIsExposed(Thing t)
        {
            if (t.Map == null)
            {
                return false;
            }

            return t.Position.UsesOutdoorTemperature(t.Map);
        }
    }
}
