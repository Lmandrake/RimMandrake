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
                        Hostile(s, "p", O(s, 1, 0));
                        s.numbers["force"] = RimMandrakeKineticArmsMod.ForceOf("Thump");
                        Fire(sh, "Bullet_ThumpCannon", O(s, 0, 0), "Gun_ThumpCannon");
                        if (s.name == "thump_off")
                        {
                            RimMandrakeKineticArmsSettings.thumpCannonThrows = true;
                            s.verdict = sc =>
                            {
                                RimMandrakeKineticArmsMod.ApplySettings();
                                string m = Moved(sc, "p", out int dx, out int dz);
                                return Result(sc, dx == 0 && dz == 0 && sc.numbers["force"] == 0f, m + " forceWhileOff=" + sc.numbers["force"]);
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
                        Hostile(s, "side", O(s, -1, 1)); // shooter side of the back-step centre: outside the cone
                        Fire(sh, "RM_Proj_PalmThump", t, "RM_Gun_PalmThumper");
                        s.verdict = sc =>
                        {
                            string a = AlongAxis(sc, "p", 1, 0, 2, true);
                            string m = Moved(sc, "side", out int dx, out int dz);
                            bool sideStill = dx == 0 && dz == 0;
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
                            bool others = !looter("OutlanderCivil") && !looter("OutlanderRough") && !looter("TribeCivil") && !looter("Empire");
                            string pPirate = pick("Pirate", 0f, 0.99f), pGren = pick("Grenadier_Destructive", 0f, 0.5f),
                                pBoss = pick("PirateBoss", 0f, 0.999f), pMiss = pick("Pirate", 0.5f, 0f);
                            bool ok = pirates && others && pPirate == "RM_Gun_PalmThumper" && pGren == "RM_Weapon_ThudderGrenade"
                                && pBoss != "RM_Gun_GravRam" && pBoss != "none" && pMiss == "none";
                            return Result(sc, ok, "pirateFactions=" + pirates + " otherFactionsClean=" + others + " pirate=" + pPirate
                                + " grenadier=" + pGren + " boss=" + pBoss + " rollMiss=" + pMiss);
                        };
                        return null;
                    }

                case "strength_zero":
                    {
                        RimMandrakeKineticArmsSettings.kineticStrength = 0f;
                        RimMandrakeKineticArmsMod.ApplySettings();
                        Pawn sh = Colonist(s, "shooter", O(s, -6, 0));
                        Pawn t = Hostile(s, "p", O(s, 0, 0));
                        Fire(sh, "RM_Proj_RepulsorBolt", t, "RM_Gun_RepulsorRifle");
                        s.verdict = sc =>
                        {
                            RimMandrakeKineticArmsSettings.kineticStrength = 1f;
                            RimMandrakeKineticArmsMod.ApplySettings();
                            string m = Moved(sc, "p", out int dx, out int dz);
                            return Result(sc, dx == 0 && dz == 0, m + " (strength 0: no throw)");
                        };
                        return null;
                    }
            }
            return "unknown scene " + s.name;
        }
    }
}
