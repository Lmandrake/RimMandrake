using System.Collections.Generic;
using Verse;

namespace RimMandrake.Property
{
    // A thin IExposable wrapper around List&lt;ClaimRecord&gt; so it can be a
    // Dictionary&lt;Thing, ClaimRecordList&gt; value under LookMode.Deep — Scribe's
    // dictionary deep-look needs an IExposable value type with a parameterless
    // constructor, not a bare List&lt;T&gt;.
    public class ClaimRecordList : IExposable
    {
        public List<ClaimRecord> Records = new List<ClaimRecord>();

        public void ExposeData()
        {
            Scribe_Collections.Look(ref Records, "records", LookMode.Deep);
            if (Records == null) Records = new List<ClaimRecord>();
        }
    }
}
