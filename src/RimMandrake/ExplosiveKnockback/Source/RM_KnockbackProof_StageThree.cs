#if RM_PROOFS
// Proof build only (RM_PROOFS). The five scenes Stage 3 owed the 0.1.0 bars (RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN,
// 2026-11-14): sc_hose_drop, sc_closed_containers, sc_settings_sweep, sc_frame_probe_check and sc_barrage_perf in
// design/concepts/ExplosiveKnockback/scenes.json, each with its control lane. NOT YET RUN LIVE. Commands: version/test_table.json.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.ExplosiveKnockback
{
    public static partial class RM_KnockbackProof
    {
        // ── sc_hose_drop: hose_carry_drop (and its control hose_carry_drop_off) ──────────────────────

        /// <summary>A colonist on a real RM_CarryHoseEnd job from a FlowWorks reel; when the colonist has walked 4 cells out
        /// carrying the end, a Bomb lands one cell south. Main: the throw drops the end on the takeoff cell (Dropped, no
        /// carrier, the reel's end cell is the takeoff cell), the launch line says hoseDropped, the landing is 3 cells out.
        /// Control (_off, Settings enabled false): the same blast, no launch line, the colonist still carries the end.</summary>
        private static string HoseCarryDrop(Scene s)
        {
            bool off = s.name.EndsWith("_off");
            if (!RM_KnockbackCompat.FlowWorks || !RM_KnockbackCompat.Hoses)
            {
                return "FlowWorks hose reels not hooked (flowworks=" + RM_KnockbackCompat.FlowWorks + " hoses=" + RM_KnockbackCompat.Hoses + ")";
            }
            JobDef carryJob = DefDatabase<JobDef>.GetNamedSilentFail("RM_CarryHoseEnd");
            if (DefDatabase<ThingDef>.GetNamedSilentFail("RM_HoseReel") == null || carryJob == null)
            {
                return "RM_HoseReel or RM_CarryHoseEnd not loaded";
            }
            Thing reel = Build("RM_HoseReel", O(s, -6, 0));
            Track(s, "reel", reel);
            ThingComp comp = (reel as ThingWithComps)?.AllComps.FirstOrDefault(c => c.GetType().Name == "CompHoseReel");
            if (comp == null)
            {
                return "the reel has no CompHoseReel";
            }
            Type ct = comp.GetType();
            Func<string> carry = () => Convert.ToString(AccessTools.Field(ct, "carry").GetValue(comp));
            Func<Pawn> carrier = () => AccessTools.Field(ct, "carrier").GetValue(comp) as Pawn;
            Func<IntVec3> endCell = () => (IntVec3)AccessTools.Property(ct, "EndCell").GetValue(comp);
            IntVec3 dest = O(s, 6, 0);
            string why = AccessTools.Method(ct, "OrderDeploy").Invoke(comp, new object[] { dest }) as string;
            if (why != null)
            {
                return "the reel refused the deploy order: " + why;
            }
            dest = (IntVec3)AccessTools.Field(ct, "pendingAt").GetValue(comp);   // the order's own target (ResolveTarget may move it)
            Pawn p = Colonist(s, "p", O(s, -4, 0), drafted: false);
            if (!p.jobs.TryTakeOrderedJob(JobMaker.MakeJob(carryJob, reel, dest), JobTag.Misc))
            {
                return "the colonist refused the RM_CarryHoseEnd job";
            }
            if (off)
            {
                bool was = RimMandrakeExplosiveKnockbackSettings.enabled;
                s.restore = () => RimMandrakeExplosiveKnockbackSettings.enabled = was;
                // restore-check: ok s.restore is set above; RM_KnockbackProof.Stage's catch runs it (RunRestore) when Build throws
                RimMandrakeExplosiveKnockbackSettings.enabled = false;
            }
            var obs = new Dictionary<string, string>();
            Map m0 = Map;
            for (int d = 1; d <= 400; d++)
            {
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + d, () =>
                {
                    int now = Find.TickManager.TicksGame;
                    if (s.numbers.TryGetValue("blastTick", out float bt))
                    {
                        if (!obs.ContainsKey("carry") && now >= bt + 3)
                        {
                            obs["carry"] = carry();
                            obs["carrier"] = carrier() == null ? "none" : carrier() == p ? "p" : carrier().LabelShort;
                            IntVec3 e = endCell();
                            obs["end"] = e.IsValid ? e.x + "," + e.z : "invalid";
                            obs["pCell"] = p.Spawned ? p.Position.x + "," + p.Position.z : "away";
                        }
                        return;
                    }
                    if (carry() == "Carrying" && carrier() == p && p.Spawned && Cheb(p.Position, reel.Position) >= 4)
                    {
                        s.starts["takeoff"] = p.Position;
                        s.numbers["blastTick"] = now;
                        s.numbers["hurtBefore"] = p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury);
                        Boom(m0, p.Position + IntVec3.South, 2.9f, DamageDefOf.Bomb, 5);
                    }
                }));
            }
            s.verdict = sc =>
            {
                if (!sc.numbers.ContainsKey("blastTick"))
                {
                    return "INVALID " + sc.name + " the colonist never carried the hose end 4 cells out (carry=" + carry() + " job="
                        + (p.CurJobDef?.defName ?? "none") + ")";
                }
                if (p.Dead || p.Downed)
                {
                    return "INVALID " + sc.name + " the carrier was downed or killed by the blast";
                }
                if (!obs.ContainsKey("carry"))
                {
                    return "INVALID " + sc.name + " the hose was not sampled after the blast";
                }
                IntVec3 to = sc.starts["takeoff"];
                string at = to.x + "," + to.z;
                var launch = ForThing(sc, "launch", p);
                bool hurt = p.health.hediffSet.hediffs.Count(h => h is Hediff_Injury) > sc.numbers["hurtBefore"];
                string detail = "takeoff=" + at + " carry=" + obs["carry"] + " carrier=" + obs["carrier"] + " end=" + obs["end"]
                    + " pCell=" + obs["pCell"] + " hurt=" + hurt + (launch.Count > 0 ? " [" + Rec(launch[0]) + "]" : " no launch line");
                if (off)
                {
                    // control: the blast alone (damage, interruption) does not drop the hose
                    return Result(sc, RM_KnockbackVerdicts.HoseControl(launch.Count, obs["carry"], obs["carrier"], obs["pCell"], at, hurt), detail);
                }
                bool hd = launch.Count == 1 && launch[0]["hoseDropped"] is bool hdv && hdv;
                int cheb = launch.Count == 1 && launch[0]["to"] is IntVec3 lt ? Cheb(lt, to) : -1;
                bool ok = RM_KnockbackVerdicts.HoseDrop(launch.Count, hd, obs["carry"], obs["carrier"], obs["end"], at, cheb,
                    out bool launched, out bool dropped, out bool three);
                return Result(sc, ok, "launched=" + launched + " dropped=" + dropped + " three=" + three + " " + detail);
            };
            return null;
        }

        // ── sc_closed_containers: closed_containers (and its control closed_containers_control) ───────

        private static readonly string[] Lockers = { "free", "wall", "pawn", "pit", "heavy" };

        /// <summary>One Bomb of 30 at radius 2.9 among closed containers: four LWM weapons lockers (free-, wall-, pawn- and
        /// pit-backed), a fifth filled to 76-249 kg, an LWM safe (500 kg), a 1x1 SealedCrate, a 2x2 AncientSecurityCrate and the
        /// Armoury's tagged secret floor panel holding loose goods. Control (_control): the same goods loose at the same cells,
        /// and the panel with its opt-in tag removed. The bar says "thrown a short way" (owner by card 2026-11-14 ~9:47 PM PST,
        /// OWNER:1794721689897638306, "Throw it, as built"; it said "slides one cell"): moved at least one cell away from the
        /// blast, never past the throw cap, journal container line action thrown. The bar's "drawn offset in the thing trace" has no instrument (no trace,
        /// and a jolt draws nothing): reported UNMEASURED.</summary>
        private static string ClosedContainers(Scene s)
        {
            bool control = s.name.EndsWith("_control");
            const string locker = "LWM_WeaponsLocker", safe = "LWM_Safe", crate = "SealedCrate", sec = "AncientSecurityCrate";
            const string panel = "guy762_SecretFloorPanel_darkwhiteoutlines";
            foreach (string d in new[] { locker, safe, crate, sec, panel })
            {
                if (DefDatabase<ThingDef>.GetNamedSilentFail(d) == null)
                {
                    return d + " not loaded (LWM's Deep Storage, Odyssey, Ideology and Jawa Armoury Rebalance are on this scene's list)";
                }
            }
            if (!RM_KnockbackCompat.FlowWorks)
            {
                return "FlowWorks not loaded: no pit for the pit-backed locker";
            }
            ThingDef panelDef = DefDatabase<ThingDef>.GetNamed(panel);
            var tag = panelDef.GetModExtension<RM_KnockbackClosedStorage>();
            if (tag == null || panelDef.thingClass == null || typeof(Building_Crate).IsAssignableFrom(panelDef.thingClass))
            {
                return panel + " carries no RM_KnockbackClosedStorage tag, or is a crate";
            }
            var cells = new Dictionary<string, IntVec3>
            {
                ["free"] = O(s, 1, 0), ["wall"] = O(s, -1, 0), ["pawn"] = O(s, 0, 1), ["pit"] = O(s, 0, -1), ["heavy"] = O(s, 1, 1),
                ["safe"] = O(s, -1, 1), ["crate"] = O(s, -1, -1), ["sec"] = O(s, 1, -2), ["panel"] = O(s, 2, 1),
            };
            Build("Wall", O(s, -2, 0));
            Colonist(s, "backer", O(s, 0, 2));
            if (!Pit(O(s, 0, -2), 1, 1))
            {
                return "the pit cell behind the pit-backed locker did not dig";
            }
            List<ThingDef> guns = DefDatabase<ThingDef>.AllDefsListForReading.Where(d => d.IsRangedWeapon && !d.MadeFromStuff && d.tradeability != Tradeability.None
                && !d.destroyOnDrop && d.GetStatValueAbstract(StatDefOf.Mass) >= 1f).OrderByDescending(d => d.GetStatValueAbstract(StatDefOf.Mass)).ToList();
            if (control)
            {
                // the same goods, loose at the same cells
                foreach (string k in Lockers)
                {
                    Item(s, "g_" + k, "Gun_Revolver", 1, cells[k]);
                }
                Item(s, "g_panel", "Steel", 20, cells["panel"]);
                // the panel, its tag removed by Stage (the guard's cache cleared both ways)
                s.restore = () => { if (!panelDef.modExtensions.Contains(tag)) panelDef.modExtensions.Add(tag); ClearClosedCache(panelDef); };
                // restore-check: ok s.restore is set on the line above; RM_KnockbackProof.Stage's catch runs it when Build throws
                panelDef.modExtensions.Remove(tag);
                ClearClosedCache(panelDef);
                Thing pn = Build(panel, O(s, -2, -3));
                Track(s, "panel", pn);
                Item(s, "pg", "Steel", 20, pn.Position);
                if (RM_KnockbackCompat.IsClosedContainer(pn))
                {
                    return "the untagged panel still classes closed";
                }
                Blast(O(s, -2, -2), 2.9f, DamageDefOf.Bomb, 30);   // the panel's own blast, one cell north of it
            }
            else
            {
                ThingDef lockerDef = DefDatabase<ThingDef>.GetNamed(locker);
                foreach (string k in Lockers)
                {
                    if (k == "heavy" && !RaiseLockerMass(s, lockerDef, RimMandrakeExplosiveKnockbackSettings.closedContainerMassLimit - 1f
                        - lockerDef.GetStatValueAbstract(StatDefOf.Mass, GenStuff.DefaultStuffFor(lockerDef))))
                    {
                        return locker + " has no LWM.DeepStorage.Properties maxTotalMass to raise";
                    }
                    Thing b = Build(locker, cells[k]);
                    Track(s, k, b);
                    Item(s, "g_" + k, "Gun_Revolver", 1, b.Position);
                }
                // the heavy locker: guns until its whole mass is 76-249 kg. As shipped LWM caps a weapons locker at 50 kg
                // (maxTotalMass) and 10 kg a weapon, so 58 kg with its own 8: RaiseLockerMass lifts the 50 the way Deep Storage's
                // own per-unit settings dialog does, and the guns go in as a player's would, its storage filter set to allow
                // them (defaultStorageSettings allows nothing; visit 1 read 9.4 kg because every gun was refused) and placed
                // through LWM's capacity check. RIMMANDRAKE_STAGE_HEAVY_LOCKER_LANE_LWM_CAPS_AT_58KG.
                Thing heavyBox = s.things["heavy"];
                StorageSettings heavySettings = (heavyBox as IStoreSettingsParent)?.GetStoreSettings();
                foreach (ThingDef g in guns)
                {
                    heavySettings?.filter?.SetAllow(g, true);
                }
                float total = Mass(heavyBox);
                int n = 0;
                // RIMMANDRAKE_FILL_HEAVY_LOCKER_REAL_MASS_ESTIMATE_FELL_SHORT: the fill reads the locker's REAL mass after every gun
                // (it summed the defs' abstract masses, which run high: 30 guns estimated at 76 kg weighed 74.9, INVALID in
                // visit 3 and again live 2026-11-17), and may take up to 60 guns
                for (bool any = true; any && total < 76f && n < 60;)
                {
                    any = false;
                    foreach (ThingDef g in guns)
                    {
                        if (total >= 76f || n >= 60)
                        {
                            break;
                        }
                        float gm = g.GetStatValueAbstract(StatDefOf.Mass, GenStuff.DefaultStuffFor(g));
                        if (total + gm > 249f || !(heavySettings?.AllowedToAccept(g) ?? false))
                        {
                            continue;
                        }
                        Thing t = ThingMaker.MakeThing(g, GenStuff.DefaultStuffFor(g));
                        GenPlace.TryPlaceThing(t, heavyBox.Position, Map, ThingPlaceMode.Direct, out Thing placed);
                        if (placed != null && placed.Spawned && placed.Position == heavyBox.Position)
                        {
                            total = Mass(heavyBox);
                            n++;
                            any = true;
                        }
                        else if (!t.Destroyed && !t.Spawned)
                        {
                            t.Destroy();
                        }
                    }
                }
                s.numbers["heavyMass"] = Mass(heavyBox);
                Track(s, "safe", Build(safe, cells["safe"]));
                Item(s, "g_safe", "Silver", 50, cells["safe"]);
                Thing cr = Build(crate, cells["crate"]);
                Track(s, "crate", cr);
                (cr as IThingHolder)?.GetDirectlyHeldThings()?.TryAdd(ThingMaker.MakeThing(ThingDefOf.Steel));
                Track(s, "sec", Build(sec, cells["sec"]));
                Thing pn = Build(panel, cells["panel"]);
                Track(s, "panel", pn);
                Item(s, "g_panel", "Steel", 20, pn.Position);
                foreach (string k in new[] { "free", "wall", "pawn", "pit", "heavy", "safe", "crate", "sec", "panel" })
                {
                    if (!RM_KnockbackCompat.IsClosedContainer(s.things[k]))
                    {
                        return k + " (" + s.things[k].def.defName + ") is not classed closed";
                    }
                    s.numbers["goods_" + k] = GoodsOn(s.things[k]).Count;
                }
                s.numbers["crateMass"] = Mass(cr);
                s.numbers["limit"] = RimMandrakeExplosiveKnockbackSettings.closedContainerMassLimit;
                if (s.numbers["crateMass"] >= 250f)
                {
                    return "the sealed crate weighs " + s.numbers["crateMass"] + " kg, not under 250";
                }
            }
            // a 300-tick advance draws few frames and a jolt lives 20 ticks: draw its frame each tick, through the shipped drawing code
            RM_MapComponent_Knockback jolter = Map.GetComponent<RM_MapComponent_Knockback>();
            for (int d = 1; d <= 60; d++)
            {
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + d, () => jolter.MapComponentUpdate()));
            }
            Blast(s.o, 2.9f, DamageDefOf.Bomb, 30);
            s.verdict = sc =>
            {
                if (control)
                {
                    int flew = Lockers.Count(k => { Moved(sc, "g_" + k, out Thing _, out int c); return c >= 1; });
                    string mp = Moved(sc, "pg", out Thing _, out int pc);
                    return Result(sc, flew == Lockers.Length && pc >= 1, "looseFlew=" + flew + "/" + Lockers.Length + " untaggedPanel " + mp);
                }
                var rows = new List<string>();
                bool ok = true;
                if (!(sc.numbers["heavyMass"] >= 76f && sc.numbers["heavyMass"] <= 249f))
                {
                    rows.Add("heavy=INVALID mass " + sc.numbers["heavyMass"].ToString("0.#") + " kg");
                }
                foreach (string k in new[] { "free", "heavy", "crate" })
                {
                    if (k == "heavy" && rows.Count > 0)
                    {
                        continue;
                    }
                    Thing b = sc.things[k];
                    var line = ForThing(sc, "container", b);
                    int c = b.Spawned ? Cheb(b.Position, sc.starts[k]) : -1;
                    bool away = b.Spawned && Cheb(b.Position, sc.o) > Cheb(sc.starts[k], sc.o);
                    bool held = k == "crate" || (GoodsOn(b).Count == (int)sc.numbers["goods_" + k]);
                    bool thrown = line.Count == 1 && (string)line[0]["action"] == "thrown";
                    bool row = RM_KnockbackVerdicts.ContainerThrown(c, RimMandrakeExplosiveKnockbackSettings.maxThrowCells, away, thrown, held);
                    ok &= row;
                    rows.Add(k + "=" + (row ? "thrown" : "FAIL") + " cells=" + c + " away=" + away + " held=" + held
                        + " action=" + (line.Count > 0 ? (string)line[0]["action"] : "none") + "x" + line.Count);
                }
                foreach (string k in new[] { "wall", "pawn", "pit", "safe", "sec" })
                {
                    Thing b = sc.things[k];
                    var line = ForThing(sc, "container", b);
                    bool stayed = b.Spawned && b.Position == sc.starts[k];
                    bool jolt = line.Count == 1 && (string)line[0]["action"] == "jolt";
                    bool held = k == "sec" || GoodsOn(b).Count == (int)sc.numbers["goods_" + k];
                    float drawn = RM_MapComponent_Knockback.JoltDrawn.TryGetValue(b.thingIDNumber, out float jd) ? jd : 0f;
                    bool row = stayed && jolt && held && drawn > 0f;
                    ok &= row;
                    rows.Add(k + "=" + (row ? "jolted" : "FAIL") + " stayed=" + stayed + " held=" + held + " lines=" + line.Count
                        + " action=" + (line.Count > 0 ? (string)line[0]["action"] : "none") + " drawnOffset=" + drawn.ToString("0.000"));
                }
                {
                    Thing pn = sc.things["panel"];
                    bool kept = GoodsOn(pn).Count == (int)sc.numbers["goods_panel"] && sc.things["g_panel"].Spawned
                        && pn.Spawned && sc.things["g_panel"].Position == pn.Position;
                    ok &= kept;
                    rows.Add("panel=" + (kept ? "kept" : "FAIL") + " goods on its cell=" + GoodsOn(pn).Count);
                }
                bool invalid = rows.Any(r => r.Contains("INVALID"));
                string detail = string.Join("; ", rows) + " limit=" + sc.numbers["limit"] + " crateMass=" + sc.numbers["crateMass"].ToString("0.#");
                return invalid ? "INVALID " + sc.name + " " + detail : Result(sc, ok, detail);
            };
            return null;
        }

        /// <summary>Raise LWM's per-unit maxTotalMass on <paramref name="d"/> to <paramref name="kg"/> for this scene (the field
        /// Deep Storage's per-unit settings dialog edits; restored when the scene ends). Comps spawned after read it; a comp
        /// that copied it at spawn is caught after Build by the caller's capacity check, not here.</summary>
        private static bool RaiseLockerMass(Scene s, ThingDef d, float kg)
        {
            object props = d.comps?.FirstOrDefault(c => c.GetType().FullName == "LWM.DeepStorage.Properties");
            FieldInfo f = props?.GetType().GetField("maxTotalMass", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
            if (f == null || f.FieldType != typeof(float))
            {
                return false;
            }
            float was = (float)f.GetValue(props);
            Action prev = s.restore;
            s.restore = () => { f.SetValue(props, was); prev?.Invoke(); };
            // restore-check: ok s.restore is set on the line above; RM_KnockbackProof.Stage's catch runs it when Build throws
            f.SetValue(props, Math.Max(was, kg));
            return true;
        }

        private static float Mass(Thing b)
        {
            float m = b.GetStatValue(StatDefOf.Mass);
            foreach (Thing g in GoodsOn(b))
            {
                m += g.GetStatValue(StatDefOf.Mass) * g.stackCount;
            }
            if (b is IThingHolder h && h.GetDirectlyHeldThings() is ThingOwner o)
            {
                foreach (Thing g in o)
                {
                    m += g.GetStatValue(StatDefOf.Mass) * g.stackCount;
                }
            }
            return m;
        }

        private static List<Thing> GoodsOn(Thing b)
        {
            return b.Spawned ? b.Position.GetThingList(b.Map).Where(t => t.def.category == ThingCategory.Item).ToList() : new List<Thing>();
        }

        private static void ClearClosedCache(ThingDef d)
        {
            (AccessTools.Field(typeof(RM_KnockbackCompat), "closedByDef")?.GetValue(null) as IDictionary)?.Remove(d);
        }

        // ── sc_settings_sweep: settings_sweep (default), settings_sweep_<lane>, settings_sweep_after (control) ─────

        /// <summary>The game-side lanes (the kernel-side lines are T_SETTINGS_SWEEP_OFFLINE). Each lane: its fields and
        /// values, and the observations it may change; every other observation must equal the default run's.
        /// closedGuard switches closedContainerGuard and fireHalf switches fireAtHalf (blind cycle 2, steward's decision 6).</summary>
        private static readonly Dictionary<string, KeyValuePair<string[], string[]>> SweepLanes = new Dictionary<string, KeyValuePair<string[], string[]>>
        {
            ["throwAnimals"] = Lane(new[] { "throwAnimals=False" }, "A"),
            ["throwMechanoids"] = Lane(new[] { "throwMechanoids=False" }, "M"),
            ["throwDowned"] = Lane(new[] { "throwDowned=False" }, "D"),
            ["throwItems"] = Lane(new[] { "throwItems=False" }, "G", "Gcell", "H", "gasGoods"),
            ["throwCorpses"] = Lane(new[] { "throwCorpses=False" }, "C"),
            ["landingStun"] = Lane(new[] { "landingStunMin=30", "landingStunMax=40" }, "stun"),
            ["doorsTakeDamage"] = Lane(new[] { "doorsTakeDamage=False" }, "door"),
            ["debugDrawVectors"] = Lane(new[] { "debugDrawVectors=True" }, "draws"),
            ["vanillaCratesClosed"] = Lane(new[] { "vanillaCratesClosed=False" }, "crate"),
            ["heavyGoodsMinMass"] = Lane(new[] { "heavyGoodsMinMass=100" }, "H"),
            ["heavyGoodsKnock"] = Lane(new[] { "heavyGoodsKnock=False" }, "H"),
            // flyingGoods off skips goods AND corpses with flying_off (RIMMANDRAKE_SKIP_GOODS_WHEN_FLIGHT_OFF_OLD_HOP_LINGERED): C is its own
            ["flyingGoods"] = Lane(new[] { "flyingGoods=False" }, "G", "Gcell", "H", "gasGoods", "C"),
            ["shoveClosedContainers"] = Lane(new[] { "shoveClosedContainers=False" }, "locker", "crate"),
            ["gasChain"] = Lane(new[] { "gasChain=False" }, "gas", "gasGoods"),
            ["lightMassLimit20"] = Lane(new[] { "lightMassLimit=20" }, "C", "H"),
            ["closedGuard"] = Lane(new[] { "closedContainerGuard=False" }, "locker", "lockerGoods", "G", "Gcell", "H"),
            ["fireHalf"] = Lane(new[] { "fireAtHalf=False" }),
            // the blast show off (bar blast_show_switches_off_clean): every throw observation equals the default run's
            ["showOff"] = Lane(new[] { "showFireAndFlash=False", "showScreenShake=False", "showAirRipple=False", "showCraterScars=False",
                                       "showSmoke=False", "showSootOnThings=False", "showSootOnPawns=False",
                                       "showShakeStrength=0", "showMarksLast=0" }),
        };

        private static KeyValuePair<string[], string[]> Lane(string[] set, params string[] changes) => new KeyValuePair<string[], string[]>(set, changes);

        /// <summary>The default run's observations, kept for every later lane (the runner runs settings_sweep first).</summary>
        private static Dictionary<string, string> sweepDefault;
        /// <summary>Every saved field's value read in the default run, for the after-control.</summary>
        private static Dictionary<string, string> sweepFieldDefaults;
        /// <summary>Debug-vector draws counted by the map component (proof build only).</summary>
        internal static int VectorDraws;

        /// <summary>The sweep list: the scene's action list plus enabled and shieldsAbsorbThrow.</summary>
        private static readonly string[] SweepFields =
        {
            "strength", "maxThrowCells", "ownCapScale", "unpatchedHarmfulPercent", "creatureMassLimit", "closedContainerMassLimit",
            "vanillaCratesClosed", "blastPowerFromDamage", "throwAnimals", "throwMechanoids", "throwDowned", "throwItems", "throwCorpses",
            "lightMassLimit", "heavyGoodsMinMass", "sandbagsStopThrow", "impactDamageEnabled", "impactDamagePerCell", "landingStunMin",
            "landingStunMax", "recoveryWindowTicks", "doorsTakeDamage", "throwIntoPits", "shieldDebitPerForce", "debugDrawVectors",
            "blastPowerRefPercent", "thrownGoodsBlastDamagePercent", "goodsWallImpactPerCell", "goodsFlightSpeed", "goodsArcHeight",
            "goodsSpinDegPerTick", "goodsRebound", "goodsReboundKeepPercent", "openStorageProtectsGoods", "heavyGoodsDamageMin",
            "heavyGoodsDamageMax", "heavyGoodsStaggerTicks", "gasBurstRadius", "gasBurstGoodsCells", "gasPawnCooldownTicks",
            "flyingGoods", "shoveClosedContainers", "heavyGoodsKnock", "gasChain", "enabled", "shieldsAbsorbThrow",
            "closedContainerGuard", "fireAtHalf", "showFireAndFlash", "showScreenShake", "showAirRipple", "showCraterScars",
            "showSmoke", "showSootOnThings", "showSootOnPawns", "showShakeStrength", "showMarksLast",
        };

        private static IEnumerable<System.Reflection.FieldInfo> SavedFields() => typeof(RimMandrakeExplosiveKnockbackSettings)
            .GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static)
            .Where(f => !f.IsInitOnly && !f.IsLiteral && (f.FieldType == typeof(bool) || f.FieldType == typeof(int) || f.FieldType == typeof(float)));

        private static string SettingsSweep(Scene s)
        {
            string lane = s.name == "settings_sweep" ? "default" : s.name == "settings_sweep_after" ? "after" : s.name.Substring("settings_sweep_".Length);
            if (lane != "default" && lane != "after" && !SweepLanes.ContainsKey(lane))
            {
                return "unknown sweep lane " + lane + " (lanes: " + string.Join(",", SweepLanes.Keys) + ")";
            }
            if (lane != "default" && sweepDefault == null)
            {
                return "run settings_sweep (the default lane) first in the same session";
            }
            MapComponent vg = VentGas(out Type vt);
            if (vg == null)
            {
                return "the Cauldron (mandrake.rm.cauldron) not loaded: no vent gas";
            }
            if (DefDatabase<ThingDef>.GetNamedSilentFail("LWM_WeaponsLocker") == null)
            {
                return "LWM's Deep Storage (lwm.deepstorage) not loaded: no LWM_WeaponsLocker";
            }
            var head = new List<string>();
            if (lane == "default")
            {
                // every saved field is on the sweep list, and no cap or body-size field survives
                var saved = new HashSet<string>(SavedFields().Select(f => f.Name));
                var listed = new HashSet<string>(SweepFields);
                var extra = saved.Except(listed).ToList();
                var missing = listed.Except(saved).ToList();
                var banned = new[] { "maxThrowsPerExplosion", "maxItemThrowsPerMapTick", "immuneBodySize" }.Where(saved.Contains).ToList();
                head.Add("fields=" + (extra.Count == 0 && missing.Count == 0 && banned.Count == 0 ? "equal" : "DIFFER extra[" + string.Join(",", extra)
                    + "] missing[" + string.Join(",", missing) + "] banned[" + string.Join(",", banned) + "]"));
                head.Add("kernel=" + KernelReadBack());
                sweepFieldDefaults = SavedFields().ToDictionary(f => f.Name, f => Convert.ToString(f.GetValue(null), System.Globalization.CultureInfo.InvariantCulture));
            }
            else if (lane != "after")
            {
                var restore = new List<KeyValuePair<System.Reflection.FieldInfo, object>>();
                foreach (string kv in SweepLanes[lane].Key)
                {
                    string[] p = kv.Split('=');
                    var f = typeof(RimMandrakeExplosiveKnockbackSettings).GetField(p[0]);
                    restore.Add(new KeyValuePair<System.Reflection.FieldInfo, object>(f, f.GetValue(null)));
                    f.SetValue(null, Convert.ChangeType(p[1], f.FieldType, System.Globalization.CultureInfo.InvariantCulture));
                }
                s.restore = () => { foreach (var r in restore) r.Key.SetValue(null, r.Value); };
            }
            SweepLane(s, vg, vt, out Func<Dictionary<string, string>> observe);
            s.verdict = sc =>
            {
                Dictionary<string, string> obs = observe();
                string seen = string.Join(" ", obs.Select(kv => kv.Key + "=" + kv.Value));
                int stun = obs.TryGetValue("stunTicks", out string st) && int.TryParse(st, out int sv) ? sv : -1;
                if (lane == "default")
                {
                    bool all = new[] { "P", "A", "M", "D", "G", "C" }.All(k => obs[k] == "thrown") && obs["door"] == "hurt" && obs["draws"] == "no"
                        && obs["crate"] != "none" && obs["locker"] != "none" && obs["H"] == "knocked" && obs["gas"] == "burst"
                        && stun >= RimMandrakeExplosiveKnockbackSettings.landingStunMin - 2 && stun <= RimMandrakeExplosiveKnockbackSettings.landingStunMax + 2;
                    sweepDefault = obs;
                    return Result(sc, all && head.All(h => !h.Contains("DIFFER") && !h.Contains("FAIL")), string.Join(" ", head) + " " + seen);
                }
                string[] changes = lane == "after" ? new string[0] : SweepLanes[lane].Value;
                var drift = obs.Keys.Where(k => k != "stunTicks" && !changes.Contains(k) && sweepDefault.TryGetValue(k, out string dv) && dv != obs[k]).ToList();
                bool own;
                switch (lane)
                {
                    case "after":
                        var unset = SavedFields().Where(f => sweepFieldDefaults.TryGetValue(f.Name, out string dv)
                            && dv != Convert.ToString(f.GetValue(null), System.Globalization.CultureInfo.InvariantCulture)).Select(f => f.Name).ToList();
                        own = unset.Count == 0;
                        seen = "unsetAfter[" + string.Join(",", unset) + "] " + seen;
                        break;
                    case "throwAnimals": own = obs["A"].StartsWith("skip:animals_off"); break;
                    case "throwMechanoids": own = obs["M"].StartsWith("skip:mechanoids_off"); break;
                    case "throwDowned": own = obs["D"].StartsWith("skip:downed_off"); break;
                    case "throwItems": own = obs["G"].StartsWith("skip:items_off") && obs["H"] == "no"; break;
                    case "throwCorpses": own = obs["C"].StartsWith("skip:corpses_off"); break;
                    case "landingStun": own = stun >= 28 && stun <= 42; break;
                    case "doorsTakeDamage": own = obs["door"] == "whole"; break;
                    case "debugDrawVectors": own = obs["draws"] == "yes" || !Prefs.DevMode; break;
                    case "vanillaCratesClosed": own = obs["crate"] == "none"; break;
                    case "heavyGoodsMinMass":
                    case "heavyGoodsKnock": own = obs["H"] == "no"; break;
                    case "flyingGoods": own = obs["G"].StartsWith("skip:") && obs["Gcell"] == "same" && obs["C"].StartsWith("skip:flying_off"); break;
                    case "shoveClosedContainers": own = obs["locker"] == "none" && obs["lockerGoods"] == "kept"; break;
                    case "gasChain": own = obs["gas"] == "none"; break;
                    case "lightMassLimit20": own = obs["P"] == "thrown"; break;
                    // the locker's goods are thrown loose: no longer on the locker's cell after the blast
                    case "closedGuard": own = obs["lockerGoods"] == "lost"; seen = "lockerGoods=" + obs["lockerGoods"] + " " + seen; break;
                    // fire throws nothing: a Flame damage type's resolved force is 0 with the switch off (read while it is off)
                    case "fireHalf":
                        float ff = RM_Patch_DamageWorker_ExplosionKnockback.ConfigOf(null, DamageDefOf.Flame).force;
                        own = ff <= 0f;
                        seen = "flameForce=" + ff.ToString("0.###") + " " + seen;
                        break;
                    // the show's switches read while off: no part of the show is on, and the throws (drift) are the default's
                    case "showOff":
                        KbShowSwitches sw = RM_KnockbackShow.Switches();
                        own = !sw.fireAndFlash && !sw.screenShake && !sw.airRipple && !sw.craterScars && sw.shakeStrength == 0f;
                        seen = "showSwitches=" + (own ? "off" : "ON") + " " + seen;
                        break;
                    default: own = false; break;
                }
                if (lane == "debugDrawVectors" && !Prefs.DevMode)
                {
                    return "INVALID " + sc.name + " the vector overlay draws only in dev mode";
                }
                return Result(sc, own && drift.Count == 0, "own=" + own + " drift[" + string.Join(",", drift) + "] " + seen);
            };
            return null;
        }

        /// <summary>One Settings -> Kernel() read-back per kernel-side setting: set it, read the kernel's copy, put it back.</summary>
        private static string KernelReadBack()
        {
            var bad = new List<string>();
            void Rb(string field, object v, Func<KbSettings, bool> read)
            {
                var f = typeof(RimMandrakeExplosiveKnockbackSettings).GetField(field);
                object was = f.GetValue(null);
                try
                {
                    f.SetValue(null, v);
                    if (!read(RimMandrakeExplosiveKnockbackSettings.Kernel()))
                    {
                        bad.Add(field);
                    }
                }
                finally
                {
                    f.SetValue(null, was);
                }
            }
            Rb("strength", 0.5f, k => k.globalMultiplier == 0.5f);
            Rb("maxThrowCells", 2, k => k.maxCells == 2);
            Rb("ownCapScale", 0.5f, k => RimMandrakeExplosiveKnockbackSettings.Kernel(4).maxCells == RM_KnockbackMath.CapFor(4, RimMandrakeExplosiveKnockbackSettings.maxThrowCells, 0.5f));
            Rb("creatureMassLimit", 90f, k => k.creatureMassLimit == 90f);
            Rb("lightMassLimit", 60f, k => k.lightMassLimit == 60f);
            Rb("impactDamageEnabled", false, k => !k.impactEnabled);
            Rb("impactDamagePerCell", 8f, k => k.impactPerCell == 8f);
            Rb("sandbagsStopThrow", true, k => k.sandbagsStop);
            Rb("throwIntoPits", false, k => !k.intoPits);
            return bad.Count == 0 ? "9/9" : "FAIL[" + string.Join(",", bad) + "]";
        }

        /// <summary>The sweep's lane, identical in every run. Main blast at the origin (radius 2.9): colonist P east, an animal
        /// A under 90 kg west, a mech M under 90 kg north, a downed colonist D south, 10 steel G south-west, a small corpse C
        /// north-east. Door lane at (-5,5): colonist Q thrown east into a door. Heavy lane at (5,5): 30 steel (15 kg) thrown
        /// west at colonist H. Container lane at (5,-5): a SealedCrate west, an LWM weapons locker east, each free-backed.
        /// Gas lane at (-5,-5): a radius-1 puff of the Cauldron's vent gas, 10 steel beside it, lit by its own Ignite.</summary>
        /// <summary>ByMass among the kinds that cannot fly. Visit 2 run 3 (2026-11-26, SITE): the middle kind under 90 kg on
        /// the visit tier was RM_FireWasp, a flyer; it took off on its own before the fireHalf blast, and the mod rightly spared
        /// it (skip: flying), so lane A read a drift that no setting made.</summary>
        internal static PawnKindDef GroundedByMass(string band, float lo, float hi, string prefer)
        {
            float mid = (lo + hi) / 2f;
            var inBand = AnimalKinds().Where(k => KindMass(k) >= lo && KindMass(k) < hi
                && k.race.GetStatValueAbstract(StatDefOf.MaxFlightTime) <= 0f).ToList();
            if (inBand.Count == 0)
            {
                throw new InvalidOperationException("no loaded animal kind that cannot fly for the " + band + " band, "
                    + lo.ToString("0.#") + "-" + hi.ToString("0.#") + " kg adult");
            }
            return inBand.OrderBy(k => Official(k) ? 1 : 0)
                .ThenBy(k => prefer == "light" ? KindMass(k) : prefer == "heavy" ? -KindMass(k) : Math.Abs(KindMass(k) - mid))
                .ThenBy(k => k.defName, StringComparer.Ordinal).First();
        }

        private static void SweepLane(Scene s, MapComponent vg, Type vt, out Func<Dictionary<string, string>> observe)
        {
            Map map = Map;
            Pawn P = Colonist(s, "P", O(s, 1, 0));
            Pawn A = Adult(GroundedByMass("under 90 kg", 5f, 90f, "middle"));
            GenSpawn.Spawn(A, O(s, -1, 0), map);
            Track(s, "A", A);
            PawnKindDef mk = DefDatabase<PawnKindDef>.AllDefsListForReading.Where(k => k.RaceProps != null && k.RaceProps.IsMechanoid
                && k.race.GetStatValueAbstract(StatDefOf.Mass) < 90f && k.race.GetStatValueAbstract(StatDefOf.Mass) > 5f)
                .OrderBy(k => k.defName == "Mech_Militor" ? 0 : 1).ThenBy(k => k.defName, StringComparer.Ordinal).FirstOrDefault();
            if (mk == null)
            {
                throw new InvalidOperationException("no mech kind under 90 kg loaded");
            }
            Pawn M = PawnGenerator.GeneratePawn(mk, Faction.OfPlayer);
            GenSpawn.Spawn(M, O(s, 0, 1), map);
            Track(s, "M", M);
            Pawn D = Colonist(s, "D", O(s, 0, -1), drafted: false);
            HealthUtility.DamageUntilDowned(D, false);
            Item(s, "G", "Steel", 10, O(s, -1, -1));
            Pawn cp = Adult(SmallAnimal());
            GenSpawn.Spawn(cp, O(s, 1, 1), map);
            cp.Kill(null);
            Track(s, "C", cp.Corpse);
            Pawn Q = Colonist(s, "Q", O(s, -4, 5));
            Thing door = Build("Door", O(s, -2, 5));
            Track(s, "door", door);
            s.numbers["doorHp"] = door.HitPoints;
            Item(s, "Hs", "Steel", 30, O(s, 4, 5));
            Pawn H = Colonist(s, "H", O(s, 2, 5));
            Thing crate = Build("SealedCrate", O(s, 4, -5));
            Track(s, "crate", crate);
            Thing lk = Build("LWM_WeaponsLocker", O(s, 6, -5));
            Track(s, "locker", lk);
            Item(s, "lg", "Gun_Revolver", 1, lk.Position);
            vt.GetMethod("ClearOf")?.Invoke(null, new object[] { map });
            vt.GetMethod("SeedCloud").Invoke(null, new object[] { map, O(s, -5, -5), 1, 250 });
            // inside the seeded cloud, so a burst always reaches it (two cells out it was reached on 13 of 18 lanes: visit 1)
            Item(s, "gg", "Steel", 10, O(s, -5, -4));
            Action prev = s.restore;
            s.restore = () => { vt.GetMethod("ClearOf")?.Invoke(null, new object[] { map }); prev?.Invoke(); };
            int draws0 = VectorDraws;
            Blast(s.o, 2.9f);
            Blast(O(s, -5, 5), 2.9f);
            Blast(O(s, 5, 5), 2.9f);
            Blast(O(s, 5, -5), 2.9f);
            vt.GetMethod("Ignite").Invoke(vg, new object[] { O(s, -5, -5), null });
            // the landing stun of P: away (in the flyer), back, then the tick the stun ends
            for (int d = 1; d <= 290; d++)
            {
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + d, () =>
                {
                    int now = Find.TickManager.TicksGame;
                    if (!P.Spawned) { s.numbers["away"] = 1; return; }
                    if (s.numbers.ContainsKey("away") && !s.numbers.ContainsKey("land")) s.numbers["land"] = now;
                    if (s.numbers.ContainsKey("land") && !s.numbers.ContainsKey("stunEnd") && !P.stances.stunner.Stunned) s.numbers["stunEnd"] = now;
                }));
            }
            observe = () =>
            {
                var o = new Dictionary<string, string>();
                foreach (string k in new[] { "P", "A", "M", "D", "G", "C" })
                {
                    o[k] = Fate(s, k);
                }
                o["Gcell"] = s.things["G"].Spawned && s.things["G"].Position == s.starts["G"] ? "same" : "moved";
                o["stunTicks"] = s.numbers.ContainsKey("stunEnd") ? ((int)(s.numbers["stunEnd"] - s.numbers["land"])).ToString() : "UNMEASURED";
                o["door"] = !door.Destroyed && door.HitPoints == (int)s.numbers["doorHp"] ? "whole" : "hurt";
                o["draws"] = VectorDraws > draws0 ? "yes" : "no";
                var cl = ForThing(s, "container", crate);
                o["crate"] = cl.Count > 0 ? (string)cl[0]["action"] : "none";
                var ll = ForThing(s, "container", lk);
                o["locker"] = ll.Count > 0 ? (string)ll[0]["action"] : "none";
                o["lockerGoods"] = s.things["lg"].Spawned && lk.Spawned && s.things["lg"].Position == lk.Position ? "kept" : "lost";
                o["H"] = Recs(s, "heavy_hit").Any(r => r.TryGetValue("pawnId", out object id) && Convert.ToInt32(id) == H.thingIDNumber) ? "knocked" : "no";
                o["gas"] = Recs(s, "gas_burst").Count > 0 ? "burst" : "none";
                o["gasGoods"] = s.things["gg"].Spawned && s.things["gg"].Position == s.starts["gg"] ? "still" : "moved";
                return o;
            };
        }

        /// <summary>"thrown" (a launch, item_move or container line), "skip:&lt;reason&gt;", or "still".</summary>
        private static string Fate(Scene s, string key)
        {
            Thing t = s.things[key];
            if (ForThing(s, "launch", t).Count + ForThing(s, "item_move", t).Count > 0)
            {
                return "thrown";
            }
            var sk = ForThing(s, "skip", t);
            return sk.Count > 0 ? "skip:" + sk[0]["reason"] : "still";
        }

        // ── sc_frame_probe_check and sc_barrage_perf: the frame-time probe ───────────────────────────

        /// <summary>True once frame_probe_selfcheck has passed in this session (barrage_perf's start line).</summary>
        private static bool probeSelfCheckPassed;
        private static float barrageBaselineWorst = -1f, barrageBaselineP99 = -1f;

        /// <summary>The barrage-and-gas-chain window in probe seconds: the first shell at stagedTick+60 (1.0 s) to the last
        /// gas burst or landing (at most 8.1 s in visit 2's journal), with margin; the bar reads the p99 frame inside it
        /// (owner 2026-11-15, "1 agree."; criterion_repairs/sc_barrage_perf_2026-11-15/FINDINGS.md).</summary>
        internal const float BarrageWindowLoS = 0.9f;
        internal const float BarrageWindowHiS = 8.25f;

        /// <summary>frame_probe_selfcheck (unpaused at normal speed) and frame_probe_selfcheck_paused (the control). Starts
        /// the probe, sleeps one frame 100 ms at +30 ticks, fires a grenade into five stacks at +60; the Verdict stops it.
        /// Run with the runner's --ticks 0 --real-seconds 8: stepping ticks inside one frame is not frames.</summary>
        private static string FrameProbeSelfCheck(Scene s)
        {
            bool paused = s.name.EndsWith("_paused");
            for (int i = 0; i < 5; i++)
            {
                Item(s, "g" + i, "Steel", 10, O(s, i - 2, 1));
            }
            TimeSpeed was = Find.TickManager.CurTimeSpeed;
            Find.TickManager.CurTimeSpeed = paused ? TimeSpeed.Paused : TimeSpeed.Normal;
            s.restore = () => { RM_FrameProbe.Stop(); Find.TickManager.CurTimeSpeed = was; };
            RM_FrameProbe.Begin();
            Map m0 = Map;
            if (paused)
            {
                RM_FrameProbe.SleepNextMs = 100;   // ticks do not run while paused: sleep at once
            }
            else
            {
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + 30, () => RM_FrameProbe.SleepNextMs = 100));
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + 60, () => Boom(m0, O(s, 0, 0), 2.9f, DamageDefOf.Bomb, 1)));
            }
            s.verdict = sc =>
            {
                KbFrameSummary g = RM_FrameProbe.Stop();
                bool check = KbFrameStats.SelfCheck(g, 100f, out string why);
                string detail = Summary(g) + " selfCheck=" + (check ? "pass" : why) + " rows=" + RM_FrameProbe.LastPath;
                if (paused)
                {
                    // the control: every row marked paused, and the self-check refuses it
                    return Result(sc, g.rows > 0 && g.pausedRows == g.rows && !check, detail);
                }
                bool ok = check && g.maxInAir > 0;
                probeSelfCheckPassed |= ok;
                return Result(sc, ok, detail);
            };
            return null;
        }

        private const float FullListOffP99Ms = 21.7f;   // measured: sc_barrage_perf visit 5, ArchBig, 314 mods, 2026-11-23

        /// <summary>barrage_perf (and barrage_perf_off, the mod off: the baseline). On any list (the tier is enough: owner
        /// 2026-11-16, "the smallest list to observe it is the best idea"; the cheapest test that decides the bar, 2026-11-23),
        /// barrage_perf_off first in the same session: a 10x10 stockpile, one stack on every cell, and a 40-cell cloud of the Cauldron's vent gas; six Bomb shells (radius 2.9,
        /// damage 50) into the stockpile half a second apart, then the cloud lit. The 99th-percentile unpaused frame inside
        /// the barrage-and-chain window (BarrageWindowLoS-HiS) at most 50 ms; the worst frame is reported, not judged.
        /// The bar is worded on the full list, so this run must also clear it there: the mod's own cost (this p99 less the same
        /// session's mod-off p99) added to the full list's measured mod-off p99 (FullListOffP99Ms) is at most 50 ms.
        /// Run frame_probe_selfcheck first in the same session; then --ticks 0 --real-seconds 25.</summary>
        private static string BarragePerf(Scene s)
        {
            bool off = s.name.EndsWith("_off");
            int mods = ModsConfig.ActiveModsInLoadOrder.Count();
            if (!probeSelfCheckPassed)
            {
                return "the frame probe's self-check has not passed this session: run frame_probe_selfcheck first";
            }
            MapComponent vg = VentGas(out Type vt);
            if (vg == null)
            {
                return "the Cauldron not loaded: no vent gas";
            }
            Map map = Map;
            Prepare(s.o, 12);
            var zone = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, map.zoneManager);
            map.zoneManager.RegisterZone(zone);
            string[] goods = { "Steel", "ComponentIndustrial", "WoodLog", "Cloth", "MealSurvivalPack", "Silver", "Plasteel", "Leather_Plain", "Gold", "MedicineIndustrial" };
            int stacks = 0;
            foreach (IntVec3 c in new CellRect(s.o.x - 11, s.o.z - 5, 10, 10))
            {
                zone.AddCell(c);
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(goods[stacks % goods.Length]) ?? ThingDefOf.Steel;
                Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
                t.stackCount = Math.Max(1, Math.Min(d.stackLimit, 20));
                if (GenPlace.TryPlaceThing(t, c, map, ThingPlaceMode.Direct))
                {
                    stacks++;
                }
            }
            vt.GetMethod("ClearOf")?.Invoke(null, new object[] { map });
            string seeded = (string)vt.GetMethod("SeedCloud").Invoke(null, new object[] { map, O(s, 6, 0), 3, 250 });
            bool was = RimMandrakeExplosiveKnockbackSettings.enabled;
            TimeSpeed speed = Find.TickManager.CurTimeSpeed;
            s.restore = () =>
            {
                RM_FrameProbe.Stop();
                RimMandrakeExplosiveKnockbackSettings.enabled = was;
                Find.TickManager.CurTimeSpeed = speed;
                vt.GetMethod("ClearOf")?.Invoke(null, new object[] { map });
                if (map.zoneManager.AllZones.Contains(zone)) zone.Delete();
            };
            if (off)
            {
                // restore-check: ok s.restore is set above; RM_KnockbackProof.Stage's catch runs it (RunRestore) when Build throws
                RimMandrakeExplosiveKnockbackSettings.enabled = false;
            }
            Find.TickManager.CurTimeSpeed = TimeSpeed.Normal;
            RM_FrameProbe.Begin();
            var shells = new[] { O(s, -9, -3), O(s, -4, -3), O(s, -9, 2), O(s, -4, 2), O(s, -6, 0), O(s, -2, 0) };
            for (int i = 0; i < shells.Length; i++)
            {
                IntVec3 at = shells[i];
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + 60 + 30 * i, () => Boom(map, at, 2.9f, DamageDefOf.Bomb, 50, null, true)));
            }
            RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + 300, () => vt.GetMethod("Ignite").Invoke(vg, new object[] { O(s, 6, 0), null })));
            s.verdict = sc =>
            {
                KbFrameSummary g = RM_FrameProbe.Stop(BarrageWindowLoS, BarrageWindowHiS);
                bool within = KbFrameStats.WithinBudget(g, 50f, out string why);
                int bursts = Recs(sc, "gas_burst").Count, launches = Recs(sc, "launch").Count + Recs(sc, "item_move").Count;
                string detail = Summary(g) + " budget=" + (within ? "within 50 ms" : why) + " mods=" + mods + " machine=" + Environment.MachineName
                    + " stacks=" + stacks + " cloud=" + seeded + " moves=" + launches + " gasBursts=" + bursts + " rows=" + RM_FrameProbe.LastPath;
                if (off)
                {
                    barrageBaselineWorst = g.worstMs;
                    barrageBaselineP99 = g.windowP99Ms;
                    return Result(sc, g.rows > 0 && g.pausedRows < g.rows / 10 + 1, "baseline " + detail);
                }
                if (launches == 0)
                {
                    return "INVALID " + sc.name + " nothing was thrown: " + detail;
                }
                if (barrageBaselineP99 < 0)
                {
                    return "INVALID " + sc.name + " no mod-off baseline this session (run barrage_perf_off first): " + detail;
                }
                float ours = Math.Max(0f, g.windowP99Ms - barrageBaselineP99);
                bool onFullList = FullListOffP99Ms + ours <= 50f;
                detail += " oursMs=" + ours.ToString("0.0") + " fullListP99Ms=" + (FullListOffP99Ms + ours).ToString("0.0") + (onFullList ? "" : " OVER 50");
                return Result(sc, within && onFullList, detail + " baselineWorstMs=" + (barrageBaselineWorst < 0 ? "UNMEASURED (run barrage_perf_off first)" : barrageBaselineWorst.ToString("0.0"))
                    + " baselineWindowP99Ms=" + (barrageBaselineP99 < 0 ? "UNMEASURED" : barrageBaselineP99.ToString("0.0")));
            };
            return null;
        }

        private static string Summary(KbFrameSummary g)
        {
            return "frames=" + g.framesElapsed + " probeRows=" + g.rows + " paused=" + g.pausedRows + " wall=" + g.wallSeconds.ToString("0.00") + "s worstMs="
                + g.worstMs.ToString("0.0") + " meanMs=" + g.meanMs.ToString("0.0") + " maxInAir=" + g.maxInAir
                + (float.IsPositiveInfinity(g.windowHiS) ? "" : " window=" + g.windowLoS + "-" + g.windowHiS + "s windowRows=" + g.windowRows
                    + " windowP99Ms=" + g.windowP99Ms.ToString("0.0"));
        }
    }

    /// <summary>Proof build only: the frame-time probe (leaf frame_time_probe). One row per rendered frame (Unity Update):
    /// real milliseconds since the previous frame, paused or not, and the knockback things in the air (carriers and thrown
    /// pawns). Stop writes the rows to RM_FrameProbe_&lt;stamp&gt;.csv in the game's data folder and returns the summary.</summary>
    public sealed class RM_FrameProbe : MonoBehaviour
    {
        private static RM_FrameProbe live;
        internal static int SleepNextMs;
        internal static string LastPath = "none";
        // the rate every recorded walk arm ran at while the window was visible (474 to 520 rows in 9.5 s). Vsync alone does not hold
        // a covered window: live 2026-11-23, 21 pairs read 517 to 2678 window frames in both arms, and a p99 over frames falls
        // as the rate rises, so the arms were not like for like
        internal const int ProbeFps = 60;
        private int priorVSync, priorTarget;
        private readonly List<float> ms = new List<float>();
        private readonly List<bool> paused = new List<bool>();
        private readonly List<int> inAir = new List<int>();
        private float firstReal = -1f, lastReal;
        private int firstFrame, lastFrame;
        // what each frame's mod work cost (the Test Pilot sitting on RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES): the
        // request flush, the pawn takeoffs inside it, the pawn landings (vanilla RespawnPawn included) and the job resume
        // inside them, plus gen-0 collections. Stopwatch timestamps at those call sites, no extra Harmony patches.
        internal static double FlushMs, PawnTakeoffMs, LandMs, ResumeMs;
        internal static int Takeoffs, Lands;
        private readonly List<string> parts = new List<string>();
        private int lastGc = -1;

        internal static double MsSince(long t0)
        {
            return (System.Diagnostics.Stopwatch.GetTimestamp() - t0) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
        }

        internal static void Begin()
        {
            Stop();
            var go = new GameObject("RM_FrameProbe");
            DontDestroyOnLoad(go);
            live = go.AddComponent<RM_FrameProbe>();
            live.priorVSync = QualitySettings.vSyncCount;
            live.priorTarget = Application.targetFrameRate;
            // restore-check: ok the probe's own OnDestroy puts both priors back, and Unity runs it however the probe ends
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = ProbeFps;
        }

        internal static KbFrameSummary Stop()
        {
            return Stop(0f, float.PositiveInfinity);
        }

        /// <summary>Stop, and read the p99 frame inside [windowLoS, windowHiS] probe seconds (KbFrameStats.Summarize).</summary>
        internal static KbFrameSummary Stop(float windowLoS, float windowHiS)
        {
            if (live == null)
            {
                return default;
            }
            RM_FrameProbe p = live;
            live = null;
            KbFrameSummary g = KbFrameStats.Summarize(p.ms.ToArray(), p.paused.ToArray(), p.inAir.ToArray(), p.lastFrame - p.firstFrame,
                p.firstReal < 0f ? 0f : p.lastReal - p.firstReal, windowLoS, windowHiS);
            try
            {
                string path = System.IO.Path.Combine(GenFilePaths.SaveDataFolderPath, "RM_FrameProbe_" + DateTime.Now.ToString("yyyyMMddTHHmmss") + ".csv");
                var sb = new System.Text.StringBuilder("row,ms,paused,in_air,flush_ms,takeoff_ms,takeoffs,land_ms,resume_ms,lands,gc\n");
                for (int i = 0; i < p.ms.Count; i++)
                {
                    sb.Append(i).Append(',').Append(p.ms[i].ToString("0.###", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
                        .Append(p.paused[i] ? 1 : 0).Append(',').Append(p.inAir[i]).Append(',').Append(i < p.parts.Count ? p.parts[i] : "").Append('\n');
                }
                System.IO.File.WriteAllText(path, sb.ToString());
                LastPath = path;
            }
            catch (Exception ex)
            {
                LastPath = "UNWRITTEN " + ex.GetType().Name;
            }
            DestroyImmediate(p.gameObject);     // at once: a Begin in this same frame must read the restored priors
            return g;
        }

        private void OnDestroy()
        {
            // restore-check: ok this IS the restore (the priors read in Begin)
            QualitySettings.vSyncCount = priorVSync;
            Application.targetFrameRate = priorTarget;
        }

        private void Update()
        {
            float now = Time.realtimeSinceStartup;
            if (firstReal < 0f)
            {
                firstReal = now;
                firstFrame = Time.frameCount;
            }
            else
            {
                ms.Add((now - lastReal) * 1000f);
                paused.Add(Find.TickManager == null || Find.TickManager.Paused);
                inAir.Add(InAir());
                var ci = System.Globalization.CultureInfo.InvariantCulture;
                int gc = GC.CollectionCount(0);
                parts.Add(FlushMs.ToString("0.###", ci) + "," + PawnTakeoffMs.ToString("0.###", ci) + "," + Takeoffs + ","
                    + LandMs.ToString("0.###", ci) + "," + ResumeMs.ToString("0.###", ci) + "," + Lands + "," + (lastGc < 0 ? 0 : gc - lastGc));
                lastGc = gc;
            }
            lastReal = now;
            lastFrame = Time.frameCount;
            FlushMs = PawnTakeoffMs = LandMs = ResumeMs = 0;
            Takeoffs = Lands = 0;
            if (SleepNextMs > 0)
            {
                int z = SleepNextMs;
                SleepNextMs = 0;
                System.Threading.Thread.Sleep(z);
            }
        }

        private static int InAir()
        {
            Map m = Find.CurrentMap;
            if (m == null)
            {
                return 0;
            }
            int n = 0;
            if (RM_KnockbackDefOf.RM_ThingFlyer_Knockback != null)
            {
                n += m.listerThings.ThingsOfDef(RM_KnockbackDefOf.RM_ThingFlyer_Knockback).Count;
            }
            if (RM_KnockbackDefOf.RM_PawnFlyer_Knockback != null)
            {
                n += m.listerThings.ThingsOfDef(RM_KnockbackDefOf.RM_PawnFlyer_Knockback).Count;
            }
            return n;
        }
    }
}
#endif
