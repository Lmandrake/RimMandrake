using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    /// <summary>
    /// The zhool's red haze (RM_OcularJelly). Owner ruling 2026-10-15, by card (Transient/phase0_p3_questions.md Q2, "A.
    /// Rebuild it in our code"): the zhool leaves a faint reddish haze, and plants inside it slowly turn into one of the
    /// Contagion's own flesh-plants. Replaces the donor's Alpha Animals gas (AA_OcularGas, VEF/AlphaBehaviours code).
    ///
    /// No gas grid and no GameCondition. The vanilla gas grid holds a fixed set of gas types (no red haze among them), so
    /// the haze is drawn with the game's own fleck system: tinted puffs around the creature, emitted only while its map
    /// is the one on screen. Conversion is driven from THIS comp (the creature ticks every tick; a plant ticks only
    /// TickLong, so a plant comp could not do it): every scanIntervalTicks it samples cellsPerScan random cells inside
    /// hazeRadius (budgeted: a handful of cell lookups per zhool per scan, never a map sweep), and an eligible plant there
    /// turns with chance baseChance x the rate setting. A tree becomes treeResult, ground cover groundCoverResult, any
    /// other plant shrubResult (RM_ZhoolHazeKernel.Classify), keeping its growth.
    ///
    /// Where: only on a map whose biome is one of ours (its defining mod's packageId starts "mandrake."): biome mechanics
    /// are promised inside our biomes only (owner, 2026-10-15), and no cross-biome switch is built. Off our biomes the
    /// haze still shows and nothing turns. Never a plant of the Contagion's own (immunePlants and the three results), a
    /// stump, a special tree carrying comps, or (unless the crop switch is on) a player's sown crop.
    ///
    /// The readable sign: every conversion throws a red puff on the cell, and the first conversion in a day (game-wide)
    /// sends a message naming both plants, with the new plant as its look target. Nothing is deleted without a
    /// replacement standing in its cell. The haze touches no temperature, no pawn and no hediff (one kind of heat,
    /// planet-wide: it adds none).
    ///
    /// Mod Settings: zhoolHazeEnabled, zhoolHazeDensity (the look), zhoolConversionEnabled, zhoolConversionRate,
    /// zhoolConvertsCrops.
    /// </summary>
    public class CompProperties_ZhoolHaze : CompProperties
    {
        public float hazeRadius = 3.9f;
        public int hazeIntervalTicks = 90;
        public float hazePuffs = 1f;
        public FleckDef hazeFleck;
        public Color hazeColor = new Color(0.72f, 0.16f, 0.14f, 0.35f);
        public float hazeScale = 1.6f;

        public int scanIntervalTicks = 250;
        public int cellsPerScan = 2;
        public float baseChance = 0.04f;
        public int messageCooldownTicks = 60000;

        public ThingDef treeResult;
        public ThingDef groundCoverResult;
        public ThingDef shrubResult;
        public List<ThingDef> immunePlants = new List<ThingDef>();

        public CompProperties_ZhoolHaze()
        {
            compClass = typeof(CompZhoolHaze);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
                yield return e;
            if (treeResult?.plant == null) yield return "CompProperties_ZhoolHaze: treeResult is missing or not a plant";
            if (groundCoverResult?.plant == null) yield return "CompProperties_ZhoolHaze: groundCoverResult is missing or not a plant";
            if (shrubResult?.plant == null) yield return "CompProperties_ZhoolHaze: shrubResult is missing or not a plant";
            if (hazeRadius <= 0f || hazeRadius > GenRadial.MaxRadialPatternRadius)
                yield return "CompProperties_ZhoolHaze: hazeRadius out of range: " + hazeRadius;
            if (scanIntervalTicks < 60) yield return "CompProperties_ZhoolHaze: scanIntervalTicks below 60 is not budgeted";
            if (cellsPerScan < 1 || cellsPerScan > 8) yield return "CompProperties_ZhoolHaze: cellsPerScan must be 1..8";
        }
    }

    public class CompZhoolHaze : ThingComp
    {
        // Game-wide message throttle; RM_ZhoolHazeKernel.MessageDue resets it when the clock runs backwards (new game).
        private static int lastMessageTick = -1;

        private HashSet<ThingDef> immune;

        private CompProperties_ZhoolHaze Props => (CompProperties_ZhoolHaze)props;

        public override void CompTick()
        {
            if (!parent.Spawned) return;
            if (parent.IsHashIntervalTick(Props.hazeIntervalTicks))
                EmitHaze();
            if (parent.IsHashIntervalTick(Props.scanIntervalTicks))
                Scan();
        }

        private bool Breathing()
        {
            return parent is Pawn p && !p.Dead && !p.Downed;
        }

        private void EmitHaze()
        {
            if (!RM_ContagionSettings.zhoolHazeEnabled || !Breathing()) return;
            Map map = parent.Map;
            if (map != Find.CurrentMap) return;           // a look only: nobody sees an off-screen map
            int n = RM_ZhoolHazeKernel.Puffs(Props.hazePuffs, RM_ContagionSettings.zhoolHazeDensity, Rand.Value);
            for (int i = 0; i < n; i++)
            {
                Vector3 loc = parent.DrawPos + new Vector3(Rand.Range(-1f, 1f), 0f, Rand.Range(-1f, 1f)) * Props.hazeRadius * 0.6f;
                Puff(loc, map, Props.hazeScale, Props.hazeColor);
            }
        }

        private void Puff(Vector3 loc, Map map, float scale, Color color)
        {
            if (!loc.ShouldSpawnMotesAt(map)) return;
            FleckCreationData d = FleckMaker.GetDataStatic(loc, map, Props.hazeFleck ?? FleckDefOf.Smoke, scale);
            d.instanceColor = color;
            d.rotationRate = Rand.Range(-30f, 30f);
            d.velocityAngle = Rand.Range(0, 360);
            d.velocitySpeed = Rand.Range(0.1f, 0.3f);
            map.flecks.CreateFleck(d);
        }

        private static bool OurBiome(Map map)
        {
            string pid = map?.Biome?.modContentPack?.PackageId;
            return pid != null && pid.StartsWith("mandrake.");
        }

        private bool Immune(ThingDef def)
        {
            if (immune == null)
            {
                immune = new HashSet<ThingDef>(Props.immunePlants ?? new List<ThingDef>());
                if (Props.treeResult != null) immune.Add(Props.treeResult);
                if (Props.groundCoverResult != null) immune.Add(Props.groundCoverResult);
                if (Props.shrubResult != null) immune.Add(Props.shrubResult);
            }
            return immune.Contains(def);
        }

        private void Scan()
        {
            if (!RM_ContagionSettings.zhoolConversionEnabled || !Breathing()) return;
            Map map = parent.Map;
            if (!OurBiome(map)) return;
            int cells = GenRadial.NumCellsInRadius(Props.hazeRadius);
            float chance = RM_ZhoolHazeKernel.Chance(Props.baseChance, RM_ContagionSettings.zhoolConversionRate);
            for (int i = 0; i < Props.cellsPerScan; i++)
            {
                IntVec3 c = parent.Position + GenRadial.RadialPattern[Rand.Range(0, cells)];
                if (!c.InBounds(map)) continue;
                Plant plant = c.GetPlant(map);
                if (plant == null || plant.Destroyed) continue;
                ThingDef def = plant.def;
                bool eligible = RM_ZhoolHazeKernel.Eligible(true, true, Immune(def), def.plant.isStump,
                    def.comps != null && def.comps.Count > 0, plant.sown, RM_ContagionSettings.zhoolConvertsCrops);
                if (!eligible || !Rand.Chance(chance)) continue;
                Convert(plant, map);
            }
        }

        private void Convert(Plant old, Map map)
        {
            ThingDef def = old.def;
            HazeShape shape = RM_ZhoolHazeKernel.Classify(def.plant.IsTree,
                def.altitudeLayer == AltitudeLayer.FloorEmplacement, def.plant.maxMeshCount);
            ThingDef result = shape == HazeShape.Tree ? Props.treeResult
                : shape == HazeShape.GroundCover ? Props.groundCoverResult : Props.shrubResult;
            if (result == null || result == def) return;
            IntVec3 cell = old.Position;
            float growth = Mathf.Clamp(old.Growth, 0.15f, 1f);
            string oldLabel = old.LabelNoCount;
            Plant made = (Plant)ThingMaker.MakeThing(result);
            made.Growth = growth;
            old.Destroy(DestroyMode.Vanish);               // the replacement spawns in the same tick, same cell
            GenSpawn.Spawn(made, cell, map);
            for (int i = 0; i < 3; i++)
                Puff(cell.ToVector3Shifted() + new Vector3(Rand.Range(-0.3f, 0.3f), 0f, Rand.Range(-0.3f, 0.3f)), map, 1.1f,
                     new Color(Props.hazeColor.r, Props.hazeColor.g, Props.hazeColor.b, 0.7f));
            int now = Find.TickManager.TicksGame;
            if (RM_ZhoolHazeKernel.MessageDue(now, lastMessageTick, Props.messageCooldownTicks))
            {
                lastMessageTick = now;
                Messages.Message("A zhool's red haze has turned a " + oldLabel + " into " + made.LabelNoCount + ".",
                    new LookTargets(made), MessageTypeDefOf.NeutralEvent, historical: true);
            }
        }
    }
}
