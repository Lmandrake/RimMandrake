// HOSE_FRAME_SHRINK_PER_FRAME_GARBAGE (review 2026-10-26): RM_MapComponent_Hoses.DrawAll built two key strings per hose per
// frame -- the lay key in EnsureLay (two IntVec3s, the shape fingerprint's six floats, the trail key, the port) and the draw
// key (pose tag + layKey + rank + port + mate) -- only to compare them with the strings already cached. On a 100-hose map
// that is ~1-2 KB of garbage per hose per frame. These memos keep the last inputs and the string built from them: the same
// inputs return the same string INSTANCE (no allocation); any changed input rebuilds it exactly as before. Doubles and
// floats compare bit for bit, so every input that could print differently rebuilds. The FrameLegacy path does not use them.
// Verse-free: compiled into the SelfTest project (HoseFrameMemoChecks).
using System;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>The draw key of one hose (DrawAll): "P"/"F" settled or "T"+tick, layKey, "@"+rank, "|p"+port, "|m"+mate key.</summary>
    internal sealed class HoseDrawKeyMemo
    {
        private bool has, settled, plump, onPort;
        private int tick, rank;
        private long px, pz;
        private string layKey, mate, key;

        /// <summary>The key exactly as <see cref="Build"/> makes it; the cached instance when no input changed.</summary>
        public string Get(bool settled, bool plump, int tick, string layKey, int rank, bool onPort, double portX, double portZ, string mate)
        {
            long bx = onPort ? BitConverter.DoubleToInt64Bits(portX) : 0, bz = onPort ? BitConverter.DoubleToInt64Bits(portZ) : 0;
            if (has && settled == this.settled && (settled ? plump == this.plump : tick == this.tick) && rank == this.rank
                && onPort == this.onPort && bx == px && bz == pz && string.Equals(layKey, this.layKey) && string.Equals(mate, this.mate))
                return key;
            has = true;
            this.settled = settled; this.plump = plump; this.tick = tick; this.rank = rank; this.onPort = onPort; px = bx; pz = bz;
            this.layKey = layKey; this.mate = mate;
            return key = Build(settled, plump, tick, layKey, rank, onPort, portX, portZ, mate);
        }

        /// <summary>The pre-memo expression (RM_MapComponent_Hoses.DrawAll before 2026-10-26), kept verbatim.</summary>
        public static string Build(bool settled, bool plump, int tick, string layKey, int rank, bool onPort, double portX, double portZ, string mate)
        {
            string key = (settled ? (plump ? "P" : "F") : "T" + tick) + layKey + "@" + rank;
            if (onPort) key += "|p" + portX.ToString("0.000") + "," + portZ.ToString("0.000");
            if (mate != null) key += "|m" + mate;
            return key;
        }
    }

    /// <summary>The inputs of one hose's lay key (EnsureLay). The caller builds the string on a miss and stores it with
    /// <see cref="Store"/>; <see cref="Same"/> says whether the stored string still describes these inputs.</summary>
    internal sealed class HoseLayKeyMemo
    {
        private bool has, relayOn, relayLaid, fed, hasPort;
        private int posX, posY, posZ, endX, endY, endZ, relayId, trailCount;
        private ulong trailHash;
        private string look, relayLook, shape;
        private long px, pz, ax, az;
        public string Key { get; private set; }

        public bool Same(int posX, int posY, int posZ, string look, int endX, int endY, int endZ, bool relayOn, int relayId, string relayLook, bool relayLaid,
                         int trailCount, ulong trailHash, string shape, bool fed, bool hasPort, double px, double pz, double ax, double az)
        {
            if (!has) return false;
            if (posX != this.posX || posY != this.posY || posZ != this.posZ || endX != this.endX || endY != this.endY || endZ != this.endZ || relayOn != this.relayOn || fed != this.fed
                || hasPort != this.hasPort || trailCount != this.trailCount || trailHash != this.trailHash) return false;
            if (relayOn && (relayId != this.relayId || relayLaid != this.relayLaid || !string.Equals(relayLook, this.relayLook))) return false;
            if (hasPort && (Bits(px) != this.px || Bits(pz) != this.pz || Bits(ax) != this.ax || Bits(az) != this.az)) return false;
            return string.Equals(look, this.look) && string.Equals(shape, this.shape);
        }

        public void Store(int posX, int posY, int posZ, string look, int endX, int endY, int endZ, bool relayOn, int relayId, string relayLook, bool relayLaid,
                          int trailCount, ulong trailHash, string shape, bool fed, bool hasPort, double px, double pz, double ax, double az, string key)
        {
            has = true;
            this.posX = posX; this.posY = posY; this.posZ = posZ; this.look = look; this.endX = endX; this.endY = endY; this.endZ = endZ;
            this.relayOn = relayOn; this.relayId = relayId; this.relayLook = relayLook; this.relayLaid = relayLaid;
            this.trailCount = trailCount; this.trailHash = trailHash; this.shape = shape; this.fed = fed; this.hasPort = hasPort;
            this.px = Bits(px); this.pz = Bits(pz); this.ax = Bits(ax); this.az = Bits(az);
            Key = key;
        }

        private static long Bits(double v) => BitConverter.DoubleToInt64Bits(v);
    }
}
