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
using Verse.AI;

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
    public static partial class RM_KnockbackProof
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
            public Dictionary<string, IntVec3> atBlast;     // spared_states: each thing's cell just after the blast (visit 1)
            public Dictionary<string, IntVec3> stagedCells; // spared_states: each spared thing's cell as staged (the sleeper has its own bed check)
            public Dictionary<string, IntVec3> preBlast;    // spared_states: each thing's cell on the blast's tick, before it
            public string placeFault;                       // Item: a good that could not be placed, and what held its cell
            public readonly Dictionary<string, string> wantWhy = new Dictionary<string, string>(); // WantCells: its inputs, per key
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
            // 2026-11-14 Stage 3 reconcile (Maturation Pipeline pilot): the locked scenes.json entry points. NOT YET RUN LIVE.
            "pawn_hits_pawn", "only_explosions", "open_storage", "no_cross_ordered", "spared_states", "blast_kinds",
            "goods_fly_wild", "gas_chain", "gas_census", "pawn_arc", "pit_goods_fetch",
            // 2026-11-14 Stage 3, the eleven bars (RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN; RM_KnockbackProof_StageThree.cs),
            // each with its control lane. settings_sweep_<lane> is any lane of SweepLanes. NOT YET RUN LIVE.
            "hose_carry_drop", "hose_carry_drop_off", "closed_containers", "closed_containers_control", "settings_sweep",
            "settings_sweep_after", "frame_probe_selfcheck", "frame_probe_selfcheck_paused", "barrage_perf", "barrage_perf_off",
            // 2026-11-15 Stage 6 visit 1 road back (RIMMANDRAKE_WRITE_GAS_INTO_PIT_SCENE_UNKNOWN_EVERY_BUILD): sc_gas_shove_into_pit
            // and its control lane. NOT YET RUN LIVE.
            "gas_into_pit", "gas_into_pit_off",
            // 2026-11-15 sc_goods_obstacles, named by the test table and never built (RIMMANDRAKE_WRITE_GOODS_OBSTACLES_SCENE_NAMED_NEVER_BUILT;
            // RM_KnockbackProof_GoodsObstacles.cs): door, sandbags and deep water lanes, with the obstacle-free control. NOT YET RUN LIVE.
            "goods_obstacles", "goods_obstacles_control",
            // 2026-11-15 the showcase sc_storeroom_bomb_pit and its pit-filled control (RM_KnockbackProof_StoreroomBombPit.cs). NOT YET RUN LIVE.
            "storeroom_bomb_pit", "storeroom_bomb_pit_control",
            // 2026-11-17 sc_pit_fall as written: open and covered lanes, the no-pit control (RM_KnockbackProof_PitFall.cs). NOT YET RUN LIVE.
            "pit_colonist_control",
        };

        private static Map Map => Find.CurrentMap;

        // ── bridge surface ───────────────────────────────────────────────

        public static string Names(string _)
        {
            return string.Join(",", SceneNames) + " flowworks=" + RM_KnockbackCompat.FlowWorks + " hoses=" + RM_KnockbackCompat.Hoses;
        }

        /// <summary>Forgets which cells near o burst: the mod lets a gas cell burst once per GasCellOnceTicks (600), and the runner
        /// stages the next scene at the same origin 300 ticks later. Visit 4: sc_cauldron_gas read FAIL (26 gas_reburst_skip, 22
        /// at age 300) because sc_gas_chain had just burst its cells. The rule itself is untouched; only another scene's bursts
        /// are forgotten.</summary>
        private static void ForgetGasBursts(IntVec3 o, int radius)
        {
            var comp = Map?.GetComponent<RM_MapComponent_Knockback>();
            var f = typeof(RM_MapComponent_Knockback).GetField("gasCellBurstTick", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            if (comp == null || f == null)
            {
                throw new InvalidOperationException("gas burst memory not reachable: RM_MapComponent_Knockback.gasCellBurstTick");
            }
            var mem = (Dictionary<IntVec3, int>)f.GetValue(comp);
            foreach (IntVec3 c in mem.Keys.Where(k => k.InHorDistOf(o, radius)).ToList())
            {
                mem.Remove(c);
            }
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
                                    int cellsN = RM_KnockbackMath.WildCells(1f, radius, 1f, mass, k, RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild); // goods fly wild (blind cycle 1)
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
                    if (!PondSite(map, new IntVec3(x, 0, z)))
                    {
                        o.Add(x + "," + z);
                    }
                }
            }
            return string.Join(";", o);
        }

        /// <summary>Visit 2 (2026-11-15, SITE): a natural pond in a scene's rect leaves FlowWorks a dry bed that Prepare's
        /// Soil paint does not remove, and the relative climb rule then reads the takeoff cell 4 deep (sc_pit_fall: a thrown
        /// colonist dropped one notch into the pit, no descent). Such a rect is never a scene site.</summary>
        private static bool PondSite(Map map, IntVec3 o)
        {
            foreach (IntVec3 c in CellRect.CenteredOn(o, 7).ClipInsideMap(map))
            {
                TerrainDef td = c.GetTerrain(map);
                if ((td != null && (td.IsWater || td.defName.StartsWith("RM_Lakebed"))) || RM_KnockbackCompat.NaturalBedAt(map, c))
                {
                    return true;
                }
            }
            return false;
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
                ForgetGasBursts(s.o, 12);
                // the site is asserted, never hoped: a prepared rect reads no FlowWorks climb depth (a natural pond's bed outlasts
                // the Soil paint; Origins skips such rects, a hand-given origin is refused here)
                foreach (IntVec3 c in CellRect.CenteredOn(s.o, 7).ClipInsideMap(Map))
                {
                    int depth = RM_KnockbackCompat.ClimbDepthAt(Map, c);
                    if (depth != 0)
                    {
                        return "INVALID " + s.name + " site: climb depth " + depth + " at " + c.x + "," + c.z
                            + " after prepare (a natural pond bed); stage it elsewhere";
                    }
                }
                string why = Build(s);
                if (why == null && s.placeFault != null)
                {
                    why = "site: " + s.placeFault;
                }
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

        /// <summary>The frame probe's bridge read (RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED; Begin/Stop
        /// are internal and jawa/static_call reaches only public static). "begin" starts RM_FrameProbe (a running one is
        /// stopped first); "stop[,loS,hiS]" stops it and returns "FRAME " + its summary (windowP99Ms over the unpaused rows
        /// inside [loS, hiS] probe seconds) + " path=" + the CSV; "NONE" when no probe ran or it saw no frame.</summary>
        public static string Frame(string arg)
        {
            string[] p = (arg ?? "").Split(',');
            string verb = p[0].Trim().ToLowerInvariant();
            if (verb == "begin")
            {
                RM_FrameProbe.Begin();
                return "BEGUN";
            }
            if (verb != "stop")
            {
                return "ERROR Frame wants begin | stop[,loS,hiS], got '" + arg + "'";
            }
            float lo = 0f, hi = float.PositiveInfinity;
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            if (p.Length >= 3 && (!float.TryParse(p[1].Trim(), System.Globalization.NumberStyles.Float, inv, out lo)
                || !float.TryParse(p[2].Trim(), System.Globalization.NumberStyles.Float, inv, out hi)))
            {
                return "ERROR Frame stop window unreadable: '" + arg + "'";
            }
            KbFrameSummary g = RM_FrameProbe.Stop(lo, hi);
            if (g.rows == 0)
            {
                return "NONE no probe running, or it saw no frame";
            }
            return "FRAME " + Summary(g) + " path=" + RM_FrameProbe.LastPath;
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
            if (placed == null || !placed.Spawned)
            {
                // RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS: a Direct place onto a cell that already holds an
                // item of another def spawns nothing, and the unspawned good's start is no cell: the scene then reads "planned 0
                // cells". Stage turns this into an INVALID that names what held the cell.
                s.placeFault = (s.placeFault == null ? "" : s.placeFault + "; ") + "could not place " + count + " " + def + " at "
                    + c.x + "," + c.z + ", the cell holds [" + string.Join(", ", c.GetThingList(Map).Select(x => x.def.defName + x.thingIDNumber
                    + " x" + x.stackCount + " " + x.def.category)) + "]";
            }
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
        /// blast beside the lightest loaded animal; the throw must be read, not the kill). Cleared by the scene's restore.</summary>
        internal static readonly HashSet<int> NoHarm = new HashSet<int>();

        /// <summary>Test-only mass pins (thing id -> kg) the knockback request reads in place of the measured mass
        /// (RM_MapComponent_Knockback, under RM_PROOFS). sc_mass_and_power pins its colonist to 64-76 kg; the scene's restore
        /// removes every pin it set.</summary>
        internal static readonly Dictionary<int, float> PinnedMass = new Dictionary<int, float>();

        /// <summary>The mass scenes choose their animals BY MASS from whatever animal kinds are loaded, never by name: this
        /// mod names no creature (a franchise-free RM_ tier mod; owner 2026-11-13 at sc_mass_and_power: "We shouldn't have
        /// anything called a Thrumbo in the game anymore"). Candidates: flesh animal kinds with a life stage, not dryads, weighed
        /// as the race's Mass stat read on its def (StatPart_BodySize applies race.baseBodySize there) x the adult life stage's
        /// bodySizeFactor (the spawned pawn's BodySize; a race that sets its own
        /// Mass, e.g. a 0.04 kg tikkit, is not 60 kg x body size: live6 2026-11-13 picked one at 2.4 kg that weighed 0.0). Tie-break, deterministic: non-Ludeon content first (a
        /// tier without Cherry Picker still loads the vanilla beasts the full list cuts, VANILLA_BEAST_EXCISION_1), then the
        /// band's preference (lightest, heaviest, or nearest the band's middle), then defName ordinal. An empty band throws,
        /// naming the band in kg. The scene re-weighs the spawned pawn and its row prints the label and the measured mass.</summary>
        internal static float KindMass(PawnKindDef k)
        {
            RaceProperties r = k.RaceProps;
            float factor = r.lifeStageAges[r.lifeStageAges.Count - 1].def?.bodySizeFactor ?? 1f;
            return k.race.GetStatValueAbstract(StatDefOf.Mass) * factor;   // the abstract read already applies race.baseBodySize
        }

        private static IEnumerable<PawnKindDef> AnimalKinds()
        {
            return DefDatabase<PawnKindDef>.AllDefsListForReading.Where(k => k.race != null && k.RaceProps != null
                && k.RaceProps.Animal && k.RaceProps.IsFlesh && !k.RaceProps.Dryad && k.RaceProps.lifeStageAges != null
                && k.RaceProps.lifeStageAges.Count > 0);
        }

        private static bool Official(PawnKindDef k)
        {
            return k.modContentPack != null && k.modContentPack.IsOfficialMod;
        }

        /// <summary>One animal kind with lo &lt;= adult mass &lt; hi kg; prefer: "light", "heavy" or "middle".</summary>
        internal static PawnKindDef ByMass(string band, float lo, float hi, string prefer)
        {
            float mid = (lo + hi) / 2f;
            var inBand = AnimalKinds().Where(k => KindMass(k) >= lo && KindMass(k) < hi).ToList();
            if (inBand.Count == 0)
            {
                throw new InvalidOperationException("no loaded animal kind for the " + band + " band, " + lo.ToString("0.#")
                    + "-" + hi.ToString("0.#") + " kg adult");
            }
            return inBand.OrderBy(k => Official(k) ? 1 : 0)
                .ThenBy(k => prefer == "light" ? KindMass(k) : prefer == "heavy" ? -KindMass(k) : Math.Abs(KindMass(k) - mid))
                .ThenBy(k => k.defName, StringComparer.Ordinal).First();
        }

        /// <summary>The four bands sc_mass_and_power, heavy_skip and body_override stand up.</summary>
        // from 1 kg: a 0.1 kg pick (dhuvvox, live6) weighed just under the scene's 0.1 kg check and turned every lane INVALID
        internal static PawnKindDef SmallAnimal() => ByMass("lightest", 1f, 30f, "light");
        internal static PawnKindDef UnderLimitAnimal() => ByMass("heaviest under the 150 kg limit", 100f, 150f, "heavy");
        internal static PawnKindDef OverrideAnimal() => ByMass("160-200 kg", 160f, 200f, "middle");
        internal static PawnKindDef HeavyAnimal() => ByMass("220-260 kg", 220f, 260f, "middle");

        private static string Named(Pawn p, float mass)
        {
            return p.kindDef.label + " " + mass.ToString("0.0") + " kg";
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

        /// <summary>Where an unspawned thing went, for a verdict line (RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS:
        /// a good read "gone" after a throw, and nothing said whether it was destroyed, merged into a stack (destroyed, stack 0)
        /// or picked up, and by whom).</summary>
        internal static string Gone(Thing t)
        {
            if (t == null)
            {
                return "gone(null)";
            }
            IThingHolder h = t.ParentHolder;
            string holder = h == null ? "none" : h.GetType().Name;
            if (h is Pawn_CarryTracker ct)
            {
                holder += ":" + ct.pawn?.LabelShort + ct.pawn?.thingIDNumber + " job=" + ct.pawn?.CurJobDef?.defName;
            }
            else if (h is Pawn_InventoryTracker it)
            {
                holder += ":" + it.pawn?.LabelShort + it.pawn?.thingIDNumber;
            }
            else if (h is Thing ht)
            {
                holder += ":" + ht.def.defName + ht.thingIDNumber;
            }
            return "gone(destroyed=" + t.Destroyed + " stack=" + t.stackCount + " holder=" + holder + ")";
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
                return key + " not spawned " + Gone(t);
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

        /// <summary>sc_pit_fetch's window: the two ordered hauls finish well inside it (RIMMANDRAKE_SHRINK_KNOCKBACK_SCENES_ONE_SAVE_IN_AIR).</summary>
        private const int PitFetchTicks = 5000;

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
            float dist = (s.starts[key] - s.o).LengthHorizontal;
            float wild = RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild;
            int cells = RM_KnockbackVerdicts.GoodCells(dist, r, mass, k, wild);
            // RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS: a long batch once planned 0 cells here; an INVALID
            // line prints these inputs (WantWhy) so the next sighting names the input that went to 0
            s.wantWhy[key] = "inputs " + key + ": dist=" + dist.ToString("0.00") + " mass=" + mass.ToString("0.###") + " stack=" + t.stackCount
                + " spawned=" + t.Spawned + " at=" + s.starts[key].x + "," + s.starts[key].z + " o=" + s.o.x + "," + s.o.z + " wild=" + wild
                + " k{mult=" + k.globalMultiplier + " base=" + k.baseCells + " max=" + k.maxCells + " light=" + k.lightMassLimit + " ref=" + k.refMass + "}";
            return cells;
        }

        private static string WantWhy(Scene s, string key)
        {
            return s.wantWhy.TryGetValue(key, out string w) ? " [" + w + "]" : " [no inputs recorded]";
        }

        /// <summary>WantCells for a blast centred on <paramref name="centre"/> rather than the scene origin (a scene with several
        /// lanes, each with its own blast: goods_obstacles).</summary>
        private static int WantCellsFrom(Scene s, string key, IntVec3 centre, float r)
        {
            KbSettings k = RimMandrakeExplosiveKnockbackSettings.Kernel();
            Thing t = s.things[key];
            float mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount;
            return RM_KnockbackVerdicts.GoodCells((s.starts[key] - centre).LengthHorizontal, r, mass, k, RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild);
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
                        bool alive = t is Pawn p && !p.Dead;
                        bool ok = RM_KnockbackVerdicts.Calibration(cells, t.Spawned, t.Position.x, t.Position.z, sc.starts["p"].x, sc.starts["p"].z,
                            alive, launch.Count, out bool away);
                        return Result(sc, ok, m + " away=" + away + " alive=" + alive
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
                case "pit_colonist_control":
                    return PitFall(s);  // sc_pit_fall's open and covered lanes and its no-pit control (RM_KnockbackProof_PitFall.cs)

                case "pit_enemy":
                    if (!RM_KnockbackCompat.FlowWorks)
                    {
                        return "FlowWorks not loaded";
                    }
                    if (!Pit(O(s, 3, -1), 3, 3))
                    {
                        return "could not dig the pit";
                    }
                    Hostile(s, "p", O(s, 1, 0));
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
                            int want = RM_KnockbackVerdicts.GoodCells((sc.starts[key] - sc.o).LengthHorizontal, 2.9f, mass, k, RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild);
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
                    // the spin trace (leaf goods_arc_spin_rebound: "loose goods and corpses ... spinning fast"): each tick, the angle
                    // the pawn renderer draws a carried body at; the turn adds up while it is in the air
                    Map km = Map;
                    for (int d = 1; d <= 200; d++)
                    {
                        RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + d, () =>
                        {
                            foreach (string key in new[] { "p0", "p1", "p2" })
                            {
                                Pawn p = (Pawn)s.things[key];
                                if (!p.Dead || p.Corpse == null || km != Find.CurrentMap || CarrierOf(km, p.Corpse) == null)
                                {
                                    continue;
                                }
                                float angle = p.Drawer.renderer.BodyAngle(PawnRenderFlags.None);
                                if (s.numbers.TryGetValue(key + "_angle", out float was))
                                {
                                    s.numbers[key + "_turn"] = (s.numbers.TryGetValue(key + "_turn", out float sum) ? sum : 0f)
                                        + Math.Abs(UnityEngine.Mathf.DeltaAngle(was, angle));
                                }
                                s.numbers[key + "_angle"] = angle;
                                s.numbers[key + "_airTicks"] = (s.numbers.TryGetValue(key + "_airTicks", out float air) ? air : 0f) + 1f;
                            }
                        }));
                    }
                    s.verdict = sc =>
                    {
                        int dead = 0, thrown = 0, spun = 0;
                        var turns = new List<string>();
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
                            float turn = sc.numbers.TryGetValue(key + "_turn", out float tn) ? tn : 0f;
                            turns.Add(key + ":" + turn.ToString("0") + "deg/" + (sc.numbers.TryGetValue(key + "_airTicks", out float at) ? at : 0f) + "t");
                            spun += turn >= 30f ? 1 : 0;
                        }
                        if (dead == 0)
                        {
                            return "INVALID " + sc.name + " the blast killed nobody";
                        }
                        return Result(sc, thrown == dead && spun == dead, "dead=" + dead + " corpsesThrown=" + thrown + " corpsesSpun=" + spun
                            + " [" + string.Join(" ", turns) + "]");
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
                        // an adult animal of 220-260 kg, chosen by mass: over the global 150 kg creature limit (a calf could
                        // weigh under it)
                        Pawn a = Adult(HeavyAnimal());
                        GenSpawn.Spawn(a, O(s, 1, 0), Map);
                        Track(s, "big", a);
                        s.restore = () => { if (!a.Destroyed) a.Destroy(); };
                    }
                    Blast(s.o, 2.9f);
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "big", out Thing t, out int cells);
                        var skip = ForThing(sc, "skip", t).Where(r => (string)r["reason"] == "too_heavy_creature").ToList();
                        return Result(sc, skip.Count == 1 && ForThing(sc, "launch", t).Count == 0, Named((Pawn)t, t.GetStatValue(StatDefOf.Mass)
                            - MassUtility.InventoryMass((Pawn)t)) + ": " + m + " skips(too_heavy_creature)=" + skip.Count
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
                    // a living adult animal of 160-200 kg, chosen by mass: heavier than the global 150 kg, so spared by the
                    // global creature mass limit, and thrown under a creatureMassLimitOverride of 216 (the grav-ram's)
                    PawnKindDef big = OverrideAnimal();
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
                        return big.label + " (" + big.defName + ") weighs " + s.numbers["mass"].ToString("0.0") + " kg, not 150-216";
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
                        return Result(sc, bigLaunch == 1 && ctrlLaunch == 0 && ctrlSkip, Named((Pawn)t, sc.numbers["mass"]) + ": " + m + "; " + mc
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
                            return "INVALID " + sc.name + " component planned " + want + " cells: does not reach the wall" + WantWhy(sc, "comp");
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
                case "goods_fly_wild":   // sc_storeroom_mortar, by rename (Stage 3 reconcile): checks the rebound only; see the table
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
                            return "INVALID " + sc.name + " planned " + want + " cells leaves no rebound (back=" + back + ")" + WantWhy(sc, "comp");
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
                    // flyingGoods off -> goods unthrown (settings_scale_and_switch: "goods in the air off, goods unthrown, never the
                    // old hop"): one skip flying_off, no item_move, never inside a carrier, still on its cell with its count
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
                            return "INVALID " + sc.name + " steel would not be thrown with flying goods on (want=0): the control is empty";
                        }
                        string m = Moved(sc, "steel", out Thing tt, out int cells);
                        bool skipped = ForThing(sc, "skip", t).Any(r => (string)r["reason"] == "flying_off");
                        bool noMove = ForThing(sc, "item_move", t).Count == 0;
                        bool neverAir = !sc.numbers.ContainsKey("steel_airTick");
                        bool ok = RM_KnockbackVerdicts.FlyOff(skipped, noMove, neverAir, tt.Spawned, cells, tt.stackCount, 75);
                        return Result(sc, ok, m + " wantIfOn=" + want + " flyingOffSkip=" + skipped + " itemMoves=" + (noMove ? 0 : 1) + " seenInCarrier=" + !neverAir);
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
                            + " heavyAt=" + (heavy.Spawned ? heavy.Position.x + "," + heavy.Position.z : Gone(heavy)) + " ph=" + ph.Position.x + "," + ph.Position.z
                            + " phHp=" + ph.health.summaryHealth.SummaryHealthPercent.ToString("0.000") + " lightAt=" + (light.Spawned ? light.Position.x + "," + light.Position.z : Gone(light))
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
                            + " resident=" + (res.Spawned ? res.Position.x + "," + res.Position.z : Gone(res)) + " gun=" + (gun.Spawned ? gun.Position.x + "," + gun.Position.z : Gone(gun))
                            + " inPit=" + (gun.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, gun.Position)) + " [" + Rec(ll[0]) + "]");
                    };
                    return null;

                case "gas_census":       // sc_cauldron_gas, by rename: the tagged source (today the vent gas alone) must be registered
                    if (s.name == "gas_census" && !RM_KnockbackCompat.VentGasRegistered)
                    {
                        return "the Cauldron's vent gas is not registered with the gas chain";
                    }
                    goto case "gas_clumps";
                case "gas_chain":        // sc_gas_chain, by rename (Stage 3 reconcile): checks what gas_clumps checks; see the table
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
                        var rebounds = Recs(sc, "item_rebound").ToLookup(r => ((int)r["exp"], (int)r["thingId"]));
                        var landings = Recs(sc, "item_land").ToLookup(r => ((int)r["exp"], (int)r["thingId"]));
                        var launches = Recs(sc, "launch").Where(r => ids.Contains((int)r["exp"])).ToList();
                        int goodsCap = RimMandrakeExplosiveKnockbackSettings.gasBurstGoodsCells;
                        // row chain: fails alone when the gas burns with no bursts or all at once (planted: Plant gasreg=off)
                        bool chain = bursts.Count >= 3 && ticks >= 2;
                        // row goods: fails alone when no good moves or one flies past the burst cap
                        int maxTravel = 0, maxDisplacement = 0;
                        foreach (var move in moves)
                        {
                            var key = ((int)move["exp"], (int)move["thingId"]);
                            bool wallFirst = move.TryGetValue("wallFirst", out object wall) && (bool)wall;
                            // The initial wall bounce repeats the first leg already recorded by item_move.
                            int travel = (int)move["cells"] + rebounds[key].Skip(wallFirst ? 1 : 0)
                                .Sum(r => Cheb((IntVec3)r["at"], (IntVec3)r["to"]));
                            var landed = (bool)move["flying"] ? landings[key].LastOrDefault() : move;
                            int displacement = landed == null ? int.MaxValue : Cheb((IntVec3)move["from"], (IntVec3)landed["to"]);
                            maxTravel = Math.Max(maxTravel, travel);
                            maxDisplacement = Math.Max(maxDisplacement, displacement);
                        }
                        bool goods = moves.Count >= 1 && moves.All(r => (int)r["planned"] <= goodsCap)
                            && maxTravel <= goodsCap && maxDisplacement <= goodsCap;
                        // row shove: fails alone when a person is thrown further than a cell, hurt by the shove, or more often than the cooldown
                        Pawn p = (Pawn)sc.things["p"];
                        var mine = launches.Where(r => (int)r["thingId"] == p.thingIDNumber).Select(r => (int)r["tick"]).OrderBy(t => t).ToList();
                        bool gap = true;
                        for (int i = 1; i < mine.Count; i++)
                        {
                            gap &= mine[i] - mine[i - 1] >= RimMandrakeExplosiveKnockbackSettings.gasPawnCooldownTicks;
                        }
                        bool shove = mine.Count >= 1 && gap && launches.All(r => (int)r["planned"] <= 1 && Convert.ToSingle(r["impact"]) == 0f);
                        bool noHeavyHit = !Recs(sc, "heavy_hit").Any(r => ids.Contains((int)r["exp"]));
                        // row cover: fails alone when a burst breaks the pit cover (a burst is not a blast: no deck break). The
                        // burning gas's own fire may scorch it (vanilla fire on a flammable cover): HP is reported, not judged
                        bool cover = !sc.things.ContainsKey("cover") || (!sc.things["cover"].Destroyed && RM_KnockbackCompat.CoverAt(Map, sc.starts["cover"]) == sc.things["cover"]);
                        return Result(sc, chain && goods && shove && cover && noHeavyHit, "chain=" + chain + " goods=" + goods + " shove=" + shove + " cover=" + cover
                            + " noHeavyHit=" + noHeavyHit + " maxGoodsTravel=" + maxTravel + " maxGoodsDisplacement=" + maxDisplacement
                            + " bursts=" + bursts.Count + " burstTicks=" + ticks + " goodsMoves=" + moves.Count + " maxGoodsPlanned=" + moves.Select(r => (int)r["planned"]).DefaultIfEmpty(0).Max()
                            + " pawnShoves=" + mine.Count + " cooldownOk=" + gap + " gasReg=" + RM_KnockbackCompat.VentGasRegistered
                            + (sc.things.ContainsKey("cover") ? " coverHp=" + (sc.things["cover"].Destroyed ? -1 : Hp(sc.things["cover"])) + "/" + sc.numbers["coverHp"] : " no cover"));
                    };
                    return null;

                case "gas_into_pit":
                case "gas_into_pit_off":
                    {
                        // sc_gas_shove_into_pit (RIMMANDRAKE_WRITE_GAS_INTO_PIT_SCENE_UNKNOWN_EVERY_BUILD): a drafted colonist on the
                        // west rim of an open 3x3 pit, on the east edge cell of a radius-2 cloud of the Cauldron's vent gas that
                        // stops short of the pit. The cell due west of the colonist is lit first, so the first burst in reach
                        // (bursts are processed in order; the 120-tick cooldown drops the rest) shoves it due east, into the pit.
                        // _off, the control: the vent grid's registration with the gas chain removed, the same lit; no shove.
                        bool off = s.name == "gas_into_pit_off";
                        if (!RM_KnockbackCompat.FlowWorks)
                        {
                            return "FlowWorks not loaded";
                        }
                        MapComponent vg = VentGas(out Type vt);
                        if (vg == null)
                        {
                            return "The Cauldron (RimMandrake.Biomes) not loaded: no vent gas";
                        }
                        if (!RM_KnockbackCompat.VentGasRegistered)
                        {
                            return "the Cauldron's vent gas is not registered with the gas chain";
                        }
                        if (!Pit(O(s, 1, -1), 3, 3) || RM_KnockbackCompat.CoverAt(Map, O(s, 1, 0)) != null)
                        {
                            return "could not dig an open pit";
                        }
                        vt.GetMethod("ClearOf")?.Invoke(null, new object[] { Map });
                        bool reg = RM_KnockbackCompat.VentGasRegistered;
                        Action prev = s.restore;
                        s.restore = () =>
                        {
                            RM_KnockbackCompat.VentGasRegistered = reg;
                            vt.GetMethod("ClearOf")?.Invoke(null, new object[] { Map });
                            prev?.Invoke();
                        };
                        string seeded = (string)vt.GetMethod("SeedCloud").Invoke(null, new object[] { Map, O(s, -2, 0), 2, 250 });
                        Pawn p = Colonist(s, "p", O(s, 0, 0));
                        int dens = (int)vt.GetMethod("DensityAt").Invoke(vg, new object[] { O(s, 0, 0) });
                        if (dens <= 0)
                        {
                            return "the colonist's cell holds no vent gas: " + seeded;
                        }
                        s.numbers["dens"] = dens;
                        if (off)
                        {
                            RM_KnockbackCompat.VentGasRegistered = false;
                        }
                        object lit = vt.GetMethod("Ignite").Invoke(vg, new object[] { O(s, -1, 0), null });
                        if (!(lit is bool b) || !b)
                        {
                            return "the vent gas did not light: " + seeded;
                        }
                        s.numbers["pHurt"] = p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury);
                    }
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        var launch = ForThing(sc, "launch", t);
                        var desc = ForThing(sc, "descent", t);
                        var land = ForThing(sc, "land", t);
                        int bursts = Recs(sc, "gas_burst").Count;
                        bool inPit = t.Spawned && RM_KnockbackCompat.IsSuperdeep(Map, t.Position);
                        string d = m + " bursts=" + bursts + " launches=" + launch.Count + " descents=" + desc.Count + " inPit=" + inPit
                            + " gasAtColonist=" + sc.numbers["dens"] + " gasReg=" + RM_KnockbackCompat.VentGasRegistered
                            + (launch.Count > 0 ? " [" + Rec(launch[0]) + "]" : "");
                        if (sc.name == "gas_into_pit_off")
                        {
                            // row control: fails alone when the colonist ends in the pit with the gas chain unhooked (the
                            // fire, or a walk, put it there). Visit 2 (2026-11-15): the lit cloud's vanilla fire sets the colonist
                            // alight and a burning colonist runs (4 to 9 cells, 2 of 4 runs), so cells moved count only unburned.
                            bool burned = t is Pawn bp && (bp.IsBurning() || bp.health.hediffSet.hediffs.Any(h => h.def.defName == "Burn"));
                            return Result(sc, bursts == 0 && launch.Count == 0 && desc.Count == 0 && !inPit && (cells == 0 || burned),
                                d + " burned=" + burned);
                        }
                        // row shove: one launch, one cell, no impact (a shove is not a throw)
                        bool shove = launch.Count == 1 && (int)launch[0]["planned"] <= 1 && Convert.ToSingle(launch[0]["impact"]) == 0f;
                        // row fell: it landed on the pit's first cell and went down it once
                        bool landed = land.Count == 1 && (IntVec3)land[0]["at"] == O(sc, 1, 0);
                        bool fell = landed && desc.Count == 1 && inPit;
                        // row unhurt: the shove added no injury (the fall's own, if any, comes with the descent: reported)
                        int hurt = t is Pawn pp ? pp.health.hediffSet.hediffs.Count(h => h is Hediff_Injury) : -1;
                        return Result(sc, bursts >= 1 && shove && fell, d + " shove=" + shove + " landedOnFirstPitCell=" + landed
                            + " injuries " + sc.numbers["pHurt"] + "->" + hurt);
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

                // ── Stage 3 reconcile, 2026-11-14 (Maturation Pipeline pilot): the locked scenes.json entry points that had
                // no case. Written and compile-checked offline; NOT YET RUN LIVE (Stage 6).

                case "pawn_hits_pawn":
                    // sc_pawn_hits_pawn: a colonist one cell from the impact, a standing pawn two cells beyond on the ray.
                    // Control: the same throw 5 cells north with nothing in the way lands 3 cells out.
                    Colonist(s, "p", O(s, 1, 0));
                    Colonist(s, "w", O(s, 3, 0), drafted: true);
                    Colonist(s, "q", O(s, 1, 5));
                    Blast(s.o, 2.9f);
                    Blast(O(s, 0, 5), 2.9f);
                    // the same stop when the standing pawn stands on an intact pit cover (42225e0686; visit 4: the planted
                    // PF_CALLER_PAWN_ON_COVER_IGNORED read PASS, no lane had a pawn on a cover)
                    if (RM_KnockbackCompat.FlowWorks)
                    {
                        if (!Pit(O(s, 3, -5), 1, 1))
                        {
                            return "could not dig the covered lane's pit";
                        }
                        Build("RM_PitCover_ReinforcedFrame", O(s, 3, -5));
                        Colonist(s, "p2", O(s, 1, -5));
                        Colonist(s, "w2", O(s, 3, -5), drafted: true);
                        if (RM_KnockbackCompat.CoverAt(Map, O(s, 3, -5)) == null)
                        {
                            return "the covered lane's cover is not intact after building it";
                        }
                        Blast(O(s, 0, -5), 2.9f);
                    }
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        Moved(sc, "q", out Thing _, out int qc);
                        bool onCover = true;
                        string cm = "covered lane not staged (no FlowWorks)";
                        if (sc.things.ContainsKey("p2"))
                        {
                            cm = Moved(sc, "p2", out Thing p2, out int c2);
                            var cb = ForThing(sc, "launch", p2).Concat(ForThing(sc, "blocked", p2)).ToList();
                            onCover = cb.Count == 1 && (string)cb[0]["stop"] == "Pawn" && Convert.ToSingle(cb[0]["impact"]) > 0f
                                && p2.Spawned && p2.Position == O(sc, 2, -5) && RM_KnockbackCompat.CoverAt(Map, O(sc, 3, -5)) != null;
                            cm = "covered lane " + cm + (cb.Count > 0 ? " [" + Rec(cb[0]) + "]" : " no record");
                        }
                        var b = ForThing(sc, "launch", t).Concat(ForThing(sc, "blocked", t)).ToList();
                        bool pawnStop = b.Count == 1 && (string)b[0]["stop"] == "Pawn" && Convert.ToSingle(b[0]["impact"]) > 0f;
                        if (qc != 3)
                        {
                            return "INVALID " + sc.name + " control threw " + qc + " cells, not 3";
                        }
                        return Result(sc, t.Spawned && t.Position == O(sc, 2, 0) && pawnStop && onCover, m + (b.Count > 0 ? " [" + Rec(b[0]) + "]" : " no record") + " | " + cm);
                    };
                    return null;

                case "only_explosions":
                    {
                        // sc_only_explosions: a melee blow and a rifle bullet at a standing colonist queue no throw; a grenade
                        // two cells away then throws the same colonist (the control: it is throwable).
                        Pawn p = Colonist(s, "p", O(s, 2, 0));
                        Pawn hitter = Colonist(s, "h", O(s, 2, 1));
                        int before = RM_KnockbackJournal.Recs.Count(r => (string)r["type"] == "request");
                        p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, 1f, 0f, -1f, hitter));
                        p.TakeDamage(new DamageInfo(DamageDefOf.Bullet, 1f, 0f, -1f, hitter, null, DefDatabase<ThingDef>.GetNamedSilentFail("Gun_BoltActionRifle")));
                        s.numbers["reqAfterHits"] = RM_KnockbackJournal.Recs.Count(r => (string)r["type"] == "request") - before;
                        s.numbers["movedAfterHits"] = p.Position == s.starts["p"] ? 0 : 1;
                        Blast(s.o, 2.9f);
                    }
                    s.verdict = sc =>
                    {
                        string m = Moved(sc, "p", out Thing t, out int cells);
                        bool quiet = sc.numbers["reqAfterHits"] == 0 && sc.numbers["movedAfterHits"] == 0;
                        bool thrown = cells >= 1 && ForThing(sc, "launch", t).Count == 1;
                        if (!thrown)
                        {
                            return "INVALID " + sc.name + " the grenade control did not throw: " + m;
                        }
                        return Result(sc, quiet, "melee+bullet requests=" + sc.numbers["reqAfterHits"] + " moved=" + sc.numbers["movedAfterHits"] + "; grenade " + m);
                    };
                    return null;

                case "open_storage":
                    {
                        // sc_open_storage (held statement, owner 2026-11-12: "Anything that draws its contents is open"): a shelf,
                        // a small shelf, a hopper and a table, each holding goods, each classed open by the guard, beside one
                        // blast. Control: the same goods on bare floor around a blast 5 cells south.
                        string[] defs = { "ShelfSmall", "Hopper", "Shelf", "Table2x2c" };
                        IntVec3[] at = { O(s, 1, 0), O(s, -1, 0), O(s, 0, 1), O(s, 0, -2) };
                        for (int i = 0; i < defs.Length; i++)
                        {
                            if (DefDatabase<ThingDef>.GetNamedSilentFail(defs[i]) == null)
                            {
                                return defs[i] + " not loaded";
                            }
                            Thing f = Build(defs[i], at[i], DefDatabase<ThingDef>.GetNamed(defs[i]).MadeFromStuff ? "WoodLog" : null);
                            Thing g = Item(s, "g" + i, "Steel", 20, at[i]);
                            if (RM_MapComponent_Knockback.InClosedContainer(g, Map))
                            {
                                return defs[i] + " classed closed by the guard (it draws its contents: must be open)";
                            }
                            Item(s, "f" + i, "Steel", 20, at[i] + new IntVec3(0, 0, -5));
                        }
                        Blast(s.o, 2.9f);
                        Blast(O(s, 0, -5), 2.9f);
                    }
                    s.verdict = sc =>
                    {
                        var sb = new StringBuilder();
                        bool ok = true;
                        for (int i = 0; i < 4; i++)
                        {
                            sb.Append(Moved(sc, "g" + i, out Thing g, out int gc)).Append(" | ");
                            Moved(sc, "f" + i, out Thing _, out int fc);
                            bool stored = ForThing(sc, "skip", g).Any(r => (string)r["reason"] == "in_storage");
                            ok &= gc > 0 && !stored;
                            sb.Append("floor control ").Append(fc).Append(" cells; ");
                        }
                        return Result(sc, ok, sb.ToString());
                    };
                    return null;

                case "no_cross_ordered":
                    {
                        // sc_no_careless_fall: a colonist ordered across an open pit and a second across a covered pit both
                        // walk round; no descent. (The concealed-pit raider control is not staged here: listed UNBUILT.)
                        if (!RM_KnockbackCompat.FlowWorks || !Pit(O(s, 0, -3), 1, 3) || !Pit(O(s, 0, 2), 1, 3))
                        {
                            return "FlowWorks not loaded / dig failed";
                        }
                        Thing cover = Build("RM_PitCover_ReinforcedFrame", O(s, 0, 3));
                        Track(s, "cover", cover);
                        Pawn a = Colonist(s, "a", O(s, -3, -2), drafted: true);
                        Pawn b = Colonist(s, "b", O(s, -3, 3), drafted: true);
                        a.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, O(s, 3, -2)));
                        b.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, O(s, 3, 3)));
                        if (a.CurJobDef != JobDefOf.Goto || b.CurJobDef != JobDefOf.Goto)
                        {
                            return "the walk orders are not the current jobs";
                        }
                    }
                    s.verdict = sc =>
                    {
                        Pawn a = (Pawn)sc.things["a"], b = (Pawn)sc.things["b"];
                        int falls = Recs(sc, "descent").Count;
                        bool arrived = a.Position == O(sc, 3, -2) && b.Position == O(sc, 3, 3);
                        return Result(sc, arrived && falls == 0, "a@" + a.Position + " b@" + b.Position + " descents=" + falls + " (step 2000 ticks)");
                    };
                    return null;

                case "spared_states":
                    {
                        // sc_spared: who is never thrown, each with its journal skip reason. The FLYING lane is not staged:
                        // a flyer's flight is never live-tested without the owner present (standing rule); listed UNBUILT.
                        if (!RM_KnockbackCompat.FlowWorks || !Pit(O(s, -2, -1), 1, 3))
                        {
                            return "FlowWorks not loaded / dig failed";
                        }
                        Pawn big = Adult(HeavyAnimal());
                        GenSpawn.Spawn(big, O(s, 1, 0), Map);
                        Track(s, "big", big);
                        Colonist(s, "pit", O(s, -2, 0));
                        Item(s, "pitstack", "Steel", 10, O(s, -2, 1));
                        Pawn carrier = Colonist(s, "carrier", O(s, 0, 1), drafted: false);
                        Pawn carried = Colonist(s, "carried", O(s, 0, 2), drafted: false);
                        carried.health.AddHediff(HediffDefOf.Anesthetic);   // the scene's "carrying a downed pawn" (visit 1)
                        carrier.carryTracker.TryStartCarry(carried, 1, reserve: false);   // the count overload despawns it (SplitOff)
                        Thing bed = Build("Bed", O(s, 1, -2), "WoodLog");
                        Pawn sleeper = Colonist(s, "sleeper", bed.Position, drafted: false);
                        if (sleeper.needs?.rest != null)
                        {
                            sleeper.needs.rest.CurLevel = 0.05f;   // a rested colonist got up before the blast (visit 1)
                        }
                        sleeper.jobs.StartJob(JobMaker.MakeJob(JobDefOf.LayDown, bed), JobCondition.InterruptForced);
                        Pawn corpseOf = Adult(HeavyAnimal());
                        GenSpawn.Spawn(corpseOf, O(s, -1, -1), Map);
                        corpseOf.Kill(null);
                        Track(s, "corpse", corpseOf.Corpse);
                        Action prev = s.restore;
                        s.restore = () => { if (!big.Destroyed) big.Destroy(); prev?.Invoke(); };
                        // Stage 6 visit 1 (2026-11-15): an undrafted carrier with no job drops its pawn within the 60 ticks before the
                        // blast, so the carry starts in the blast's own action; each spared thing's cell is read 8 ticks after it
                        // (atBlast), since a skipped animal wanders and a woken sleeper gets up before the 300-tick verdict
                        var atBlast = new Dictionary<string, IntVec3>();
                        // the carry is re-pinned every tick from +55 to +64 and read on each tick of the blast's spread (+60 to +64);
                        // from +1 to +68 the spared pawns' own walking is stopped (pather.StopDead), and each spared thing's cell
                        // just before the blast (+60) is compared with its cell at +68: the blast's effect alone. Until 2026-11-23
                        // the hold began at +55 and visit 4 read FAIL once, the carrier with no request line: a pawn free for 55
                        // ticks can be off the blast. A spared thing off its staged cell at +60 is INVALID, never FAIL or PASS.
                        s.numbers["carryingAtBlast"] = 1;
                        var before = new Dictionary<string, IntVec3>();
                        string[] spared = { "big", "pit", "pitstack", "carrier", "sleeper", "corpse" };
                        s.stagedCells = spared.Where(k => k != "sleeper").ToDictionary(k => k, k => s.things[k].Position);
                        const int holdFrom = 1;
                        for (int d = holdFrom; d <= 68; d++)
                        {
                            int dd = d;
                            RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + dd, () =>
                            {
                                foreach (string k in spared)
                                {
                                    if (s.things[k] is Pawn sp && sp.Spawned && k != "sleeper")
                                    {
                                        sp.pather?.StopDead();
                                    }
                                }
                                if (dd >= 55 && dd < 60 && sleeper.Spawned && !sleeper.InBed() && !bed.Destroyed)   // it got up once in 3 runs (visit 1)
                                {
                                    sleeper.jobs.StartJob(JobMaker.MakeJob(JobDefOf.LayDown, bed), JobCondition.InterruptForced);
                                }
                                if (dd >= 55 && dd <= 64 && carrier.carryTracker.CarriedThing != carried && carried.Spawned)
                                {
                                    carrier.carryTracker.TryStartCarry(carried, 1, reserve: false);   // the count overload despawns it (SplitOff)
                                }
                                if (dd >= 60 && dd <= 64 && carrier.Spawned && carrier.carryTracker.CarriedThing != carried)
                                {
                                    s.numbers["carryingAtBlast"] = 0;
                                }
                                if (dd == 60)
                                {
                                    foreach (string k in spared)
                                    {
                                        if (s.things[k].Spawned)
                                        {
                                            before[k] = s.things[k].Position;
                                        }
                                    }
                                    Blast(s.o, 2.9f);
                                }
                                if (dd == 68)
                                {
                                    foreach (string k in spared)
                                    {
                                        if (s.things[k].Spawned)
                                        {
                                            atBlast[k] = s.things[k].Position;
                                        }
                                    }
                                }
                            }));
                        }
                        s.preBlast = before;
                        s.atBlast = atBlast;
                    }
                    s.verdict = sc =>
                    {
                        if (!sc.numbers.TryGetValue("carryingAtBlast", out float cab) || cab < 1f)
                        {
                            return "INVALID " + sc.name + " the carrier was not carrying its pawn at the blast";
                        }
                        string off = string.Join(", ", sc.stagedCells.Select(kv =>
                        {
                            bool seen = sc.preBlast.TryGetValue(kv.Key, out IntVec3 pre);
                            return RM_KnockbackVerdicts.SparedOffCell(kv.Key, seen, pre.x, pre.z, kv.Value.x, kv.Value.z);
                        }).Where(x => x != null));
                        if (off.Length > 0)
                        {
                            return "INVALID " + sc.name + " off its staged cell at the blast (origin " + sc.o.x + "," + sc.o.z + "): " + off;
                        }
                        var want = new Dictionary<string, string> { ["big"] = "too_heavy_creature", ["pit"] = "in_pit", ["pitstack"] = "in_pit",
                            ["carrier"] = "carrying_pawn", ["sleeper"] = "in_bed", ["corpse"] = "too_heavy" };
                        var sb = new StringBuilder();
                        bool ok = ((Pawn)sc.things["sleeper"]).InBed() || ForThing(sc, "skip", sc.things["sleeper"]).Count > 0;
                        if (!ok)
                        {
                            return "INVALID " + sc.name + " the sleeper never lay in the bed before the blast";
                        }
                        foreach (var kv in want)
                        {
                            Thing t = sc.things[kv.Key];
                            bool skip = ForThing(sc, "skip", t).Any(r => (string)r["reason"] == kv.Value);
                            bool stayed = sc.atBlast != null && sc.atBlast.TryGetValue(kv.Key, out IntVec3 atBlast)
                                ? sc.preBlast != null && sc.preBlast.TryGetValue(kv.Key, out IntVec3 pre) && atBlast == pre : kv.Key == "carrier";
                            ok &= skip && stayed && ForThing(sc, "launch", t).Count == 0;
                            sb.Append(kv.Key).Append(skip ? " " + kv.Value : " NO " + kv.Value).Append(stayed ? "" : " MOVED").Append("; ");
                        }
                        return Result(sc, ok, sb.ToString() + "blast at +60 ticks (step 300)");
                    };
                    return null;

                case "blast_kinds":
                    {
                        // sc_blast_kinds, the vanilla lanes (each colonist one cell east of its impact, lanes 3 cells apart):
                        // frag (Bomb), Bomb-child BombSuper, an incendiary shell (Flame), the same shell swapped to Bomb, and
                        // EMP, smoke, stun, extinguish and toxic gas. The Outer Rim lanes (sonic, plasma) and the unpatched
                        // modded lane at percent 0 are not staged here: listed UNBUILT (their mod is not on the minimal list).
                        ThingDef shell = DefDatabase<ThingDef>.GetNamedSilentFail("Shell_Incendiary");
                        var lanes = new List<(string key, DamageDef dt, ThingDef proj)>
                        {
                            ("frag", DamageDefOf.Bomb, null), ("bombsuper", DefDatabase<DamageDef>.GetNamedSilentFail("BombSuper"), null),
                            ("flame", DamageDefOf.Flame, shell), ("swapped", DamageDefOf.Bomb, shell),
                            ("emp", DamageDefOf.EMP, null), ("smoke", DamageDefOf.Smoke, null), ("stun", DamageDefOf.Stun, null),
                            ("extinguish", DamageDefOf.Extinguish, null), ("toxgas", DefDatabase<DamageDef>.GetNamedSilentFail("ToxGas"), null),
                        };
                        if (lanes.Any(l => l.dt == null) || shell == null)
                        {
                            return "a lane's damage type or the incendiary shell is not loaded";
                        }
                        for (int i = 0; i < lanes.Count; i++)
                        {
                            IntVec3 c = O(s, (i % 3) * 5 - 6, (i / 3) * 5 - 5);
                            Colonist(s, lanes[i].key, c + IntVec3.East);
                            NoHarm.Add(s.things[lanes[i].key].thingIDNumber);
                            Boom(Map, c, 1.9f, lanes[i].dt, 1, lanes[i].proj);
                        }
                        Action prev = s.restore;
                        s.restore = () => { foreach (Thing t in s.things.Values) NoHarm.Remove(t.thingIDNumber); prev?.Invoke(); };
                    }
                    s.verdict = sc =>
                    {
                        float Pct(string k)
                        {
                            var rq = ForThing(sc, "request", sc.things[k]);
                            return rq.Count == 1 ? 100f * Convert.ToSingle(rq[0]["force"]) / Math.Max(1e-4f, Convert.ToSingle(rq[0]["damageRatio"])) : -1f;
                        }
                        Moved(sc, "flame", out Thing _, out int fc);
                        Moved(sc, "swapped", out Thing _, out int bc);
                        bool flame = Math.Abs(Pct("flame") - 50f) < 0.5f && Math.Abs(Pct("swapped") - 100f) < 0.5f && fc <= (bc + 1) / 2 + 1;
                        bool frag = Math.Abs(Pct("frag") - 100f) < 0.5f && Math.Abs(Pct("bombsuper") - 100f) < 0.5f;
                        var quiet = new[] { "emp", "smoke", "stun", "extinguish", "toxgas" };
                        bool zeros = quiet.All(k => ForThing(sc, "request", sc.things[k]).Count == 0 && sc.things[k].Position == sc.starts[k]);
                        return Result(sc, flame && frag && zeros, "flame%=" + Pct("flame") + " swapped%=" + Pct("swapped") + " cells " + fc + "/" + bc
                            + " frag%=" + Pct("frag") + " bombsuper%=" + Pct("bombsuper") + " harmless quiet=" + zeros);
                    };
                    return null;

                case "pawn_arc":
                    {
                        // sc_pawn_arc: a colonist ordered to haul a stack to a stockpile is thrown; a walker ordered onto the
                        // landing planned at launch arrives mid-flight. Traced every tick: holder, drawn position, job. Control:
                        // a third pawn moved by a debug teleport of the same distance, traced the same way.
                        Zone_Stockpile zone = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, Map.zoneManager);
                        Map.zoneManager.RegisterZone(zone);
                        zone.AddCell(O(s, 1, -5));
                        Action prev = s.restore;
                        s.restore = () => { if (zone.zoneManager != null) zone.Delete(); prev?.Invoke(); };
                        Pawn p = Colonist(s, "p", O(s, 1, 0), drafted: false);
                        Thing st = Item(s, "st", "Steel", 20, O(s, 1, 0));
                        Job haul = JobMaker.MakeJob(JobDefOf.HaulToCell, st, O(s, 1, -5));
                        haul.count = st.stackCount;
                        haul.haulMode = HaulMode.ToCellStorage;
                        p.jobs.TryTakeOrderedJob(haul);
                        if (p.CurJobDef != JobDefOf.HaulToCell || p.CurJob.targetA.Thing != st)
                        {
                            return "the colonist's current job is not a haul of the stack";
                        }
                        // one cell from the planned landing O(4,0), a colonist of at least 4.4 cells/s, ordered there now: three cells
                        // out, or ordered at the launch line, it cannot arrive inside a ~17-tick flight (visit 1, 2026-11-15)
                        Pawn w = null;
                        for (int i = 0; i < 8; i++)
                        {
                            w = Colonist(s, "w", O(s, 4, 1), drafted: true);
                            if (w.GetStatValue(StatDefOf.MoveSpeed) >= 4.4f)
                            {
                                break;
                            }
                            w.Destroy();
                        }
                        if (w.Destroyed)
                        {
                            return "no colonist of move speed 4.4 in 8 tries";
                        }
                        w.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, O(s, 4, 0)));
                        Pawn tp = Colonist(s, "tp", O(s, -4, 4), drafted: true);
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
                                var launch = ForThing(s, "launch", p);
                                if (launch.Count == 1 && !s.numbers.ContainsKey("plannedX"))
                                {
                                    IntVec3 to = (IntVec3)launch[0]["to"];
                                    s.numbers["plannedX"] = to.x;
                                    s.numbers["plannedZ"] = to.z;
                                    s.numbers["launchTick"] = dd;
                                    if (to != O(s, 4, 0))   // re-ordering restarts the walker's step: it then arrives on the landing tick
                                    {
                                        w.jobs.TryTakeOrderedJob(JobMaker.MakeJob(JobDefOf.Goto, to));
                                    }
                                }
                                if (!p.Spawned && p.ParentHolder is PawnFlyer f && f.def == RM_KnockbackDefOf.RM_PawnFlyer_Knockback && s.numbers.ContainsKey("plannedX"))
                                {
                                    float x = f.DrawPos.x, sx = s.starts["p"].x + 0.5f, ex = (float)s.numbers["plannedX"] + 0.5f;
                                    if (x > Math.Min(sx, ex) + 0.05f && x < Math.Max(sx, ex) - 0.05f)
                                    {
                                        s.numbers["between"] = s.numbers.TryGetValue("between", out float b) ? b + 1 : 1;
                                    }
                                    if (s.numbers.ContainsKey("plannedX") && w.Position.x == (int)s.numbers["plannedX"] && w.Position.z == (int)s.numbers["plannedZ"])
                                    {
                                        s.numbers["walkerInFlight"] = dd;
                                    }
                                }
                                if (p.Spawned && s.numbers.ContainsKey("launchTick") && !s.numbers.ContainsKey("landTick"))
                                {
                                    s.numbers["landTick"] = dd;
                                }
                                if (s.numbers.ContainsKey("landTick") && !s.numbers.ContainsKey("stunEnd") && p.stances?.stunner != null && !p.stances.stunner.Stunned)
                                {
                                    s.numbers["stunEnd"] = dd;
                                }
                                if (s.numbers.ContainsKey("stunEnd") && !s.numbers.ContainsKey("rehaul") && p.CurJob != null
                                    && (p.CurJobDef == JobDefOf.HaulToCell || p.CurJobDef == JobDefOf.HaulToContainer) && p.CurJob.targetA.Thing == st)
                                {
                                    s.numbers["rehaul"] = dd;
                                }
                                if (dd == 5 && tp.Spawned)
                                {
                                    IntVec3 c = tp.Position + new IntVec3(3, 0, 0);
                                    tp.DeSpawn();
                                    GenSpawn.Spawn(tp, c, m0);
                                    if (tp.drafter != null)
                                    {
                                        tp.drafter.Drafted = true;   // respawned undrafted, it hauled the dropped stack itself (visit 1)
                                    }
                                }
                                if (dd >= 4 && dd <= 7 && (!tp.Spawned || tp.ParentHolder is PawnFlyer))
                                {
                                    s.numbers["tpHeld"] = 1;
                                }
                            }));
                        }
                        // the blast goes off two ticks after the walker's order (live 2026-11-17: INVALID 4 of 9 runs on one site,
                        // "the walker never stood on the planned cell between launch and landing"). A walker of 4.4 to 4.6 cells/s
                        // needs 16 or 17 ticks for its one cell of soil and the flight lands 18 ticks after the blast, so a tick or
                        // two of job start decided the row. Two ticks' head start puts it there with the same margin again, and
                        // still after the launch (the colonist is in the air from the blast's next tick).
                        Map blastMap = Map;
                        IntVec3 blastAt = s.o;
                        RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + 2, () =>
                        {
                            if (blastMap == Find.CurrentMap)
                            {
                                Blast(blastAt, 2.9f);
                            }
                        }));
                    }
                    s.verdict = sc =>
                    {
                        Pawn p = (Pawn)sc.things["p"];
                        if (!sc.numbers.ContainsKey("plannedX"))
                        {
                            return "INVALID " + sc.name + " no launch line for the colonist";
                        }
                        if (!sc.numbers.ContainsKey("walkerInFlight"))
                        {
                            return "INVALID " + sc.name + " the walker never stood on the planned cell between launch and landing";
                        }
                        var planned = new IntVec3((int)sc.numbers["plannedX"], 0, (int)sc.numbers["plannedZ"]);
                        bool arc = sc.numbers.TryGetValue("between", out float bt) && bt >= 1;
                        bool onPlanned = p.Spawned && sc.numbers.ContainsKey("landTick") && ForThing(sc, "redirect", p).Count == 0
                            && ForThing(sc, "land", p).Any(r => (IntVec3)r["at"] == planned);
                        bool hitWalker = ForThing(sc, "land_on_pawn", p).Any(r => (int)r["pawnId"] == sc.things["w"].thingIDNumber);
                        bool stun = sc.numbers.ContainsKey("stunEnd") && sc.numbers["stunEnd"] - sc.numbers["landTick"] <= RimMandrakeExplosiveKnockbackSettings.landingStunMax;
                        bool rehaul = sc.numbers.ContainsKey("rehaul");
                        bool control = !sc.numbers.ContainsKey("tpHeld");
                        return Result(sc, arc && onPlanned && hitWalker && stun && rehaul && control, "arcTicks=" + bt + " planned=" + planned.x + "," + planned.z
                            + " onPlanned=" + onPlanned + " hitWalker=" + hitWalker + " stun=" + stun + " rehaul=" + rehaul + " teleportControlClean=" + control
                            + " (step 900 ticks)");
                    };
                    return null;

                case "pit_goods_fetch":
                    {
                        // sc_pit_fetch: a stack and a corpse on a pit floor with a lowered ladder; a stockpile and a corpse
                        // stockpile outside; one free hauler. Control: the same in a second pit whose ladder is raised.
                        // RIMMANDRAKE_FIX_DRY_PIT_HAULER_DESCENT_SWIMS_HID_IT (live 2026-11-16, the hauler's job log): with the pits
                        // dry the hauler went down and picked the stack up, then vanilla's duplicate pickup
                        // (Toils_Haul.CheckForGetOpportunityDuplicate: a same-def stack within 8 cells, a region search FlowWorks'
                        // reach veto never sees) retargeted it at the control stack 6 cells off; that pit's ladder is raised, the
                        // path errored, the stack was dropped on the ladder cell, all day. The control pit now sits in the far
                        // corner (13+ cells), and the main pit is 5 wide so the corpse lies inside it, not on an edge row a
                        // hauler on the rim can touch (RIMMANDRAKE_MOVE_PIT_FETCH_CORPSE_OFF_RIM_TOUCHED_ABOVE). Offline guard:
                        // selftest_explosiveknockback_pit_fetch.py. The FlowWorks defect itself is filed for FlowWorks.
                        if (!RM_KnockbackCompat.FlowWorks || !Pit(O(s, 3, 4), 5, 3) || !Pit(O(s, -7, -7), 3, 3))
                        {
                            return "FlowWorks not loaded / dig failed";
                        }
                        // Visit 2 (2026-11-15, SITE): over 60000 ticks FlowWorks' rain filled both pits to 2 m, and dug water 2 m deep
                        // is swum (owner R12): the hauler swam into the raised-ladder control and carried its steel out. Rain stays
                        // out of the excavations for this scene; the player's value comes back at the verdict.
                        var rf = AccessTools.Field(AccessTools.TypeByName("RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"), "rainFillsExcavationsEnabled");
                        if (rf == null)
                        {
                            return "FlowWorks' rainFillsExcavationsEnabled setting not found";
                        }
                        object rfWas = rf.GetValue(null);
                        rf.SetValue(null, false);
                        Action prevRain = s.restore;
                        s.restore = () => { rf.SetValue(null, rfWas); prevRain?.Invoke(); };
                        // The control is a fixed RM_Ladder: FlowWorks never counts a portable ladder raised
                        // (RM_CompLadder.EffectivelyRaised = raised && !Props.portable && ...), so a raised portable one left
                        // the control pit open (RIMMANDRAKE_TRACE_PIT_FETCH_CONTROL_STACK_PAST_RAISED_LADDER).
                        ThingDef ld = DefDatabase<ThingDef>.GetNamedSilentFail("RM_LadderPortable");
                        ThingDef fixedLd = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Ladder");
                        var lowered = AccessTools.Method(AccessTools.TypeByName("RimMandrake.FlowWorks.RM_ClimbJoins"), "LoweredLadderAt", new[] { typeof(Map), typeof(IntVec3) });
                        if (ld == null || fixedLd == null || lowered == null)
                        {
                            return "the FlowWorks ladder defs or RM_ClimbJoins.LoweredLadderAt is not loaded";
                        }
                        Thing Ladder(ThingDef def, IntVec3 rim, IntVec3 edge)
                        {
                            foreach (IntVec3 at in new[] { rim, edge })
                            {
                                foreach (Rot4 r in new[] { Rot4.East, Rot4.West, Rot4.North, Rot4.South })
                                {
                                    Thing l = GenSpawn.Spawn(ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null), at, Map, r);
                                    l.SetFactionDirect(Faction.OfPlayer);
                                    if ((bool)lowered.Invoke(null, new object[] { Map, rim }) || (bool)lowered.Invoke(null, new object[] { Map, edge }))
                                    {
                                        return l;
                                    }
                                    l.Destroy();
                                }
                            }
                            return null;
                        }
                        Thing lad = Ladder(ld, O(s, 2, 5), O(s, 3, 5));
                        Thing ctl = Ladder(fixedLd, O(s, -6, -4), O(s, -6, -5));
                        if (lad == null || ctl == null)
                        {
                            return "no placement of RM_LadderPortable / RM_Ladder reads as a lowered ladder at the pit rim";
                        }
                        ThingComp comp = ((ThingWithComps)ctl).AllComps.FirstOrDefault(c => c.GetType().Name == "RM_CompLadder");
                        var setRaised = comp == null ? null : AccessTools.Method(comp.GetType(), "SetRaised", new[] { typeof(bool) });
                        if (setRaised == null)
                        {
                            return "the control ladder has no RM_CompLadder.SetRaised";
                        }
                        // SetRaised, not a field write: it also clears reachability and bumps the climb masks.
                        setRaised.Invoke(comp, new object[] { true });
                        if ((bool)lowered.Invoke(null, new object[] { Map, O(s, -6, -4) }) || (bool)lowered.Invoke(null, new object[] { Map, O(s, -6, -5) }))
                        {
                            return "the raised control ladder still reads lowered (FlowWorks' ladders can be raised and lowered setting off?)";
                        }
                        Item(s, "st", "Steel", 20, O(s, 4, 5));
                        Item(s, "cst", "Steel", 20, O(s, -6, -6));
                        Pawn dead = Colonist(s, "dead", O(s, 6, 5), drafted: false);
                        dead.Kill(null);
                        // live 2026-11-16: vanilla forbids a corpse that dies outside the home area (Pawn.Kill ->
                        // SetForbiddenIfOutsideHomeArea), so no one hauled it; the scene's corpse is allowed, as the stack is
                        dead.Corpse?.SetForbidden(false, warnOnFail: false);
                        Track(s, "corpse", dead.Corpse);
                        var zones = new List<Zone>();
                        var za = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, Map.zoneManager);
                        Map.zoneManager.RegisterZone(za);
                        za.AddCell(O(s, 0, 6));
                        var zb = new Zone_Stockpile(StorageSettingsPreset.DumpingStockpile, Map.zoneManager);
                        Map.zoneManager.RegisterZone(zb);
                        zb.AddCell(O(s, 0, 4));
                        zones.Add(za);
                        zones.Add(zb);
                        Action prev = s.restore;
                        s.restore = () => { foreach (Zone z in zones) if (z.zoneManager != null) z.Delete(); prev?.Invoke(); };
                        if (!za.GetStoreSettings().AllowedToAccept(s.things["st"]) || !zb.GetStoreSettings().AllowedToAccept(s.things["corpse"]))
                        {
                            return "a stockpile does not accept its thing";
                        }
                        // live 2026-11-16: a generated colonist often cannot haul (the scene went INVALID 4 runs in 7), and the
                        // map's other colonists hauled too, so "the hauler used the ladder" read the wrong pawn. The hauler is
                        // regenerated until it can haul, and every other colonist's hauling is off for the scene (put back after).
                        Pawn h = null;
                        for (int tries = 0; tries < 12 && (h == null || h.WorkTypeIsDisabled(WorkTypeDefOf.Hauling)); tries++)
                        {
                            if (h != null)
                            {
                                s.things.Remove("h");
                                h.Destroy(DestroyMode.Vanish);
                            }
                            h = Colonist(s, "h", O(s, 0, 0), drafted: false);
                        }
                        if (h.WorkTypeIsDisabled(WorkTypeDefOf.Hauling))
                        {
                            return "the hauler cannot haul (12 colonists generated)";
                        }
                        var others = Map.mapPawns.FreeColonistsSpawned.Where(p => p != h && p.workSettings != null
                            && p.workSettings.EverWork && p.workSettings.GetPriority(WorkTypeDefOf.Hauling) > 0)
                            .Select(p => new KeyValuePair<Pawn, int>(p, p.workSettings.GetPriority(WorkTypeDefOf.Hauling))).ToList();
                        foreach (var kv in others)
                        {
                            kv.Key.workSettings.SetPriority(WorkTypeDefOf.Hauling, 0);
                        }
                        Action prevHaul = s.restore;
                        s.restore = () =>
                        {
                            foreach (var kv in others)
                            {
                                if (!kv.Key.Destroyed && kv.Key.workSettings != null)
                                {
                                    kv.Key.workSettings.SetPriority(WorkTypeDefOf.Hauling, kv.Value);
                                }
                            }
                            prevHaul?.Invoke();
                        };
                        // visit 3 (2026-11-16, SITE): after 53 scenes the map held their corpses and steel; the hauler carried
                        // them into this scene's stockpiles, the stack merged into another and the corpse was moved off its
                        // cell (2 FAIL of 2 there, 2 PASS of 2 on a fresh map). Every haulable that is not the scene's is
                        // forbidden for the scene and allowed again after.
                        var mine = new HashSet<Thing>(s.things.Values);
                        var foreign = Map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver)
                            .Where(t => t.Spawned && !mine.Contains(t) && t.TryGetComp<CompForbiddable>() != null && !t.IsForbidden(Faction.OfPlayer))
                            .ToList();
                        foreach (Thing t in foreign)
                        {
                            t.SetForbidden(true, warnOnFail: false);
                        }
                        Action prevForbid = s.restore;
                        s.restore = () =>
                        {
                            foreach (Thing t in foreign)
                            {
                                if (!t.Destroyed)
                                {
                                    t.SetForbidden(false, warnOnFail: false);
                                }
                            }
                            prevForbid?.Invoke();
                        };
                        s.numbers["foreignForbidden"] = foreign.Count;
                        // RIMMANDRAKE_SHRINK_KNOCKBACK_SCENES_ONE_SAVE_IN_AIR (2026-11-25): the hauler was left at large for up to a
                        // day (60000 ticks) to choose its own work; 6 of 12 runs did not pass. The two hauls are now ORDERED (the
                        // stack, then the corpse, each to the storage HaulToStorageJob picks), the hauler's needs are held full
                        // so no meal or bed interrupts it, its path cells are read, and the scene runs 5000 ticks.
                        // An ordered haul skips the free-will test a hauler at large meets (reach included), so the free-will
                        // answer is read first and judged: the lowered-ladder pit's goods haulable, the raised-ladder control's
                        // not (fresh reader, 2026-11-25: a reach veto that shut the lowered pit would else pass on the order).
                        s.numbers["autoHaulMain"] = HaulAIUtility.PawnCanAutomaticallyHaulFast(h, s.things["st"], false)
                            && HaulAIUtility.PawnCanAutomaticallyHaulFast(h, s.things["corpse"], false) ? 1 : 0;
                        s.numbers["autoHaulControl"] = HaulAIUtility.PawnCanAutomaticallyHaulFast(h, s.things["cst"], false) ? 1 : 0;
                        Job jSt = HaulAIUtility.HaulToStorageJob(h, s.things["st"], true);
                        Job jCorpse = HaulAIUtility.HaulToStorageJob(h, s.things["corpse"], true);
                        if (jSt == null || jCorpse == null)
                        {
                            return "no storage job for the " + (jSt == null ? "stack" : "corpse") + " (HaulToStorageJob null: no reachable stockpile cell)";
                        }
                        if (!h.jobs.TryTakeOrderedJob(jSt, JobTag.Misc))
                        {
                            return "the hauler refused the ordered haul of the stack";
                        }
                        h.jobs.jobQueue.EnqueueLast(jCorpse, JobTag.Misc);
                        s.numbers["ordered"] = 2;
                        Map m0 = Map;
                        var ladderCells = new HashSet<IntVec3> { lad.Position, O(s, 2, 5), O(s, 3, 5) };
                        for (int d = 10; d <= PitFetchTicks; d += 10)
                        {
                            RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + d, () =>
                            {
                                if (m0 != Find.CurrentMap || !h.Spawned)
                                {
                                    return;
                                }
                                foreach (Need n in new Need[] { h.needs?.food, h.needs?.rest, h.needs?.joy })
                                {
                                    if (n != null)
                                    {
                                        n.CurLevelPercentage = 1f;
                                    }
                                }
                                if (RM_KnockbackCompat.IsSuperdeep(m0, h.Position))
                                {
                                    s.numbers["haulerInPit"] = 1;
                                }
                                List<IntVec3> nodes = h.pather?.curPath?.NodesReversed;
                                if (nodes != null && nodes.Any(c => RM_KnockbackCompat.IsSuperdeep(m0, c)))
                                {
                                    s.numbers["pathIntoPit"] = 1;
                                    if (nodes.Any(c => ladderCells.Contains(c)))
                                    {
                                        s.numbers["pathViaLadder"] = 1;
                                    }
                                }
                            }));
                        }
                    }
                    s.verdict = sc =>
                    {
                        Thing st = sc.things["st"], cst = sc.things["cst"], corpse = sc.things["corpse"];
                        Map m = Map;
                        bool stOut = st.Spawned && !RM_KnockbackCompat.IsSuperdeep(m, st.Position) && m.zoneManager.ZoneAt(st.Position) is Zone_Stockpile;
                        bool corpseOut = corpse.Destroyed ? false : corpse.Spawned ? !RM_KnockbackCompat.IsSuperdeep(m, corpse.Position)
                            && m.zoneManager.ZoneAt(corpse.Position) is Zone_Stockpile : corpse.ParentHolder is Building_Grave;
                        bool inPit = sc.numbers.ContainsKey("haulerInPit"), pathIn = sc.numbers.ContainsKey("pathIntoPit");
                        bool ladder = inPit || pathIn;
                        bool control = cst.Spawned && RM_KnockbackCompat.IsSuperdeep(m, cst.Position);
                        float am = sc.numbers.TryGetValue("autoHaulMain", out float amv) ? amv : -1f;
                        float ac = sc.numbers.TryGetValue("autoHaulControl", out float acv) ? acv : -1f;
                        bool reach = am == 1f && ac == 0f;
                        return Result(sc, stOut && corpseOut && ladder && control && reach, "free-will haul: main " + am + " control " + ac
                            + " (want 1, 0); stack out=" + stOut + " corpse out=" + corpseOut + " hauler in pit=" + inPit
                            + " path into pit=" + pathIn + " path via ladder cell=" + sc.numbers.ContainsKey("pathViaLadder")
                            + " raised-ladder control stack still in its pit=" + control + " (2 hauls ordered, needs held, step " + PitFetchTicks + " ticks)");
                    };
                    return null;

                case "mass_and_power":
                case "mass_and_power_x2":
                case "mass_and_power_off":
                case "mass_and_power_off_x2":
                case "mass_and_power_250":
                case "mass_and_power_250_x2":
                    return MassAndPower(s);

                case "hose_carry_drop":
                case "hose_carry_drop_off":
                    return HoseCarryDrop(s);
                case "closed_containers":
                case "closed_containers_control":
                    return ClosedContainers(s);
                case "frame_probe_selfcheck":
                case "frame_probe_selfcheck_paused":
                    return FrameProbeSelfCheck(s);
                case "barrage_perf":
                case "barrage_perf_off":
                    return BarragePerf(s);
                case "settings_sweep":
                case "settings_sweep_after":
                    return SettingsSweep(s);
                case "goods_obstacles":
                case "goods_obstacles_control":
                    // the pokes sit here, beside the restore that undoes them, in the file whose Stage catch and Verdict run it
                    s.restore = FlightRestore(s);
                    RimMandrakeExplosiveKnockbackSettings.flyingGoods = true;
                    RimMandrakeExplosiveKnockbackSettings.goodsRebound = true;
                    return GoodsObstacles(s);
                case "storeroom_bomb_pit":
                case "storeroom_bomb_pit_control":
                    return StoreroomBombPit(s);
            }
            if (s.name.StartsWith("settings_sweep_"))   // one lane per SweepLanes key
            {
                return SettingsSweep(s);
            }
            return "unknown scene " + s.name;
        }

        /// <summary>sc_mass_and_power (design/concepts/ExplosiveKnockback/scenes.json; owner cards 2026-11-13 "Cutoff -> A mass
        /// limit", "Blast power -> Type x damage"): the lightest loaded animal N, a clothed colonist with a sidearm E, the heaviest
        /// animal under 150 kg S and a 220-260 kg animal W (chosen by mass, ByMass),
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
                    PinnedMass.Remove(t.thingIDNumber);
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

            PawnKindDef smallKind = SmallAnimal(), underKind = UnderLimitAnimal(), heavyKind = HeavyAnimal();
            Pawn small = Adult(smallKind);
            Pawn under = Adult(underKind);
            Pawn heavy = Adult(heavyKind);
            GenSpawn.Spawn(small, O(s, 0, 1), Map);
            Track(s, "small", small);
            GenSpawn.Spawn(under, O(s, 0, -1), Map);
            Track(s, "under", under);
            GenSpawn.Spawn(heavy, O(s, -1, 0), Map);
            Track(s, "heavy", heavy);
            // a colonist with a revolver, drawn at 45-76 kg as the kernel weighs it (Mass stat minus inventory: worn clothes add
            // nothing, MEASURED live 2026-11-13 at 48.75 and 60.75 kg, so a 64-76 draw never came in 40 tries), then its kernel mass
            // PINNED into 64-76 kg by the test-only PinnedMass hook (judge gap g4, the Conductor's decision 2026-11-14): under 63.5 kg
            // a colonist ties a capped light animal at damage 100, against the oracle's "light > colonist"; over 76.9 a 144 kg one at 50
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
            Track(s, "colonist", col);
            PinnedMass[col.thingIDNumber] = Math.Min(76f, Math.Max(64f, col.GetStatValue(StatDefOf.Mass) - MassUtility.InventoryMass(col)));
            if (col.drafter != null)
            {
                col.drafter.Drafted = true;
            }

            KbSettings k = RimMandrakeExplosiveKnockbackSettings.Kernel();
            float ratio = RM_KnockbackMath.DamageRatio(damage, RM_Patch_DamageWorker_ExplosionKnockback.RefDamageOf(DamageDefOf.Bomb),
                RimMandrakeExplosiveKnockbackSettings.blastPowerRefPercent, RimMandrakeExplosiveKnockbackSettings.blastPowerFromDamage);
            s.numbers["ratio"] = ratio;
            var bands = new Dictionary<string, (float lo, float hi)>
            {
                ["small"] = (0.1f, 30f), ["colonist"] = (64f, 76f), ["under"] = (100f, 150f), ["heavy"] = (150.001f, 1000f),
            };
            foreach (string key in Keys)
            {
                var p = (Pawn)s.things[key];
                float mass = PinnedMass.TryGetValue(p.thingIDNumber, out float pin) ? pin : p.GetStatValue(StatDefOf.Mass) - MassUtility.InventoryMass(p);
                if (mass < bands[key].lo || mass > bands[key].hi)
                {
                    return key + " " + p.kindDef.label + " weighs " + mass.ToString("0.0") + " kg, outside " + bands[key].lo.ToString("0") + "-" + bands[key].hi.ToString("0");
                }
                s.numbers["mass_" + key] = mass;
                s.numbers["want_" + key] = RM_KnockbackMath.Eligible(KbKind.Pawn, mass, k)
                    ? RM_KnockbackMath.ThrowCells(1f, 2.9f, 1f * ratio, mass, k) : 0f;
                // injuries only: a hot afternoon gave a colonist Heatstroke in the window, which is not the hook's to stop (visit 1)
                s.numbers["hediffs_" + key] = p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury || h is Hediff_MissingPart);
                NoHarm.Add(p.thingIDNumber);
            }
            Boom(Map, s.o, 2.9f, DamageDefOf.Bomb, damage, null, true);
            s.verdict = sc => MassAndPowerVerdict(sc, damage, lane);
            return null;
        }

        private static readonly string[] Keys = { "small", "colonist", "under", "heavy" };

        private static string MassAndPowerVerdict(Scene sc, int damage, string lane)
        {
            var sb = new StringBuilder();
            bool ok = true;
            var cells = new Dictionary<string, int>();
            var dirs = new Dictionary<string, IntVec3> { ["small"] = IntVec3.North, ["colonist"] = IntVec3.East, ["under"] = IntVec3.South, ["heavy"] = IntVec3.West };
            foreach (string key in Keys)
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
                int newHediffs = p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury || h is Hediff_MissingPart) - (int)sc.numbers["hediffs_" + key];
                if (newHediffs > 0)
                {
                    return "INVALID " + sc.name + " the injury hook let " + newHediffs + " hediff(s) through on " + key;
                }
                cells[key] = want == 0 ? 0 : got;
                ok &= rowOk && reqOk;
                sb.Append(" " + key + "(" + Named(p, sc.numbers["mass_" + key]) + ")=" + (want == 0 ? "spared" : got.ToString())
                    + "/want " + want + (rowOk ? "" : "!") + (reqOk ? "" : " request!"));
            }
            bool order = cells["small"] >= cells["colonist"] && cells["colonist"] > cells["under"] && cells["under"] > cells["heavy"]
                && (lane == "250" ? cells["heavy"] > 0 : cells["heavy"] == 0) && (cells["small"] > cells["colonist"] || cells["small"] == 6);
            return Result(sc, ok && order, "lane=" + lane + " damage=" + damage + " ratio=" + sc.numbers["ratio"].ToString("0.00")
                + sb + " order=" + order);
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
