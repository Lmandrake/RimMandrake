using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.LiquidTypes
{
    // LIQUID_TYPES_SPIKES_1, Spike B (mechanism side): proves the pH-damage
    // + apparel-corrosion code path the doc's §4a asks for, on ONE def
    // (RM_AcidShallow/RM_AcidDeep, Spike A's output).
    //
    // Pattern borrowed from RimWorld's own SteadyEnvironmentEffects (terrain
    // heatPerTick push) and RimMandrake.EnvironmentalHazards.Gas_Damaging
    // (tick-and-scan damage+hediff): a MapComponent that ticks rarely
    // (TickRareInterval, ~250 ticks) and scans every spawned, non-dead pawn's
    // terrain for an RM_LiquidProperties extension.
    //
    // What this proves, offline: the extension is readable via
    // Def.GetModExtension<T>() (Verse.Def, confirmed by rimsage read), the
    // damage route is DamageInfo + Pawn.TakeDamage (vanilla API, no
    // reflection), and apparel corrosion is Apparel.HitPoints -=, the same
    // field ArmorUtility already exposes publicly for wear-and-tear.
    //
    // Wiring, confirmed by reading Verse.Map.FillComponents directly (not
    // guessed): the engine auto-instantiates EVERY non-abstract
    // MapComponent subclass it finds via AllSubclassesNonAbstract() on every
    // map, calling exactly this (Map) constructor. No Harmony patch, no
    // XML, no registration call needed — this class existing in the loaded
    // assembly is sufficient for every map to carry one.
    //
    // What is NOT proven here (owed, per LIQUID_TYPES_SPIKES_1's own verify
    // bar): this has never ticked inside a running game. No live/quicktest
    // pass has confirmed a pawn standing in RM_AcidShallow actually takes
    // AcidBurn damage or that a worn Apparel's HitPoints visibly drops.
    public class LiquidCorrosionMapComponent : MapComponent
    {
        private const int TickInterval = 250; // ~4.2s at normal speed — coarse on purpose, matches GasDamageExtension's default coarseness rationale

        public LiquidCorrosionMapComponent(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (map.IsHashIntervalTick(TickInterval))
            {
                DoCorrosionPass();
            }
        }

        private void DoCorrosionPass()
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn == null || pawn.Dead || !pawn.Spawned)
                {
                    continue;
                }

                TerrainDef terrain = pawn.Position.GetTerrain(map);
                RM_LiquidProperties props = terrain?.GetModExtension<RM_LiquidProperties>();
                if (props == null)
                {
                    continue;
                }

                // "Immersion" vs "contact": the split §3 flags as native-less.
                // Cheapest honest proxy available without a bespoke depth
                // field of our own: WaterDeepBase-derived terrains carry
                // Impassable passability (measured in §1's table — WaterDeep
                // 300/Impassable vs WaterShallow 30/Standable); a drafted
                // pawn cannot normally stand in Impassable terrain at all,
                // so in practice only flying/swimming pawns reach it. Left
                // as a TODO for whoever builds past the spike — this proxy
                // is not exercised by RM_AcidShallow (Standable) in any test
                // this spike ran.
                LiquidDamageSpec spec = props.damageOnContact;
                if (spec?.damageDef != null && spec.amount > 0f)
                {
                    DamageInfo dinfo = new DamageInfo(spec.damageDef, spec.amount, 0f, -1f, null);
                    pawn.TakeDamage(dinfo);
                }

                if (props.corrodesApparel && pawn.apparel != null)
                {
                    List<Apparel> worn = pawn.apparel.WornApparel;
                    for (int a = 0; a < worn.Count; a++)
                    {
                        Apparel piece = worn[a];
                        // Proportional to pH distance from neutral (7), per
                        // §4a: "basic liquids mirror at the other end of the
                        // scale — same code path." 1 HP per pass is deliberately
                        // slow; this is a spike value, not a tuned one.
                        float pHDistance = System.Math.Abs(props.pH - 7f);
                        if (pHDistance > 3f)
                        {
                            piece.HitPoints -= 1;
                            if (piece.HitPoints <= 0)
                            {
                                pawn.apparel.Remove(piece);
                            }
                        }
                    }
                }
            }
        }
    }
}
