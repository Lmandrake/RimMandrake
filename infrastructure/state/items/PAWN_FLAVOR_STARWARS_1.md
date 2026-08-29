# PAWN_FLAVOR_STARWARS_1 — backstories, childhoods and traits, in-fiction

Owner, 2026-08-29 (verbatim): "assess and make star wars compliant all
backgrounds, childhoods, traits, etc. Make them robust, interesting, and star
wars themes where appropriate. Work with the user to define this richly."

## Why this is BENCH's, not FOUNDRY's
"Work with the user to define this richly" is a design pass, not a build —
this needs the owner's taste on which vanilla/donor-mod content stays generic
background noise versus which gets reworked into Star Wars fiction. Filed
`needs: owner` on purpose.

## Scope, as named by the owner
- **Backstories** — RimWorld's `BackstoryDef`s, split `slot: Childhood` and
  `slot: Adulthood`. These are what "backgrounds" and "childhoods" both mean
  in-engine; there is no separate "background" def type.
- **Traits** — `TraitDef`s and their degrees.
- **"etc."** — left open; the owner said "etc." Candidates worth raising with
  him rather than assuming: `MentalBreakDef` flavor text, `ThoughtDef` labels,
  and title/name-in-record flavor for xenotypes he's already themed. Do not
  expand scope on your own — ask which of these he means before touching them.

## What an assessment pass needs before any rework starts
1. **Census first**: how many backstories/traits are currently active across
   the full 578-mod list, and what fraction already read as
   generic-vanilla-Rimworld vs already Star-Wars-flavored (Jawa-authored ones,
   OuterRim's own, etc.) — this is a `measure`/def-dump job, not a guess.
2. **Read before rewrite**: `BackstoryDef` and `TraitDef` fields that carry
   flavor (`title`, `titleFemale`, `desc`, `spawnCategories`, `workDisables`,
   `skillGains`) versus fields that carry mechanism (skill gains, disabled
   work types, spawn category weight) — a "make it Star Wars" pass must not
   silently break the mechanism half while reskinning the flavor half.
3. **Precedent**: this project already has a "PURE Star Wars" ruling for the
   xenotype roster (`XENOTYPE_ROSTER_PURE_SW_1` — non-canon species cut, not
   reflavored). The owner may want the same standard here (rewrite everything
   to be in-fiction) or a lighter touch (only reflavor what's easy, leave
   mechanically-load-bearing vanilla content alone) — this is exactly the kind
   of call "robust, interesting, and star wars themes WHERE APPROPRIATE"
   leaves open, and is the first thing to nail down with him.

## Watch out
- A donor mod's backstories/traits can be **inherited or patched by other
  mods** (see [[inherited-list-items-cannot-be-patched-away]] and
  [[patched-collisions-need-the-capture]] pattern from prior censuses) — a
  rework here needs the CURRENT joined view (dump + patches), not raw XML from
  one mod folder, or it will silently miss what another mod already changed.
- `spawnCategories` on a backstory decides which pawn-generation pools draw
  it; reflavoring the text is safe, but touching this field changes WHO can
  get the backstory and needs the same rigor as the pawnkind/tag work in
  `rimworld-content-moderation`.
- This is real content-authoring scope (potentially hundreds of defs) — expect
  it to be its own multi-session arc, not a single BENCH sitting. Consider
  whether it wants a `retarget` to v2 once the shape of "how much" is known,
  or stays v1 if the owner wants it done before he plays.

No `## spec`/`## verify`/`## criteria` yet, deliberately — those come out of
the BENCH conversation with the owner, not before it.
