# Speculative art commission — 2026-09-27

Owner directive, verbatim: "check for any art that hasn't yet been commissioned that
could be. The art pipeline is totally free and unblocked... take some liberties and
throw some potential candidates out for testing. Perhaps whole screen renders of
loading screens, or UI elements... anything that might help later. Take some risks and
have fun! Or perhaps some alternative creatures you flagged as potentially
problematic... we can afford to explore."

**19 jobs filed** into `infrastructure/artpipe/pending/` (facingless, single-render
`spec_`-prefixed jobs, painterly style per `ART_PAINTERLY_RESTORATION_1`). The daemon
(pid 614, confirmed the only instance running) had already claimed 3 into `active/`
within the minute. Tracked under a new ledger item, `SPECULATIVE_ART_COMMISSION_1`
(filed for BENCH, `needs: offline`), so this batch has a provenance anchor separate
from any production wave.

## Survey

Checked before queuing anything, in this order:

1. **`fill_queue.py --help` + source, `AGENTS.md`, `README.md`** — learned the job
   schema, the painterly style law, the facing/derive-facings mechanism (facingless =
   omit `facings` entirely, no suffix), the real canvas ceiling
   (`common.CANVAS_CEILING_PX = 1024`, not the drawSize-derived rule of thumb, which is
   advisory only), and the channel rule (Codex only).
2. **`design/Jawa/worldbuilding/`** (~140 files) for authentic imagery: `the_one_map.md`
   (the Scald's perched-crater-lake mechanism, the Rust Cathedral, the one-unsetting-sun
   fact), `the_seas.md` (shore-rite, wreck salvage, Twilight Deep skylights), `the_seas`
   family docs under `biomes/the_twilight_deep*.md`, `landmark_art_direction.md` (Ancient
   Launch Site, Cliffs/strata vocabulary for the Fall Line), `fall_line_major_region_label.md`,
   `ui_appearance_spec.md` and `ui_shell_spec.md` (UI shell state — see below).
3. **`infrastructure/artpipe/registry.jsonl`** (8,074 lines) — grepped every candidate
   subject before writing its job. This caught real duplicates (below) and confirmed
   every subject I did queue has **zero prior registry hits**.
4. **`Transient/*.decisions.json`** (16 review sheets) — read every non-"keep" verdict
   looking for "improve"/"replace"/"regen" rows that never got re-queued.
5. **`design/RimStarWars/canon_references/`** — none of the candidates I ended up
   queuing are true Star Wars canon subjects (the deep-cave/Rot fauna are invented
   RSW-tier names, and AA_Atispec is an Alpha Animals donor creature, not canon), so no
   rig-limit exclusion applied this round.

### What I found already done (and did NOT re-queue)

- **The entire "Deeps fauna regen" wave is already fully commissioned and generated.**
  `deeps_flora_fauna_review_2026-09-18.decisions.json`'s 8 "regen" verdicts (BloodropMoth
  → Drinker, BovineBeetle → Grabber, FacetMothLarvae → Soulchime, GlowSlug → Glowbulb,
  ShatterjawBeetle → Shatterjaw, Gembug, Megapleura, MossBeetleLarvae) all show
  `registered`/`queued`/`generated` events under `DEEPS_FAUNA_VERDICTS_1` — the renamed
  creatures gave a false "not found" on my first grep by old name.
- **The entire "Rot flora regen" wave is already fully commissioned.** All 9 spot-checked
  names from `rot_flora_fauna_review_2026-09-18.decisions.json` (giant agarilux,
  bleeding tooth, witches oyster, etc.) have 6–16 registry hits each.
- **`GREATBOLE_BARK_EDGE_ART_1`** — the exact defect named in this task's own brief
  ("`RUT_GreatboleCore` currently renders a retinted vanilla DeepDrill") — is **closed
  and shipped** (`6d0dbf802`, 2026-09-25): marker fixed to draw nothing, real bark/heartwood
  atlas art generated (via a Nano Banana Pro fallback since Codex was down that day) and
  wired with `linkType CornerFiller`. Nothing to queue here.
- **`KORRUM_ART_REGEN_1`** and the Stoneback/Bokka art standard are both closed with
  passing generated art (`RSW_Stoneback_{north,south,east}` all verdict `pass`).
- **Ash'karr orbital planet art already exists**: `design/Jawa/art/planet_ashkarr_{establishing,nightside,substellar,terminator_grey,terminator_twilight}.png`. I did not
  re-queue an orbital/globe shot; the nightside job I did queue is a distinct
  ground-level companion piece.
- **The UI shell (menu background, loader, button chrome) is already built and
  SHIPPED in a different, LOCKED direction than this task's painterly style law.**
  `ui_shell_spec.md` documents a 2026-09-05 owner pivot away from painterly/rust toward
  a procedural "ancient ship helm" look (grey-green gunmetal, vector-line schematic,
  amber/cyan) — *"I love love love the tech panel you made. Rusty buttons are out"* —
  built as a deterministic PIL 9-slice asset (`D_helm` in `gen_textures.py`), not an
  artpipe/Codex render, and a 9-slice button atlas has exact corner-tiling requirements
  a raw AI render doesn't meet anyway. **I deliberately did not queue any button/tab/
  gizmo/title-wordmark jobs** — that direction is already decided, shipped, and outside
  this pipeline's mechanism entirely; queuing rust-painterly UI chrome would directly
  contradict a locked owner ruling.
- **`AA_Behemoth`** (2026-09-06 review) was "approve", not a candidate. **Capybara**
  ("revise", no note) has no live defName anywhere in `src/` — likely already cut —
  too ambiguous to chase without more research, skipped.
- The large "replace"-verdict blanket waves (`desert_family_review_2026-09-20`,
  `port_alphaanimals_2026-09-20`, `port_swac_2026-09-20`, `port_tail_2026-09-20` —
  109+55+36+95 = 295 rows) are real owed production work, but they're an existing,
  already-tracked mass-migration effort (`DESERT_FAMILY_PORT_EXECUTION_1`), not a gap —
  queuing speculative alternates into that scope would be duplicating a live wave, not
  filling a hole.

## What I queued and why (19 jobs)

**13 scene / loading-screen renders** (1024×1024, the pipeline's real ceiling —
`common.CANVAS_CEILING_PX`; no precedent exists anywhere in `done/`/`failed/` for a
non-square canvas, so I stayed square rather than gamble an untested aspect ratio into
an unfamiliar validation path):

- `spec_scene_dunesea` — the Dune Sea under Ash'karr's one relentless unsetting sun.
  **Correction made in-flight**: the owner's brief said "twin suns," but Ash'karr is
  tidally locked with exactly ONE sun that never sets (`divine_satiation_engine.md`,
  owner ruling 2026-08-30: *"the old 'twin suns' line is dead"*) — rendered correctly,
  noted in the job's own `style_notes` so it's traceable.
- `spec_scene_jawacaravan` — a scavenger caravan crossing the dunes. This is
  `ui_appearance_spec.md`'s own **Candidate row C**, explicitly logged as "yes, secondary"
  owed art, never generated.
- `spec_scene_kolyskadive` — the gravship Kolyska diving into a sea. Ship-only diving is
  canon (`RM_SeaDiveHatch`); no art of the ship exists anywhere in the registry.
- `spec_scene_scald`, `spec_scene_greysea`, `spec_scene_propanelake`,
  `spec_scene_twilightskylights` — the four named seas, each pulling real documented
  imagery (the Scald's perched-crater-and-spillway mechanism; Grey Sea's salt crust;
  Propane Lake's sub-−55°C alien chemistry; the Twilight Deep's living mold-roof
  skylights and kelp).
- `spec_scene_fallline`, `spec_scene_rustcathedral`, `spec_scene_launchsite`,
  `spec_scene_wrecksite`, `spec_scene_sacredshore`, `spec_scene_nightsidemargin` — six
  more world moments with zero existing art and real documented anchors (escarpment
  pass, the mechanoid Rust Cathedral, the Ancient Launch Site, sunken-wreck salvage
  lore, Oomo's shore-rite, the ground-level nightside margin).

**5 UI letter/alert icons** (128×128, transparent, matching the shipped
`rut_gene_furnaceblood_icon_v1` flat-icon precedent) for event families that fire
today on stock vanilla LetterDef icons with no bespoke art: Greatbole Fruitfall, Flame
Harvest, Long Hunger, Ship Break, Survival Pod/Pod Crash. Confirmed via `grep` that none
of these `IncidentWorker_*` classes reference a custom icon anywhere in `src/`.

**1 alternative creature take**: `spec_creature_atispec_altconcept` — AA_Atispec, a live,
cast Alpha Animals donor creature that got a "revise" verdict 2026-09-06 (*"so strange I
almost love it. A rainbow lobster thing... at least it's creative"*) and was never
touched again — not part of any of the later bulk "replace" waves. A genuine standalone
gap, non-canon, no rig-limit concern.

## Operational caveat — flag this, don't hide it

The artpipe daemon's `background: "transparent"` path validates that all four image
corners are actually transparent (`AGENTS.md`, `artpiped.py`'s legibility/geometry
check) — a contract built for creature/plant/item sprites, never exercised for a
full-frame landscape scene (zero precedent in `done/` or `failed/` for either a
non-square canvas or a fully-opaque "scene" job). My 13 scene jobs use
`background: "transparent"` anyway, because the alternative (a named hex backdrop)
makes the daemon inject "one perfectly flat solid field of X, used nowhere in the
subject" into the prompt, which is actively wrong for a landscape. **Expect some or all
of the 13 scene renders to land in `failed/` purely on the corner-transparency check,
not on content** — the PNG itself should still be inspectable under
`infrastructure/artpipe/_artsrc/<job id>/`. If several land in `done/` cleanly, the
concern didn't bite; if they fail, check `_artsrc/` before assuming the render itself
is bad.

## What I deliberately skipped

- **UI chrome/button/tab/gizmo repaints and the title wordmark** — already shipped in a
  different, explicitly-locked "ancient ship helm" style; queuing painterly-rust chrome
  here would contradict a standing owner ruling (see Survey).
- **The 295-row bulk "replace" port waves** — real owed work, already tracked at scale
  under `DESERT_FAMILY_PORT_EXECUTION_1`; not a gap, and far outside a 15–30 job
  speculative round.
- **Any Star Wars canon subject with a known rig limit** (Ithorian neck, Kaminoan
  proportions, Muun body, Lasat legs) — none of my candidates touched these, so no
  exclusions were needed this round, but I checked.
- **Capybara** (an old, un-noted "revise" verdict) — no live defName found anywhere in
  `src/`; too ambiguous to spend a job on without more digging.
- **A campaign title wordmark concept** — genuinely still an open owner question
  (`ui_appearance_spec.md` §8, item 1), but its correct art direction is the locked
  gunmetal/vector-line console style, not this round's mandated painterly style — noted
  here for whoever picks that question up next, rather than queued wrong.
