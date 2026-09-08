using System.Collections.Generic;
using System.Linq;
using System.Text;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    public class CompProperties_HeadIdentity : CompProperties
    {
        public CompProperties_HeadIdentity() => compClass = typeof(CompHeadIdentity);
    }

    /// <summary>
    /// DROIDWORKS_HEADS_BRAINS_SPIKES_1 (packet B3). Carried on every
    /// RSW_DW_Head_* item (thingClass Thing_DWHead, below). Empty
    /// (hasSnapshot false) on a head bought fresh from a trader/Trade Moot;
    /// populated the moment CompDWHeadDropper spawns one off a dying droid -
    /// "kill -> head drops with its name" is the packet's own verify line.
    /// Traits are copied whole-cloth, not filtered to a hardware-quirk
    /// allowlist: DROIDWORKS_WIPE_SEVERITY_1 (B10, unbuilt) is what actually
    /// GIVES a droid a permanent RSW_DW_HardwareQuirk trait, and whatever
    /// pool that lands in shows up here automatically once it exists - this
    /// comp just snapshots whatever the pawn was carrying.
    /// </summary>
    public class CompHeadIdentity : ThingComp
    {
        public string pawnName;
        public string kindLabel;
        public string factionOfOrigin;
        public List<string> traitLabels = new List<string>();
        public bool hasSnapshot;

        public void SnapshotFrom(Pawn pawn)
        {
            pawnName = pawn.Name?.ToStringShort ?? pawn.LabelShortCap;
            kindLabel = pawn.kindDef?.label ?? pawn.def.label;
            factionOfOrigin = pawn.Faction?.def.label;
            traitLabels = pawn.story?.traits?.allTraits.Select(t => t.LabelCap).ToList()
                ?? new List<string>();
            hasSnapshot = true;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref pawnName, "dwPawnName");
            Scribe_Values.Look(ref kindLabel, "dwKindLabel");
            Scribe_Values.Look(ref factionOfOrigin, "dwFactionOfOrigin");
            Scribe_Values.Look(ref hasSnapshot, "dwHasSnapshot", false);
            Scribe_Collections.Look(ref traitLabels, "dwTraitLabels", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.LoadingVars && traitLabels == null)
                traitLabels = new List<string>();
        }

        public override string CompInspectStringExtra()
        {
            if (!hasSnapshot) return null;
            var sb = new StringBuilder();
            sb.Append("Salvaged from: " + pawnName + " (" + kindLabel + ")");
            if (!factionOfOrigin.NullOrEmpty())
                sb.Append("\nFaction of origin: " + factionOfOrigin);
            if (traitLabels.Count > 0)
                sb.Append("\nHardware quirks: " + string.Join(", ", traitLabels));
            return sb.ToString();
        }
    }

    /// <summary>
    /// thingClass for every RSW_DW_Head_* def. A head with a snapshot shows
    /// the droid it came from in its label (the packet's verify line, "kill
    /// -> head drops with its name") - a fresh, never-installed head (bought,
    /// looted from stock) falls back to the plain def label.
    /// </summary>
    public class Thing_DWHead : ThingWithComps
    {
        public override string LabelNoCount
        {
            get
            {
                CompHeadIdentity identity = GetComp<CompHeadIdentity>();
                if (identity == null || !identity.hasSnapshot || identity.pawnName.NullOrEmpty())
                    return base.LabelNoCount;
                return base.LabelNoCount + " (" + identity.pawnName + ")";
            }
        }
    }
}
