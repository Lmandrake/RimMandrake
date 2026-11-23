# Agent brief — writing a species canon reference entry

Read this whole file before you start. Your prompt names the species that you own. This file says what to do for
each of them. This file is reusable: each future batch reads this file instead of a new brief.

## Why this library exists

The owner uses this library to **correct how the races LOOK in game**. A text-only prompt invents the appearance
wrong. This library was built to catch that failure. So the most valuable content that you produce is:

- **appearance, behaviour, unusual abilities, and size** (the owner's four, verbatim)
- the **visual brief**: look at the actual reference images and say what they show. **Where the images disagree with
  the prose, say so loudly and trust the images on appearance.** The anooba entry's text said "varying tones of gray"
  while all three images showed tiger-like stripes. That sentence is why the library is worth having.

## Hard requirement: write incrementally

A watchdog keeps killing agents on this job at around ten minutes. Every agent that held its results in memory lost
them.

- Write each `description.md` **the moment that species is done.** Never batch.
- If you are running long, stop cleanly. Then append a status line to `RACES_TODO.md`. The line names which species you
  finished and which you did not.
- Whatever is on disk when you die is the deliverable. Act accordingly.

## Entry format — copy it, do not invent it

Before you write anything, read `anooba/description.md` (the original) and `hutt/description.md` (a species example).
Then create `design/RimStarWars/canon_references/<slug>/` with:

- **`description.md`**, with sections in this order:
  - `# Name`
  - a `**defName**:` line
  - `## Sourced text (Wookieepedia)`
  - `## Visual brief`
  - `## Source URLs`
  - `## Candidate images`
  - `## ruling` — left **empty**, with a note that the owner has not reviewed it. The ruling is his, never yours.
- **reference images**, named `wookieepedia_<what-it-is>.jpg`
- **`donor_current_sprite.png`**, if the repo already has art for that species. The only art on disk can be a corpse
  or a desiccated variant. If so, say so and treat that art as weak evidence. The anooba entry does this correctly.

**defNames:** the shipping list is `src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, with 70
xenotypes. That file is **generated, so never edit it.**

- `RACES_TODO.md` already records the defName for every species. Verify it against the XML, and use the real one.
- If no defName exists, say so plainly. **Never invent a defName.**

## Fetching

**WebSearch is dead on this model group.**

🔑 **Try plain `curl` to the API first — it works, and it is far faster than Fetcher.** A batch measured this on
2026-09-15, and that batch completed all seven of its species this way. `curl` to `starwars.fandom.com/api.php`
returned wikitext directly, with **no Cloudflare block**. Only the rendered article HTML is walled; the API is not. So:

```
curl -s 'https://starwars.fandom.com/api.php?action=parse&page=<PageName>&format=json&prop=wikitext'
```

Fall back to Fetcher (invoke the `fetcher` skill) only if `curl` is actually blocked.

⚠️ **Fetcher truncates at 50,000 characters, and long species articles exceed it.** A batch lost the Biology sections
of two species this way.

- If you must use Fetcher and the text is cut off, **say in the entry that the remainder is UNREAD rather than
  absent**. UNREAD and absent are different claims, and only one of them is honest.
- `curl` has no such cap, which is another reason to prefer `curl`.

Other fetching rules:

- **Never request the rendered article HTML.** That is the Cloudflare-walled path. Use the API endpoint above.
- **Page-title traps are real.** The Rakata article is titled **Rakatan**, and its actual substance lives in
  `Rakata/Legends`. A main page can be a stub with an empty infobox. Then check the `/Legends` variant before you
  conclude that the species is undocumented.
- **Prefer FETCH of URLs you construct over SEARCH.** Fetcher's SEARCH degrades silently and returns thin results.
  Species article names are predictable.
- `https://www.starwars.com/databank/<name>` sometimes carries official text.
- Images live at `https://static.wikia.nocookie.net/starwars/images/...`. Download the real files; do not merely cite
  them.
- A FETCH returns in **well under a second.** Poll for the delivery immediately; do not sleep first. Confirm success by
  reading `MANIFEST.txt` in the delivery folder or `Complete/<id>.txt.log`. Do not infer success from files existing.
- **If a fetch pattern fails twice, note it in the entry and move on.** Do not loop.

## 🔴 Do not read oversized images — it kills your session

If you view an image over **2000px in either dimension**, the run aborts outright. You then lose each species that you
had not yet written. One batch died this way with two of its five species unwritten.

Wookieepedia images are frequently far larger than 2000px. So before you view a downloaded image, check its size. View
a downscaled copy if needed:

```
sips -g pixelWidth -g pixelHeight <file>                 # check dimensions
sips -Z 1600 <file> --out /tmp/<name>_small.jpg           # downscale a COPY to /tmp
```

Keep the full-size original in the entry directory, because the original is the reference asset. View only the `/tmp`
copy. Never downscale the original in place.

The image limit is also a reason to write each entry as you finish it. A session that dies on image four does not take entries one
through three with it.

## Discipline

- **Every fact carries its source URL.** No URL, no fact.
- **Distinguish wikitext that you actually pulled from search snippets that you did not pull.** Mark a snippet claim
  unconfirmed. The anooba entry flags a claim about Tuskens this way, because the claim appeared only in a snippet and
  not in the article body.
- **Never invent a height, mass, lifespan or date.** Unsourced means absent. The Rakata entry correctly recorded all
  three as unsourced rather than guessing. That record of unsourced values is the standard.
- **Check whether an image is one that the wiki disowns.** The Rakata directory contained a Mon Calamari that someone
  had mislabelled. It also held a figure that Lucasfilm confirmed was "generic alien extra #3457". Both images are kept,
  but labelled as negative references. Do the same.
- **Flag loudly when a repo def contradicts canon.** The Rakata xenotype carries psychic genes, although post-plague
  Rakata are Force-blind. It also has orange/brown skin where canon is grey to reddish-grey. Findings like that are the
  single most useful thing that you can report, because the owner wants this library for exactly that. **Report them;
  do not fix the def yourself.**
- **Do not run `git commit` or `git push`.** Several agents share this git index, and the window commits for you.
- Do not modify any existing entry directory. Do not touch the 45 pre-existing creature entries.

## If your subject is a DROID, three things change

Everything above still applies. The differences are:

1. **Add a `## Provenance` section** after the sourced text. The section carries **manufacturer**, **era / time
   period**, and **typical owners** (which species, factions or worlds actually used the droid). The owner asked for
   these three by name. The same rule applies as to every other fact: each field cites a URL or is absent.
   ⚠️ **Era is usually genuinely missing.** A script checked all 1,757 droid articles, and only 48 carry an era. So a
   blank era is the normal, correct answer, and the owner has ruled that it stays blank. Do not infer an era from the
   droid's name, its manufacturer, or the film that you remember it from.

2. **One entry per REPO CHASSIS, not per canon variant.** The "in repo" column of `DROIDS_INDEX.md` groups them: 11
   canon droideka variants share one repo sprite set, and 13 B1 variants share another. The sprite is the unit of art
   correction. So write one entry that covers the chassis, and **list the canon variants it stands for** inside the
   entry. Take the slug from the chassis, e.g. `droid_droideka`, `droid_b1`, `droid_hk_series`. Prefix the slug with
   `droid_`, so that droids sort together and never collide with a species slug.

3. **The def target is different.** Droids are not xenotypes. Find what actually defines them in this repo:
   PawnKindDefs, ThingDefs, and the sprites under `design/Jawa/fauna/sprites/` with names like
   `JDSCIS_B1_Security_Droid.png` and `OuterRim_MSEDroid.png`. First read `design/Jawa/worldbuilding/droid_taxonomy.md`
   and `design/Jawa/reconciled_lore/08_droids.md`. **Never invent a defName.** If you cannot find one, say so.

The source of truth for which droids are in scope is the `in repo` column of
`design/RimStarWars/canon_references/DROIDS_INDEX.md`.

## 🔴 What a regen is validated against — owner ruled 2026-09-15

**Sourced canon plus the visual brief IS the target.**

- The owner does not rule every entry. He rules where he wants to depart from canon deliberately.
- Where canon is ambiguous or a regen is contested, an art-judge agent decides first
  (`design/RimMandrake/delegation_policy.md`, owner 2026-10-22). He then reviews the curated result.
- So an empty `## ruling` section does **not** mean that the entry is unusable. An empty ruling means that canon
  stands unopposed.

The consequence for you: the entry must be good enough to be judged against directly. So every entry carries the two
sections below.

## Two sections every entry must carry

**`## Must show`** — three to six **testable** items distilled from that entry's own visual brief. Each item is a
thing that a reviewer can look at a sprite and answer yes or no about. Not prose, not atmosphere. Write the items as a
checklist:

```
## Must show
- [ ] Banded/striped coat, not flat grey — three independent images agree
- [ ] Large erect ears with pink-toned interiors
- [ ] Spiky dorsal mane from skull down the spine
- [ ] Front legs visibly longer than hind (sloped, hyena stance)
- [ ] Chin tusk projecting from the lower jaw
```

Distil the items from what the visual brief already says. **Add no new claims.** If a claim is not in the visual brief
above the checklist, the claim does not belong in the checklist. Where the visual brief flags that images contradict
the prose, the checklist follows the images.

**`## Engine limits`** — any constraint that makes part of the canon appearance **undisplayable as things stand**.
This section exists so that a regen brief cannot ask for the impossible. Write `none known` if there are none. The
limits found so far:

- **A single-channel tint mask cannot express a two-tone or patterned animal.** This blocks the Herglic's orca
  eye-patch and throat, Lasat striping, Cathar striping, and any horn or appendage that must differ in hue from skin
  (Iktotchi). Such a pattern needs **art**, not a colour value.
- **`useSkinShader: false` over a greyscale mask means no skin gene can tint that face.** This is known on Bothan,
  Gungan, Duros and Twi'lek heads. Duros and Twi'lek have no mask file at all. ⚠️ What actually renders needs in-game
  confirmation.
- **A red-channel-only mask** cannot give horns a different hue from skin (Iktotchi).
- **Shared textures**: `Races_Primitive.xml` reuses the MSE droid texture, so an edit to that texture changes two
  races.
- 🔴 **The pawn rig itself.** RimWorld draws a pawn as a head plus a body on a fixed human-shaped skeleton. So a
  species whose defining feature lives in **neck length, leg form or overall proportion cannot express it at all**. No
  texture fixes this. Found on **Ithorian** (forward-curving neck), **Kaminoan** (neck roughly twice head length, head
  and neck about 20% of standing height), **Muun** (long-legged narrow body) and **Lasat** (digitigrade legs on a human
  skeleton).

  The rig limit is the hardest class of limit, because it is not a bug and not a missing asset: it is the renderer.
  Record the rig limit plainly, so that nobody commissions art that chases it. Treat the best achievable silhouette as the target instead.

**Keep the three classes apart — their fixes are completely different:**

| class | what it means | fix |
|---|---|---|
| **missing gene** | the def simply does not carry the trait | edit the def |
| **engine limit** | the shader or mask pipeline cannot express it | new art, or a mask with more channels |
| **rig limit** | the pawn skeleton cannot express it | nothing; retarget the goal |

To record a limit is not to fix it. A fix is a cosmetic change. A second agent judges that change against
`design/RimMandrake/art_judge_brief.md` (owner, 2026-10-22). The fix must not break animated faces.

## What to report

Report in under 250 words:

- which species you completed;
- any def-versus-canon contradictions that you found;
- anything that you could not source.
