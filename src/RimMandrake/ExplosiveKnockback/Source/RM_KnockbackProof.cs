using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>
    /// In-game runner scenes (design §8.2), driven through the bridge's jawa/static_call:
    ///   Stage("scene,x,z")  clears a 15x15 patch at (x,z), builds the scene, sets the blast off -> "STAGED ..."
    ///   (the runner then steps ~300 ticks)
    ///   Verdict("scene")    -> "PASS scene ..." / "FAIL scene ..." read from the knockback JOURNAL plus state
    ///   Journal("all"|"n")  the last n journal lines; Clear("x") empties it; Settings("field=value") pokes a setting.
    /// SCRATCH MAPS ONLY: Stage destroys everything in its patch.
    /// </summary>
    public static class RM_KnockbackProof
    {
        private sealed class Scene
        {
            public string name;
            public IntVec3 o;
            public int stagedTick;
            public readonly Dictionary<string, Thing> things = new Dictionary<string, Thing>();
            public readonly Dictionary<string, IntVec3> starts = new Dictionary<string, IntVec3>();
            public readonly Dictionary<string, float> numbers = new Dictionary<string, float>();
            public Func<Scene, string> verdict;
            public Action restore;
        }

        private static readonly Dictionary<string, Scene> scenes = new Dictionary<string, Scene>();

        public static readonly string[] SceneNames =
        {
            "calibration", "wall_stop", "door_stop", "over_sandbags", "pit_colonist", "pit_enemy", "no_cross",
            "cover_breaks", "items", "corpse_into_pit", "killed_by_blast", "shelf", "in_pit_skip", "heavy_skip",
            "caps", "tick_cap", "settings_off", "emp_no_throw",
        };

        private static Map Map => Find.CurrentMap;

        // ── bridge surface ───────────────────────────────────────────────

        public static string Names(string _)
        {
            return string.Join(",", SceneNames) + " flowworks=" + RM_KnockbackCompat.FlowWorks + " gss=" + RM_KnockbackCompat.GimmeSomeSlack;
        }

        public static string Clear(string _)
        {
            RM_KnockbackJournal.Clear();
            return "CLEARED";
        }

        public static string Journal(string arg)
        {
            IReadOnlyList<string> l = RM_KnockbackJournal.Lines;
            int n = int.TryParse(arg, out int k) ? k : l.Count;
            return string.Join("\n", l.Skip(Math.Max(0, l.Count - n)));
        }

        /// <summary>"field=value" on RimMandrakeExplosiveKnockbackSettings; "reset" restores every default.</summary>
        public static string Settings(string arg)
        {
            if (arg == "reset")
            {
                RimMandrakeExplosiveKnockbackMod.Reset();
                return "RESET";
            }
            string[] kv = arg.Split('=');
            var f = typeof(RimMandrakeExplosiveKnockbackSettings).GetField(kv[0]);
            if (f == null || kv.Length != 2)
            {
                return "REFUSED: no field " + kv[0];
            }
            f.SetValue(null, Convert.ChangeType(kv[1], f.FieldType, System.Globalization.CultureInfo.InvariantCulture));
            return "SET " + kv[0] + "=" + f.GetValue(null);
        }

        /// <summary>n scene origins on a 15-cell pitch inside the current map, row-major from the south-west.</summary>
        public static string Origins(string arg)
        {
            Map map = Map;
            int n = int.TryParse(arg, out int k) ? k : SceneNames.Length;
            var o = new List<string>();
            for (int z = 12; z < map.Size.z - 12 && o.Count < n; z += 15)
            {
                for (int x = 12; x < map.Size.x - 12 && o.Count < n; x += 15)
                {
                    o.Add(x + "," + z);
                }
            }
            return string.Join(";", o);
        }

        public static string Stage(string arg)
        {
            string[] a = arg.Split(',');
            if (a.Length != 3 || !int.TryParse(a[1], out int x) || !int.TryParse(a[2], out int z) || Map == null)
            {
                return "REFUSED: arg must be scene,x,z on a current map";
            }
            var s = new Scene { name = a[0], o = new IntVec3(x, 0, z), stagedTick = Find.TickManager.TicksGame };
            try
            {
                Prepare(s.o, 7);
                string why = Build(s);
                if (why != null)
                {
                    return "INVALID " + s.name + " " + why;
                }
            }
            catch (Exception ex)
            {
                return "ERROR " + s.name + " " + ex.GetType().Name + ": " + ex.Message;
            }
            scenes[s.name] = s;
            return "STAGED " + s.name + " at " + x + "," + z + " tick=" + s.stagedTick;
        }

        public static string Verdict(string name)
        {
            if (!scenes.TryGetValue(name, out Scene s))
            {
                return "INVALID " + name + " not staged";
            }
            try
            {
                return s.verdict(s);
            }
            catch (Exception ex)
            {
                return "ERROR " + name + " " + ex.GetType().Name + ": " + ex.Message;
            }
            finally
            {
                s.restore?.Invoke();
            }
        }

        // ── scene construction ───────────────────────────────────────────

        private static void Prepare(IntVec3 o, int r)
        {
            Map map = Map;
            foreach (IntVec3 c in CellRect.CenteredOn(o, r).ClipInsideMap(map))
            {
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (t is Pawn || t.def.destroyable)
                    {
                        if (!t.Destroyed)
                        {
                            t.Destroy(DestroyMode.Vanish);
                        }
                    }
                }
                if (!RM_KnockbackCompat.IsSuperdeep(map, c))
                {
                    TerrainDef td = c.GetTerrain(map);
                    if (td == null || td.passability == Traversability.Impassable || td.IsWater)
                    {
                        map.terrainGrid.SetTerrain(c, TerrainDefOf.Soil);
                    }
                }
                map.roofGrid.SetRoof(c, null);
                map.fogGrid.Unfog(c);
                map.snowGrid?.SetDepth(c, 0f);
            }
        }

        private static Pawn Colonist(Scene s, string key, IntVec3 c, bool drafted = true)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            p.equipment?.DestroyAllEquipment();
            p.inventory?.DestroyAll();
            GenSpawn.Spawn(p, c, Map);
            if (drafted && p.drafter != null)
            {
                p.drafter.Drafted = true;
            }
            Track(s, key, p);
            return p;
        }

        private static Pawn Hostile(Scene s, string key, IntVec3 c)
        {
            Faction f = Find.FactionManager.RandomEnemyFaction(false, false, true, TechLevel.Industrial)
                ?? Find.FactionManager.RandomEnemyFaction();
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Mercenary_Gunner") ?? PawnKindDefOf.Colonist;
            Pawn p = PawnGenerator.GeneratePawn(kind, f);
            p.equipment?.DestroyAllEquipment();
            p.inventory?.DestroyAll();
            GenSpawn.Spawn(p, c, Map);
            Track(s, key, p);
            return p;
        }

        private static void Track(Scene s, string key, Thing t)
        {
            s.things[key] = t;
            s.starts[key] = t.Position;
        }

        private static Thing Build(string def, IntVec3 c, string stuff = null)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamed(def);
            ThingDef st = stuff != null ? DefDatabase<ThingDef>.GetNamed(stuff) : (d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
            Thing t = ThingMaker.MakeThing(d, st);
            t.SetFactionDirect(Faction.OfPlayer);
            return GenSpawn.Spawn(t, c, Map);
        }

        private static Thing Item(Scene s, string key, string def, int count, IntVec3 c)
        {
            Thing t = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed(def));
            t.stackCount = count;
            GenPlace.TryPlaceThing(t, c, Map, ThingPlaceMode.Direct, out Thing placed);
            Track(s, key, placed ?? t);
            return placed ?? t;
        }

        private static bool Pit(IntVec3 a, int w, int h)
        {
            bool ok = true;
            foreach (IntVec3 c in new CellRect(a.x, a.z, w, h))
            {
                ok &= RM_KnockbackCompat.DigToSuperdeep(Map, c);
            }
            return ok;
        }

        private static void Blast(IntVec3 c, float radius, DamageDef dt = null, int dmg = 1)
        {
            GenExplosion.DoExplosion(c, Map, radius, dt ?? DamageDefOf.Bomb, null, dmg);
        }

        private static IntVec3 O(Scene s, int dx, int dz) => s.o + new IntVec3(dx, 0, dz);

        // ── journal reads ────────────────────────────────────────────────

        private static List<Dictionary<string, object>> Recs(Scene s, string type)
        {
            return RM_KnockbackJournal.Recs.Where(r => (string)r["type"] == type && (int)r["tick"] >= s.stagedTick).ToList();
        }

        private static List<Dictionary<string, object>> ForThing(Scene s, string type, Thing t)
        {
            return Recs(s, type).Where(r => r.TryGetValue("thingId", out object id) && (int)id == t.thingIDNumber).ToList();
        }

        private static string Rec(Dictionary<string, object> r)
        {
            return string.Join(" ", r.Where(kv => kv.Key != "thingId").Select(kv => kv.Key + "=" + (kv.Value is IntVec3 c ? c.x + "," + c.z : Convert.ToString(kv.Value))));
        }

        private static int Cheb(IntVec3 a, IntVec3 b) => Math.Max(Math.Abs(a.x - b.x), Math.Abs(a.z - b.z));

        private static string Result(Scene s, bool ok, string detail)
        {
            return (ok ? "PASS " : "FAIL ") + s.name + " " + detail;
        }

        private static string Moved(Scene s, string key, out Thing t, out int cells)
        {
            t = s.things[key];
            cells = -1;
            if (t is Pawn p && p.Dead && p.Corpse != null)
            {
                t = p.Corpse;
            }
            if (!t.Spawned)
            {
                return key + " not spawned";
            }
            cells = Cheb(t.Position, s.starts[key]);
            return key + " " + s.starts[key].x + "," + s.starts[key].z + "->" + t.Position.x + "," + t.Position.z + " (" + cells + " cells)";
        }

        // ── the scenes ───────────────────────────────────────────────────

        private static string Build(Scene s)
        {
            Map map = Map;
            switch (s.name)
            {
                case "calibration":
                    Colonist(s, "p", O(s, 1, 0));
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var launch = ForThing(sc, "launch", t);
                        bool away = t.Spawned && t.Position.x > sc.starts["p"].x && t.Position.z == sc.starts["p"].z;
                        bool alive = t is Pawn p && !p.Dead;
                        return Result(sc, cells == 3 && away && alive && launch.Count == 1, m + " away=" + away + " alive=" + alive
                            + " launches=" + launch.Count + (launch.Count > 0 ? " [" + Rec(launch[0]) + "]" : ""));
                    };
                    return null;

                case "wall_stop":
                    Colonist(s, "p", O(s, 1, 0));
                    Build("Wall", O(s, 3, 0), "BlocksGranite");
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var b = ForThing(sc, "launch", t).Concat(ForThing(sc, "blocked", t)).ToList();
                        bool wall = b.Count == 1 && (string)b[0]["stop"] == "Wall" && Convert.ToSingle(b[0]["impact"]) > 0f;
                        return Result(sc, t.Spawned && t.Position == O(sc, 2, 0) && wall, m + (b.Count > 0 ? " [" + Rec(b[0]) + "]" : " no record"));
                    };
                    return null;

                case "door_stop":
                    Colonist(s, "p", O(s, 1, 0));
                    Thing door = Build("Door", O(s, 3, 0), "WoodLog");
                    Build("Wall", O(s, 3, 1), "BlocksGranite");
                    Build("Wall", O(s, 3, -1), "BlocksGranite");
                    s.numbers["doorHp"] = door.HitPoints;
                    s.things["door"] = door;
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var b = ForThing(sc, "launch", t).Concat(ForThing(sc, "blocked", t)).ToList();
                        Thing d = sc.things["door"];
                        bool hit = b.Count == 1 && (string)b[0]["stop"] == "Door";
                        bool hpDown = d.Spawned && d.HitPoints < sc.numbers["doorHp"] - 1; // the 1-damage blast itself takes 1
                        return Result(sc, t.Position == O(sc, 2, 0) && hit && hpDown, m + " doorHp " + sc.numbers["doorHp"] + "->" + d.HitPoints
                            + (b.Count > 0 ? " [" + Rec(b[0]) + "]" : ""));
                    };
                    return null;

                case "over_sandbags":
                    Colonist(s, "p", O(s, 1, 0));
                    for (int dz = -2; dz <= 2; dz++)
                    {
                        Build("Sandbags", O(s, 2, dz), "Cloth");
                    }
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        return Result(sc, t.Spawned && t.Position.x > sc.o.x + 2, m + " (sandbags at x+2)");
                    };
                    return null;

                case "pit_colonist":
                case "pit_enemy":
                    if (!RM_KnockbackCompat.FlowWorks)
                    {
                        return "FlowWorks not loaded";
                    }
                    if (!Pit(O(s, 3, -1), 3, 3))
                    {
                        return "could not dig the pit";
                    }
                    if (s.name == "pit_colonist")
                    {
                        Colonist(s, "p", O(s, 1, 0));
                    }
                    else
                    {
                        Hostile(s, "p", O(s, 1, 0));
                    }
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var desc = ForThing(sc, "descent", t);
                        bool inPit = t.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, t.Position);
                        return Result(sc, inPit && t.Position == O(sc, 3, 0) && desc.Count == 1, m + " inPit=" + inPit + " descents=" + desc.Count);
                    };
                    return null;

                case "no_cross":
                    if (!RM_KnockbackCompat.FlowWorks || !Pit(O(s, 2, -1), 1, 3))
                    {
                        return "FlowWorks not loaded / dig failed";
                    }
                    Colonist(s, "p", O(s, 0, 0));
                    Blast(O(s, -1, 0), 4.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        return Result(sc, t.Spawned && t.Position == O(sc, 2, 0), m + " (1-wide pit at x+2; must stop IN it)");
                    };
                    return null;

                case "cover_breaks":
                    if (!RM_KnockbackCompat.FlowWorks || !Pit(O(s, 1, -1), 3, 3))
                    {
                        return "FlowWorks not loaded / dig failed";
                    }
                    foreach (IntVec3 c in new CellRect(s.o.x + 1, s.o.z - 1, 3, 3))
                    {
                        Build("RM_PitCover_WovenScrap", c);
                    }
                    // a second deck nobody stands on
                    if (!Pit(O(s, -2, -2), 2, 2))
                    {
                        return "dig failed";
                    }
                    foreach (IntVec3 c in new CellRect(s.o.x - 2, s.o.z - 2, 2, 2))
                    {
                        Build("RM_PitCover_WovenScrap", c);
                    }
                    Colonist(s, "p", O(s, 2, 0), drafted: true);
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        int left = 0;
                        foreach (IntVec3 c in new CellRect(sc.o.x + 1, sc.o.z - 1, 3, 3).Concat(new CellRect(sc.o.x - 2, sc.o.z - 2, 2, 2)))
                        {
                            if (RM_KnockbackCompat.CoverAt(Map, c) != null)
                            {
                                left++;
                            }
                        }
                        Pawn p = (Pawn)sc.things["p"];
                        bool inPit = p.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, p.Position);
                        var desc = ForThing(sc, "descent", p);
                        return Result(sc, left == 0 && inPit && desc.Count >= 1, "coversLeft=" + left + " pawnInPit=" + inPit + " descents=" + desc.Count
                            + " at " + p.Position.x + "," + p.Position.z);
                    };
                    return null;

                case "items":
                    Item(s, "steel", "Steel", 75, O(s, 1, 0));
                    Item(s, "comp", "ComponentIndustrial", 1, O(s, 0, 1));
                    {
                        ThingDef sd = DefDatabase<ThingDef>.GetNamed("ElectricSmelter");
                        Thing smelter = ThingMaker.MakeThing(sd, GenStuff.DefaultStuffFor(sd));
                        Thing min = smelter.MakeMinified();
                        GenPlace.TryPlaceThing(min, O(s, -1, 0), Map, ThingPlaceMode.Direct, out Thing placed);
                        Track(s, "heavy", placed ?? min);
                    }
                    s.numbers["steelCount"] = 75;
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        var sb = new StringBuilder();
                        bool ok = true;
                        KbSettings k = RimMandrakeExplosiveKnockbackSettings.Kernel();
                        foreach (string key in new[] { "steel", "comp", "heavy" })
                        {
                            Thing t = sc.things[key];
                            float mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount;
                            int want = mass > k.lightMassLimit ? 0 : RM_KnockbackMath.ThrowCells((sc.starts[key] - sc.o).LengthHorizontal, 2.9f, 1f, mass, k);
                            sb.Append(Moved(sc, key, out Thing tt, out int cells)).Append(" mass=").Append(mass.ToString("0.#")).Append(" want=").Append(want).Append("; ");
                            ok &= tt.Spawned && cells == want;
                        }
                        Thing st = sc.things["steel"];
                        ok &= st.stackCount == 75;
                        ok &= sc.things["heavy"].GetStatValue(StatDefOf.Mass) > k.lightMassLimit; // else the scene proves nothing
                        return Result(sc, ok, sb + "steelCount=" + st.stackCount);
                    };
                    return null;

                case "corpse_into_pit":
                    if (!RM_KnockbackCompat.FlowWorks || !Pit(O(s, 3, -1), 3, 3))
                    {
                        return "FlowWorks not loaded / dig failed";
                    }
                    {
                        Pawn p = Colonist(s, "p", O(s, 1, 0), drafted: false);
                        p.Kill(null);
                        Track(s, "corpse", p.Corpse);
                    }
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "corpse", out Thing t, out int cells);
                        bool inPit = t.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, t.Position);
                        bool forbidden = t.Spawned && t.IsForbidden(Faction.OfPlayer);
                        return Result(sc, inPit && t.Position == O(sc, 3, 0), m + " onPitFloor=" + inPit + " forbidden=" + forbidden);
                    };
                    return null;

                case "killed_by_blast":
                    Colonist(s, "p", O(s, 1, 0), drafted: false);
                    GenExplosion.DoExplosion(s.o, Map, 2.9f, DamageDefOf.Bomb, null, 400);
                    s.verdict = sc =>
                    {
                        Pawn p = (Pawn)sc.things["p"];
                        Corpse c = p.Corpse;
                        bool moved = c != null && c.Spawned && Cheb(c.Position, sc.starts["p"]) >= 1;
                        var rec = c == null ? new List<Dictionary<string, object>>() : ForThing(sc, "item_move", c);
                        return Result(sc, p.Dead && moved && rec.Count == 1, "dead=" + p.Dead + " corpseMoved=" + moved
                            + (rec.Count > 0 ? " [" + Rec(rec[0]) + "]" : ""));
                    };
                    return null;

                case "shelf":
                    {
                        Thing shelf = Build("Shelf", O(s, 1, 0), "WoodLog");
                        Item(s, "steel", "Steel", 20, shelf.Position);
                    }
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "steel", out Thing t, out int cells);
                        return Result(sc, cells == 0, m + " (on a shelf: must stay)");
                    };
                    return null;

                case "in_pit_skip":
                    if (!RM_KnockbackCompat.FlowWorks || !Pit(O(s, 1, -1), 3, 3))
                    {
                        return "FlowWorks not loaded / dig failed";
                    }
                    Colonist(s, "p", O(s, 1, 0));
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var skip = ForThing(sc, "skip", t).Where(r => (string)r["reason"] == "in_pit").ToList();
                        return Result(sc, cells == 0 && skip.Count == 1, m + " skips(in_pit)=" + skip.Count);
                    };
                    return null;

                case "heavy_skip":
                    {
                        PawnKindDef big = DefDatabase<PawnKindDef>.GetNamed("Thrumbo");
                        Pawn a = PawnGenerator.GeneratePawn(big, null);
                        GenSpawn.Spawn(a, O(s, 1, 0), Map);
                        Track(s, "big", a);
                        s.restore = () => { if (!a.Destroyed) a.Destroy(); };
                    }
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "big", out Thing t, out int cells);
                        var skip = ForThing(sc, "skip", t).Where(r => (string)r["reason"] == "too_big").ToList();
                        return Result(sc, skip.Count == 1 && ForThing(sc, "launch", t).Count == 0, m + " skips(too_big)=" + skip.Count);
                    };
                    return null;

                case "caps":
                    {
                        int i = 0;
                        foreach (IntVec3 c in GenRadial.RadialCellsAround(s.o, 4.9f, false))
                        {
                            if (i < 10 && c != s.o && Math.Abs(c.x - s.o.x) == 2 && Math.Abs(c.z - s.o.z) <= 2)
                            {
                                Colonist(s, "p" + i, c);
                                i++;
                            }
                        }
                        int n = 0;
                        foreach (IntVec3 c in GenRadial.RadialCellsAround(s.o, 4.9f, true))
                        {
                            if (n < 60 && c.GetFirstPawn(Map) == null)
                            {
                                Item(s, "i" + n, "Steel", 10, c);
                                n++;
                            }
                        }
                        s.numbers["pawns"] = i;
                        s.numbers["items"] = n;
                    }
                    Blast(s.o, 5.9f);
                    s.verdict = sc =>
                    {
                        int exp = Recs(sc, "request").Where(r => (IntVec3)r["centre"] == sc.o).Select(r => (int)r["exp"]).FirstOrDefault();
                        int launches = Recs(sc, "launch").Count(r => (int)r["exp"] == exp);
                        var pawnIds = new HashSet<int>(sc.things.Values.OfType<Pawn>().Select(p => p.thingIDNumber));
                        int pawnsHandled = Recs(sc, "launch").Concat(Recs(sc, "blocked"))
                            .Count(r => (int)r["exp"] == exp && r.ContainsKey("thingId") && pawnIds.Contains((int)r["thingId"]));
                        int moves = Recs(sc, "item_move").Count(r => (int)r["exp"] == exp);
                        int capped = Recs(sc, "skip").Count(r => (int)r["exp"] == exp && (string)r["reason"] == "cap_per_explosion");
                        int cap = RimMandrakeExplosiveKnockbackSettings.maxThrowsPerExplosion;
                        bool ok = launches + moves <= cap && pawnsHandled == (int)sc.numbers["pawns"] && capped > 0;
                        return Result(sc, ok, "pawns=" + sc.numbers["pawns"] + " pawnsHandled=" + pawnsHandled + " items=" + sc.numbers["items"] + " launches=" + launches + " itemMoves=" + moves
                            + " cappedSkips=" + capped + " cap=" + cap);
                    };
                    return null;

                case "tick_cap":
                    {
                        int n = 0;
                        foreach (IntVec3 c in GenRadial.RadialCellsAround(s.o, 1.9f, true))
                        {
                            Item(s, "i" + n, "Steel", 10, c);
                            n++;
                        }
                        s.numbers["items"] = n;
                    }
                    RimMandrakeExplosiveKnockbackSettings.maxItemThrowsPerMapTick = 3;
                    Blast(s.o, 2.9f);
                    s.restore = () => RimMandrakeExplosiveKnockbackSettings.maxItemThrowsPerMapTick = 60;
                    s.verdict = sc =>
                    {
                        var moves = Recs(sc, "item_move");
                        int maxPerTick = moves.GroupBy(r => (int)r["tick"]).Select(g => g.Count()).DefaultIfEmpty(0).Max();
                        int dropped = Recs(sc, "skip").Count(r => (string)r["reason"] == "cap_per_tick");
                        return Result(sc, maxPerTick <= 3 && dropped > 0, "items=" + sc.numbers["items"] + " moves=" + moves.Count + " maxPerTick=" + maxPerTick
                            + " droppedByTickCap=" + dropped);
                    };
                    return null;

                case "settings_off":
                    Colonist(s, "p", O(s, 1, 0));
                    Item(s, "steel", "Steel", 10, O(s, -1, 0));
                    RimMandrakeExplosiveKnockbackSettings.enabled = false;
                    Blast(s.o, 2.9f);
                    s.restore = () => RimMandrakeExplosiveKnockbackSettings.enabled = true;
                    s.verdict = sc =>
                    {
                        string m1 = Moved(sc, "p", out Thing t1, out int c1);
                        string m2 = Moved(sc, "steel", out Thing t2, out int c2);
                        bool wave = ((Pawn)t1).health.hediffSet.hediffs.Any(h => h is Hediff_Injury) || t2.HitPoints < t2.MaxHitPoints;
                        return Result(sc, c1 == 0 && c2 == 0 && wave, m1 + "; " + m2 + " waveHitThem=" + wave);
                    };
                    return null;

                case "emp_no_throw":
                    Colonist(s, "p", O(s, 1, 0));
                    Blast(s.o, 2.9f, DamageDefOf.EMP, 10);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        return Result(sc, cells == 0 && ForThing(sc, "request", t).Count == 0, m + " (EMP force 0: no request)");
                    };
                    return null;
            }
            return "unknown scene " + s.name;
        }
    }
}
