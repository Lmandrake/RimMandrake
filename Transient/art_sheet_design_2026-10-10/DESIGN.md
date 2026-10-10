# Biome art review sheets — design pass (2026-10-10)

Status: PROPOSAL. Live builder and served sheets unchanged. Files here: `mock_sheet.html` (+`img/`), `proposed_mock.png`, `current_therot_blastpod.png`, `current_greentide_pekopeko.png`.

## 1. Confusion catalogue (ranked)

**Evidence.** 27 `Transient/biome_ffar/*.decisions.json` (991 rows, **500 non-empty owner notes**), the
structural state of 898 decided rows read against each sheet's own ITEMS, and 29 progress/verify files
(`*_2026-10-10.md`, `*close_progress*.md`). Note counts are regex-classified (multi-label), so they are
"notes that mention X", not exclusive buckets. Ranked by cost: wrong art shipped / owner re-asked first.

| # | Confusion | Count | Examples |
|---|---|---|---|
| 1 | **Pictures carry no slot meaning.** Young/grown, male/female, flying, swimming and catch item sit in look-alike strips; one big "renders found by NAME" bucket holds everything unbound (adult, young, flying frame, male, catch, other creature). | 140 rows have >1 graphic slot; 6 row picks are an unbound render on a multi-slot row; 31 catch rows show the *creature's* renders as candidates | **BlastpodShroom** (Rot): picked C (a grown random variant) and ✕'d C; ✕'d D, the plant's **only young picture**; same on **GreyLady**. **PekoPeko** (Greentide): row pick N is `regen_gt_pekopeko_flying_f_4` — a single *flight frame* render, picked as the female **body**; male flight frames (E) sit under the female flip key. **HulduCatch**: candidates are Huldu creature renders (D,E,F,G) beside meat-item donor art. FireHawk: "I don't clearly see those options here" (walk vs flying). **Sketto** (Leaning Scrub): 14 `sketto_fly_*` flight-frame renders sit in the BODY strip as body candidates. |
| 2 | **"Variant" means three things.** The tick is offered on every set of every slot, prechecked by default on every non-donor set, and *one click on any tick turns every machine-default tick into an owner tick* (`artToggleVariant` deletes `variantsDefault` for the whole row). | 224 rows still on machine default; 307 explicit after a click; **33 ticks on a non-adult slot** (21 flight, 5 swimming, 5 second-gender body, 2 young); 94 ticked letters no longer on the page | Thozzik: a default tick on RM_ThozzikSpawned kept his explicit ✕ alive — "the machine's, not his". Dactillion F (old flyer) stayed ✓ after "remove F". WitchesOyster B/C ticked on a single-texture plant (no folder to ship into). Bladderquill/Shadefern/Steamfrond/Verdimoss/Weepmat B never shipped. |
| 3 | **Requests with no control get typed into the note.** | 158 notes ask for more variants (≈60 with a number: "two more", "one more", "many"); 104 description; 66 rename; 43 "based on (b)/the image"; 34 move biome/tier; 26 size/bodysize/behaviour; 23 facings ("now N and S"); 9 life-stage/pose | "Rename" with **no name** on 14 Rot rows → naming sheet needed; Weepingstones 9 rows: the art job marked the note "followed" and the rename/description half was dropped; "triple the cell length" read as drawSize×3, corpse missed; "Two more variants, more realistic" graded each of 48 jobs against the whole note → all refiled. |
| 4 | **Pick and ✕ are independent and unguarded.** You can pick a set and ✕ it, ✕ the only picture of a required slot, ✕ live pictures that cannot be deleted. | 4 pick+✕ same set (BlastpodShroom C, VioletWimple A, BleedingTooth A, Wrinklecap A); 2 slots fully ✕'d (young plant) | BENCH had to ask: "BlastpodShroom — A stays?"; young pictures kept and redraws queued by inference. Purge refused because bytes are live elsewhere: Gizka ♀ south, Vozzik C, Corrik. |
| 5 | **Stale/retired/never-shown pictures look current.** | 124 never-shown pictures across 16 sheets (fixed today); Rot 13 never-shown + 9 re-encoded copies | VioletWimple/Wrinklecap pick "A" was the cartoon his own 10-09 card retired; MortalMorel column A ≠ what the slot held; weepingstones fish A/B showed donor art while the game drew C. |
| 6 | **Dependent rows judged before their source.** | 8 catch jobs rendered with no source (Weepingstones), Twilight NuudalCatch C picked v1 while creature is v2 | "Make it look like a dead one of these. Of course generate AFTER the source is settled" typed on 6 catch rows. |
| 7 | **Undecided vs decided is invisible.** A row with a ✕ and a note but no letter click reads as undecided; a prefill looks like a decision. | Rot 5 rows (AngelMoth, AgariluxPrime, AgelessCap, Nuitae, RegenerantVeil); Weepingstones 4 never clicked | enact treated them as undecided; BENCH had to infer. |
| 8 | **Sheet-confusion questions he typed into notes.** | 15 | "Why tinted green?", "why is that showing blue?", "Where's the ikee art I had before?", "Is this a dug up plant?", "Redundant?" ×2 (Thozzik), "the graphics renders in your sheet for scale are very hard to interpret". |

**Questions BENCH had to ask him afterwards (today alone):** Thozzik delete/keep (default tick conflict) ·
VioletWimple/Wrinklecap "is A the retired cartoon?" · BlastpodShroom pick+✕ · unseen random-folder pictures ·
14 renames with no name (a whole naming sheet) · catch art before creature settled · Ollopom "beauty bonus"
meaning · Huldu fur commodity · Colossia/korrim/Reeds scope. Every one of these is a missing control or a
missing slot label — except Ollopom's "beauty bonus", Huldu's fur commodity and the Colossia/korrim/Reeds scope, which are genuine judgement and rightly stay as notes.

## 2. The flying-art "variant" tick that cannot be unchecked

**Root cause — measured.** The flight set's `✓ variant` button is **covered by the wing-beat playback image**.
In `_itemBody` the playback cell is `<div class="bs-cell bs-play"><img src=…></div>` — the `<img>` is NOT wrapped in
`.ac-thumb`, so the `.bs-cell .ac-thumb{width:86px;height:86px}` rule never sizes it. A flight frame is a wide,
wings-spread sprite, so the ▶S/▶N playback images render at natural size, overflow their 86 px cell, and sit on top
of the set's footer. Screenshot of the live PekoPeko row (`current_greentide_pekopeko.png`, the flight set top-left): the
▶N bird is drawn over the button, which reads "✓ var…". A real click lands on the image (no handler) and the
tick never changes. A scripted `button.click()` in headless Edge DOES toggle it (Strill, Sketto, Dactillion —
scratchpad `edge_probe.py`), which is exactly the signature of an occluded control rather than broken logic.

Three further facts make it worse, and are why his worry is right:

1. **The flight set is also always "picked", and nothing can un-pick it.** `generate_biome` writes `prefillPicks
   {"_flip:<prefix>": <live flip letter>}` for every flyer (Strill E, Sketto E, FireHawk X, Krizzak G), and
   `_itemBody` renders `picks = Object.assign({}, it.prefillPicks, d.picks)`. A flight strip usually holds ONE
   set, `artPick` only sets (never toggles), and there is no "none / redo this slot" control per slot — so the
   green "picked" frame on the flight set can never be removed, whatever the variant button says.
2. **The variant tick is prechecked on it.** `window.artDefaultVariants` (owner rule 2026-10-06) ticks every
   set that is not a donor original — a `live` flip-book counts as ours — so 21 rows carry the flight set as a
   variant (e.g. Neebray B, Screecher C, Shyrack D, Sketto E, all `variantsDefault`).
3. **One click launders every default.** `artToggleVariant` calls `artEnsureVariants` (materialises the
   default list) then `delete rec.variantsDefault` — so toggling ANY set's variant converts the flight set's
   machine tick into an owner tick. The queue wrapper also materialises the list on every save of the row.

**Why his worry is right (latent enact bug).** `enact.py` step 2b ships "explicit" ticks and reads only
`v["picks"]`, not `prefillPicks`. For a row like Strill (`variants [C,D,E]`, `picks` absent) the flight set E is
not "the pick" in enact's eyes, so it is treated as an owner-ticked variant of graphic `_flip:…`. Today that is
harmless only because live frames short-circuit as `installed_already`. For an **artpipe** flight set
(FireHawk j/t, Krizzak Z, FireWasp G) the same path calls `own_slot(..., variant=True)`, which builds
`res = "_flip:<prefix>V_<L>"` and wires an `alternateGraphics` entry — i.e. it would ship wing-beat frames as
an alternate BODY graphic. Same mechanism made the Thozzik conflict.

**Fix (in the proposal):** constrain the playback `<img>` (wrap it in `.ac-thumb` / `object-fit:contain`, `pointer-events:none`) — a one-line CSS fix that can ship before the redesign; variant controls exist only in a slot whose kind is an adult random/alternate pool;
no default ticks; `variantsDefault` never converts to owner ticks; per-slot picks are explicit data with a
per-slot "none / redo / keep current" state; enact refuses a variant letter whose slot is not a pool.

## 3. Proposal

### 3.1 The unit of decision is the SLOT, not the row
A **slot** is one picture the game draws for the subject. The builder already knows most of them (census
`art.resources[].role`, `gametex.def_extra_texpaths`), but flattens life stage and sex into "body". Proposed slot
vocabulary, each read from the live def dump, never inferred from a filename:

| kind | slot | source in the def | required? |
|---|---|---|---|
| animal | `adult` (`adult·male` when the kind has `femaleGraphicData`) | last `lifeStages[].bodyGraphicData` | always |
| animal | `adult·female` | last `lifeStages[].femaleGraphicData` | when present |
| animal | `young` / `juvenile` (one per distinct texPath, labelled with the lifeStageDef: AnimalBaby, AnimalJuvenile, larva …) | earlier `lifeStages[i].bodyGraphicData` whose texPath differs from adult | when it differs |
| animal | `flying` (`·female` when `flyingAnimationFramePathPrefixFemale`) | PawnKindDef flip-book prefix | when `MaxFlightTime > 0` |
| animal | `swimming` | swimming graphic | when present |
| animal | `alt-adult` POOL | `alternateGraphics` | pool |
| animal | `corpse/dessicated` | shown read-only, never pickable | — |
| plant | `grown` (POOL when texPath is a `Graphic_Random` folder) | `graphicData` | always |
| plant | `young` | `plant.immatureGraphicPath` | when present |
| plant | `leafless` | `plant.leaflessGraphicPath` | when present |
| item | `catch` / `item` | ThingDef `graphicData` of the catch | always; **depends on** the creature row |
| — | `unassigned` | renders matched by NAME only | — |

**Unassigned renders cannot be picked.** He (or the render's own job metadata — `job.role`, `job.slot`, which artpipe
should write from now on) assigns each to a slot first; a flight-frame render is offered only as "flight frame of
sequence X", never as a body. This single rule kills PekoPeko N, Sketto's 14 `sketto_fly_*` renders sitting in the
BODY strip, BlastpodShroom E/F, and HulduCatch's creature renders.

### 3.2 Controls per slot (revised after GPT review)
- **Click a picture = use it for this slot.** No separate "use my pick" radio (GPT: redundant and contradictory).
  Slot-level buttons are only `accept unchanged` and `redraw this slot` (+ `not drawn` for an optional slot whose
  fallback is known). An untouched slot is persisted as **unreviewed, unchanged** — distinct from an explicit
  `accept unchanged` — and nothing is prefilled as his choice. A row-level `accept all unchanged slots` button and
  keyboard keys (1–9 pick within the focused slot, R redraw, U accept) keep the fast path fast.
- **Four different verbs, never one ✕:** `✕ not for this slot` (local rejection, deletes nothing) · `leave the
  random pool` (pool slots only) · `retire from the game` (live picture; stays until replaced) · `delete from the
  art store` (only in the zoom view, refused with the reason when the bytes are shared). Today's single ✕ means
  all four at once, which is why purges were refused or silently protected.
- **`in random pool` exists only where the graphic configuration is a pool** (Graphic_Random folder,
  `alternateGraphics`), whichever slot that is. Never offered on a sex/age/flight/swim/catch slot that is not
  itself a pool. **No default ticks.** Current members show as `IN GAME`; an untouched pool means unchanged. A
  bulk "add every new render of ours to the pool" button replaces the 2026-10-06 default (owner decision Q2).
- Per-facing rejection stays in the zoom view ("fix only this facing").

### 3.3 Guards (all client-side, re-checked in enact)
1. ✕ on the **only** picture of a required slot → slot becomes `redraw`, and the card says "D stays in game until
   the new one is installed" (current enact already keeps it; now the sheet says so before he clicks).
2. Pick + ✕ of one set is impossible (3.2).
3. A set whose bytes are **retired by a later ruling elsewhere** (art_rulings / ledger) carries a `retired on
   <date> (<sheet/card>)` badge and `use this` is disabled unless he un-retires it there.
4. A live picture's ✕ reads `✕ retire (stays until replaced)`; a ✕ the store cannot delete (bytes live in another
   mod/row) is shown disabled with the reason, not accepted and refused later.
5. A **dependent** row (catch, juvenile drawn from adult, female drawn from male) shows `Waits for <row/slot>`
   and its redraw is queued automatically once the source slot settles — no note needed.
6. A row is `decided` only when every required slot has a state; the row header says "needs you: <slots>".
   The ✕-only / note-only touch can no longer look decided or undecided by accident.

### 3.4 Non-art requests become fields ("asks") — the note is for everything else
| ask | control | today's note volume |
|---|---|---|
| rename | text field + "suggest names for me" | 66 (14 with no name) |
| description | keep / improve / rewrite to match the chosen art | 104 |
| more art | make **N** new **<slot>** versions based on **<letter>** + "how should they differ" | 158 |
| size | body size number; drawn size × | 26 |
| belongs | move to biome ▾ · tier RM/RSW/RUT · cut from this biome | 34 + 51 cuts |
| facings | auto chip "C has no N, S" → [draw N, S from C] | 23 |
| depends | catch/young/female source row (auto) | 6+ |

Each ask is its own work item in enact (art job, def edit, roster move), so "followed" is per ask — the
Weepingstones "art job marked the whole note followed, rename dropped" failure cannot recur.

### 3.5 Decisions JSON — schema 2 (version-aware; every schema-1 file still reads)
```json
"RM_BlastpodShroom": {
  "schema": 2,
  "decision": "A",                       // kept: = adult/grown pick, so every v1 reader still works
  "slots": {
    "grown": {"res": "RotSporeKit/Things/Plant/Boomshroom/BoomshroomGrown", "state": "pick", "pick": "A",
              "pool": {"add": ["B"], "remove": ["C"]}},
    "young": {"res": "RotSporeKit/Things/Plant/Boomshroom/BoomshroomImmature", "state": "redraw"}
  },
  "assign": {"E": "grown", "F": null},   // unassigned renders he labelled
  "purge": ["<sha>", "..."],             // unchanged; per-picture
  "asks": {"rename": {"name": null, "suggest": false}, "describe": "improve",
           "more": [{"slot": "grown", "n": 2, "base": "A", "how": "more realistic"}],
           "size": null, "move": null, "facings": null},
  "note": ""                             // free text, now only for what has no field
}
```
**Revised after GPT review.** Schema 2 is NOT safe for a v1 reader: `decision` alone cannot express a young
redraw or a pool removal, so enact refuses a `schema: 2` record unless it is the v2-aware build, and the sheet
writes `schema: 2` only after that build lands. Each slot also carries `slot_id` (def + field + lifeStage index +
sex, e.g. `RM_PekoPeko/PawnKind.lifeStages[2].femaleGraphicData`), and each set a stable `set_id` (sha256 of its
sorted facing shas) beside its letter, so a letter can never silently point at different pictures; pool changes
record the baseline membership they were made against and enact refuses if the live pool has moved. `assign`
values are explicit strings (`"grown"`, `"not_needed"`, `"other_subject:<def>"`), never `null`. A row is saved
atomically with the sheet's inventory revision.

**Reading schema 1:** `decision` → adult/primary slot pick; `picks{res: L}` → `slots[slot_of(res)].pick`;
`variants` → pool membership **only** for letters whose slot is a pool; a v1 variant letter on a non-pool slot is
read as "keep" (protect from purge) and reported once in enact as `ignored v1 variant tick on <slot>`;
`variantsDefault:true` → no owner pool change (enact already ignores it). Old notes stay as `note`; nothing is
re-parsed into asks retroactively (a one-off migration may *propose* asks for him to confirm, never write them).
Migration resolves every v1 letter against **the snapshot that file was saved against** (`ruled` snapshot /
`shownBase`), never today's inventory; a letter that cannot be resolved is quarantined and listed, not guessed.
Already-laundered defaults (a `variants` list materialised by `artToggleVariant` from the 10-06 default) cannot be
told apart from his ticks after the fact: enact lists them as `legacy variant tick — ruling unknown` instead of
shipping or protecting them silently.

### 3.6 How enact consumes it (transactional)
`enact.py` step 2 iterates `slots` (falls back to the v1 path when `schema` is absent): `pick` → install into
that slot's texPath; `pool.add/remove` → folder / alternateGraphics edits; `redraw` → job with the slot's res,
facings and `base` reference; a variant letter is accepted only if `slot_kind(letter) == pool` (fixes the
`_flip:…V_X` junk path). Step 3 files one job per `asks.more[]` entry and one TODO per def-side ask; step
"followed" is recorded per ask id **only after the work is verified done** (job DONE and installed, def edit
committed), never when the job is filed. Enact journals each operation by `set_id`/ask id so an interrupted run
resumes instead of re-filing; a dependency (catch ← creature) delays only *derivative generation* — keeping or
picking existing catch art is allowed at once.

## 4. Mock (current vs proposed)

Static mock, real thumbnails, 3 rows: `D:\Luke\dev\RimMandrake\Transient\art_sheet_design_2026-10-10\mock_sheet.html`
(render: `proposed_mock.png`). Current-sheet renders of the same subjects, taken from COPIES of the live sheets in
headless Edge: `current_therot_blastpod.png`, `current_greentide_pekopeko.png`.

- **Kabbrik pod / RM_BlastpodShroom (Rot).** Current: three strips headed `body`, `young plant`, `renders found by
  NAME` in 11 px text; the row pick is the right-hand letter column, so "C" is picked AND shows `✕ purging`; the
  only young picture D is `✕ purging` with nothing saying it is the only one. Proposed: `PLANT · GROWN` (a pool,
  with `in random pool`), `PLANT · YOUNG` (required; ✕ turns the slot to redraw and says D stays until replaced),
  `RENDERS NOT YET ASSIGNED` (must be labelled before use), and the asks row.
- **Peko-peko / RSW_PekoPeko (Greentide).** Current: two strips both titled `body` (PekoPeko_f / PekoPeko_m —
  sex only in the filename), a flight strip holding the MALE frames under the FEMALE key, a duplicate `kept` set,
  six by-name renders that are single flight frames shown as S/E/N "sets" — his row pick N is one of them — and
  the ▶ playback images overflowing onto the `✓ variant` buttons. Proposed: `ADULT · FEMALE`, `ADULT · MALE`,
  `FLYING · MALE`, `FLYING · FEMALE`, unassigned renders labelled "flight frame — not a body".
- **Huldu catch / RM_HulduCatch (Weepingstones).** Current: meat-item donor art beside four renders of the living
  otter, all pickable, default-ticked variants C, D. Proposed: one `CATCH ITEM` slot, blocked with "Waits for
  RM_Huldu", creature renders shown in a non-pickable reference lane.

## 5. GPT critical review and what changed

`gpt_consult.py -m gpt-6.1-sol --effort high` on DESIGN.md v1 + `mock_sheet.html` v1 + the current row renderer.
Full answer: scratchpad `gpt_answer.md` (≈850 words); the substance:

**Verdict (its words):** "The proposal relocates ambiguity but does not yet eliminate it: pools, dependencies,
migration and completion still require agent inference. The mock visibly contradicts several rules. Fix the
immediate renderer/enact bugs, then specify executable state transitions and migration conflicts before
implementing this layout."

| GPT critique | Accepted? | Change made |
|---|---|---|
| "keep" radio + checked "use this" contradict; slot-state radio is redundant | yes | click-to-use; slot buttons only `accept unchanged` / `redraw`; mock fixed (Peko male/flight no longer show keep+picked) |
| ✕ conflates slot rejection, pool removal, retirement, deletion | yes | four separate verbs (§3.2) |
| "untouched = keep" is a no-op, not approval | yes | persisted as *unreviewed, unchanged*; row-level "accept all unchanged" |
| mock called Kabbrik decided with an unassigned render; Huldu catch blocked yet pickable | yes | row header counts unassigned renders; dependency delays only derivative jobs (§3.6), mock updated |
| "additive, v1 readers still work" is false | yes | schema 2 is version-gated; enact refuses unsupported records (§3.5) |
| letters are unstable; need set ids, slot ids, inventory revision, pool baselines | yes | `set_id`, `slot_id`, baseline-checked pool deltas, atomic row save (§3.5) |
| migrate against each file's own snapshot; laundered defaults are unrecoverable | yes | §3.5 migration + `legacy variant tick — ruling unknown` |
| mark asks "followed" only after verified completion; journal + resume | yes | §3.6 |
| shared texPaths: one resource can serve several stages/sexes; `MaxFlightTime>0` alone is not proof | yes | a lane shows "also used by: juvenile, female" and edits warn; flight slot requires the flip-book prefix AND the stat |
| corpse/desiccated cannot be always read-only (size asks missed corpses) | partly | shown read-only, but a size ask lists every slot it rescales, corpse included |
| numeric size fields do not capture "triple the cell length" | yes | size stays a field + required free-text scope; current value shown |
| mock dropped canon and in-game-size context | yes | mock shows the context column placeholder; those panels are unchanged |
| asks should collapse; note must stay prominent | yes | asks are chips that expand; note box enlarged, "nuance welcome" |
| "every question was a missing control" overstates it | yes | §1 wording kept to the questions that ARE missing controls; Ollopom beauty / Colossia scope are judgement, stay as notes |

Not taken: keyboard-only flow as the primary path (the owner works by mouse; keys are an addition).

## 6. Implementation plan

**Stage 0 — hotfixes, no schema change (ship first, each ≤ 1 h, own selftest):**
1. `art_sheet.py` `_itemBody.faces()`: wrap the playback `<img>` in `.ac-thumb` (or `.bs-play img{max-width:100%;max-height:100%;object-fit:contain;pointer-events:none}`) so the flight `✓ variant` is clickable. Selftest: render a flip row through `gate_browser` and assert `elementFromPoint` at every `.bs-var` centre is the button.
2. `art_sheet.py` `artToggleVariant`: stop materialising + laundering defaults (record owner ticks separately, e.g. `variantsOwner: [...]`, and never delete `variantsDefault` for letters he did not click). Selftest in `selftest_art.py`.
3. `enact.py` 2b: refuse an explicit variant whose graphic is `_flip:`/swimming/young/second-sex (anything not a pool); list it as `ignored variant tick on <slot>`. Selftest `selftest_enact.py` with the Strill shape (`variants [C,D,E]`, no `picks`).
4. `art_sheet.py`: `artDefaultVariants` excludes non-pool slots (stop prechecking flight/swim/young/sex sets) pending Q2.

**Stage 1 — slot model (builder only, sheets still schema 1):**
- `gametex.py` deftex schema 3: keep the `lifeStages[i]` index and lifeStageDef, `bodyGraphicData` vs `femaleGraphicData`, flip prefixes (+Female), swimming, alternateGraphics, plant immature/leafless, Graphic_Random-ness; per texPath a list of slot_ids (a shared path stays one resource with several contexts).
- `biome_census.py` / `art_sheet.generate_biome`: lanes from slot_ids; `ROLE_TEXT` replaced by slot labels ("ADULT · FEMALE", "PLANT · YOUNG (immature)" …); by-name renders go to UNASSIGNED unless the artpipe job carries `slot` (new field written by `fill_queue.py`); catch rows get the creature renders as a reference lane.
- `scaled_review_gate.py`: new rulings — every lane labelled with a slot; no `.bs-var` outside a pool lane; no pickable card in UNASSIGNED/REFERENCE; no control occluded (req 13 hit-test). Selftests in `selftest_scaled_review_gate.py`.

**Stage 2 — schema 2 + controls:**
- Sheet JS (`art_sheet.py` BIOME_BODY + the review-sheets skill's `sheet_template.html` hooks): click-to-use per slot, slot buttons, four ✕ verbs, pool tick, guards §3.3, asks chips, `schema: 2` records with `slot_id`/`set_id`/inventory revision. The skill's server already merges per row; it gains a revision check only.
- `enact.py`: v2 path over `slots` + `asks`; v1 path kept; journal by `set_id`/ask id; "followed" per ask after verification; dependency gates only derivative jobs. `remap_decisions.py` learns `set_id`.
- New `src/RimMandrake/Utils/art/migrate_decisions_v2.py`: reads each v1 file against its own snapshot and writes a **proposal** file beside it (never the decisions file) listing quarantined letters and `legacy variant tick — ruling unknown`.
- Selftests: `selftest_sheet_slots.py` (slot derivation for PekoPeko, Sketto, BlastpodShroom, HulduCatch, Thozzik); `selftest_enact_v2.py` (pick+✕ impossible, only-young ✕ → redraw, pool-baseline drift refused, catch dependency, interrupted-run resume); a v1 back-compat replay of all 27 current decisions files that must produce an identical enact plan except the listed legacy ticks.

**Stage 3 — rollout:** rebuild one biome (The Rot) under schema 2, he reviews one sitting, then all sheets. The review-sheets SKILL.md gets the slot/verb vocabulary.

## 7. Owner decisions

**Q1 · header "Young art"** — When you ✕ the only young (or female, or flying) picture, what should the sheet do?
- (a) Treat it as "redraw this slot": the old picture stays in the game until the new one is installed. *(recommended)*
- (b) Refuse the ✕ until you have picked or asked for a replacement.
- (c) Remove it at once and let the game fall back to the adult picture until a new one exists.

**Q2 · header "Variant tick"** — The 2026-10-06 rule pre-ticks every new render as a variant. Keep it?
- (a) No pre-ticks; an "add all new renders to the random pool" button per row instead. *(recommended)*
- (b) Pre-tick only inside a random-pool slot of the adult/grown form.
- (c) Keep pre-ticking as today, but never on young/sex/flying/swimming/catch pictures.

**Q3 · header "Note fields"** — Which requests should get their own control instead of the note?
- (a) Rename (with a name box), description, "make N more based on X", missing facings; the rest stays in the note. *(recommended)*
- (b) All of those plus size, move-biome/tier and cut.
- (c) Only rename and "make N more"; everything else stays in the note.

**Q4 · header "Old ticks"** — About 300 past rows carry variant ticks that may have been the machine's default, not yours. What should happen to them?
- (a) List them once on a short sheet so you confirm or drop each. *(recommended)*
- (b) Treat them all as yours and ship them.
- (c) Ignore them; only ticks made on the new sheet count.
