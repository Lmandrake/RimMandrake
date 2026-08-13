# Beautiful_Tilemap — concept spec

**Status: `[v2]` concept. Nothing built.** Stashed for CREATE to evaluate; per
`V1_SCOPE.md` this must not become v1 without an owner ruling. **Tags:**
`CONCEPT` = the owner's idea as given · `VERIFIED` = measured against files in
this repo · `ANALYSIS` = added critique, decided by nobody yet.

## 1. The concept — `CONCEPT`
We have utterly beautiful hand-authored maps we downloaded, and the ability to
generate "ok" tier maps from the game via the bridge. Could we author Python, or
Python + GPT, that learns to take game maps and make them closer to the
hand-authored ones, or better?

| step | what happens |
|---|---|
| 1 | Generate an image of the entire map |
| 2 | Pass it to GPT — "make this look more natural, interesting and enticing for RimWorld play; here are the adjectives this biome is supposed to represent" — possibly with contextual prompting about neighbouring tiles or what is happening in the game |
| 3 | GPT returns a candidate PNG |
| 4 | An `interest_evaluator` script validates the new map is more interesting than the original, by whatever metrics apply |
| 5 | A final script translates that into the appropriate terrain types for that biome, by colour and rationale |

If the principles could be encoded in Python/C# it could be an uploadable mod,
but the GPT generative step probably keeps it private.

## 2. Assets that already exist — `VERIFIED`
| asset | path | state |
|---|---|---|
| Hand-authored corpus | `research\RimMandrake\hand_authored_maps\` | 41 entries; 39 of 40 source repos yielded genuine saves; **44 `.rws`** (some repos bundle variants) |
| Corpus census | `research/RimMandrake/reference/rimworld_handcrafted_map_atlas.md` | Source list and study-first shortlist |
| Creator technique | `research\RimMandrake\samuel_streamer_study\02_TECHNIQUE_ANALYSIS.md` | Pt 1 mechanical toolkit, Pt 2 storytelling tricks |
| Save grid read/write | `Utils\rimbench\savemap.py` | Rewrites terrain grids; hazards in §2b |
| Live terrain paint | `skills\rimbridge\` | `jawa/set_terrain_batch`, `jawa/get_terrain_batch` |
| Biome→terrain vocabulary | `design/Jawa/worldbuilding/biome_terrain_palette.md`, `worldbuilding\resource_terrain_matrix.html` | Both present. Biome and terrain kept as separate defTypes; per-terrain verification legend |
| Applier already ruled on | `design/RimMandrake/map_authoring_decision.md` | Bridge vs save-editing decided; inherited here, not reopened |

### 2a. The corpus is machine-readable today — `VERIFIED`
Every `.rws` decoded directly from its `topGridDeflate`:

| measure | result |
|---|---|
| Decoded | **44 of 44**, zero failures; `len(grid) == mapSizeX * mapSizeZ` held on every map |
| Sizes | 250² (17), 275² (10), 300² (7), 350² (2), 400² (2), 500² (2), plus 325×225 and 275×325 |
| Distinct terrains per map | min 11, median 19, max 44 |
| Game versions | 1.4 (21), 1.5 (16), 1.6 (7) |

**The load-bearing finding: decoding needs only `zlib` and `base64` — no game, no
mod set, no load.** The corpus is measurable offline, immediately.

### 2b. Hazards the build must respect — `VERIFIED`
| hazard | consequence |
|---|---|
| `fogGridDeflate` is a **bitfield**, one bit per cell, not the 2-byte shorts every other grid uses | Decoding at 16× the wrong width still "succeeds" and re-encoding silently corrupts the fog of a healthy save. Never add it to `GRIDS`; pass-through is safe by construction |
| `foundationGrid` **not handled** by `savemap.py` | Its sample held one uniform value, so no rule was inferrable. Check before authoring over gravship substructure |
| `clear_under` | Painting natural terrain into `topGrid` alone orphans buried terrain — a state the game never produces. `clear_under=False` only when painting a **floor** |
| Foundation build order | **foundation → terrain → things.** A floor is a one-way door, the refusal is **silent at the write**, and only read-back catches it. `write()` also refuses in-place — always a new path |
| `shortHash` depends on the loaded mod set | Constrains which metrics work on the corpus — §6a |

## 3. Added architecture — `ANALYSIS`
Three parts with a clean seam, which settles the owner's mod-or-private question.

| part | does | deterministic? | shippable as a mod? |
|---|---|---|---|
| **A. METRIC** (`interest_evaluator`) | Scores a map. Learned from the corpus | Yes | **Yes** — needs no external model |
| **B. GENERATOR** | Proposes a candidate. Procedural, GPT-assisted, or both | No, if GPT is in it | Only if procedural |
| **C. APPLIER** | Writes cells, via the bridge or `savemap.py` | Yes | Yes |

**Only B need stay private** — A and C are ordinary code, and if B is ever built
procedurally the whole thing ships. The seam is an explicit **cell-plan**: a list
of `(region, terrain, rationale)`. A and C speak it; only B has to be clever.

## 4. The main technical risk — `ANALYSIS`
**The image round-trip is the weakest link.** A 250×250 map is **62,500 discrete
cells with exact identities**; a returned PNG is a *painting*, not a grid.

| failure | why |
|---|---|
| Colour→terrain is lossy | Terrain identity is categorical. Interpolated, dithered and anti-aliased pixels have no correct answer |
| Output not cell-aligned | Nothing constrains the return to the original grid pitch, or even its dimensions |
| Fine structure becomes noise | Single-cell features — a chokepoint, a one-tile bridge — sit below the resolution a model reliably preserves |
| **Beautiful at a glance, unplayable at a cell** | Mush that reads well zoomed out and pathfinds terribly zoomed in. The specific failure to fear |
| Not reproducible | Same prompt, different map, so a regression cannot be diagnosed |

This does not make the idea wrong — it makes **step 5 the hard part**, and step 5
is currently one line of the concept.

## 5. Generator options, compared — `ANALYSIS`
| | **B1 — pixels** (concept as written) | **B2 — plan, not pixels** | **B3 — procedural only** |
|---|---|---|---|
| Model returns | A candidate PNG | Structure as text or coarse regions: a river here, a ridge there, a clearing, a chokepoint | Nothing; Python decides |
| Cells decided by | Colour classification | Deterministic Python paints exact cells from the plan | Python |
| Cell-exactness | Lost, then approximated | **Kept** | Kept |
| Reviewable before it lands | Only as an image | **Yes — plan is readable text** | Yes |
| Reproducible | No | Plan replays exactly | Yes |
| Surprise / organic feel | **Best** — its real advantage | Medium; bounded by the offered vocabulary | Weakest |
| Shippable as a mod | No | No | **Yes** |

**B2 is the recommendation, not a verdict — and B1's advantage is understated
above:** an image model has seen a great many natural landscapes, and that
irregularity is hard to get from a rule, while B2's plans risk feeling like one
template applied five ways. The honest answer is probably a hybrid — **B1 as idea
source, B2 as the pipe**: ask for the image, read structure *out of it* into a
plan, paint from the plan. The image never touches cells.

## 6. The metric — the piece worth building first — `ANALYSIS`
**The corpus may make the GPT step optional for the metric entirely.** 44 maps is
a measurable corpus, not an inspiration board. Compute what separates it from
vanilla:

| family | candidate features |
|---|---|
| Adjacency | Terrain-pair transition frequencies; how often A borders B versus chance |
| Region structure | Connected-region size distribution — count, mean, tail |
| Edge complexity | Perimeter-to-area ratio per region; crinkly or smooth coastline |
| Openness | Open-vs-blocked ratio, globally and in local windows |
| Chokepoints | Count and width of minimum cuts between large open regions |
| Water & elevation | Presence, connectivity, branching of water; ridge continuity |
| Distribution | Clustering versus uniform scatter — the most likely vanilla tell |

**That is the `interest_evaluator`, learned from data rather than asserted** — and
the part most likely to ship as a mod, needing no external model.

### 6a. What the corpus can and cannot tell us — `VERIFIED` + `ANALYSIS`
`shortHash → defName` requires a dump taken with **the same mod set as the save**.
Corpus maps come from other creators, span 1.4–1.6, and carry their own
`<meta><modIds>`, so our dump cannot resolve their names. This matters less than it looks:

| metric kind | needs names? | available on the corpus |
|---|---|---|
| Topology — region sizes, edge complexity, openness, chokepoints, clustering, adjacency *structure* | **No** — works on raw hash values | **Yes, today** |
| Semantics — is this water, is it buildable, is it biome-appropriate | **Yes** | Needs a per-map resolution step |

**Build the topology metrics first** — computable now, and where the
hand-versus-vanilla difference most plausibly lives. Semantics need a
vanilla-terrain hash table (vanilla defNames are stable so their hashes are
*likely* stable across mod sets — **verify, do not assume**) or per-map dumps.

### 6b. Validation needs a control — `ANALYSIS`
**Before trusting any metric, check it ranks the 44 hand-authored maps above
vanilla-generated ones.** Generate vanilla maps via the bridge at matched sizes
and biomes, score both populations, require clean separation. **If the metric
cannot separate the corpus from vanilla it cannot judge a candidate, and
everything downstream is built on nothing.** A hard gate, and a cheap one.

⚠️ **Two confounds.** The corpus spans **three game versions** and **eight sizes**, so
a metric that merely detects "1.4" or "is 500×500" would pass while measuring
nothing. Match controls on size; normalise or stratify by version.

## 7. Playability gates are not optional — `ANALYSIS`
**A beautiful map with no buildable flat area, blocked pathing, or no geothermal
is worse than an ok one.** Hard constraints sit beside the aesthetic score and
**must be able to veto** — no weighted sum where beauty buys off unplayability.

| gate | check |
|---|---|
| Buildable area | Contiguous buildable region above a floor size, near the likely landing point |
| Connectivity | Edges reachable from the interior; no sealed regions holding required resources |
| Pathing | No unintended full-width barrier; caravan and raid entry viable |
| Resources | Geothermal, ore, soil at or above biome norm; water reachable if the biome is supposed to have it |
| Substructure sanity | Landing area not left in a state the build order cannot fix — foundation is a one-way door |

Structure: **hard gates first, veto on failure; score only what survives.**

## 8. Context inputs — `ANALYSIS`
| input | source | how it enters |
|---|---|---|
| Biome adjectives | `design/Jawa/worldbuilding/biome_terrain_palette.md` already carries per-biome role and character (desert as "the primary sea to cross"); `design/Jawa/worldbuilding/desert_world_design.md` carries the four-axis "why land here?" framing | Prompt text block, and the allowed-terrain whitelist |
| Legal terrain per biome | Same file, Tables A/B | **A hard filter on output**, not a suggestion. The applier refuses terrain the biome cannot carry |
| Neighbouring tiles | Biomes adjacent on the planet grid | Edge-conditioning: a map bordering a lush tile should not have a hard discontinuity at the map edge |
| In-game situation | Bridge reads — faction presence, quest state, colony status | Optional flavour ("this tile is contested"). Lowest priority; add last |
| Creator technique | `research\RimMandrake\samuel_streamer_study\02_TECHNIQUE_ANALYSIS.md` Pt 2 | Not prompt text — **generator design principles**: one legible premise, then subtract everything that contradicts it; constraint as narrative engine |

## 9. Cost of one end-to-end run — `ANALYSIS`
| stage | time / tokens (estimates except where marked) |
|---|---|
| Read source map | < 1 s `VERIFIED` — pure zlib |
| Model call, image→image (B1) | 10–60 s, image-priced |
| Model call, image→plan (B2) | 5–30 s, ~2–10k in / ~1–4k out |
| Colour→terrain translation (B1 only) | seconds to minutes |
| Apply via bridge | `jawa/set_terrain_batch` moved 421 cells in **one call, 14.0 ms** `VERIFIED`; a full 62,500-cell repaint was extrapolated at ~2.4 min before batching collapsed it |
| Apply via `savemap.py` | seconds, but costs a **save/load cycle** — a cold load is ~23–30 min |

⚠️ **Bridge latency figures here are samples, not properties** — three runs on one
map spread 35%. Re-measure; never design against a quoted number.

**The dominant cost is the apply path, not the model.** Bridge apply is seconds,
save-editing costs a game load — that, not token spend, decides whether iteration
is tolerable. Read `design/RimMandrake/map_authoring_decision.md` before any build.

## 10. Smallest useful first version — `ANALYSIS`
**Metric only. Score existing maps. Generate nothing, apply nothing.**

| in | 44 corpus `.rws` + a matched set of vanilla-generated maps |
|---|---|
| out | A score per map, and which features separate the populations |
| proves | That "interesting" is measurable at all |
| costs | No model, no mod, no game load beyond generating controls |

Why this slice: **independently useful** even if nothing else is built (it ranks
maps the campaign is choosing between); it **de-risks everything downstream**,
since every generator option and the whole apply path depend on being able to say
a candidate is better; it **needs no external model**; and it runs **entirely
offline**. If §6b fails the project stops here having spent very little.

**Stop after it and evaluate. Do not queue the generator until the metric
separates the populations.**

## 11. Open questions the owner must answer before a build starts
| # | question | why it blocks |
|---|---|---|
| 1 | Pixels (B1), plan (B2), or hybrid? | Decides whether colour→terrain translation is built at all — the largest chunk of work |
| 2 | Is the goal "better than vanilla" or "close to the corpus"? | The corpus is a *target* in one reading, a *floor* in the other. Different metric, different success test |
| 3 | Run on landing (once per tile) or on demand? | On-landing must be fast and unattended, so gates must be trusted without review; on-demand lets a human read the plan first |
| 4 | May a map the player already occupies change under them? | Repainting a colonised tile destroys plants and can strand buildings. Probably fresh tiles only — but that is a ruling |
| 5 | Ship the metric as a mod, or keep everything internal? | Only affects part A, but changes how A is written from day one |
| 6 | Which biomes are in scope? | Desert and arid are the campaign's own and well documented; the palette covers far more. Scoping cuts the work sharply |
| 7 | How much surprise versus how much control? | Question 1 restated as taste — and only the owner can answer it |

**This spec builds and benchmarks nothing beyond the §2a decode census.** Every
option above is open; the only claims presented as settled are tagged `VERIFIED`,
and each is a measurement of a file in this repo.
