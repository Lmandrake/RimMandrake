#if RM_PROOFS
using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>sc_storeroom_bomb_pit, the showcase (design/concepts/ExplosiveKnockback/scenes.json; owner 2026-11-12: "Just put a
    /// bomb into a storeroom with people in it beside a pit. Shows some items falling into the pit and some people as well."),
    /// RIMMANDRAKE_WRITE_STOREROOM_BOMB_PIT_SCENE_TABLE_NAMED_FIRST. NOT YET RUN LIVE.
    /// Offsets from the impact cell o: a walled 7x7 interior (walls x=+-4 for z -3..4, z=+4 across), open to the south onto
    /// a superdeep pit x -3..3, z -5..-4 (near row z -4) with one covered cell in the near row. A Shelf at (1,2) and a ShelfSmall
    /// at (-2,2) holding mixed goods; LWM's weapons locker at (-2,0) with a free cell (-3,0) behind it; 75 steel at (1,1) on the
    /// ray to colonist p4 at (3,3), outside the 2.9 blast; colonists pE (1,0), pS (0,-1), pW (-2,-2); loose floor stacks, one
    /// whose kernel plan ends in the open pit and one whose plan ends exactly on the covered cell (both chosen at Stage by the
    /// kernel's own Resolve on the built room, so a kernel change re-picks them instead of breaking the scene).
    /// The thing trace (every tick, 900 ticks): each good's spawned cell, carrier height and spin; a good spawned on two cells
    /// on consecutive ticks is a despawn-spawn pair; a good coming to rest on a superdeep cell is its descent (the FlowWorks
    /// descent journal carries pawns only). _control: the same room, the pit filled in and the cover removed after planning.
    /// One shell = Blast(o, 2.9) like every scene since calibration (harms at 1, pushes at the type's reference damage).</summary>
    public static partial class RM_KnockbackProof
    {
        private static readonly AccessTools.FieldRef<RM_ThingFlyer_Knockback, float> CarrierHeight =
            AccessTools.FieldRefAccess<RM_ThingFlyer_Knockback, float>("height");
        private static readonly AccessTools.FieldRef<RM_ThingFlyer_Knockback, float> CarrierSpin =
            AccessTools.FieldRefAccess<RM_ThingFlyer_Knockback, float>("spinRate");

        private static readonly string[] RoomColonists = { "pE", "pS", "pW", "p4" };

        /// <summary>Where the kernel throws a loose stack of `mass` kg from `from` (blast at s.o, radius 2.9), on the map as built
        /// now; Invalid when it is not thrown. Mirrors WantCells and the request's Resolve call.</summary>
        private static IntVec3 PlanGood(Scene s, IntVec3 from, float mass)
        {
            KbSettings k = RimMandrakeExplosiveKnockbackSettings.Kernel();
            if (mass > k.lightMassLimit)
            {
                return IntVec3.Invalid;
            }
            int cells = RM_KnockbackMath.WildCells((from - s.o).LengthHorizontal, 2.9f, 1f, mass, k, RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild);
            if (cells <= 0)
            {
                return IntVec3.Invalid;
            }
            KbResult r = RM_KnockbackMath.Resolve(new RM_MapKbGrid(Map, null, false), from.x, from.z, from.x - s.o.x, from.z - s.o.z,
                cells, KbKind.Item, mass, k);
            return r.cellsTravelled > 0 ? new IntVec3(r.destX, 0, r.destZ) : IntVec3.Invalid;
        }

        private static float DefMass(string def, int n) => DefDatabase<ThingDef>.GetNamed(def).GetStatValueAbstract(StatDefOf.Mass) * n;

        private static bool OpenPitCell(IntVec3 c) => RM_KnockbackCompat.IsSuperdeep(Map, c) && RM_KnockbackCompat.CoverAt(Map, c) == null;

        private static IEnumerable<string> GoodKeys(Scene s) => s.things.Keys.Where(k => k.StartsWith("g_")).ToList();

        private static string StoreroomBombPit(Scene s)
        {
            bool control = s.name == "storeroom_bomb_pit_control";
            if (!RM_KnockbackCompat.FlowWorks)
            {
                return "FlowWorks not loaded";
            }
            const string lockerDef = "LWM_WeaponsLocker";
            if (DefDatabase<ThingDef>.GetNamedSilentFail(lockerDef) == null)
            {
                return lockerDef + " not loaded: add LWM's Deep Storage (lwm.deepstorage) to the list";
            }
            foreach (string d in new[] { "Shelf", "ShelfSmall", "RM_PitCover_WovenScrap" })
            {
                if (DefDatabase<ThingDef>.GetNamedSilentFail(d) == null)
                {
                    return d + " not loaded";
                }
            }
            // the room: walls, then the pit along the open south side (planning reads both)
            for (int dz = -3; dz <= 4; dz++)
            {
                Build("Wall", O(s, -4, dz), "BlocksGranite");
                Build("Wall", O(s, 4, dz), "BlocksGranite");
            }
            for (int dx = -3; dx <= 3; dx++)
            {
                Build("Wall", O(s, dx, 4), "BlocksGranite");
            }
            if (!Pit(O(s, -3, -5), 7, 2))
            {
                return "could not dig the pit";
            }
            // open shelves of mixed goods two cells north
            var mixed = new[] { ("Cloth", 20), ("MedicineIndustrial", 4), ("Silver", 40), ("ComponentIndustrial", 3), ("Beer", 6), ("Chocolate", 8) };
            int mi = 0;
            var used = new HashSet<IntVec3>();
            foreach ((string def, IntVec3 at) in new[] { ("Shelf", O(s, 1, 2)), ("ShelfSmall", O(s, -2, 2)) })
            {
                Thing shelf = Build(def, at, "WoodLog");
                foreach (IntVec3 c in shelf.OccupiedRect())
                {
                    used.Add(c);
                    for (int j = 0; j < 2; j++, mi++)
                    {
                        string key = "g_shelf" + mi;
                        Thing g = Item(s, key, mixed[mi % mixed.Length].Item1, mixed[mi % mixed.Length].Item2, c);
                        if (!g.Spawned || g.Position != c)
                        {
                            return def + " cell " + c.x + "," + c.z + " did not take " + key + " (" + g.def.defName + ")";
                        }
                        if (RM_MapComponent_Knockback.InClosedContainer(g, Map))
                        {
                            return def + " classed closed by the guard (a shelf draws its contents: must be open)";
                        }
                    }
                }
            }
            // the closed locker two cells west, a free cell behind it
            Thing box = Build(lockerDef, O(s, -2, 0));
            Track(s, "box", box);
            Item(s, "lk_pistol", "Gun_Autopistol", 1, box.Position);
            Item(s, "lk_revolver", "Gun_Revolver", 1, box.Position);
            foreach (string k in new[] { "lk_pistol", "lk_revolver" })
            {
                if (s.things[k].Position != box.Position)
                {
                    return lockerDef + " did not take " + k;
                }
                s.numbers[k + "Hp"] = Hp(s.things[k]);
            }
            if (!RM_KnockbackCompat.IsClosedContainer(box))
            {
                return lockerDef + " is not classed closed by the guard";
            }
            s.numbers["boxMass"] = Mass(box);
            if (s.numbers["boxMass"] > RimMandrakeExplosiveKnockbackSettings.closedContainerMassLimit)
            {
                return lockerDef + " with its weapons weighs " + s.numbers["boxMass"].ToString("0.#") + " kg, over closedContainerMassLimit";
            }
            used.Add(box.Position);
            used.Add(O(s, -3, 0));   // the free cell behind the locker
            // the heavy steel, on the ray to p4 two cells beyond it
            Thing steel = Item(s, "g_steel", "Steel", 75, O(s, 1, 1));
            s.numbers["steelMass"] = steel.GetStatValue(StatDefOf.Mass) * steel.stackCount;
            if (s.numbers["steelMass"] < RimMandrakeExplosiveKnockbackSettings.heavyGoodsMinMass)
            {
                return "the steel stack weighs " + s.numbers["steelMass"].ToString("0.#") + " kg, under heavyGoodsMinMass";
            }
            if (WantCells(s, "g_steel", 2.9f) < 2)
            {
                return "the steel throw is too short to reach p4 two cells beyond it: " + WantCells(s, "g_steel", 2.9f) + " cells";
            }
            used.Add(steel.Position);
            // the colonists, drafted (a careless walk is what the control rules out)
            Colonist(s, "pE", O(s, 1, 0));
            Colonist(s, "pS", O(s, 0, -1));
            Colonist(s, "pW", O(s, -2, -2));
            Colonist(s, "p4", O(s, 3, 3));
            foreach (string k in RoomColonists)
            {
                used.Add(s.starts[k]);
            }
            used.Add(s.o);
            // loose floor stacks within two cells: two plain ones, one planned into the open pit, one onto the covered cell
            Item(s, "g_floorA", "WoodLog", 8, O(s, -1, 1));
            Item(s, "g_floorB", "Cloth", 10, O(s, 2, -1));
            used.Add(O(s, -1, 1));
            used.Add(O(s, 2, -1));
            IntVec3 sLanding = O(s, 0, -4);   // pS's planned landing, about three cells south
            var cand = new List<IntVec3>();
            for (int dz = -2; dz <= 0; dz++)
            {
                for (int dx = -2; dx <= 2; dx++)
                {
                    IntVec3 c = O(s, dx, dz);
                    if (!used.Contains(c))
                    {
                        cand.Add(c);
                    }
                }
            }
            IntVec3 pitFrom = IntVec3.Invalid, pitTo = IntVec3.Invalid;
            foreach (IntVec3 c in cand)
            {
                IntVec3 to = PlanGood(s, c, DefMass("Cloth", 10));
                if (to.IsValid && to != sLanding && OpenPitCell(to))
                {
                    pitFrom = c;
                    pitTo = to;
                    break;
                }
            }
            if (!pitFrom.IsValid)
            {
                return "no floor cell within two cells whose planned throw ends in the open pit";
            }
            cand.Remove(pitFrom);
            IntVec3 coverFrom = IntVec3.Invalid, coverCell = IntVec3.Invalid;
            int coverCount = 0;
            Thing cover = null;
            // visit 2 (2026-11-15): the cover goes on FIRST. Planned against the open pit, a throw stops on the first pit cell it
            // meets; with the cover built that cell no longer stops it, so a plan made before the cover never matched after it.
            for (int cx = -6; cx <= 6 && !coverFrom.IsValid; cx++)
            {
                IntVec3 cc = new IntVec3(s.o.x + cx, 0, s.o.z - 4);
                if (!cc.InBounds(Map) || cc == sLanding || cc == pitTo || !OpenPitCell(cc))
                {
                    continue;
                }
                cover = Build("RM_PitCover_WovenScrap", cc);
                foreach (IntVec3 c in cand)
                {
                    for (int n = 1; n <= 24 && !coverFrom.IsValid; n++)   // 24 logs = 9.6 kg, under the 10 kg heavy threshold
                    {
                        if (PlanGood(s, c, DefMass("WoodLog", n)) == cc)
                        {
                            coverFrom = c;
                            coverCell = cc;
                            coverCount = n;
                        }
                    }
                    if (coverFrom.IsValid)
                    {
                        break;
                    }
                }
                if (!coverFrom.IsValid)
                {
                    cover.Destroy(DestroyMode.Vanish);
                    cover = null;
                }
            }
            if (!coverFrom.IsValid)
            {
                return "no floor stack within two cells whose planned throw ends on a covered near-row pit cell";
            }
            Item(s, "g_pit", "Cloth", 10, pitFrom);
            Item(s, "g_cover", "WoodLog", coverCount, coverFrom);
            s.numbers["coverX"] = coverCell.x;
            s.numbers["coverZ"] = coverCell.z;
            if (control)
            {
                cover.Destroy(DestroyMode.Vanish);
                foreach (IntVec3 c in new CellRect(s.o.x - 3, s.o.z - 5, 7, 2))
                {
                    RM_KnockbackCompat.FillToSurface(Map, c);
                    if (RM_KnockbackCompat.IsSuperdeep(Map, c))
                    {
                        return "could not fill the pit in at " + c.x + "," + c.z;
                    }
                }
            }
            // the thing trace: every good (and the locker's weapons) from its start, every colonist's flight
            foreach (string k in s.things.Keys)
            {
                s.numbers[k + "_ps"] = 1;
                s.numbers[k + "_px"] = s.starts[k].x;
                s.numbers[k + "_pz"] = s.starts[k].z;
            }
            Map m0 = Map;
            for (int d = 1; d <= 900; d++)
            {
                int dd = d;
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + d, () =>
                {
                    if (m0 != Find.CurrentMap)
                    {
                        return;
                    }
                    s.numbers["traceTicks"] = s.numbers.TryGetValue("traceTicks", out float tt) ? tt + 1 : 1;
                    foreach (string k in s.things.Keys.Where(k => k.StartsWith("g_") || k.StartsWith("lk_")).ToList())
                    {
                        TraceGood(s, k, m0);
                    }
                    foreach (string k in RoomColonists)
                    {
                        Pawn p = (Pawn)s.things[k];
                        if (!p.Spawned && p.ParentHolder is PawnFlyer)
                        {
                            s.numbers[k + "_air"] = 1;
                        }
                        else if (p.Spawned && s.numbers.ContainsKey(k + "_air") && !s.numbers.ContainsKey(k + "_landTick"))
                        {
                            s.numbers[k + "_landTick"] = dd;
                        }
                        if (s.numbers.TryGetValue(k + "_landTick", out float lt) && dd - lt <= 2 && p.stances?.stunner != null && p.stances.stunner.Stunned)
                        {
                            s.numbers[k + "_stunned"] = 1;
                        }
                    }
                }));
            }
            Blast(s.o, 2.9f);
            s.verdict = StoreroomBombPitVerdict;
            return null;
        }

        /// <summary>One tick of the thing trace for s.things[k]: a despawn-spawn pair (spawned on another cell the very next tick,
        /// no carrier between), a descent (comes to rest on a superdeep cell from anywhere else), the carrier's height and spin.</summary>
        private static void TraceGood(Scene s, string k, Map m)
        {
            Thing t = s.things[k];
            bool wasSpawned = s.numbers[k + "_ps"] > 0;
            if (t.Spawned)
            {
                IntVec3 c = t.Position;
                bool deep = RM_KnockbackCompat.IsSuperdeep(m, c);
                if (wasSpawned && (c.x != (int)s.numbers[k + "_px"] || c.z != (int)s.numbers[k + "_pz"]))
                {
                    s.numbers[k + "_tele"] = s.numbers.TryGetValue(k + "_tele", out float n) ? n + 1 : 1;
                }
                bool wasDeep = wasSpawned && RM_KnockbackCompat.IsSuperdeep(m, new IntVec3((int)s.numbers[k + "_px"], 0, (int)s.numbers[k + "_pz"]));
                if (deep && !wasDeep)
                {
                    s.numbers[k + "_desc"] = s.numbers.TryGetValue(k + "_desc", out float n) ? n + 1 : 1;
                }
                s.numbers[k + "_ps"] = 1;
                s.numbers[k + "_px"] = c.x;
                s.numbers[k + "_pz"] = c.z;
                return;
            }
            s.numbers[k + "_ps"] = 0;
            RM_ThingFlyer_Knockback f = CarrierOf(m, t);
            if (f == null || !f.Spawned)
            {
                return;
            }
            UnityEngine.Vector3 _ = f.DrawPos;   // recomputes the arc for this tick
            float h = CarrierHeight(f);
            s.numbers[k + "_air"] = 1;
            s.numbers[k + "_maxH"] = Math.Max(s.numbers.TryGetValue(k + "_maxH", out float mh) ? mh : 0f, h);
            if (CarrierSpin(f) != 0f)
            {
                s.numbers[k + "_spin"] = 1;
            }
        }

        private static string StoreroomBombPitVerdict(Scene sc)
        {
            bool control = sc.name == "storeroom_bomb_pit_control";
            Map map = Map;
            var cover = new IntVec3((int)sc.numbers["coverX"], 0, (int)sc.numbers["coverZ"]);
            var goods = GoodKeys(sc).ToList();
            // ── start assertions read from the trace: INVALID, never FAIL ──
            if (!sc.numbers.ContainsKey("traceTicks"))
            {
                return "INVALID " + sc.name + " the thing trace never ran (no tick stepped)";
            }
            foreach (Thing f in map.listerThings.ThingsOfDef(RM_KnockbackDefOf.RM_ThingFlyer_Knockback))
            {
                if (f is RM_ThingFlyer_Knockback k && k.Inner != null && sc.things.Values.Contains(k.Inner))
                {
                    return "INVALID " + sc.name + " not at rest: " + k.Inner.def.defName + " still flying after " + sc.numbers["traceTicks"] + " ticks";
                }
            }
            foreach (string k in RoomColonists)
            {
                if (!sc.things[k].Spawned && sc.things[k].ParentHolder is PawnFlyer)
                {
                    return "INVALID " + sc.name + " not at rest: " + k + " still flying";
                }
            }
            Pawn p4 = (Pawn)sc.things["p4"];
            if (ForThing(sc, "request", p4).Count > 0 || ForThing(sc, "launch", p4).Count > 0)
            {
                return "INVALID " + sc.name + " p4 was reached by the blast (it must stand outside it)";
            }
            var plannedTo = new Dictionary<string, IntVec3>();
            foreach (string k in RoomColonists.Take(3))
            {
                var l = ForThing(sc, "launch", sc.things[k]);
                if (l.Count == 1)
                {
                    plannedTo[k] = (IntVec3)l[0]["to"];
                    IntVec3 from = (IntVec3)l[0]["from"];
                    foreach ((int x, int z) in RM_KnockbackMath.Line(from.x, from.z, from.x - sc.o.x, from.z - sc.o.z, Convert.ToInt32(l[0]["planned"])))
                    {
                        foreach (string o in RoomColonists.Where(o => o != k))
                        {
                            if (sc.starts[o].x == x && sc.starts[o].z == z)
                            {
                                return "INVALID " + sc.name + " " + k + "'s planned path crosses " + o + "'s cell " + x + "," + z;
                            }
                        }
                    }
                }
            }
            foreach (string k in goods)
            {
                var mv = ForThing(sc, "item_move", sc.things[k]);
                if (mv.Count > 0)
                {
                    plannedTo[k] = (IntVec3)mv[0]["to"];
                }
            }
            if (!plannedTo.ContainsKey("pS"))
            {
                return "INVALID " + sc.name + " no launch line for pS";
            }
            if (!plannedTo.TryGetValue("g_cover", out IntVec3 coverTo) || coverTo != cover)
            {
                return "INVALID " + sc.name + " the covered-cell stack was not planned onto " + cover.x + "," + cover.z
                    + (plannedTo.ContainsKey("g_cover") ? " (planned " + coverTo.x + "," + coverTo.z + ")" : " (no item_move)");
            }
            if (!control)
            {
                bool pawnToPit = RoomColonists.Take(3).Any(k => plannedTo.TryGetValue(k, out IntVec3 c) && c != cover && RM_KnockbackCompat.IsSuperdeep(map, c));
                bool goodToPit = goods.Any(k => k != "g_cover" && plannedTo.TryGetValue(k, out IntVec3 c) && c != cover && RM_KnockbackCompat.IsSuperdeep(map, c));
                if (!pawnToPit || !goodToPit)
                {
                    return "INVALID " + sc.name + " the trace's planned cells put no " + (!pawnToPit ? "colonist" : "loose good") + " in the open pit";
                }
            }
            var pawnDesc = RoomColonists.ToDictionary(k => k, k => ForThing(sc, "descent", sc.things[k]).Count);
            int Desc(string k) => sc.numbers.TryGetValue(k + "_desc", out float n) ? (int)n : 0;
            if (control)
            {
                // ── the pit filled in: nothing descends, and the pit-bound things land where the trace planned them ──
                int falls = pawnDesc.Values.Sum() + goods.Sum(Desc);
                var off = new List<string>();
                foreach (string k in new[] { "pS", "g_pit", "g_cover" })
                {
                    Thing t = sc.things[k];
                    if (!plannedTo.ContainsKey(k) || !t.Spawned || t.Position != plannedTo[k] || RM_KnockbackCompat.IsSuperdeep(map, t.Position))
                    {
                        off.Add(k + (t.Spawned ? "@" + t.Position.x + "," + t.Position.z : " gone") + (plannedTo.ContainsKey(k) ? " planned " + plannedTo[k].x + "," + plannedTo[k].z : " unplanned"));
                    }
                }
                return Result(sc, falls == 0 && off.Count == 0, "descents=" + falls + " offPlan=[" + string.Join("; ", off) + "] cover cell "
                    + cover.x + "," + cover.z + " solid=" + !RM_KnockbackCompat.IsSuperdeep(map, cover) + " (step 300-900 ticks)");
            }
            // ── row east: carried away, stops dead at the east wall two cells on, lands alive and stunned ──
            Pawn pE = (Pawn)sc.things["pE"];
            var eb = ForThing(sc, "launch", pE).Concat(ForThing(sc, "blocked", pE)).ToList();
            bool eWall = eb.Count == 1 && (string)eb[0]["stop"] == "Wall" && Convert.ToSingle(eb[0]["impact"]) > 0f;
            bool east = eWall && pE.Spawned && !pE.Dead && pE.Position == O(sc, 3, 0) && sc.numbers.ContainsKey("pE_air")
                && sc.numbers.ContainsKey("pE_stunned");
            // ── row south: carried about three cells straight south ──
            Pawn pS = (Pawn)sc.things["pS"];
            IntVec3 s0 = sc.starts["pS"];
            bool south = pS.Spawned && !pS.Dead && pS.Position.x == s0.x && s0.z - pS.Position.z >= 2 && s0.z - pS.Position.z <= 4
                && sc.numbers.ContainsKey("pS_air");
            // ── row goods: every stack with a request moved; arc, spin, a rebound; zero despawn-spawn pairs ──
            var unmoved = goods.Where(k => ForThing(sc, "request", sc.things[k]).Count > 0 && ForThing(sc, "item_move", sc.things[k]).Count == 0).ToList();
            var flown = goods.Where(k => ForThing(sc, "item_move", sc.things[k]).Any(r => r.TryGetValue("flying", out object fl) && fl is bool b && b)).ToList();
            var flat = flown.Where(k => !(sc.numbers.TryGetValue(k + "_maxH", out float h) && h > 0f)).ToList();
            bool spin = flown.Any(k => sc.numbers.ContainsKey(k + "_spin"));
            int rebounds = goods.Sum(k => ForThing(sc, "item_rebound", sc.things[k]).Count);
            int tele = sc.things.Keys.Sum(k => sc.numbers.TryGetValue(k + "_tele", out float n) ? (int)n : 0);
            bool goodsOk = unmoved.Count == 0 && flown.Count > 0 && flat.Count == 0 && spin && rebounds >= 1 && tele == 0;
            // ── row container: contents unchanged, the locker thrown a short way straight away from the blast ──
            Thing box = sc.things["box"];
            var cl = ForThing(sc, "container", box);
            bool contents = new[] { "lk_pistol", "lk_revolver" }.All(k => sc.things[k].Spawned && box.Spawned && sc.things[k].Position == box.Position
                && Hp(sc.things[k]) == sc.numbers[k + "Hp"] && ForThing(sc, "item_move", sc.things[k]).Count == 0);
            bool boxThrown = box.Spawned && cl.Count == 1 && (string)cl[0]["action"] == "thrown" && box.Position.z == sc.starts["box"].z
                && box.Position.x < sc.starts["box"].x;
            // ── row heavy: the steel strikes p4 (2-5 blunt, a stagger) and stops there ──
            Thing st = sc.things["g_steel"];
            var hh = ForThing(sc, "heavy_hit", st);
            float dmg = hh.Count == 1 ? Convert.ToSingle(hh[0]["damage"]) : -1f;
            bool heavy = hh.Count == 1 && (int)hh[0]["pawnId"] == p4.thingIDNumber && dmg >= 2f && dmg <= 5f && Convert.ToInt32(hh[0]["stunTicks"]) > 0
                && st.Spawned && Cheb(st.Position, p4.Position) <= 1;
            // ── row pit: some goods and at least one colonist on the pit floor, one descent each ──
            var pitPawns = RoomColonists.Where(k => sc.things[k].Spawned && sc.things[k].Position != cover && RM_KnockbackCompat.IsSuperdeep(map, sc.things[k].Position)).ToList();
            var pitGoods = goods.Where(k => k != "g_cover" && sc.things[k].Spawned && RM_KnockbackCompat.IsSuperdeep(map, sc.things[k].Position)).ToList();
            bool pit = pitPawns.Count >= 1 && pitPawns.All(k => pawnDesc[k] == 1) && pitGoods.Count >= 1 && pitGoods.All(k => Desc(k) == 1);
            // ── row cover: the stack aimed at the covered cell falls through it, one descent, the cover destroyed ──
            Thing cg = sc.things["g_cover"];
            bool coverGone = RM_KnockbackCompat.CoverAt(map, cover) == null;
            bool through = coverGone && cg.Spawned && cg.Position == cover && Desc("g_cover") == 1;
            return Result(sc, east && south && goodsOk && contents && boxThrown && heavy && pit && through,
                "east=" + east + " [" + (eb.Count > 0 ? Rec(eb[0]) : "no launch") + " at " + pE.Position.x + "," + pE.Position.z + " stunned=" + sc.numbers.ContainsKey("pE_stunned") + "]"
                + " south=" + south + " [" + Moved(sc, "pS", out Thing _, out int _) + "]"
                + " goods=" + goodsOk + " [unmoved=" + string.Join(",", unmoved) + " flown=" + flown.Count + " flat=" + string.Join(",", flat)
                + " spin=" + spin + " rebounds=" + rebounds + " despawnSpawnPairs=" + tele + "]"
                + " container=" + (contents && boxThrown) + " [contents=" + contents + " thrown=" + boxThrown + (cl.Count > 0 ? " " + Rec(cl[0]) : " no container line") + "]"
                + " heavy=" + heavy + " [" + (hh.Count > 0 ? Rec(hh[0]) : "no heavy_hit") + "]"
                + " pit=" + pit + " [pawns=" + string.Join(",", pitPawns.Select(k => k + ":" + pawnDesc[k])) + " goods=" + string.Join(",", pitGoods.Select(k => k + ":" + Desc(k))) + "]"
                + " cover=" + through + " [cell " + cover.x + "," + cover.z + " gone=" + coverGone + " stack@" + (cg.Spawned ? cg.Position.x + "," + cg.Position.z : "gone") + " descents=" + Desc("g_cover") + "]"
                + " (step 300-900 ticks)");
        }
    }
}
#endif
