// LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY: live proof hooks for the Lean rows (walk lines 39-41), driven by validation.py's
// lean chain through jawa/static_call on the saved RM_LeaningScrub site. Each answers "PASS ...", "FAIL ..." or
// "UNMEASURED ..." and leaves the map as it found it (it destroys only what it spawned, and restores every setting).
//   ProofHeading()         the wind points at the sun: HeadingDegrees == HeadingFromSunBearing(SunGeometry(tile)),
//                          Downwind == its (cos, sin), and a second read answers the same (one heading per map).
//   ProofScent("on@x,z")   a wild non-predator native at (x,z) flees a person 8 cells UPWIND (within leanScentRange),
//                          never one 8 cells DOWNWIND, never one upwind beyond the range. Through the SHIPPED path:
//                          JobGiver_AnimalFlee.TryIssueJobPackage, so the Harmony postfix runs as in play.
//   ProofScent("off@x,z")  leanScentEnabled false: the upwind person draws no flee.
//   ProofFire("on@x,z")    300 single fires per arm on a nine-cell grass bed, each spread through the SHIPPED
//                          Fire.TrySpread (prefix included); among immediate neighbour ignitions the downwind share
//                          must beat the leanFireEnabled-off share by half the lift leanFireBias promises, z >= 3.
//   ProofFire("off@x,z")   the off arm alone: reports the vanilla share (PASS when measured; the comparison is "on").
using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    public static class RM_TheLeanProof
    {
        private const int ScentStep = 8;
        private const int FireTrials = 300;
        private const float FireBed = 1.5f; // the trial fire and its eight neighbours: the grass bed

        private static bool ParseAt(string args, out string mode, out IntVec3 at)
        {
            mode = (args ?? "").Trim();
            at = IntVec3.Invalid;
            int i = mode.IndexOf('@');
            if (i < 0) return false;
            string[] xz = mode.Substring(i + 1).Split(',');
            mode = mode.Substring(0, i);
            if (xz.Length != 2 || !int.TryParse(xz[0], out int x) || !int.TryParse(xz[1], out int z)) return false;
            at = new IntVec3(x, 0, z);
            return true;
        }

        private static string LeanOrWhy(Map map, out RM_MapComponent_Lean lean)
        {
            lean = null;
            if (map == null) return "UNMEASURED: no current map";
            if (map.Biome?.GetModExtension<RM_LeanExtension>() == null)
                return "UNMEASURED: not a Leaning Scrub map (biome " + map.Biome?.defName + " carries no RM_LeanExtension)";
            lean = map.GetComponent<RM_MapComponent_Lean>();
            if (lean == null) return "FAIL: RM_MapComponent_Lean is not on a Leaning Scrub map";
            if (!lean.Applies) return "FAIL: RM_MapComponent_Lean.Applies false on a biome carrying RM_LeanExtension";
            return null;
        }

        // ── heading ──────────────────────────────────────────────────────────────────────────────────────────────
        public static string ProofHeading()
        {
            Map map = Find.CurrentMap;
            string why = LeanOrWhy(map, out RM_MapComponent_Lean lean);
            if (why != null) return why;
            RM_LeanExtension ext = map.Biome.GetModExtension<RM_LeanExtension>();
            if (!map.Tile.Valid) return "UNMEASURED: the map has no world tile";
            Vector2 longLat = Find.WorldGrid.LongLatOf(map.Tile);
            RimMandrake.CreatureBehaviors.RM_MapComponent_PinnedSun.SunGeometry(longLat.y, longLat.x,
                ext.substellarLatitude, ext.substellarLongitude, out float bearing, out float _);
            float want = RM_LeanKernel.HeadingFromSunBearing(bearing);
            float h1 = lean.HeadingDegrees;
            Vector2 d = lean.Downwind;
            float h2 = lean.HeadingDegrees;
            RM_LeanKernel.Direction(want, out float wx, out float wz);
            string st = string.Format("tile={0} lat={1:F2} long={2:F2} sunBearing={3:F3} heading={4:F3} want={5:F3} "
                + "downwind=({6:F3},{7:F3}) leansWest={8}", map.Tile, longLat.y, longLat.x, bearing, h1, want, d.x, d.y,
                RM_LeanKernel.WindLeansWest(d.x));
            if (h1 < 0f || h1 >= 360f) return "FAIL: heading outside [0,360) " + st;
            float diff = Mathf.Abs(Mathf.DeltaAngle(h1, want));
            if (diff > 0.01f) return "FAIL: the wind does not point at the sun " + st;
            if (Mathf.Abs(d.x - wx) > 1e-3f || Mathf.Abs(d.y - wz) > 1e-3f) return "FAIL: Downwind is not (cos,sin) of the heading " + st;
            if (h2 != h1) return "FAIL: the heading moved between two reads " + st;
            return "PASS " + st;
        }

        // ── scent ────────────────────────────────────────────────────────────────────────────────────────────────
        private static PawnKindDef NativeNonPredator(Map map)
        {
            foreach (PawnKindDef k in map.Biome.AllWildAnimals)
            {
                if (k?.RaceProps != null && k.RaceProps.Animal && !k.RaceProps.predator && !k.RaceProps.Dryad
                    && !k.RaceProps.Insect && map.Biome.CommonalityOfAnimal(k) > 0f)
                {
                    return k;
                }
            }
            return null;
        }

        private static IntVec3 Offset(IntVec3 c, Vector2 dir, float k)
        {
            RM_LeanKernel.Step(c.x, c.z, dir.x, dir.y, k, out int ox, out int oz);
            return new IntVec3(ox, 0, oz);
        }

        // A FRESH pawn with no relations: the convenience overload may redress an existing world pawn, which the
        // cleanup would then destroy (GPT review 2026-11-02).
        private static Pawn Fresh(PawnKindDef kind)
        {
            return PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, forceGenerateNewPawn: true,
                canGeneratePawnRelations: false));
        }

        // Destroy, then discard: Destroy alone may pass the pawn to WorldPawns and keep it referenced.
        private static void Dispose(Pawn p)
        {
            if (p == null) return;
            if (!p.Destroyed) p.Destroy();
            if (Find.WorldPawns.Contains(p)) Find.WorldPawns.RemoveAndDiscardPawnViaGC(p);
            else if (!p.Discarded) p.Discard(true);
        }

        private static Job FleeJobFor(Pawn animal)
        {
            JobGiver_AnimalFlee giver = new JobGiver_AnimalFlee();
            ThinkResult r = giver.TryIssueJobPackage(animal, default(JobIssueParams));
            return r.Job;
        }

        // canFlee: whether FleeUtility could route the animal away from this person at all (calibration: a boxed-in
        // animal fleeing nothing is UNMEASURED, never a scent FAIL). The distance mirrors RM_TheLeanPatches.AnimalFlee_Postfix:
        // max(24, ceil(distance) + 12).
        private static string Probe(Pawn animal, IntVec3 personAt, Map map, PawnKindDef personKind, out bool fled, out bool canFlee)
        {
            fled = canFlee = false;
            if (!personAt.InBounds(map) || !personAt.Standable(map)) return "cell " + personAt + " not standable";
            Pawn person = Fresh(personKind);
            try
            {
                GenSpawn.Spawn(person, personAt, map);
                Job j = FleeJobFor(animal);
                fled = j != null && (j.def == JobDefOf.Flee || j.def == JobDefOf.FleeAndCower);
                int dist = (int)Math.Ceiling((animal.Position - person.Position).LengthHorizontal);
                canFlee = FleeUtility.FleeJob(animal, person, Math.Max(24, dist + 12)) != null;
                return j == null ? "none" : j.def.defName;
            }
            finally
            {
                Dispose(person);
            }
        }

        public static string ProofScent(string args)
        {
            if (!ParseAt(args, out string mode, out IntVec3 at)) return "UNMEASURED: args must be on@x,z or off@x,z, got " + args;
            Map map = Find.CurrentMap;
            string why = LeanOrWhy(map, out RM_MapComponent_Lean lean);
            if (why != null) return why;
            PawnKindDef kind = NativeNonPredator(map);
            if (kind == null) return "UNMEASURED: RM_LeaningScrub lists no wild non-predator animal";
            // A factionless wild man: a person the animal can smell, with no colony and no hostility of its own.
            PawnKindDef personKind = DefDatabase<PawnKindDef>.GetNamedSilentFail("WildMan") ?? PawnKindDefOf.Villager;
            float range = RM_LeaningScrubSettings.leanScentRange;
            if (range <= ScentStep) return "UNMEASURED: leanScentRange " + range + " is not beyond the " + ScentStep + "-cell probe";
            if (!at.InBounds(map) || !at.Standable(map)) return "UNMEASURED: anchor " + at + " not standable";
            foreach (Pawn h in map.mapPawns.AllHumanlikeSpawned)
            {
                if (h.Position.InHorDistOf(at, range * 2f + ScentStep))
                    return "UNMEASURED: " + h.LabelShort + " at " + h.Position + " is within scent reach of the anchor " + at;
            }
            Vector2 dir = lean.Downwind;
            bool savedMod = RM_LeaningScrubSettings.modEnabled, savedLean = RM_LeaningScrubSettings.leanEnabled,
                savedScent = RM_LeaningScrubSettings.leanScentEnabled;
            Pawn animal = null;
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                RM_LeaningScrubSettings.leanEnabled = true;
                RM_LeaningScrubSettings.leanScentEnabled = mode != "off";
                animal = Fresh(kind);
                GenSpawn.Spawn(animal, at, map);
                string alone = FleeJobFor(animal)?.def.defName ?? "none";
                if (alone != "none") return "UNMEASURED: the animal flees with nobody near (" + alone + ") kind=" + kind.defName;
                IntVec3 upAt = Offset(at, dir, -ScentStep);
                float upDist = (upAt - at).LengthHorizontal;
                if (upDist > range) return "UNMEASURED: the rounded upwind probe sits " + upDist + " cells out, beyond leanScentRange " + range;
                // Flee destinations are a random search: the upwind probe gets three tries (any flee counts); every
                // negative probe must show the animal COULD have fled, else its "no flee" proves nothing.
                string up = "none";
                bool fledUp = false, canUp = true;
                for (int tries = 0; tries < 3 && !fledUp; tries++)
                {
                    up = Probe(animal, upAt, map, personKind, out fledUp, out bool can);
                    canUp &= can;
                }
                string down = Probe(animal, Offset(at, dir, ScentStep), map, personKind, out bool fledDown, out bool canDown);
                string far = Probe(animal, Offset(at, dir, -(range + 4f)), map, personKind, out bool fledFar, out bool canFar);
                string st = string.Format("kind={0} heading={1:F1} range={2} upwind={3} downwind={4} beyond={5}",
                    kind.defName, lean.HeadingDegrees, range, up, down, far);
                if (up.StartsWith("cell")) return "UNMEASURED: the upwind probe cell was not standable " + st;
                if (mode == "off")
                {
                    if (!fledUp && !canUp) return "UNMEASURED: off arm, the animal has nowhere to flee to " + st;
                    return fledUp ? "FAIL: leanScentEnabled off but the animal fled an upwind person " + st : "PASS off " + st;
                }
                if (up.StartsWith("cell") || down.StartsWith("cell") || far.StartsWith("cell"))
                    return "UNMEASURED: a probe cell was not standable " + st;
                if (!fledUp && !canUp) return "UNMEASURED: the animal has nowhere to flee to " + st;
                if (!fledUp) return "FAIL: no flee from a person " + ScentStep + " cells upwind " + st;
                if (fledDown) return "FAIL: fled a person downwind (it can never smell them) " + st;
                if (fledFar) return "FAIL: fled a person upwind beyond leanScentRange " + st;
                if (!canDown || !canFar) return "UNMEASURED: a negative probe had nowhere to flee to " + st;
                return "PASS " + st;
            }
            finally
            {
                Dispose(animal);
                RM_LeaningScrubSettings.modEnabled = savedMod;
                RM_LeaningScrubSettings.leanEnabled = savedLean;
                RM_LeaningScrubSettings.leanScentEnabled = savedScent;
            }
        }

        // ── fire ─────────────────────────────────────────────────────────────────────────────────────────────────
        // GPT review 2026-11-02: the proof destroys only what it made (fires in its own cleared bed, sparks born of its
        // own TrySpread calls), counts only IMMEDIATE ignitions of the eight neighbours (vanilla's far branch launches a
        // Spark that lands later; the lean branch never does, so far ignitions would compare unlike outcomes), runs on
        // a uniformly ignitable bed (grass on all nine cells, nothing else), and answers UNMEASURED when the sample
        // cannot resolve the promised lift.
        private static readonly MethodInfo TrySpread = AccessTools.Method(typeof(Fire), "TrySpread");

        private static void ClearBedFires(Map map, IntVec3 at)
        {
            List<Thing> doomed = new List<Thing>();
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(at, FireBed, true))
            {
                if (!cell.InBounds(map)) continue;
                foreach (Thing t in cell.GetThingList(map))
                    if (t is Fire) doomed.Add(t);
            }
            foreach (Thing t in doomed) if (!t.Destroyed) t.Destroy();
        }

        private static HashSet<Thing> Sparks(Map map)
        {
            return new HashSet<Thing>(map.listerThings.ThingsOfDef(ThingDefOf.Spark));
        }

        // One arm: (downwind neighbour ignitions, all neighbour ignitions, trials that lit no neighbour).
        private static void Arm(Map map, IntVec3 at, Vector2 dir, bool leanOn, out int down, out int hits, out int misses)
        {
            down = hits = misses = 0;
            RM_LeaningScrubSettings.leanFireEnabled = leanOn;
            for (int i = 0; i < FireTrials; i++)
            {
                ClearBedFires(map, at);
                HashSet<Thing> before = Sparks(map);
                Fire f = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
                f.fireSize = 1f;
                GenSpawn.Spawn(f, at, map);
                TrySpread.Invoke(f, null);
                bool any = false;
                for (int k = 0; k < 8; k++)
                {
                    IntVec3 c = new IntVec3(at.x + RM_LeanKernel.NeighbourDx[k], 0, at.z + RM_LeanKernel.NeighbourDz[k]);
                    if (c.GetFirstThing<Fire>(map) == null) continue;
                    any = true;
                    hits++;
                    if (RM_LeanKernel.Alignment(RM_LeanKernel.NeighbourDx[k], RM_LeanKernel.NeighbourDz[k], dir.x, dir.y)
                        > RM_LeanKernel.FireAlignment) down++;
                }
                if (!any) misses++;
                foreach (Thing t in Sparks(map)) if (!before.Contains(t) && !t.Destroyed) t.Destroy();
            }
            ClearBedFires(map, at);
        }

        public static string ProofFire(string args)
        {
            if (!ParseAt(args, out string mode, out IntVec3 at)) return "UNMEASURED: args must be on@x,z or off@x,z, got " + args;
            Map map = Find.CurrentMap;
            string why = LeanOrWhy(map, out RM_MapComponent_Lean lean);
            if (why != null) return why;
            if (TrySpread == null) return "FAIL: Fire.TrySpread not found (the lean-fire rule cannot be armed either)";
            foreach (IntVec3 c in GenRadial.RadialCellsAround(at, FireBed, true))
            {
                if (!c.InBounds(map) || !c.Standable(map) || c.Roofed(map) || c.GetThingList(map).Count > 0)
                    return "UNMEASURED: the bed around " + at + " is not open, empty, standable ground (" + c + ")";
            }
            float bias = RM_LeaningScrubSettings.leanFireBias;
            Vector2 dir = lean.Downwind;
            int nDown = RM_LeanKernel.DownwindNeighbours(dir.x, dir.y, new int[8]);
            double p0 = nDown / 8.0;    // vanilla's adjacent branch picks one of the eight neighbours uniformly
            bool savedMod = RM_LeaningScrubSettings.modEnabled, savedLean = RM_LeaningScrubSettings.leanEnabled,
                savedFire = RM_LeaningScrubSettings.leanFireEnabled;
            List<Thing> bed = new List<Thing>();
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                RM_LeaningScrubSettings.leanEnabled = true;
                foreach (IntVec3 c in GenRadial.RadialCellsAround(at, FireBed, true))
                    bed.Add(GenSpawn.Spawn(ThingDefOf.Plant_Grass, c, map));
                Arm(map, at, dir, false, out int offDown, out int offHits, out int offMiss);
                double pOff = offHits > 0 ? (double)offDown / offHits : 0;
                string stOff = string.Format("downwindNeighbours={0} p0={1:F3}; off {2}/{3} downwind ({4:F3}), {5} lit no "
                    + "neighbour", nDown, p0, offDown, offHits, pOff, offMiss);
                if (offHits < 30) return "UNMEASURED: too few spreads to measure (" + stOff + ")";
                double seOff = Math.Sqrt(p0 * (1 - p0) / offHits);
                if (Math.Abs(pOff - p0) > 4 * seOff + 1e-9) return "UNMEASURED: vanilla spread is not uniform over the bed " + stOff;
                if (mode == "off") return "PASS off " + stOff;
                if (bias <= 0f || nDown == 0) return "UNMEASURED: leanFireBias " + bias + " / " + nDown + " downwind neighbours promise nothing " + stOff;
                Arm(map, at, dir, true, out int onDown, out int onHits, out int onMiss);
                if (onHits < 30) return "UNMEASURED: too few spreads with the lean on " + onHits + " " + stOff;
                // Lower bound of the lean-on downwind share among neighbour ignitions: the bias branch always picks a
                // downwind neighbour; the rest is vanilla (its far branch only shrinks the vanilla part, raising the share).
                double pExp = bias + (1 - bias) * p0;
                double seExp = Math.Sqrt(pExp * (1 - pExp) / onHits + p0 * (1 - p0) / offHits);
                if (seExp > 0 && (pExp - p0) / seExp < 4.0)
                    return string.Format("UNMEASURED: {0} + {1} ignitions cannot resolve a lift of {2:F3} (expected z {3:F2}) {4}",
                        onHits, offHits, pExp - p0, (pExp - p0) / seExp, stOff);
                double pOn = (double)onDown / onHits;
                double se = Math.Sqrt(pOn * (1 - pOn) / onHits + pOff * (1 - pOff) / offHits);
                double z = se > 0 ? (pOn - pOff) / se : 0;
                double floor = pOff + 0.5 * (pExp - p0);
                string st = string.Format("heading={0:F1} bias={1} on {2}/{3} downwind ({4:F3}), {5} lit no neighbour; "
                    + "expected>={6:F3}; {7}; floor={8:F3} z={9:F2}", lean.HeadingDegrees, bias, onDown, onHits, pOn,
                    onMiss, pExp, stOff, floor, z);
                if (pOn < floor || z < 3.0) return "FAIL: fire does not favour downwind cells " + st;
                return "PASS " + st;
            }
            finally
            {
                ClearBedFires(map, at);
                foreach (Thing g in bed) if (g != null && !g.Destroyed) g.Destroy();
                RM_LeaningScrubSettings.modEnabled = savedMod;
                RM_LeaningScrubSettings.leanEnabled = savedLean;
                RM_LeaningScrubSettings.leanFireEnabled = savedFire;
            }
        }
    }
}
