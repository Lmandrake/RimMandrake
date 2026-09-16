# Agent brief — writing a species canon reference entry

Read this whole file before starting. Your prompt names which species you own; this file
says what to do for each of them. Reusable: any future batch reads this instead of being
re-briefed.

## Why this library exists

The owner uses it to **correct how the races LOOK in game**. A text-only prompt invents
appearance wrong — that is the failure this library was built to catch. So the most
valuable content you produce is:

- **appearance, behaviour, unusual abilities, and size** (the owner's four, verbatim)
- the **visual brief**, where you look at the actual reference images and say what they
  show — and **where the images disagree with the prose, say so loudly and trust the
  images on appearance.** The anooba entry's text said "varying tones of gray" while all
  three images showed tiger-like stripes. That sentence is why the library is worth having.

## Hard requirement: write incrementally

Agents on this job keep getting killed by a watchdog at around ten minutes. Every one
that held results in memory lost them.

- Write each `description.md` **the moment that species is done.** Never batch.
- If you are running long, stop cleanly and append a status line to `RACES_TODO.md`
  naming which species you finished and which you did not.
- Whatever is on disk when you die is the deliverable. Act accordingly.

## Entry format — copy it, do not invent it

Read `anooba/description.md` (the original) and `hutt/description.md` (a species example)
before writing anything. Then create `design/RimStarWars/canon_references/<slug>/` with:

- **`description.md`**, sections in this order:
  - `# Name`
  - a `**defName**:` line
  - `## Sourced text (Wookieepedia)`
  - `## Visual brief`
  - `## Source URLs`
  - `## Candidate images`
  - `## ruling` — left **empty**, noting the owner has not reviewed it. The ruling is his,
    never yours.
- **reference images**, named `wookieepedia_<what-it-is>.jpg`
- **`donor_current_sprite.png`** if the repo already has art for that species. If the only
  art on disk is a corpse or desiccated variant, say so and treat it as weak evidence —
  the anooba entry does this correctly.

**defNames:** the shipping list is
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml` — 70
xenotypes, and it is **generated, so never edit it.** `RACES_TODO.md` already records the
defName for every species; verify against the XML and use the real one. If none exists,
say so plainly. **Never invent a defName.**

## Fetching

**WebSearch is dead on this model group.**

🔑 **Try plain `curl` to the API first — it works, and it is far faster than Fetcher.**
Measured 2026-09-15 by a batch that completed all seven of its species this way:
`curl` to `starwars.fandom.com/api.php` returned wikitext directly with **no Cloudflare
block**. Only the rendered article HTML is walled; the API is not. So:

```
curl -s 'https://starwars.fandom.com/api.php?action=parse&page=<PageName>&format=json&prop=wikitext'
```

Fall back to Fetcher (invoke the `fetcher` skill) only if `curl` is actually blocked.

⚠️ **Fetcher truncates at 50,000 characters, and long species articles exceed it.** A
batch lost the Biology sections of two species this way. If you must use Fetcher and the
text is cut off, **say in the entry that the remainder is UNREAD rather than absent** —
those are different claims, and only one of them is honest. `curl` has no such cap, which
is another reason to prefer it.

- **Never request the rendered article HTML** — that is the Cloudflare-walled path. Use the
  API endpoint above.
- **Page-title traps are real.** The Rakata article is titled **Rakatan**, and its actual
  substance lives in `Rakata/Legends`. If a main page is a stub with an empty infobox,
  check the `/Legends` variant before concluding the species is undocumented.
- **Prefer FETCH of URLs you construct over SEARCH** — Fetcher's SEARCH degrades silently
  and returns thin results. Species article names are predictable.
- `https://www.starwars.com/databank/<name>` sometimes carries official text.
- Images live at `https://static.wikia.nocookie.net/starwars/images/...`. Download the real
  files; do not merely cite them.
- A FETCH returns in **well under a second.** Poll for the delivery immediately — do not
  sleep first. Confirm success by reading `MANIFEST.txt` in the delivery folder or
  `Complete/<id>.txt.log`, rather than inferring it from files existing.
- **If a fetch pattern fails twice, note it in the entry and move on.** Do not loop.

## 🔴 Do not read oversized images — it kills your session

An image over **2000px in either dimension** aborts the run outright when you view it, and
you lose any species you had not yet written. One batch died this way with two of its five
species unwritten.

Wookieepedia images are frequently far larger than 2000px. So before viewing a downloaded
image, check it and view a downscaled copy if needed:

```
sips -g pixelWidth -g pixelHeight <file>                 # check dimensions
sips -Z 1600 <file> --out /tmp/<name>_small.jpg           # downscale a COPY to /tmp
```

Keep the full-size original in the entry directory — it is the reference asset. View only
the `/tmp` copy. Never downscale the original in place.

This is also a reason to write each entry as you finish it: a session that dies on image
four does not take entries one through three with it.

## Discipline

- **Every fact carries its source URL.** No URL, no fact.
- **Distinguish wikitext you actually pulled from search snippets you did not.** Mark the
  latter unconfirmed. The anooba entry flags a claim about Tuskens this way, because it
  appeared only in a snippet and not in the article body.
- **Never invent a height, mass, lifespan or date.** Unsourced means absent. The Rakata
  entry correctly recorded all three as unsourced rather than guessing — that is the
  standard.
- **Check whether an image is one the wiki disowns.** The Rakata directory contained a
  Mon Calamari that someone had mislabelled, and a figure Lucasfilm confirmed was "generic
  alien extra #3457". Both are kept, but labelled as negative references. Do the same.
- **Flag loudly when a repo def contradicts canon.** The Rakata xenotype carries psychic
  genes although post-plague Rakata are Force-blind, and orange/brown skin where canon is
  grey to reddish-grey. Findings like that are the single most useful thing you can report,
  because they are exactly what the owner wants this library for. **Report them; do not fix
  the def yourself.**
- **Do not run `git commit` or `git push`.** Several agents share this index and the window
  commits for you.
- Do not modify any existing entry directory, and do not touch the 45 pre-existing creature
  entries.

## What to report

Under 250 words: which species you completed, any def-versus-canon contradictions found,
and anything you could not source.
