using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    // ══════════════════════════════════════════════════════════════════
    // PYRELANDS_STRUCK_GLASS_RITE_BUILD_1 — the engine under the Struck Glass rite (Zizzik, feeding by breakage).
    //
    // Owner, typed 2026-10-01: "Struck Glass. Make a ~ring of the lightning glass, and then during any lightning storm step on
    // them violently to break them. Triggers a REALLY powerful lightning blast somewhere randomly on the map (maybe even the
    // ship) and utter delight within the god." Input revised by card 2026-10-15: glass sand (RM_GlassSand, the Stillsand item).
    // Spec: design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md §6 R1; register
    // design/Jawa/salvation_rites_2026-10-01.md B9.
    //
    // The rite itself (precept, pattern, behaviour, outcome, memories) is the campaign tier's XML in mandrake.rut.rites
    // (Defs/RUT_StruckGlass.xml); this file is the franchise-free engine it points at and never names a faith — the same split
    // as the Joining Water (GelatinousSlime/Source/JoiningWater.cs) and the Nine Faults.
    //
    //   RM_StruckGlassRing                        a ring of glass sand on the ground; CompRefuelable holds the sand (colonists
    //                                             haul it in), the rite stamps it all out. One old ring is laid on every new
    //                                             Pyrelands map (GenStep_StruckGlassRing, BiomeDef extraGenSteps); more can be
    //                                             laid anywhere (Ideology tab), since the rite works on any map in a storm.
    //   RM_RitualObligationTargetWorker_StruckGlassRing   the rite may start only at a FULL ring during a lightning storm
    //                                             (the reason line says which is missing).
    //   RM_RitualOutcomeEffectWorker_StruckGlass  empties the ring and calls one really powerful strike at a random cell
    //                                             (the ship included unless the setting forbids buildings); the outcome
    //                                             letter names where it fell and what it hit. Cohesion only: memories come
    //                                             from the XML outcome chances; no hediff, no stat, no power.
    //
    // "Lightning storm" = the current weather has a WeatherEventMaker whose event is a lightning flash or strike (vanilla
    // thunderstorm, dry thunderstorm, Pyrelands Cinderfall, any modded weather built the same way). All numbers PROVISIONAL.
    // ══════════════════════════════════════════════════════════════════
    public class RM_StruckGlassExtension : DefModExtension
    {
        /// <summary>Fraction of the explosion cells that catch fire (vanilla lightning: a 1.9-cell Flame burst).</summary>
        public float fireChance = 0.6f;
        public DamageDef damage;
    }

    public static class RM_StruckGlass
    {
        public const string RingDefName = "RM_StruckGlassRing";

        public static ThingDef RingDef => DefDatabase<ThingDef>.GetNamedSilentFail(RingDefName);

        public static bool Enabled => PyrelandsMechanicsGate.On && RM_PyrelandsSettings.struckGlassEnabled;

        public static bool IsLightningStorm(Map map)
        {
            WeatherDef w = map?.weatherManager?.curWeather;
            if (w?.eventMakers == null) return false;
            foreach (WeatherEventMaker m in w.eventMakers)
                if (m?.eventClass != null && typeof(WeatherEvent_LightningFlash).IsAssignableFrom(m.eventClass)) return true;
            return false;
        }

        /// <summary>Null when the ring can be used now, else the reason line shown on the ritual gizmo.</summary>
        public static string BlockReason(Thing ring)
        {
            if (!Enabled) return "The Struck Glass is switched off in the Pyrelands mod settings.";
            CompRefuelable fuel = ring.TryGetComp<CompRefuelable>();
            if (fuel != null && !fuel.IsFull)
                return "The ring is not whole: it needs " + fuel.Props.fuelCapacity.ToString("0") + " glass sand (it holds "
                       + fuel.Fuel.ToString("0") + "). Glass sand comes from shovelling sand.";
            if (!IsLightningStorm(ring.Map)) return "There is no lightning storm. The glass is only stamped out under lightning.";
            return null;
        }

        /// <summary>The random cell the strike falls on: anywhere in the open or under a built roof, never under overhead
        /// rock. With buildings forbidden, a cell with no building within the blast; falls back to any cell rather than
        /// failing the rite.</summary>
        public static IntVec3 PickStrikeCell(Map map, float radius, bool mayHitBuildings)
        {
            bool Ok(IntVec3 c)
            {
                if (!c.InBounds(map) || !c.Standable(map)) return false;
                RoofDef roof = c.GetRoof(map);
                return roof == null || !roof.isThickRoof;
            }
            if (!mayHitBuildings)
            {
                for (int i = 0; i < 200; i++)
                {
                    IntVec3 c = CellFinderLoose.RandomCellWith(Ok, map, 50);
                    if (!c.IsValid) break;
                    bool clear = true;
                    foreach (IntVec3 n in GenRadial.RadialCellsAround(c, radius, true))
                    {
                        if (!n.InBounds(map)) continue;
                        foreach (Thing t in n.GetThingList(map))
                            if (t.def.category == ThingCategory.Building && t.def.building != null && !t.def.building.isNaturalRock)
                            { clear = false; break; }
                        if (!clear) break;
                    }
                    if (clear) return c;
                }
            }
            IntVec3 any = CellFinderLoose.RandomCellWith(Ok, map, 1000);
            return any.IsValid ? any : CellFinder.RandomCell(map);
        }
    }

    public class GenStep_StruckGlassRing : GenStep
    {
        public ThingDef ringDef;
        public override int SeedPart => 0x57C61A5;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (ringDef == null || !RM_PyrelandsSettings.struckGlassRingOnNewMaps || !PyrelandsMechanicsGate.On) return;
            for (int pass = 0; pass < 2; pass++)
            {
                for (int attempt = 0; attempt < 120; attempt++)
                {
                    IntVec3 c = CellFinderLoose.RandomCellWith(x => x.InBounds(map), map, 50);
                    if (!c.IsValid || !Fits(map, c, pass == 0)) continue;
                    Thing ring = ThingMaker.MakeThing(ringDef);
                    // the player can only haul sand into a ring of their own (RefuelWorkGiverUtility.CanRefuel)
                    if (map.IsPlayerHome || map.ParentFaction == Faction.OfPlayer) ring.SetFaction(Faction.OfPlayer);
                    GenSpawn.Spawn(ring, c, map);
                    return;
                }
            }
            Log.Warning("[Pyrelands] Struck Glass: no cell found for the old glass ring.");
        }

        /// <summary>First pass wants bare ash (the ruled find: "an old stamped ring on bare ash"); the second takes any dry ground.</summary>
        private static bool Fits(Map map, IntVec3 c, bool wantAsh)
        {
            foreach (IntVec3 n in GenAdj.OccupiedRect(c, Rot4.North, new IntVec2(3, 3)))
            {
                if (!n.InBounds(map) || !n.Standable(map) || n.GetEdifice(map) != null || n.Roofed(map)) return false;
                TerrainDef t = n.GetTerrain(map);
                if (t == null || t.IsWater) return false;
                if (wantAsh && !t.defName.StartsWith("RM_FE_Ash")) return false;
            }
            return true;
        }
    }

    public class RM_RitualObligationTargetWorker_StruckGlassRing : RitualObligationTargetFilter
    {
        public RM_RitualObligationTargetWorker_StruckGlassRing() { }
        public RM_RitualObligationTargetWorker_StruckGlassRing(RitualObligationTargetFilterDef def) : base(def) { }

        public override IEnumerable<TargetInfo> GetTargets(RitualObligation obligation, Map map)
        {
            ThingDef ring = RM_StruckGlass.RingDef;
            if (ring == null || !RM_StruckGlass.Enabled) yield break;
            foreach (Thing t in map.listerThings.ThingsOfDef(ring)) yield return t;
        }

        protected override RitualTargetUseReport CanUseTargetInternal(TargetInfo target, RitualObligation obligation)
        {
            // plain false for everything else: a fail REASON would show a disabled ritual gizmo on every thing
            if (!target.HasThing || target.Thing.def.defName != RM_StruckGlass.RingDefName) return false;
            if (target.Thing.Faction != Faction.OfPlayer) return "The ring is not yours: claim it first.";
            string why = RM_StruckGlass.BlockReason(target.Thing);
            return why == null ? (RitualTargetUseReport)true : why;
        }

        public override IEnumerable<string> GetTargetInfos(RitualObligation obligation)
        {
            yield return "a full ring of glass sand, during a lightning storm";
        }
    }

    public class RM_RitualOutcomeEffectWorker_StruckGlass : RitualOutcomeEffectWorker_FromQuality
    {
        public RM_RitualOutcomeEffectWorker_StruckGlass() { }
        public RM_RitualOutcomeEffectWorker_StruckGlass(RitualOutcomeEffectDef def) : base(def) { }

        protected override void ApplyExtraOutcome(Dictionary<Pawn, int> totalPresence, LordJob_Ritual jobRitual,
            RitualOutcomePossibility outcome, out string extraOutcomeDesc, ref LookTargets letterLookTargets)
        {
            extraOutcomeDesc = null;
            Thing ring = jobRitual?.selectedTarget.Thing;
            Map map = jobRitual?.Map ?? ring?.Map;
            if (map == null || !RM_StruckGlass.Enabled) return;
            CompRefuelable fuel = ring?.TryGetComp<CompRefuelable>();
            if (fuel != null && fuel.Fuel > 0f) fuel.ConsumeFuel(fuel.Fuel);   // the glass is stamped out, all of it

            RM_StruckGlassExtension ext = def.GetModExtension<RM_StruckGlassExtension>() ?? new RM_StruckGlassExtension();
            float radius = RM_PyrelandsSettings.struckGlassBlastRadius;
            IntVec3 cell = RM_StruckGlass.PickStrikeCell(map, radius, RM_PyrelandsSettings.struckGlassMayHitBuildings);

            string hit = DescribeHits(map, cell, radius);
            map.weatherManager.eventHandler.AddEvent(new WeatherEvent_LightningStrike(map, cell));   // bolt, flash, thunder
            GenExplosion.DoExplosion(cell, map, radius, ext.damage ?? DamageDefOf.Bomb, null,
                chanceToStartFire: ext.fireChance, damageFalloff: true, screenShakeFactor: 2f);

            extraOutcomeDesc = "The glass broke under their feet and the sky answered: lightning fell " + Where(map, cell, ring)
                               + (hit.Length > 0 ? ", striking " + hit + "." : ", on open ground.");
            letterLookTargets = new LookTargets(new TargetInfo(cell, map));
        }

        private static string Where(Map map, IntVec3 cell, Thing ring)
        {
            string s = "at (" + cell.x + ", " + cell.z + ")";
            if (ring != null && ring.Spawned) s += ", " + ((int)ring.Position.DistanceTo(cell)) + " cells from the ring";
            if (cell.Roofed(map)) s += ", through a roof";
            return s;
        }

        /// <summary>What stood in the blast before it went off, for the letter.</summary>
        private static string DescribeHits(Map map, IntVec3 cell, float radius)
        {
            HashSet<Thing> seen = new HashSet<Thing>();
            List<string> pawns = new List<string>();
            int buildings = 0;
            foreach (IntVec3 n in GenRadial.RadialCellsAround(cell, radius, true))
            {
                if (!n.InBounds(map)) continue;
                foreach (Thing t in n.GetThingList(map))
                {
                    if (!seen.Add(t)) continue;
                    if (t is Pawn p) { if (pawns.Count < 4) pawns.Add(p.LabelShort); }
                    else if (t.def.category == ThingCategory.Building && t.def.building != null && !t.def.building.isNaturalRock) buildings++;
                }
            }
            StringBuilder sb = new StringBuilder();
            if (pawns.Count > 0) sb.Append(string.Join(", ", pawns));
            if (buildings > 0) sb.Append(sb.Length > 0 ? " and " : "").Append(buildings).Append(buildings == 1 ? " structure" : " structures");
            return sb.ToString();
        }
    }
}
