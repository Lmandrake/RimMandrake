## spec
Standing owner instruction: "always have at least one background sub agent
working on art regeneration." Waves 1-3 exhausted the `art: "redo"` pool in
`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`
(`ART_REGEN_WAVE3_QUEUE_1` found zero eligible `redo` rows left). Owner ruling
2026-09-11 authorized drawing wave 4 from the 338 `art: "improve"` rows
instead, and added binding semantics for that bucket (`infrastructure/artpipe/
README.md`, "'improve' semantics" section, right after "redo" semantics):
full regen (same mechanism as redo), Star Wars-named creatures keep their
canon identity, non-SW names are free to be reimagined (general kind fixed,
specific name/character not), and every prompt must explicitly ask for heavy
black outlines that read clean at standard zoom and below.

Of the 338 `art: "improve"` rows (178 `decision: "in"`, 105 `move`, 55
`out`), this wave drew only from the 178 `in` rows with a real biome
assignment (`fauna:<biome>:Name` keys) — the `homeless:*` rows in the same
`in` bucket carry unresolved reserve/injectable/faction/trader dispositions
from the 2026-09-10 sitting and were left alone as a design-call bucket, same
carve-out logic as prior waves' `move`/`out` exclusions. Excluded by name:
everything already in `infrastructure/artpipe/done/`, `failed/`, `active/` or
`pending/` before this wave filed — notably `AA_Lockjaw`/`AA_Mantrap` (both
also tagged `art: improve`, already mid-iteration from an earlier pass) and
every wave 1-3 `redo` creature (`AA_Frostmite`, `AA_ShadowCharger`,
`AA_Thunderox`, `Dragonsnake`, `Fambaa`, `GR_Spidercat`, `Horax`,
`Insectomorph`, `Kreetle`, `VAEWaste_Megatardi`, `Zakkeg`).

**7 creatures picked (batch size, mixing both halves of the ruling)**:

SW-canon, identity KEPT (converged on canonical look):
- `Ronto` (desert, large) — the classic Jawa pack beast: elephantine,
  four-legged, trunked, wrinkled grey-brown hide.
- `Anooba` (arid_shrubland, medium) — the Jawa hunting/guard beast: lean,
  hyena-like, tawny mottled fur.
- `Dewback` (weeping_stones, large) — the Tatooine reptilian mount: thick
  grey-green scaly hide, blunt-snouted, stumpy-legged.

Non-SW names, REIMAGINED (general kind kept, name/character invented):
- `GR_ParagonRat` (wasteland, small, note "This creature steals") → invented
  **Grithe**: a chitin-plated insectoid-rodent scavenger with oversized
  grasping forepaws, not a literal rat.
- `BMT_Maligoat` (wasteland, medium) → invented **Kroffa**: a six-legged
  plated desert grazer with curling horns and mandible-like mouthparts, not
  a literal goat.
- `GR_Molebear` (wasteland, medium) → invented **Grutt**: a tusked,
  armor-plated burrower with oversized digging claws and blind vestigial
  eyes, not a literal mole-bear.
- `BMT_FleeceSpider` (wasteland, small, note "0.6 cells") → invented
  **Puffmite**: a filament-tufted, crystalline/bioluminescent tiny arachnid,
  not a literal fleece spider.

Each job's `style_notes` records which half of the ruling applied and why.
Every prompt explicitly requests "heavy, clean black outline around the
whole silhouette and all major internal linework, thick enough to read
clearly at standard RimWorld zoom and below" per the outline requirement.

21 jobs filed (7 creatures x 3 facings south/east/north, 512x512 transparent,
codex channel, reference: null — full regen, same shape as wave 1-3) via
`fill_queue.py --input Transient/art_regen_wave4_improve.json --channel
codex`, dry-run first then for real. `pgrep -f artpiped.py` confirmed the
daemon already running; within ~60s of filing, `active/` held 3 claimed jobs
and `pending/` had dropped from 21 to 18 — confirmed consuming, not just
sitting.

## verify
Each of the 7 creatures' 3 facings lands in `infrastructure/artpipe/done/`
with `worker_status: ok`. Wiring into a mod's `Textures/` tree is a separate
step this item does not do (same pattern as prior waves).

## criteria
21/21 jobs complete (done or a clean, explained failed), daemon left running
so it keeps draining the queue unattended. Queueing itself — not the art
finishing — is what closes this item.
