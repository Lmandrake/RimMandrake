# IRIAZ_ART_REGEN_1 Iriaz art regeneration

state:    doing
row:      unassigned
needs:    offline
target:   v1
kind:     task
owner-said: "Iriaz seems like it needs regeneration"

## spec

Owner filed this 2026-09-14 off a general "seems like it needs
regeneration" impression, with no specific complaint. A prior pass
(PYRELANDS_CREATURE_RERENDER_1, 2026-09-16) already delivered painterly v2
regen art for Iriaz — 3 facings at
`Transient/pyrelands_full_review_2026-09-16/facings/pyrelands_iriaz_v2_{north,south,east}.png`
— identity drawn from `design/RimStarWars/canon_references/iriaz/description.md`
(Dantooine grassland herbivore: long-necked antelope/giraffe-proportioned
quadruped, muted olive-teal hide, leopard-style orange-yellow spotted
markings, ONE long ridged backward-curving horn, thin whip-like tail, no
visible fur). That art was already wired into
`src/RimStarWars/IriazArtOverride/Textures/swanimals/Iriaz/` at commit
`de46f98c1` (2026-09-17, before this item was picked back up) — confirmed
byte-identical to the Transient source (matching md5 on all 3 facings).

**Canon identity question, checked and resolved.** A different agent's
unrelated art-queue search flagged tonight: "iriaz -> unresolved canon
identity conflict (four-legged Dantooine antelope vs. two-legged Dathomir
render used so far) -- genuinely needs an owner ruling first." Checked this
directly:
- `design/RimStarWars/canon_references/iriaz/description.md` describes only
  ONE identity: a four-legged Dantooine grassland quadruped. There is no
  "Dathomir" or two-legged variant anywhere in that doc, nor in
  `design/Jawa/worldbuilding/starwars_iconic_creatures.md` (which has no
  Iriaz entry at all -- Iriaz was historically "UNGATED" there per commit
  `f209d892c`'s message, before the dedicated canon-library entry existed).
  A repo-wide grep found no file pairing "Iriaz" with "Dathomir". The flag
  does not correspond to anything in this repo and appears to be either
  stale (from before the 2026-09-13 canon doc existed) or a mix-up with an
  unrelated creature.
- The canon doc's own `## ruling` section is empty, but per this repo's own
  canon-library convention (CLAUDE.md: "An empty ## ruling means canon
  stands unopposed, not that the entry is unusable"), that alone would be
  enough to proceed.
- More decisively: the owner has ALREADY ruled on this exact art, in the
  ledger, after the canon doc was written. `PYRELANDS_CREATURE_RERENDER_1`
  note (2026-09-16) flagged the v2 render as FAILING Must-show because it
  looked like it drew a second horn. The owner reviewed it and corrected
  that read (ledger 2026-09-17, commit `de46f98c1`): *"the 'second horn' is
  an ear (owner correction)"*. A later ledger note (`ownerSaid: "Lock in
  that Iriaz."`) reads: *"IRIAZ LOCKED 2026-09-17: iriaz v2 set is final
  (ear confirmed, not a second horn). No further iriaz versions."* This is
  a direct owner sign-off on the specific v2 art already wired, confirming
  it matches every Must-show line (one horn, not two) and settling the
  identity question completely -- there is no remaining ambiguity to guess
  at.

**What was actually still broken (not art content, wiring):** SWBestiary
(`mandrake.rsw.swbestiary`, the mod that ports/vendors `RSW_Iriaz`) bundles
its OWN donor-vintage Iriaz art at the exact same relative texPath
(`swanimals/Iriaz/Iriaz_{north,south,east}.png`, confirmed different md5
than the v2 art) as `IriazArtOverride`. `IriazArtOverride/About/About.xml`
declared `loadAfter Mlie.StarWarsAnimalCollection` but NOT
`mandrake.rsw.swbestiary` -- the exact same same-path load-order collision
class found and fixed for Nuna tonight (`NUNA_ART_REGEN_1`, commit
`206d6aec8`). Checked the current full-modlist snapshot
(`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`, 635 mods):
`mandrake.rsw.iriazartoverride` sits at index 311, `mandrake.rsw.swbestiary`
at index 558 -- SWBestiary loads LATER and would have won the same-path
resolution, silently reverting Iriaz to the old donor-vintage art on any
load using that order. `IriazArtOverride` was also missing its `LICENSE`
file (present on every sibling *ArtOverride mod, byte-identical CC0 1.0
text, md5 `eb125555b32e9c63388382e9ea9045a7`).

**Fix applied:**
1. Added `<li>mandrake.rsw.swbestiary</li>` to `IriazArtOverride`'s
   `loadAfter`, with an explanatory paragraph matching Nuna's, so SWBestiary
   can no longer win the same-path collision regardless of mod order.
2. Added the missing `LICENSE` file (copied from `NunaArtOverride`, verified
   byte-identical to the family convention).
3. `validate_patch.py src/RimStarWars/IriazArtOverride`: 0 errors, 0
   warnings.
4. Deployed via `deploy_custom_mods.py --mod IriazArtOverride --apply`:
   `+ LICENSE`, `~ About/About.xml`, verified in sync.

Note: `mandrake.rsw.iriazartoverride` is currently ABSENT from the LIVE
`ModsConfig.xml` (30-mod minimal test list active right now, not the full
635-mod list) -- this is expected under the minimal-modlist regime, not a
defect; it is present in the full-list snapshot at the index checked above.

## verify

- `validate_patch.py`: OK, 0 errors, 0 warnings (static only; no `--defs`
  pass needed, this mod touches no Defs/Patches).
- Deploy: `deploy_custom_mods.py --mod IriazArtOverride` plan-then-apply,
  both files verified in sync after apply.
- Load-order collision: confirmed real (not hypothetical) via
  `ModsConfig.FULL.LATEST.xml` index comparison (311 vs 558); confirmed
  fixed by the added `loadAfter` entry, matching the exact pattern and
  wording already proven correct by `NUNA_ART_REGEN_1`.
- Canon identity: resolved by direct owner ruling recorded in the ledger
  (`ownerSaid: "Lock in that Iriaz."`, 2026-09-17) on the specific v2 art
  already wired here -- not inferred, not guessed.
- NOT live-verified in this pass: no bridge/restart was used (per FOUNDRY
  belt-mode scope, this stayed fully offline); the next natural full-list
  restart should confirm Iriaz renders the v2 art in-world with the fix
  applied. This is the same "not yet live-verified" caveat Nuna's fix
  carried and is not a reason to hold the item -- the wiring, validation
  and collision fix are all independently confirmed offline.
