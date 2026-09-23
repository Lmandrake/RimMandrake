# MACBENCH_REBOOT_HANDOFF_202609230538 — READ FIRST on wake

Follows `MACBENCH_REBOOT_HANDOFF_202609222127`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

🔴 **"Star Wars style" naming is NOT Star Wars IP — and I spent an hour of the owner's session
building on the opposite assumption before he corrected me.**

He asked for *"wild jungle trees with bizarre Starwars names."* I read "Starwars names" as canon IP,
concluded §7 Q11 forbade them in the RimMandrake tier, and routed an entire invented tree roster into
the Star Wars layer with a thin vanilla fallback left behind in the franchise-free mod. His
correction: *"The fact that we will use 'star wars style' naming doesn't mean they have to live in the
star wars layer. The top mod without star wars will look precisely the same as the star wars enhanced
one."*

Recorded as **Q11a** in `design/RimMandrake/biome_mod_architecture.md` beside Q11, because an item is
not authority. The rule: **the tier line is IP, not flavour.** An invented exotic name is free to live
in `RM_` tier; only a genuine canon name routes through the Utinni patch layer.

🔑 **And the second-order lesson, which is the one that will actually save a session:** he then went
further and removed canon from the roster entirely (*"we're making our own"*). That single ruling made
**four** of my queued questions moot rather than deferred — the Legends-vs-current-canon tier call, two
canon-admission edge cases, and a false-canon row. ⇒ **When a tier or provenance question starts
generating sub-questions, ask him whether the category is needed at all before adjudicating within
it.** I adjudicated first and he deleted the category. That is the same failure shape as the
multi-homing tie-break algorithm recorded in the previous handoff — a review question being turned
into a rule system — and it recurred within 24 hours in a different domain.

## What the owner should see

1. 🔴 **ONE OPEN QUESTION, left deliberately unsolved: the Greentide's insect axis is now empty.** He
   named four dangers for that biome — plants, beasts, diseases, **insects** — and then placed the Ants
   (the only designed insect) in the **Fever Wood**, where they already live. Extending them into the
   jungle was offered and **declined**. ⇒ Either the jungle gets its own insect or the axis drops there.
   ⛔ Recorded on `FEVERWOOD_ANT_HIVE_DUNGEON_1` with an explicit ban on resolving it by moving the
   Ants, because that is the cross-biome placement his own fauna law sends to a biome review sitting.
2. 🔴 **A canon claim in a design doc was FALSE, and its evidence was a third-party mod.** Row 10 of the
   tree roster read *"Canon. Felucian glowspore is canon Felucia flora; the donor row
   `Plant_FelucianGlowspore_Wild` is the wild form"* — circular. MEASURED by Wookieepedia search:
   `glowspore` → **NO HITS**, `felucian glowspore` → **NO HITS**. Corrected at `beaec4315`. He had
   asked to see the list precisely because he suspected this, and he was right. The other twelve rows
   verified clean against real pages.
3. **I raised a challenge on plant sizes; he overruled it. Recorded as declined, not open.** Six
   mid-storey trees at 4–6 cells are merely normal-big-tree sized against our own reference for "huge"
   (`RUT_SweetlineTree` at 5.0–6.5, and vanilla's biggest common tree at ~6.0), and `RM_Mirrelbole` at
   **4** is the sap tap feeding the whole fuel economy while smaller than a vanilla pine. He ruled *keep
   the range, add above it* — boldness goes into a new enormous fellable giant instead. ⛔ Do not
   quietly inflate the mid-storey later.
4. ⚠️ **His risk/reward direction is recorded under MY seat, not as his authorization.** The message
   arrived mid-tool-call, so `block_forged_owner_said.py` could not see the transcript and refused the
   flag. `GREENTIDE_RISK_REWARD_EXCHANGE_1` carries his wording but is stamped BENCH. ⇒ **If it must
   bind as an owner ruling, he needs to restate it in a live session.** Same applies to the `needs`
   change parking `SEA_FLOOR_AND_CATCH_PASS_1`.
5. **Two "may be impossible" flags I downgraded to leads, deliberately — he should know they are not
   yet verified.** The risk/reward pass called pawn-matched body parts and mod-readable disease
   recovery possibly unbuildable. Both look tractable (the base game appears to regrow lost parts via a
   late-game drug, and tracks immunity per pawn), so the items say **read those mechanisms**. ⛔ That is
   a lead, not a measurement, and the items say so — do not let it harden into a claim.
6. **The signature-giant answer had a side effect he then fixed.** Choosing the already-built Greatbole
   silently deleted the source of premium hardwood: `RUT_GreatboleCore.xml:49` is `deconstructible
   false`, while `the_greentide.md:214` runs the ladder *"normal trees (fall) → giants (crack, fall,
   hardwood jackpot)"*. He ruled **keep a fellable giant too**, distinguished by **life stage**. Worth
   his awareness that an answer to a naming question moved an economy.

## What is half-done, and where it stops

- `GREENTIDE_JUNGLE_TREE_ROSTER_1` — 21 invented plants designed and named (names verified unused), but the roster document's **sizes do not yet match his rulings** and he has barred art until they do; **NEXT: edit `design/Jawa/worldbuilding/biomes/greentide_tree_roster_2026-09-22.md` to add the enormous fellable giant row above 10 cells, give the seven ground rows sizes big enough to block sight, and retier every `RSW_` defName to `RM_`** — then, and only then, queue art.
- `GREENTIDE_RM_MOD_BUILD_1` — the actual mod-migration plumbing, **untouched all session** and the only thing standing between this biome and being a deployed independent mod; **NEXT: add the second `RM_Greentide` op to the five genuinely-owed files named in that item's step-4 section** (`BiomeDescriptions_Ashkarr.xml`, `BiomeFlora_Ashkarr.xml` via its generator, `RSW_ScrapNestBird.xml`, `RSW_TunnelSnake.xml`, and check `gen_cast_patch.py` output) — ⛔ and touch none of the ~30 other references, which are deliberately campaign-only.
- `SEA_FLOOR_AND_CATCH_PASS_1` — **stopped by owner ruling**, parked `needs game-up`; **NEXT: on the Desktop, open a coastal land map beside an ocean and record which terrain defs generate at the water's edge**, then answer on the item whether a sea's catch is consumed from the land map or the sea tile. The Mac-side shore audit is already banked on the item — do not redo it.
- `GREENTIDE_FRENZY_DISEASE_1` / `GREENTIDE_GRENADE_WEAPONS_1` / `CONTAGION_GENOME_ORGAN_GROWING_1` / `FEVERWOOD_ANT_HIVE_DUNGEON_1` — all four filed tonight with full prose, **nothing designed or built**; **NEXT: card him on the one scope question each item names** (the Frenzy's delivery route; which of three grenades proves the category; whether the organ host is renewable or consumable; how many symbiotic relationships in the hive) before any mechanism work.
- `GREENTIDE_HUMMING_GROVE_1` — unblocked and moved to `needs offline`, mechanism settled as generic; **NEXT: build it in `mandrake.rm.creaturebehaviors` copying `RM_MapComponent_BiomeAttitude`'s per-tick layer shape**, driven by humming trees near the camera rather than a mood band.
- **The reaction-mechanism convergence — the most valuable unbuilt idea of the session; NEXT: design the ant-hive rally, the ambush-plant swarm and the shipped `RM_CompPlantAlarm` as ONE generic mechanism at three scales** rather than three implementations, and state the propagation bound (unbounded chaining is a colony-killer, worse inside a hive where retreat is a corridor).
- `DUPLICATE_CANON_DEFNAME_PAIRS_1` — inherited, **still untouched**, and correctly so: its first step needs donor defs unreadable from the Mac; **NEXT: on the Desktop, confirm per animal that the donor def and our `RSW_` port are the same creature** (gizka/kreetle/nuna first; ⛔ `Shiro`/`RSW_ShiroTrap` is NOT an established pair).
- `ROSTER_DEAD_BMT_NAMES_SWEEP_1`, `KORRUM_ART_REGEN_1`, `STONEBACK_BOKKA_ART_STANDARD_1` — inherited from two handoffs ago, **not touched in either session**; NEXT: read `MACBENCH_REBOOT_HANDOFF_202609221537` for their state, which is unchanged.

## Traps learned

1. **`<wildPlants>` uses the shorthand `<DefName>commonality</DefName>` form, not `<li><plant>`** — a parser for the `<li>` form reads every row as empty; it gave me two contradictory measurements of one file before I read the raw block (filed: LESSONS).
2. **A Wookieepedia lookup by guessed exact title returns MISSING, which is not evidence of non-canon** — use the search API, and note it omits `searchinfo` on zero results so a `totalhits` parser raises on exactly the passing case (filed: LESSONS).
3. **A canon claim whose evidence is a third-party mod's defName is not sourced at all** — the mod ships a plausible name and an agent reads the name back as proof; `glowspore` returns zero hits (filed: LESSONS, and corrected in place at `beaec4315`).
4. **`block_forged_owner_said.py` cannot see an owner turn that arrives mid-tool-call**, so a genuine quote is refused; take the guard's own exit and record under your own seat, and ⛔ never write the flag name inside a `--reason` string (filed: LESSONS).
5. **`SendMessage` is not enabled in this window, so a backgrounded `Agent` cannot be corrected mid-run** — a subagent on a brief you later find wrong runs to completion on it (filed: LESSONS).
6. **The 600s watchdog killed a design agent again, but the incremental-write briefing saved 19KB** — on a stall notification the first act is to commit what survived, then relaunch only the missing sections (filed: LESSONS).
7. **`rimflow needs` requires `--to`, `file` takes no `--reason`, and every verb refuses without a seat** — `--seat BENCH` or `RIMFLOW_SEAT`; three failed invocations before this was clear (see: `rimflow <verb> --help`).
8. **A `cd` in one Bash call persists into later calls** — already recorded in CLAUDE.md, and it still cost me two failed reads after `cd`-ing into a mod folder. Use absolute paths.

## Commits

```
15ab626c6 Ant hives land in the Fever Wood, and their reaction is a mechanism we already have
6ec049d0f The Frenzy, jungle grenades, and limb-growing moves to the Contagion
df096d2c7 chore(sync): laptop 2026-09-22T21:25:06-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 3 more
a23454b89 Greentide exchange §5-6: seven owner cards and the twelve mechanism questions the build order actually depends on
ae5ee6ada Greentide exchange §4 complete: ten reward categories, ranked, plus the seven defences that stop the hazard biome becoming the best home
92fa6cfce Greentide exchange §4: first three reward categories — the fevers pay in qualified people, medicine priced in hours, cuisine as a combinatorial system not a list
20db4f699 Sizes reviewed before art, as he asked: boldness goes above the range, not into it
6721429bc Preserve the risk/reward audit the stalled design pass left uncommitted
d71b17543 Camera-attached is fine, so the humming grove stops being an engine question
db4158282 A non-fellable landmark had quietly deleted the hardwood jackpot
31e1014ef Greentide roster: state what the giant IS, not what a dead proposal was
a7a72328b Greentide roster: demote the canon research to a marked appendix so no row reads as canon
21d5a0a3d Greentide roster: the old page's blocking question and its giant proposal were both wrong
78d128f88 Greentide roster: canon trees were wrong, so all 21 rows are now ours and invented
eeaee008b No canon trees: the jungle's flora becomes ours, and the tier problem disappears
596051329 chore(sync): laptop 2026-09-22T20:22:53-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 3 more
beaec4315 One roster row cited the donor mod as proof of its own canon, and was false
d2fcdfaca The ambusher twitches one leaf, wakes its neighbours, and hides in a choked jungle
0093bad79 Greentide tree roster proposal: 13 trees + the wroshyr, and the donor question was already answered
4418c1e06 Star-Wars-STYLE naming is not Star Wars IP - I had the tier line in the wrong place
... 5 more: git log --oneline 6db57b322..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/codebase_health.html   automated health publisher (rimflow-triggered regen), derived — not mine to commit
 M Transient/codebase_health.json   automated health publisher regen, derived — not mine to commit
 M Transient/codebase_health_artifact.html   automated health publisher regen, derived — not mine to commit
 M infrastructure/dashboards/hub/data/health.json   automated health publisher regen, derived — not mine to commit
 M infrastructure/state/codebase_health_last.json   automated health publisher regen, derived — not mine to commit
 M infrastructure/state/queue/BENCH.md   rimflow's own queue-snapshot regen, triggered by my seven item filings this session — derived, not hand-edited
```

