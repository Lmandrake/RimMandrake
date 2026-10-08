// Verse-free kernel of the gravship-landing reveal: the gate (Odyssey, arrival map, setting) and the root walk that decides which
// fogged outdoor cells get a flood-unfog. The engine's FloodUnfog itself stays behind IRevealWorld. GravshipLanding's postfix calls
// these with the same expressions; SelfTest/GravshipLandingFuzz.cs compiles this file alone against a model of the engine flood.
// Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;` here breaks the self-test build, which is the guard rail).
namespace RimMandrake.GravshipLanding
{
    /// <summary>The map as the reveal sees it. BlocksFog = the cell's edifice makes fog (a wall, rock).</summary>
    public interface IRevealWorld
    {
        bool InBounds(int x, int z);
        bool IsFogged(int x, int z);
        bool IsRoofed(int x, int z);
        bool BlocksFog(int x, int z);
        void FloodUnfog(int x, int z);
    }

    public static class RM_LandingKernel
    {
        /// <summary>The reveal runs only with Odyssey, on a gravship-arrival map, with the setting on.</summary>
        public static bool Enabled(bool odysseyActive, bool arrivalMap, bool settingOn) { return odysseyActive && arrivalMap && settingOn; }

        /// <summary>A cell that starts a flood: inside the map, still fogged, unroofed, and not itself a fog-making edifice.</summary>
        public static bool IsRoot(bool inBounds, bool fogged, bool roofed, bool blocksFog) { return inBounds && fogged && !roofed && !blocksFog; }

        /// <summary>Flood-unfog from every root in the rect; returns how many floods it started.</summary>
        public static int Reveal(IRevealWorld w, int minX, int minZ, int width, int height)
        {
            int roots = 0;
            for (int z = minZ; z < minZ + height; z++)
                for (int x = minX; x < minX + width; x++)
                {
                    bool inb = w.InBounds(x, z);
                    if (!inb) continue;
                    if (!IsRoot(inb, w.IsFogged(x, z), w.IsRoofed(x, z), w.BlocksFog(x, z))) continue;
                    w.FloodUnfog(x, z);
                    roots++;
                }
            return roots;
        }
    }
}
