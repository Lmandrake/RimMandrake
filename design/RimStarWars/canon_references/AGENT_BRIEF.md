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

## If your subject is a DROID, three things change

Everything above still applies. These are the differences:

1. **Add a `## Provenance` section** after the sourced text, carrying **manufacturer**,
   **era / time period**, and **typical owners** — which species, factions or worlds actually
   used it. The owner asked for these three by name. Same rule as every other fact: each field
   cites a URL or is absent. ⚠️ **Era is usually genuinely missing** — a script checked all
   1,757 droid articles and only 48 carry one, so a blank here is the normal, correct answer
   and the owner has ruled that it stays blank. Do not infer an era from the droid's name, its
   manufacturer, or which film you remember it from.

2. **One entry per REPO CHASSIS, not per canon variant.** The index's "in repo" column groups
   them: 11 canon droideka variants share one repo sprite set, and 13 B1 variants share
   another. The sprite is the unit of art correction, so write one entry covering the chassis
   and **list the canon variants it stands for** inside it. Slug from the chassis, e.g.
   `droid_droideka`, `droid_b1`, `droid_hk_series` — prefix `droid_` so droids sort together
   and never collide with a species slug.

3. **The def target is different.** Droids are not xenotypes. Find what actually defines them
   in this repo — PawnKindDefs, ThingDefs, and the sprites under `design/Jawa/fauna/sprites/`
   with names like `JDSCIS_B1_Security_Droid.png` and `OuterRim_MSEDroid.png`. Read
   `design/Jawa/worldbuilding/droid_taxonomy.md` and `design/Jawa/reconciled_lore/08_droids.md`
   first. **Never invent a defName** — if you cannot find one, say so.

Source of truth for which droids are in scope: the `in repo` column of
`design/RimStarWars/canon_references/DROIDS_INDEX.md`.

## 🔴 What a regen is validated against — owner ruled 2026-09-15

**Sourced canon plus the visual brief IS the target.** The owner does not rule every entry;
he rules only where canon is ambiguous, where he wants to depart from canon deliberately, or
where a regen is contested. So an empty `## ruling` section does **not** mean the entry is
unusable — it means canon stands unopposed.

Consequence for you: the entry must be good enough to be judged against directly. Which is
why every entry carries the two sections below.

## Two sections every entry must carry

**`## Must show`** — three to six **testable** items distilled from that entry's own visual
brief, each one a thing a reviewer can look at a sprite and answer yes or no about. Not
prose, not atmosphere. Written as a checklist:

```
## Must show
- [ ] Banded/striped coat, not flat grey — three independent images agree
- [ ] Large erect ears with pink-toned interiors
- [ ] Spiky dorsal mane from skull down the spine
- [ ] Front legs visibly longer than hind (sloped, hyena stance)
- [ ] Chin tusk projecting from the lower jaw
```

Distil from what the brief already says. **Add no new claims** — if it is not in the brief
above it, it does not belong in the checklist. Where the brief flags that images contradict
the prose, the checklist follows the images.

**`## Engine limits`** — any constraint that makes part of the canon appearance
**undisplayable as things stand**, so a regen brief cannot ask for the impossible. Write
`none known` if there are none. The ones found so far:

- **A single-channel tint mask cannot express a two-tone or patterned animal.** This blocks
  the Herglic's orca eye-patch and throat, Lasat striping, Cathar striping, and any horn or
  appendage that must differ in hue from skin (Iktotchi). Such a pattern needs **art**, not a
  colour value.
- **`useSkinShader: false` over a greyscale mask means no skin gene can tint that face.**
  Known on Bothan, Gungan, Duros and Twi'lek heads; Duros and Twi'lek have no mask file at
  all. ⚠️ Needs in-game confirmation of what actually renders.
- **A red-channel-only mask** cannot give horns a different hue from skin (Iktotchi).
- **Shared textures**: `Races_Primitive.xml` reuses the MSE droid texture, so editing it
  changes two races.

⛔ **Cosmetic changes need the owner's permission** before they are made — they can break
animated faces. Recording a limit is not the same as fixing it.

## What to report

Under 250 words: which species you completed, any def-versus-canon contradictions found,
and anything you could not source.
