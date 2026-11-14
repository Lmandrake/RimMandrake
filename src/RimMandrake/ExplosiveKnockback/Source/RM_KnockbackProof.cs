#if RM_PROOFS
// Proof build only (RM_PROOFS, csproj property RmProofs=true): the release DLL carries no proof type or
// bridge entry point. Build: python3 src/RimMandrake/Utils/winbuild.py ExplosiveKnockback -- -p:RmProofs=true
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using HarmonyLib;
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
            "all_fly_no_cap", "settings_off", "emp_no_throw",
            // 2026-10-06 finish pass (KINETIC_BLAST_WEAPONS_1): per-blast config, stun-lock guard, shields. NOT YET RUN LIVE.
            "lookup_projectile", "lookup_zero_wins", "impact_factor", "body_override", "immunity_window", "shield_counter",
            // 2026-11-12 RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD: thrown goods fly in a carrier. NOT YET RUN LIVE.
            "goods_fly_midair", "goods_fly_lands", "goods_fly_wall", "goods_fly_rebound", "goods_fly_off",
            // 2026-11-12 closed containers under a blast they survive; fire at half; unpatched harmful at full.
            "fire_half", "harmful_unpatched",
            // 2026-11-12 round 2: containers thrown whole, heavy goods knock, landings never bump, burning gas clumps.
            "container_thrown", "heavy_knock", "land_no_bump", "land_no_bump_pit", "gas_clumps",
            // 2026-11-13 creature mass limit + blast power (sc_mass_and_power, the showcase): the run at damage 50, the run at
            // 100, and the two control lanes (blastPowerFromDamage off; creatureMassLimit 250). NOT YET RUN LIVE.
            "mass_and_power", "mass_and_power_x2", "mass_and_power_off", "mass_and_power_off_x2", "mass_and_power_250",
            "mass_and_power_250_x2",
        };

        private static Map Map => Find.CurrentMap;

        // ── bridge surface ───────────────────────────────────────────────

        public static string Names(string _)
        {
            return string.Join(",", SceneNames) + " flowworks=" + RM_KnockbackCompat.FlowWorks + " hoses=" + RM_KnockbackCompat.Hoses;
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

        /// <summary>"DefName": reads, never changes, whether a building def is a closed container by the shipped rule
        /// (RM_KnockbackCompat.IsClosedDef, what IsClosedContainer applies). Owner 2026-11-12: "Anything that draws its contents is open", so a
        /// proof stages a container that hides its contents (LWM's Deep Storage locker, a sealed crate); it never tags a
        /// drawing def (a shelf, a hopper) closed. Returns "CLOSED def", "OPEN def" or "REFUSED: ...".</summary>
        public static string IsClosed(string arg)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(arg ?? "");
            if (d == null || d.category != ThingCategory.Building)
            {
                return "REFUSED: no building def " + arg;
            }
            return (RM_KnockbackCompat.IsClosedDef(d) ? "CLOSED " : "OPEN ") + d.defName;
        }

        /// <summary>Planted breaks for the mutation checks, "name=on|off" (or "flameforce=x"): throwcap (re-impose the old
        /// 40-per-explosion cap), directfirst (the old Direct-first landing), nocontentsshield (blast damages goods in a
        /// closed container), gasreg (the Cauldron vent gas registration), flameforce (the Flame DamageDef's force).
        /// "reset" undoes all of them. Not saved.</summary>
        public static string Plant(string arg)
        {
            string[] kv = (arg ?? "").Split('=');
            string k = kv[0];
            bool on = kv.Length == 2 && kv[1] == "on";
            switch (k)
            {
                case "reset":
                    RM_MapComponent_Knockback.ProofThrowCap = 0;
                    RM_MapComponent_Knockback.ProofDirectFirst = false;
                    RM_Patch_DamageWorker_ExplosionKnockback.ProofNoContentsShield = false;
                    RM_KnockbackCompat.VentGasRegistered = RM_KnockbackCompat.VentGasHooked;
                    SetFlameForce(0.5f);
                    return "PLANT reset";
                case "throwcap":
                    RM_MapComponent_Knockback.ProofThrowCap = on ? 40 : 0;
                    break;
                case "directfirst":
                    RM_MapComponent_Knockback.ProofDirectFirst = on;
                    break;
                case "nocontentsshield":
                    RM_Patch_DamageWorker_ExplosionKnockback.ProofNoContentsShield = on;
                    break;
                case "gasreg":
                    RM_KnockbackCompat.VentGasRegistered = on && RM_KnockbackCompat.VentGasHooked;
                    break;
                case "flameforce":
                    if (kv.Length != 2 || !float.TryParse(kv[1], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float f))
                    {
                        return "REFUSED: flameforce=<number>";
                    }
                    SetFlameForce(f);
                    break;
                default:
                    return "REFUSED: no plant " + k;
            }
            return "PLANT " + arg + " throwcap=" + RM_MapComponent_Knockback.ProofThrowCap + " directfirst=" + RM_MapComponent_Knockback.ProofDirectFirst
                + " nocontentsshield=" + RM_Patch_DamageWorker_ExplosionKnockback.ProofNoContentsShield + " gasreg=" + RM_KnockbackCompat.VentGasRegistered
                + " flameforce=" + DamageDefOf.Flame.GetModExtension<RM_KnockbackExtension>()?.force;
        }

        private static void SetFlameForce(float f)
        {
            RM_KnockbackExtension e = DamageDefOf.Flame.GetModExtension<RM_KnockbackExtension>();
            if (e != null)
            {
                e.force = f;
            }
        }

        /// <summary>The Cauldron's vent-gas map component on the current map (reflection: no hard reference), or null.</summary>
        private static MapComponent VentGas(out Type type)
        {
            type = AccessTools.TypeByName("RimMandrake.Cauldron.RM_MapComponent_VentGas");
            if (type == null || Map == null)
            {
                return null;
            }
            foreach (MapComponent mc in Map.components)
            {
                if (mc != null && type.IsInstanceOfType(mc))
                {
                    return mc;
                }
            }
            return null;
        }

        private static float Hp(Thing t) => t.def.useHitPoints ? t.HitPoints : -1f;

        // ── owner look matrices (standing test principle, owner 2026-11-12: one cell prepared, then replicated with
        //    each variable varied, with a readable grid key). Matrix("kind,x,z") clears and builds the whole grid with
        //    its south-west corner at x,z and returns one "row|col|label|x,z|w,h" per cell, ';'-joined. Nothing is fired:
        //    shells wait for a damage hit (fire_matrix.py), gas waits for its fire to burn (unpause). ──

        private static int ShellCount(Thing t) => t.def.defName.StartsWith("Shell_") ? t.stackCount : 0;

        private static Thing Spawn(string def, int count, IntVec3 c, string stuff = null)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamed(def);
            Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? (stuff != null ? DefDatabase<ThingDef>.GetNamed(stuff) : GenStuff.DefaultStuffFor(d)) : null);
            t.stackCount = Math.Min(count, d.stackLimit);
            GenPlace.TryPlaceThing(t, c, Map, ThingPlaceMode.Direct, out Thing placed);
            return placed ?? t;
        }

        private static Pawn Drafted(IntVec3 c)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            p.equipment?.DestroyAllEquipment();
            p.inventory?.DestroyAll();
            GenSpawn.Spawn(p, c, Map);
            if (p.drafter != null)
            {
                p.drafter.Drafted = true;
            }
            return p;
        }

        /// <summary>The radius a stack of n of this shell explodes with (CompExplosive: base plus the per-stack growth).</summary>
        private static float ShellRadius(string def, int n)
        {
            CompProperties_Explosive e = DefDatabase<ThingDef>.GetNamed(def).GetCompProperties<CompProperties_Explosive>();
            if (e == null)
            {
                return 0f;
            }
            float r = e.explosiveRadius;
            if (e.explosiveExpandPerStackcount > 0f)
            {
                r += UnityEngine.Mathf.Sqrt((n - 1) * e.explosiveExpandPerStackcount);
            }
            return UnityEngine.Mathf.Min(r, GenRadial.MaxRadialPatternRadius - 1f);
        }

        public static string Matrix(string arg)
        {
            string[] a = (arg ?? "").Split(',');
            if (a.Length != 3 || !int.TryParse(a[1], out int x0) || !int.TryParse(a[2], out int z0) || Map == null)
            {
                return "REFUSED: kind,x,z";
            }
            var cells = new List<string>();
            try
            {
                switch (a[0])
                {
                    case "container":
                        {
                            // rows: container kind; cols: shells 1|3 x distance 1|2|3. Each cell: HE shells at its centre, the
                            // container d cells east holding 20 steel and 5 medicine, the same goods loose d cells west.
                            var kinds = new List<KeyValuePair<string, string>>();
                            // a modded container that hides what it holds (owner 2026-11-12: "Anything that draws its contents
                            // is open", so Cold Storage's drawing lockers and crock are open and not rows here)
                            if (DefDatabase<ThingDef>.GetNamedSilentFail("LWM_WeaponsLocker") != null)
                            {
                                kinds.Add(new KeyValuePair<string, string>("LWM_WeaponsLocker", null));
                            }
                            // the game's own 1x1 sealed crates, contents in their ThingOwner: Anomaly's unbreakable gray box, and
                            // Odyssey's ancient safe (100 HP: any HE shell in reach destroys it, measured 2026-11-12)
                            foreach (string cd in new[] { "GrayBox", "AncientSafe" })
                            {
                                if (DefDatabase<ThingDef>.GetNamedSilentFail(cd) != null)
                                {
                                    kinds.Add(new KeyValuePair<string, string>(cd, null));
                                }
                            }
                            kinds.Add(new KeyValuePair<string, string>("ShelfSmall", "Plasteel")); // control: an OPEN shelf
                            int[] shells = { 1, 3 };
                            int[] dists = { 1, 2, 3 };
                            const int pitch = 19;
                            for (int r = 0; r < kinds.Count; r++)
                            {
                                for (int ci = 0; ci < shells.Length * dists.Length; ci++)
                                {
                                    int n = shells[ci / dists.Length], d = dists[ci % dists.Length];
                                    var o = new IntVec3(x0 + 9 + ci * pitch, 0, z0 + 9 + r * pitch);
                                    Prepare(o, 9);
                                    Spawn("Shell_HighExplosive", n, o);
                                    Thing box = Build(kinds[r].Key, o + new IntVec3(d, 0, 0), kinds[r].Value);
                                    bool locker = kinds[r].Key == "LWM_WeaponsLocker"; // it accepts weapons only: two guns
                                    var steel = ThingMaker.MakeThing(locker ? DefDatabase<ThingDef>.GetNamed("Gun_Autopistol") : ThingDefOf.Steel);
                                    steel.stackCount = locker ? 1 : 20;
                                    var med = ThingMaker.MakeThing(locker ? DefDatabase<ThingDef>.GetNamed("Gun_Revolver") : ThingDefOf.MedicineIndustrial);
                                    med.stackCount = locker ? 1 : 5;
                                    if (box is IThingHolder h && !(box is Building_Storage) && h.GetDirectlyHeldThings() is ThingOwner inside)
                                    {
                                        inside.TryAdd(steel);
                                        inside.TryAdd(med);
                                    }
                                    else
                                    {
                                        GenPlace.TryPlaceThing(steel, box.Position, Map, ThingPlaceMode.Direct);
                                        GenPlace.TryPlaceThing(med, box.Position, Map, ThingPlaceMode.Direct);
                                    }
                                    Spawn("Steel", 20, o + new IntVec3(-d, 0, 0));
                                    Spawn("MedicineIndustrial", 5, o + new IntVec3(-d, 0, 1));
                                    string label = kinds[r].Key.Replace("LWM_WeaponsLocker", "Deep Storage weapons locker (hides, two guns)")
                                        .Replace("ShelfSmall", "OPEN small shelf (control)").Replace("AncientSafe", "ancient safe (100 HP)").Replace("GrayBox", "gray box (unbreakable)") + " | " + n + " HE | d" + d + " | closed=" + RM_KnockbackCompat.IsClosedContainer(box);
                                    cells.Add(r + "|" + ci + "|" + label + "|" + (o.x - 9) + "," + (o.z - 9) + "|19,19");
                                }
                            }
                            break;
                        }
                    case "heavy":
                        {
                            // rows: the stack (15, 10, 5, 0.26 kg); cols: a drafted colonist 2|3|4 cells beyond the stack on the
                            // throw line, outside the blast. One HE shell at each cell's centre, the stack 1 cell east.
                            string[] defs = { "Steel", "Steel", "Steel", "Cloth" };
                            int[] counts = { 30, 20, 10, 10 };
                            int[] gaps = { 2, 3, 4 };
                            const int pitch = 11;
                            for (int r = 0; r < defs.Length; r++)
                            {
                                for (int ci = 0; ci < gaps.Length; ci++)
                                {
                                    var o = new IntVec3(x0 + 3 + ci * pitch, 0, z0 + 5 + r * pitch);
                                    Prepare(o + new IntVec3(3, 0, 0), 5);
                                    Spawn("Shell_HighExplosive", 1, o);
                                    Thing st = Spawn(defs[r], counts[r], o + new IntVec3(1, 0, 0));
                                    Drafted(o + new IntVec3(1 + gaps[ci], 0, 0));
                                    float kg = st.GetStatValue(StatDefOf.Mass) * st.stackCount;
                                    cells.Add(r + "|" + ci + "|" + counts[r] + " " + defs[r] + " = " + kg.ToString("0.##") + " kg (" + (kg >= RimMandrakeExplosiveKnockbackSettings.heavyGoodsMinMass ? "heavy" : "light")
                                        + ") | person " + gaps[ci] + " beyond|" + (o.x - 2) + "," + (o.z - 3) + "|11,7");
                                }
                            }
                            break;
                        }
                    case "gas":
                        {
                            // rows: cloud density 30|60|120; cols: cloud radius 1|2|3. Each cell: a cloud of the Cauldron's vent gas,
                            // a fire at its centre (it burns on unpause), three steel stacks and a drafted colonist in it, a pit
                            // cell under a woven cover just past its east edge, an open pit cell just past its west edge.
                            MapComponent vg = VentGas(out Type vt);
                            if (vg == null)
                            {
                                return "REFUSED: no Cauldron vent gas on this map";
                            }
                            int[] dens = { 80, 160, 250 };
                            int[] rad = { 1, 2, 3 };
                            const int pitch = 15;
                            for (int r = 0; r < dens.Length; r++)
                            {
                                for (int ci = 0; ci < rad.Length; ci++)
                                {
                                    var o = new IntVec3(x0 + 7 + ci * pitch, 0, z0 + 7 + r * pitch);
                                    Prepare(o, 7);
                                    int R = rad[ci];
                                    vt.GetMethod("SeedCloud").Invoke(null, new object[] { Map, o, R, dens[r] });
                                    Spawn("Steel", 10, o + new IntVec3(1, 0, 0));
                                    Spawn("Steel", 10, o + new IntVec3(-1, 0, 1));
                                    Spawn("Steel", 10, o + new IntVec3(0, 0, -1));
                                    Drafted(o + new IntVec3(Math.Min(R, 1), 0, Math.Min(R, 1)));
                                    if (RM_KnockbackCompat.FlowWorks)
                                    {
                                        RM_KnockbackCompat.DigToSuperdeep(Map, o + new IntVec3(R + 1, 0, 0));
                                        Build("RM_PitCover_ReinforcedFrame", o + new IntVec3(R + 1, 0, 0));
                                        RM_KnockbackCompat.DigToSuperdeep(Map, o + new IntVec3(-R - 1, 0, 0));
                                    }
                                    // fuel under the starter fire: a bare-ground fire can burn out before the Cauldron's scan
                                    // (40 ignitions a scan, map-wide) reaches it (measured: the 9th cell never lit)
                                    Spawn("WoodLog", 10, o);
                                    var fire = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
                                    fire.fireSize = 1f;
                                    GenSpawn.Spawn(fire, o, Map);
                                    cells.Add(r + "|" + ci + "|gas density " + dens[r] + " | radius " + R + "|" + (o.x - 7) + "," + (o.z - 7) + "|15,15");
                                }
                            }
                            break;
                        }
                    case "land":
                        {
                            // rows: what lands (a revolver: stackLimit 1; 10 steel; 5 medicine) onto 10 resident wood; cols: the
                            // landing cell is bare ground | the first cell of a superdeep pit | a full small shelf (3 stacks).
                            // One HE shell, the lander 1 cell east; the landing cell from the kernel at the shell's radius.
                            string[] defs = { "Gun_Revolver", "Steel", "MedicineIndustrial" };
                            int[] counts = { 1, 10, 5 };
                            // goods never come to rest on a shelf cell (Fillage partial), so the third column is a resident of
                            // the SAME kind: a stack merges into it, a revolver (stackLimit 1) cannot and lands beside
                            string[] spots = { "ground", "pit", "same kind" };
                            const int pitch = 13;
                            float radius = ShellRadius("Shell_HighExplosive", 1);
                            KbSettings k = RimMandrakeExplosiveKnockbackSettings.Kernel();
                            for (int r = 0; r < defs.Length; r++)
                            {
                                for (int ci = 0; ci < spots.Length; ci++)
                                {
                                    var o = new IntVec3(x0 + 3 + ci * pitch, 0, z0 + 6 + r * pitch);
                                    Prepare(o + new IntVec3(4, 0, 0), 6);
                                    Spawn("Shell_HighExplosive", 1, o);
                                    Thing t = Spawn(defs[r], counts[r], o + new IntVec3(1, 0, 0));
                                    float mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount;
                                    int cellsN = RM_KnockbackMath.ThrowCells(1f, radius, 1f, mass, k);
                                    IntVec3 land = o + new IntVec3(1 + Math.Max(1, cellsN), 0, 0);
                                    if (spots[ci] == "pit")
                                    {
                                        land = o + new IntVec3(Math.Min(1 + cellsN, 3), 0, 0);
                                        foreach (IntVec3 c in new CellRect(land.x, land.z - 1, 3, 3))
                                        {
                                            RM_KnockbackCompat.DigToSuperdeep(Map, c);
                                        }
                                        Spawn("WoodLog", 10, land);
                                    }
                                    else if (spots[ci] == "same kind")
                                    {
                                        Spawn(defs[r], counts[r], land);
                                    }
                                    else
                                    {
                                        Spawn("WoodLog", 10, land);
                                    }
                                    cells.Add(r + "|" + ci + "|" + counts[r] + " " + defs[r] + " onto " + spots[ci] + " (resident " + (spots[ci] == "same kind" ? defs[r] : "wood") + " at " + (land.x - o.x) + " east)|" + (o.x - 2) + "," + (o.z - 3) + "|13,7");
                                }
                            }
                            break;
                        }
                    default:
                        return "REFUSED: no matrix " + a[0];
                }
            }
            catch (Exception ex)
            {
                return "ERROR " + ex.GetType().Name + ": " + ex.Message + " after " + cells.Count + " cells";
            }
            return string.Join(";", cells);
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
            // a re-stage of a scene whose Verdict never ran: undo what it changed (a def extension, a setting) first
            if (scenes.TryGetValue(a[0], out Scene pending))
            {
                RunRestore(pending);
            }
            var s = new Scene { name = a[0], o = new IntVec3(x, 0, z), stagedTick = Find.TickManager.TicksGame };
            try
            {
                Prepare(s.o, 7);
                string why = Build(s);
                if (why != null)
                {
                    RunRestore(s);
                    return "INVALID " + s.name + " " + why;
                }
            }
            catch (Exception ex)
            {
                // Build may already have added an extension to a vanilla def or poked a setting: never leave it behind
                RunRestore(s);
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
                RunRestore(s);
            }
        }

        /// <summary>Runs a scene's restore once; a second call (re-stage, repeated Verdict) is a no-op.</summary>
        private static void RunRestore(Scene s)
        {
            Action r = s.restore;
            s.restore = null;
            r?.Invoke();
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
                RM_KnockbackCompat.FillToSurface(map, c); // a pit left by an earlier scene at this origin
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
            Boom(Map, c, radius, dt, dmg);
        }

        /// <summary>Stages one explosion through the game's own call. realPower false (every scene before 2026-11-13): the
        /// blast harms at dmg but pushes as a blast at its type's reference damage (ratio 1), so those scenes keep the
        /// numbers they were written for. realPower true: the push reads the explosion's own damage, as in play.</summary>
        private static Explosion Boom(Map m, IntVec3 c, float radius, DamageDef dt, int dmg, ThingDef proj = null, bool realPower = false)
        {
            dt = dt ?? DamageDefOf.Bomb;
            GenExplosion.DoExplosion(c, m, radius, dt, null, dmg, -1f, null, null, proj);
            // StartExplosion damages nothing (cells are hit from the next tick on), so registering after the call is in time
            Explosion e = m.thingGrid.ThingsListAt(c).OfType<Explosion>().OrderByDescending(x => x.thingIDNumber).FirstOrDefault();
            if (e != null && !realPower)
            {
                RM_Patch_DamageWorker_ExplosionKnockback.ProofPowerDamage[e.thingIDNumber] =
                    RM_Patch_DamageWorker_ExplosionKnockback.RefDamageOf(dt) * RimMandrakeExplosiveKnockbackSettings.blastPowerRefPercent / 100f;
            }
            return e;
        }

        /// <summary>Proof build only: things whose damage is absorbed whole (sc_mass_and_power stages a real 50 / 100 damage
        /// blast beside a 12 kg rat; the throw must be read, not the kill). Cleared by the scene's restore.</summary>
        internal static readonly HashSet<int> NoHarm = new HashSet<int>();

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

        // ── flying goods (RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD) ─────────

        /// <summary>The knockback carrier holding t on this map, or null.</summary>
        private static RM_ThingFlyer_Knockback CarrierOf(Map map, Thing t)
        {
            foreach (Thing f in map.listerThings.ThingsOfDef(RM_KnockbackDefOf.RM_ThingFlyer_Knockback))
            {
                if (f is RM_ThingFlyer_Knockback k && k.Inner == t)
                {
                    return k;
                }
            }
            return null;
        }

        /// <summary>Looks for s.things[key] inside a carrier on each tick stagedTick+from..to; the first sighting writes
        /// key_airTick, key_airCount, key_airDestX/Z, key_airTicksLeft. A stale action after a reload sees another map
        /// and does nothing.</summary>
        private static void SampleFlight(Scene s, string key, int from, int to)
        {
            Map m0 = Map;
            Thing t = s.things[key];
            for (int d = from; d <= to; d++)
            {
                int dd = d;
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + d, () =>
                {
                    if (m0 != Find.CurrentMap || s.numbers.ContainsKey(key + "_airTick"))
                    {
                        return;
                    }
                    RM_ThingFlyer_Knockback c = CarrierOf(m0, t);
                    if (c != null && c.Spawned && !t.Spawned)
                    {
                        s.numbers[key + "_airTick"] = dd;
                        s.numbers[key + "_airCount"] = t.stackCount;
                        s.numbers[key + "_airDestX"] = c.DestCell.x;
                        s.numbers[key + "_airDestZ"] = c.DestCell.z;
                        s.numbers[key + "_airTicksLeft"] = c.TicksLeft;
                    }
                }));
            }
        }

        /// <summary>Bridge read, also after a reload (no scene state): every carrier on the current map as
        /// "id inner=def xN innerId=n at=x,z dest=x,z left=ticks bounces=n", one per line; "NONE" when there is none.</summary>
        public static string Flights(string _)
        {
            if (Map == null)
            {
                return "NONE no map";
            }
            var l = new List<string>();
            foreach (Thing f in Map.listerThings.ThingsOfDef(RM_KnockbackDefOf.RM_ThingFlyer_Knockback))
            {
                if (f is RM_ThingFlyer_Knockback k)
                {
                    Thing i = k.Inner;
                    l.Add(k.ThingID + " inner=" + (i?.def.defName ?? "none") + " x" + (i?.stackCount ?? 0) + " innerId=" + (i?.ThingID ?? "none")
                          + " at=" + k.Position.x + "," + k.Position.z + " dest=" + k.DestCell.x + "," + k.DestCell.z
                          + " left=" + k.TicksLeft + " bounces=" + k.Bounces);
                }
            }
            return l.Count == 0 ? "NONE" : string.Join("\n", l);
        }

        /// <summary>Restore flyingGoods, goodsFlightSpeed and goodsRebound when the scene ends (the caller assigns it to s.restore before any poke).</summary>
        private static Action FlightRestore(Scene s)
        {
            bool fg = RimMandrakeExplosiveKnockbackSettings.flyingGoods;
            float sp = RimMandrakeExplosiveKnockbackSettings.goodsFlightSpeed;
            bool rb = RimMandrakeExplosiveKnockbackSettings.goodsRebound;
            Action prev = s.restore;
            return () =>
            {
                RimMandrakeExplosiveKnockbackSettings.flyingGoods = fg;
                RimMandrakeExplosiveKnockbackSettings.goodsFlightSpeed = sp;
                RimMandrakeExplosiveKnockbackSettings.goodsRebound = rb;
                prev?.Invoke();
            };
        }

        /// <summary>The cells the kernel throws s.things[key] from a blast at s.o of radius r (0 when too heavy).</summary>
        private static int WantCells(Scene s, string key, float r)
        {
            KbSettings k = RimMandrakeExplosiveKnockbackSettings.Kernel();
            Thing t = s.things[key];
            float mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount;
            return mass > k.lightMassLimit ? 0 : RM_KnockbackMath.ThrowCells((s.starts[key] - s.o).LengthHorizontal, r, 1f, mass, k);
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
                    Boom(Map, s.o, 2.9f, DamageDefOf.Bomb, 9999);
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
                        // owner ruling 2026-11-11: open storage protects nothing; the old rule only behind its toggle
                        bool keep = RimMandrakeExplosiveKnockbackSettings.openStorageProtectsGoods;
                        return Result(sc, keep ? cells == 0 : cells > 0,
                            m + (keep ? " (openStorageProtectsGoods: must stay)" : " (on an open shelf: must move)"));
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
                        var skip = ForThing(sc, "skip", t).Where(r => (string)r["reason"] == "too_heavy_creature").ToList();
                        return Result(sc, skip.Count == 1 && ForThing(sc, "launch", t).Count == 0, m + " skips(too_heavy_creature)=" + skip.Count
                            + (skip.Count > 0 ? " [" + Rec(skip[0]) + "]" : ""));
                    };
                    return null;

                case "all_fly_no_cap":
                    {
                        // RIMMANDRAKE_LIFT_KNOCKBACK_THROW_CAPS_PLAN_SAYS_GONE (owner 2026-11-12, "No caps please."): a 5.9 blast
                        // over 10 colonists and 80 light stacks. The old caps were 40 throws an explosion and 60 item
                        // throws a tick; with them gone every request is executed in the one tick the wave lands.
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
                        foreach (IntVec3 c in GenRadial.RadialCellsAround(s.o, 5.5f, true))
                        {
                            if (n < 80 && c.GetFirstPawn(Map) == null)
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
                        int requests = Recs(sc, "request").Count(r => (int)r["exp"] == exp);
                        int launches = Recs(sc, "launch").Count(r => (int)r["exp"] == exp);
                        var moves = Recs(sc, "item_move").Where(r => (int)r["exp"] == exp).ToList();
                        int maxTick = moves.GroupBy(r => (int)r["tick"]).Select(g => g.Count()).DefaultIfEmpty(0).Max();
                        int capped = Recs(sc, "skip").Count(r => (int)r["exp"] == exp && ((string)r["reason"]).StartsWith("cap_"));
                        // every request ends in exactly one outcome line: a launch, an item move, a blocked line or a skip
                        int outcomes = launches + moves.Count + Recs(sc, "blocked").Count(r => (int)r["exp"] == exp)
                            + Recs(sc, "skip").Count(r => (int)r["exp"] == exp);
                        // row no_cap: fails alone when any cap drops a throw (planted: Plant throwcap=on)
                        bool noCap = capped == 0 && launches + moves.Count > 40;
                        // row all_fly: fails alone when a light stack the wave reaches is left lying (the kernel says it
                        // moves a cell or more, from its start) - every one of them flies
                        int want = 0;
                        for (int k = 0; k < (int)sc.numbers["items"]; k++)
                        {
                            want += WantCells(sc, "i" + k, 5.9f) > 0 ? 1 : 0;
                        }
                        bool allFly = moves.Count >= want && want > 40;
                        bool whole = outcomes == requests;
                        sc.numbers["want"] = want;
                        return Result(sc, noCap && allFly && whole, "no_cap=" + noCap + " all_fly=" + allFly + " every_request_answered=" + whole
                            + " kernelSaysMove=" + want
                            + " requests=" + requests + " launches=" + launches + " itemMoves=" + moves.Count + " maxMovesInOneTick=" + maxTick
                            + " cappedSkips=" + capped + " pawns=" + sc.numbers["pawns"] + " items=" + sc.numbers["items"]);
                    };
                    return null;

                case "settings_off":
                    Colonist(s, "p", O(s, 1, 0));
                    Item(s, "steel", "Steel", 10, O(s, -1, 0));
                    {
                        bool wasEnabled = RimMandrakeExplosiveKnockbackSettings.enabled;
                        s.restore = () => RimMandrakeExplosiveKnockbackSettings.enabled = wasEnabled;
                    }
                    RimMandrakeExplosiveKnockbackSettings.enabled = false;
                    Blast(s.o, 2.9f);
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
                    Boom(Map, s.o, 2.9f, DamageDefOf.Bomb, 1, proj);
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
                    Boom(Map, s.o, 2.9f, DamageDefOf.Bomb, 1, proj);
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
                    // a living animal heavier than the global 150 kg and at most 216 (a rhino, 180): spared by the global creature
                    // mass limit, thrown under a creatureMassLimitOverride of 216 (the grav-ram's)
                    PawnKindDef big = DefDatabase<PawnKindDef>.AllDefs.Where(k => k.RaceProps != null && k.RaceProps.Animal
                        && k.RaceProps.baseBodySize * 60f > 160f && k.RaceProps.baseBodySize * 60f < 205f && k.RaceProps.IsFlesh
                        && k.RaceProps.lifeStageAges.Count > 0).OrderBy(k => k.RaceProps.baseBodySize).FirstOrDefault();
                    if (big == null)
                    {
                        return "no flesh animal kind of 160-205 kg (60 x body size) on this list";
                    }
                    ThingDef proj = DefDatabase<ThingDef>.GetNamed("Bullet_Revolver");
                    AddExt(s, proj, new RM_KnockbackExtension { force = 4f, maxThrowCells = 10, creatureMassLimitOverride = 216f });
                    Pawn a = Adult(big);
                    GenSpawn.Spawn(a, O(s, 1, 0), Map);
                    Track(s, "big", a);
                    Pawn b = Adult(big);
                    GenSpawn.Spawn(b, O(s, -1, 3), Map);
                    Track(s, "control", b);
                    s.numbers["mass"] = a.GetStatValue(StatDefOf.Mass) - MassUtility.InventoryMass(a);
                    if (s.numbers["mass"] <= 150f || s.numbers["mass"] > 216f)
                    {
                        return big.defName + " weighs " + s.numbers["mass"].ToString("0") + " kg, not 150-216";
                    }
                    Boom(Map, s.o, 2.9f, DamageDefOf.Bomb, 1, proj);
                    Boom(Map, O(s, -1, 4), 1.5f, DamageDefOf.Bomb, 1); // control: Bomb, the global 150 kg holds
                    s.verdict = sc =>
                    {
                        // Verdict from the JOURNAL, not displacement: both are live animals that walk or flee after a blast,
                        // so "moved N cells" cannot tell a throw from a walk (bridge5 2026-10-09: the control logged a
                        // too_big skip AND moved 5 cells, in a direction no blast could have thrown it).
                        string m = Moved(sc, "big", out Thing t, out int cells);
                        string mc = Moved(sc, "control", out Thing tc, out int cc);
                        int bigLaunch = ForThing(sc, "launch", t).Count;
                        int ctrlLaunch = ForThing(sc, "launch", tc).Count;
                        bool ctrlSkip = ForThing(sc, "skip", tc).Any(r => (string)r["reason"] == "too_heavy_creature");
                        return Result(sc, bigLaunch == 1 && ctrlLaunch == 0 && ctrlSkip, m + "; " + mc + " mass=" + sc.numbers["mass"].ToString("0")
                            + " bigLaunches=" + bigLaunch + " controlLaunches=" + ctrlLaunch + " controlTooHeavy=" + ctrlSkip);
                    };
                    return null;
                }

                case "immunity_window":
                {
                    int was = RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks;
                    s.restore = () => RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks = was;
                    RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks = 600;
                    Pawn p = Colonist(s, "p", O(s, -3, 0));
                    Blast(O(s, -4, 0), 2.9f); // throws p east ~3 cells, toward the origin
                    Map m0 = Map;
                    // a second blast 250 ticks later beside wherever p landed: still inside stun + 600, so "immune"
                    RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + 250, () =>
                    {
                        if (p.Spawned)
                        {
                            Boom(m0, p.Position + IntVec3.West, 2.9f, DamageDefOf.Bomb, 1);
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
                    // A freshly made belt starts at energy 0 (CompShield.energy's field default; it only charges by
                    // CompTick), so the throw counter had nothing to drain (bridge5 2026-10-09: energy 0->0). Charge it.
                    if (sh != null)
                    {
                        AccessTools.FieldRefAccess<CompShield, float>("energy")(sh) = belt.GetStatValue(StatDefOf.EnergyShieldEnergyMax);
                    }
                    s.numbers["energy0"] = sh?.Energy ?? -1f;
                    s.things["belt"] = belt;
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var sk = ForThing(sc, "skip", t).Where(r => (string)r["reason"] == "shield").ToList();
                        CompShield shc = ((Apparel)sc.things["belt"]).GetComp<CompShield>();
                        float e1 = shc?.Energy ?? -1f;
                        // drained BY THE COUNTER: its own record, not the belt total (vanilla's damage absorption drains it too)
                        bool drained = sc.numbers["energy0"] > 0f && sk.Count == 1
                            && (Convert.ToSingle(sk[0]["energyAfter"]) < Convert.ToSingle(sk[0]["energyBefore"]) || Convert.ToBoolean(sk[0]["broke"]));
                        return Result(sc, cells == 0 && sk.Count == 1 && drained, m + " energy " + sc.numbers["energy0"].ToString("0.###")
                            + "->" + e1.ToString("0.###") + (sk.Count > 0 ? " [" + Rec(sk[0]) + "]" : " no shield skip"));
                    };
                    return null;
                }

                case "goods_fly_midair":
                case "goods_fly_lands":
                {
                    // midair: the stack is inside a carrier, unspawned, count intact, a few ticks after the blast.
                    // lands: it ends spawned on the cell the instant move would pick (ThrowCells), count intact, no carrier
                    // left, one item_move flying=true and one item_land. Slow speed so the flight spans the sampling ticks.
                    s.restore = FlightRestore(s);
                    RimMandrakeExplosiveKnockbackSettings.flyingGoods = true;
                    RimMandrakeExplosiveKnockbackSettings.goodsFlightSpeed = 6f;
                    Item(s, "steel", "Steel", 75, O(s, 1, 0));
                    s.numbers["want"] = WantCells(s, "steel", 2.9f);
                    SampleFlight(s, "steel", 1, 30);
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        Thing t = sc.things["steel"];
                        int want = (int)sc.numbers["want"];
                        if (want < 1)
                        {
                            return "INVALID " + sc.name + " steel would not be thrown (want=0): the scene proves nothing";
                        }
                        if (sc.name == "goods_fly_midair")
                        {
                            bool seen = sc.numbers.TryGetValue("steel_airTick", out float at);
                            bool count = seen && (int)sc.numbers["steel_airCount"] == 75;
                            return Result(sc, seen && count, seen
                                ? "in carrier at +" + at + " ticks, count=" + sc.numbers["steel_airCount"] + " dest=" + sc.numbers["steel_airDestX"] + ","
                                  + sc.numbers["steel_airDestZ"] + " ticksLeft=" + sc.numbers["steel_airTicksLeft"]
                                : "never seen inside a carrier on ticks +1..+30");
                        }
                        string m = Moved(sc, "steel", out Thing tt, out int cells);
                        var mv = ForThing(sc, "item_move", t);
                        var land = ForThing(sc, "item_land", t);
                        bool flew = mv.Count == 1 && Equals(mv[0]["flying"], true);
                        bool landed = land.Count == 1 && tt.Spawned && Convert.ToInt32(land[0]["count"]) == 75;
                        bool none = CarrierOf(tt.MapHeld ?? Map, t) == null;
                        bool ok = flew && landed && none && tt.Spawned && cells == want && tt.stackCount == 75;
                        return Result(sc, ok, m + " want=" + want + " count=" + tt.stackCount + " flying=" + flew + " item_land=" + land.Count
                                              + " carrierLeft=" + !none + (land.Count > 0 ? " [" + Rec(land[0]) + "]" : ""));
                    };
                    return null;
                }

                case "goods_fly_wall":
                {
                    // the flight is cut short by a wall: rebound off, so the stack lands beside the wall and the wall impact
                    // (goods_impact stop=Wall, damage>0) applies to it there, exactly as the instant move does today
                    s.restore = FlightRestore(s);
                    RimMandrakeExplosiveKnockbackSettings.flyingGoods = true;
                    RimMandrakeExplosiveKnockbackSettings.goodsRebound = false;
                    Item(s, "comp", "ComponentIndustrial", 1, O(s, 1, 0));
                    Build("Wall", O(s, 3, 0), "BlocksGranite");
                    s.numbers["want"] = WantCells(s, "comp", 2.9f);
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        Thing t = sc.things["comp"];
                        int want = (int)sc.numbers["want"];
                        if (want < 2)
                        {
                            return "INVALID " + sc.name + " component planned " + want + " cells: does not reach the wall";
                        }
                        string m = Moved(sc, "comp", out Thing tt, out int cells);
                        var imp = ForThing(sc, "goods_impact", t);
                        bool hit = imp.Count == 1 && (string)imp[0]["stop"] == "Wall" && Convert.ToSingle(imp[0]["damage"]) > 0f;
                        // the impact may break the component: then it is gone at the wall, which is still the cut-short rule
                        bool beside = tt.Spawned ? tt.Position == O(sc, 2, 0) : imp.Count == 1 && Equals(imp[0]["destroyed"], true);
                        bool flew = ForThing(sc, "item_move", t).Any(r => Equals(r["flying"], true));
                        return Result(sc, hit && beside && flew, m + " want=" + want + " flying=" + flew
                                                                   + (imp.Count > 0 ? " [" + Rec(imp[0]) + "]" : " no goods_impact"));
                    };
                    return null;
                }

                case "goods_fly_rebound":
                {
                    // rebound on: the cut-short flight bounces back off the wall with about goodsReboundKeepPercent of the
                    // cells it had left; the impact applies at the bounce, the stack ends west of the wall, no carrier left
                    s.restore = FlightRestore(s);
                    RimMandrakeExplosiveKnockbackSettings.flyingGoods = true;
                    RimMandrakeExplosiveKnockbackSettings.goodsRebound = true;
                    Item(s, "comp", "ComponentIndustrial", 1, O(s, 1, 0));
                    Build("Wall", O(s, 3, 0), "BlocksGranite");
                    s.numbers["want"] = WantCells(s, "comp", 2.9f);
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        Thing t = sc.things["comp"];
                        int want = (int)sc.numbers["want"];
                        int left = want - 1;                       // one cell to O(2,0), the rest is cut short
                        int back = RM_KnockbackMath.ReboundCells(left, RimMandrakeExplosiveKnockbackSettings.goodsReboundKeepPercent);
                        if (back < 1)
                        {
                            return "INVALID " + sc.name + " planned " + want + " cells leaves no rebound (back=" + back + ")";
                        }
                        string m = Moved(sc, "comp", out Thing tt, out int cells);
                        var rb = ForThing(sc, "item_rebound", t);
                        var imp = ForThing(sc, "goods_impact", t);
                        bool bounced = rb.Count >= 1 && (string)rb[0]["hit"] == "Wall";
                        bool atRebound = imp.Any(r => (string)r["at"] == "rebound");
                        bool west = tt.Spawned && tt.Position.x < O(sc, 2, 0).x;
                        bool none = !tt.Spawned || CarrierOf(tt.Map, t) == null;
                        return Result(sc, bounced && atRebound && west && none, m + " want=" + want + " back=" + back + " rebounds=" + rb.Count
                                                                               + " impactAtRebound=" + atRebound + (rb.Count > 0 ? " [" + Rec(rb[0]) + "]" : ""));
                    };
                    return null;
                }

                case "goods_fly_off":
                {
                    // control: flyingGoods off -> today's instant move (item_move flying=false, never inside a carrier),
                    // same cell and count as a flight would land on
                    s.restore = FlightRestore(s);
                    RimMandrakeExplosiveKnockbackSettings.flyingGoods = false;
                    Item(s, "steel", "Steel", 75, O(s, 1, 0));
                    s.numbers["want"] = WantCells(s, "steel", 2.9f);
                    SampleFlight(s, "steel", 1, 30);
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        Thing t = sc.things["steel"];
                        int want = (int)sc.numbers["want"];
                        if (want < 1)
                        {
                            return "INVALID " + sc.name + " steel would not be thrown (want=0)";
                        }
                        string m = Moved(sc, "steel", out Thing tt, out int cells);
                        var mv = ForThing(sc, "item_move", t);
                        bool instant = mv.Count == 1 && Equals(mv[0]["flying"], false);
                        bool neverAir = !sc.numbers.ContainsKey("steel_airTick");
                        bool ok = instant && neverAir && tt.Spawned && cells == want && tt.stackCount == 75
                                  && ForThing(sc, "item_land", t).Count == 0;
                        return Result(sc, ok, m + " want=" + want + " instant=" + instant + " seenInCarrier=" + !neverAir);
                    };
                    return null;
                }

                case "fire_half":
                    // RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS: Flame (incendiary) throws at half a Bomb's force. Control: a Bomb
                    // 5 cells north, same radius and offset. Fails alone when the Flame patch is not 0.5.
                    Colonist(s, "p", O(s, 1, 0));
                    Colonist(s, "q", O(s, 1, 5));
                    Blast(s.o, 2.9f, DamageDefOf.Flame, 1);
                    Blast(O(s, 0, 5), 2.9f);
                    s.verdict = sc =>
                    {
                        var rq = ForThing(sc, "request", sc.things["q"]);
                        var rp = ForThing(sc, "request", sc.things["p"]);
                        if (rq.Count != 1)
                        {
                            return "INVALID " + sc.name + " Bomb control made " + rq.Count + " requests";
                        }
                        float fq = Convert.ToSingle(rq[0]["force"]);
                        float fp = rp.Count == 1 ? Convert.ToSingle(rp[0]["force"]) : -1f;
                        Moved(sc, "p", out Thing _, out int cp);
                        Moved(sc, "q", out Thing _, out int cq);
                        bool ok = rp.Count == 1 && Math.Abs(fp - 0.5f * fq) < 0.01f && (string)rp[0]["damType"] == "Flame" && cp <= cq;
                        return Result(sc, ok, "flameForce=" + fp + " bombForce=" + fq + " flameCells=" + cp + " bombCells=" + cq);
                    };
                    return null;

                case "harmful_unpatched":
                    {
                        // a damaging DamageDef this mod does not patch (vanilla Thump) throws at unpatchedHarmfulPercent,
                        // default 100. Control: a Bomb 5 cells south. Fails alone when the default is not 100.
                        DamageDef thump = DefDatabase<DamageDef>.GetNamedSilentFail("Thump");
                        if (thump == null || thump.GetModExtension<RM_KnockbackExtension>() != null || !thump.harmsHealth)
                        {
                            return "Thump absent, patched or harmless: not an unpatched harmful blast";
                        }
                        Colonist(s, "p", O(s, 1, 0));
                        Colonist(s, "q", O(s, 1, -5));
                        Blast(s.o, 2.9f, thump, 1);
                        Blast(O(s, 0, -5), 2.9f);
                    }
                    s.verdict = sc =>
                    {
                        var rq = ForThing(sc, "request", sc.things["q"]);
                        var rp = ForThing(sc, "request", sc.things["p"]);
                        if (rq.Count != 1)
                        {
                            return "INVALID " + sc.name + " Bomb control made " + rq.Count + " requests";
                        }
                        float fq = Convert.ToSingle(rq[0]["force"]);
                        float fp = rp.Count == 1 ? Convert.ToSingle(rp[0]["force"]) : -1f;
                        Moved(sc, "p", out Thing _, out int cp);
                        Moved(sc, "q", out Thing _, out int cq);
                        bool ok = rp.Count == 1 && (string)rp[0]["source"] == "unpatched" && Math.Abs(fp - fq) < 0.01f && cp == cq;
                        return Result(sc, ok, "thumpForce=" + fp + " source=" + (rp.Count == 1 ? rp[0]["source"] : "none") + " bombForce=" + fq
                            + " thumpCells=" + cp + " bombCells=" + cq + " unpatchedHarmfulPercent=" + RimMandrakeExplosiveKnockbackSettings.unpatchedHarmfulPercent);
                    };
                    return null;

                case "container_thrown":
                    {
                        // RIMMANDRAKE_THROW_CLOSED_CRATES_WHOLE_CONTENTS_RIDE_SAFE: a closed container, LWM's Deep Storage weapons
                        // locker (1x1, 8 kg, showContents false: it hides what it holds, so closed with no tag; owner 2026-11-12,
                        // "Anything that draws its contents is open"), holding two guns its filter accepts, a Bomb of 30 at
                        // distance 1. Control: the same two guns loose on open ground. No hiding container loaded: refused,
                        // never a drawing def tagged closed.
                        const string def = "LWM_WeaponsLocker";
                        if (DefDatabase<ThingDef>.GetNamedSilentFail(def) == null)
                        {
                            return def + " not loaded: add LWM's Deep Storage (lwm.deepstorage) to the list";
                        }
                        Thing box = Build(def, O(s, 1, 0));
                        Track(s, "box", box);
                        Item(s, "pistol", "Gun_Autopistol", 1, box.Position);
                        Item(s, "revolver", "Gun_Revolver", 1, box.Position);
                        Item(s, "looseRevolver", "Gun_Revolver", 1, O(s, -1, 0));
                        Item(s, "loosePistol", "Gun_Autopistol", 1, O(s, 0, -1));
                        s.numbers["revolverHp"] = Hp(s.things["revolver"]);
                        s.numbers["looseRevolverHp"] = Hp(s.things["looseRevolver"]);
                        if (!RM_KnockbackCompat.IsClosedContainer(box))
                        {
                            return def + " is not a closed container";
                        }
                    }
                    Blast(s.o, 2.9f, DamageDefOf.Bomb, 30);
                    s.verdict = sc =>
                    {
                        Thing box = sc.things["box"], st = sc.things["pistol"], med = sc.things["revolver"], lm = sc.things["looseRevolver"];
                        string ms = Moved(sc, "loosePistol", out Thing _, out int looseCells);
                        if (looseCells < 1 || lm.Destroyed || Hp(lm) >= sc.numbers["looseRevolverHp"])
                        {
                            return "INVALID " + sc.name + " control: loose goods did not move or were not hurt: " + ms + " looseRevolverHp=" + (lm.Destroyed ? -1 : Hp(lm));
                        }
                        var c = ForThing(sc, "container", box);
                        int boxCells = box.Spawned ? Cheb(box.Position, sc.starts["box"]) : -1;
                        // row thrown: fails alone when the container stays put (planted: shoveClosedContainers off)
                        bool thrown = !box.Destroyed && box.Spawned && boxCells >= 1 && c.Count == 1 && (string)c[0]["action"] == "thrown";
                        // row together: fails alone when the goods are left behind or scattered apart from it
                        bool together = st.Spawned && med.Spawned && box.Spawned && st.Position == box.Position && med.Position == box.Position
                            && ForThing(sc, "item_move", st).Count == 0 && ForThing(sc, "item_move", med).Count == 0;
                        // row shorter: fails alone when the container flies as far as the same goods loose (mass ignored)
                        bool shorter = boxCells >= 1 && boxCells < looseCells;
                        // row shielded: fails alone when blast damage reaches goods inside (planted: Plant nocontentsshield=on)
                        bool shielded = !med.Destroyed && Hp(med) == sc.numbers["revolverHp"];
                        return Result(sc, thrown && together && shorter && shielded, "thrown=" + thrown + " together=" + together + " shorter=" + shorter
                            + " shielded=" + shielded + " box=" + box.def.defName + " boxCells=" + boxCells + " looseCells=" + looseCells
                            + " revolverHp=" + (med.Destroyed ? -1 : Hp(med)) + "/" + sc.numbers["revolverHp"] + " looseRevolverHp=" + Hp(lm) + "/" + sc.numbers["looseRevolverHp"]
                            + (c.Count > 0 ? " [" + Rec(c[0]) + "]" : " no container line"));
                    };
                    return null;

                case "heavy_knock":
                    {
                        // RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS: 30 steel (15 kg) thrown east past a colonist standing outside
                        // the blast; 10 cloth (light) thrown west past another. Shared blast, mirrored geometry.
                        Item(s, "heavy", "Steel", 30, O(s, 1, 0));
                        Item(s, "light", "Cloth", 10, O(s, -1, 0));
                        Colonist(s, "ph", O(s, 4, 0));
                        Colonist(s, "pl", O(s, -4, 0));
                        if (WantCells(s, "heavy", 2.9f) < 4 || WantCells(s, "light", 2.9f) < 4)
                        {
                            return "throws too short to reach the colonists: heavy=" + WantCells(s, "heavy", 2.9f) + " light=" + WantCells(s, "light", 2.9f);
                        }
                        s.numbers["phHp"] = ((Pawn)s.things["ph"]).health.summaryHealth.SummaryHealthPercent;
                        s.numbers["plHp"] = ((Pawn)s.things["pl"]).health.summaryHealth.SummaryHealthPercent;
                        s.numbers["heavyMass"] = s.things["heavy"].GetStatValue(StatDefOf.Mass) * 30;
                    }
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        Thing heavy = sc.things["heavy"], light = sc.things["light"];
                        Pawn ph = (Pawn)sc.things["ph"], pl = (Pawn)sc.things["pl"];
                        var hh = ForThing(sc, "heavy_hit", heavy);
                        var lh = ForThing(sc, "heavy_hit", light);
                        var lp = ForThing(sc, "goods_pass", light);
                        // row hit: fails alone when a heavy stack flies through a person (planted: heavyGoodsKnock off)
                        bool hit = hh.Count == 1 && (int)hh[0]["pawnId"] == ph.thingIDNumber && heavy.Spawned && Cheb(heavy.Position, ph.Position) <= 1
                            && ph.health.summaryHealth.SummaryHealthPercent < sc.numbers["phHp"];
                        // row pass: fails alone when light goods hit people too (planted: heavyGoodsMinMass 0)
                        bool pass = lh.Count == 0 && lp.Count >= 1 && pl.health.summaryHealth.SummaryHealthPercent == sc.numbers["plHp"]
                            && light.Spawned && light.Position.x < pl.Position.x;
                        return Result(sc, hit && pass, "hit=" + hit + " pass=" + pass + " heavyMass=" + sc.numbers["heavyMass"]
                            + " heavyAt=" + (heavy.Spawned ? heavy.Position.x + "," + heavy.Position.z : "gone") + " ph=" + ph.Position.x + "," + ph.Position.z
                            + " phHp=" + ph.health.summaryHealth.SummaryHealthPercent.ToString("0.000") + " lightAt=" + (light.Spawned ? light.Position.x + "," + light.Position.z : "gone")
                            + (hh.Count > 0 ? " [" + Rec(hh[0]) + "]" : " no heavy_hit") + " passes=" + lp.Count);
                    };
                    return null;

                case "land_no_bump":
                case "land_no_bump_pit":
                    {
                        // RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS: a revolver (stackLimit 1: Direct spawns it even
                        // into a full cell) is thrown onto the cell a resident steel stack holds; _pit: that cell is the
                        // first cell of a superdeep pit (the owner's station 4: a pit good pushed out to the rim).
                        bool pit = s.name == "land_no_bump_pit";
                        Item(s, "gun", "Gun_Revolver", 1, O(s, 1, 0));
                        int cells = WantCells(s, "gun", 2.9f);
                        IntVec3 land;
                        if (pit)
                        {
                            if (!RM_KnockbackCompat.FlowWorks || !Pit(O(s, 3, -1), 3, 3))
                            {
                                return "FlowWorks not loaded / dig failed";
                            }
                            land = O(s, 3, 0);
                            if (cells < 2)
                            {
                                return "revolver throw " + cells + " cells does not reach the pit";
                            }
                        }
                        else
                        {
                            if (cells < 2)
                            {
                                return "revolver throw " + cells + " cells too short";
                            }
                            land = O(s, 1 + cells, 0);
                        }
                        Item(s, "resident", "Steel", 10, land);
                        s.numbers["landX"] = land.x;
                        s.numbers["landZ"] = land.z;
                    }
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        Thing gun = sc.things["gun"], res = sc.things["resident"];
                        var land = new IntVec3((int)sc.numbers["landX"], 0, (int)sc.numbers["landZ"]);
                        var ll = ForThing(sc, "item_land", gun).Concat(ForThing(sc, "item_move", gun).Where(r => !(bool)r["flying"])).ToList();
                        var dest = ll.Count > 0 && ll[0].ContainsKey("dest") ? (IntVec3)ll[0]["dest"] : IntVec3.Invalid;
                        if (!dest.IsValid || dest != land)
                        {
                            return "INVALID " + sc.name + " the revolver did not head for the resident's cell " + land.x + "," + land.z
                                + (ll.Count > 0 ? " [" + Rec(ll[0]) + "]" : " no landing line");
                        }
                        // row stays: fails alone when a landing shoves the resident (planted: Plant directfirst=on)
                        bool stays = !res.Destroyed && res.Spawned && res.Position == land && res.stackCount == 10;
                        // row landed: fails alone when the lander is lost instead (vanished, or never set down)
                        bool landed = !gun.Destroyed && gun.Spawned && gun.Position != land;
                        bool journal = ll.Count == 1 && Convert.ToInt32(ll[0]["residentsMoved"]) == 0;
                        return Result(sc, stays && landed && journal, "stays=" + stays + " landed=" + landed + " journal_zero_moved=" + journal
                            + " resident=" + (res.Spawned ? res.Position.x + "," + res.Position.z : "gone") + " gun=" + (gun.Spawned ? gun.Position.x + "," + gun.Position.z : "gone")
                            + " inPit=" + (gun.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, gun.Position)) + " [" + Rec(ll[0]) + "]");
                    };
                    return null;

                case "gas_clumps":
                    {
                        // RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS: a radius-2 cloud of the Cauldron's vent gas, three steel stacks
                        // and a drafted colonist in it, a woven pit cover over a pit cell at its edge; one cell lit, the
                        // Cauldron's own fire scan spreads it. Control (planted): Plant gasreg=off, the same lit, no bursts.
                        MapComponent vg = VentGas(out Type vt);
                        if (vg == null)
                        {
                            return "The Cauldron (RimMandrake.Biomes) not loaded: no vent gas";
                        }
                        vt.GetMethod("ClearOf")?.Invoke(null, new object[] { Map });
                        // thick (250 of 255): a thin cloud diffuses under the ignite threshold (24) before the next fire scan
                        string seeded = (string)vt.GetMethod("SeedCloud").Invoke(null, new object[] { Map, s.o, 2, 250 });
                        Item(s, "s0", "Steel", 10, O(s, 1, 0));
                        Item(s, "s1", "Steel", 10, O(s, -1, 1));
                        Item(s, "s2", "Steel", 10, O(s, 0, -2));
                        Colonist(s, "p", O(s, -1, -1));
                        if (RM_KnockbackCompat.FlowWorks && Pit(O(s, 3, 0), 1, 1))
                        {
                            Thing cover = Build("RM_PitCover_ReinforcedFrame", O(s, 3, 0)); // 160 HP: the gas's own fire scorches, never fells it in 300 ticks
                            Track(s, "cover", cover);
                            s.numbers["coverHp"] = Hp(cover);
                        }
                        s.numbers["pHp"] = ((Pawn)s.things["p"]).health.summaryHealth.SummaryHealthPercent;
                        object lit = vt.GetMethod("Ignite").Invoke(vg, new object[] { s.o, null });
                        if (!(lit is bool b) || !b)
                        {
                            return "the vent gas did not light: " + seeded;
                        }
                        Action prev = s.restore;
                        s.restore = () => { vt.GetMethod("ClearOf")?.Invoke(null, new object[] { Map }); prev?.Invoke(); };
                    }
                    s.verdict = sc =>
                    {
                        var bursts = Recs(sc, "gas_burst");
                        var ids = new HashSet<int>(bursts.Select(r => (int)r["exp"]));
                        int ticks = bursts.Select(r => (int)r["tick"]).Distinct().Count();
                        var moves = Recs(sc, "item_move").Where(r => ids.Contains((int)r["exp"])).ToList();
                        var launches = Recs(sc, "launch").Where(r => ids.Contains((int)r["exp"])).ToList();
                        int goodsCap = RimMandrakeExplosiveKnockbackSettings.gasBurstGoodsCells;
                        // row chain: fails alone when the gas burns with no bursts or all at once (planted: Plant gasreg=off)
                        bool chain = bursts.Count >= 3 && ticks >= 2;
                        // row goods: fails alone when no good moves or one flies past the burst cap
                        bool goods = moves.Count >= 1 && moves.All(r => (int)r["planned"] <= goodsCap);
                        // row shove: fails alone when a person is thrown further than a cell, hurt by the shove, or more often than the cooldown
                        Pawn p = (Pawn)sc.things["p"];
                        var mine = launches.Where(r => (int)r["thingId"] == p.thingIDNumber).Select(r => (int)r["tick"]).OrderBy(t => t).ToList();
                        bool gap = true;
                        for (int i = 1; i < mine.Count; i++)
                        {
                            gap &= mine[i] - mine[i - 1] >= RimMandrakeExplosiveKnockbackSettings.gasPawnCooldownTicks;
                        }
                        bool shove = mine.Count >= 1 && gap && launches.All(r => (int)r["planned"] <= 1 && Convert.ToSingle(r["impact"]) == 0f);
                        // row cover: fails alone when a burst breaks the pit cover (a burst is not a blast: no deck break). The
                        // burning gas's own fire may scorch it (vanilla fire on a flammable cover): HP is reported, not judged
                        bool cover = !sc.things.ContainsKey("cover") || (!sc.things["cover"].Destroyed && RM_KnockbackCompat.CoverAt(Map, sc.starts["cover"]) == sc.things["cover"]);
                        return Result(sc, chain && goods && shove && cover, "chain=" + chain + " goods=" + goods + " shove=" + shove + " cover=" + cover
                            + " bursts=" + bursts.Count + " burstTicks=" + ticks + " goodsMoves=" + moves.Count + " maxGoodsPlanned=" + moves.Select(r => (int)r["planned"]).DefaultIfEmpty(0).Max()
                            + " pawnShoves=" + mine.Count + " cooldownOk=" + gap + " gasReg=" + RM_KnockbackCompat.VentGasRegistered
                            + (sc.things.ContainsKey("cover") ? " coverHp=" + (sc.things["cover"].Destroyed ? -1 : Hp(sc.things["cover"])) + "/" + sc.numbers["coverHp"] : " no cover"));
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

                case "mass_and_power":
                case "mass_and_power_x2":
                case "mass_and_power_off":
                case "mass_and_power_off_x2":
                case "mass_and_power_250":
                case "mass_and_power_250_x2":
                    return MassAndPower(s);
            }
            return "unknown scene " + s.name;
        }

        /// <summary>sc_mass_and_power (design/concepts/ExplosiveKnockback/scenes.json; owner cards 2026-11-13 "Cutoff -> A mass
        /// limit", "Blast power -> Type x damage"): a rat N, a clothed colonist with a sidearm E, a muffalo S and a thrumbo W,
        /// each one cell from one Bomb blast of radius 2.9 at damage 50 (or 100: the _x2 scenes). The blast REALLY deals that
        /// damage, so the push reads it; NoHarm absorbs the injury on the four (asserted: no new hediff). Lanes: _off =
        /// blastPowerFromDamage off; _250 = creatureMassLimit 250. Every other setting at its default (Reset, restored after).
        /// Verdict from the JOURNAL's launch / skip records (animals walk after landing; displacement cannot tell).</summary>
        private static string MassAndPower(Scene s)
        {
            bool x2 = s.name.EndsWith("_x2");
            string lane = s.name.Contains("_off") ? "off" : s.name.Contains("_250") ? "250" : "default";
            int damage = x2 ? 100 : 50;
            // snapshot every setting, then defaults, then the lane's one change; the restore puts the snapshot back
            var fields = typeof(RimMandrakeExplosiveKnockbackSettings).GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static)
                .Where(f => !f.IsLiteral && !f.IsInitOnly).ToList();
            var saved = fields.Select(f => f.GetValue(null)).ToList();
            Action prev = s.restore;
            s.restore = () =>
            {
                for (int i = 0; i < fields.Count; i++)
                {
                    fields[i].SetValue(null, saved[i]);
                }
                foreach (Thing t in s.things.Values)
                {
                    NoHarm.Remove(t.thingIDNumber);
                }
                prev?.Invoke();
            };
            RimMandrakeExplosiveKnockbackMod.Reset();
            if (RimMandrakeExplosiveKnockbackSettings.creatureMassLimit != 150f || !RimMandrakeExplosiveKnockbackSettings.blastPowerFromDamage
                || RimMandrakeExplosiveKnockbackSettings.maxThrowCells != 6)
            {
                return "defaults are not creatureMassLimit 150, blastPowerFromDamage on, maximum throw 6";
            }
            if (lane == "off")
            {
                RimMandrakeExplosiveKnockbackSettings.blastPowerFromDamage = false;
            }
            else if (lane == "250")
            {
                RimMandrakeExplosiveKnockbackSettings.creatureMassLimit = 250f;
            }

            Pawn rat = Adult(DefDatabase<PawnKindDef>.GetNamed("Rat"));
            Pawn muffalo = Adult(DefDatabase<PawnKindDef>.GetNamed("Muffalo"));
            Pawn thrumbo = Adult(DefDatabase<PawnKindDef>.GetNamed("Thrumbo"));
            GenSpawn.Spawn(rat, O(s, 0, 1), Map);
            Track(s, "rat", rat);
            GenSpawn.Spawn(muffalo, O(s, 0, -1), Map);
            Track(s, "muffalo", muffalo);
            GenSpawn.Spawn(thrumbo, O(s, -1, 0), Map);
            Track(s, "thrumbo", thrumbo);
            // a colonist with a revolver, 45-76 kg as the kernel weighs it (Mass stat minus inventory: worn clothes add nothing,
            // MEASURED live 2026-11-13 at 48.75 and 60.75 kg, so the old 64-76 band never drew one in 40 tries). Under 63.5 kg a
            // colonist ties the capped rat at damage 100 (the order judge allows a tie at the cap); over 76.9 the muffalo at 50
            Pawn col = null;
            ThingDef revolver = DefDatabase<ThingDef>.GetNamedSilentFail("Gun_Revolver");
            for (int tries = 0; tries < 40 && col == null; tries++)
            {
                Pawn c = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
                c.equipment?.DestroyAllEquipment();
                c.inventory?.DestroyAll();
                if (revolver != null)
                {
                    c.equipment?.AddEquipment((ThingWithComps)ThingMaker.MakeThing(revolver));
                }
                float cm = c.GetStatValue(StatDefOf.Mass) - MassUtility.InventoryMass(c);
                if (cm >= 45f && cm <= 76f)
                {
                    col = c;
                }
                else
                {
                    c.Destroy();
                }
            }
            if (col == null)
            {
                return "no generated colonist weighed 45-76 kg in 40 draws";
            }
            GenSpawn.Spawn(col, O(s, 1, 0), Map);
            if (col.drafter != null)
            {
                col.drafter.Drafted = true;
            }
            Track(s, "colonist", col);

            KbSettings k = RimMandrakeExplosiveKnockbackSettings.Kernel();
            float ratio = RM_KnockbackMath.DamageRatio(damage, RM_Patch_DamageWorker_ExplosionKnockback.RefDamageOf(DamageDefOf.Bomb),
                RimMandrakeExplosiveKnockbackSettings.blastPowerRefPercent, RimMandrakeExplosiveKnockbackSettings.blastPowerFromDamage);
            s.numbers["ratio"] = ratio;
            var bands = new Dictionary<string, (float lo, float hi)>
            {
                ["rat"] = (1f, 30f), ["colonist"] = (45f, 76f), ["muffalo"] = (100f, 150f), ["thrumbo"] = (150.001f, 1000f),
            };
            foreach (string key in new[] { "rat", "colonist", "muffalo", "thrumbo" })
            {
                var p = (Pawn)s.things[key];
                float mass = p.GetStatValue(StatDefOf.Mass) - MassUtility.InventoryMass(p);
                if (mass < bands[key].lo || mass > bands[key].hi)
                {
                    return key + " weighs " + mass.ToString("0.0") + " kg, outside " + bands[key].lo.ToString("0") + "-" + bands[key].hi.ToString("0");
                }
                s.numbers["mass_" + key] = mass;
                s.numbers["want_" + key] = RM_KnockbackMath.Eligible(KbKind.Pawn, mass, k)
                    ? RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f * ratio, mass, k) : 0f;
                s.numbers["hediffs_" + key] = p.health.hediffSet.hediffs.Count;
                NoHarm.Add(p.thingIDNumber);
            }
            // the table DEFAULTS.md states for the stated masses (rat 12, colonist ~70, muffalo 144, thrumbo 240)
            var table = lane == "off" || !x2
                ? new Dictionary<string, int> { ["rat"] = 5, ["colonist"] = 3, ["muffalo"] = 2, ["thrumbo"] = lane == "250" ? 1 : 0 }
                : new Dictionary<string, int> { ["rat"] = 6, ["colonist"] = 5, ["muffalo"] = 4, ["thrumbo"] = lane == "250" ? 3 : 0 };
            foreach (var kv in table)
            {
                s.numbers["table_" + kv.Key] = kv.Value;
            }
            Boom(Map, s.o, 2.9f, DamageDefOf.Bomb, damage, null, true);
            s.verdict = sc => MassAndPowerVerdict(sc, damage, lane);
            return null;
        }

        private static string MassAndPowerVerdict(Scene sc, int damage, string lane)
        {
            var sb = new StringBuilder();
            bool ok = true, table = true;
            var cells = new Dictionary<string, int>();
            var dirs = new Dictionary<string, IntVec3> { ["rat"] = IntVec3.North, ["colonist"] = IntVec3.East, ["muffalo"] = IntVec3.South, ["thrumbo"] = IntVec3.West };
            foreach (string key in new[] { "rat", "colonist", "muffalo", "thrumbo" })
            {
                var p = (Pawn)sc.things[key];
                int want = (int)sc.numbers["want_" + key];
                var req = ForThing(sc, "request", p);
                var launch = ForThing(sc, "launch", p);
                var skip = ForThing(sc, "skip", p);
                bool reqOk = req.Count == 1 && Convert.ToInt32(Convert.ToSingle(req[0]["damage"])) == damage
                    && Math.Abs(Convert.ToSingle(req[0]["radius"]) - 2.9f) < 0.01f
                    && Math.Abs(Convert.ToSingle(req[0]["damageRatio"]) - sc.numbers["ratio"]) < 1e-3f;
                int got = 0;
                bool rowOk;
                if (want == 0)
                {
                    rowOk = launch.Count == 0 && skip.Any(r => (string)r["reason"] == "too_heavy_creature");
                }
                else
                {
                    IntVec3 from = launch.Count == 1 ? (IntVec3)launch[0]["from"] : IntVec3.Invalid;
                    IntVec3 to = launch.Count == 1 ? (IntVec3)launch[0]["to"] : IntVec3.Invalid;
                    got = launch.Count == 1 ? Cheb(from, to) : -1;
                    bool straight = launch.Count == 1 && to == from + dirs[key] * got;
                    bool landed = ForThing(sc, "land", p).Any(r => (bool)r["spawned"] && !(bool)r["dead"]);
                    rowOk = got == want && straight && landed && !p.Dead;
                }
                int newHediffs = p.health.hediffSet.hediffs.Count - (int)sc.numbers["hediffs_" + key];
                if (newHediffs > 0)
                {
                    return "INVALID " + sc.name + " the injury hook let " + newHediffs + " hediff(s) through on " + key;
                }
                cells[key] = want == 0 ? 0 : got;
                table &= cells[key] == (int)sc.numbers["table_" + key];
                ok &= rowOk && reqOk;
                sb.Append(" " + key + "(" + sc.numbers["mass_" + key].ToString("0.0") + "kg)=" + (want == 0 ? "spared" : got.ToString())
                    + "/want " + want + (rowOk ? "" : "!") + (reqOk ? "" : " request!"));
            }
            bool order = cells["rat"] >= cells["colonist"] && cells["colonist"] > cells["muffalo"] && cells["muffalo"] > cells["thrumbo"]
                && (lane == "250" || cells["thrumbo"] == 0) && (cells["rat"] > cells["colonist"] || cells["rat"] == 6);
            return Result(sc, ok && order, "lane=" + lane + " damage=" + damage + " ratio=" + sc.numbers["ratio"].ToString("0.00")
                + sb + " order=" + order + " statedTable=" + table);
        }
    }

    /// <summary>Proof build only: absorbs ALL damage to the things RM_KnockbackProof.NoHarm names (sc_mass_and_power).
    /// The explosion's damage still reaches the knockback hook: ExplosionDamageThing's postfix enqueues the throw.</summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.TakeDamage))]
    public static class RM_Patch_Thing_ProofNoHarm
    {
        [HarmonyPriority(Priority.First)]
        public static bool Prefix(Thing __instance, ref DamageWorker.DamageResult __result)
        {
            if (RM_KnockbackProof.NoHarm.Count == 0 || !RM_KnockbackProof.NoHarm.Contains(__instance.thingIDNumber))
            {
                return true;
            }
            __result = new DamageWorker.DamageResult();
            return false;
        }
    }
}
#endif
