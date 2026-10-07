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
            // 2026-10-06 finish pass (KINETIC_BLAST_WEAPONS_1): per-blast config, stun-lock guard, shields. NOT YET RUN LIVE.
            "lookup_projectile", "lookup_zero_wins", "impact_factor", "body_override", "immunity_window", "shield_counter",
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

        private static Pawn Adult(PawnKindDef k)
        {
            Pawn p = PawnGenerator.GeneratePawn(k, null);
            p.ageTracker.AgeBiologicalTicks = (long)(p.RaceProps.lifeStageAges[p.RaceProps.lifeStageAges.Count - 1].minAge * 3600000f) + 1;
            return p;
        }

        /// <summary>Adds a knockback extension to a def for one scene; the scene's restore removes it again.</summary>
        private static void AddExt(Scene s, Def d, RM_KnockbackExtension ext)
        {
            if (d.modExtensions == null)
            {
                d.modExtensions = new List<DefModExtension>();
            }
            d.modExtensions.Add(ext);
            Action prev = s.restore;
            s.restore = () =>
            {
                d.modExtensions.Remove(ext);
                prev?.Invoke();
            };
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
                        var land = ForThing(sc, "land", t);
                        // the LANDING cell, not the current one: a held hostile walks about on the pit floor afterwards
                        bool landed = land.Count == 1 && (IntVec3)land[0]["at"] == O(sc, 3, 0);
                        bool inPit = t.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, t.Position);
                        return Result(sc, inPit && landed && desc.Count == 1, m + " landedOnFirstPitCell=" + landed + " stillInPit=" + inPit
                            + " descents=" + desc.Count);
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
                        // the heaviest-but-small minifiable building in the game, so "heavy stays" is measured on a thing
                        // that really is over the limit (a minified electric smelter is only 20 kg: measured live)
                        ThingDef sd = DefDatabase<ThingDef>.AllDefs
                            .Where(d => d.Minifiable && d.size.x * d.size.z <= 2)
                            .OrderByDescending(d => d.GetStatValueAbstract(StatDefOf.Mass, GenStuff.DefaultStuffFor(d)))
                            .First();
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
                    // three pawns and a huge blast: explosion damage lands on random parts, so one pawn can survive it
                    // (measured live: a 400-damage blast left one standing); the verdict judges every one that died
                    Colonist(s, "p0", O(s, 1, 0), drafted: false);
                    Colonist(s, "p1", O(s, 0, 1), drafted: false);
                    Colonist(s, "p2", O(s, -1, 0), drafted: false);
                    GenExplosion.DoExplosion(s.o, Map, 2.9f, DamageDefOf.Bomb, null, 9999);
                    s.verdict = sc =>
                    {
                        int dead = 0, thrown = 0;
                        foreach (string key in new[] { "p0", "p1", "p2" })
                        {
                            Pawn p = (Pawn)sc.things[key];
                            if (!p.Dead || p.Corpse == null)
                            {
                                continue;
                            }
                            dead++;
                            if (ForThing(sc, "item_move", p.Corpse).Count == 1 && Cheb(p.Corpse.Position, sc.starts[key]) >= 1)
                            {
                                thrown++;
                            }
                        }
                        if (dead == 0)
                        {
                            return "INVALID " + sc.name + " the blast killed nobody";
                        }
                        return Result(sc, thrown == dead, "dead=" + dead + " corpsesThrown=" + thrown);
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

                case "lookup_projectile":
                case "lookup_zero_wins":
                {
                    // a projectile ThingDef's own extension beats the DamageDef's (design §2.1). The extension is added to a
                    // vanilla bullet def for the scene only and removed again in restore.
                    bool zero = s.name == "lookup_zero_wins";
                    ThingDef proj = DefDatabase<ThingDef>.GetNamed("Bullet_Revolver");
                    var ext = new RM_KnockbackExtension { force = zero ? 0f : 2.5f, maxThrowCells = 8 };
                    AddExt(s, proj, ext);
                    Colonist(s, "p", O(s, 1, 0));
                    GenExplosion.DoExplosion(s.o, Map, 2.9f, DamageDefOf.Bomb, null, 1, -1f, null, null, proj);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var req = ForThing(sc, "request", t);
                        if (zero)
                        {
                            // explicit force 0 on the projectile wins over Bomb's 1.0: nothing is even requested
                            return Result(sc, cells == 0 && req.Count == 0, m + " requests=" + req.Count);
                        }
                        bool src = req.Count == 1 && (string)req[0]["source"] == "projectile";
                        // kernel: force 2.5, d 1, r 2.9, 70 kg -> round(4 x 2.5 x 0.655 x ~1) = 7 capped by 8; read the kernel, not a literal
                        int want = RM_KnockbackMath.ThrowCells(1f, 2.9f, 2.5f, ((Pawn)t).GetStatValue(StatDefOf.Mass), RimMandrakeExplosiveKnockbackSettings.Kernel(ext.ToConfig()));
                        return Result(sc, src && cells >= want - 1 && cells <= want, m + " want~" + want + (req.Count > 0 ? " [" + Rec(req[0]) + "]" : " no request"));
                    };
                    return null;
                }

                case "impact_factor":
                {
                    ThingDef proj = DefDatabase<ThingDef>.GetNamed("Bullet_Revolver");
                    AddExt(s, proj, new RM_KnockbackExtension { force = 1f, impactFactor = 0f });
                    Colonist(s, "p", O(s, 1, 0));
                    Build("Wall", O(s, 3, 0), "BlocksGranite");
                    GenExplosion.DoExplosion(s.o, Map, 2.9f, DamageDefOf.Bomb, null, 1, -1f, null, null, proj);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var b = ForThing(sc, "launch", t).Concat(ForThing(sc, "blocked", t)).ToList();
                        bool ok = b.Count == 1 && (string)b[0]["stop"] == "Wall" && Convert.ToSingle(b[0]["impact"]) == 0f;
                        return Result(sc, ok && t.Position == O(sc, 2, 0), m + (b.Count > 0 ? " [" + Rec(b[0]) + "]" : " no record"));
                    };
                    return null;
                }

                case "body_override":
                {
                    // an animal with 2.5 <= body size < 3.6: immune under the global 2.5, thrown under a 3.6 override
                    PawnKindDef big = DefDatabase<PawnKindDef>.AllDefs.Where(k => k.RaceProps != null && k.RaceProps.Animal
                        && k.RaceProps.baseBodySize >= 2.5f && k.RaceProps.baseBodySize < 3.5f && k.RaceProps.IsFlesh
                        && k.RaceProps.lifeStageAges.Count > 0).OrderBy(k => k.RaceProps.baseBodySize).FirstOrDefault();
                    if (big == null)
                    {
                        return "no animal kind with body size 2.5-3.5 on this list";
                    }
                    ThingDef proj = DefDatabase<ThingDef>.GetNamed("Bullet_Revolver");
                    AddExt(s, proj, new RM_KnockbackExtension { force = 4f, maxThrowCells = 10, immuneBodySizeOverride = 3.6f });
                    Pawn a = Adult(big);
                    GenSpawn.Spawn(a, O(s, 1, 0), Map);
                    Track(s, "big", a);
                    Pawn b = Adult(big);
                    GenSpawn.Spawn(b, O(s, -1, 3), Map);
                    Track(s, "control", b);
                    s.numbers["bodySize"] = a.BodySize;
                    GenExplosion.DoExplosion(s.o, Map, 2.9f, DamageDefOf.Bomb, null, 1, -1f, null, null, proj);
                    GenExplosion.DoExplosion(O(s, -1, 4), Map, 1.5f, DamageDefOf.Bomb, null, 1); // control: Bomb, global 2.5 holds
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "big", out Thing t, out int cells);
                        string mc = Moved(sc, "control", out Thing tc, out int cc);
                        bool ctrlSkip = ForThing(sc, "skip", tc).Any(r => (string)r["reason"] == "too_big");
                        return Result(sc, cells > 0 && cc == 0 && ctrlSkip, m + "; " + mc + " bodySize=" + sc.numbers["bodySize"].ToString("0.0")
                            + " controlTooBig=" + ctrlSkip);
                    };
                    return null;
                }

                case "immunity_window":
                {
                    int was = RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks;
                    RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks = 600;
                    s.restore = () => RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks = was;
                    Pawn p = Colonist(s, "p", O(s, -3, 0));
                    Blast(O(s, -4, 0), 2.9f); // throws p east ~3 cells, toward the origin
                    Map m0 = Map;
                    // a second blast 250 ticks later beside wherever p landed: still inside stun + 600, so "immune"
                    RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + 250, () =>
                    {
                        if (p.Spawned)
                        {
                            GenExplosion.DoExplosion(p.Position + IntVec3.West, m0, 2.9f, DamageDefOf.Bomb, null, 1);
                        }
                    }));
                    s.verdict = sc =>
                    {
                        Thing t = sc.things["p"];
                        int launches = ForThing(sc, "launch", t).Count;
                        bool immune = ForThing(sc, "skip", t).Any(r => (string)r["reason"] == "immune");
                        bool guard = t is Pawn pp && pp.Spawned && !pp.Map.GetComponent<RM_MapComponent_Knockback>().CanLaunch(pp, out _);
                        return Result(sc, launches == 1 && immune && guard, "launches=" + launches + " immuneSkip=" + immune + " guardHolds=" + guard);
                    };
                    return null;
                }

                case "shield_counter":
                {
                    Pawn p = Colonist(s, "p", O(s, 1, 0));
                    ThingDef beltDef = DefDatabase<ThingDef>.GetNamedSilentFail("Apparel_ShieldBelt");
                    if (beltDef == null)
                    {
                        return "no Apparel_ShieldBelt def";
                    }
                    var belt = (Apparel)ThingMaker.MakeThing(beltDef, GenStuff.DefaultStuffFor(beltDef));
                    p.apparel.Wear(belt);
                    CompShield sh = belt.GetComp<CompShield>();
                    s.numbers["energy0"] = sh?.Energy ?? -1f;
                    s.things["belt"] = belt;
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var sk = ForThing(sc, "skip", t).Where(r => (string)r["reason"] == "shield").ToList();
                        CompShield shc = ((Apparel)sc.things["belt"]).GetComp<CompShield>();
                        float e1 = shc?.Energy ?? -1f;
                        bool drained = e1 < sc.numbers["energy0"];
                        return Result(sc, cells == 0 && sk.Count == 1 && drained, m + " energy " + sc.numbers["energy0"].ToString("0.###")
                            + "->" + e1.ToString("0.###") + (sk.Count > 0 ? " [" + Rec(sk[0]) + "]" : " no shield skip"));
                    };
                    return null;
                }

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
