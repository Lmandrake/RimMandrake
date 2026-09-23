---
name: rimworld-canon-references
description: Grade Star Wars creature, species and droid work against design/RimStarWars/canon_references/ — 137 entries whose sourced canon plus visual brief IS the acceptance target, so appearance is READ from the entry instead of invented, `## Must show` is the pass bar and `## Engine limits` says which parts of canon may not be asked for at all. Use before generating, regenerating, reskinning or judging any Star Wars creature/species/droid sprite; before writing or correcting a xenotype, PawnKindDef or ThingDef for one; when a review says a species looks wrong; before calling an appearance defect fixable, because the rig-limit class cannot be fixed at all and art chasing it is pure waste; and before any cosmetic change, which needs the owner's permission first.
---

# Canon references — the entry is the target, not your memory

`design/RimStarWars/canon_references/` holds one directory per droid chassis,
species and creature — a `description.md` plus its reference images. **The library
exists because a text-only prompt invents appearance wrong** — that is
`AGENT_BRIEF.md`'s opening and it is the whole point. Its composition and the
owner's standing rules for it are in `CLAUDE.md > What is where`.

So the rule that governs everything here: **for any subject with an entry, the
entry is the brief. Read it before you draw, patch or grade.** Nothing enforces
that but you.

> **The two sections that are the brief: `## Must show` and `## Engine limits`.**
> The first is the pass bar; the second is the list of things you may not ask for.
> Read both before writing a prompt, not after looking at the render.

| I want to… | Start at |
|---|---|
| find the entry for the thing in hand | §1 |
| generate or regenerate a sprite | §2 |
| act on a defect I found | §3 |
| read the `## ruling` section | §4 |
| change how something looks | §5 — ⛔ stop |
| check the entry still matches the def it grades | §6 |
| **write or refresh an entry** | `../../design/RimStarWars/canon_references/AGENT_BRIEF.md` — not this file |

---

## 1. Find the entry — and what to do when there is none

One directory per subject, slug-named: `canon_references/<slug>/description.md`.
Droids are prefixed `droid_` and there is **one entry per repo chassis, not per
canon variant** (`droid_b1` covers 11 canon rows) — the reasoning is in
`AGENT_BRIEF.md`.

**The slug is not the defName.** Every one of the 137 entries carries a
`**defName**:` line, so route from a def to its entry by searching the library
for the defName rather than guessing the slug. The two roster files are
`DROIDS_INDEX.md` (its `in repo` column is the scope of record for droids) and
`RACES_TODO.md`.

🔑 **An entry can be a pointer.** `massassi` is a caste of `sith_species` and the
shared anatomy lives in the parent entry. Follow the chain before concluding an
entry is thin.

🔴 **No entry means you have no target.** Two legitimate moves, and inventing is
neither: write the entry first under `AGENT_BRIEF.md`, or say the art/def work is
blocked on it. A canon fact you looked up inline and did not record with its
source URL is not a target — nobody can grade against it later, which is the
failure the library was built to end.

---

## 2. Before generating anything

- **`## Must show` is the pass bar, and it is testable by construction** — 3–6
  lines a reviewer can answer yes/no on the finished sprite. Carry them into the
  prompt, then check them off against the render **at display size**. Craft rules
  (canvas, alpha, facings, px/cell) are `generating-rimworld-sprites`; this skill
  supplies only the subject.
- **`## Engine limits` is read BEFORE the prompt.** It exists so a brief cannot
  ask for the impossible. **`none known` is a real answer, and the usual one** —
  measured 2026-09-16, **108 of 137** entries say it. It means go ahead, not
  "unchecked".
- **Where the brief says the images contradict the prose, the images win on
  appearance and the checklist already follows them.** Do not re-litigate from the
  sourced text; the disagreement is recorded deliberately.
- **The entry decides WHICH canon form you are drawing.** Some subjects have two
  that are not variants of each other — the Massassi's original and
  alchemically-altered forms — and the checklist is written conditionally on the
  choice. Pick one explicitly and say which; a sprite between the two lands on
  neither.
- **A negative reference is still a reference.** Entries deliberately keep images
  the wiki disowns or that a colourist got wrong, labelled as such. Read the label
  before sampling a palette.

---

## 3. Classify the defect BEFORE proposing a fix

The three classes and their fixes are the owner's, tabulated in
`AGENT_BRIEF.md > Two sections every entry must carry` and in the repo's
`CLAUDE.md`. What that table does not give you is **how to tell which one you are
looking at**, so work down these questions in order:

1. **Does the mod already own something that expresses it?** A gene, a field, a
   value in the pool. If yes it is a **missing gene** — the def simply does not
   list it. Settle this by searching the shipped defs, not by memory: the Massassi
   entry could say the lifespan is expressible precisely because
   `RSW_lifespan_nine` and `RSW_lifespan_half` are declared in
   `src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml` and merely absent
   from that xenotype.
2. **Is it a two-tone, patterned or per-region appearance?** Then it is an
   **engine limit** — a single-channel tint mask cannot express it, and no colour
   value ever will. It needs art or more mask channels.
3. **Is it neck length, leg form, or overall body proportion?** Then it is a **rig
   limit and cannot be fixed at all.** The named cases are **Ithorian**
   (forward-curving neck), **Kaminoan** (proportion), **Muun** (long-legged narrow
   body) and **Lasat** (digitigrade legs). 🔴 **Stop. Retarget to the best
   achievable silhouette and say in the report that you did.** A pass spent
   chasing one of these produces nothing — that is the specific waste this section
   exists to prevent.

⚠️ **A `Def-versus-canon` list in an entry is a findings list, not a work order.**
It was written by an entry author under instructions to report and not fix. The
queue item you are working under decides whether the def may change — and §5
applies regardless.

---

## 4. An empty `## ruling` means canon stands unopposed

Measured 2026-09-16 across all 137 entries: **25 carry a ruling, 112 are empty.**
Empty is the normal state and the entry is fully usable — the owner rules only on
ambiguity, a deliberate departure from canon, or a contested regen
(`AGENT_BRIEF.md`, his ruling of 2026-09-15).

⛔ **Never block, defer or downgrade work because an entry is "unruled".** That
reading turns 112 complete briefs into blockers.

Where a ruling **does** exist:

- **It outranks the sourced canon and the visual brief**, including the library's
  own earlier read. `gizka` is the worked case: the owner rejected the entry's
  quadruped finding, the brief's line was superseded, and the entry now says
  bipedal.
- **It usually names a specific image FILENAME** as the reference of record, and
  often carries verbatim instructions ("Follow #3 closely", "Make it Olive
  colored"). Use the file it names, not your own pick from the directory.

⚠️ **Reading a drafted checklist to the owner line by line is how you find out
which items were never his intent.** One sitting reading a `## Must show`-style
checklist produced three rulings that DELETED art, including one that
dissolved a doc's own self-described hardest, precedent-less asset into an
asset already on the list. A line he cannot accept is usually a design claim
somebody invented and never actually tested against his intent — not a
sourcing error.

---

## 5. ⛔ Cosmetic changes need the owner's permission FIRST

The rule and its reason (they can break animated faces) are in `CLAUDE.md`. What
it means at the moment you are about to act:

| you are about to… | permission needed? |
|---|---|
| record a finding, limit or contradiction **in the entry** | no — recording is not fixing |
| add/remove/swap a head, eye, skin, hair or body gene | **yes** |
| change a `texPath`, or replace shipped art with a regen | **yes** |
| edit a non-cosmetic def field the entry flags (lifespan, aptitude, namer) | still gated by your queue item, not by this rule |

Raise it or file it per your window file (`infrastructure/agents/BENCH.md` /
`FOUNDRY.md`). Recording a limit is not the same as fixing it, and neither is
having found a good reason.

---

## 6. Is the entry still true about the def it grades?

Entries cite defNames and repo paths, and both move. Three checks, all offline:

- **The defName** — search `src/RimStarWars/` for the entry's `**defName**:`
  value. If it is gone, the entry is grading a def nobody ships, and a rename is
  the likely cause — renames to the tier grammar (`design/NAMING_SCHEME_PLAN.md`)
  are ordinary owed work, not gated on anything (`NAMING_SCHEME_EXECUTION_1`
  closed 2026-08-31).
- **The cited repo paths** — measured 2026-09-16, **0 of 137 entries cite a
  missing `src/…` or `design/…` path.** There is no background noise here, so one
  miss is a real, new break.
- **The local assets** — reference images live **in the entry directory**, and an
  entry naming a file that is not there is a real defect. `mirialan` cited
  `wookieepedia_mirialan_luminara_swm41.png` in three places while the disk held
  `wookieepedia_luminaraunduli_swm41.png`, and its Source-URLs line asserted the
  file was "already on disk under that name… re-verified this pass" — which was
  never true. Fixed at `252f8ff2e`.

🔴 **A prose claim that a file was verified is not verification. List the
directory.**

⚠️ **A naive filename check is noisy — confirm before reporting.** Entries
legitimately name upstream Wookieepedia `File:` titles, sibling sprites that live
under `design/Jawa/fauna/sprites/`, and another entry's asset by
cross-reference (`mon_calamari` points at a bad image held in `rakata/`). And
"there is **no** `donor_current_sprite.png`" is a correct negative statement about
missing repo art, not a dangling reference.

---

## What this skill deliberately does not carry

- **Writing or refreshing an entry** — format, sourcing discipline, the fetching
  route, the 2000px-image trap that kills a session, the write-incrementally rule:
  `canon_references/AGENT_BRIEF.md`. It is the operating doc; this file only says
  how to *consume* what it produces.
- **The owner's library-wide rulings** — the three defect classes, the cosmetic
  gate, what an empty ruling means: `CLAUDE.md > What is where`. Restated nowhere,
  pointed at from here.
- **Sprite craft** → `generating-rimworld-sprites`. **Genes, heads and why a
  species "has no art"** → `rimworld-xenotypes`. **Finding the art on disk** →
  `reading-rimworld-graphics`. **Deploying it** → `rimworld-deploy`.

⛔ **Do not upgrade an `## Engine limits` line into an engine fact.** Those lines
are entry authors' recorded findings, and some say so out loud — the
`useSkinShader: false` limit is annotated *"needs in-game confirmation of what
actually renders."* RimSage has never connected on the Laptop, so what the shader
or the renderer actually does **cannot be measured there at all**. Cite the limit
as the entry's finding, or answer UNMEASURED.

## Where it all lives

```
design/RimStarWars/canon_references/<slug>/description.md   the target
                                    <slug>/*.jpg|png        its reference images
                                    AGENT_BRIEF.md          how to write an entry
                                    DROIDS_INDEX.md         which droids are in scope
                                    RACES_TODO.md           the species roster
src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml
                                                            species defs — GENERATED, never edit
src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/            creature defs
src/RimStarWars/<Name>ArtOverride/Textures/                 our creature art overrides
```
