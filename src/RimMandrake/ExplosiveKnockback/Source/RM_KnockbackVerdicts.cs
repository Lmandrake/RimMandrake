#if RM_PROOFS || RM_KB_SELFTEST
using System;

namespace RimMandrake.ExplosiveKnockback
{
    // The verdict and plan arithmetic of the proof scenes, lifted out of the Verse scenes (RM_KnockbackProof*.cs) so the
    // offline SelfTest runs it (RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED: blind cycle 5 planted nine
    // faults in these lines and every offline suite stayed green). The scenes read the game and pass plain values in;
    // nothing here reads the game. Verse-free on purpose, like RM_KnockbackMath.cs: the SelfTest compiles this file with
    // RM_KB_SELFTEST, the proof build with RM_PROOFS, and the release DLL not at all.
    public static class RM_KnockbackVerdicts
    {
        /// <summary>The cells the kernel throws a loose good of `mass` kg at `dist` from a blast of radius r (force 1, the
        /// scenes' reference shell): 0 over the light-goods mass limit, else WildCells with the goods' wild factor.
        /// The proof's WantCells, WantCellsFrom and PlanGood all plan through this.</summary>
        public static int GoodCells(float dist, float radius, float mass, KbSettings k, float wild)
        {
            if (mass > k.lightMassLimit)
            {
                return 0;
            }
            return RM_KnockbackMath.WildCells(dist, radius, 1f, mass, k, wild);
        }

        /// <summary>sc_calibration: the colonist is thrown exactly 3 cells (people_thrown_three_cells), straight away from
        /// the blast (same row, larger x), alive, with exactly one launch line. `away` comes back for the detail text.</summary>
        public static bool Calibration(int cells, bool spawned, int x, int z, int startX, int startZ, bool alive, int launches,
            out bool away)
        {
            away = spawned && x > startX && z == startZ;
            return cells == 3 && away && alive && launches == 1;
        }

        /// <summary>sc_goods_obstacles' start assertion for one lane: null when the kernel plan of lane `lane` ("D" door,
        /// "S" sandbags, "W" deep water) reaches its obstacle as the scene needs, else why not (the scene then does not
        /// run). `beyond` is the obstacle's column; `originX` only shapes the message. Control: every lane must fly its
        /// whole distance and land past the obstacle's column. Door: the plan stops at the door with at least one cell
        /// to rebound (`back`, ReboundCells of the cells left after the door cell). Sandbags: past the column. Water: a
        /// Water stop on the last cell before it.</summary>
        public static string ObstaclePlan(string lane, bool control, KbStop stop, int destX, int beyond, int originX, int want,
            float keepPercent, out int back)
        {
            back = 0;
            if (control)
            {
                if (stop != KbStop.Distance || destX <= beyond)
                {
                    return "control lane " + lane + " plan " + stop + " to x+" + (destX - originX) + ": does not land beyond where the obstacle stood (want=" + want + ")";
                }
                return null;
            }
            if (lane == "D")
            {
                back = RM_KnockbackMath.ReboundCells(want - 1, keepPercent);
                if (stop != KbStop.Door || back < 1)
                {
                    return "lane D plan " + stop + " want=" + want + " back=" + back + ": the throw does not reach the door with cells to rebound";
                }
                return null;
            }
            if (lane == "S")
            {
                if (destX <= beyond)
                {
                    return "lane S plan " + stop + " to x+" + (destX - originX) + ": the throw does not carry past the sandbags (want=" + want + ")";
                }
                return null;
            }
            if (stop != KbStop.Water || destX != beyond - 1)
            {
                return "lane " + lane + " plan " + stop + " to x+" + (destX - originX) + ": deep water is not a Water stop on the last cell before it (want=" + want + ")";
            }
            return null;
        }

        /// <summary>sc_hose_drop_control (knockback off): the blast alone does not drop the hose. Passes only with no launch
        /// line, the colonist still carrying the hose end on its takeoff cell, and hurt by the blast (so the blast landed).</summary>
        public static bool HoseControl(int launches, string carry, string carrier, string pCell, string takeoff, bool hurt)
        {
            bool still = carry == "Carrying" && carrier == "p" && pCell == takeoff;
            return launches == 0 && still && hurt;
        }

        /// <summary>sc_hose_drop: one launch line that says the hose dropped, the hose end lying on the takeoff cell with no
        /// carrier, and the launch landing 3 cells (Chebyshev) from takeoff. `launchCheb` is that distance, or -1 when the
        /// launch line has no landing cell. The three parts come back for the detail text.</summary>
        public static bool HoseDrop(int launches, bool hoseDroppedFlag, string carry, string carrier, string end, string takeoff,
            int launchCheb, out bool launched, out bool dropped, out bool three)
        {
            launched = launches == 1 && hoseDroppedFlag;
            dropped = carry == "Dropped" && carrier == "none" && end == takeoff;
            three = launches == 1 && launchCheb == 3;
            return launched && dropped && three;
        }

        /// <summary>sc_goods_fly_off (flying goods off): the good is skipped with reason flying_off, has no item_move line,
        /// is never seen in a carrier, and lies spawned on its own cell with its whole stack.</summary>
        public static bool FlyOff(bool skipped, bool noMove, bool neverAir, bool spawned, int cells, int count, int startCount)
        {
            return skipped && noMove && neverAir && spawned && cells == 0 && count == startCount;
        }

        /// <summary>sc_goods_obstacles, lane D: the first rebound line hit the door and carried ReboundCells(left, keep%)
        /// cells. `reboundLines` is the good's item_rebound line count; `hit`, `left` and `cells` read off the first.</summary>
        public static bool DoorBounced(int reboundLines, string hit, int left, int cells, float keepPercent)
        {
            return reboundLines >= 1 && hit == "Door" && cells == RM_KnockbackMath.ReboundCells(left, keepPercent);
        }

        /// <summary>sc_goods_obstacles' verdict for one lane, the stack at (x, z) after the blasts. `beyond` is the obstacle's
        /// column, `row` the lane's z. Control: at rest where the kernel planned it (planX, planZ), having flown. D: flew,
        /// bounced off the door, the door still closed, at rest on the blast side. S: at rest past the sandbags in its row.
        /// W: flew, dry, unfogged, never drawn on deep water, at rest on the last cell before it. Every lane: at rest, no
        /// despawn-spawn pair (hops), never hidden.</summary>
        public static bool ObstacleLane(string lane, bool control, bool rest, bool flew, int x, int z, int planX, int planZ, int beyond,
            int row, bool bounced, bool doorClosed, bool dry, bool visible, int inWater, int hops, int hidden)
        {
            bool ok;
            if (control)
            {
                ok = rest && flew && x == planX && z == planZ;
            }
            else if (lane == "D")
            {
                ok = flew && bounced && doorClosed && rest && x < beyond;
            }
            else if (lane == "S")
            {
                ok = rest && flew && x > beyond && z == row;
            }
            else
            {
                ok = flew && dry && visible && inWater == 0 && x == beyond - 1 && z == row;
            }
            return ok && rest && hops == 0 && hidden == 0;
        }

        /// <summary>sc_closed_containers, one thrown container: moved 1..maxCells cells (Chebyshev; -1 when gone), farther from
        /// the blast than it started, one container line reading "thrown", its contents held.</summary>
        public static bool ContainerThrown(int cells, int maxCells, bool away, bool thrown, bool held)
        {
            return cells >= 1 && cells <= maxCells && away && thrown && held;
        }

        /// <summary>PitProbe's start gate: null when the hauler is there and spawned, the steel is there and a map is current;
        /// else the INVALID line naming what is missing.</summary>
        public static string PitProbeMissing(string name, bool hThere, bool hSpawned, bool hDead, string hHolder, bool stThere,
            bool stSpawned, bool stDestroyed, string stHolder, bool mapThere)
        {
            if (hThere && stThere && hSpawned && mapThere)
            {
                return null;
            }
            return "INVALID " + name + " hauler or steel missing (h=" + hThere + " hSpawned=" + (hThere && hSpawned)
                + " hDead=" + (hThere && hDead) + " hHolder=" + hHolder + " st=" + stThere + " stSpawned="
                + (stThere && stSpawned) + " stDestroyed=" + (stThere && stDestroyed) + " stHolder=" + stHolder
                + ")";
        }
    }
}
#endif
