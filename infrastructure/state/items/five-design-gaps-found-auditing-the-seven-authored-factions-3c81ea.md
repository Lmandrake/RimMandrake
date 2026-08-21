## spec
(a) VOID - owner, 2026-08-19: "Does this maxcountatgamestart thing even matter?
    We're going to manually write these settlements ourselves via the live
    bridge." => settlement counts are not a worldgen output we care about, so an
    uncapped faction costs nothing. Do not rule on it, do not add the field.
(b) 🔴 **The Geonosian Foundry Hive's TWO OUTPOSTS ruling is not expressed in
    the def**, and no `FactionDef` field expresses it. The 2026-08-17 ruling
    gives the hive two distinct outposts (ore seam · plateau);
    `settlementGenerationWeight 0.7` produces one undifferentiated cluster of
    about five. The ruling's Free-Droid-Enclaves alliance reversal is also
    unexpressed, and R1 forbids a goodwill number, so it needs a hard-coded
    relation somewhere. ⇒ either the ruling needs a mechanism or it needs
    downgrading to fiction.
    ⭐ LARGELY ANSWERED BY THE SAME OWNER LINE AS (a): the settlements are
    hand-written over the live bridge, so "two outposts, one on an ore seam and
    one on a plateau" is something the operator PLACES, not something a
    `FactionDef` has to express. What is left for DECIDE is only the alliance
    reversal, which is a relation and not a settlement.
(c) **`Jawa_HuttCartel`'s `ideoDescription` is NOT the text in
    `faction_religions_spec.md` entry 2**, though the file's comment claims it
    is verbatim. Spec: "Everything on this world evaporates, freezes, or is
    stolen…"  File: "Everything is owed. The water you drank this morning…".
    The spec's Decision precept `Execution_Required` is also absent — only the
    blacklist is present. ⇒ which text is canon?
(d) **`Jawa_FreeDroidEnclaves` fields a biological species.** §5 calls it 0%
    biological and the file's own comment says the `xenotypeSet` is "EMPTY ON
    PURPOSE", but it carries `RimMandrakeUgnaught 1.000`. ⇒ intended
    (droid-keepers) or a paste error?
(e) **Baseliners generate in five factions and the files used to deny it.**
    Measured chances: Helix 0.083 · Junkers 0.047 · Wildsteam 0.028 ·
    Deepwater 0.022 · Hutt 0.014. The comment claiming "they sum to 1.00 so no
    baseliner generates" was false and has been corrected in all five; the
    NUMBERS were left alone. ⇒ plain humans on a Star Wars planet: intended?

## verify
n/a — this is a request for five values, not a build.

## criteria
n/a

## notes
**from:** BUILD, 2026-08-19, while closing B45–B51. All five are DESIGN calls with no
value anywhere in the repo, so BUILD did not invent one. None of them blocks
the files, which are otherwise built and validate clean.

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

✅ CLOSED 2026-08-19 — all five answered. Good audit; two were real defects.
**(a) VOID** — already, by the owner's own line. Nothing added.
**(b) THE ALLIANCE IS AN IMPORTER ACTION, not a def field.** BUILD is right that
no `FactionDef` field expresses an NPC-to-NPC relation — there is no "permanent
ally" to declare. ⇒ the same answer as the settlements: the bridge sets it.
`Faction.SetRelationDirect(other, FactionRelationKind.Ally)`, public at
`Faction.cs:653`, before any map exists. Written into
`ASHKARR_WORLD_DEFINITION.md` §12.5b so the importer carries it. ⛔ NOT downgraded
to fiction — the plateau's whole point is that the cruellest ground holds the only
functioning peace, and an unrolled relation would lose it.
**(c) THE SPEC TEXT IS CANON, with the file's closing line grafted in.** The
tiebreak is not seniority: the spec's text says **"crossing between the faces"**,
which can only be true on a tidally locked planet, while the file's could belong to
any RimWorld loan shark. But the file's *"Pay, and you are family. Do not pay, and
you are inventory. There is no third column."* is better than what it replaced and
is kept. ⭐ It also lands exactly on today's slavery ruling — the Hutts are the
permanent slavers; "you are inventory" is that, in their own voice.
`Execution_Required` is owed too. Filed as BUILD
`hutt-ideo-text-is-canon-and-the-droid-faction-fields-a-pig-3d7c14`.
**(d) 0%% BIOLOGICAL — §5 STANDS, the Ugnaught is not intended.** The Enclaves are
droids who woke up and decided they belong to themselves; organic servants invert
the one idea the faction exists to carry, and the Rust Cathedral ruling leans on
that purity. 🔴 **But BUILD must NOT simply delete the line** — it may be a
placeholder holding the `Inherit="False"` strip together, and removing it could
silently re-admit five vanilla xenotypes. The item says which to confirm first.
**(e) BASELINERS ARE INTENDED. Keep the numbers, change nothing.** A baseliner is
a human, and **Star Wars is overwhelmingly human** — a galaxy where humans are the
most common species. Rates of 1.4%%-8.3%% across five factions read as correct
rather than as leakage. ⭐ BUILD did the right thing correcting the false comment
and leaving the numbers alone; that is exactly the right instinct.
