// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 -- a SIGNATURE is one presence's light (design atmospheric_base_god_patterns_2026-10-24.md
// §4): its territory shape, its three readings (resting / pleased / angry, each an RM_AtmosphericSchemeDef), and the
// canon PAIRINGS it shares a boundary with (owner ruling §9.15: authored pairings for canon pairs, the leader's shape
// elsewhere). The territory rule itself is pure kernel (Kernel/RM_TerritoryShapes.cs); this def only carries data.
// A claim is matched to a signature through its scheme: the signature whose readings hold that scheme. No signature =
// the wedge, which is how every claim ran before signatures existed.
using System.Collections.Generic;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public class RM_SignatureTerritory
    {
        public RM_ShapeKind shape = RM_ShapeKind.Wedge;
        public RM_Anchor anchor = RM_Anchor.Core;
        public float minShare;   // ranked second, this presence's rank share never drops under this (0 = the kernel's fifth)

        public RM_TerritoryShape Shape => new RM_TerritoryShape { kind = shape, anchor = anchor };
    }

    public class RM_SignatureReadings
    {
        public RM_AtmosphericSchemeDef resting, pleased, angry;
        public IEnumerable<RM_AtmosphericSchemeDef> All() { if (resting != null) yield return resting; if (pleased != null) yield return pleased; if (angry != null) yield return angry; }
    }

    /// <summary>One authored canon pairing, written on ONE of the two signatures: this signature tides from myAnchor,
    /// `with` from theirAnchor; hunts = this signature's front hunts the other's.</summary>
    public class RM_SignaturePairing
    {
        public RM_SignatureDef with;
        public RM_Anchor myAnchor = RM_Anchor.Core, theirAnchor = RM_Anchor.Core;
        public bool hunts;
        public string label;
    }

    public class RM_SignatureDef : Def
    {
        public RM_SignatureTerritory territory = new RM_SignatureTerritory();
        public RM_SignatureReadings readings = new RM_SignatureReadings();
        public List<RM_SignaturePairing> pairings = new List<RM_SignaturePairing>();
        public string tell;   // the one-line description of how this presence reads (design §2)

        [Unsaved] private static Dictionary<RM_AtmosphericSchemeDef, RM_SignatureDef> bySchemeCache;
        [Unsaved] private static List<RM_PairingRule> rulesCache;

        /// <summary>The signature whose readings hold this scheme, or null. Built once after defs load.</summary>
        public static RM_SignatureDef ForScheme(RM_AtmosphericSchemeDef s)
        {
            if (s == null) return null;
            if (bySchemeCache == null)
            {
                var m = new Dictionary<RM_AtmosphericSchemeDef, RM_SignatureDef>();
                foreach (RM_SignatureDef d in DefDatabase<RM_SignatureDef>.AllDefsListForReading)
                    foreach (RM_AtmosphericSchemeDef r in d.readings.All())
                        if (!m.ContainsKey(r)) m[r] = d;
                bySchemeCache = m;
            }
            return bySchemeCache.TryGetValue(s, out RM_SignatureDef sig) ? sig : null;
        }

        /// <summary>Every authored pairing as kernel rules, by defName.</summary>
        public static List<RM_PairingRule> Rules
        {
            get
            {
                if (rulesCache != null) return rulesCache;
                var l = new List<RM_PairingRule>();
                foreach (RM_SignatureDef d in DefDatabase<RM_SignatureDef>.AllDefsListForReading)
                    foreach (RM_SignaturePairing p in d.pairings)
                        if (p?.with != null)
                            l.Add(new RM_PairingRule { a = d.defName, b = p.with.defName, anchorA = p.myAnchor, anchorB = p.theirAnchor, aHunts = p.hunts, label = p.label });
                rulesCache = l;
                return l;
            }
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (readings == null || readings.resting == null) yield return "a signature needs <readings><resting> (the scheme it shows at rest)";
            if (territory == null) yield return "<territory> may not be empty";
            if (pairings != null)
                foreach (RM_SignaturePairing p in pairings)
                {
                    if (p == null || p.with == null) { yield return "a <pairings> entry names no <with> signature"; continue; }
                    if (p.with == this) yield return "a signature may not pair with itself";
                }
        }
    }
}
