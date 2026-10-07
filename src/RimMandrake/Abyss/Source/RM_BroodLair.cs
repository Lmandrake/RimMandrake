using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Abyss
{
    // ABYSS_LIGHTFALL_BROOD_WRECK_1 — the brood lair: a sleeping, landscape-sized summ brood-mother coiled
    // round her clutch, a bone field, and a wrecked rescue gravship driven into the wall, all on one map,
    // all under ONE wake meter (RM_BroodWakeLogic.cs holds the rules; this file is the Verse half).
    //
    // WHERE IT APPEARS. RM_GenStep_BroodLair is added to every surface map (MapCommonBase patch) and
    // self-gates: it builds only when the map's tile carries the RM_BroodLair mutator (the free tier's
    // route on a generated planet) or its landmark def carries RM_BroodLairExtension (the campaign's
    // route: UtinniPatches puts the extension on RUT_Lightfall, because the frozen world's tile 9023
    // already holds its landmark and a mutator added to the LandmarkDef now would never reach it).
    //
    // NOT FANTASY DRAGONS (owner, typed 2026-10-01): no fire, no hoard, no "dragon" in any text.

    /// <summary>Marks a LandmarkDef whose map holds a brood lair.</summary>
    public class RM_BroodLairExtension : DefModExtension { }

    public class RM_MapComponent_BroodWake : MapComponent
    {
        public BroodWakeLogic wake = new BroodWakeLogic();
        public bool lairBuilt;
        public Thing mother;          // the sleeping building while asleep
        public IntVec3 motherCell = IntVec3.Invalid;
        private int lastDecayTick = -1;

        private const int Interval = 250;
        private const float LightRadius = 14f;

        public RM_MapComponent_BroodWake(Map map) : base(map) { }

        public static RM_MapComponent_BroodWake For(Map map)
        {
            return map?.GetComponent<RM_MapComponent_BroodWake>();
        }

        /// <summary>Feed the meter from anywhere (salvage, the egg). <paramref name="why"/> names the source in the message.</summary>
        public void Notify(float amount, string why)
        {
            if (!lairBuilt || !RM_AbyssSettings.broodLairEnabled) return;
            Announce(wake.Add(amount), why);
        }

        public override void MapComponentTick()
        {
            if (!lairBuilt || wake.awake) return;
            int now = Find.TickManager.TicksGame;
            if (now % Interval != 0) return;
            if (!RM_AbyssSettings.broodLairEnabled) return;

            // a crossing held back for its warning wakes her now
            Announce(wake.Recheck(), "too much was taken");
            if (wake.awake) return;

            // light near the sleeper: every lit glower inside the radius
            if (motherCell.IsValid)
            {
                int lights = 0;
                List<Thing> glowers = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
                for (int i = 0; i < glowers.Count; i++)
                {
                    CompGlower g = glowers[i].TryGetComp<CompGlower>();
                    if (g != null && g.Glows && glowers[i].Position.InHorDistOf(motherCell, LightRadius)) lights++;
                }
                if (lights > 0) Announce(wake.Add(BroodWakeLogic.LightPerSourcePerRare * lights), "the light");
            }

            if (lastDecayTick < 0) lastDecayTick = now;
            float days = (now - lastDecayTick) / (float)GenDate.TicksPerDay;
            if (days >= 0.25f)
            {
                Announce(wake.Decay(days), "too much was taken");
                lastDecayTick = now;
            }
        }

        private void Announce(BroodStage sign, string why)
        {
            if (sign == BroodStage.Asleep) return;
            LookTargets at = mother != null && mother.Spawned ? new LookTargets(mother) : (motherCell.IsValid ? new LookTargets(new TargetInfo(motherCell, map)) : null);
            SoundDef rumble = DefDatabase<SoundDef>.GetNamedSilentFail("Thunder_OffMap");
            switch (sign)
            {
                case BroodStage.Stirring:
                    Messages.Message("The brood-mother shifts in her sleep (" + why + "). Her throat-sacs flicker.", at, MessageTypeDefOf.ThreatSmall);
                    rumble?.PlayOneShotOnCamera(map);
                    break;
                case BroodStage.Rumbling:
                    Find.LetterStack.ReceiveLetter("She is close to waking",
                        "A low rumble runs through the stone under the brood-mother and her breathing has changed (" + why + "). "
                        + "Whatever you are taking from this place, you have taken a lot of it. If she wakes, nothing you carry will stop her.",
                        LetterDefOf.ThreatSmall, at);
                    rumble?.PlayOneShotOnCamera(map);
                    if (map == Find.CurrentMap) Find.CameraDriver.shaker.DoShake(1.5f);
                    break;
                case BroodStage.Awake:
                    WakeMother(why);
                    break;
            }
        }

        private void WakeMother(string why)
        {
            IntVec3 cell = motherCell;
            if (mother != null && mother.Spawned)
            {
                cell = mother.Position;
                mother.DeSpawn();
            }
            mother = null;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_SummAllRender");
            if (kind == null || !cell.IsValid) return;
            Pawn she = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer,
                map.Tile, fixedBiologicalAge: 150f, fixedChronologicalAge: 150f));
            she.Name = new NameSingle("the All-Render");
            IntVec3 spot = CellFinder.StandableCellNear(cell, map, 6f);
            if (!spot.IsValid) spot = cell;
            GenSpawn.Spawn(she, spot, map);
            HediffDef awake = DefDatabase<HediffDef>.GetNamedSilentFail("RM_BroodMotherAwake");
            if (awake != null) she.health.AddHediff(awake);
            she.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.ManhunterPermanent, "woken", forced: true);
            if (map == Find.CurrentMap) Find.CameraDriver.shaker.DoShake(4f);
            Find.LetterStack.ReceiveLetter("Summ the All-Render is awake",
                "Too much was taken (" + why + "). The brood-mother has uncoiled: a summ the size of the land around her, "
                + "and nothing you have will bring her down. Do not fight. Get to the ship and go.",
                LetterDefOf.ThreatBig, she);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lairBuilt, "lairBuilt", false);
            Scribe_References.Look(ref mother, "mother");
            Scribe_Values.Look(ref motherCell, "motherCell", IntVec3.Invalid);
            Scribe_Values.Look(ref lastDecayTick, "lastDecayTick", -1);
            Scribe_Values.Look(ref wake.pressure, "wakePressure", 0f);
            Scribe_Values.Look(ref wake.peak, "wakePeak", 0f);
            Scribe_Values.Look(ref wake.threshold, "wakeThreshold", 1f);
            Scribe_Values.Look(ref wake.stirAnnounced, "wakeStir", false);
            Scribe_Values.Look(ref wake.rumbleAnnounced, "wakeRumble", false);
            Scribe_Values.Look(ref wake.awake, "wakeAwake", false);
        }
    }

    /// <summary>The sleeping brood-mother. Landscape-sized (a 7x7 impassable footprint drawn ~15 cells across).
    /// Any harm done to her wakes her at once; she takes none of it.</summary>
    public class Building_RM_BroodMother : Building
    {
        public override void PreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            absorbed = true;
            if (Spawned && dinfo.Def != null && dinfo.Def.harmsHealth)
            {
                RM_MapComponent_BroodWake c = RM_MapComponent_BroodWake.For(Map);
                if (c != null) c.Notify(10f, "she was struck");
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            RM_MapComponent_BroodWake c = Spawned ? RM_MapComponent_BroodWake.For(Map) : null;
            string line = c != null ? c.wake.Describe() : "Deeply asleep.";
            return s.NullOrEmpty() ? line : s + "\n" + line;
        }
    }

    public class RM_GenStep_BroodLair : GenStep
    {
        public ThingDef motherDef;
        public ThingDef eggDef;
        public ThingDef greatBoneDef;
        public ThingDef boneDef;
        public ThingDef wreckDef;
        public IntRange eggCount = new IntRange(2, 3);
        public IntRange greatBones = new IntRange(4, 6);
        public IntRange boneHeaps = new IntRange(5, 9);
        public IntRange boneHeapSize = new IntRange(15, 40);

        public override int SeedPart => 715640219;

        public static bool MapWantsLair(Map map)
        {
            Tile t = map?.TileInfo;
            if (t == null) return false;
            if (t.Landmark?.def != null && t.Landmark.def.HasModExtension<RM_BroodLairExtension>()) return true;
            if (t.Mutators != null)
                for (int i = 0; i < t.Mutators.Count; i++)
                    if (t.Mutators[i].defName == "RM_BroodLair") return true;
            return false;
        }

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_AbyssSettings.broodLairEnabled || !MapWantsLair(map)) return;
            RM_MapComponent_BroodWake comp = RM_MapComponent_BroodWake.For(map);
            if (comp == null || comp.lairBuilt || motherDef == null) return;

            if (!TryFindLairCenter(map, out IntVec3 center)) return;
            comp.wake.threshold = BroodWakeLogic.RollThreshold(Rand.Value, RM_AbyssSettings.broodSleepDepth);
            comp.lairBuilt = true;

            ClearRect(map, CellRect.CenteredOn(center, 4));
            Thing mother = GenSpawn.Spawn(ThingMaker.MakeThing(motherDef), center, map, Rot4.South);
            comp.mother = mother;
            comp.motherCell = center;

            // the clutch, against her coils
            if (eggDef != null)
            {
                int n = eggCount.RandomInRange;
                for (int i = 0; i < n; i++)
                    if (CellFinder.TryFindRandomCellNear(center, map, 7, c => c.Standable(map) && !mother.OccupiedRect().Contains(c) && c.GetFirstItem(map) == null, out IntVec3 ec))
                        GenSpawn.Spawn(ThingMaker.MakeThing(eggDef), ec, map);
            }

            // the bone field, a ring further out
            if (greatBoneDef != null)
            {
                int n = greatBones.RandomInRange;
                for (int i = 0; i < n; i++)
                    if (TryCellInRing(map, center, 10f, 20f, 1, out IntVec3 bc))
                        GenSpawn.Spawn(ThingMaker.MakeThing(greatBoneDef), bc, map, Rot4.Random);
            }
            if (boneDef != null)
            {
                int n = boneHeaps.RandomInRange;
                for (int i = 0; i < n; i++)
                    if (TryCellInRing(map, center, 8f, 22f, 0, out IntVec3 hc))
                    {
                        Thing heap = ThingMaker.MakeThing(boneDef);
                        heap.stackCount = Mathf.Min(boneHeapSize.RandomInRange, boneDef.stackLimit);
                        GenSpawn.Spawn(heap, hc, map);
                    }
            }

            // the rescue ship in the wall, inside her lair
            if (wreckDef != null && RM_AbyssSettings.wreckEnabled && TryCellInRing(map, center, 12f, 24f, 4, out IntVec3 wc))
            {
                ClearRect(map, CellRect.CenteredOn(wc, 4));
                Thing wreck = ThingMaker.MakeThing(wreckDef);
                wreck.SetFaction(Faction.OfPlayer);   // so salvage bills can be placed without a claim step
                GenSpawn.Spawn(wreck, wc, map, Rot4.South);
            }
        }

        private static bool TryFindLairCenter(Map map, out IntVec3 center)
        {
            IntVec3 mid = map.Center;
            for (int radius = 20; radius <= 60; radius += 10)
            {
                if (CellFinder.TryFindRandomCellNear(mid, map, radius, c => RoomyEnough(map, c, 4), out center)) return true;
            }
            center = IntVec3.Invalid;
            return false;
        }

        private static bool RoomyEnough(Map map, IntVec3 c, int half)
        {
            CellRect r = CellRect.CenteredOn(c, half);
            if (!r.InBounds(map) || r.minX < 10 || r.minZ < 10 || r.maxX > map.Size.x - 10 || r.maxZ > map.Size.z - 10) return false;
            foreach (IntVec3 x in r)
            {
                TerrainDef t = x.GetTerrain(map);
                if (t == null || t.passability == Traversability.Impassable || t.IsWater) return false;
            }
            return true;
        }

        private static bool TryCellInRing(Map map, IntVec3 center, float min, float max, int roomHalf, out IntVec3 cell)
        {
            for (int tries = 0; tries < 60; tries++)
            {
                float ang = Rand.Range(0f, 360f);
                float d = Rand.Range(min, max);
                IntVec3 c = center + new Vector3(Mathf.Cos(ang * Mathf.Deg2Rad) * d, 0f, Mathf.Sin(ang * Mathf.Deg2Rad) * d).ToIntVec3();
                if (!c.InBounds(map)) continue;
                if (roomHalf > 0 ? RoomyEnough(map, c, roomHalf) : (c.Standable(map) && c.GetFirstItem(map) == null && c.GetEdifice(map) == null))
                {
                    cell = c;
                    return true;
                }
            }
            cell = IntVec3.Invalid;
            return false;
        }

        // rock and plants out of the footprint; terrain is left as the chasm made it
        private static void ClearRect(Map map, CellRect r)
        {
            foreach (IntVec3 c in r.ClipInsideMap(map))
            {
                List<Thing> things = c.GetThingList(map);
                for (int i = things.Count - 1; i >= 0; i--)
                {
                    Thing t = things[i];
                    if (t is Pawn) continue;
                    if (t.def.category == ThingCategory.Building || t.def.category == ThingCategory.Plant || t.def.category == ThingCategory.Item)
                        t.Destroy(DestroyMode.Vanish);
                }
                map.roofGrid.SetRoof(c, null);
            }
        }
    }
}
