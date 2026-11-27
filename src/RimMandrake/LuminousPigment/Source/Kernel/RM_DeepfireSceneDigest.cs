// RM_DeepfireSceneDigest.cs - the digest of LuminousPigment's per-game counters, for the test hooks (DeepfireTestHooks.cs).
// Item RIMMANDRAKE_GIVE_ONE_MOD_A_DIGEST_HOOK_SO_A_DIRTY_RESET_CAN_SHOW. Verse-free: the SelfTest fuzz family `testhooks` runs it.
// The counters are GameComponent_Deepfire's godCoatEvents (def key -> first-coat god events, the anti-pinning count) and
// impressedQuadrum (faction loadID -> the quadrum it was last impressed). Both carry over from one staged scene to the next on
// the same game, so a repeat that does not reset them starts its second copy diminished.
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace RimMandrake.LuminousPigment
{
    public static class RM_DeepfireSceneDigest
    {
        /// <summary>The render of no counters: the state right after the reset hook.</summary>
        public const string Clean = "godCoat[] impressed[]";

        /// <summary>Sorted and length-prefixed ("<len>:<key>=<count>"), so two equal states render equal whatever their order, and
        /// a key that holds a separator cannot make two different states render alike.</summary>
        public static string Render(IDictionary<string, int> godCoat, IDictionary<int, int> impressed)
        {
            CultureInfo inv = CultureInfo.InvariantCulture;
            var sb = new StringBuilder("godCoat[");
            if (godCoat != null)
            {
                var keys = new List<string>(godCoat.Keys);
                keys.Sort(string.CompareOrdinal);
                for (int i = 0; i < keys.Count; i++)
                {
                    if (i > 0) sb.Append(';');
                    sb.Append(keys[i].Length.ToString(inv)).Append(':').Append(keys[i]).Append('=').Append(godCoat[keys[i]].ToString(inv));
                }
            }
            sb.Append("] impressed[");
            if (impressed != null)
            {
                var ids = new List<int>(impressed.Keys);
                ids.Sort();
                for (int i = 0; i < ids.Count; i++)
                {
                    if (i > 0) sb.Append(';');
                    sb.Append(ids[i].ToString(inv)).Append('=').Append(impressed[ids[i]].ToString(inv));
                }
            }
            return sb.Append(']').ToString();
        }
    }
}
