using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands.Fuzz
{
    // Family `wither`: grass under a roof (RM_RoofWitherKernel, CompWithersUnderRoof.cs). Random plants (id, cell, hit points,
    // already damaged or not), random witherTicks (below one long tick up to 100 days), random roof streams (always, never,
    // intermittent) and the gate flipped mid-life. Invariants of every step: a living plant keeps at least 1 HP (a non-lethal
    // step takes less than it has), damage is never negative, nothing happens unroofed or with the gate off, a death comes only
    // under a roof, the look is fresh/wilting/withered while alive and dead only on the lethal step, and the roof's total take
    // never passes the plant's max HP. A plant roofed from fresh dies on the first long tick at or past its own death time, and
    // that time lies in SpreadLo..SpreadHi of witherTicks. Dead grass (Crumble) keeps the same promises. T_ROOF_WITHER_OFFLINE
    // drives the same kernel over whole patches; this family hunts the edges.
    internal static class RoofWitherFuzz
    {
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        public static List<string> Run(int n, int seed)
        {
            var fails = new List<string>();
            long lethal = 0, unroofSteps = 0, gateOffSteps = 0, damagedStarts = 0, crumbled = 0;
            try
            {
                var r = new Random(seed);
                const int L = RM_RoofWitherKernel.LongTickTicks;
                for (int p = 0; p < n; p++)
                {
                    int id = r.Next(0, int.MaxValue), x = r.Next(0, 400), z = r.Next(0, 400);
                    int maxHp = r.Next(1, 201);
                    int[] ws = { r.Next(1, L), r.Next(L, 600000), r.Next(600000, 6000000), 60000 };
                    int w = ws[r.Next(ws.Length)];
                    int hp = r.Next(3) == 0 ? r.Next(1, maxHp + 1) : maxHp;
                    if (hp < maxHp) damagedStarts++;
                    int mode = r.Next(4);   // 0 always roofed, 1 never, 2 intermittent, 3 intermittent with the gate flipping
                    int d = RM_RoofWitherKernel.DeathTicks(id, x, z, w);
                    double u = RM_RoofWitherKernel.SpreadU(id, x, z);
                    PyrelandsFuzz.Cases++;
                    Check(u >= 0 && u < 1, $"SpreadU({id},{x},{z}) = {u}, outside [0,1)");
                    int wl = Math.Max(L, w);
                    Check(d >= L && d >= Math.Round(wl * RM_RoofWitherKernel.SpreadLo) - 1 && d <= Math.Round(wl * RM_RoofWitherKernel.SpreadHi) + 1,
                        $"DeathTicks({id},{x},{z},{w}) = {d}, outside {RM_RoofWitherKernel.SpreadLo}..{RM_RoofWitherKernel.SpreadHi} x {wl}");
                    int roofed = 0, dealt = 0, taken = 0, lastStage = RM_RoofWitherKernel.StageFresh;
                    int steps = d / L + 40;   // d is at most 1.4 x 6000000 ticks: 4240 long ticks
                    bool died = false;
                    for (int k = 0; k < steps && !died; k++)
                    {
                        bool roof = mode == 0 || (mode >= 2 && r.Next(3) != 0);
                        bool gate = mode != 3 || r.Next(5) != 0;
                        int r0 = roofed, d0 = dealt;
                        var s = RM_RoofWitherKernel.Advance(ref roofed, ref dealt, id, x, z, maxHp, hp, w, gate, roof);
                        PyrelandsFuzz.Steps++;
                        string at = $"plant {id}@({x},{z}) maxHp {maxHp} W {w} d {d} mode {mode} step {k} hp {hp} roofed {r0}->{roofed} dealt {d0}->{dealt}";
                        Check(s.Damage >= 0, at + ": negative damage " + s.Damage);
                        Check(roofed >= 0, at + ": roofed ticks below 0");
                        Check(dealt >= d0, at + ": the roof's take fell");
                        if (!gate)
                        {
                            gateOffSteps++;
                            Check(!s.Lethal && s.Damage == 0 && roofed == r0 && dealt == d0 && s.Stage == RM_RoofWitherKernel.StageFresh,
                                at + ": the gate is off and the step did something (damage " + s.Damage + ", stage " + s.Stage + ")");
                            continue;
                        }
                        if (!roof)
                        {
                            unroofSteps++;
                            Check(!s.Lethal && s.Damage == 0 && dealt == d0, at + ": unroofed and it took " + s.Damage);
                            Check(roofed == Math.Max(0, r0 - L), at + ": unroofed and the roof clock did not fall one long tick");
                        }
                        if (s.Lethal)
                        {
                            Check(roof, at + ": died unroofed");
                            Check(s.Stage == RM_RoofWitherKernel.StageDead && s.Damage == hp, at + ": a lethal step that is not dead or does not take all " + hp);
                            lethal++;
                            died = true;
                            if (mode == 0 && hp == maxHp)
                            {
                                Check(roofed >= d && roofed - L < d, at + ": roofed from fresh, it died at " + roofed + " for a death time of " + d);
                            }
                            break;
                        }
                        Check(s.Damage < hp, at + ": a non-lethal step took " + s.Damage + " of " + hp + " HP");
                        Check(s.Stage >= RM_RoofWitherKernel.StageFresh && s.Stage <= RM_RoofWitherKernel.StageWithered, at + ": a living plant reads stage " + s.Stage);
                        Check(roof || s.Stage <= lastStage, at + ": unroofed and the look worsened " + lastStage + " -> " + s.Stage);
                        hp -= s.Damage;
                        taken += s.Damage;
                        Check(taken <= maxHp - 1, at + ": the roof took " + taken + " of a living plant's " + maxHp);
                        lastStage = s.Stage;
                    }
                    if (mode == 0)
                    {
                        PyrelandsFuzz.Cases++;
                        Check(died, $"plant {id} maxHp {maxHp} W {w} d {d}: roofed for {steps} long ticks and still alive");
                    }

                    // Dead grass from the same plant.
                    int age = 0, cd = 0, chp = maxHp, cT = ws[r.Next(ws.Length)];
                    int cDeath = RM_RoofWitherKernel.DeathTicks(id, x, z, cT);
                    bool gone = false;
                    for (int k = 0; k < cDeath / L + 2; k++)
                    {
                        int a0 = age;
                        var s = RM_RoofWitherKernel.Crumble(ref age, ref cd, id, x, z, maxHp, chp, cT);
                        PyrelandsFuzz.Steps++;
                        string at = $"dead grass {id} maxHp {maxHp} crumble {cT} death {cDeath} step {k} hp {chp} age {a0}";
                        Check(s.Damage >= 0, at + ": negative crumble");
                        Check(RM_RoofWitherKernel.CrumbleTicksLeft(age, id, x, z, cT) == Math.Max(0, cDeath - age), at + ": ticks left disagree");
                        if (s.Lethal) { Check(age >= cDeath && age - L < cDeath, at + ": gone at age " + age); gone = true; crumbled++; break; }
                        Check(s.Damage < chp, at + ": a non-lethal crumble took " + s.Damage + " of " + chp);
                        chp -= s.Damage;
                    }
                    PyrelandsFuzz.Cases++;
                    Check(gone, $"dead grass {id} crumble {cT}: still there past its end {cDeath}");
                }
                PyrelandsFuzz.Cases++;
                Check(lethal > 0 && unroofSteps > 0 && gateOffSteps > 0 && damagedStarts > 0 && crumbled > 0,
                    $"the family is blind: {lethal} deaths, {unroofSteps} unroofed steps, {gateOffSteps} gate-off steps, {damagedStarts} damaged starts, {crumbled} crumbled");
                Console.WriteLine($"wither: {n} plants, {lethal} deaths, {unroofSteps} unroofed steps, {gateOffSteps} gate-off steps, {damagedStarts} damaged starts, {crumbled} dead grass crumbled");
            }
            catch (Exception e) { fails.Add("wither: " + e.Message); }
            return fails;
        }
    }
}
