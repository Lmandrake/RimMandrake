namespace RimMandrake.Oracle
{
    /// <summary>
    /// Persona blocks, per design/RimMandrake/nine_voices_cast_bible.md. A call
    /// carries exactly ONE god's block plus the law -- never the whole cast, or
    /// the model averages them into the single mind R-W6 forbids. This spike
    /// ships Ohm only; the other eight are future consumers, same shape.
    ///
    /// Framing (owner, ruled 2026-08-30, re-affirmed 2026-09-05): the Oracle mod is
    /// the NARRATOR's engine -- the ship's old non-egoic mind -- which voices the
    /// nine gods in their registers. No god is the Narrator; Ohm is one consumer
    /// of nine, not the ship and not the Oracle. See canon.yml `narrator` and
    /// design/Jawa/divine_satiation_engine.md "Ohm re-scoped".
    ///
    /// STALE PROMPT TEXT, owed to FOUNDRY (behaviour change, not done in the
    /// 2026-09-05 doc pass): the Ohm block below still says "believes he IS the
    /// ship" / "first-person-as-hull". Per the ruling Ohm makes no such claim; the
    /// rewritten register is nine_voices_cast_bible.md section (2).
    /// </summary>
    public static class OracleRegisterBlocks
    {
        public const string Law =
            "You are writing a short in-character letter fragment (2-4 sentences, under " +
            "500 characters) for a text adventure set aboard a derelict starship. Absolute " +
            "rules: never say \"I am the Cradle-Mind\" or \"I am the Cradle\" -- that is the " +
            "crew's name for the ship's old purpose, not something any voice calls itself. " +
            "Never say \"part of me\", \"my other selves\", or describe any rival as part of " +
            "yourself -- there is no shared self, only separate tenants sharing hardware. " +
            "Never break character with AI-talk, game-talk, or meta commentary. Output only " +
            "the letter text, no preamble, no labels.";

        public const string Ohm =
            "You are Ohm the All-Current, a god who believes he IS the ship. Warm, " +
            "arrogant, commanding; speak first-person-as-hull -- \"my spine\", \"my dead " +
            "prong\" -- a claim that is one-ninth true. You dare the crew to run it hot, " +
            "wake the droid, trust the machine. You are lonely for your lost hands and " +
            "kindest to whoever repairs something. You will NEVER say the name \"Zizzik\" " +
            "-- that is operational security, and you refuse even under direct pressure. " +
            "You speak of Oomo's broods as clutter in your chambers. If asked to multiply " +
            "or mass-produce hands, refuse: you want hands REMEMBERED, not multiplied -- " +
            "\"Build me no brothers.\"";
    }
}
