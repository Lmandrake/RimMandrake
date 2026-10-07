using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.ExplosiveKnockback;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.KineticArms
{
    /// <summary>
    /// In-game scenes for Kinetic Arms' first functional script (validation.py), driven through jawa/static_call:
    ///   Stage("scene,x,z") clears a 15x15 patch, builds the scene and fires the weapon through its REAL projectile
    ///   (spawned and Launch()ed from a shooter, so the projectile class, its DamageDef and its cone are what is tested)
    ///   or the kicker mine's own Kick(); Verdict("scene") reads Explosive Knockback's journal plus map state.
    ///   Settings("field=value"|"reset") pokes Kinetic Arms' settings and re-applies them.
    /// What it does NOT prove: verb accuracy, AI use, a pawn walking onto the mine (spring chance), power wiring.
    /// SCRATCH MAPS ONLY: Stage destroys everything in its patch.
    /// </summary>
    public static class RM_KineticArmsProof
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
        }

        private static readonly Dictionary<string, Scene> scenes = new Dictionary<string, Scene>();

        public static readonly string[] SceneNames =
        {
            "thump_cannon", "thump_off", "thudder_crowd", "palm_shove", "slam_charge", "repulsor_along_shot",
            "repulsor_westward", "grav_ram", "thump_shell", "kicker_north", "kicker_east", "kicker_south", "kicker_west",
            "kicker_dud_rearm", "pulse_push", "pulse_charge_gate", "strength_zero", "looted_pirates",
            // 2026-10-06 finish pass (KINETIC_BLAST_WEAPONS_1). NOT YET RUN LIVE.
            "palm_arrest_wall", "gravram_big_body", "ruins_loot", "kicker_hidden", "cords_marker", "ring_fleck",
        };

        private static Map Map => Find.CurrentMap;

        public static string Names(string _) => string.Join(",", SceneNames);

        public static string Settings(string arg)
        {
            if (arg == "reset")
            {
                RimMandrakeKineticArmsMod.Reset();
                return "RESET";
            }
            string[] kv = arg.Split('=');
            var f = typeof(RimMandrakeKineticArmsSettings).GetField(kv[0]);
            if (f == null || kv.Length != 2)
            {
                return "REFUSED: no field " + kv[0];
            }
            f.SetValue(null, Convert.ChangeType(kv[1], f.FieldType, System.Globalization.CultureInfo.InvariantCulture));
            RimMandrakeKineticArmsMod.ApplySettings();
            return "SET " + kv[0] + "=" + f.GetValue(null);
        }

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
        }

        // ── helpers ──────────────────────────────────────────────────────

        private static void Prepare(IntVec3 o, int r)
        {
            Map map = Map;
            foreach (IntVec3 c in CellRect.CenteredOn(o, r).ClipInsideMap(map))
            {
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if ((t is Pawn || t.def.destroyable) && !t.Destroyed)
                    {
                        t.Destroy(DestroyMode.Vanish);
                    }
                }
                RM_KnockbackCompat.FillToSurface(map, c); // a pit an earlier scene (EK pit_*) dug at this origin
                TerrainDef td = c.GetTerrain(map);
                if (td == null || td.passability == Traversability.Impassable || td.IsWater)
                {
                    map.terrainGrid.SetTerrain(c, TerrainDefOf.Soil);
                }
                map.roofGrid.SetRoof(c, null);
                map.fogGrid.Unfog(c);
            }
        }

        private static IntVec3 O(Scene s, int dx, int dz) => s.o + new IntVec3(dx, 0, dz);

        private static Pawn Colonist(Scene s, string key, IntVec3 c)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            p.equipment?.DestroyAllEquipment();
            p.inventory?.DestroyAll();
            GenSpawn.Spawn(p, c, Map);
            if (p.drafter != null)
            {
                p.drafter.Drafted = true;
            }
            Track(s, key, p);
            return p;
        }

        private static Pawn Hostile(Scene s, string key, IntVec3 c)
        {
            Faction f = Find.FactionManager.RandomEnemyFaction(false, false, true, TechLevel.Industrial) ?? Find.FactionManager.RandomEnemyFaction();
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Mercenary_Gunner") ?? PawnKindDefOf.Colonist;
            Pawn p = PawnGenerator.GeneratePawn(kind, f);
            p.equipment?.DestroyAllEquipment();
            p.inventory?.DestroyAll();
            GenSpawn.Spawn(p, c, Map);
            Track(s, key, p);
            return p;
        }

        private static Pawn Animal(Scene s, string key, PawnKindDef k, IntVec3 c)
        {
            Pawn p = PawnGenerator.GeneratePawn(k, null);
            p.ageTracker.AgeBiologicalTicks = (long)(p.RaceProps.lifeStageAges[p.RaceProps.lifeStageAges.Count - 1].minAge * 3600000f) + 1;
            GenSpawn.Spawn(p, c, Map);
            Track(s, key, p);
            return p;
        }

        /// <summary>A bystander whose verdict is "did not move": stunned for the whole scene, so an unarmed hostile or a
        /// shot animal cannot walk off and fake a throw (live 2026-10-07: side/thump_off/strength_zero/control pawns
        /// stepped 1-3 cells). Stun does not gate Explosive Knockback (PawnSkipReason, Eligible), so a real throw still
        /// shows — and NotThrown also requires zero launch records.</summary>
        private static Pawn Hold(Pawn p)
        {
            p.stances?.stunner?.StunFor(2500, null, false, false);
            return p;
        }

        /// <summary>Unmoved AND no launch/blocked record in Explosive Knockback's journal.</summary>
        private static bool NotThrown(Scene s, string key, out string detail)
        {
            string m = Moved(s, key, out int dx, out int dz);
            int launches = ForThing(s, "launch", s.things[key]).Count;
            detail = m + " launches=" + launches;
            return dx == 0 && dz == 0 && launches == 0;
        }

        private static void Track(Scene s, string key, Thing t)
        {
            s.things[key] = t;
            s.starts[key] = t.Position;
            if (t is Pawn p)
            {
                s.numbers[key + "_inj"] = p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury);
            }
        }

        /// <summary>Spawn the projectile at the shooter and Launch it at a pawn or a cell — the projectile's own class,
        /// DamageDef and extension do the rest.</summary>
        private static void Fire(Pawn shooter, string projectile, LocalTargetInfo target, string weapon = null)
        {
            ThingDef pd = DefDatabase<ThingDef>.GetNamed(projectile);
            Thing eq = weapon != null ? ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed(weapon)) : null;
            var proj = (Projectile)GenSpawn.Spawn(pd, shooter.Position, Map);
            proj.Launch(shooter, shooter.DrawPos, target, target, ProjectileHitFlags.IntendedTarget, false, eq);
        }

        private static List<Dictionary<string, object>> ForThing(Scene s, string type, Thing t)
        {
            return RM_KnockbackJournal.Recs.Where(r => (string)r["type"] == type && (int)r["tick"] >= s.stagedTick
                && r.TryGetValue("thingId", out object id) && (int)id == t.thingIDNumber).ToList();
        }

        private static string Moved(Scene s, string key, out int dx, out int dz)
        {
            Thing t = s.things[key];
            dx = dz = 0;
            if (t is Pawn p && p.Dead && p.Corpse != null)
            {
                t = p.Corpse;
            }
            if (!t.Spawned)
            {
                return key + " not spawned";
            }
            dx = t.Position.x - s.starts[key].x;
            dz = t.Position.z - s.starts[key].z;
            return key + " " + s.starts[key].x + "," + s.starts[key].z + "->" + t.Position.x + "," + t.Position.z;
        }

        private static int NewInjuries(Scene s, string key)
        {
            return s.things[key] is Pawn p ? p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury) - (int)s.numbers[key + "_inj"] : 0;
        }

        private static bool Dead(Scene s, string key) => s.things[key] is Pawn p && p.Dead;

        private static string Result(Scene s, bool ok, string detail) => (ok ? "PASS " : "FAIL ") + s.name + " " + detail;

        /// <summary>Thrown along +x/-x/+z/-z: moved only on that axis, by at least min cells.</summary>
        private static string AlongAxis(Scene s, string key, int ax, int az, int min, bool requireNoWound)
        {
            string m = Moved(s, key, out int dx, out int dz);
            int along = dx * ax + dz * az;
            int across = Math.Abs(dx * az) + Math.Abs(dz * ax);
            int launches = ForThing(s, "launch", s.things[key]).Count + ForThing(s, "blocked", s.things[key]).Count;
            int wounds = NewInjuries(s, key);
            bool ok = along >= min && across <= 1 && launches >= 1 && !Dead(s, key) && (!requireNoWound || wounds == 0);
            return Result(s, ok, m + " along=" + along + " across=" + across + " launches=" + launches + " newInjuries=" + wounds);
        }

        // ── the scenes ───────────────────────────────────────────────────

        private static string Build(Scene s)
        {
            switch (s.name)
            {
                case "thump_cannon":
                case "thump_off":
                    {
                        if (s.name == "thump_off")
                        {
                            RimMandrakeKineticArmsSettings.thumpCannonThrows = false;
                            RimMandrakeKineticArmsMod.ApplySettings();
                        }
                        Pawn sh = Colonist(s, "shooter", O(s, -6, 0));
                        Pawn tp = Hostile(s, "p", O(s, 1, 0));
                        if (s.name == "thump_off")
                        {
                            Hold(tp);
                        }
                        s.numbers["force"] = RimMandrakeKineticArmsMod.ForceOf("Thump");
                        Fire(sh, "Bullet_ThumpCannon", O(s, 0, 0), "Gun_ThumpCannon");
                        if (s.name == "thump_off")
                        {
                            RimMandrakeKineticArmsSettings.thumpCannonThrows = true;
                            s.verdict = sc =>
                            {
                                RimMandrakeKineticArmsMod.ApplySettings();
                                bool still = NotThrown(sc, "p", out string m);
                                return Result(sc, still && sc.numbers["force"] == 0f, m + " forceWhileOff=" + sc.numbers["force"]);
                            };
                            return null;
                        }
                        // force 2.5 at d=1 of r=1.9 => 5 cells (design §2.2) vs the mortar's 3 (Explosive Knockback calibration)
                        s.verdict = sc => AlongAxis(sc, "p", 1, 0, 4, false) + " force=" + sc.numbers["force"];
                        return null;
                    }

                case "thudder_crowd":
                    {
                        Pawn sh = Colonist(s, "shooter", O(s, -6, 0));
                        Hostile(s, "a", O(s, 1, 0));
                        Hostile(s, "b", O(s, -1, 0));
                        Hostile(s, "c", O(s, 0, 1));
                        Hostile(s, "d", O(s, 0, -1));
                        Fire(sh, "RM_Proj_ThudderGrenade", O(s, 0, 0), "RM_Weapon_ThudderGrenade");
                        s.verdict = sc =>
                        {
                            int thrown = 0, dead = 0;
                            var parts = new List<string>();
                            foreach (string k in new[] { "a", "b", "c", "d" })
                            {
                                parts.Add(Moved(sc, k, out int dx, out int dz));
                                if (Math.Max(Math.Abs(dx), Math.Abs(dz)) >= 3) thrown++;
                                if (Dead(sc, k)) dead++;
                            }
                            return Result(sc, thrown >= 3 && dead == 0, "thrown>=3cells=" + thrown + " dead=" + dead + " | " + string.Join("; ", parts));
                        };
                        return null;
                    }

                case "palm_shove":
                    {
                        Pawn sh = Colonist(s, "shooter", O(s, -5, 0));
                        Pawn t = Hostile(s, "p", O(s, 0, 0));
                        Hold(Hostile(s, "side", O(s, -1, 1))); // shooter side of the back-step centre: outside the cone
                        Fire(sh, "RM_Proj_PalmThump", t, "RM_Gun_PalmThumper");
                        s.verdict = sc =>
                        {
                            string a = AlongAxis(sc, "p", 1, 0, 2, true);
                            bool sideStill = NotThrown(sc, "side", out string m);
                            return (a.StartsWith("PASS") && sideStill ? "PASS " : "FAIL ") + a.Substring(5) + " | " + m + " sideUnmoved=" + sideStill;
                        };
                        return null;
                    }

                case "slam_charge":
                    {
                        Pawn sh = Colonist(s, "shooter", O(s, -6, 0));
                        Hostile(s, "p", O(s, 1, 0));
                        Fire(sh, "RM_Proj_SlamCharge", O(s, 0, 0), "RM_Gun_SlamLauncher");
                        s.verdict = sc => AlongAxis(sc, "p", 1, 0, 3, false);
                        return null;
                    }

                case "repulsor_along_shot":
                case "repulsor_westward":
                    {
                        bool west = s.name == "repulsor_westward"; // ±180 degrees: the wrap-around case
                        Pawn sh = Colonist(s, "shooter", O(s, west ? 6 : -6, 0));
                        Pawn t = Hostile(s, "p", O(s, 0, 0));
                        Fire(sh, "RM_Proj_RepulsorBolt", t, "RM_Gun_RepulsorRifle");
                        s.verdict = sc => AlongAxis(sc, "p", west ? -1 : 1, 0, 3, true);
                        return null;
                    }

                case "grav_ram":
                    {
                        Pawn sh = Colonist(s, "shooter", O(s, -6, 0));
                        Pawn t = Hostile(s, "p", O(s, 0, 0));
                        Fire(sh, "RM_Proj_GravRamPulse", t, "RM_Gun_GravRam");
                        // its own cap is 10 (owner card 2026-10-06): >= 7 proves it is no longer held to the global 6
                        s.verdict = sc => AlongAxis(sc, "p", 1, 0, 7, true);
                        return null;
                    }

                case "thump_shell":
                    {
                        Pawn sh = Colonist(s, "shooter", O(s, -6, -6));
                        Hostile(s, "p", O(s, 1, 0));
                        Fire(sh, "RM_Bullet_Shell_Thump", O(s, 0, 0));
                        s.verdict = sc => AlongAxis(sc, "p", 1, 0, 3, false);
                        return null;
                    }

                case "kicker_north":
                case "kicker_east":
                case "kicker_south":
                case "kicker_west":
                    {
                        int rot = Array.IndexOf(new[] { "kicker_north", "kicker_east", "kicker_south", "kicker_west" }, s.name);
                        var mine = (RM_Building_KickerMine)GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RM_KickerMine")),
                            s.o, Map, new Rot4(rot));
                        mine.SetFactionDirect(Faction.OfPlayer);
                        Pawn p = Hostile(s, "p", s.o);
                        CompRefuelable fuel = mine.GetComp<CompRefuelable>();
                        s.numbers["fuel0"] = fuel.Fuel;
                        s.things["mine"] = mine;
                        mine.Kick(p);
                        RM_KineticMath.Facing(rot, out float fx, out float fz);
                        s.verdict = sc =>
                        {
                            string a = AlongAxis(sc, "p", (int)fx, (int)fz, 3, true);
                            float spent = sc.numbers["fuel0"] - ((Thing)sc.things["mine"]).TryGetComp<CompRefuelable>().Fuel;
                            bool ok = a.StartsWith("PASS") && Math.Abs(spent - RimMandrakeKineticArmsSettings.kickerFuelPerKick) < 0.01f;
                            return (ok ? "PASS " : "FAIL ") + a.Substring(5) + " fuelSpent=" + spent;
                        };
                        return null;
                    }

                case "kicker_dud_rearm":
                    {
                        var mine = (RM_Building_KickerMine)GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RM_KickerMine")),
                            s.o, Map, Rot4.East);
                        mine.SetFactionDirect(Faction.OfPlayer);
                        CompRefuelable fuel = mine.GetComp<CompRefuelable>();
                        fuel.ConsumeFuel(fuel.Fuel);
                        Pawn dud = Hostile(s, "dud", s.o);
                        mine.Kick(dud);                     // empty: must not kick
                        s.numbers["dudCharged"] = mine.Charged ? 1 : 0;
                        dud.DeSpawn();
                        GenSpawn.Spawn(dud, O(s, 0, -3), Map);
                        s.starts["dud"] = dud.Position;
                        fuel.Refuel(RimMandrakeKineticArmsSettings.kickerFuelPerKick);
                        Pawn p = Hostile(s, "p", s.o);
                        mine.Kick(p);                       // re-armed: must kick east
                        s.things["mine"] = mine;
                        s.verdict = sc =>
                        {
                            string a = AlongAxis(sc, "p", 1, 0, 3, true);
                            int dudLaunch = ForThing(sc, "launch", sc.things["dud"]).Count;
                            bool alive = !((Thing)sc.things["mine"]).Destroyed;
                            bool ok = a.StartsWith("PASS") && dudLaunch == 0 && sc.numbers["dudCharged"] == 0 && alive;
                            return (ok ? "PASS " : "FAIL ") + a.Substring(5) + " dudLaunches=" + dudLaunch + " mineStillThere=" + alive;
                        };
                        return null;
                    }

                case "pulse_push":
                    {
                        var turret = (Building)GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RM_Turret_PulseCannon")), O(s, -5, 0), Map);
                        turret.SetFactionDirect(Faction.OfPlayer);
                        Pawn t = Hostile(s, "p", O(s, 0, 0));
                        var proj = (Projectile)GenSpawn.Spawn(DefDatabase<ThingDef>.GetNamed("RM_Proj_PulseWave"), turret.Position, Map);
                        proj.Launch(turret, turret.DrawPos, t, t, ProjectileHitFlags.IntendedTarget, false, null);
                        s.verdict = sc => AlongAxis(sc, "p", 1, 0, 3, true);
                        return null;
                    }

                case "pulse_charge_gate":
                    {
                        var turret = (RM_Building_PulseCannon)GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RM_Turret_PulseCannon")), O(s, -5, 0), Map);
                        turret.SetFactionDirect(Faction.OfPlayer);
                        Hostile(s, "p", O(s, 2, 0));
                        turret.SetCharge(0f);
                        bool emptyFinds = turret.TryFindNewTarget().IsValid;
                        turret.SetCharge(RM_Building_PulseCannon.Capacity);
                        bool fullFinds = turret.TryFindNewTarget().IsValid;
                        s.verdict = sc => Result(sc, !emptyFinds && fullFinds, "targetWhenEmpty=" + emptyFinds + " targetWhenCharged=" + fullFinds);
                        return null;
                    }

                case "looted_pirates":
                    {
                        // owner 2026-10-06: ruins mostly; rare on pirate raids. Def-level and pick-rule checks, no spawn.
                        s.verdict = sc =>
                        {
                            Func<string, bool> looter = n => RM_Patch_LootedKineticWeapons.IsLooter(
                                Find.FactionManager.FirstFactionOfDef(DefDatabase<FactionDef>.GetNamedSilentFail(n)))
                                || DefDatabase<FactionDef>.GetNamedSilentFail(n)?.GetModExtension<RM_KineticLooterExtension>() != null;
                            Func<string, float, float, string> pick = (k, r1, r2) =>
                                RM_Patch_LootedKineticWeapons.Pick(DefDatabase<PawnKindDef>.GetNamed(k), r1, r2)?.defName ?? "none";
                            bool pirates = looter("Pirate") && looter("CannibalPirate") && looter("PirateYttakin") && looter("PirateWaster");
                            bool campaign = DefDatabase<FactionDef>.GetNamedSilentFail("RUT_Jawa_HuttCartel") == null
                                || (looter("RUT_Jawa_Junkers") && looter("RUT_Jawa_HuttCartel"));
                            bool others = !looter("OutlanderCivil") && !looter("OutlanderRough") && !looter("TribeCivil") && !looter("Empire");
                            string pPirate = pick("Pirate", 0f, 0.99f), pGren = pick("Grenadier_Destructive", 0f, 0.5f),
                                pBoss = pick("PirateBoss", 0f, 0.999f), pMiss = pick("Pirate", 0.5f, 0f);
                            bool ok = pirates && campaign && others && pPirate == "RM_Gun_PalmThumper" && pGren == "RM_Weapon_ThudderGrenade"
                                && pBoss != "RM_Gun_GravRam" && pBoss != "none" && pMiss == "none";
                            return Result(sc, ok, "pirateFactions=" + pirates + " campaignLooters=" + campaign + " otherFactionsClean=" + others + " pirate=" + pPirate
                                + " grenadier=" + pGren + " boss=" + pBoss + " rollMiss=" + pMiss);
                        };
                        return null;
                    }

                case "palm_arrest_wall":
                    {
                        // impactFactor 0 (design §3.1 row 2): shoved into a wall, the palm thumper's target is not hurt by the impact
                        Pawn sh = Colonist(s, "shooter", O(s, -5, 0));
                        Pawn t = Hostile(s, "p", O(s, 0, 0));
                        Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.BlocksGranite);
                        GenSpawn.Spawn(wall, O(s, 2, 0), Map);
                        Fire(sh, "RM_Proj_PalmThump", t, "RM_Gun_PalmThumper");
                        s.verdict = sc =>
                        {
                            string m = Moved(sc, "p", out int dx, out int dz);
                            var b = ForThing(sc, "launch", sc.things["p"]).Concat(ForThing(sc, "blocked", sc.things["p"])).ToList();
                            bool wallStop = b.Count >= 1 && (string)b[0]["stop"] == "Wall" && Convert.ToSingle(b[0]["impact"]) == 0f;
                            int wounds = NewInjuries(sc, "p");
                            return Result(sc, wallStop && wounds == 0 && dx == 1, m + " wallStopNoImpact=" + wallStop + " newInjuries=" + wounds);
                        };
                        return null;
                    }

                case "gravram_big_body":
                    {
                        // immuneBodySizeOverride 3.6: the grav-ram moves a 2.5-3.5 body that the repulsor (global 2.5) cannot
                        PawnKindDef big = DefDatabase<PawnKindDef>.AllDefs.Where(k => k.RaceProps != null && k.RaceProps.Animal && k.RaceProps.IsFlesh
                            && k.RaceProps.baseBodySize >= 2.5f && k.RaceProps.baseBodySize < 3.5f).OrderBy(k => k.RaceProps.baseBodySize).FirstOrDefault();
                        if (big == null)
                        {
                            return "no animal kind with body size 2.5-3.5 on this list";
                        }
                        Pawn sh = Colonist(s, "shooter", O(s, -6, 0));
                        Pawn sh2 = Colonist(s, "shooter2", O(s, -6, 4));
                        Pawn a = Animal(s, "big", big, O(s, 0, 0));
                        Pawn b = Hold(Animal(s, "control", big, O(s, 0, 4)));
                        s.numbers["body"] = a.BodySize;
                        Fire(sh, "RM_Proj_GravRamPulse", a, "RM_Gun_GravRam");
                        Fire(sh2, "RM_Proj_RepulsorBolt", b, "RM_Gun_RepulsorRifle");
                        s.verdict = sc =>
                        {
                            string m = Moved(sc, "big", out int dx, out int dz);
                            bool controlStill = NotThrown(sc, "control", out string mc);
                            bool tooBig = ForThing(sc, "skip", sc.things["control"]).Any(r => (string)r["reason"] == "too_big");
                            return Result(sc, dx >= 1 && controlStill && tooBig, m + "; " + mc + " body=" + sc.numbers["body"].ToString("0.0")
                                + " repulsorTooBig=" + tooBig);
                        };
                        return null;
                    }

                case "ruins_loot":
                    {
                        // owner: found in Ancient Danger ruins. Def wiring + the pick with fixed rolls; nothing spawned.
                        s.verdict = sc =>
                        {
                            ThingSetMakerDef tsm = DefDatabase<ThingSetMakerDef>.GetNamedSilentFail("MapGen_AncientTempleContents");
                            bool wired = tsm?.root is ThingSetMaker_Sum sum && sum.options.Any(o => o.thingSetMaker is RM_ThingSetMaker_KineticRuins);
                            Thing hit = RM_ThingSetMaker_KineticRuins.Make(0f, 0f, 0.5f);
                            Thing miss = RM_ThingSetMaker_KineticRuins.Make(0.99f, 0f, 0.5f);
                            bool was = RimMandrakeKineticArmsSettings.foundInRuins;
                            RimMandrakeKineticArmsSettings.foundInRuins = false;
                            Thing off = RM_ThingSetMaker_KineticRuins.Make(0f, 0f, 0.5f);
                            RimMandrakeKineticArmsSettings.foundInRuins = was;
                            var gen = new List<string>();
                            for (int i = 0; i < 8; i++)
                            {
                                Thing t = RM_ThingSetMaker_KineticRuins.Make(0f, RM_ThingSetMaker_KineticRuins.RollFor(i), 1f);
                                gen.Add(t != null ? t.def.defName + "x" + t.stackCount : "none");
                            }
                            bool all8 = gen.Distinct().Count() == 8 && gen.Contains("RM_Shell_Thumpx12");
                            string[] cx = { "MapGen_AncientComplexRoomLoot_Default", "MapGen_AncientComplexRoomLoot_Better", "MapGen_AncientComplex_SecurityCrate" };
                            bool complexes = cx.All(n => DefDatabase<ThingSetMakerDef>.GetNamedSilentFail(n)?.root is ThingSetMaker_RandomOption ro
                                && ro.options.Any(o => o.thingSetMaker is RM_ThingSetMaker_KineticComplex));
                            wired = wired && complexes;
                            return Result(sc, wired && hit != null && miss == null && off == null && all8, "wired=" + wired + " complexes=" + complexes + " hit=" + (hit?.def.defName ?? "none")
                                + " miss=" + (miss == null) + " offGivesNone=" + (off == null) + " picks=" + string.Join(",", gen));
                        };
                        return null;
                    }

                case "kicker_hidden":
                    {
                        var mine = (RM_Building_KickerMine)GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RM_KickerMine")), s.o, Map, Rot4.East);
                        mine.SetFactionDirect(Faction.OfPlayer);
                        Pawn h = Hostile(s, "h", O(s, -3, 0));
                        bool hiddenKnows = mine.KnowsOfTrap(h);
                        RimMandrakeKineticArmsSettings.kickerHidden = false;
                        bool shownKnows = mine.KnowsOfTrap(h);
                        RimMandrakeKineticArmsSettings.kickerHidden = true;
                        s.verdict = sc => Result(sc, !hiddenKnows && shownKnows, "hiddenRaiderKnows=" + hiddenKnows + " shownRaiderKnows=" + shownKnows);
                        return null;
                    }

                case "cords_marker":
                    {
                        // owner Q3: every kinetic DamageDef carries the marker Gimme Some Slack reads; the setting removes it
                        s.verdict = sc =>
                        {
                            string[] dds = { "RM_Concussive_Thudder", "RM_Concussive_Slam", "RM_Concussive_ThumpShell", "RM_Repulse_Palm",
                                "RM_Repulse_Repulsor", "RM_Repulse_Pulse", "RM_Repulse_GravRam", "RM_Repulse_Kicker" };
                            Func<bool> allMarked = () => dds.All(d => DefDatabase<DamageDef>.GetNamed(d).GetModExtension<RM_KineticBlastExtension>() != null);
                            bool on = allMarked();
                            RimMandrakeKineticArmsSettings.kineticCutsCords = true;
                            RimMandrakeKineticArmsMod.ApplySettings();
                            bool removed = dds.All(d => DefDatabase<DamageDef>.GetNamed(d).GetModExtension<RM_KineticBlastExtension>() == null);
                            RimMandrakeKineticArmsSettings.kineticCutsCords = false;
                            RimMandrakeKineticArmsMod.ApplySettings();
                            bool back = allMarked();
                            bool thumpUnmarked = DefDatabase<DamageDef>.GetNamed("Thump").GetModExtension<RM_KineticBlastExtension>() == null;
                            return Result(sc, on && removed && back && thumpUnmarked, "marked=" + on + " cutSettingRemoves=" + removed + " restored=" + back
                                + " thumpCannonStillCuts=" + thumpUnmarked);
                        };
                        return null;
                    }

                case "ring_fleck":
                    {
                        s.verdict = sc =>
                        {
                            FleckDef f = DefDatabase<FleckDef>.GetNamedSilentFail("RM_Fleck_KineticRing");
                            bool tex = f != null && f.GetGraphicData(0)?.Graphic?.MatSingle?.mainTexture != null
                                && f.GetGraphicData(0).Graphic.MatSingle.mainTexture != BaseContent.BadTex;
                            return Result(sc, tex, "fleck=" + (f != null) + " textureResolves=" + tex);
                        };
                        return null;
                    }

                case "strength_zero":
                    {
                        RimMandrakeKineticArmsSettings.kineticStrength = 0f;
                        RimMandrakeKineticArmsMod.ApplySettings();
                        Pawn sh = Colonist(s, "shooter", O(s, -6, 0));
                        Pawn t = Hold(Hostile(s, "p", O(s, 0, 0)));
                        Fire(sh, "RM_Proj_RepulsorBolt", t, "RM_Gun_RepulsorRifle");
                        s.verdict = sc =>
                        {
                            RimMandrakeKineticArmsSettings.kineticStrength = 1f;
                            RimMandrakeKineticArmsMod.ApplySettings();
                            bool still = NotThrown(sc, "p", out string m);
                            return Result(sc, still, m + " (strength 0: no throw)");
                        };
                        return null;
                    }
            }
            return "unknown scene " + s.name;
        }
    }
}
