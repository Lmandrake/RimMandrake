## spec
Standing owner instruction: "always have at least one background sub agent
working on art regeneration." Continuation of `ART_REGEN_WAVE4_QUEUE_1`, same
source pool: `art: "improve"` rows in `design/Jawa/worldbuilding/review/
round2/decisions_propagated.json`, same binding semantics
(`infrastructure/artpipe/README.md`, "'improve' semantics" section): full
regen (same mechanism as `redo`), Star Wars-named creatures keep canon
identity, non-SW names are free to be reimagined (general kind fixed,
specific name/character not), every prompt explicitly asks for heavy black
outlines.

Of the 338 `art: "improve"` rows, restricted to `decision: "in"` rows with a
real biome assignment (`fauna:<biome>:Name` keys, excluding `homeless:*`
design-call rows — same carve-out as wave 4), minus every name already
spoken for in `infrastructure/artpipe/done/` or `failed/` (all of wave 1-4's
`redo`/`improve` creatures, the `AA_Lockjaw`/`AA_Mantrap` mid-iteration
attempts, and internal test jobs like `bgtest_*`): **51 eligible candidates**
remained (deduplicated by name across biomes — several names, e.g.
`Whisperbird`, `Jamel`, `Grank`, `Shiro`, appear under more than one biome
key for the same creature).

**7 creatures picked (batch size, mixing both halves of the ruling, same
3-kept/4-reimagined ratio as wave 4)**:

SW-canon, identity KEPT (converged on canonical look):
- `GreaterKraytDragon` (dune_sea + deep_desert, titan) — the legendary
  Tatooine desert titan: colossal armor-plated saurian, bony-crested head.
- `Vornskyr` (the_miasma, large) — the Kessel/Rebels predator: lean,
  spiny-ridged lizard-hound with needle teeth.
- `Orray` (the_pyrelands, medium) — the Geonosis arena/mount beast:
  six-legged, long-necked, birdlike-headed reptavian.

Non-SW names, REIMAGINED (general kind kept, name/character invented):
- `RSW_Yobshrimp` (the_miasma, medium) → invented **FeatherFeel** — a
  feather-fronded sensory filter-feeder, not a literal shrimp. The row's own
  note says "Rename to FeatherFeel" — an owner-mandated rename, not a
  discretionary one.
- `Jamel` (desert, large) → invented **Duskram** — a frilled,
  ceratopsian-headed desert grazer with dual fatty dorsal ridges, not a
  literal camel despite the source name's echo.
- `BMT_FoundryBeetle` (the_scarlands, large, note "very very slow mover,
  almost helpless") → invented **Slagmaw** — a rust-and-slag-plated grinder
  with heat-vent shell slits, not a literal beetle.
- `AA_Terramorph` (wasteland + the_scarlands) → name KEPT as-is, not
  renamed: the 2026-09-10 sitting ruling already gave it an established lore
  identity ("dayside lurker", wasteland+scarlands range), so the current
  name already earns its place per the improve ruling's own carve-out
  ("get inspired... invent... if the current one doesn't earn its place" —
  this one does). Only art quality/outline fixed; a terrain-camouflage crust
  look leans into the already-ruled character without implementing the
  terrain-matching color-change mechanic floated (but not ruled) in that
  sitting.

Each job's `style_notes` records which half of the ruling applied, and for
`AA_Terramorph` specifically records why the name was kept rather than
invented. Every prompt explicitly requests "heavy, clean black outline
around the whole silhouette and all major internal linework, thick enough
to read clearly at standard RimWorld zoom and below" per the outline
requirement.

21 jobs filed (7 creatures x 3 facings south/east/north, 512x512
transparent, codex channel, reference: null — full regen, same shape as
waves 1-4) via `fill_queue.py --input Transient/art_regen_wave5_improve.json
--channel codex`, dry-run first (0 duplicates/errors, confirming no name
collision with the wave 1-4 pool) then for real. `pgrep -f artpiped.py`
confirmed the daemon already running (from wave 4, still up); within ~60s of
filing, `active/` held 3 claimed jobs (`aa_terramorph_v1_*`) and `pending/`
had dropped from 21 to 18 — confirmed consuming, not just sitting.

## verify
Each of the 7 creatures' 3 facings lands in `infrastructure/artpipe/done/`
with `worker_status: ok`. Wiring into a mod's `Textures/` tree is a separate
step this item does not do (same pattern as prior waves).

## criteria
21/21 jobs complete (done or a clean, explained failed), daemon left running
so it keeps draining the queue unattended. Queueing itself — not the art
finishing — is what closes this item.
