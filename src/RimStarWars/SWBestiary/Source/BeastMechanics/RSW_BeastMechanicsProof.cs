using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // SWBESTIARY_COVERAGE_GAPS_1 follow-up (r28 left metal eating and hoarding proven only by a settings round-trip).
    // Live proof hook for jawa/static_call, args "current": spawns the real creature on the current map, puts the scrap
    // and nest beside it, and asks the SHIPPED job giver what it would do, then asks again with the setting off.
    // Everything it spawns is destroyed before it returns. Read-only on settings: the toggle is restored in a finally.
    // (The metal-eat proof moved to CreatureBehaviors' RM_MetalEaterProof with the mechanic, KHORRAK_STEEL_DIET_TIER_1.)
    public static class RSW_BeastMechanicsProof
    {
        private sealed class HoardProbe : JobGiver_HoardScrap
        {
            public Job Give(Pawn p) => TryGiveJob(p);
        }

        private static ThingDef RaceWith<T>() where T : CompProperties =>
            DefDatabase<ThingDef>.AllDefsListForReading.FirstOrDefault(d => d.race != null && d.GetCompProperties<T>() != null);

        private static Pawn SpawnWild(ThingDef race, Map map, out IntVec3 cell, out string error)
        {
            cell = IntVec3.Invalid;
            error = null;
            PawnKindDef kind = DefDatabase<PawnKindDef>.AllDefsListForReading.FirstOrDefault(k => k.race == race);
            if (kind == null)
            {
                error = "no PawnKindDef for " + race.defName;
                return null;
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 40, c => c.Standable(map) && !c.Roofed(map)
                    && !map.areaManager.Home[c] && c.GetFirstItem(map) == null && c.GetEdifice(map) == null
                    && GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)).Count(a => a.InBounds(map) && a.Standable(map)
                        && !map.areaManager.Home[a] && a.GetFirstItem(map) == null && a.GetEdifice(map) == null) >= 6,
                    out cell))
            {
                error = "no open non-home cell";
                return null;
            }
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, fixedBiologicalAge: 5f,
                fixedChronologicalAge: 5f));
            GenSpawn.Spawn(p, cell, map);
            return p;
        }

        private static string JobText(Job j) =>
            j == null ? "none" : j.def.defName + " target=" + (j.targetA.Thing?.def.defName ?? "-")
                                 + " targetB=" + (j.targetB.Thing?.def.defName ?? "-");

        /// <summary>A rested, fed scrap-hoarder with its nest nearby and a hoardable item a few cells off: the giver
        /// must hand it RSW_HoardScrap (scrap, nest), and nothing with scrapHoardingEnabled off.</summary>
        public static string ProofHoard(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef race = RaceWith<CompProperties_ScrapHoarder>();
            if (map == null || race == null)
            {
                return "ERROR no map or no race with CompProperties_ScrapHoarder";
            }
            var props = race.GetCompProperties<CompProperties_ScrapHoarder>();
            ThingDef nestDef = DefDatabase<ThingDef>.GetNamedSilentFail(props.nestDef);
            ThingDef scrapDef = props.hoardableDefs?.Select(n => DefDatabase<ThingDef>.GetNamedSilentFail(n)).FirstOrDefault(d => d != null);
            if (nestDef == null || scrapDef == null)
            {
                return "ERROR nest " + props.nestDef + " or hoardable not loaded";
            }
            Pawn p = SpawnWild(race, map, out IntVec3 cell, out string err);
            if (p == null)
            {
                return "ERROR " + err;
            }
            Thing nest = null, scrap = null;
            bool was = RSW_BeastMechanicsSettings.scrapHoardingEnabled;
            try
            {
                if (!CellFinder.TryFindRandomCellNear(cell, map, 6, c => c.Standable(map) && c.GetFirstItem(map) == null
                        && c.GetEdifice(map) == null && !map.areaManager.Home[c] && c.DistanceTo(cell) >= 3f
                        && GenSpawn.CanSpawnAt(nestDef, c, map), out IntVec3 nestCell))
                {
                    return "ERROR no nest cell";
                }
                nest = GenSpawn.Spawn(nestDef, nestCell, map, WipeMode.Vanish);
                if (!CellFinder.TryFindRandomCellNear(cell, map, 6, c => c.Standable(map) && c.GetFirstItem(map) == null
                        && c.GetEdifice(map) == null && !map.areaManager.Home[c] && c.DistanceTo(nestCell) > 3f, out IntVec3 scrapCell))
                {
                    return "ERROR no scrap cell";
                }
                scrap = GenSpawn.Spawn(ThingMaker.MakeThing(scrapDef), scrapCell, map);
                if (p.needs?.food != null) p.needs.food.CurLevelPercentage = 1f;
                if (p.needs?.rest != null) p.needs.rest.CurLevel = 1f;
                var probe = new HoardProbe();
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = true;
                string on = JobText(probe.Give(p));
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = false;
                string off = JobText(probe.Give(p));
                return "hoarder=" + race.defName + " nest=" + nestDef.defName + " scrap=" + scrapDef.defName
                       + " on=" + on.Replace(' ', '|') + " off=" + off.Replace(' ', '|');
            }
            finally
            {
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = was;
                if (scrap != null && !scrap.Destroyed) scrap.Destroy();
                if (nest != null && !nest.Destroyed) nest.Destroy();
                if (!p.Destroyed) p.Destroy();
            }
        }

        /// <summary>TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE. Builds a player brine tank on an open cell, puts a fresh player grub in it
        /// through the tank's own TryAcceptThing, pours in 3 brine and drives the tank's own TickRare: first with the tank switched
        /// off (nothing may move), then on with short PROOF settings (0.5 day per jar, 1 day to white) for 1.1 days. Reports
        /// the jars dropped, brine left, the grub's white flag and what vanilla's TryGetAlternate now answers. Everything it
        /// spawns is destroyed and the settings restored before it returns.</summary>
        public static string ProofBrineTank(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef tankDef = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_TaozinBrineTank");
            PawnKindDef grubKind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RSW_TaozinGrub");
            ThingDef brineDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Brine");
            if (map == null || tankDef == null || grubKind == null || brineDef == null)
            {
                return "ERROR missing map/RSW_TaozinBrineTank/RSW_TaozinGrub/RM_Brine (tank needs mandrake.rsw.cuisine + Stillsand)";
            }
            ThingDef output = tankDef.GetModExtension<RSW_BrineTankExtension>()?.output;
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 40, c => GenSpawn.CanSpawnAt(tankDef, c, map) && c.Standable(map)
                    && c.GetFirstItem(map) == null && c.GetEdifice(map) == null
                    && GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)).All(a => a.InBounds(map) && a.Standable(map) && a.GetFirstItem(map) == null),
                    out IntVec3 cell))
            {
                return "ERROR no open cell for the tank";
            }
            // Jars already on the map before the proof are neither counted nor destroyed: only ones it made.
            var before = new System.Collections.Generic.HashSet<Thing>(output == null ? Enumerable.Empty<Thing>() : map.listerThings.ThingsOfDef(output));
            System.Func<System.Collections.Generic.List<Thing>> made = () => output == null ? new System.Collections.Generic.List<Thing>()
                : map.listerThings.ThingsOfDef(output).Where(t => !before.Contains(t)).ToList();
            bool wasOn = RSW_BeastMechanicsSettings.taozinBrineTankEnabled;
            float wasJar = RSW_BeastMechanicsSettings.taozinDaysPerJar, wasPale = RSW_BeastMechanicsSettings.taozinPaleDays;
            Building_RSW_BrineTank tank = null;
            Pawn grub = null;
            try
            {
                tank = (Building_RSW_BrineTank)GenSpawn.Spawn(ThingMaker.MakeThing(tankDef), cell, map, WipeMode.Vanish);
                tank.SetFaction(Faction.OfPlayer);
                grub = PawnGenerator.GeneratePawn(new PawnGenerationRequest(grubKind, Faction.OfPlayer));
                bool accepted = tank.TryAcceptThing(grub);
                CompRefuelable fuel = tank.GetComp<CompRefuelable>();
                fuel.Refuel(3f);
                RSW_BeastMechanicsSettings.taozinDaysPerJar = 0.5f;
                RSW_BeastMechanicsSettings.taozinPaleDays = 1f;
                int ticks = (int)(1.1f * GenDate.TicksPerDay) / GenTicks.TickRareInterval;

                RSW_BeastMechanicsSettings.taozinBrineTankEnabled = false;
                for (int i = 0; i < ticks; i++) tank.TickRare();
                int offJars = output == null ? -1 : made().Sum(t => t.stackCount);
                float offFuel = fuel.Fuel;
                bool offPale = grub.TryGetComp<RSW_CompTaozinBrining>()?.pale ?? false;

                RSW_BeastMechanicsSettings.taozinBrineTankEnabled = true;
                for (int i = 0; i < ticks; i++) tank.TickRare();
                int jars = output == null ? -1 : made().Sum(t => t.stackCount);
                RSW_CompTaozinBrining comp = grub.TryGetComp<RSW_CompTaozinBrining>();
                bool alt = grub.TryGetAlternate(out AlternateGraphic _, out int index);
                return "accepted=" + accepted + " off_jars=" + offJars + " off_brine=" + offFuel.ToString("0.##") + " off_pale=" + offPale
                       + " jars=" + jars + " brine=" + fuel.Fuel.ToString("0.##") + " pale=" + (comp?.pale ?? false)
                       + " alternate=" + (alt ? index.ToString() : "none");
            }
            finally
            {
                RSW_BeastMechanicsSettings.taozinBrineTankEnabled = wasOn;
                RSW_BeastMechanicsSettings.taozinDaysPerJar = wasJar;
                RSW_BeastMechanicsSettings.taozinPaleDays = wasPale;
                foreach (Thing jar in made()) if (!jar.Destroyed) jar.Destroy();
                if (tank != null && !tank.Destroyed) tank.Destroy();
                if (grub != null && !grub.Destroyed) grub.Destroy();
            }
        }
    }
}
