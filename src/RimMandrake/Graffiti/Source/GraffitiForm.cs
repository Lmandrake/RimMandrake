namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 design §1.2: the FORM axis, beside the
    // existing FUNCTION axis (GraffitiCategory). A mark is BOTH a form (how
    // it is made, how it decays, how it reads) and a category (what social
    // work it does) - e.g. a Stencil+Taunt is a crisp, non-decaying threat;
    // a Sigil+Devotional is a god's mark. Real-world graffiti taxonomy:
    // tag -> throw-up -> piece; stencil; wheat-paste; the scavenger's own
    // ideoligion sigils and glyphs.
    public enum GraffitiForm
    {
        Scrawl,    // untrained daub - today's RM_Graffiti_Vandal
        Tag,       // one-colour signature, fast, low commitment
        ThrowUp,   // two-colour bubble letterforms, bigger, faster to read
        Stencil,   // repeatable, crisp, does not rainWash away
        Paste,     // wheat-paste poster - decays fast, peels in rain
        Sigil,     // tier-A/tier-C ideoligion emblem, rendered or authored
        Glyph,     // small practical/hazard/meme mark - the shipped three
        Piece,     // full mural-scale work - v2, quality-tiered (fork F1)
    }
}
