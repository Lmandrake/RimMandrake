# LIVESTOCK_STARTER_TRIO_1 — onnik + karrask + moornak, shared-art batch

Green-lit from `design/Jawa/proposals/ludicrous_livestock_deep_design.md`
(owner, 2026-09-01). The doc's own v1 is the PAIR (onnik + karrask — zero new
job types, shared art base); the owner asked for a trio, so moornak rides as
the third IF it needs no new job type (its comp is passive) — drop to the pair
rather than invent a job. Everything else in the doc waits for
PROPOSAL_SUITE_REVIEW_1.

## spec

Per the doc's rosters and §7.2 shared-art batching:
1. **Onnik (kiln-belly)**: feed-cycle industrial — fed clay/raw ceramic input,
   fires it in its gut, yields ceramic product on a cycle; chokes or fires
   cold when mis-fed (the doc's mis-feed failure states). Extends the proven
   urrak/vokka single-input template. Its fired ceramic is the cuisine doc's
   sand-oven cookware — keep the product def name generic enough to share.
2. **Karrask (molt-plate)**: harvest-on-schedule — sheds carapace plates on a
   molt cycle; plates are an armor/crafting material. Standard shear-like
   harvest job, no new job code.
3. **Moornak (grief-eater)**: passive aura comp — visibly eases mourning
   (mood buff to grieving pawns in radius) while SECRETLY storing every
   debuff absorbed; on death, releases the entire backlog onto the colony.
   The hidden ledger is scribed (survives save/load). No new job type.
   ⚠️ The secret must be genuinely invisible in the inspect pane — the dread
   is the design; a visible counter kills it.
4. All three: role-band sizes per the doc, tameable, tradeable, RimStarWars
   tier; sprites via `generating-rimworld-sprites` contract (128 px/cell,
   chroma-key alpha, silhouette-first), beast-normalization spirit (born
   normalized, no retrofit).

## owner art rulings (2026-09-01)

Onnik = option 2 · karrask = option 2 · moornak = option 3. Kept files and the
full table: `src/RimStarWars/Livestock/art/mockups/PICKS.md`. Three rejects were
PROMOTED, not dropped: karrask opt 3 → its own new creature; moornak opts 1+2 →
"other crag creatures" (owner's term, family undefined) — each needs a design row
before any build; none belongs to this item.

## verify

Quicktest: spawn/tame each; (a) onnik full feed→fire→product cycle plus one
mis-feed failure observed; (b) karrask molt yields on schedule and the plate
is craftable-with; (c) moornak buffs a grieving pawn, then its death releases
the stored backlog (dev-kill after accumulation; MEASURED debuff count in =
count out); (d) save/load round-trip keeps moornak's hidden ledger; (e) art
passes the offline validator per facing before any game load.

## criteria

Three creatures live in a quicktest with full cycles observed; zero new job
types shipped; shared-art batch discipline held (one body base reused);
Player.log clean.

## Watch out

- Animal product comps: `CompHasGatherableBodyResource` covers karrask;
  onnik's feed-specific input needs a custom comp — keep it one comp, data-
  tuned, so drassik (v2) reuses it.
- Moornak's death-release must fire on ANY death path (slaughter, violence,
  age) — hook the death notify, not the slaughter job.
- Trainability/wildness numbers decide tameability at spawn — the census
  trap: a spawned "tame" test animal may substitute silently; verify the
  actual kind spawned (see census memory).

## 2026-09-02 — scoping pass, nothing written (FOUNDRY, background fanout)

0% built: no ThingDefs/PawnKindDefs/sprites for onnik/karrask/moornak exist
anywhere in the repo, only design-doc rosters and owner-picked mockup PNGs.
`src/RimStarWars/Livestock/` (`mandrake.rsw.livestock`) is currently
entirely occupied by the sibling item `FORSAKEN_CRAGS_PREDATORS_BUILD_1`'s
content (Cindermare/Skarnix) — no defName collision found (grepped for
Onnik/Karrask/Moornak across `src`, empty), but this item and
`FORSAKEN_CRAGS_PREDATORS_BUILD_1`/`HELIX_TELLUROX_BUILD_1` would share one
mod package, which needs a naming/ownership call rather than a guess.

Also: the design doc's own spec claims onnik "extends the proven
urrak/vokka single-input template" — checked, urrak/vokka have zero
implementation anywhere in `src`. Onnik's feed-cycle/cold-fire-failure
mechanic needs a genuinely new custom `ThingComp`, not a reuse; not the
small increment the spec's own framing suggested.

**Two open questions, needs owner/BENCH before building moornak:**
1. This item's own spec text (simple mood-buff + hidden ledger +
   release-on-death) doesn't match a materially richer, LATER owner ruling
   in the design doc's "RULED — owner sitting" table (same date,
   2026-09-02): self-tames readily, arrives pre-loaded with grief, a
   negative colony-wide "unsettled" hediff, 30-day release duration,
   triggers manhunter on release, sells but never buys back, must be
   trapped/abandoned. Unclear whether the later ruling supersedes this
   item's spec or belongs to a still-deferred review pass.
2. Shared-mod-folder ownership with `FORSAKEN_CRAGS_PREDATORS_BUILD_1` (see
   above) — needs a naming decision before any file gets written into that
   directory.

Smallest safe next increment once unblocked: karrask alone, XML-only
(`CompHasGatherableBodyResource` for the molt-plate harvest per the owner's
2026-09-02 ruling — "tough material like chitin, easy to work, not pretty,"
NOT wearable armor), additive-only filenames, ~1 hour. Onnik's comp is a
separate half-day pass. Final sprite art stays deferred per the doc's own
palette-pass sequence.

## 2026-09-02 — karrask built (concurrent collision), onnik/moornak still 0/3

**Karrask is now structurally built** (`Defs/ThingDefs_Animals/ThingDefs_Karrask.xml`,
`Defs/PawnKindDefs/PawnKindDefs_Karrask.xml`, `Defs/RecipeDefs/RecipeDefs_Karrask.xml`
— all currently untracked, not yet committed by whoever wrote them): natural
armor via ArmorRating stats, a `WorkToMake` stuff-property factor for
"easy to work," a Crafting-gated cure recipe at tailoring benches.
`validate_patch.py` clean except 6 expected `texPath` errors (no production
sprite yet, only the owner-picked mockup). ⚠️ **A FOUNDRY-dispatched agent
independently building the same karrask defs collided with whoever wrote
the files above** — two workers targeted this item's same files at the same
time; the agent's own content was overwritten mid-pass and it correctly did
not revert the surviving (more complete) version, only removed one
now-orphaned file of its own that would have duplicate-defName-collided
(`ThingDefs_Items/ThingDefs_KarraskMaterials.xml`, never committed, no repo
history to worry about).

**Onnik's next increment, scoped**: a new custom `ThingComp` for the
3-dose kiln-cycle feed mechanic (spaced doses over a day, cools/resets if
underfed >1 day, mis-feed produces cracked/worthless ceramic) — one new
comp, no new job type, follow this mod's existing comp-authoring pattern
(`CompLightAversion.cs`). Medium build, roughly comparable in size to
karrask's own pass.

**Moornak stays blocked** on the same scope question raised above (this
item's spec vs. the design doc's later, materially richer owner ruling) —
not re-litigated here, still needs a call before anyone writes code for it.
