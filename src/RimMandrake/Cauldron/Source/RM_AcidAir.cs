using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // VEXXITH_USES_1 — air that eats. Owner, 2026-10-09: "the Forge and Cauldron have ambient acidic environments that
    // would constantly damage the ship and even players, but materials like this allow the ship to exist there without such
    // damage... and raids from the empire suffer constant slow damage from that ambient acidity when they raid the players
    // there. Environmental/vacsuits will protect the players of course."
    //
    // Data: RM_AcidAirExtension on a BiomeDef (Patches/RM_Cauldron_AcidAir.xml). Every damage here is AcidBurn through
    // TakeDamage, so anything acid-proof (RM_VexxithAcidImmunity) is spared by the one rule that already exists, and a raider
    // burns by the rule that burns a colonist. Hull = a player building on gravship substructure with open sky on it or
    // beside it, sampled hourly. A standing hull liner rig spares the whole ship.
    // ════════════════════════════════════════════════════════════════════
    public class RM_AcidAirExtension : DefModExtension
    {
    }

    /// <summary>On a building: while it stands on a ship, the map's ship takes no ambient acid.</summary>
    public class RM_HullLinerExtension : DefModExtension
    {
    }

    /// <summary>On a gas tap: lined with vexxith plate, and a vexxiss will not pry at its own hide.</summary>
    public class RM_PryProofExtension : DefModExtension
    {
    }

    public class RM_MapComponent_AcidAir : MapComponent
    {
        private bool warned;

        public RM_MapComponent_AcidAir(Map map) : base(map) { }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref warned, "rmAcidAirWarned", false);
        }

        public override void MapComponentTick()
        {
            if (!RM_CauldronSettings.acidAirEnabled || !map.IsHashIntervalTick(RM_AcidAirKernel.IntervalTicks)) return;
            if (map.Biome == null || !map.Biome.HasModExtension<RM_AcidAirExtension>()) return;
            DamageDef acid = DefDatabase<DamageDef>.GetNamedSilentFail("AcidBurn");
            if (acid == null) return;
            BurnPawns(acid);
            if (RM_CauldronSettings.acidAirHullEnabled) BurnHull(acid);
        }

        private void BurnPawns(DamageDef acid)
        {
            // A copy: a burn can kill, and a death edits the live list.
            var pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.RaceProps == null) continue;
                bool animal = p.RaceProps.Animal;
                if (!RM_AcidAirKernel.PawnExposed(p.Dead, p.Spawned, p.kindDef != null && p.kindDef.immuneToGameConditionEffects,
                        p.Spawned && p.Position.Roofed(map), animal, animal && map.Biome.CommonalityOfAnimal(p.kindDef) > 0f)) continue;
                float chance = RM_AcidAirKernel.BurnChance(RM_CauldronSettings.acidAirFactor,
                    p.GetStatValue(StatDefOf.VacuumResistance), p.GetStatValue(StatDefOf.ToxicEnvironmentResistance));
                if (Rand.Chance(chance)) p.TakeDamage(new DamageInfo(acid, RM_AcidAirKernel.PawnBurnDamage));
            }
        }

        private void BurnHull(DamageDef acid)
        {
            List<Building> all = map.listerBuildings.allBuildingsColonist;
            var ship = new List<Building>();
            bool lined = false;
            for (int i = 0; i < all.Count; i++)
            {
                if (!OnShip(all[i])) continue;
                ship.Add(all[i]);
                if (all[i].def.HasModExtension<RM_HullLinerExtension>()) lined = true;
            }
            if (lined || ship.Count == 0) return;
            for (int i = 0; i < RM_AcidAirKernel.HullSamplesPerInterval; i++)
            {
                Building b = ship.RandomElement();
                if (b.Destroyed || !b.def.useHitPoints) continue;
                if (!RM_AcidAirKernel.HullBurns(true, false, true, Exposed(b), b.HitPoints, b.MaxHitPoints)) continue;
                int before = b.HitPoints;
                b.TakeDamage(new DamageInfo(acid, RM_AcidAirKernel.HullBurnDamage));
                if (!warned && b.HitPoints < before)
                {
                    warned = true;
                    Messages.Message("The air here is eating the ship's hull. Vexxith plate or a hull liner rig will stop it.", b,
                        MessageTypeDefOf.NegativeEvent);
                }
            }
        }

        private bool OnShip(Building b)
        {
            TerrainDef foundation = b.Spawned ? map.terrainGrid.FoundationAt(b.Position) : null;
            return foundation != null && foundation.IsSubstructure;
        }

        private bool Exposed(Building b)
        {
            if (!b.Position.Roofed(map)) return true;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(b))
                if (c.InBounds(map) && !c.Roofed(map)) return true;
            return false;
        }
    }

    /// <summary>The hull liner rig goes on a ship, or it lines nothing.</summary>
    public class RM_PlaceWorker_OnShipHull : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            TerrainDef foundation = map.terrainGrid.FoundationAt(loc);
            return foundation != null && foundation.IsSubstructure ? (AcceptanceReport)true : "Must be placed on a gravship's substructure.";
        }
    }

    /// <summary>With the setting off, the vexxith gear leaves the build menu and the benches at startup (next launch).
    /// Things already made stay. The same before-and-after dance as RM_VexxithDoorGate.</summary>
    [StaticConstructorOnStartup]
    public static class RM_VexxithGearGate
    {
        static RM_VexxithGearGate()
        {
            if (RM_CauldronSettings.vexxithGearEnabled) return;
            foreach (string name in new[] { "RM_VexxithFilterWorks", "RM_VentGasTapLined", "RM_HullLinerRig" })
            {
                ThingDef b = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (b == null) continue;
                DesignationCategoryDef cat = b.designationCategory;
                b.designationCategory = null;
                cat?.AllResolvedDesignators.RemoveAll(d => d is Designator_Build db && db.PlacingDef == b);
            }
            foreach (string name in new[] { "RM_Make_Bottle_Vexxith", "RM_Make_Bucket_Vexxith", "RM_Make_Barrel_Vexxith",
                         "Make_RM_VexxithSuit", "Make_RM_VexxithSuitHelmet" })
            {
                RecipeDef r = DefDatabase<RecipeDef>.GetNamedSilentFail(name);
                if (r?.recipeUsers == null) continue;
                foreach (ThingDef bench in r.recipeUsers) bench.AllRecipes.Remove(r);
                r.recipeUsers = new List<ThingDef>();
            }
        }
    }
}
