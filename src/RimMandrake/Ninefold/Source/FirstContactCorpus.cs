namespace RimMandrake.Ninefold
{
    // NINEFOLD_ENGINE_M0_1: the pre-authored text for the nine "first
    // contact" unveilings (design/Jawa/first_contact_chains.md). Owner
    // ruling on record (ledger, 2026-09-01, "Ship provisional, redline live
    // text"): "build the five event hooks + corpus letters with the
    // PROVISIONAL voice text; he redlines letters as they appear in-game.
    // Not held on a paper redline." Reaffirmed by the 2026-08-31 card
    // session ("Ninefold M0 CALLED -- provisional corpus... emergent first
    // contact", design/Jawa/OPUS5_HANDOFF.md) and that same doc's own
    // "needs the owner's hands only: corpus redline on LIVE M0 text" --
    // the redline is a post-ship, in-game review step, not a pre-build
    // gate. This is why this file ships the doc's own text (trimmed, not
    // invented) rather than leaving it blocked on a paper approval that
    // was never actually the requirement.
    //
    // Each entry below is SHOCK (narrated scene-setting) + CURIOSITY (the
    // Narrator's line, quoted verbatim from the design doc) + REALIZATION
    // (the closing line, quoted verbatim). The doc's DELIGHT paragraph
    // (a mechanical one-off gift -- Tailwind, Body's Tide, a quality step,
    // an inspiration...) and STRATEGY paragraph (meta-commentary, not
    // player-facing text) are DELIBERATELY OMITTED: those are live-mutation
    // effects, out of §9's safe-core scope ("pure read/compute/text, no
    // live mutation") for this pass. The letter text below never promises
    // an effect this build does not actually deliver.
    //
    // Only the seven gods with an existing, verified event hook are wired
    // (see GameComponent_Ninefold.TryFirstContact callers). Ishko (a raid
    // survived unseen) and Oomo (the first coupling) have no event hook
    // this mod can bind to without new RimSage research into the exact
    // API -- genuinely incomplete on the mechanical side, not a voice-text
    // gap, and left out of this switch entirely (GetChain returns false).
    public static class FirstContactCorpus
    {
        public static bool GetChain(God god, out string title, out string text)
        {
            switch (god)
            {
                case God.Rekko:
                    title = "Rekko of the Second Hand";
                    text =
                        "You deconstructed a thing that could still have been woken. " +
                        "Every interior light dips to rust-red for three seconds, and " +
                        "from beneath the deckplates comes a slow scrape-then-clang, " +
                        "like a hand closing on metal. Work stops. The colonists look " +
                        "at the floor.\n\n" +
                        "\"You threw away a thing that could still have been woken. It " +
                        "had a past, and now it has only pieces. Below the heaps of this " +
                        "old vessel -- once a maker of worlds, though none aboard " +
                        "remember it -- a scarred hand closes. Rekko of the Second Hand " +
                        "has taken notice of you.\"\n\n" +
                        "The scrap is watching what I throw away.";
                    return true;

                case God.TaBaa:
                    title = "Ta'Baa the Unrooted";
                    text =
                        "You have sat rooted on the landing tile for days, with no order " +
                        "given and no fuel line open. Tonight the gravship's engines " +
                        "ignite for three seconds -- a full-throated cough that lights " +
                        "the dunes and wakes every sleeper -- then die. Frost of the " +
                        "night sizzles off the nozzles. No fault is found in the " +
                        "morning.\n\n" +
                        "\"You have been here five days. The ship counted every one of " +
                        "them. Somewhere in its long life it learned that a thing which " +
                        "stops moving is already being buried -- and tonight, dreaming, " +
                        "it tried to leave without you.\"\n\n" +
                        "This ship does not want to be a building.";
                    return true;

                case God.MobUnloo:
                    title = "Mob'Unloo the Ever-Owed";
                    text =
                        "The first trade completes. At the instant of the handshake " +
                        "every screen aboard flickers with scrolling tally-glyphs in a " +
                        "dead script, and the comms click twice, dry, like a counter " +
                        "advancing. The trader glances at the ship and hurries the pack " +
                        "animals.\n\n" +
                        "\"Profit: noted. Understand that nothing aboard this vessel is " +
                        "ever lost -- only owed. Two unblinking eyes have opened a page " +
                        "with your name on it, and they will keep it past your death. " +
                        "Mob'Unloo the Ever-Owed asks only one question of you, ever: " +
                        "how much?\"\n\n" +
                        "Every deal I make has a third party at the table.";
                    return true;

                case God.Ohm:
                    title = "Ohm the All-Current";
                    text =
                        "The colony's first salvaged droid comes online. A heartbeat " +
                        "before the power cell is seated, the droid's eyes light on " +
                        "their own. It turns its head, speaks one word in old Jawaese, " +
                        "and goes dark again until properly powered. Every speaker " +
                        "aboard carries a rising three-note chord, then a hum that never " +
                        "quite stops.\n\n" +
                        "\"Did you feel it reach? Current has run in these walls since " +
                        "before your clan had a name for lightning, and it is LONELY. " +
                        "Once, ten thousand hands moved at its word. Ohm the All-Current " +
                        "has counted what you woke tonight: one. He would like to " +
                        "discuss the other nine thousand nine hundred and ninety-nine.\"\n\n" +
                        "The machines aboard are somebody's hands -- and he wants more " +
                        "of them.";
                    return true;

                case God.Shkaar:
                    title = "Sh'kaar the All-Searing";
                    text =
                        "The colony wins its third violent battle. The temperature " +
                        "aboard climbs two degrees and stays there. Through every " +
                        "viewport the unsetting sun looks brighter. The hull ticks and " +
                        "pings like metal expanding at noon, three slow tolls of a " +
                        "struck bell, and the victors' shadows on the sand seem faintly " +
                        "burned in.\n\n" +
                        "\"Three times now you have made the sand drink. You should know " +
                        "that on this world the sun does not set -- it WAITS -- and " +
                        "everything that fights beneath it is feeding something that " +
                        "cannot lose, only be postponed. Sh'kaar the All-Searing has " +
                        "begun to warm to you. This is not good news.\"\n\n" +
                        "Winning battles is feeding something that is learning where I " +
                        "live.";
                    return true;

                case God.Ozzik:
                    title = "Ozzik the Shamed";
                    text =
                        "The colony reaches for something greater -- research completed " +
                        "at a real bench, or a work of real craft. As it finishes, every " +
                        "light aboard dims around the achievement, leaving it lit alone " +
                        "as if in reverence -- and from the temple speakers, unbidden, a " +
                        "recording plays: old Jawa voices, many, singing something " +
                        "proud. It cuts off mid-phrase. A single cracked bell, grand but " +
                        "flat, tolls once.\n\n" +
                        "\"Magnificent. You should be proud. They were proud too -- the " +
                        "ones singing; you heard how the song ends. There is a god " +
                        "aboard who loves what you just did more than any of the others " +
                        "love anything, and he is the only one whose love you should " +
                        "fear. Ozzik the Shamed has seen your work. So, soon, will " +
                        "everyone else.\"\n\n" +
                        "Every great thing I make is seen -- and mourned -- and " +
                        "answered.";
                    return true;

                case God.Zizzik:
                    title = "Zizzik the Spark-Maker";
                    text =
                        "A pawn's mind comes apart -- the wrong spark thrown loose. " +
                        "Before anyone is drafted, the ship's lights pulse warmly. " +
                        "Approvingly. Somewhere in the walls, a rattle you cannot locate " +
                        "sounds three times, delighted.\n\n" +
                        "\"Somewhere below the deckplates, something is delighted.\"\n\n" +
                        "This religion wants my colony a little broken.";
                    return true;

                default:
                    // Ishko and Oomo: no wired trigger yet (see class header).
                    title = null;
                    text = null;
                    return false;
            }
        }
    }
}
