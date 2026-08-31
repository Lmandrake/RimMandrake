<!-- status: proposition for the owner — BENCH, 2026-08-31, answering his high-priority ask:
     "search the remainders of V2_DREAMS and our additional mod ideas; what could Fable spec out
     while we retain access." Ranked, decision-ready. Nothing below is started without his word
     except where noted. -->
# What to spend Fable on while we have it

**The sorting rule used:** Fable's edge is dense multi-constraint DESIGN — reading
engine source, reconciling a dozen rulings, and writing a spec a weaker model can
then execute mechanically. Anything that is "apply a known pattern N times" (bulk
XML, art pipeline, builds with finished specs) is deliberately excluded: any model
can do those later. Sources swept: `design/V2_DREAMS.md` (all 2,264 lines), the
FOUNDRY queue, and today's Depths work.

## Tier 1 — do these in this window, in this order

### 1. The Depths build spec — ride today's momentum ⭐ recommend starting NOW
The concept (`design/Jawa/worldbuilding/depths_concept.md`, v2 today) and both
donor surveys are fresh in hand. What remains is exactly Fable-shaped:
- **DEPTHS_ODYSSEY_VERIFY_1** (queued): the Odyssey source read — vacuum pipeline
  patchability, vacsuit stat gating, leak/flood-fill, orbital mapgen + arrival
  families, vanilla 1.6 flooding reach. Offline, rimsage only, game state
  irrelevant. It decides patch-mod vs companion-DLL and therefore all cost.
- Then the **v1 build spec**: the drowning/pressure/drag stat-and-extension stack
  (shaped so §7's genes switch it off per race), the per-environment weapon verb
  gate, the lure-pressure core shared with Visibility, descent arrivals, the
  Deepwater faction def surface.
Payoff: the campaign's next big mod becomes executable by any seat on any model.
*(This is on FOUNDRY's queue and BENCH-adjacent; I intend to start the source
read while AFK unless you say otherwise.)*

### 2. The Sarlacc spec — the register's own "cheapest large win"
V2_DREAMS calls it confirmed buildable and critical for v2; what blocks it is
design intelligence, not effort: verify the two unestablished mechanisms
(does `FleshmassHeart` spawn in the Undercave; can a `PitGate` be sited
deliberately), design the CQF-quest-destination route that avoids reopening
Anomaly, respect the `AmbientHorror` findings already measured, and design the
pearl economy (sited, risk-earned, non-farmable). One session of source reading +
spec writing turns the most recognizable Tatooine set-piece into a filed item.

### 3. The Nine Voices cast bible — the least substitutable item on this list
Re-scope `llm_voice_preauthoring.md` from one Cradle-Mind to the nine-god CAST
under the inherited R-W6 constraints (no narrator, rivals who never acknowledge
each other, the ship never describes itself, the tenth strand possibly
unaddressable). This is bounded by WRITING quality — persona voice, theology,
restraint — which is where the model gap is largest and where a later cheap pass
would do real damage. Pure design doc; no game, no source read.

### 4. Research-tree normalization taxonomy — draft now, rule later
`RESEARCH_TREE_NORMALIZATION_1` (BENCH queue) is gated "after the droids land,"
but the *taxonomy* isn't: restructuring ALL research across the ~578-mod game is
a synthesis over hundreds of ResearchProjectDefs and every doctrine ruling
(turret doctrine, archite ladder, weapons absorption, droid system). Fable
deliverable: the target tree shape, tier grammar, migration rules and a
validator design — handed to you as a decision document, with the mechanical
retag left for later. This also de-risks ARCHITE_LADDER_RETHINK_2, which is the
same question at smaller scale.

## Tier 2 — strong candidates if the window holds

5. **Race regeneration architecture** (V2_DREAMS "Regenerate the races from
   scratch"): 69 species, 114 genes, 713 textures authored as ours, ending the
   donor dependency `gen_races_mod.py` still carries. Spec the per-species gene
   philosophy + generator architecture now; the build is v2. Subsumes the
   four-stripped-genes question and the six deferred species.
6. **Tusken water raid behaviour**: the steal-and-withdraw `RaidStrategyDef` +
   `LordJob` design — measured 2026-08-14 that no live strategy does it, so this
   is a vanilla-source design job with a small C# result. High fiction payoff.
7. **Cantina Kitchen**: the live-food container building (the mod's genuinely
   novel spine), recipe repointing over VCE/VBE, and the faith-dependent mood
   matrix. Creative-heavy, art already solved by SW Animal Collection.
8. **Planet-method rethink brief** (`PLANET_METHOD_RETHINK_1`): NOT the rethink
   itself — that is yours — but the decision brief: what the old method produced,
   what "author directly, hydrology falls out of elevation, picture continuously"
   implies as candidate methods, and the `REFERENCE_MATCH_HARNESS_2` calibration
   plan. Prepared so your rethink session starts from evidence.

## Deliberately excluded, and why

- **Art passes** (sea monsters, creature redraws, race art polish): pipeline
  work; the bottleneck is generation and your eyes, not model intelligence.
- **Builds with finished specs**: Free Droid Enclaves (~200 lines), restraining
  bolts, rag nest, egg graphic, red mountain rain, salvage blasters, explosion
  model (spec exists at `design/Jawa/explosion_energy_model.md`) — all
  executable by any seat later.
- **Everything the worldgen ruling killed**, and GREAT_NAMESPACE_RENAME
  (executed under NAMING_SCHEME_EXECUTION_1).
- **Ikee posterchild, domestic-animal mutators, moons**: real ideas, small
  specs; they don't need Fable and shouldn't spend it.

## Recommended spend

One Fable session each, in the order 1 → 2 → 3 → 4; tier 2 as the window
allows. Item 1 is started (see its queue item); items 2–4 wait on your word —
each begins with a one-line "go" and lands as a committed spec.
