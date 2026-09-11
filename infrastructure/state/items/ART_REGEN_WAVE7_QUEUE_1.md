## spec
Standing owner instruction: "always have at least one background sub agent
working on art regeneration." Continuation of `ART_REGEN_WAVE4_QUEUE_1` /
`ART_REGEN_WAVE5_QUEUE_1` / `ART_REGEN_WAVE6_QUEUE_1`, same source pool:
`art: "improve"` rows in `design/Jawa/worldbuilding/review/round2/
decisions_propagated.json`, same binding semantics (`infrastructure/artpipe/
README.md`, "'improve' semantics" section): full regen (same mechanism as
`redo`), Star Wars-named creatures keep canon identity, non-SW names are
free to be reimagined (general kind fixed, specific name/character not),
every prompt explicitly asks for heavy black outlines. Same as wave 6, every
candidate was checked directly against `design/RimStarWars/
star_wars_canon_names.md`'s Creatures/Species section rather than guessed by
vibes.

Of the 338 `art: "improve"` rows, restricted to `decision: "in"` rows with a
real biome assignment (`fauna:<biome>:Name` keys, excluding `homeless:*`
design-call rows — same carve-out as waves 4-6), minus every name already
spoken for by wave 1-6's picks (both original and invented names) and
`AA_Lockjaw`/`AA_Mantrap`'s mid-iteration attempts: **28 eligible candidates**
remained (deduplicated by name across biomes) — consistent with wave 6's own
count of 35 remaining before it picked 7 (35 − 7 = 28).

**7 creatures picked (batch size, mixing both halves of the ruling, same
3-kept/4-reimagined ratio as waves 4-6)**:

SW-canon, identity KEPT — confirmed present as solid (non-UNCERTAIN) entries
in `star_wars_canon_names.md`'s master-bestiary list:
- `Whisperbird` (four biomes: arid_shrubland/the_fever_wood/the_greentide/
  the_miasma, medium; the_greentide picked as representative) — confirmed
  [B], no individual Wookieepedia writeup exists yet, so the silent-flying
  avian-predator kind was drawn from the name itself and the row's own size
  context, same treatment wave 6 gave `Ollopom`.
- `Hawk-bat` / row name `Hawkbat` (the_greentide, medium) — confirmed [B]
  AND individually recognizable as a real screen-canon species (Star Wars
  Rebels, Kashyyyk/Onderon): leathery-winged, red-eyed, shrieking nocturnal
  ambush flyer. Drawn to that established look.
- `Peko-peko` / row name `PekoPeko` (the_greentide, large) — confirmed [B]
  AND individually recognizable as a real screen-canon species (Star Wars
  Rebels): a large flightless draft/mount bird. Drawn to that established
  look.

Non-SW names, REIMAGINED (general kind kept, name/character invented) —
checked against the doc and found nowhere in it (all donor-mod prefixed
names: Alpha Animals, BiomesTeam, a "GR_"-prefixed pack):
- `AA_MycoidColossus` (the_rot, titan, note "Biggest. 10 squares.") →
  invented **Mycolith**: a colossal composite-fungus titan with a bloated
  trunk-like body and spore-nodule skin, not a literal mushroom monster.
- `AA_RaptorShrimp` (the_miasma, large) → invented **Fenshear**: a
  raptor-postured crustacean ambush predator with oversized shearing claws,
  not a literal shrimp.
- `BMT_BovineBeetle` (the_rot, large) → invented **Grubhorn**: an armored
  beetle-carapaced grazer with curling ridged horns, not a literal cow.
- `GR_Mantistanis` (the_pyrelands, large) → invented **Emberscythe**: a
  fire-adapted mantis-like ambush predator with glowing scythe-forelimbs,
  not a literal insect.

Each job's `style_notes` records which half of the ruling applied, cites the
canon-doc check explicitly (found/not-found, with provenance code where
found), and — for the reimagined four — the donor prefix that ruled them
out. Every prompt explicitly requests "heavy, clean black outline around the
whole silhouette and all major internal linework, thick enough to read
clearly at standard RimWorld zoom and below" per the outline requirement.

21 jobs filed (7 creatures x 3 facings south/east/north, 512x512
transparent, codex channel, reference: null — full regen, same shape as
waves 1-6) via `fill_queue.py --input Transient/art_regen_wave7_improve.json
--channel codex`, dry-run first (0 duplicates/errors) then for real.
`pgrep -f artpiped.py` confirmed the daemon already running (PID 699477).
Within the ~60-90s window, `active/` picked up 3 claimed jobs
(`emberscythe_v1_*`) and `pending/` dropped from 21 to 18 — confirmed
consuming, not just sitting.

## verify
Each of the 7 creatures' 3 facings lands in `infrastructure/artpipe/done/`
with `worker_status: ok`. Wiring into a mod's `Textures/` tree is a separate
step this item does not do (same pattern as prior waves).

## criteria
21/21 jobs complete (done or a clean, explained failed), daemon left running
so it keeps draining the queue unattended. Queueing itself — not the art
finishing — is what closes this item.
