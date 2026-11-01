# Art style memory: what the owner likes, learned from his overrides

Kept by The Artist (`src/RimMandrake/rimflow/roles/artist.md`), updated at the end of every Artist run. It records what his
overrides show, so that a style question gets an answer that cites him. It is not a constraint file: the Opus judge does not
read it, and it decides no verdict. A line here reaches the pipeline only through `ledger.py fix` and `runner.py regress`.

Every line cites a criteria-ledger id (`infrastructure/state/art_eval/criteria_ledger.jsonl`) or a ruling. Lines beginning
`> CL-nnn:` are his words, copied verbatim; `selftest_artist_role.py` checks each one against the ledger.

**Studied through:** CL-045. Seeded 2026-11-01 from the ledger, 45 entries. No Artist run has happened yet: this seed is the
builder's reading. The first run re-reads it against the ledger and may strike any of it.

## How to answer a style question

Say which of the three you are giving. **Ruled**: `art_judge_brief.md`, a card, or his words on the subject. **Pattern**: under
`Patterns` below, two cases or more. **Unknown**: anything else; it goes under `Open questions` and to the Conductor.

## Patterns (two cases or more)

**He keeps live art the pipeline wants gone.** Of 33 creature overrides, 19 show him keeping the live picture (a text match on
`missed`, 2026-11-01). DEPARTURE_MISSING, F_SIZE_JUMP and F_INCONSISTENT are the codes most often named in those misses (23, 20
and 16 entries of the 33, same match; each entry can name several). So a live picture banded REALLY_BAD on those codes alone is
the pipeline's weakest call. Cases: CL-027, CL-028, CL-029, CL-031, CL-032, CL-033, CL-036, CL-037, CL-038.

**A regen is not better for being newer or bigger.**

> CL-019: "What's with the HUGE resolution on the 10-24 version? The original one was fine. This is NOT a star wars creature BTW."

Cases: CL-019, CL-031, CL-033 (live kept, every render purged).

**WEAK does not mean worthless.** He pools or picks renders the pipeline sent back: CL-034, CL-035, CL-040, CL-041. CL-032: two
renders banded WEAK were 'absurdly cool' and he asked for a new creature from them. They were wrong for the subject and good art.

**What a creature is, is in the description; a wrong description produces faithful wrong art.** The judge passes what the spec
asks for. CL-029 (he said 'These are weapon systems, not sad zombies.', and the fault was the spec's pitiable description),
CL-028 (a sessile creature judged as a walker because the spec never said so). When art is wrong in tone, read the card first.

**Resolution counts in both directions.** Too large a canvas with no reason (CL-019); 'too low res' on 512 canvases at adult
drawSize 7.0 (CL-038).

**Wall-leaning objects are a perspective problem, judged in place.** Each facing composed against its wall, never alone.

> CL-004: "(screenshot) so close on ladders! They are correctly positioned (translation) against the walls, but their perspective rotation is reversed for East and West. Just slide them across to the other wall and I think they might look ok"
> CL-009: "Portable ladders East and West are OBVIOUSLY broken. The ladders are running north/south rather then up/down!!!"
> CL-010: "The east and west ladders now read as totally flat rather than a 3d ladder. You clearly used a compressive transform that made them look flat."
> CL-011: "The south-facing one should only be small nubs sticking up, and that's correct for Rimworld. Too much is being shown as just a truncation of the north-facing ladder, and that's wrong."

## Watching (one case; not a rule yet)

- Assembled joins are judged assembled, not piece by piece.

> CL-042: "joins look horrible, I know you can do better here! The collar by the tank is superimposed and odd. the corner has no treatment at all in the north. In the south there is a crude "cap" graphic that's inappropriate."

- Faces: he agreed two renders were bad, but for 'poor quality faces', which no pipeline code names (CL-038).
- Swimming art is its own drawing, not a byte copy of the walking body (CL-044).

## Open questions

None yet. A question the record does not settle goes here with who asked it and when, and to the Conductor as a card to ask.

## Run log

- 2026-11-01: seeded by the builder of `ARTIST_ROLE_BUILD_ONE_JUDGE_KEEPS_MEMORY`.
