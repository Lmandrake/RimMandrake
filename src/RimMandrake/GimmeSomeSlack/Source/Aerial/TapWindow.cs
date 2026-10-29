using System;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>GSS_POWER_THEFT_FIX_WRONG_VICTIM. The 250-tick event window of a power tap, Verse-free so the selftest drives
    /// the PRODUCTION rule. The window used to sum energy across victims and report it against whoever the clamp bit when
    /// the event fired (GPT review FB_hose_gss_2.5). Now the window belongs to ONE victim key (the faction): when the clamp
    /// starts draining a different key, what the old key lost is flushed to the old key first, so every faction is
    /// charged only for its own energy and draining ticks.</summary>
    public sealed class TapWindow<TKey, TVictim> where TKey : class where TVictim : class
    {
        private TKey key;
        private TVictim victim;
        public float Wd;
        public int DrainTicks;

        /// <summary>One tick of draining <paramref name="stolen"/> from <paramref name="newKey"/>. If the window holds another key's
        /// energy it is flushed to that key first. Nothing happens for stolen &lt;= 0.</summary>
        public void Drain(TKey newKey, TVictim newVictim, float stolen, Action<TVictim, float, int> flush)
        {
            if (!(stolen > 0f)) return;
            if (key != null && !ReferenceEquals(key, newKey)) Flush(flush);
            key = newKey;
            victim = newVictim;
            Wd += stolen;
            DrainTicks++;
        }

        /// <summary>Report the window to its own victim (the event tick, or a victim switch) and empty it.</summary>
        public void Flush(Action<TVictim, float, int> flush)
        {
            if (Wd > 0f && victim != null) flush(victim, Wd, DrainTicks);
            Wd = 0f;
            DrainTicks = 0;
        }
    }
}
