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
            HashSet<IntVec3> seen = new HashSet<IntVec3> { start.Position };
            Queue<IntVec3> open = new Queue<IntVec3>();
            open.Enqueue(start.Position);
            // COVER_DECK_TUNE_QUADRATIC_CENSUS (GPT C4-F6): no size cap. A cap cut big decks into partial ones that each found
            // a different lead and collapsed in pieces; the flood is bounded by the covers built, and the trigger floods only
            // from a deck's local-minimum ids (CompPitCoverTrigger.RunScan).
            while (open.Count > 0)
            {
                IntVec3 c = open.Dequeue();
                Building_PitCover cover = CoverAt(map, c);
                if (cover == null)
                {
                    continue;
                }
                deck.Add(cover);
                for (int i = 0; i < 4; i++)
                {
                    IntVec3 n = c + GenAdj.CardinalDirections[i];
                    if (seen.Add(n) && CoverAt(map, n) != null)
                    {
                        open.Enqueue(n);
                    }
                }
            }
            return deck;
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

        public override void Print(SectionLayer layer)
        {
            Map map = Map;
            if (map == null)
            {
                return;
            }
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
        public static void Postfix(Explosion explosion, IntVec3 c)
        {
            Map map = explosion?.Map;
            if (!RimMandrakeFlowWorksSettings.blastsBreakPitCovers || map == null || explosion.damType == null || !explosion.damType.harmsHealth)
            {
                return;
            }
            Building_PitCover cover = RM_PitCoverUtility.CoverAt(map, c);
            if (cover == null)
            {
                return;
            }
            var fallers = new List<Pawn>();
            foreach (Building_PitCover d in RM_PitCoverUtility.Deck(cover))
            {
                foreach (Thing t in d.Position.GetThingList(map))
                {
                    if (t is Pawn p && !RM_PitCoverBeneath.IsBeneath(p))
                    {
                        fallers.Add(p);
                    }
                }
            }
            cover.Spring(fallers);
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
