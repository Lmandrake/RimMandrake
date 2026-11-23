---
name: rimworld-canon-references
description: Grade Star Wars creature, species and droid work against design/RimStarWars/canon_references/ — 137 entries whose sourced canon plus visual brief IS the acceptance target, so appearance is READ from the entry instead of invented, `## Must show` is the pass bar and `## Engine limits` says which parts of canon may not be asked for at all. Use before generating, regenerating, reskinning or judging any Star Wars creature/species/droid sprite; before writing or correcting a xenotype, PawnKindDef or ThingDef for one; when a review says a species looks wrong; before calling an appearance defect fixable, because the rig-limit class cannot be fixed at all and art chasing it is pure waste; and before any cosmetic change, which a second agent judges against design/RimMandrake/art_judge_brief.md.
---

# Canon references — the entry is the target, not your memory

`design/RimStarWars/canon_references/` is the canon library. The library holds one directory for each droid chassis,
species and creature. A directory holds an entry (a `description.md` file) and its reference images. **The library
exists because a text-only prompt invents appearance wrong.** `AGENT_BRIEF.md` in the library opens with that reason,
and that reason is the whole point.

`design/RimMandrake/standing_rulings.md` §What is where says what the library holds, and holds the owner's standing
rules for the library.

One rule governs this file: **for any subject with an entry, the entry is the brief. Read the entry before you draw,
patch or grade.** Nothing enforces this rule but you. The art pipeline's grader
(`src/RimMandrake/Utils/artpipe/canon_check.py`) grades a finished render against the entry, and only advises.

> **The two sections that are the brief: `## Must show` and `## Engine limits`.**
> `## Must show` is the pass bar. `## Engine limits` is the list of things that you may not ask for.
> Read both sections before you write a prompt, not after you look at the render.

| I want to… | Start at |
|---|---|
| find the entry for the thing in hand | §1 |
| generate or regenerate a sprite | §2 |
| act on a defect I found | §3 |
| read the `## ruling` section | §4 |
| change how something looks | §5 — stop first |
| check the entry still matches the def it grades | §6 |
| **write or refresh an entry** | `../../design/RimStarWars/canon_references/AGENT_BRIEF.md` — not this file |

---

## 1. Find the entry — and what to do when there is none

The library has one directory for each subject. The directory name is the subject's slug:
`canon_references/<slug>/description.md`. A droid slug starts with `droid_`. A droid has **one entry per repo chassis,
not per canon variant**. For example, `droid_b1` covers 11 canon rows. `AGENT_BRIEF.md` holds the reasoning.

**The slug is not the defName.** Every entry carries a `**defName**:` line. To go from a def to its entry, search the
library for the defName. Do not guess the slug.

- `INDEX.md` lists every slug with its defNames. `gen_index.py` in the library generates `INDEX.md`.
- `DROIDS_INDEX.md` is the droid roster. Its `in repo` column is the scope of record for droids.
- `RACES_TODO.md` is the species roster.

🔑 **An entry can be a pointer.** `massassi` is a caste of `sith_species`. The shared anatomy lives in the parent
entry. Follow the chain before you conclude that an entry is thin.

🔴 **No entry means you have no target.** Two moves are legitimate, and to invent is neither of them:

- write the entry first, under `AGENT_BRIEF.md`;
- say that the art work or def work is blocked on the entry.

A canon fact that you looked up inline and did not record with its source URL is not a target. Nobody can grade
against such a fact later. The library was built to end that failure.

⛔ **A third-party mod's defName is not a source, even when it is the only thing you have.**

- The general shape: a donor mod (a third-party mod whose content we use) ships a plausible name. Someone then reads
  the name back as proof. A name read back is not a source.
- Example: a "felucian glowspore" wild-plant row was recorded as "Canon". The row cited `Plant_FelucianGlowspore_Wild`
  as its evidence. `glowspore` returns zero Wookieepedia hits. The name is the mod author's own invention.
- Absence from our own entries is no evidence either way. Write the entry as UNSOURCED and say so. Do not turn a donor
  defName into a citation.

🔑 **Looking up a subject on Wookieepedia: a MISSING page from a guessed exact title is not evidence the subject is
non-canon.**

- A guessed title misses a real page constantly. `Brylark`, `Vesuvague_hanging_tree` and `Felucian_glowspore` all
  returned MISSING. The real pages of the first two are `Brylark tree` and `Vesuvague tree`.
- Use the search API instead of a direct page fetch: `action=query&list=search&srsearch=<name>`.
- On zero results, the search API omits `searchinfo` entirely. So a parser that reads `totalhits` raises an error on
  exactly the zero-result case, which is a valid answer. Instead, test whether the `search` array is empty.

**Fetching the article itself: only the RENDERED HTML is Cloudflare-walled.**

- Prefer `curl`:

  ```
  curl -s 'https://starwars.fandom.com/api.php?action=parse&page=<X>&format=json&prop=wikitext'
  ```

  `curl` works without a login and has no size cap.
- Fetcher (the project `~/dev/Fetcher`) also works, but Fetcher TRUNCATES AT 50,000 CHARS. Fetcher has silently lost a
  whole species' Biology section that way.
- A main page can be a stub. Its real content then often lives at `<Name>/Legends`.
- A page's own TITLE can lie. The Rakata article is titled "Rakatan".

**Canon web searches need controls.**

- fandom.com answers 403 to python-urllib's default User-Agent. `curl` with a browser User-Agent works.
- Run a positive control before you trust any zero-hit search (for example, dewback → 3 hits).
- A Wookieepedia `list=search` hit is not an occurrence. The search 'brogg' hit a page whose wikitext holds zero
  'brogg'. Probe the page with `action=parse` before you call a name collision.

---

## 2. Before generating anything

- **`## Must show` is the pass bar, and it is testable by construction.**
  - A reviewer can answer yes or no to each line on the finished sprite. `AGENT_BRIEF.md` asks for 3–6 lines. Many
    entries hold more. Every visual line that the facing can show counts.
  - Carry the lines into the prompt. Then check them off against the render **at display size**.
  - For craft rules (canvas, alpha, facings, px/cell), use `generating-rimworld-sprites`. This skill supplies only the
    subject.
- **`## Engine limits` is read BEFORE the prompt.**
  - The section exists so that a brief cannot ask for the impossible.
  - The queue filler (`src/RimMandrake/Utils/artpipe/fill_queue.py`) adds only `## Visual brief` and `## Must show` to
    a job. So carry the limits yourself.
  - **`none known` is a real answer, and the usual one.** The words mean "go ahead". The words do not mean "unchecked".
- **Where the brief says the images contradict the prose, the images win on appearance.** The checklist already
  follows the images. Do not argue the point again from the sourced text. The disagreement is recorded deliberately.
- **The entry decides WHICH canon form you are drawing.**
  - Some subjects have two forms that are not variants of each other. Example: the Massassi's original form and
    alchemically-altered form.
  - The checklist is written conditionally on the choice. Pick one form explicitly, and say which. A sprite between
    the two forms matches neither form.
- **A negative reference is still a reference.** Some entries deliberately keep an image that the wiki disowns, or
  that a colourist got wrong. The entry labels such an image. Read the label before you sample a palette.
- **"Star Wars style" naming is not Star Wars IP: the tier line is IP, not flavour.**
  - An invented exotic name may live in the franchise-free `RM_` tier. Only a genuine canon name routes through the
    Utinni patch layer.
  - Owner, 2026-09-22: "The top mod without star wars will look precisely the same as the star wars enhanced one save
    for any star wars beasts we populate it with".
  - The ruling is question Q11a (a name that only sounds like Star Wars) in
    `design/RimMandrake/biome_mod_architecture.md`.
- **Read the canon entry and the shipped source before you design a canon-adjacent feature. This project has usually
  already answered the question.**
  - The single dianoga entry answered six design questions. The six were transparent colour change, humming that scares
    prey, hearing, water dependency, limb regeneration and bone-eating bait.
  - Shipped source, example 1: `RM_ToxinSealant`, with `RM_MapComponent_LivingRegrowth` as the gate on regrowth.
  - Shipped source, example 2: `RM_CompTerritorialAnchor`/`RM_AnchorGuard`.
  - Shipped source, example 3: `RM_MapComponent_StrandingPools.IsReconnected()`. The method asks whether a stranded
    pool joins open water. That question IS the swim-eligibility test. Its 4-way water flood-fill is in
    `RM_PoolKernel.Reconnected()`.
  - Shipped source, example 4: `RM_CompVerminBreeder` stops at a hard cap. `RM_VerminPressureExtension` holds the soft
    cap and the hard cap. `RM_MapComponent_VerminPopulation` computes the aggression ramp between them.
  - Before you claim that a name "ships", check what KIND of thing the name resolved to. `RUT_WardenMother` exists
    only as an XML example inside a C# comment. The shipped def is `RM_WardenMother`.

---

## 3. Classify the defect BEFORE proposing a fix

The three classes and their fixes are the owner's. The table is in `AGENT_BRIEF.md > Two sections every entry must
carry`. `design/RimMandrake/standing_rulings.md` §What is where restates the classes. The table does not say **how to
tell which class you are looking at**. So ask these questions in order:

1. **Does the mod already own something that expresses the appearance?** That thing is a gene, a field, or a value in
   the list that a def picks from (for example the skin genes of a xenotype).
   - If yes, the defect is a **missing gene**: the def simply does not list the thing.
   - Search the shipped defs to settle this question. Do not answer from memory.
   - Example: the Massassi entry says that the lifespan is expressible. `RSW_lifespan_nine` and `RSW_lifespan_half`
     are declared in `src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml`. Both genes are merely absent from that
     xenotype.
2. **Is the appearance two-tone, patterned or different per region?** Then the defect is an **engine limit**. A
   single-channel tint mask cannot express such an appearance, and no colour value ever will. The fix needs art or
   more mask channels.
3. **Is the defect in neck length, leg form, or overall body proportion?** Then the defect is a **rig limit and cannot
   be fixed at all.**
   - The named cases are **Ithorian** (forward-curving neck), **Kaminoan** (proportion), **Muun** (long-legged narrow
     body) and **Lasat** (digitigrade legs).
   - 🔴 **Stop. Retarget to the best achievable silhouette, and say in the report that you did.** A pass that chases a
     rig limit produces nothing. This section exists to prevent that waste.

⚠️ **A `Def-versus-canon` list in an entry is a findings list, not a work order.** The entry's author wrote the list
under instructions to report and not to fix. The queue item that you work under decides whether the def may change. §5
applies in each case.

---

## 4. An empty `## ruling` means canon stands unopposed

Most entries have an empty `## ruling`. The words `(empty — owner has not reviewed …)` also mean an empty ruling.
Empty is the normal state, and the entry is fully usable.

- The owner rules on a deliberate departure from canon (`AGENT_BRIEF.md`, his ruling of 2026-09-15). The
  Conductor may rule on one too, as its own recorded act (§5).
- Ambiguity and contested regens go to an art-judge agent first (`design/RimMandrake/delegation_policy.md`,
  2026-10-22).

⛔ **Never block, defer or downgrade work because an entry is "unruled".** That reading turns every complete brief with
an empty ruling into a blocker.

Where a ruling **does** exist:

- **The ruling outranks the sourced canon and the visual brief**, including the library's own earlier read. Example:
  the owner rejected the quadruped finding in `gizka`. The brief's line was superseded. The entry now says bipedal.
- **The ruling usually names a specific image FILENAME** as the reference of record. Use the file that the ruling
  names, not your own pick from the directory.
- The ruling often carries verbatim instructions ("Follow #3 closely", "Make it Olive colored").
- The named file can be gone: a later ruling of the owner deleted it (for example `cancell` and `dragonsnake`). Then
  follow the later ruling. The entry's `## Visual brief` or `## ruling` says what replaced the file.

⚠️ **Reading a drafted checklist to the owner line by line is how you find out which items were never his intent.**
One sitting read such a checklist, in the style of `## Must show`. That sitting produced three rulings that DELETED
art. One ruling turned a doc's own self-described hardest, precedent-less asset into an asset that was already on the
list. If the owner cannot accept a line, the cause is usually not a sourcing error. Usually somebody invented a design
claim and never tested it against his intent.

---

## 5. Cosmetic changes are judged by a second agent, not asked of the owner

Owner, 2026-10-22: *"Nearly everything including art."* The policy is `design/RimMandrake/delegation_policy.md`. The
constraints are in `design/RimMandrake/art_judge_brief.md`. The brief keeps the reason of the old rule: a pawn cosmetic
change must not break animated faces. Read this table at the moment that you are about to act:

| you are about to… | what it needs |
|---|---|
| record a finding, limit or contradiction **in the entry** | nothing — recording is not fixing |
| add/remove/swap a head, eye, skin, hair or body gene | a judge agent's KEEP (brief §F, Cosmetic changes to pawns), logged `--why "delegated: cosmetic"` |
| change a `texPath`, or replace shipped art with a regen | a judge agent's KEEP; never over a picture he KEPT (that stays his; the open exceptions are in policy §2) |
| depart from canon deliberately, or write an entry's `## ruling` | the owner, or the Conductor window as its own recorded act (policy §2). A helper, judge or other seat only records a ruling that one of them gave |

---

## 6. Is the entry still true about the def it grades?

Entries cite defNames and repo paths, and both move. Make three checks, all offline:

- **The defName** — search `src/` for the entry's `**defName**:` value.
  - If the defName is gone, the entry grades a def that nobody ships. A rename is the likely cause.
  - A rename to the tier grammar (`design/NAMING_SCHEME_PLAN.md`) is ordinary owed work. Nothing gates such a rename
    (`NAMING_SCHEME_EXECUTION_1`, the one-time rename migration, closed 2026-08-31).
- **The cited repo paths** — normally no entry cites a missing `src/…` or `design/…` path. So one miss is a real,
  new break.
- **The local assets** — reference images live **in the entry directory**. An entry that names a file as
  its image has a real defect if the file is not there.
  - Example: `mirialan` cited `wookieepedia_mirialan_luminara_swm41.png` in three places. The disk held
    `wookieepedia_luminaraunduli_swm41.png`. The entry also said that the file was "already on disk under that name"
    and "re-verified this pass". That claim was never true.

🔴 **A prose claim that a file was verified is not verification. List the directory.**

⚠️ **A naive filename check is noisy — confirm before reporting.** Four kinds of filename are legitimate:

- an upstream Wookieepedia `File:` title;
- a sibling sprite that lives under `design/Jawa/fauna/sprites/`;
- another entry's asset, by cross-reference (`mon_calamari` names a bad image that `rakata/` once held);
- an image that the entry records as deleted or absent. The realism sweep of 2026-10-08 (the owner's order to replace
  cartoon images) deleted many images. And "there is **no** `donor_current_sprite.png`" is a correct statement that
  repo art is missing, not a dangling reference.

---

## What this skill deliberately does not carry

- **Writing or refreshing an entry**: `canon_references/AGENT_BRIEF.md`. That file is the operating doc. `AGENT_BRIEF.md`
  holds the format, sourcing discipline, the fetching route, the 2000px-image trap that kills a session, and the
  write-incrementally rule. This skill only says how to *consume* what that file produces.
- **The owner's library-wide rulings** (the three defect classes, what an empty ruling means):
  `design/RimMandrake/standing_rulings.md` §What is where, and `AGENT_BRIEF.md`.
- **Sprite craft** → `generating-rimworld-sprites`.
- **Genes, heads and why a species "has no art"** → `rimworld-xenotypes`.
- **Finding the art on disk** → `reading-rimworld-graphics`.
- **Deploying the art** → `rimworld-deploy`.
- **Counts, dates and incidents behind these lessons** → `references/history.md`.

⛔ **Do not upgrade an `## Engine limits` line into an engine fact.**

- Those lines are entry authors' recorded findings. `AGENT_BRIEF.md` says of the
  `useSkinShader: false` limit that what actually renders needs in-game confirmation.
- RimSage (`mcp__rimsage__*`) answers on Archmagi (the Windows desktop) only. RimSage has never connected on the Laptop
  (the owner's Mac, `mt-400028`). So what the shader or the renderer actually does **cannot be measured on the Laptop
  at all**.
- Cite the limit as the entry's finding, or answer UNMEASURED.

## Where it all lives

```
design/RimStarWars/canon_references/<slug>/description.md   the target
                                    <slug>/*.jpg|png|webp   its reference images
                                    AGENT_BRIEF.md          how to write an entry
                                    INDEX.md                every slug with its defNames (generated)
                                    DROIDS_INDEX.md         which droids are in scope
                                    RACES_TODO.md           the species roster
src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml
                                                            species defs — GENERATED, never edit
src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/            most creature defs (more: SeaBeasts/, DesertPort/, Livestock/ …)
src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/<Name>/  our creature redraws (donor defs patched to them in Patches/ArtFold/)
```
