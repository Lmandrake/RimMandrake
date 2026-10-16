// SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR (owner 2026-10-16): a sluice or grate on a dug canal cell turns so its leaf spans
// between the banks, the way a door spans between walls. Offline checks on the production verdict
// (RM_FlowDoorFacingMath) over small grids, plus the production call site. Each case has a can-fail.
// NOT proven here: the door drawing turned on screen, or its blueprint turning as the canal is dug past it. Live check owed.
using System;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class FlowDoorFacingChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        // Grid legend: '#' bank (walkable undug ground), '.' dug channel, 'S' superdeep channel (dug AND impassable: vanilla
        // reads it as a wall), 'W' a real wall, 'G' another flow door on a dug cell, '~' natural water, '@' the door under test
        // (on a dug cell unless the grid says 'd': a door on dry ground). Rows run north (top) to south.
        private static readonly int[] DX = { 1, -1, 0, 0 };   // E, W, N, S
        private static readonly int[] DZ = { 0, 0, 1, -1 };

        /// <summary>"N" = Rot4.North (leaf spans East-West), "E" = Rot4.East (leaf spans North-South).</summary>
        private static string Facing(params string[] rows)
        {
            int h = rows.Length;
            int ax = -1, az = -1;
            for (int r = 0; r < h; r++)
            {
                int i = rows[r].IndexOfAny(new[] { '@', 'd' });
                if (i >= 0) { ax = i; az = h - 1 - r; }
            }
            Assert(ax >= 0, "can-fail: grid has no door");
            bool onChannel = At(rows, ax, az) == '@';
            int[] q = new int[4];
            for (int k = 0; k < 4; k++)
            {
                int x = ax + DX[k], z = az + DZ[k];
                char c = At(rows, x, z);
                bool inBounds = c != '\0';
                bool channel = c == '.' || c == 'S' || c == 'G' || c == '~';
                bool door = c == 'G';
                char opposite = At(rows, ax - DX[k], az - DZ[k]);
                int vanilla = c == 'W' || c == 'S' ? 9 : door ? (opposite == 'G' ? 5 : 1) : 0;
                q[k] = RM_FlowDoorFacingMath.SideQuality(onChannel, inBounds, channel, door, vanilla);
            }
            return RM_FlowDoorFacingMath.FacesNorth(q[0], q[1], q[2], q[3]) ? "N" : "E";
        }

        private static char At(string[] rows, int x, int z)
        {
            int r = rows.Length - 1 - z;
            if (r < 0 || r >= rows.Length || x < 0 || x >= rows[r].Length) return '\0';
            return rows[r][x];
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("FlowDoorFacing_spans_between_the_banks", () =>
            {
                // a north-south canal: banks east and west, the leaf spans East-West (North)
                Assert(Facing("#.#", "#@#", "#.#") == "N", "N-S canal: leaf spans E-W");
                // an east-west canal: leaf spans North-South (East). can-fail: vanilla alone says North here (all zeros)
                Assert(Facing("###", ".@.", "###") == "E", "E-W canal: leaf spans N-S");
                Assert(RM_FlowDoorFacingMath.FacesNorth(0, 0, 0, 0), "can-fail: vanilla's tie-break on open ground is North");
            });
            Case("FlowDoorFacing_superdeep_channel_is_not_a_wall", () =>
            {
                // vanilla scores an impassable superdeep cell 9 and would lay the gate ALONG the channel
                Assert(Facing("###", "S@S", "###") == "E", "superdeep E-W canal: leaf still spans N-S");
                Assert(Facing("#S#", "#@#", "#S#") == "N", "superdeep N-S canal: leaf spans E-W");
                Assert(!RM_FlowDoorFacingMath.FacesNorth(0, 0, 3, 3) && RM_FlowDoorFacingMath.FacesNorth(18, 0, 3, 3),
                    "can-fail: two 9s along the channel would outvote the banks");
            });
            Case("FlowDoorFacing_ends_bends_and_mouths", () =>
            {
                Assert(Facing("###", "#@#", "#.#") == "N", "dead end of a N-S canal: spans E-W across its mouth");
                Assert(Facing("###", "#@.", "###") == "E", "dead end of an E-W canal");
                Assert(Facing("~~~", "#@#", "#.#") == "N", "a canal opening north into a lake: the lake continues the channel");
                Assert(Facing("#.#", ".@.", "#.#") == "N", "a crossroads: vanilla's tie-break");
            });
            Case("FlowDoorFacing_gates_side_by_side_form_one_barrier", () =>
            {
                // a three-wide E-W canal barred by a N-S column of gates: every gate spans N-S
                Assert(Facing("#####", "..G..", "..@..", "..G..", "#####") == "E", "middle gate of three");
                Assert(Facing("#####", "..@..", "..G..", "..G..", "#####") == "E", "edge gate of three");
                Assert(Facing("##.##", "##.##", "#G@G#", "##.##") == "N", "a N-S canal three wide, barred E-W");
            });
            Case("FlowDoorFacing_walls_still_win_and_dry_ground_is_vanilla", () =>
            {
                Assert(Facing("#W#", ".@.", "#W#") == "E", "walls north and south: still spans N-S");
                Assert(Facing("#.#", "W@W", "#.#") == "N", "walls east and west on a N-S canal");
                // a flow door on DRY ground is vanilla's verdict exactly: open ground ties to North even on an E-W line of cut
                Assert(Facing("###", ".d.", "###") == "N", "can-fail: a door off the channel is not re-scored");
                Assert(RM_FlowDoorFacingMath.SideQuality(false, true, false, false, 0) == 0, "vanilla score untouched off-channel");
                Assert(RM_FlowDoorFacingMath.SideQuality(true, true, false, false, 9) == 9, "a real wall keeps its 9");
                Assert(RM_FlowDoorFacingMath.SideQuality(true, false, false, false, 0) == 0, "off the map is nothing");
            });
            Case("FlowDoorFacing_call_site_is_vanilla_door_rotation", () =>
            {
                string src = RiverSwitchFlipChecks.Src("Superdeep/RM_FlowDoors.cs");
                RiverSwitchFlipChecks.Has(src, @"\[HarmonyPatch\(typeof\(DoorUtility\), nameof\(DoorUtility\.DoorRotationAt\)\)\]",
                    "the postfix rides DoorUtility.DoorRotationAt (redone every frame a door or its blueprint draws)");
                RiverSwitchFlipChecks.Has(src, @"__result = RM_FlowDoorFacingMath\.FacesNorth\(e, w, n, s\) \? Rot4\.North : Rot4\.East;",
                    "the verdict decides the rotation");
                RiverSwitchFlipChecks.Has(src, @"eng\.IsExcavated\(c\) \|\| eng\.IsSourceCell\(c\)", "a channel side is dug or natural liquid");
                RiverSwitchFlipChecks.Has(src, @"return edifice is Building_RM_FlowDoor;", "only flow doors are re-scored");
            });
        }
    }
}
