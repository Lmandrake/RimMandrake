using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Noise;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_FIRE_CADENCE_1 — the biome clock.
    ///
    /// 🔑 OWNER, 2026-09-14, verbatim: "the fires should come every few days, not
    /// a rare event." That is a CADENCE, and it is a different mechanism from
    /// MapComponent_BurnLine's standing-burn reseed, which this class does not
    /// replace:
    ///
    ///   - the RESEED is a floor. It only ever fires when the map has been
    ///     completely fireless for two days, and it lights ONE smoulder. Its job
    ///     is "the burn exists somewhere, always".
    ///   - the FRONT (here) is the clock. Every 2-4 days, whatever else is
    ///     burning, a line of grass goes up and walks. Its job is "the grass
    ///     burns on a schedule you can plan around".
    ///
    /// A map with a healthy standing burn never triggers the reseed at all, and
    /// under the old code that map saw nothing happen for weeks — which is
    /// exactly the "rare event" the owner ruled against.
    ///
    /// 🔴 IT LIGHTS A LINE, NOT A POINT. One smoulder in dry grass usually dies
    /// to vanilla's own fire maths before it becomes anything. A front is
    /// FireFrontWidthCells ignitions on one bearing, so the thing that walks off
    /// downwind is a burn-line rather than a candle. Every cell still goes
    /// through vanilla's FireUtility.ChanceToStartFireIn, so terrain
    /// flammability, paved strips and the existing fire
    /// chain are all respected without re-deriving any of them — this is how it
    /// "burns THROUGH quickgrass" rather than around it.
    ///
    /// 🔑 NULL INSTIGATOR, deliberately. MapComponent_BurnLine.IsPlayerAttributed
    /// reads Fire.instigator, so a front lit by the biome accrues no arson debt
    /// and provokes no Tribe raid. The biome is not the colony's fault.
    ///
    /// Owned and ticked by MapComponent_BurnLine (one biome check, one tick gate,
    /// one ExposeData for the whole kit) rather than being a second MapComponent:
    /// RimWorld instantiates every MapComponent on every map in the save, and one
    /// that early-outs is still one more virtual call per map per tick.
    /// </summary>
    public class PyrelandsFireFront
    {
        private readonly Map map;

        /// <summary>Absolute game tick the next front is due. -1 means "not
        /// scheduled yet" — set on the first tick after a load or a map gen, so
        /// the scheduled front never fires on tick one. (A fresh map's first fire
        /// is the opening front below, a separate smaller line.)</summary>
        private int nextFrontTick = -1;

        /// <summary>PYRE_OPENING_FRONT (owner, by card, 2026-10-22: "GPT review Q7 → Pyrelands fresh map starts with a
        /// smouldering front"). False on a map built by this code (the constructor runs at generation), so the fresh map
        /// lights one small front on its first watch interval. Saved with default TRUE: a save from before this field has
        /// no key and loads as done, so an old map never bursts into an "opening" fire on load.</summary>
        private bool openingDone;

        /// <summary>Test drive only (RearmOpeningFront): the tick the opening window restarts from. Unsaved.</summary>
        private int openingRearmTick = int.MinValue;

        /// <summary>Cells the opening front lit, and when (-1 = not lit on this session). Unsaved: probe output only.</summary>
        private int openingLit;
        private int openingLitTick = -1;
        private IntVec3 openingOrigin = IntVec3.Invalid;

        /// <summary>Yesterday's fire (2026-11-07): the scar GenStep_PyrelandsYesterdayFire laid, whose leading arc the opening
        /// front lights. Saved; the defaults (no scar, arc already lit) leave a save from before these fields as it was.</summary>
        private IntVec3 scarCentre = IntVec3.Invalid;
        private int scarEdge = -1;
        private float scarRadius;
        private bool scarLaid;
        private bool scarArcLit = true;

        public PyrelandsFireFront(Map map)
        {
            this.map = map;
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref nextFrontTick, "fireFrontNextTick", -1);
            Scribe_Values.Look(ref openingDone, "fireFrontOpeningDone", true);
            Scribe_Values.Look(ref scarCentre, "fireFrontScarCentre", IntVec3.Invalid);
            Scribe_Values.Look(ref scarEdge, "fireFrontScarEdge", -1);
            Scribe_Values.Look(ref scarRadius, "fireFrontScarRadius", 0f);
            Scribe_Values.Look(ref scarLaid, "fireFrontScarLaid", false);
            Scribe_Values.Look(ref scarArcLit, "fireFrontScarArcLit", true);
        }

        /// <summary>Lays yesterday's fire on this map and keeps its plan for the arc (GenStep_PyrelandsYesterdayFire at generation,
        /// RearmOpening at runtime: one path). False, and nothing laid, when the gates are off or no edge has room (a small map):
        /// the opening front then lights its plain line.</summary>
        internal bool LayYesterdayFire(bool atGeneration)
        {
            scarLaid = false;
            scarArcLit = true;
            if (!(PyrelandsMechanicsGate.On && RM_PyrelandsSettings.fireClockEnabled)
                || !PyrelandsYesterdayFire.TryPlan(map, atGeneration, out scarCentre, out scarEdge, out scarRadius))
            {
                scarCentre = IntVec3.Invalid;
                scarEdge = -1;
                scarRadius = 0f;
                return false;
            }
            PyrelandsYesterdayFire.Lay(map, scarCentre, scarEdge, scarRadius, Find.TickManager.TicksGame);
            scarLaid = true;
            scarArcLit = false;
            return true;
        }

        /// <summary>The fresh map's opening front, once. No letter: a burn somewhere is this biome's normal state, and a
        /// letter at arrival would read as an attack. Null instigator, like every front the biome lights.</summary>
        private void TickOpeningFront(bool enabled)
        {
            int now = Find.TickManager.TicksGame;
            int from = Mathf.Max(map.generationTick, openingRearmTick);
            RM_OpeningAction act = RM_BurnKernel.OpeningFront(openingDone, enabled, now - from, PyrelandsTuning.OpeningFrontWindowTicks);
            if (act == RM_OpeningAction.Skip)
            {
                openingDone = true;
                return;
            }
            if (act != RM_OpeningAction.Light)
            {
                return;
            }
            // Yesterday's fire: its leading arc is the opening front. One message, no letter (see above); an arc that lit
            // nothing (rain, its rim grazed bare) falls through to the plain line this same interval.
            if (scarLaid && !scarArcLit)
            {
                int arcLit = LightScarArc(out IntVec3 mid);
                if (arcLit > 0)
                {
                    scarArcLit = true;
                    openingDone = true;
                    openingLit = arcLit;
                    openingLitTick = now;
                    openingOrigin = mid;
                    Messages.Message("RM_YesterdayFireMessage".Translate(("RM_Compass" + scarEdge * 2).Translate()),
                        new LookTargets(new TargetInfo(mid, map)), MessageTypeDefOf.NeutralEvent);
                    return;
                }
            }
            if (!TryFindOrigin(out IntVec3 origin))
            {
                return;
            }
            int lit = IgniteLine(origin, null, PyrelandsTuning.OpeningFrontWidthCells, PyrelandsTuning.OpeningFrontFireSize);
            if (lit > 0)
            {
                openingDone = true;
                openingLit = lit;
                openingLitTick = now;
                openingOrigin = origin;
            }
        }

        /// <summary>Lights the scar's leading arc: every stride'th cell in bearing order, at most YesterdayFireArcFireCap, at
        /// the opening front's fire size and with no instigator. mid is the arc's middle cell (the message looks there).</summary>
        private int LightScarArc(out IntVec3 mid)
        {
            List<IntVec3> arc = PyrelandsYesterdayFire.ArcCells(map, scarCentre, scarEdge, scarRadius, MapComponent_BurnLine.For(map));
            mid = arc.Count > 0 ? arc[arc.Count / 2] : IntVec3.Invalid;
            int stride = RM_BurnKernel.ArcStride(arc.Count, PyrelandsTuning.YesterdayFireArcFireCap, PyrelandsTuning.YesterdayFireArcStride);
            int lit = 0;
            for (int i = stride / 2; i < arc.Count && lit < PyrelandsTuning.YesterdayFireArcFireCap; i += stride)
            {
                if (FireUtility.TryStartFireIn(arc[i], map, PyrelandsTuning.OpeningFrontFireSize, null))
                {
                    lit++;
                }
            }
            return lit;
        }

        /// <summary>Probe text for MapComponent_BurnLine.ProbeOpeningFront.</summary>
        internal string ProbeOpening()
        {
            string scar = scarLaid
                ? PyrelandsYesterdayFire.Census(map, scarCentre, scarEdge, scarRadius) + ";arcCandidates="
                  + PyrelandsYesterdayFire.ArcCells(map, scarCentre, scarEdge, scarRadius, MapComponent_BurnLine.For(map)).Count
                : "scarCells=0;bare=0;sprouts=0;pods=0;ash=0;arcCandidates=0";
            return string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "done={0};lit={1};litTick={2};origin={3};mapAge={4};now={5};scarLaid={6};scarCentre={7};scarSide={8};scarRadius={9:0.0};{10};arcLit={11}",
                openingDone, openingLit, openingLitTick,
                openingOrigin.IsValid ? openingOrigin.x + "," + openingOrigin.z : "invalid",
                Find.TickManager.TicksGame - map.generationTick, Find.TickManager.TicksGame,
                scarLaid, scarCentre.IsValid ? scarCentre.x + "," + scarCentre.z : "invalid", PyrelandsYesterdayFire.Side(scarEdge),
                scarRadius, scar, scarArcLit);
        }

        /// <summary>Test drive only: make this map "fresh" for the opening front again, its window starting now, and burn a
        /// new yesterday's fire in by the GenStep's own path (stamps at now minus their age) for the arc to light.</summary>
        internal void RearmOpening()
        {
            openingDone = false;
            openingRearmTick = Find.TickManager.TicksGame;
            openingLit = 0;
            openingLitTick = -1;
            openingOrigin = IntVec3.Invalid;
            LayYesterdayFire(false);
        }

        /// <summary>Called from MapComponent_BurnLine's already-gated tick: this
        /// only ever runs on a Pyrelands map, on the watch interval.</summary>
        public void Tick()
        {
            // Off means off, but keep the clock honest: re-arm from now, so
            // switching the mechanism back on does not fire instantly with a
            // months-overdue timer (RM_BurnKernel.FrontTick does both).
            bool enabled = PyrelandsMechanicsGate.On && RM_PyrelandsSettings.fireClockEnabled;
            TickOpeningFront(enabled);
            if (RM_BurnKernel.FrontTick(ref nextFrontTick, Find.TickManager.TicksGame, enabled, ScheduleTicks) != RM_FrontAction.Fire)
            {
                return;
            }

            // DEEP_TRIBES_FIRE_RITE_1 — sometimes this scheduled burn is not the
            // biome's own, it is the Tribes'. The rite REPLACES the front rather
            // than adding to it: the party walks in and lights it themselves when
            // they arrive, so the clock has fired either way. Anything that stops
            // the rite being sendable (no Tribes in this world, at war, nowhere to
            // walk in from) falls straight through to the plain front below, which
            // is what "all-off degrades to the fire clock" means.
            if (TryRunRite())
            {
                return;
            }

            int lit = TryStartFront();
            if (lit > 0)
            {
                Find.LetterStack.ReceiveLetter(
                    "RM_FireFrontLetterLabel".Translate(),
                    "RM_FireFrontLetterText".Translate(),
                    LetterDefOf.NegativeEvent,
                    new TargetInfo(lastOrigin, map));
            }
        }

        /// <summary>
        /// Re-arm the clock. The interval is randomized per front rather than
        /// fixed, so the player learns "every few days" and never learns a tick
        /// count to farm.
        /// </summary>
        private static int ScheduleTicks()
        {
            // MOD_OPTIONS_RETROFIT_1 absorption: the per-number sliders that
            // used to live on mandrake.rut.pyrelandsmechanics' settings screen
            // were not re-exposed — fireClockEnabled is the one switch RM_
            // Pyrelands ships for this mechanic. Values are unchanged from
            // shipped defaults (PyrelandsTuning.FireFrontMinDays/MaxDays).
            float minDays = PyrelandsTuning.FireFrontMinDays;
            float maxDays = PyrelandsTuning.FireFrontMaxDays;
            return RM_BurnKernel.ScheduleTicks(minDays, maxDays, Rand.Value, GenDate.TicksPerDay);
        }

        private IntVec3 lastOrigin = IntVec3.Invalid;

        /// <summary>
        /// Light the front. Returns how many cells actually took, which is 0 on a
        /// map that is soaked, paved or entirely roofed — a legitimate outcome,
        /// not an error, and the clock has already been re-armed either way.
        /// </summary>
        private int TryStartFront()
        {
            if (!TryFindOrigin(out IntVec3 origin))
            {
                return 0;
            }
            lastOrigin = origin;
            return IgniteAt(origin, null);
        }

        /// <summary>
        /// DEEP_TRIBES_FIRE_RITE_1 — roll the rite, and send it if it rolls.
        /// Returns true only when a party is actually standing on the map with a
        /// Lord; every other outcome returns false so the caller lights the plain
        /// front instead and the clock never silently skips a beat.
        /// </summary>
        private bool TryRunRite()
        {
            // PyrelandsFireRiteHook — null on a franchise-free world (no
            // campaign mod loaded to fill it in), which falls straight through
            // to the plain front below. The hook implementation (Utinni's
            // PyrelandsFireRite.TrySend, if present) does its OWN enabled/
            // frequency gating; RM_Pyrelands does not know the Tribes exist.
            if (PyrelandsFireRiteHook.TrySend == null)
            {
                return false;
            }
            if (!TryFindOrigin(out IntVec3 origin))
            {
                return false;
            }
            lastOrigin = origin;
            return PyrelandsFireRiteHook.TrySend(map, origin);
        }

        /// <summary>
        /// Light a front on one bearing through <paramref name="origin"/>.
        ///
        /// 🔴 The instigator is the whole difference between the biome's front and
        /// the Tribes' rite. Null is the biome (no arson debt, nobody's fault);
        /// the lead harvester is the rite (still no arson debt — see
        /// MapComponent_BurnLine.IsPlayerAttributed, which only counts fires whose
        /// instigator belongs to the PLAYER — but every burn that follows now
        /// carries their name, because Fire.TrySpread hands the instigator down to
        /// every child fire).
        /// </summary>
        internal int IgniteAt(IntVec3 origin, Thing instigator)
        {
            return IgniteLine(origin, instigator, PyrelandsTuning.FireFrontWidthCells, PyrelandsTuning.FireFrontFireSize);
        }

        /// <summary>IgniteAt's body with the line's width and fire size given: the scheduled front and the rite pass the
        /// front's own, the opening front its smaller line (PYRE_OPENING_FRONT).</summary>
        private int IgniteLine(IntVec3 origin, Thing instigator, int width, float fireSize)
        {
            if (!origin.IsValid)
            {
                return 0;
            }

            // A bearing for the LINE itself; the burn then walks off it in
            // whichever direction vanilla's own spread maths prefers.
            float angle = Rand.Range(0f, 360f);

            RM_BurnKernel.FrontLine(angle, width, out int[] offX, out int[] offZ);
            int lit = 0;

            // RM_BurnKernel.FrontLine gives exactly `width` DISTINCT cells at any bearing, for odd and even widths
            // (an `i <= half` loop lit one cell too many on an even width; a unit Euclidean step truncated to cells
            // folded a diagonal 9-wide line onto about 5 cells).
            for (int i = 0; i < offX.Length; i++)
            {
                IntVec3 cell = origin + new IntVec3(offX[i], 0, offZ[i]);
                if (!IsLawfulFrontCell(cell))
                {
                    continue;
                }
                if (FireUtility.TryStartFireIn(cell, map, fireSize, instigator))
                {
                    lit++;
                }
            }

            return lit;
        }

        /// <summary>
        /// Where the front starts. Weighted toward ember-grass because ember-grass
        /// IS the biome's fuel ladder (src/RimMandrake/Pyrelands/Defs/
        /// ThingDefs_Plants/EmberGrass.xml) — a front that starts in the fuel is a
        /// front that goes somewhere.
        ///
        /// Two passes, not a weighted sum: sample for an ember-grass cell first,
        /// and only fall back to any lawful flammable cell if the map has none.
        /// Cheaper than scoring the whole map and it degrades to the reseed's own
        /// behaviour on a map where the plant never established.
        /// </summary>
        private bool TryFindOrigin(out IntVec3 origin)
        {
            ThingDef emberGrass = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_EmberGrass");
            if (emberGrass != null)
            {
                List<Thing> grass = map.listerThings.ThingsOfDef(emberGrass);
                if (grass.Count > 0)
                {
                    for (int i = 0; i < PyrelandsTuning.FireFrontEmberGrassTries; i++)
                    {
                        IntVec3 c = grass[Rand.Range(0, grass.Count)].Position;
                        if (IsLawfulFrontCell(c))
                        {
                            origin = c;
                            return true;
                        }
                    }
                }
            }

            return CellFinderLoose.TryGetRandomCellWith(
                IsLawfulFrontCell, map, PyrelandsTuning.FireFrontSeedTries, out origin);
        }

        /// <summary>
        /// The same four gates the standing-burn reseed passes — this is the
        /// biome, not an attack. Shared with MapComponent_BurnLine so a change to
        /// "where the biome may light" only ever has to be made once.
        /// </summary>
        private bool IsLawfulFrontCell(IntVec3 c)
        {
            return MapComponent_BurnLine.For(map)?.IsLawfulBurnCell(c) ?? false;
        }
    }

    /// <summary>
    /// Yesterday's fire (PYRE_OPENING_FRONT, 2026-11-07). The walk bar pyre_burn_line_present, owner's words: "a fresh
    /// Pyrelands map shows an active line of fire somewhere, with a visibly scorched trail behind its advancing front".
    /// On map s the 5-cell opening line lit in standing grass: a fire, but no trail behind it. So a fresh map starts with
    /// a half-disc scar burned in from one edge, and the opening front lights along its leading arc.
    ///
    /// Depth is radial (distance from the scar's centre on the edge over the ragged boundary at that bearing): the fire
    /// started at the edge and walked inward, so 0 is the oldest char and 1 is the line still burning.
    /// </summary>
    internal static class PyrelandsYesterdayFire
    {
        private static readonly string[] Sides = { "north", "east", "south", "west" };

        /// <summary>One scar's shape: centre on the map edge, inward normal, nominal radius and the ragged edge's noise. Rebuilt
        /// from the saved plan (the seed is the map's id and the centre), so the arc after a load is the arc that was laid.</summary>
        private sealed class Shape
        {
            internal readonly Map map;
            internal readonly IntVec3 centre;
            internal readonly int nx, nz;
            internal readonly float radius;
            internal readonly CellRect box;
            private readonly Perlin noise;
            private readonly bool wetNear;

            internal Shape(Map map, IntVec3 centre, int edge, float radius)
            {
                this.map = map;
                this.centre = centre;
                this.radius = radius;
                RM_BurnKernel.ScarEdgeFrame(edge, 0.5f, map.Size.x, map.Size.z, out _, out _, out nx, out nz);
                int reach = Mathf.CeilToInt(radius * (1f + PyrelandsTuning.YesterdayFireRagged)) + 2;
                box = CellRect.CenteredOn(centre, reach).ClipInsideMap(map);
                noise = new Perlin(PyrelandsTuning.YesterdayFireEdgeFrequency, 2.0, 0.5, 3,
                    Gen.HashCombineInt(map.uniqueID * 7919 + 2203, centre.x * 4099 + centre.z), QualityMode.Medium);
                wetNear = AnyWater(map, box.ExpandedBy(Mathf.CeilToInt(PyrelandsTuning.YesterdayFireWetReach)).ClipInsideMap(map));
            }

            /// <summary>True when c lies inside the ragged half-disc; depth01 is its distance over the boundary there.</summary>
            internal bool Contains(IntVec3 c, out float depth01)
            {
                depth01 = 0f;
                float dx = c.x - centre.x, dz = c.z - centre.z;
                if (dx * nx + dz * nz < 0f) return false;
                // z 0.37: off the lattice, where Perlin reads 0 at every whole coordinate.
                float n = (float)noise.GetValue(RM_BurnKernel.ScarBearing(dx, dz, nx, nz) * radius, 0.0, 0.37);
                float edge = RM_BurnKernel.ScarBoundary(radius, n, PyrelandsTuning.YesterdayFireRagged);
                float dist = Mathf.Sqrt(dx * dx + dz * dz);
                if (edge <= 0f || dist > edge) return false;
                depth01 = dist / edge;
                return true;
            }

            internal bool Burnable(IntVec3 c) => PyrelandsYesterdayFire.Burnable(map, c, wetNear);
        }

        /// <summary>Ground yesterday's fire burned: open, unroofed, scorchable, dry ground with no building on it (rock, a wall
        /// and a ruin are all buildings), outside home and any zone. Wet ground is the green ring around water (about
        /// YesterdayFireWetReach, GenStep_PyrelandsGreenRing): that grass did not burn.</summary>
        private static bool Burnable(Map map, IntVec3 c, bool checkWet)
        {
            if (!c.InBounds(map) || map.roofGrid.Roofed(c)) return false;
            TerrainDef t = c.GetTerrain(map);
            if (t == null || t.IsWater || t.passability == Traversability.Impassable || !FireEcologyHookMod.IsScorchableGround(t)) return false;
            if (c.GetFirstBuilding(map) != null || map.areaManager.Home[c] || map.zoneManager.ZoneAt(c) != null) return false;
            if (checkWet)
            {
                int n = GenRadial.NumCellsInRadius(PyrelandsTuning.YesterdayFireWetReach);
                for (int i = 1; i < n; i++)
                {
                    IntVec3 w = c + GenRadial.RadialPattern[i];
                    if (w.InBounds(map) && w.GetTerrain(map).IsWater) return false;
                }
            }
            return true;
        }

        private static bool AnyWater(Map map, CellRect r)
        {
            foreach (IntVec3 c in r)
            {
                if (c.GetTerrain(map).IsWater) return true;
            }
            return false;
        }

        /// <summary>What the scar must keep its farthest reach YesterdayFireFrontClearance from: the map centre and, at
        /// generation, the landing spot (none on a gravship landing); at runtime every free colonist on the map.</summary>
        private static List<IntVec3> References(Map map, bool atGeneration)
        {
            List<IntVec3> refs = new List<IntVec3> { map.Center };
            if (atGeneration)
            {
                if (MapGenerator.PlayerStartSpotValid) refs.Add(MapGenerator.PlayerStartSpot);
            }
            else
            {
                foreach (Pawn p in map.mapPawns.FreeColonistsSpawned) refs.Add(p.Position);
            }
            return refs;
        }

        /// <summary>Picks the scar: YesterdayFireSitesPerEdge sites on each edge, away from the corners, each with its own
        /// rolled radius shrunk to the clearance; a site is kept when enough of a sample of its half-disc can burn. False on
        /// a map too small for any (ScarRadius 0), or with no usable site.</summary>
        internal static bool TryPlan(Map map, bool atGeneration, out IntVec3 centre, out int edge, out float radius)
        {
            centre = IntVec3.Invalid;
            edge = -1;
            radius = 0f;
            List<IntVec3> refs = References(map, atGeneration);
            List<IntVec3> sites = new List<IntVec3>();
            List<int> siteEdges = new List<int>();
            List<float> siteRadii = new List<float>();
            for (int e = 0; e < 4; e++)
            {
                for (int s = 0; s < PyrelandsTuning.YesterdayFireSitesPerEdge; s++)
                {
                    float along = Rand.Range(PyrelandsTuning.YesterdayFireSiteMinAlong, PyrelandsTuning.YesterdayFireSiteMaxAlong);
                    RM_BurnKernel.ScarEdgeFrame(e, along, map.Size.x, map.Size.z, out int cx, out int cz, out int nx, out int nz);
                    IntVec3 c0 = new IntVec3(cx, 0, cz);
                    float clearance = float.MaxValue;
                    foreach (IntVec3 r in refs) clearance = Mathf.Min(clearance, c0.DistanceTo(r));
                    float rad = RM_BurnKernel.ScarRadius(Rand.Range(PyrelandsTuning.YesterdayFireMinRadius, PyrelandsTuning.YesterdayFireMaxRadius),
                        clearance, PyrelandsTuning.YesterdayFireFrontClearance, PyrelandsTuning.YesterdayFireRagged, PyrelandsTuning.YesterdayFireFloorRadius);
                    if (rad <= 0f) continue;
                    bool wet = AnyWater(map, CellRect.CenteredOn(c0, Mathf.CeilToInt(rad * (1f + PyrelandsTuning.YesterdayFireRagged)
                        + PyrelandsTuning.YesterdayFireWetReach)).ClipInsideMap(map));
                    int ok = 0;
                    for (int i = 0; i < PyrelandsTuning.YesterdayFireSiteSamples; i++)
                    {
                        float a = Rand.Range(-90f, 90f) * Mathf.Deg2Rad, d = rad * Mathf.Sqrt(Rand.Value);
                        // The normal rotated by a: (nx cos - nz sin, nx sin + nz cos).
                        IntVec3 p = c0 + new IntVec3(Mathf.RoundToInt(d * (nx * Mathf.Cos(a) - nz * Mathf.Sin(a))), 0,
                            Mathf.RoundToInt(d * (nx * Mathf.Sin(a) + nz * Mathf.Cos(a))));
                        if (Burnable(map, p, wet)) ok++;
                    }
                    if (!RM_BurnKernel.ScarSiteUsable(ok, PyrelandsTuning.YesterdayFireSiteSamples, PyrelandsTuning.YesterdayFireSiteMinBurnable)) continue;
                    sites.Add(c0);
                    siteEdges.Add(e);
                    siteRadii.Add(rad);
                }
            }
            if (sites.Count == 0) return false;
            int k = Rand.Range(0, sites.Count);
            centre = sites[k];
            edge = siteEdges[k];
            radius = siteRadii[k];
            return true;
        }

        /// <summary>Burns the scar in: its plants go (trees stand: a grass fire runs under them), then the ash and the burn
        /// stamps (after the plants, so the drift field's burn-edge lift lands on the rim), then the sprouts where it is
        /// oldest and the ripe pods where it is youngest.</summary>
        internal static void Lay(Map map, IntVec3 centre, int edge, float radius, int now)
        {
            Shape shape = new Shape(map, centre, edge, radius);
            List<IntVec3> cells = new List<IntVec3>();
            List<float> depths = new List<float>();
            foreach (IntVec3 c in shape.box)
            {
                if (shape.Contains(c, out float d) && shape.Burnable(c))
                {
                    cells.Add(c);
                    depths.Add(d);
                }
            }
            foreach (IntVec3 c in cells)
            {
                Plant p = c.GetPlant(map);
                if (p != null && !p.def.plant.IsTree) p.Destroy(DestroyMode.Vanish);
            }
            MapComponent_PyrelandsAshField ash = MapComponent_PyrelandsAshField.For(map);
            for (int i = 0; i < cells.Count; i++)
            {
                PyrelandsDriftField.LayScarAsh(map, cells[i]);
                ash?.StampBurn(cells[i], RM_BurnKernel.ScarStampTick(now, depths[i],
                    PyrelandsTuning.YesterdayFireOldestAgeTicks, PyrelandsTuning.YesterdayFireYoungestAgeTicks));
            }

            // Sprouts at about the wild ratio of the biome's two grasses.
            ThingDef ember = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_EmberGrass");
            ThingDef quick = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_Quickgrass");
            float wEmber = ember != null ? map.Biome.CommonalityOfPlant(ember) : 0f;
            float wQuick = quick != null ? map.Biome.CommonalityOfPlant(quick) : 0f;
            if (wEmber + wQuick <= 0f) wEmber = ember != null ? 1f : 0f;
            for (int i = 0; i < cells.Count && wEmber + wQuick > 0f; i++)
            {
                if (!Rand.Chance(RM_BurnKernel.ScarSproutChance(depths[i], PyrelandsTuning.YesterdayFireSproutChance,
                    PyrelandsTuning.YesterdayFireSproutEndDepth))) continue;
                ThingDef def = Rand.Value * (wEmber + wQuick) < wEmber ? ember : quick;
                if (!def.CanEverPlantAt(cells[i], map, false, false)) continue;
                Plant sprout = (Plant)ThingMaker.MakeThing(def);
                sprout.Growth = Rand.Range(PyrelandsTuning.YesterdayFireSproutGrowthMin, PyrelandsTuning.YesterdayFireSproutGrowthMax);
                GenSpawn.Spawn(sprout, cells[i], map);
            }

            // Ripe pods, as the burn's own fruit roll lands them (Patch_FireTick_AshAndScorchFruit): legal spot, map cap.
            ThingDef fruitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_ScorchFruit");
            if (fruitDef == null || !RM_PyrelandsSettings.scorchFruitEnabled) return;
            List<IntVec3> young = new List<IntVec3>();
            for (int i = 0; i < cells.Count; i++)
            {
                // Standable by Burnable (no building, passable ground); not the path grid, which is not built during generation.
                if (depths[i] >= PyrelandsTuning.YesterdayFireYoungDepth && RM_FireEcoKernel.FruitLandingLegal(true, true,
                    cells[i].GetPlant(map) != null, FireEcologyHookMod.IsScorchableGround(cells[i].GetTerrain(map)))) young.Add(cells[i]);
            }
            young.Shuffle();
            for (int i = 0; i < young.Count && i < PyrelandsTuning.YesterdayFirePods; i++)
            {
                if (!RM_FireEcoKernel.UnderFruitCap(map.listerThings.ThingsOfDef(fruitDef).Count, RM_PyrelandsSettings.scorchFruitMapCap)) break;
                Thing fruit = ThingMaker.MakeThing(fruitDef);
                if (fruit is Plant pod) pod.Growth = 1f;
                GenSpawn.Spawn(fruit, young[i], map);
            }
        }

        /// <summary>The leading arc: grass cells just outside the boundary (a cardinal neighbour inside it), on bearings within
        /// YesterdayFireArcMinCos of the inward normal, lawful for the biome to light; in bearing order, so a stride reads as a line.</summary>
        internal static List<IntVec3> ArcCells(Map map, IntVec3 centre, int edge, float radius, MapComponent_BurnLine line)
        {
            Shape shape = new Shape(map, centre, edge, radius);
            List<IntVec3> arc = new List<IntVec3>();
            List<float> bearings = new List<float>();
            foreach (IntVec3 c in shape.box)
            {
                float dx = c.x - centre.x, dz = c.z - centre.z;
                if (!RM_BurnKernel.ArcFacing(dx, dz, shape.nx, shape.nz, PyrelandsTuning.YesterdayFireArcMinCos) || shape.Contains(c, out _)) continue;
                bool rim = false;
                for (int k = 0; k < 4 && !rim; k++)
                {
                    IntVec3 n = c + GenAdj.CardinalDirections[k];
                    rim = n.InBounds(map) && shape.Contains(n, out _);
                }
                if (!rim) continue;
                Plant p = c.GetPlant(map);
                if (p == null || p.def.plant.IsTree || line == null || !line.IsLawfulBurnCell(c)) continue;
                arc.Add(c);
                bearings.Add(RM_BurnKernel.ScarBearing(dx, dz, shape.nx, shape.nz));
            }
            List<int> order = new List<int>(arc.Count);
            for (int i = 0; i < arc.Count; i++) order.Add(i);
            order.Sort((a, b) => bearings[a].CompareTo(bearings[b]));
            List<IntVec3> sorted = new List<IntVec3>(arc.Count);
            foreach (int i in order) sorted.Add(arc[i]);
            return sorted;
        }

        /// <summary>The probe's census of a laid scar: burnable cells inside it, bare ones, young grass, pods, ashed cells.</summary>
        internal static string Census(Map map, IntVec3 centre, int edge, float radius)
        {
            Shape shape = new Shape(map, centre, edge, radius);
            ThingDef fruitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_ScorchFruit");
            ThingDef ashDef = PyrelandsDriftField.AshDef;
            int cells = 0, bare = 0, sprouts = 0, pods = 0, ashed = 0;
            foreach (IntVec3 c in shape.box)
            {
                if (!shape.Contains(c, out _) || !shape.Burnable(c)) continue;
                cells++;
                Plant p = c.GetPlant(map);
                if (p == null) bare++;
                else if (p.def == fruitDef) pods++;
                else if (!p.def.plant.IsTree) sprouts++;
                if (ashDef != null && c.GetFirstThing(map, ashDef) != null) ashed++;
            }
            return string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "scarCells={0};bare={1};sprouts={2};pods={3};ash={4}", cells, bare, sprouts, pods, ashed);
        }

        internal static string Side(int edge) => edge >= 0 && edge < 4 ? Sides[edge] : "none";
    }

    /// <summary>Lays yesterday's fire on a fresh Pyrelands map (PyrelandsYesterdayFire). Order 1220 (PyrelandsGenSteps.xml):
    /// after every Pyrelands step and vanilla's Plants and Animals, so no later fill re-grasses the scar.</summary>
    public class GenStep_PyrelandsYesterdayFire : GenStep
    {
        public override int SeedPart => 0x59F1E0A7;

        public override void Generate(Map map, GenStepParams parms)
        {
            MapComponent_BurnLine.For(map)?.FireFront?.LayYesterdayFire(true);
        }
    }
}
