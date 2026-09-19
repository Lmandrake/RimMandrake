# RAZORJACK_IDENTITY_RESTYLE_1

Owner filing, 2026-09-14 (`infrastructure/state/ledger/events.jsonl:8474`),
verbatim: "Our razorjack looks strange to me. like a lava beast. It should
not. It should look semi-camoulflaged with the tall grasses, like a predator
might. Underside can be red, but above should be the same yellow-gold as the
grasses. Needs regenerated description into our own modspace and a new Star
Wars-esque name generated."

## spec

Subject: `AA_Razorjack` (ThingDef + PawnKindDef), a donor def owned by the
Alpha Animals mod (`sarg.alphaanimals`), cast into the Pyrelands biome roster
(`PYRELANDS_FIRE_WEB_COMMISSION_1`). Not a Star Wars canon species — no
`design/RimStarWars/canon_references/` entry exists or is owed; this is a
generic donor creature, so the SW-flavoured name is our own invention with
no canon to check against.

Three sub-tasks, all closed by this pass:

1. **Art** — restyle to grass-camo (yellow-gold above matching tall grass,
   red underside), remove the lava/ember read entirely.
2. **Description** — new text in our own modspace/voice, not the donor's.
3. **Name** — new Star Wars-esque species name.

### What was already done before this pass (found on claim)

A prior FOUNDRY session (2026-09-14 to 2026-09-16) had already done nearly
all of this work and committed it:

- **Name**: owner picked **"Sytheclaw"** from a BENCH card the same day the
  item was filed (ledger note `RAZORJACK_IDENTITY_RESTYLE_1`, 2026-09-14).
- **Description + label**: `src/RimUtinni/UtinniPatches/Patches/RazorjackIdentity_Sytheclaw.xml`,
  a `PatchOperationFindMod`/`PatchOperationSequence` against the Alpha
  Animals ThingDef/PawnKindDef, replacing `label` → `sytheclaw` and
  `description` with an original-voice text ("A low-slung pack predator
  built for the tall gold grass of the burning plains...") matching the
  tone/length of sibling identity patches (checked against
  `FlamefangIdentity.xml`'s Boomsnake description: similar structure —
  habitat/behaviour sentence, hunting-method sentence, signature-trait
  closer).
- **Art**: `src/RimUtinni/RazorjackArtOverride/` — a label/art-only override
  mod (packageId `mandrake.rut.razorjackartoverride`, `loadAfter
  sarg.alphaanimals`) shipping three facing textures at the donor's exact
  texPath (`Things/Pawn/Animal/AA_Razorjack/AA_Razorjack_{north,east,south}.png`,
  512×512, so same-path load-order resolution wins over the donor art with
  no defName/Def/Patch changes). Rendered and wired in commits `3a255e2bb`
  → `08b53e328` → `9e7e773a0` → `c51c341ba`. The dessicated-corpse texture
  (`AA_Dessicated_Razorjack`) intentionally stays on donor art (not part of
  the owner's complaint).
- **Owner re-confirmed the art stands**: 2026-09-17 ruling on a separate
  south-facing top-down regen sweep (`PYRELANDS_SOUTH_TOPDOWN_REGEN_1`)
  explicitly kept "Razorjack and Barbslinger high-angle fronts... as wired" —
  i.e. he has already looked at this exact art post-restyle and approved it
  a second time.

### What this pass did

1. **Verified the art visually** (read all three PNGs as images): north,
   east, south all show a low-slung quadruped predator, plates dry
   yellow-gold matching tall-grass tone, underside/inner legs raw red, no
   ember/lava/heat colouring anywhere. Matches the owner's brief exactly.
2. **Verified technical validity**: all three PNGs open in PIL, RGBA,
   512×512, non-zero size (north 216772 B, east 136414 B, south 267881 B).
3. **`validate_patch.py` clean** on `RazorjackIdentity_Sytheclaw.xml`
   (0 errors, 0 warnings; no `--defs` available offline so xpath hit-counts
   weren't re-executed, but the xpath shape was already static-checked
   before commit).
4. **`code_review_status.py check`**: the About.xml and all three PNGs are
   already `CLEAN` (wave 40, `38ce6b1fa`, 2026-09-17). Only the identity
   patch XML was `DIRTY` (never reviewed) — see `## verify`.
5. **Corrected a stale/wrong reasoning line** in
   `RazorjackIdentity_Sytheclaw.xml`'s header comment. It read: "defName
   stays AA_Razorjack until NAMING_SCHEME_EXECUTION_1" — but that item
   closed 2026-08-31 (`54a8e28d`, "Deploy the full rename"), *before* this
   comment was written (2026-09-14/16), so it cited an already-closed gate
   as a reason to defer, which CLAUDE.md flags by name as the exact
   anti-pattern to delete on sight. Replaced with the actual, correct
   reasoning: `AA_Razorjack` is a donor-owned ThingDef/PawnKindDef living in
   the Alpha Animals mod, never absorbed into our own `src/` tree, so it
   isn't "ours" to rename under the three-tier scheme
   (`NAMING_SCHEME_PLAN.md` §1 governs our own shipping identity; a donor
   def only gets a new defName via a full vendored-absorption with a
   documented old→new map, like Armoury's ~1,470 defs — not attempted here
   and not warranted for one creature).
6. **Decided against renaming the defName** (the brief's "rename if
   appropriate"). Reasoning: `AA_Razorjack` is referenced by defName in at
   least seven other live files outside this item's scope
   (`AnimalTolerances_Ashkarr.xml`, `AnimalBiomeDuplicates_Generated.xml`,
   `BiomeCastEvictions_WildBiomes.xml`, `BiomeCast_Ashkarr.xml`,
   `WildAnimals_Pyrelands.xml`, `RUT_Contagion.xml`, `RUT_Greentide.xml`),
   plus the donor mod's own internal references and any existing save data.
   Renaming it would require a full absorption pipeline (copy the def into
   our own mod under a new defName, retire the donor def, remap every
   reference with a documented old→new table — the same discipline as the
   MLIE fauna-absorption work) which is a materially bigger, separate piece
   of work than "restyle art + reword description + pick a name." The
   player-facing identity (label, description, name) is fully ours already
   via the patch; the internal defName is plumbing nobody sees. Not
   appropriate to fold into this item silently — flagging here instead of
   guessing.

## verify

- `python3 skills/rimworld-modding/scripts/validate_patch.py
  src/RimUtinni/UtinniPatches/Patches/RazorjackIdentity_Sytheclaw.xml` →
  `OK - 0 errors, 0 warning(s)`.
- All three override PNGs opened cleanly via PIL: RGBA, 512×512, non-zero
  byte counts (confirmed above).
- Visual check (Read tool, all three facings) against the owner's brief:
  yellow-gold above / red underside / no lava-beast read — pass.
- `code_review_status.py mark-clean` run this pass on
  `src/RimUtinni/UtinniPatches/Patches/RazorjackIdentity_Sytheclaw.xml`
  after the comment-only correction and commit (full-file review, zero
  significant findings beyond the stale-gate line already fixed).
- No live/bridge check taken — bridge not free, and the owner has already
  visually re-approved this exact art in-session twice (2026-09-16 wave
  review, 2026-09-17 south-facing ruling), so a third look isn't owed by
  this pass.
