using System.Collections.Generic;
using System.Text;
using RimMandrake.LoreStages;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ScarlandsLadder
{
    // WARSCAR_PILGRIM_CAMPS_1 (design warscar_turn3_development_2026-09-30.md section 2.10; texts are
    // warscar_bedazzle_cast_2026-09-30.md section 6B, ruled final by card 2026-09-30). The missing caller
    // of GameComponent_LoreStage.AdvanceStage("Scarlands"): a pilgrim's journal, found at a camp on a
    // RUT_Scarlands map beside the body of the one who wrote it. Reading it (once per journal) moves the
    // Scarlands ladder up one rung, and the letter quotes the journal page that belongs to the new rung.
    // A sixth journal, past the top rung, says nothing new. The body stays: pilgrims never vanish, they
    // are found.

    public class ScarlandsLadderSettings : ModSettings
    {
        public static bool campsEnabled = true;             // camps generate on new RUT_Scarlands maps
        public static float campsPerMap = 1f;               // 0-3, new maps
        public static bool journalsAdvanceLadder = true;    // reading a journal moves the Scarlands ladder

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref campsEnabled, "campsEnabled", true);
            Scribe_Values.Look(ref campsPerMap, "campsPerMap", 1f);
            Scribe_Values.Look(ref journalsAdvanceLadder, "journalsAdvanceLadder", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.CheckboxLabeled("Pilgrim camps on Scarlands maps", ref campsEnabled,
                "A cold fire, a bedroll, the pilgrim who never left, and a journal. New maps only.");
            if (campsEnabled)
            {
                list.Label("Camps per map: up to " + Mathf.RoundToInt(campsPerMap) + " (new maps)");
                campsPerMap = list.Slider(campsPerMap, 0f, 3f);
            }
            list.CheckboxLabeled("Reading a pilgrim's journal teaches the Scarlands", ref journalsAdvanceLadder,
                "Each journal read moves the Scarlands' description one stage further. Off: the journals can "
              + "still be read, but teach nothing.");
            list.End();
        }
    }

    public class ScarlandsLadderMod : Mod
    {
        public static ScarlandsLadderSettings settings;

        public ScarlandsLadderMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ScarlandsLadderSettings>();
        }

        public override string SettingsCategory()
        {
            return "Scarlands Ladder";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    /// <summary>The journal page that belongs to each rung, 1-based: pages[n - 1] is quoted when a
    /// read moves the ladder to rung n.</summary>
    public class RUT_PilgrimJournalExtension : DefModExtension
    {
        public List<string> pages = new List<string>();
    }

    public class CompProperties_RUT_PilgrimJournal : CompProperties
    {
        public CompProperties_RUT_PilgrimJournal()
        {
            compClass = typeof(CompRUT_PilgrimJournal);
        }
    }

    public class CompRUT_PilgrimJournal : ThingComp
    {
        public bool read;

        public override void PostExposeData()
        {
            Scribe_Values.Look(ref read, "rutPilgrimJournalRead", false);
        }

        public override string CompInspectStringExtra()
        {
            return read ? "Read." : "Unread.";
        }
    }

    public class CompUseEffect_RUT_ReadPilgrimJournal : CompUseEffect
    {
        public override void DoEffect(Pawn usedBy)
        {
            base.DoEffect(usedBy);
            RUT_PilgrimJournals.Read(parent, usedBy, true);
        }

        public override AcceptanceReport CanBeUsedBy(Pawn p)
        {
            CompRUT_PilgrimJournal c = parent.TryGetComp<CompRUT_PilgrimJournal>();
            if (c != null && c.read)
            {
                return "Already read.";
            }
            return base.CanBeUsedBy(p);
        }
    }

    public static class RUT_PilgrimJournals
    {
        public const string Ladder = "Scarlands";

        /// <summary>Reads one journal. Returns "STAGE n moved=True|False" or "ALREADY READ".</summary>
        public static string Read(Thing journal, Pawn reader, bool tell)
        {
            CompRUT_PilgrimJournal comp = journal?.TryGetComp<CompRUT_PilgrimJournal>();
            if (comp == null || comp.read)
            {
                return "ALREADY READ";
            }
            comp.read = true;
            GameComponent_LoreStage gc = Current.Game?.GetComponent<GameComponent_LoreStage>();
            if (!ScarlandsLadderSettings.journalsAdvanceLadder || gc == null)
            {
                if (tell)
                {
                    Messages.Message("The journal's pages are water-stained past reading.", journal, MessageTypeDefOf.NeutralEvent);
                }
                return "STAGE " + (gc?.GetStage(Ladder) ?? -1) + " moved=False (setting off or no lore component)";
            }
            bool moved = gc.AdvanceStage(Ladder);
            int stage = gc.GetStage(Ladder);
            if (tell)
            {
                List<string> pages = journal.def.GetModExtension<RUT_PilgrimJournalExtension>()?.pages;
                if (moved && pages != null && stage >= 1 && stage <= pages.Count)
                {
                    string who = reader != null ? reader.LabelShort : "Someone";
                    Find.LetterStack.ReceiveLetter("A pilgrim's journal",
                        who + " reads the last page that is still legible:\n\n\"" + pages[stage - 1] + "\"",
                        LetterDefOf.NeutralEvent, journal);
                }
                else
                {
                    Messages.Message("The journal says nothing the Scarlands have not already taught.", journal,
                        MessageTypeDefOf.NeutralEvent);
                }
            }
            return "STAGE " + stage + " moved=" + moved;
        }

        /// <summary>Bridge proof (jawa/static_call): resets the Scarlands ladder to 0, then reads
        /// <paramref name="count"/> fresh journals in sequence beside the first free colonist and
        /// destroys them. "STAGES 1,2,3,4,5,5 moved T,T,T,T,T,F | desc Crater fields and slag ...".
        /// Mutates the save's ladder: a test-map proof only.</summary>
        public static string ProofReadSequence(Map map, int count)
        {
            GameComponent_LoreStage gc = Current.Game?.GetComponent<GameComponent_LoreStage>();
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_PilgrimJournal");
            if (map == null || gc == null || def == null)
            {
                return "REFUSED: map " + (map != null) + " lore " + (gc != null) + " journal def " + (def != null);
            }
            Pawn reader = null;
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
            {
                reader = p;
                break;
            }
            IntVec3 at = reader != null ? reader.Position : map.Center;
            gc.SetStage(Ladder, 0);
            StringBuilder stages = new StringBuilder();
            StringBuilder moved = new StringBuilder();
            for (int i = 0; i < count; i++)
            {
                Thing j = GenSpawn.Spawn(ThingMaker.MakeThing(def), at, map);
                string r = Read(j, reader, false);
                j.Destroy();
                int s = gc.GetStage(Ladder);
                stages.Append(i == 0 ? "" : ",").Append(s);
                moved.Append(i == 0 ? "" : ",").Append(r.Contains("moved=True") ? "T" : "F");
            }
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RUT_Scarlands");
            string desc = biome?.description ?? "(no RUT_Scarlands)";
            return "STAGES " + stages + " moved " + moved + " | desc " + desc.Substring(0, Mathf.Min(120, desc.Length));
        }

        /// <summary>Bridge proof (jawa/static_call): runs the camp genstep on the current map with
        /// <paramref name="count"/> camps and reports what landed. "CAMPS 2 | journals 2 corpses 2 fires 2".</summary>
        public static string ProofCamps(Map map, int count)
        {
            if (map == null)
            {
                return "REFUSED: no map";
            }
            int placed = GenStep_RUT_PilgrimCamps.PlaceCamps(map, count);
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_PilgrimJournal");
            int journals = def == null ? 0 : map.listerThings.ThingsOfDef(def).Count;
            int corpses = 0;
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse))
            {
                if (t is Corpse c && c.InnerPawn != null && c.InnerPawn.RaceProps.Humanlike)
                {
                    corpses++;
                }
            }
            return "CAMPS " + placed + " | journals " + journals + " corpses " + corpses
                + " fires " + map.listerThings.ThingsOfDef(ThingDefOf.Campfire).Count;
        }
    }

    /// <summary>A cold fire, a bedroll, the pilgrim sitting dead beside it, and the journal on the
    /// bedroll. Placed on open ground away from the map edge.</summary>
    public class GenStep_RUT_PilgrimCamps : GenStep
    {
        public override int SeedPart => 61270931;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!ScarlandsLadderSettings.campsEnabled)
            {
                return;
            }
            PlaceCamps(map, Mathf.RoundToInt(ScarlandsLadderSettings.campsPerMap));
        }

        public static int PlaceCamps(Map map, int count)
        {
            int placed = 0;
            for (int i = 0; i < count; i++)
            {
                if (CellFinderLoose.TryGetRandomCellWith(c => CampFits(map, c), map, 1000, out IntVec3 c0))
                {
                    PlaceCamp(map, c0);
                    placed++;
                }
            }
            return placed;
        }

        private static bool CampFits(Map map, IntVec3 c)
        {
            if (c.CloseToEdge(map, 12) || c.Fogged(map))
            {
                return false;
            }
            foreach (IntVec3 x in CellRect.CenteredOn(c, 1))
            {
                if (!x.InBounds(map) || !x.Standable(map) || x.GetEdifice(map) != null || x.Roofed(map)
                    || x.GetFirstItem(map) != null || x.GetTerrain(map).IsWater)
                {
                    return false;
                }
            }
            return true;
        }

        private static void PlaceCamp(Map map, IntVec3 c)
        {
            foreach (IntVec3 x in CellRect.CenteredOn(c, 1))
            {
                Plant p = x.GetPlant(map);
                p?.Destroy();
            }
            Thing fire = GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.Campfire), c, map);
            CompRefuelable fuel = fire.TryGetComp<CompRefuelable>();
            if (fuel != null && fuel.Fuel > 0f)
            {
                fuel.ConsumeFuel(fuel.Fuel);      // a cold fire
            }
            IntVec3 bedCell = c + IntVec3.West;
            Thing bed = ThingMaker.MakeThing(ThingDefOf.Bedroll, ThingDefOf.Cloth);
            GenSpawn.Spawn(bed, bedCell, map, Rot4.East);
            ThingDef journal = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_PilgrimJournal");
            if (journal != null)
            {
                GenSpawn.Spawn(ThingMaker.MakeThing(journal), c + IntVec3.North + IntVec3.West, map);
            }
            Pawn pilgrim = PawnGenerator.GeneratePawn(PawnKindDefOf.Villager, null);
            GenSpawn.Spawn(pilgrim, c + IntVec3.South, map, Rot4.East);
            pilgrim.Kill(null);
            Corpse corpse = pilgrim.Corpse;
            CompRottable rot = corpse?.TryGetComp<CompRottable>();
            if (rot != null)
            {
                rot.RotProgress = rot.PropsRot.TicksToDessicated + 1;
            }
            corpse?.SetForbidden(true, false);
        }
    }
}
