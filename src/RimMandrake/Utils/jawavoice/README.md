# JawaVoice authoring kit

Tooling for writing Jawaese that sounds like the Jawaese already in the mod,
rather than like a bag of syllables with apostrophes in it.

## Why this exists

`JawaVoice_Insults.xml` v1 was written by ear on 2026-08-11. It read fine in
isolation and was measurably wrong against the 639-line corpus already shipping
in `src/Jawa/JawaVoice/Patches/`:

| metric | corpus | v1 |
|---|---|---|
| reduplication | 38.8% | 9.3% |
| top content word | 2.3% | **32.6%** (`nyeta`) |
| breathy `h` | 32.6% | 22.6% |
| doubled vowels | 45.4% | 36.9% |
| words per line | 3.96 | 3.91 ✓ |
| gloss/Jawaese ratio | 2.55 | 2.57 ✓ |

The length instincts were right and the *ear* was wrong. Four scored rewrites
took the insults from there to a composite distance of **0.056**.

The single biggest finding: **reduplication is the grammar, not a tic.** The
corpus doubles a word with a changed final vowel in 38.8% of lines (`bab bab`,
`mihsha mihshu`, `toobba toobbu`), and three of the Grade A canon phrases do it
too — `Togo togu`, `Taa baa`, `M'um m'aloo`. It is treated here as an
**intensifier**: `sh'akka sh'akku` = "priced, and priced again".

## Files

| file | what it does |
|---|---|
| `jawafit.py` | scores a line set on 8 phonological/rhythmic metrics |
| `compose.py` | composite distance from the corpus for both files; run this |
| `lines_insults.py` | the 50 authored Insult/Slight lines, `(Jawaese, gloss)` |
| `lines_ideology.py` | the 47 authored Ideology lines, keyed by defName |
| `header_insults.txt` | doc header prepended to the generated insults XML |
| `genxml.py` | emits `JawaVoice_Insults.xml` |
| `genideo.py` | emits `JawaVoice_Ideology.xml` (header is embedded) |

## Workflow

```bash
# edit the writing
vim src/RimMandrake/Utils/jawavoice/lines_insults.py

# regenerate the patch, then score it
python src/RimMandrake/Utils/jawavoice/genxml.py
python src/RimMandrake/Utils/jawavoice/compose.py

# deploy and parse-check in ONE chain, per CLAUDE.md
python src/RimMandrake/Utils/deploy_custom_mods.py --apply && \
  python skills/rimworld-modding/scripts/validate_patch.py <deployed file>
```

Generation exists because each authored line becomes **four** rules, one per
speaker condition (`PlayerColony`, `PlayerTribe`, `OuterRim_Jawa`,
`OuterRim_JawaTribal`). Grammar conditions AND together and there is no OR, so
four cases means four literal copies. Hand-maintaining them lets the copies
drift apart, and the drift is invisible in play because the engine just picks a
different copy.

## Pidgin glosses (2026-08-12, owner's call)

**The English half is not a translation. It is how the Jawa talks.**

Glosses were originally written as fluent English, which made every speech
bubble a paragraph of subtitle under four syllables of speech. They are now
clipped pidgin: articles dropped, auxiliaries dropped, sentences short.

```
Hands where I can see them. That is    ->  Hands where I see! That is law here.
  the whole of the law here.

Sit. We will go through it one piece   ->  Sit. One piece at time, together,
  at a time, like any salvage.               like salvage.
```

Mean gloss went 10.4 words -> 7.3, longest 17 -> 10. Nothing exceeds one short
line, because nobody reads a paragraph floating over a pawn's head.

⚠️ **This deliberately breaks the `ratio` metric and that is correct.** The
corpus's own glosses are fluent English (*"I'm not feeling well, but I'm sure
I'll recover soon!"*), so corpus gloss length is no longer the target. `ratio`
fell from 2.47 to 1.67 the moment the rewrite landed, while **every Jawaese
metric stayed identical** — proof the change touched only the English. `ratio`
is therefore reported but excluded from the composite. Do not "fix" it by
padding the glosses back out.

## Reading the scores

`compose.py` prints distance from the corpus, lower being better. Treat it as a
**guardrail against a tin ear, not a target.** Two lessons paid for already:

- **Do not chase the flagged metrics.** v2 fixed the three bad numbers and broke
  the four good ones, swapping the `nyeta` crutch for a worse `nooh` crutch at
  42%. Check every column, not the ones you were losing on.
- **A worse score can be the right call.** `lines_ideology.py` sits at 0.171
  against the insults' 0.056, because Ideology leans on canon ceremony
  vocabulary (`ashuna`, `ibana`, `utinni`, `mambay`, `sabioto`) which happens to
  contain no `h` and no apostrophe. A lexicon substitution was tested to close
  it: it improved Ideology to 0.173 and damaged the insults to 0.089, a net
  loss, and was rejected. Forcing sand-and-smell imagery into counselling scenes
  to buy the `h` back would trade real writing for a number.

The `tic` column fires on `ta` ("you"), which a set of lines all addressed *at*
somebody will legitimately repeat. `compose.py` excludes it and reports
top-**content**-word concentration instead.

## What the metrics cannot see

Whether the line is funny. That took a blind review: 36 lines from v1 and v5
shuffled with provenance withheld, each scored 0–3 on *funny*, *distinctively
Jawa*, and *reads as speech not caption*. v5 won 8.26 to 7.00, and the gain was
concentrated in **funny** (2.74 vs 2.00). Two v1 lines scored a perfect 9 and
were rescued into v5's lexicon rather than lost — the manifest joke and the
crate joke. Do that again after any substantial rewrite; the scorer will happily
approve something that is phonologically perfect and completely unfunny.
