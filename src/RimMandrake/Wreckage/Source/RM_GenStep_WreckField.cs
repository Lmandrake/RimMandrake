using System.Collections.Generic;
using System.Linq;
using System.Xml;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wreckage
{
    // SALVAGE_WRECKAGE_EVERYWHERE_1, design §3d / §3d-i. One weighted-list wreck field per
    // biome, replacing one GenStepDef per silhouette (GenStep_ScatterThings takes a single
    // thingDef). ALL NUMBERS PROVISIONAL.

    // One row of a field's <wrecks>, element-name-as-key like BiomeAnimalRecord
    // (RimSage RimWorld/BiomeAnimalRecord.cs): <RM_SomeWreck>1</RM_SomeWreck>. Never a <li>
    // form, so a roster counter that reads child elements sees every row.
    public class RM_WreckFieldEntry
    {
        public ThingDef thing;
        public float weight = 1f;

        public void LoadDataFromXmlCustom(XmlNode xmlRoot)
        {
            DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef(this, "thing", xmlRoot);
            weight = ParseHelper.FromString<float>(xmlRoot.FirstChild.Value);
        }
    }

    // The placement law's classes (design §3d-i): how long a wreck survives in a place sets
    // how many there are. A field names its class instead of restating numbers, so re-tuning
    // "High" re-tunes every sea floor. The class carries no loot shift: a tier is per-def,
    // set at resolve time, so the law's "+1 tier" lives in the weathering rows the class's
    // biomes use (Frozen for Riddled, for instance).
    public class RM_WreckDensityClassDef : Def
    {
        public FloatRange countPer10kCellsRange = FloatRange.Zero;
        public float clusterChance;
        public IntRange clusterSizeRange = new IntRange(2, 4);

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (countPer10kCellsRange.min < 0f || countPer10kCellsRange.max < countPer10kCellsRange.min)
            {
                yield return "countPer10kCellsRange " + countPer10kCellsRange + " is negative or inverted";
            }
            if (clusterChance < 0f || clusterChance > 1f)
            {
                yield return "clusterChance " + clusterChance + " outside [0, 1]";
            }
            if (clusterSizeRange.min < 2 || clusterSizeRange.max < clusterSizeRange.min)
            {
                yield return "clusterSizeRange " + clusterSizeRange + " must be 2 or more";
            }
        }
    }

    public class RM_GenStep_WreckField : GenStep_Scatterer
    {
        // Mod Settings key: one checkbox per distinct key (design §6), and the gate key
        // "Wreckage.field.<key>". The biome's own mod may also register a gate under the bare
        // key (TerminalBiomes registers "Scald" for its biome switch); unregistered reads on.
        public string settingsKey;

        // Older gate keys that now mean this field (the Scald's "Scald.S6").
        [NoTranslate]
        public List<string> gateAliases;

        public RM_WreckDensityClassDef densityClass;

        public List<RM_WreckFieldEntry> wrecks = new List<RM_WreckFieldEntry>();

        // Overrides of the class; unset (negative / zero) means "use the class".
        public float clusterChance = -1f;
        public IntRange clusterSizeRange = IntRange.Zero;

        // Same meaning as GenStep_ScatterThings' (tag-based, every cell within the radius).
        public float terrainValidationRadius;

        [NoTranslate]
        public List<string> terrainValidationAllowed;

        [NoTranslate]
        public List<string> terrainValidationDisallowed;

        private const int ClusterRadius = 4;

        [Unsaved(false)]
        private ThingDef pending;

        public RM_GenStep_WreckField()
        {
            // A field is confined to its terrain tag, so "no cell found" on a map with little
            // of that terrain is the expected end of the loop, not a warning.
            warnOnFail = false;
        }

        public override int SeedPart => 1612749307;

        private float EffectiveClusterChance =>
            RM_WreckageKernel.ClusterChance(clusterChance, densityClass?.clusterChance ?? 0f);

        private IntRange EffectiveClusterSize =>
            RM_WreckageKernel.UseOwnClusterSize(clusterSizeRange.max) ? clusterSizeRange : densityClass?.clusterSizeRange ?? new IntRange(2, 4);

        public IEnumerable<ThingDef> WreckDefs => wrecks.Where(w => w.thing != null).Select(w => w.thing);

        protected override bool ShouldSkipMap(Map map)
        {
            return base.ShouldSkipMap(map) || !RM_WreckageSettings.FieldActive(settingsKey);
        }

        public override void Generate(Map map, GenStepParams parms)
        {
            useFallback = false;
            if (ShouldSkipMap(map) || !wrecks.Any(w => w.thing != null && w.weight > 0f))
            {
                return;
            }
            usedSpots.Clear();
            int total = CalculateFinalCount(map);
            IntVec3 anchor = IntVec3.Invalid;
            RM_WreckageKernel.PlaceField(total,
                () =>
                {
                    pending = PickWreck();
                    if (!TryFindScatterCell(map, out anchor) || !TryPlace(pending, anchor, map))
                    {
                        return false;
                    }
                    usedSpots.Add(anchor);
                    return true;
                },
                () => Rand.Chance(EffectiveClusterChance),
                () => EffectiveClusterSize.RandomInRange,
                () =>
                {
                    ThingDef d = PickWreck();
                    return CellFinder.TryFindRandomCellNear(anchor, map, ClusterRadius,
                               c => CanPlace(d, c, map, out _), out IntVec3 c2, 30)
                           && TryPlace(d, c2, map);
                });
            usedSpots.Clear();
            pending = null;
        }

        private ThingDef PickWreck()
        {
            return wrecks.Where(w => w.thing != null && w.weight > 0f).RandomElementByWeight(w => w.weight).thing;
        }

        protected override int CalculateFinalCount(Map map)
        {
            float density = RM_WreckageSettings.wreckDensity;
            if (count >= 0)
            {
                return RM_WreckageKernel.FixedCount(count, density, GetPlacementFactor(map));
            }
            FloatRange range = countPer10kCellsRange.max > 0f
                ? countPer10kCellsRange
                : densityClass?.countPer10kCellsRange ?? FloatRange.Zero;
            float per10k = RM_WreckageKernel.Per10k(range.RandomInRange, density);
            if (per10k <= 0f)
            {
                return 0;
            }
            return RM_WreckageKernel.ScaledCount(CountFromPer10kCells(per10k, map), GetPlacementFactor(map));
        }

        protected override bool CanScatterAt(IntVec3 loc, Map map)
        {
            return pending != null && base.CanScatterAt(loc, map) && CanPlace(pending, loc, map, out _);
        }

        // Generate() places through TryPlace; this is the base's single-placement entry
        // (ForceScatterAt, a debug action), so it places one weighted wreck at loc if it fits.
        protected override void ScatterAt(IntVec3 loc, Map map, GenStepParams parms, int stackCount = 1)
        {
            ThingDef d = pending ?? PickWreck();
            if (!TryPlace(d, loc, map))
            {
                Log.Warning("[Wreckage] " + def?.defName + ": " + d + " does not fit at " + loc);
            }
        }

        private bool TryPlace(ThingDef def, IntVec3 loc, Map map)
        {
            if (!CanPlace(def, loc, map, out Rot4 rot))
            {
                return false;
            }
            Thing thing = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
            GenSpawn.Spawn(thing, loc, map, rot);
            Jacket(thing, map);
            return true;
        }

        // A jacketed weathering (Crystal-jacketed, Ice-locked) rings the wreck with its mineable
        // shell, corners included (a deconstructor may stand diagonally), so nothing can reach
        // it until a cell is mined. Cells already holding a building, item or pawn are left: a
        // cluster neighbour then shares its own wall, and nothing is ever wiped but plants and
        // filth. Returns the number of jacket cells laid.
        public static int Jacket(Thing wreck, Map map)
        {
            ThingDef shell = wreck.def.GetModExtension<RM_WreckWeathering>()?.weathering?.jacket;
            if (shell == null)
            {
                return 0;
            }
            int laid = 0;
            foreach (IntVec3 c in wreck.OccupiedRect().ExpandedBy(1).EdgeCells)
            {
                if (!c.InBounds(map) || c.GetEdifice(map) != null)
                {
                    continue;
                }
                if (c.GetThingList(map).Any(x => x.def.category != ThingCategory.Plant && x.def.category != ThingCategory.Filth))
                {
                    continue;
                }
                GenSpawn.Spawn(ThingMaker.MakeThing(shell), c, map, WipeMode.Vanish);
                laid++;
            }
            return laid;
        }

        private bool CanPlace(ThingDef def, IntVec3 loc, Map map, out Rot4 rot)
        {
            rot = Rot4.Invalid;
            if (def == null || !loc.InBounds(map) || !TerrainAllows(loc, map))
            {
                return false;
            }
            int start = def.rotatable ? Rand.Range(0, 4) : 0;
            int n = def.rotatable ? 4 : 1;
            for (int i = 0; i < n; i++)
            {
                Rot4 r = new Rot4((start + i) % 4);
                if (!GenAdj.OccupiedRect(loc, r, def.size).InBounds(map))
                {
                    continue;
                }
                // GenSpawn.CanSpawnAt covers bounds, walkability, the def's terrain affordance
                // (GenConstruct.CanBuildOnTerrain) and interaction cells (RimSage GenSpawn.cs:471).
                if (!GenSpawn.CanSpawnAt(def, loc, map, r))
                {
                    continue;
                }
                // Never wipe another wreck or a building: plants and filth only, as vanilla.
                if (GenSpawn.WouldWipeAnythingWith(loc, r, def, map,
                        x => x.def.category != ThingCategory.Plant && x.def.category != ThingCategory.Filth))
                {
                    continue;
                }
                rot = r;
                return true;
            }
            return false;
        }

        private bool TerrainAllows(IntVec3 loc, Map map)
        {
            if (terrainValidationRadius <= 0f)
            {
                return true;
            }
            foreach (IntVec3 c in GenRadial.RadialCellsAround(loc, terrainValidationRadius, useCenter: true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                TerrainDef t = c.GetTerrain(map);
                if (terrainValidationDisallowed != null && terrainValidationDisallowed.Any(t.HasTag))
                {
                    return false;
                }
                if (terrainValidationAllowed != null && !terrainValidationAllowed.All(t.HasTag))
                {
                    return false;
                }
            }
            return true;
        }

        public static IEnumerable<RM_GenStep_WreckField> AllFields()
        {
            foreach (GenStepDef d in DefDatabase<GenStepDef>.AllDefsListForReading)
            {
                if (d.genStep is RM_GenStep_WreckField f)
                {
                    yield return f;
                }
            }
        }
    }

    // Gate keys need the GenStepDefs, which do not exist in a Mod constructor, so they are
    // registered once the defs are loaded. Registering after the Mod constructors also means
    // an alias replaces any older registration of the same key (Register replaces).
    [StaticConstructorOnStartup]
    public static class RM_WreckFieldStartup
    {
        static RM_WreckFieldStartup()
        {
            foreach (GenStepDef d in DefDatabase<GenStepDef>.AllDefsListForReading)
            {
                if (!(d.genStep is RM_GenStep_WreckField f))
                {
                    continue;
                }
                if (f.settingsKey.NullOrEmpty())
                {
                    Log.Error("[Wreckage] " + d.defName + ": RM_GenStep_WreckField with no settingsKey");
                    continue;
                }
                if (!f.wrecks.Any(w => w.thing != null && w.weight > 0f))
                {
                    Log.Error("[Wreckage] " + d.defName + ": no resolvable wreck with weight > 0");
                }
                if (f.densityClass == null && f.count < 0 && f.countPer10kCellsRange.max <= 0f)
                {
                    Log.Error("[Wreckage] " + d.defName + ": no densityClass and no count of its own");
                }
                Register(f);
            }
        }

        private static void Register(RM_GenStep_WreckField f)
        {
            string key = f.settingsKey;
            RM_MechanicGates.Register("Wreckage.field." + key, () => RM_WreckageSettings.FieldActive(key));
            if (f.gateAliases == null)
            {
                return;
            }
            foreach (string alias in f.gateAliases)
            {
                RM_MechanicGates.Register(alias, () => RM_WreckageSettings.FieldActive(key));
            }
        }
    }
}
