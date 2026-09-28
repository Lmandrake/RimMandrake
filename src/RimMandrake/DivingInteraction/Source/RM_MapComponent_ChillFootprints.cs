using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_THERMAL_FOOTPRINTS_1 — warmth writes on the ice.
    //
    // Owner, card pick, 2026-09-27 sitting: "Everything warm marks the
    // Chill's ice floor — a walking pawn's melt-prints refreeze glossy, a
    // parked warm machine leaves a polished shadow. The expedition's
    // history is written on the floor, permanent-ish and legible."
    //
    // SCOPE: RM_ChillFireGate.IsChillSeabedMap(map) only, same identity
    // check every sibling Chill mechanism uses this session.
    //
    // SCOPE GUARD (binding — item's own text): melt-settle, fogging-the-
    // windows and supercool pools were NOT adopted at the same sitting.
    // This file builds thermal footprints ONLY.
    //
    // ── THE PERSISTENCE DECISION — read this before touching the file ──
    // RM_MapComponent_ChillBoilShroud (this mod's closest structural
    // precedent) does NOT Scribe its grade grid at all — it is a cosmetic
    // heat-map rebuilt from scratch every 60-tick rescan, which is exactly
    // wrong for "a durable historical record, not a live-recomputed heat
    // map" (this item's own hard requirement). A hand-rolled byte[] grid
    // (RM_MapComponent_Excavation's DataExposeUtility.LookByteArray idiom)
    // would work, but this codebase already has a PROVEN, ENGINE-OWNED
    // persistence mechanism for exactly this shape of problem: Filth.
    // RM_CompFilthTrail (EnvironmentalHazards, SUMP_MECHANICS_1) already
    // ships "a pawn crosses terrain, a mark gets left, it needs to survive
    // save/load" using ordinary Filth — and Filth is a real spawned Thing,
    // so its persistence rides Map.ExposeData's own ThingOwner Scribe with
    // ZERO custom save code, the same way every other Thing on every map
    // already survives a save/load round-trip. That is the whole answer to
    // "trace the Scribe code path": there isn't a custom one to get wrong.
    // Filth ALSO gives density for free — Filth.thickness (capped at a
    // hardcoded 5, RimWorld/Filth.cs, same fact RM_CompFilthTrail's own
    // header already recorded) IS the trail's density, read live off the
    // map, never duplicated into a second number that could drift from it.
    //
    // WHY THIS MAP ACCEPTS THE FILTH WITHOUT A PATCH (verified against the
    // decompiled engine, RimSage, not assumed — RM_CompFilthTrail's own
    // header shows a sibling case where this silently fails and needs a
    // patch, so it was checked here rather than copied blind):
    // FilthMaker.TerrainAcceptsFilth requires
    // (terrain.filthAcceptanceMask & (filthDef.filth.placementMask |
    // additionalFlags)) == that same mask. This map's own floor terrain —
    // RM_ChillIceBedrock since CHILL_RIME_TERRACES_1 (2026-09-28; was the
    // shared RM_SeaFloorGround before) — inherits NaturalTerrainBase's
    // filthAcceptanceMask unchanged, which is exactly
    // [Unnatural]; FilthProperties.placementMask defaults to exactly
    // FilthSourceFlags.Unnatural and RM_Filth_ChillFrostGlaze
    // (Defs/ThingDefs_Misc/RM_ChillFootprintFilth.xml) does not override
    // it. Unnatural & Unnatural == Unnatural ⇒ every deposit call below
    // (which passes no additionalFlags) succeeds on this terrain today,
    // with no filthAcceptanceMask patch needed. RM_ChillRimeTerrace (the
    // rime-terrace districts CHILL_RIME_TERRACES_1 paints over patches of
    // this same floor) is the same NaturalTerrainBase-inherited mask too,
    // unoverridden — footprints deposit on both without distinction.
    //
    // WHY "PERMANENT-ISH": RM_Filth_ChillFrostGlaze sets no
    // <disappearsInDays>, so FilthProperties.disappearsInDays defaults to
    // FloatRange.Zero ⇒ Filth.disappearAfterTicks is computed as 0 on
    // spawn ⇒ SteadyEnvironmentEffects' own `DisappearAfterTicks != 0`
    // guard (RimWorld/SteadyEnvironmentEffects.cs) never fires for it —
    // this filth never auto-evaporates the way Filth_Water's 0.2~0.4-day
    // puddle does. It is still ordinary Filth, so a colonist can clean it
    // (only inside a marked home area — WorkGiver_CleanFilth reads
    // listerFilthInHomeArea, and a seabed pocket map is not home area
    // unless the player deliberately makes it one) — that is vanilla's own
    // "permanent unless someone chooses to scrub it," which is exactly
    // what "permanent-ish" reads as, not a defect to work around.
    //
    // TWO SHAPES, ONE FILTH DEF, NO SEPARATE ART OR TUNING NEEDED:
    //   PAWN   — deposits once per cell actually MOVED INTO (a
    //            Dictionary<pawn id, last cell> compared each rescan), so
    //            a walking pawn leaves a thin, moving line of thickness-1
    //            marks — "melt-prints."
    //   MACHINE — a parked (stationary, by construction — it is a
    //            building) powered device deposits under its own whole
    //            footprint EVERY rescan, so it saturates to max thickness
    //            fast — "a polished shadow," visibly denser than a pawn's
    //            passing trail, using vanilla's own Graphic_Cluster
    //            (BaseFilth's graphicClass) to draw MORE copies of the
    //            same texture as thickness rises. No new FleckDef, no new
    //            art beyond the one placeholder FilthDef.
    //
    // DELIVERABLE 3 (rime terraces, NOT a bar — CHILL_RIME_TERRACES_1
    // doesn't exist yet): the natural hook for a future terrain-dependent
    // print variant is DepositAt's own terrain read, immediately below —
    // swap FootprintFilthDef for a terrain-keyed lookup there once a rime
    // terrace TerrainDef exists. Nothing here blocks on it.
    //
    // COST: no O(n²) anywhere. Each rescan is O(pawns + powered things) —
    // a dictionary lookup and at most one FilthMaker call per pawn, one
    // per powered-thing cell — same shape and a shorter cadence than
    // RM_MapComponent_ChillBoilShroud's own 60-tick room+radial scan on
    // this same small pocket map. The per-pawn last-cell dictionary is
    // pruned every scan (entries for despawned/no-longer-present pawns are
    // dropped), so it cannot grow unbounded either.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ChillFootprints : MapComponent
    {
        private const string FootprintFilthDefName = "RM_Filth_ChillFrostGlaze";

        // Tight enough to catch nearly every cell a normally-paced pawn
        // crosses (vanilla move speed puts a cell every ~13 ticks) without
        // running per-tick. Cheap: see the class header's COST note.
        private const int RescanIntervalTicks = 15;

        // RimWorld/Filth.cs: `private const int MaxThickness = 5` — the
        // real, hardcoded cap FilthMaker.TryMakeFilth's own CanBeThickened
        // check enforces, distinct from (and stricter than)
        // FilthProperties.maxThickness. Same fact RM_CompFilthTrail.cs's
        // own header already recorded for this codebase.
        private const int MaxObservedThickness = 5;

        private static ThingDef cachedFilthDef;

        private bool isChillSeabed;
        private int ticksUntilRescan = 1;

        // Runtime-only efficiency cache, NOT Scribed — same idiom
        // RM_MapComponent_ChannelCurrent's own occupant dictionary uses
        // ("rebuilt from the grid/terrain scan"). Losing it on load costs
        // nothing worse than one redundant (idempotent, thickness-capped)
        // deposit at each pawn's already-marked current cell; the actual
        // persistent record — the Filth itself — is unaffected either way.
        private readonly Dictionary<int, IntVec3> lastPawnCell = new Dictionary<int, IntVec3>();
        private readonly HashSet<int> seenThisScan = new HashSet<int>();

        public RM_MapComponent_ChillFootprints(Map map) : base(map)
        {
        }

        private static ThingDef FootprintFilthDef
        {
            get
            {
                if (cachedFilthDef == null)
                {
                    cachedFilthDef = DefDatabase<ThingDef>.GetNamedSilentFail(FootprintFilthDefName);
                }
                return cachedFilthDef;
            }
        }

        private bool Active => isChillSeabed
            && RM_DivingSettings.masterEnabled
            && RM_DivingSettings.chillThermalFootprintsEnabled;

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            isChillSeabed = RM_ChillFireGate.IsChillSeabedMap(map);
            ticksUntilRescan = RescanIntervalTicks;
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!isChillSeabed)
            {
                return; // every other map in the game: one bool check, nothing else
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillThermalFootprintsEnabled)
            {
                return;
            }

            if (--ticksUntilRescan > 0)
            {
                return;
            }
            ticksUntilRescan = RescanIntervalTicks;
            Scan();
        }

        private void Scan()
        {
            if (FootprintFilthDef == null)
            {
                return; // def failed to resolve (mod load order); nothing to deposit, nothing to crash
            }

            seenThisScan.Clear();

            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || !p.Spawned || p.Position.Roofed(map))
                {
                    continue; // sheltered indoors already reads calm, same reading BoilShroud uses for warm things
                }

                seenThisScan.Add(p.thingIDNumber);
                IntVec3 prev = lastPawnCell.TryGetValue(p.thingIDNumber, out IntVec3 recorded)
                    ? recorded
                    : IntVec3.Invalid;
                if (prev == p.Position)
                {
                    continue; // hasn't moved to a new cell since the last scan — no fresh melt-print to lay
                }
                lastPawnCell[p.thingIDNumber] = p.Position;
                DepositAt(p.Position);
            }

            // Prune entries for pawns no longer present — despawned, dead,
            // or moved off this map — so the dictionary tracks only the
            // live population and cannot grow without bound.
            if (lastPawnCell.Count > seenThisScan.Count)
            {
                List<int> stale = null;
                foreach (int id in lastPawnCell.Keys)
                {
                    if (!seenThisScan.Contains(id))
                    {
                        (stale ?? (stale = new List<int>())).Add(id);
                    }
                }
                if (stale != null)
                {
                    for (int i = 0; i < stale.Count; i++)
                    {
                        lastPawnCell.Remove(stale[i]);
                    }
                }
            }

            List<Thing> powered = map.listerThings.ThingsInGroup(ThingRequestGroup.PowerTrader);
            for (int i = 0; i < powered.Count; i++)
            {
                Thing t = powered[i];
                if (t == null || !t.Spawned || t.Position.Roofed(map))
                {
                    continue;
                }
                CompPowerTrader power = t.TryGetComp<CompPowerTrader>();
                if (power == null || !power.PowerOn)
                {
                    continue;
                }

                // "A parked warm machine" — every scan, every cell of its
                // own footprint, so a stationary device saturates to max
                // thickness fast: the "polished shadow," visibly denser
                // than a pawn's single-thickness passing trail.
                CellRect rect = t.OccupiedRect();
                foreach (IntVec3 c in rect)
                {
                    DepositAt(c);
                }
            }
        }

        private void DepositAt(IntVec3 c)
        {
            if (!c.InBounds(map) || c.Roofed(map) || !c.Standable(map))
            {
                return;
            }
            FilthMaker.TryMakeFilth(c, map, FootprintFilthDef);
        }

        /// <summary>
        /// CHILL_GARDEN_DEFENSE_1's read hook: 0 (pristine) .. 1 (fully
        /// scarred, thickness 5) trail density at <paramref name="cell"/>.
        /// Reads the live Filth directly — never a second tracked number
        /// that could drift from what is actually on the ground. Returns 0
        /// whenever this mechanism is inert (off map, toggled off, def
        /// unresolved) so a caller never needs its own gating.
        /// </summary>
        public float TrailDensityAt(IntVec3 cell)
        {
            if (!Active || !cell.InBounds(map) || FootprintFilthDef == null)
            {
                return 0f;
            }

            List<Thing> here = cell.GetThingList(map);
            for (int i = 0; i < here.Count; i++)
            {
                if (here[i] is Filth filth && filth.def == FootprintFilthDef)
                {
                    return Mathf.Clamp01(filth.thickness / (float)MaxObservedThickness);
                }
            }
            return 0f;
        }
    }
}
