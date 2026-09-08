using RimWorld;
using Verse;

namespace RimMandrake.Property
{
    // A runtime-only handle identifying a claimant: a specific Pawn (colonist,
    // cast NPC, or guest — same case, spec item 7 "fully symmetric"), or a
    // Faction's Commons pool. NOT itself IExposable — every persisted class
    // that needs one (ClaimRecord, WitnessEntry) stores the Kind/Pawn/Faction
    // fields directly and rebuilds a ClaimantRef through the properties
    // below, which sidesteps Scribe's lack of support for deep-saving a
    // struct that itself holds reference fields.
    public struct ClaimantRef
    {
        public readonly ClaimantKind Kind;
        public readonly Pawn Pawn;
        public readonly Faction Faction;

        private ClaimantRef(ClaimantKind kind, Pawn pawn, Faction faction)
        {
            Kind = kind;
            Pawn = pawn;
            Faction = faction;
        }

        public static readonly ClaimantRef Unclaimed = new ClaimantRef(ClaimantKind.None, null, null);

        public static ClaimantRef OfPawn(Pawn pawn) => new ClaimantRef(ClaimantKind.Pawn, pawn, null);

        public static ClaimantRef OfCommons(Faction faction) => new ClaimantRef(ClaimantKind.Commons, null, faction);

        public bool IsUnclaimed => Kind == ClaimantKind.None;

        // "Guest claims" (spec item 10) are not a distinct case — a guest is
        // simply a Pawn claimant whose Faction differs from the map's home
        // faction. Convenience only; nothing structural depends on this.
        public bool IsGuestOn(Map map)
        {
            if (Kind != ClaimantKind.Pawn || Pawn == null || map == null) return false;
            Faction home = map.ParentFaction ?? Faction.OfPlayer;
            return Pawn.Faction != home;
        }

        public bool Equals(ClaimantRef other)
        {
            if (Kind != other.Kind) return false;
            switch (Kind)
            {
                case ClaimantKind.Pawn:
                    return Pawn == other.Pawn;
                case ClaimantKind.Commons:
                    return Faction == other.Faction;
                default:
                    return true; // both None
            }
        }

        public override bool Equals(object obj) => obj is ClaimantRef other && Equals(other);

        public override int GetHashCode()
        {
            switch (Kind)
            {
                case ClaimantKind.Pawn:
                    return Pawn?.GetHashCode() ?? 0;
                case ClaimantKind.Commons:
                    return Faction?.GetHashCode() ?? 0;
                default:
                    return 0;
            }
        }

        public override string ToString()
        {
            switch (Kind)
            {
                case ClaimantKind.Pawn:
                    return Pawn?.LabelShort ?? "Pawn(null)";
                case ClaimantKind.Commons:
                    return (Faction?.Name ?? "Faction(null)") + " Commons";
                default:
                    return "Unclaimed";
            }
        }
    }
}
