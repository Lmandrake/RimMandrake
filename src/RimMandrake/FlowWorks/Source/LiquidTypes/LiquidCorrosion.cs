using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
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
    // Ships ON by default since b5c8547e8b (owner by card, 2026-10-15); the
    // Mod Settings toggle (liquidCorrosionEnabled) turns it off.
    public class LiquidCorrosionMapComponent : MapComponent
    {
        private const int TickInterval = 250; // ~4.2s at normal speed — coarse on purpose, matches GasDamageExtension's default coarseness rationale

        public LiquidCorrosionMapComponent(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            // ON by default (RimMandrakeFlowWorksSettings.liquidCorrosionEnabled),
            // shipped ON since b5c8547e8b (owner by card, 2026-10-15).
            //
            // Gated here rather than by removing the component: a MapComponent
            // is scribed per map, so dropping one a save already carries is a
            // save-compat problem. Off ticks and returns; the toggle needs no
            // new game.
            if (!RimMandrakeFlowWorksSettings.liquidCorrosionEnabled)
            {
                return;
            }
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
                    // Iterate backwards: WornApparel is the tracker's live list, and
                    // piece.Destroy() below takes the piece out of it (its holder is the
                    // tracker's ThingOwner), shifting everything after it down by one — a forward
                    // loop would silently skip the apparel that just slid into the removed slot for this pass.
                    List<Apparel> worn = pawn.apparel.WornApparel;
                    for (int a = worn.Count - 1; a >= 0; a--)
                    {
                        Apparel piece = worn[a];
                        if (!piece.def.useHitPoints)
                        {
                            continue;   // an item without hit points cannot be worn away
                        }
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
                                // As vanilla wear-out (Pawn_ApparelTracker.TakeWearoutDamageForDay): the
                                // piece is DESTROYED, which also takes it off the pawn. A bare
                                // apparel.Remove left an orphaned Thing with no holder, never destroyed.
                                piece.Destroy();
                                if (PawnUtility.ShouldSendNotificationAbout(pawn) && !pawn.Dead)
                                {
                                    Messages.Message(GenText.CapitalizeFirst("MessageWornApparelDeterioratedAway".Translate(GenLabel.ThingLabel(piece.def, piece.Stuff), pawn)),
                                        pawn, MessageTypeDefOf.NegativeEvent);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
