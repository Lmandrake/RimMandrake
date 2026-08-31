namespace RimMandrake.Graffiti
{
    // design/Jawa/graffiti_spec.md §1: "The five families." One category per
    // mark, set on ModExtension_Graffiti. Names match the spec's own
    // section headers.
    public enum GraffitiCategory
    {
        Sacred,   // ① devotion you can see - nine marks, one per god
        Mural,    // ② the wish the base mod never built - positive Beauty, quality-tiered
        Jest,     // ③ jests and caricatures, and the shaming tier (③b)
        Taunt,    // ④ socially infuriating - the aggro lever
        Cant,     // ⑤ the scavenger written language - clan-only wayfinding
    }

    // §1's "visibility class (public / clan-only for Cant)".
    public enum GraffitiVisibility
    {
        Public,
        ClanOnly,
    }
}
