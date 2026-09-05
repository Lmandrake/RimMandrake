using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StructureInjections
{
    // Replays a rimplace BuildPlan (compiled to the flat text format by
    // rimplace.plan.compile_flat, src/RimMandrake/Utils/rimplace/plan.py) onto
    // a freshly generated map. This is the mapgen-time twin of rimplace's LIVE
    // path (rimplace.plan.compile_calls -> jawa/set_terrain_batch / build_batch
    // / set_roof_batch over the bridge) -- same plan, same ordering, different
    // executor: direct engine calls instead of bridge round-trips, because
    // there is no running client to call back into during mapgen.
    //
    // Order mirrors compile_calls() exactly, because that order is not a
    // style choice -- it is what the live path proved necessary:
    //   foundation -> terrain -> things (transmitters before connectors,
    //   or a power network spawns dead) -> roof.
    // Paint and floor colour are best-effort and NOT part of the ordering
    // proof this class exists to make; see the TODO below.
    public class GenStep_RimplacePlan : GenStep
    {
        // Path to the compiled .txt plan, relative to THIS DEF'S owning mod's
        // root folder, e.g. "Templates/moisture_farm.txt". Ordinary XML-to-
        // field binding on the GenStepDef -- confirmed against
        // GenStep_ScatterThings' filthDef/filthExpandBy/filthChance pattern.
        public string planFile;

        // Where the plan's own (x,z) origin lands on the real map. Plans are
        // authored at small, arbitrary offline coordinates (rimplace's own
        // render defaults to rect "0,0,w,h"), so by default this GenStep
        // centers the plan's footprint on the map. Set false and supply
        // offsetX/offsetZ for placement logic driven by the caller instead
        // (e.g. a landmark-specific rect).
        public bool centerOnMap = true;
        public int offsetX;
        public int offsetZ;

        public override int SeedPart => 8462013; // arbitrary, stable, distinct from vanilla gensteps

        public override void Generate(Map map, GenStepParams parms)
        {
            if (string.IsNullOrEmpty(planFile))
            {
                Log.Error("[RimMandrake.StructureInjections] GenStep_RimplacePlan on " +
                          def.defName + " has no planFile.");
                return;
            }

            var modRoot = def.modContentPack?.RootDir;
            if (string.IsNullOrEmpty(modRoot))
            {
                Log.Error("[RimMandrake.StructureInjections] GenStepDef " + def.defName +
                          " has no owning modContentPack; cannot resolve planFile.");
                return;
            }
            var path = Path.Combine(modRoot, planFile);
            if (!File.Exists(path))
            {
                Log.Error("[RimMandrake.StructureInjections] plan file not found: " + path);
                return;
            }

            RimplacePlan plan;
            try
            {
                plan = RimplacePlan.Parse(path);
            }
            catch (System.Exception ex)
            {
                Log.Error("[RimMandrake.StructureInjections] failed to parse " + path +
                          ": " + ex);
                return;
            }

            int dx = offsetX, dz = offsetZ;
            if (centerOnMap && plan.HasFootprint)
            {
                var mapCenter = map.Center;
                var planCenterX = plan.FootprintX + plan.FootprintW / 2;
                var planCenterZ = plan.FootprintZ + plan.FootprintH / 2;
                dx = mapCenter.x - planCenterX + offsetX;
                dz = mapCenter.z - planCenterZ + offsetZ;
            }

            ApplyPlan(map, plan, dx, dz, planFile ?? "(debug)");
        }

        // Shared by Generate() (production path, driven off a GenStepDef's
        // planFile field) and the debug action (StructureInjectionsDebugActions,
        // which parses a plan itself and calls straight in) so both exercise
        // the identical ordering logic -- there is exactly one implementation
        // of "what does replaying a plan mean", proven live from either entry
        // point.
        public static void ApplyPlan(Map map, RimplacePlan plan, int dx, int dz, string sourceLabel)
        {
            // E6: an unknown directive is now VISIBLE, not a silent no-op -
            // "the failure must be visible in Player.log, not on the map."
            // One line per distinct unknown verb, not per line, so an old v1
            // plan replayed here (no CLEAR/RUN/PAWN at all) says nothing, and
            // a genuinely corrupt/future plan says so exactly once per verb.
            foreach (var kv in plan.UnknownDirectives)
                Log.Warning("[RimMandrake.StructureInjections] plan " + sourceLabel +
                            " has " + kv.Value + " '" + kv.Key +
                            "' directive line(s) this DLL does not recognise - skipped.");

            // 0. E1 CLEAR -- owner ruling 2026-09-05 (TILE_STRUCTURE_
            // REVIEW_SAVE_1) plus RIMPLACE_ENGINE_DELTAS_1 E1's full form:
            // every plan built via rimplace.luaenv.run_template carries two
            // CLEAR directives ahead of everything else (footprint+1 buffer
            // soft, then the exact footprint at "all"), so this reads what
            // the PLAN says to clear rather than hardcoding one rect/mode
            // here - a template's own `ctx:clear()` blob clears land in the
            // same list, in the same "before anything" position.
            foreach (var c in plan.Clears)
                ExecuteClear(map, c, dx, dz);

            // 1. foundation (Odyssey substructure) -- must exist before terrain
            foreach (var c in plan.Foundation)
                SetTerrainCell(map, c, dx, dz, foundation: true);

            // 2. terrain -- floors under things
            foreach (var c in plan.Terrain)
                SetTerrainCell(map, c, dx, dz, foundation: false);

            // 3. things, transmitters first: a connector (cooler, most
            // machines) binds to the nearest transmitter within
            // ConnectMaxDist AT SPAWN; a transmitter appearing afterwards
            // does not retroactively claim it (same trap compile_calls'
            // comment documents for the live path).
            var byPriority = plan.Things
                .Select(t => new { t, def2 = DefDatabase<ThingDef>.GetNamedSilentFail(t.DefName) })
                .Where(x =>
                {
                    if (x.def2 == null)
                    {
                        Log.Error("[RimMandrake.StructureInjections] no ThingDef '" +
                                  x.t.DefName + "' (plan " + sourceLabel + ")");
                        return false;
                    }
                    return true;
                })
                .OrderByDescending(x => x.def2.EverTransmitsPower);

            foreach (var x in byPriority)
                SpawnThing(map, x.t, x.def2, dx, dz);

            // 3b. E2 RUN -- after ordinary things (a run's line should not be
            // overwritten by furniture placed inside its own footprint),
            // before roof (an outdoor conduit bus is not roofed).
            foreach (var r in plan.Runs)
                ExecuteRun(map, r, dx, dz, sourceLabel);

            // 4. roof -- last: a roof over a wall that does not exist yet is
            // an unsupported span (WALLS CREATE NO ROOF is the live path's
            // own warning, and the ordering constraint is identical here).
            foreach (var c in plan.Roof)
                SetRoofCell(map, c, dx, dz);

            // TODO(paint/floor colour): the live path applies these AFTER
            // things exist via jawa/paint_building and jawa/set_terrain_layer
            // (CompColorable + a PaintColorDef -> Color lookup). Not
            // implemented here yet -- no roster row's promise depends on it
            // for v1, and it does not touch the ordering this class exists
            // to prove. Left as a known gap, not silently dropped.

            // 5. E3 PAWN -- absolute last: a spawned pawn or corpse must not
            // sit under anything a later step in THIS list could still wipe
            // (WipeMode.Vanish on a THING cell, a CLEAR that ran earlier).
            foreach (var p in plan.Pawns)
                ExecutePawn(map, p, dx, dz, sourceLabel);
        }

        // RIMPLACE_ENGINE_DELTAS_1 E1. mode="soft": destroys plants, filth,
        // chunks and loose items (Plant/Filth/Item categories) in the rect.
        // mode="all": soft, PLUS every mineable natural rock Building in the
        // rect, replacing the cell's terrain with that rock ThingDef's OWN
        // rough-rock terrain (building.leaveTerrain, falling back to
        // naturalTerrain) -- looked up per rock type at runtime, never
        // hardcoded. This mirrors exactly what Verse.Building.DeSpawn already
        // does on a live map (`def.building.leaveTerrain != null &&
        // Current.ProgramState == ProgramState.Playing`) -- confirmed by
        // reading Building.cs: that automatic terrain swap is GATED on
        // ProgramState.Playing, which mapgen time is NOT (it is
        // MapInitializing), so destroying a rock Mineable here would
        // otherwise leave bare rough-hewn-nothing where the mountain grid's
        // own terrain-under-the-rock happens not to already match. Reading
        // the ThingDef's own field is what "not hardcoded" means here: no
        // rock-name-to-terrain-name table exists or is guessed anywhere in
        // this method.
        private static void ExecuteClear(Map map, PlanClear c, int dx, int dz)
        {
            var rect = new CellRect(c.X + dx, c.Z + dz, c.W, c.H);
            bool all = c.Mode == "all";
            foreach (var cell in rect)
            {
                if (!cell.InBounds(map)) continue;
                foreach (var t in map.thingGrid.ThingsListAtFast(cell).ToList())
                {
                    if (t.def.category == ThingCategory.Plant ||
                        t.def.category == ThingCategory.Filth ||
                        t.def.category == ThingCategory.Item)
                    {
                        t.Destroy(DestroyMode.Vanish);
                        continue;
                    }
                    if (all && t.def.mineable && t.def.building != null)
                    {
                        var replacement = t.def.building.leaveTerrain ?? t.def.building.naturalTerrain;
                        t.Destroy(DestroyMode.Vanish);
                        if (replacement != null)
                            map.terrainGrid.SetTerrain(cell, replacement);
                        else
                            Log.Warning("[RimMandrake.StructureInjections] mined '" + t.def.defName +
                                        "' at " + cell + " but it declares no leaveTerrain/naturalTerrain " +
                                        "- terrain left as-is under it.");
                    }
                }
            }
        }

        // RIMPLACE_ENGINE_DELTAS_1 E2. Walks from (x,z) toward the MAP EDGE in
        // cardinal direction `dir`, placing `defName` on every cell that does
        // not already hold it, stopping at the first cell holding an
        // impassable thing that is NOT itself a conduit-class transmitter (a
        // wire is allowed to run under/through another wire's own cell, but
        // not through a wall). This is engine-side by necessity: a plan is
        // authored at small offline coordinates and the real map edge is only
        // known here.
        private static readonly IntVec3[] RunDirVecs =
        {
            new IntVec3(0, 0, 1),   // N
            new IntVec3(1, 0, 0),   // E
            new IntVec3(0, 0, -1),  // S
            new IntVec3(-1, 0, 0),  // W
        };

        private static void ExecuteRun(Map map, PlanRun r, int dx, int dz, string sourceLabel)
        {
            var def = DefDatabase<ThingDef>.GetNamedSilentFail(r.DefName);
            if (def == null)
            {
                Log.Error("[RimMandrake.StructureInjections] RUN: no ThingDef '" +
                          r.DefName + "' (plan " + sourceLabel + ")");
                return;
            }
            int dirIdx = "NESW".IndexOf(r.Dir, System.StringComparison.Ordinal);
            if (dirIdx < 0)
            {
                Log.Error("[RimMandrake.StructureInjections] RUN: unknown dir '" + r.Dir +
                          "' (plan " + sourceLabel + ")");
                return;
            }
            var step = RunDirVecs[dirIdx];
            ThingDef stuffDef = null;
            if (r.Stuff != null)
                stuffDef = DefDatabase<ThingDef>.GetNamedSilentFail(r.Stuff);

            var cell = new IntVec3(r.X + dx, 0, r.Z + dz);
            int placed = 0;
            while (cell.InBounds(map))
            {
                var here = map.thingGrid.ThingsListAtFast(cell);
                bool alreadyThis = false;
                bool blocked = false;
                foreach (var t in here)
                {
                    if (t.def == def) { alreadyThis = true; continue; }
                    // A conduit-class transmitter (the thing this RUN is
                    // itself extending, or any other transmitter) never
                    // blocks a run - two wires may share a cell. Anything
                    // else impassable stops the line.
                    if (t.def.passability == Traversability.Impassable && !t.def.EverTransmitsPower)
                        blocked = true;
                }
                if (blocked) break;
                if (!alreadyThis)
                {
                    var thing = ThingMaker.MakeThing(def, def.MadeFromStuff ? stuffDef : null);
                    GenSpawn.Spawn(thing, cell, map, WipeMode.Vanish);
                    placed++;
                }
                cell += step;
            }
            if (placed == 0)
                Log.Warning("[RimMandrake.StructureInjections] RUN of '" + r.DefName +
                            "' from (" + r.X + "," + r.Z + ") " + r.Dir +
                            " placed nothing (blocked immediately, or already all " + r.DefName +
                            ") (plan " + sourceLabel + ")");
        }

        // RIMPLACE_ENGINE_DELTAS_1 E3. Spawns a live pawn (state="alive"), or
        // kills it immediately to produce its Corpse (state="dead"), pushed
        // further into CompRottable's Dessicated stage for "dessicated"/
        // "skeleton" - RimWorld's own RotStage enum has nothing past
        // Dessicated, so "skeleton" reads as the fully-decayed terminal stage,
        // not a distinct mechanical state (see CompRottable.cs: Fresh ->
        // Rotting -> Dessicated only). faction="wild" spawns with no Faction
        // (a feral beast); a FactionDef name resolves to a live Faction
        // instance of that def if one exists in this game, else a Warning and
        // no Faction; "player" is refused UPSTREAM (rimplace.luaenv.Ctx.pawn)
        // and is defended again here in case a hand-edited plan ever carries
        // one - a mapgen template must never spawn a colonist.
        private static void ExecutePawn(Map map, PlanPawn p, int dx, int dz, string sourceLabel)
        {
            if (p.Faction == "player")
            {
                Log.Error("[RimMandrake.StructureInjections] PAWN: refusing faction=player " +
                          "for '" + p.KindDef + "' (plan " + sourceLabel + ") - a mapgen " +
                          "template must never spawn a colonist.");
                return;
            }
            var kindDef = DefDatabase<PawnKindDef>.GetNamedSilentFail(p.KindDef);
            if (kindDef == null)
            {
                Log.Error("[RimMandrake.StructureInjections] PAWN: no PawnKindDef '" +
                          p.KindDef + "' (plan " + sourceLabel + ")");
                return;
            }
            Faction faction = null;
            if (p.Faction != "wild" && !string.IsNullOrEmpty(p.Faction))
            {
                var factionDef = DefDatabase<FactionDef>.GetNamedSilentFail(p.Faction);
                faction = factionDef != null ? Find.FactionManager.FirstFactionOfDef(factionDef) : null;
                if (faction == null)
                    Log.Warning("[RimMandrake.StructureInjections] PAWN: no live Faction of def '" +
                                p.Faction + "' - spawning '" + p.KindDef + "' with no faction " +
                                "(plan " + sourceLabel + ")");
            }

            var cell = new IntVec3(p.X + dx, 0, p.Z + dz);
            if (!cell.InBounds(map)) { LogOOB(cell, p.KindDef); return; }

            var request = new PawnGenerationRequest(kindDef, faction,
                PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true);
            Pawn pawn;
            try
            {
                pawn = PawnGenerator.GeneratePawn(request);
            }
            catch (System.Exception ex)
            {
                Log.Error("[RimMandrake.StructureInjections] PAWN: GeneratePawn('" + p.KindDef +
                          "') failed (plan " + sourceLabel + "): " + ex);
                return;
            }
            GenSpawn.Spawn(pawn, cell, map, WipeMode.Vanish);

            if (p.State == "alive") return;

            pawn.Kill(null);
            var corpse = pawn.Corpse;
            if (corpse == null)
            {
                Log.Warning("[RimMandrake.StructureInjections] PAWN: '" + p.KindDef +
                            "' state=" + p.State + " but Kill() produced no Corpse " +
                            "(plan " + sourceLabel + ") - left as a fresh kill.");
                return;
            }
            if (p.State == "dessicated" || p.State == "skeleton")
            {
                var rot = corpse.GetComp<CompRottable>();
                rot?.RotImmediately(RotStage.Dessicated);
            }
        }

        private static void SetTerrainCell(Map map, PlanCell c, int dx, int dz, bool foundation)
        {
            var cell = new IntVec3(c.X + dx, 0, c.Z + dz);
            if (!cell.InBounds(map)) { LogOOB(cell, c.DefName); return; }
            var td = DefDatabase<TerrainDef>.GetNamedSilentFail(c.DefName);
            if (td == null)
            {
                Log.Error("[RimMandrake.StructureInjections] no TerrainDef '" + c.DefName + "'");
                return;
            }
            if (foundation)
                map.terrainGrid.SetFoundation(cell, td);
            else
                map.terrainGrid.SetTerrain(cell, td);
        }

        private static void SetRoofCell(Map map, PlanCell c, int dx, int dz)
        {
            var cell = new IntVec3(c.X + dx, 0, c.Z + dz);
            if (!cell.InBounds(map)) { LogOOB(cell, c.DefName); return; }
            var rd = DefDatabase<RoofDef>.GetNamedSilentFail(c.DefName);
            if (rd == null)
            {
                Log.Error("[RimMandrake.StructureInjections] no RoofDef '" + c.DefName + "'");
                return;
            }
            map.roofGrid.SetRoof(cell, rd);
        }

        private static void SpawnThing(Map map, PlanThing t, ThingDef td, int dx, int dz)
        {
            var cell = new IntVec3(t.X + dx, 0, t.Z + dz);
            if (!cell.InBounds(map)) { LogOOB(cell, t.DefName); return; }

            ThingDef stuffDef = null;
            if (t.Stuff != null)
            {
                stuffDef = DefDatabase<ThingDef>.GetNamedSilentFail(t.Stuff);
                if (stuffDef == null)
                    Log.Error("[RimMandrake.StructureInjections] no stuff ThingDef '" +
                              t.Stuff + "' for " + t.DefName + " -- spawning unstuffed.");
            }

            var thing = ThingMaker.MakeThing(td, td.MadeFromStuff ? stuffDef : null);
            var rot = new Rot4(t.Rot);
            GenSpawn.Spawn(thing, cell, map, rot, WipeMode.Vanish);
        }

        private static void LogOOB(IntVec3 cell, string defName)
        {
            Log.Warning("[RimMandrake.StructureInjections] " + defName +
                        " at " + cell + " is outside the generated map; skipped.");
        }
    }
}
