using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Pits
{
    // PIT_COVER_FALL_REWIRE_1 — the covered pit, rebuilt on the D/F primitive (owner 2026-10-02:
    // "There's no 'pit' as a special thing, it's just a channel/canal dig."). A cover is a 1x1
    // building laid over a SUPERDEEP (D=4) cell. Neighbouring covers form one deck: the
    // CompPitCoverTrigger on the deck's lead cover sums the mass of everyone standing on the WHOLE
    // deck every 30 ticks, and once it crosses the tier's rating (PitCoverTier 40/120/220 kg, 220 is
    // the owner's number) every cover in the deck gives way and the pawns on it DESCEND through the
    // superdeep trap's own descent event (fall damage, then whatever hooks PitDescent). No despawn.
    //
    // While a cover stands, its cell is not a pit for anything that walks: no descent fires, nobody
    // is held, the shooting rule treats it as ground, and its path cost is the cover's, not the
    // hole's 300 (a trap nobody walks over catches nobody). Stepping OFF a cover onto ground is a surface step too
    // (RM_Patch_PitStepCost reads a covered cell as depth 0), so a deck shows no climb-out stall at its edge. The cover prints the terrain AROUND the
    // pit so the hole beneath it cannot be seen (TerrainMimicPrinter's open question — whether the
    // seam vanishes at play zoom — is still a live-eyes check, bar pit_covered_seam_at_max_zoom).
    public class RM_PitCoverExtension : DefModExtension
    {
        public PitCoverTier tier = PitCoverTier.WovenScrap;
    }

    public static class RM_PitCoverUtility
    {
        public static Building_PitCover CoverAt(Map map, IntVec3 c)
        {
            if (map == null || !c.InBounds(map))
            {
                return null;
            }
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Building_PitCover cover && cover.Covered)
                {
                    return cover;
                }
            }
            return null;
        }

        /// <summary>Any intact deck on the cell (a cover or, later, any suspension deck), height ignored. Kept for the
        /// height-blind sites (pathing veto, trap hold, swim, trench); a site whose answer depends on the walking height
        /// reads RM_SpanUtility.DeckedAt(map, c, out deckHeightM) instead.</summary>
        public static bool IsCovered(Map map, IntVec3 c)
        {
            return RM_SpanUtility.DeckedAt(map, c);
        }

        /// <summary>Every intact cover 4-way connected to this one (this one included).</summary>
        public static List<Building_PitCover> Deck(Building_PitCover start)
        {
            List<Building_PitCover> deck = new List<Building_PitCover>();
            if (start == null || !start.Spawned)
            {
                return deck;
            }
            Map map = start.Map;
            return RM_PitDeckMath.Flood(start.Position, c => CoverAt(map, c), (c, d) => c + GenAdj.CardinalDirections[d], 4);
        }

        /// <summary>The deck when this cover is its lead (lowest id); null as soon as the flood meets a lower id, so a cover that
        /// is not the lead pays for the ground to its nearest lower id, not for the whole deck
        /// (COVER_SCAN_TAME_QUADRATIC_ID_MINIMA: decks with many local id minima).</summary>
        public static List<Building_PitCover> DeckIfLead(Building_PitCover start)
        {
            if (start == null || !start.Spawned)
            {
                return new List<Building_PitCover>();
            }
            Map map = start.Map;
            int id = start.thingIDNumber;
            return RM_PitDeckMath.Flood(start.Position, c => CoverAt(map, c), (c, d) => c + GenAdj.CardinalDirections[d], 4, c => c.thingIDNumber < id);
        }

        /// <summary>COVER_SCAN_TAME_QUADRATIC_ID_MINIMA, live proof (Artisan pass 2): one trigger census over every cover on the
        /// current map, as CompPitCoverTrigger runs it (the cheap lower-id neighbour test, then DeckIfLead), timed beside the old
        /// way (a full flood from every cover). "COVERSCAN covers=N decks=N early=N ms=.. floodEveryCoverMs=..".</summary>
        public static string ProofCoverScan(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "REFUSED: no current map";
            }
            var covers = new List<Building_PitCover>();
            foreach (Building b in map.listerBuildings.allBuildingsColonist)
            {
                if (b is Building_PitCover pc)
                {
                    covers.Add(pc);
                }
            }
            foreach (Building b in map.listerBuildings.allBuildingsNonColonist)
            {
                if (b is Building_PitCover pc)
                {
                    covers.Add(pc);
                }
            }
            int decks = 0, early = 0, deckCells = 0, oldCells = 0;
            var sw = System.Diagnostics.Stopwatch.StartNew();
            foreach (Building_PitCover self in covers)
            {
                bool lower = false;
                for (int i = 0; i < 4 && !lower; i++)
                {
                    Building_PitCover n = CoverAt(map, self.Position + GenAdj.CardinalDirections[i]);
                    lower = n != null && n.thingIDNumber < self.thingIDNumber;
                }
                if (lower)
                {
                    early++;
                    continue;
                }
                List<Building_PitCover> deck = DeckIfLead(self);
                if (deck != null)
                {
                    decks++;
                    deckCells += deck.Count;
                }
            }
            double ms = sw.Elapsed.TotalMilliseconds;
            sw.Restart();
            foreach (Building_PitCover self in covers)
            {
                oldCells += Deck(self).Count;
            }
            double oldMs = sw.Elapsed.TotalMilliseconds;
            return "COVERSCAN covers=" + covers.Count + " decks=" + decks + " early=" + early + " deckCells=" + deckCells
                + " ms=" + ms.ToString("0.000") + " floodEveryCoverMs=" + oldMs.ToString("0.000") + " floodCells=" + oldCells;
        }

        /// <summary>PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT: does the lid on <paramref name="c"/> draw its own art (an open
        /// pit square among its 8 neighbours betrays the pit, RM_PitCoverLookMath.ShowsArt) instead of the ground?</summary>
        public static bool LidShowsArt(Map map, IntVec3 c)
        {
            RM_MapComponent_Excavation eng = map?.GetComponent<RM_MapComponent_Excavation>();
            if (eng == null)
            {
                return false;
            }
            int[] seen = new int[8];
            for (int i = 0; i < 8; i++)
            {
                IntVec3 n = c + GenAdj.AdjacentCells[i];
                seen[i] = n.InBounds(map) ? RM_SuspensionUnderpass.SeenDepthAt(map, eng, n) : -1;
            }
            return RM_PitCoverLookMath.ShowsArt(seen);
        }

        /// <summary>PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT: the square <paramref name="c"/> opened or closed (dug, filled, a lid or
        /// deck laid or lifted): the lids round it re-print, since whether they show art or ground reads their neighbours.</summary>
        public static void DirtyNeighbourLids(Map map, IntVec3 c)
        {
            if (map?.mapDrawer == null)
            {
                return;
            }
            // PIT_COVER_FIX_FACES_SHOW_THROUGH: the wall faces (a Terrain-flag layer) of the square and round it read the lid too
            if (c.InBounds(map))
            {
                map.mapDrawer.MapMeshDirty(c, (ulong)MapMeshFlagDefOf.Terrain, true, false);
            }
            for (int i = 0; i < 8; i++)
            {
                IntVec3 n = c + GenAdj.AdjacentCells[i];
                if (CoverAt(map, n) != null)
                {
                    map.mapDrawer.MapMeshDirty(n, (ulong)MapMeshFlagDefOf.Things | (ulong)MapMeshFlagDefOf.Buildings);
                }
            }
        }

        /// <summary>The terrain the cover should look like: the commonest non-excavated terrain around it.</summary>
        public static TerrainDef SurfaceAround(Map map, IntVec3 c)
        {
            RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
            Dictionary<TerrainDef, int> counts = new Dictionary<TerrainDef, int>();
            for (int r = 1; r <= 4; r++)
            {
                foreach (IntVec3 n in GenRadial.RadialCellsAround(c, r, false))
                {
                    if (!n.InBounds(map) || (eng != null && eng.IsExcavated(n)))
                    {
                        continue;
                    }
                    TerrainDef t = n.GetTerrain(map);
                    if (t != null)
                    {
                        counts[t] = counts.TryGetValue(t, out int k) ? k + 1 : 1;
                    }
                }
                if (counts.Count > 0)
                {
                    break;
                }
            }
            TerrainDef best = null;
            int bestN = -1;
            foreach (KeyValuePair<TerrainDef, int> kv in counts)
            {
                if (kv.Value > bestN)
                {
                    best = kv.Key;
                    bestN = kv.Value;
                }
            }
            return best ?? TerrainDefOf.Soil;
        }
    }

    /// <summary>The trap tier of the suspension family (SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT): a hidden surface deck over a
    /// pit, with its own look (Q8). Span machinery (deck read, collapse through the descent event, climb generation) is
    /// Building_SpanDeck's; what is a cover's own is the tier, the 4-way cover deck, the mimic print and the trap trigger.</summary>
    public class Building_PitCover : Building_SpanDeck, IPitCoverHost
    {
        public bool Covered => Decked;

        public bool Sprung => Collapsed;

        public PitCoverTier CoverTier => def.GetModExtension<RM_PitCoverExtension>()?.tier ?? PitCoverTier.None;

        public override float LoadRatingKg => CoverTier.TriggerMassKg();

        protected override string CollapseSaveKey => "rmCoverSprung";

        public override bool JoinsSpan(Building_SpanDeck other) => other is Building_PitCover;

        /// <summary>FLOWWORKS_PITCOVER_FIX_BURNS_PAWN_UNHARMED (GPT edge read V3): a cover destroyed by damage (fire, shots, a
        /// blast that kills it before the explosion postfix looks) is no longer ground, so whoever stands on it falls, as the
        /// blast rule already has everyone fall (owner cards Q5 + Q9). PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO (owner card 2026-10-20):
        /// a deconstructed cover drops its riders the same way. A vanished/replaced cover is unchanged; covers have no
        /// minifiedDef, so there is no uninstall path.</summary>
        public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = Map;
            IntVec3 pos = Position;
            List<Pawn> riders = null;
            if (!collapsed && map != null && (mode == DestroyMode.KillFinalize || mode == DestroyMode.KillFinalizeLeavingsOnly || mode == DestroyMode.Deconstruct))
            {
                foreach (Thing t in pos.GetThingList(map))
                {
                    // PIT_COVER_FIX_OCCUPANT_STAYS_BELOW: whoever is beneath the lid is already on the floor
                    if (t is Pawn p && !p.Dead && !p.Flying && !RM_PitCoverBeneath.IsBeneath(p))
                    {
                        (riders ?? (riders = new List<Pawn>())).Add(p);
                    }
                }
            }
            base.DeSpawn(mode);
            RM_SuperdeepTrapState state = RM_SuperdeepTrap.EngineOf(map)?.SuperdeepTrap;
            if (riders == null || state == null)
            {
                return;
            }
            Pawn first = null;
            foreach (Pawn p in riders)
            {
                if (p.Spawned && !p.Dead && p.Position == pos)
                {
                    RM_SuperdeepTrap.OnForcedDescent(p, pos, state);
                    first = first ?? p;
                }
            }
            if (first != null)
            {
                string what = mode == DestroyMode.Deconstruct ? "A concealed pit was taken apart under " : "A concealed pit broke under ";
                Messages.Message(what + first.LabelShort + (riders.Count > 1 ? " and others." : "."),
                    new LookTargets(riders), MessageTypeDefOf.NegativeEvent);
            }
        }

        /// <summary>PIT_COVER_FIX_OCCUPANT_STAYS_BELOW: a lid laid over someone down in the pit keeps them below it.</summary>
        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            RM_PitCoverBeneath.TakeUnder(this, respawningAfterLoad);
        }

        public override List<Building_SpanDeck> SpanCells()
        {
            return new List<Building_SpanDeck>(RM_PitCoverUtility.Deck(this));
        }

        /// <summary>One cover per deck scans (the lowest id), so a deck is summed once, not once per cell.</summary>
        public bool IsDeckLead
        {
            get
            {
                foreach (Building_PitCover c in RM_PitCoverUtility.Deck(this))
                {
                    if (c.thingIDNumber < thingIDNumber)
                    {
                        return false;
                    }
                }
                return true;
            }
        }

        /// <summary>PIT_LID_FIX_VICKY_PEEKS_THROUGH: the terrain this lid last printed (null until printed), so the pit lip
        /// occluder can draw a lid square in the ground it shows without a per-frame SurfaceAround census.</summary>
        public TerrainDef PrintedSurface { get; private set; }

        /// <summary>PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT: the lid's own art material when it last printed its art (a lid beside
        /// an open pit square), else null; the pit lip occluder then draws its lid square from this art, not PrintedSurface.</summary>
        public Material PrintedArt { get; private set; }

        public override void Print(SectionLayer layer)
        {
            Map map = Map;
            if (map == null)
            {
                return;
            }
            // owner 2026-10-24 "says it's a plank covered pit, but it sure doesn't look like it (empty pit appearance?)": a lid in
            // an open pit hides nothing, so it shows its planks (gaps show the hole); a wholly covered pit keeps the ground print
            Material art = Graphic?.MatSingle;
            if (art != null && RM_PitCoverUtility.LidShowsArt(map, Position))
            {
                PrintedArt = art;
                PrintedSurface = null;
                Graphic.Print(layer, this, 0f);
                return;
            }
            PrintedArt = null;
            TerrainDef surface = RM_PitCoverUtility.SurfaceAround(map, Position);
            PrintedSurface = surface;
            Material mat = surface?.graphic?.MatSingle;
            if (mat == null)
            {
                TerrainMimicPrinter.PrintTerrainMimic(this, layer);
                return;
            }
            Vector3 center = Position.ToVector3Shifted();
            center.y = DrawPos.y;
            Printer_Plane.PrintPlane(layer, center, Vector2.one, mat);
        }

        /// <summary>PIT_COVER_BUILD_SEAM_AT_MAX_ZOOM (bar pit_covered_seam_at_max_zoom): a lid that prints ground draws, close up
        /// only (RM_PitCoverLookMath.SeamStrength), a hairline cut along every edge where it meets the bank and a faint
        /// discoloration over itself, so the player who laid it can find it; at play zoom it draws nothing and is ground.
        /// drawerType MapMeshAndRealTime: Thing.DrawAt draws no Graphic for a spawned map-mesh thing, so the print stays the lid.</summary>
        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            base.DrawAt(drawLoc, flip);
            Map map = Map;
            if (map == null || PrintedArt != null || !Covered || Find.CameraDriver == null || Find.CurrentMap != map)
            {
                return;
            }
            CameraDriver cam = Find.CameraDriver;
            float px = Screen.height / (cam.RootSize * 2f);
            float s = RM_PitCoverLookMath.SeamStrength(px, cam.RootSize, cam.config.sizeRange.min);
            if (s <= 0f)
            {
                return;
            }
            int q = Mathf.Clamp(Mathf.RoundToInt(s * SeamSteps), 1, SeamSteps);
            Vector3 c = Position.ToVector3Shifted();
            c.y = AltitudeLayer.FloorEmplacement.AltitudeFor() + 0.01f;
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(c, Quaternion.identity, Vector3.one), SeamMat(q, 0), 0);
            for (int i = 0; i < 4; i++)
            {
                IntVec3 n = Position + GenAdj.CardinalDirections[i];
                if (RM_PitCoverUtility.CoverAt(map, n) != null)
                {
                    continue;
                }
                // the cut: a dark hairline on the lid's side of the edge, a lighter lip just inside it
                IntVec3 dir = GenAdj.CardinalDirections[i];
                bool alongX = dir.z != 0;
                for (int k = 0; k < 2; k++)
                {
                    float dw = RM_PitCoverLookMath.SeamWidthCells(SeamDarkWidth, px);
                    float lw = RM_PitCoverLookMath.SeamWidthCells(SeamLightWidth, px);
                    float w = k == 0 ? dw : lw;
                    float off = 0.5f - (k == 0 ? dw * 0.5f : dw + lw * 0.5f);
                    Vector3 at = c + new Vector3(dir.x * off, 0.001f * (k + 1), dir.z * off);
                    Vector3 size = alongX ? new Vector3(1f, 1f, w) : new Vector3(w, 1f, 1f);
                    Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(at, Quaternion.identity, size), SeamMat(q, k + 1), 0);
                }
            }
        }

        private const int SeamSteps = 16;
        private const float SeamDarkWidth = 0.035f;
        private const float SeamLightWidth = 0.025f;
        private static readonly Material[,] seamMats = new Material[SeamSteps + 1, 3];

        /// <summary>The seam's three materials (0 the discoloration, 1 the dark cut, 2 the light lip) at strength step q.</summary>
        private static Material SeamMat(int q, int part)
        {
            Material m = seamMats[q, part];
            if (m == null)
            {
                float s = q / (float)SeamSteps;
                Color col = part == 0 ? new Color(0.20f, 0.17f, 0.13f, 0.07f * s)
                    : part == 1 ? new Color(0.08f, 0.06f, 0.04f, 0.42f * s)
                    : new Color(0.85f, 0.78f, 0.66f, 0.16f * s);
                m = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, col);
                seamMats[q, part] = m;
            }
            return m;
        }

        /// <summary>The whole cover deck gives way (Building_SpanDeck.Collapse: covers gone before anyone descends).</summary>
        public void Spring(List<Pawn> fallers)
        {
            Collapse(fallers);
        }

        protected override void CollapseMessage(Pawn first, List<Pawn> fallers)
        {
            Messages.Message("A concealed pit gave way under " + first.LabelShort + (fallers.Count > 1 ? " and others." : "."),
                new LookTargets(fallers), MessageTypeDefOf.NeutralEvent);
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string line = "Gives way under " + CoverTier.TriggerMassKg().ToString("0") + " kg on the whole concealed pit.";
            // PIT_COVER_FIX_OCCUPANT_STAYS_BELOW (owner card): inspecting the lid shows who is under it
            List<Pawn> below = RM_PitCoverBeneath.BeneathOn(Map, RM_PitCoverUtility.Deck(this));
            if (below.Count > 0)
            {
                List<string> names = new List<string>();
                foreach (Pawn p in below)
                {
                    names.Add(p.LabelShort);
                }
                line += "\nBelow, hidden: " + string.Join(", ", names) + ".";
            }
            return s.NullOrEmpty() ? line : s + "\n" + line;
        }

    }

    /// <summary>Owner, 2026-10-06 (cards Q5 + Q9): a blast that reaches a pit cover breaks it: damaging blasts (bombs,
    /// grenades, mortars) AND fire/incendiary; EMP, smoke, stun, firefoam and tox gas do not (harmsHealth false). The
    /// whole deck springs and everyone standing on it falls. FlowWorks' own rule, so it holds without Explosive Knockback.</summary>
    [HarmonyPatch(typeof(DamageWorker), nameof(DamageWorker.ExplosionAffectCell))]
    [RimMandrake.Shared.PatchFeature("Blasts break concealed pits", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "blastsBreakPitCovers")]
    public static class RM_Patch_ExplosionBreaksPitCover
    {
        /// <summary>COVER_BLAST_FIX_DECK_LEFT_INTACT: the cover on the cell before the blast, so the postfix still knows the
        /// deck when the blast killed that cover outright (its DeSpawn drops only its own riders).</summary>
        public static void Prefix(Explosion explosion, IntVec3 c, out Building_PitCover __state)
        {
            __state = RimMandrakeFlowWorksSettings.blastsBreakPitCovers ? RM_PitCoverUtility.CoverAt(explosion?.Map, c) : null;
        }

        public static void Postfix(Explosion explosion, IntVec3 c, Building_PitCover __state)
        {
            Map map = explosion?.Map;
            if (!RimMandrakeFlowWorksSettings.blastsBreakPitCovers || map == null || explosion.damType == null || !explosion.damType.harmsHealth)
            {
                return;
            }
            var starts = new List<Building_PitCover>();
            Building_PitCover cover = RM_PitCoverUtility.CoverAt(map, c);
            if (cover != null)
            {
                starts.Add(cover);
            }
            else if (__state != null && __state.Destroyed && !__state.Sprung)
            {
                // COVER_BLAST_FIX_DECK_LEFT_INTACT: the blast killed this square's cover; the rest of its deck (now perhaps in
                // up to four pieces, one per side) gives way too, with everyone on it
                for (int i = 0; i < 4; i++)
                {
                    Building_PitCover n = RM_PitCoverUtility.CoverAt(map, c + GenAdj.CardinalDirections[i]);
                    if (n != null)
                    {
                        starts.Add(n);
                    }
                }
            }
            foreach (Building_PitCover start in starts)
            {
                if (!start.Covered)
                {
                    continue; // one piece sprung with an earlier side
                }
                var fallers = new List<Pawn>();
                foreach (Building_PitCover d in RM_PitCoverUtility.Deck(start))
                {
                    foreach (Thing t in d.Position.GetThingList(map))
                    {
                        if (t is Pawn p && !RM_PitCoverBeneath.IsBeneath(p))
                        {
                            fallers.Add(p);
                        }
                    }
                }
                start.Spring(fallers);
            }
        }
    }

    /// <summary>A cover belongs over a pit; anywhere else it would hide nothing. PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE: a pit is
    /// a dug square with a sheer drop of 2 m or more to a neighbour (the fall the cover hides), at any depth. It was "dug to
    /// D 4", which also took the bottom of a gentle 0.5 m staircase 2 m down, where nobody falls.</summary>
    public class PlaceWorker_PitCoverOnSuperdeep : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
            Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            RM_MapComponent_Excavation engine = map?.GetComponent<RM_MapComponent_Excavation>();
            if (engine == null || !engine.IsExcavated(loc) || RM_SpikeUtility.TallestWallOver(engine, loc) < RM_PitTrapMath.Superdeep)
            {
                return "A concealed pit must be laid over a pit: a dug square with a sheer drop of 2 m or more to a neighbour.";
            }
            return true;
        }
    }

    /// <summary>A covered superdeep cell costs what the cover costs to cross, not the hole's 300. The engine
    /// takes the MAX of terrain and thing costs, so the cover's own pathCost alone cannot lower it; this prefix
    /// hands the cover's cost in as the terrain's (baseCostOverride), and vanilla still adds everything else on
    /// the cell (snow/sand, door-to-door, fire on or beside it). An override someone else already set (water,
    /// RM_Patch_PitStepCost's walked step) is left alone; the cover's thing cost is still max'd in by vanilla.</summary>
    [HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
    [RimMandrake.Shared.PatchFeature("Concealed pits are walkable at their own cost")]
    public static class RM_Patch_PathGrid_PitCoverCost
    {
        [HarmonyPrefix]
        public static void Prefix(PathGrid __instance, IntVec3 c, ref int? baseCostOverride)
        {
            if (baseCostOverride.HasValue)
            {
                return;
            }
            Map map = __instance.map;
            if (map == null || !c.InBounds(map))
            {
                return;
            }
            Building_SpanDeck cover = RM_SpanUtility.DeckAt(map, c);
            if (cover != null)
            {
                baseCostOverride = Mathf.Max(cover.def.pathCost, 0);
            }
        }
    }
}
