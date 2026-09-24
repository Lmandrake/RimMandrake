namespace RimMandrake.Graffiti
{
    // design/Jawa/graffiti_spec.md §1: "The five families," now six with
    // None for marks the family axis doesn't apply to (tier-A/C ideoligion
    // sigils and meme glyphs - see GraffitiPool/ModExtension_Graffiti's
    // requiresAnyMeme). Renamed 2026-09-24 per
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1's fork F9 (recommendation stands,
    // "rename Sacred->Devotional, Cant->Code"): Sacred -> Devotional (the
    // wider word covers both the nine campaign god-marks AND the tier-A/B/C
    // ideoligion-affinity marks this item adds); Cant -> Code (the
    // scavenger written-language family was always "coded", never literally
    // secret from the game's own systems). No live XML set either old value
    // before this rename (ModExtension_Graffiti.category was declared but
    // never assigned in any shipped def) - a pure rename, no data migration.
    public enum GraffitiCategory
    {
        None,        // no family - tier-A icon sigils, tier-C meme glyphs
        Devotional,  // (was Sacred) devotion you can see - one mark per god
        Mural,       // the wish the base mod never built - v2, fork F1
        Jest,        // jests and caricatures, and the shaming tier
        Taunt,       // socially infuriating - the aggro lever
        Code,        // (was Cant) the scavenger written language - clan-only wayfinding
    }

    // §1's "visibility class (public / clan-only for Cant/Code)".
    public enum GraffitiVisibility
    {
        Public,
        ClanOnly,
    }
}
