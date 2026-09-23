# MACBENCH_REBOOT_HANDOFF_202609231859 — READ FIRST on wake

Follows `MACBENCH_REBOOT_HANDOFF_202609231247`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔑 **A frozen sheet's HARD BAN can be superseded in a single sitting, and the built code that
existed to satisfy it becomes orphaned rationale rather than orphaned code.** The Fever Wood's
ban 1 said the deep thing is *"never resolved in ordinary play — no ambient spawn, no codex
entry, no name in player-facing text."* Eleven owner rulings later it is ambient, named, farmed
for meat, imprisoned in a tank, and killable per-map. `FEVER_WOOD_MECHANICS_1`'s F4 was
deliberately built *referenced by nothing* so the ban held "by construction" — that rationale is
now void, and I marked it so in both the sheet and the item.

⇒ **The transferable part:** when a design sitting starts contradicting a frozen sheet, the
sheet's own unfreeze clause (an owner ruling at a sitting, recorded on the item that changes it)
is the mechanism — **use it explicitly and edit the ban in place.** Do not leave the old ban
standing and hope a reader notices the newer doc. I edited `the_fever_wood.md` §6 ban 1 directly
to point at the record, because the next agent to read that sheet cold would otherwise build to
a ban that no longer exists.

🔑 **And the cheapest design move all session was reading canon, not inventing.** The dianoga's
Wookieepedia entry answered **six** separate design questions the owner had just asked —
colour-change-to-transparent (so a pool can look empty), a humming language that *"scared away
all nearby prey"* (the mechanism for his silence ruling), excellent hearing (noise calls it),
water dependency (why it can never leave, only reach), limb regeneration (why you drive it off
rather than kill it), and bone-eating omnivory (why only inedible gear is left as bait). None of
that was invented. **Read the canon entry before designing a canon-adjacent creature.**

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. 🔴 **I superseded a hard ban on a frozen sheet on his authority, and he should confirm I read
   him right.** `the_fever_wood.md` §6 ban 1 is now marked SUPERSEDED in place. His rulings
   clearly intend it — *"learn the lore at last"*, ambient tentacles, a captive on display — but
   it is a frozen-sheet ban and the edit is mine, so it deserves his eye. Record:
   `fever_wood_deep_and_mud_2026-09-23.md` §0.
2. ⚠️ **"Lavender" is not canon and I did not write it in as though it were.** He said *"There is
   a lavender association with its body parts."* MEASURED: zero occurrences across 13 dianoga
   pages. Purple is thoroughly sourced (deep purple skin; the tea stains lips purple). Recorded in
   the canon entry as his flavour note, explicitly not as canon. **"Dianoga cheese" is likewise
   UNCONFIRMED** — he named it, no page exists that I could find.
3. ✅ **I told him this biome lacked a fellable giant tree and needed an `RM_Greatbole` equivalent.
   That was WRONG**, and his own ruling showed why — *"they are so interconnected above you that
   they can no longer fall, so you can just mine right through one"* describes exactly the
   mineable `RockBase` blob already shipped. Corrected in writing with a do-not-file note.
4. 🔴 **He ruled the eye set-piece can end a colony outright with no maturity gate.** I recorded
   that the justification is then *entirely* legibility — corvath ringing a fed pool, pool size
   telegraphing reach, the chorus falling silent, the town's pool-list. If those four are not
   actually delivered, that ruling becomes arbitrary rather than honest. Worth his awareness.
5. ⚠️ **Two known exploits nobody has costed:** a colony can breed cheap animals as lure
   ammunition (§6l), and the borers' wall-altering digging has no rate. Both flagged unset rather
   than guessed.
6. 🔑 **110 of 254 of our own creature defs have no biome home** — nearly all `RSW_`, which is a
   large ready-made pool for his "inject Star Wars opportunistically" method. Caveat: that figure
   includes larvae/pupa life stages whose adults *are* placed, so the true number is lower.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `FEVERWOOD_FLORA_ROSTER_1` — 18 invented plants authored and committed, **zero art, zero defs**; NEXT: **search `infrastructure/artpipe/done/` and `_artsrc/` by subject for all 18** before queueing anything, because three Greentide plants were nearly regenerated on top of already-validated art on 2026-09-20.
- `FEVERWOOD_BOUGH_SOIL_TERRAIN_1` — filed, nothing built, and it **blocks 8 of the 18 roster rows**; NEXT: **author the bough-soil `TerrainDef` and add it as a second `additionalPasses` profile on `RM_RootCausewayBiomeExtension`** — the multi-pass field already exists, so this needs no new C#.
- `FEVERWOOD_TENTACLE_BESTIARY_1` — fully designed across six card rounds, nothing built; NEXT: on the Desktop **measure whether a hediff zeroing Moving pins a pawn mid-path without corrupting its job queue** — the sink-mud, the snare's drag and F1's rescue window all rest on it, and it is UNMEASURABLE on the Mac.
- `FEVERWOOD_SAP_SUCKER_GUILD_1` — three defences ruled, four species confirmed, no defs; NEXT: **create the first `CompProperties_HasGatherableBodyResource` precedent in this repo** (there were zero hits when F8 was written) using `RM_CompGatherableCalmGated`, which already compiles.
- `FEVERWOOD_ALIEN_BIRD_CHORUS_1` — designed, nothing built; NEXT: **give `RM_MapComponent_SilenceCue` a public "hush now" entry point**, the exact gap F2 recorded, and resolve whether `EnvironmentalHazards` can reference `CreatureBehaviors` at all.
- `FEVERWOOD_TWO_FRONT_LURE_1` / `FEVERWOOD_DIANOGA_PRISON_1` — filed this session with full prose, nothing built; NEXT: read their item files, which name what F9 already proved and what it corrected.
- **The fauna roster is NOT written** — only the flora roster is. The guild's three species, the birds, and the crown guild (borers, grazers, waiters) have rulings but no roster document; NEXT: **author `fever_wood_fauna_roster_2026-09-23.md`** in the same shape as the flora roster, working from `fever_wood_deep_and_mud_2026-09-23.md` §6c/§6n/§6q.
- **The per-biome spec sheet he asked me to read was never located.** He described *"a per-biome specification sheet with its definition, terrain, temperature ranges, assigned animals... everything you'd need to know in a single file. Remember?"* I checked the world definition, the biome cut review, the def-bindings table, `review/`, and this morning's 679-file Transient purge. What exists is a PAIR — `biomes/the_fever_wood.md` plus `biomes/rosters/the_fever_wood.json`; NEXT: **ask him to name the file**, and do not re-run the same search.
- `ROSTER_DEAD_BMT_NAMES_SWEEP_1`, `KORRUM_ART_REGEN_1`, `STONEBACK_BOKKA_ART_STANDARD_1` — ⚠️ inherited across **four** handoffs now and still untouched by me; NEXT: **drop them or work one** — carrying them a fifth time is exactly what this ritual exists to catch. ⚠️ I said I would settle them this session and did not.
- ⚠️ A real defect found in passing and **not fixed**: `rosters/the_fever_wood.json` cites `Urusai` where the shipped def is `RSW_Urusai`; NEXT: **check whether that is the class of defect `ROSTER_DEAD_BMT_NAMES_SWEEP_1` already owns** before filing anything new.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
1. `AskUserQuestion` is hook-validated — a header over **12 chars** or a question not ending in `?` refuses the whole card (filed: LESSONS).
2. The `Agent` tool refuses without an explicit `model`; omitting it inherits the caller's tier (filed: LESSONS).
3. 🔑 Wookieepedia's `action=parse&prop=wikitext` API works unauthenticated from this laptop with **no size cap** — prefer it over Fetcher, which silently truncates at 50,000 chars (filed: LESSONS).
4. A design roster can cite a **donor** defName where our shipped def carries an `RSW_` name, so a homeless census reads a cast creature as homeless (filed: LESSONS).
5. `timeout` does not exist on macOS and its failure **resets the shell's cwd** — use `curl --max-time` (filed: LESSONS).
6. ⚠️ **The 600-second backgrounded-subagent death happened again**, exactly as the previous handoff warned: a census agent died mid-read before its first write and left nothing. I re-ran the census myself in one script in less time than the agent had already burned. The mitigation in `CLAUDE.md` is right — but for a *mechanical* census, doing it inline is simply cheaper than briefing an agent to write incrementally (see: `CLAUDE.md > Tools with surprising side effects`).

## Commits

```
0a662a5a6 Two more Fever Wood items: the staked lure and the prison tank
855541669 Borers keep digging, the ants who dared the water are ruins, and the oils are a plant
5cc1f1e17 Not farmed, imprisoned - and the lure has no bloodless option
dedd2837b Verticality is paint, so the mud is what actually defends the crown
28d898abb Four triggers and four reasons, which compose instead of competing
00ed662c0 Five Fever Wood items filed with their prose, and the ledger synced
d2ae43760 Eighteen invented Fever Wood plants, organised by height above the water
9dde13365 The trunks cannot fall, the crown needs soil to grow on, and the birds are alien
b808d4c8a The drive-off ladder, and a severed tentacle is how the food economy works
614402757 The thing below becomes ambient and named, and the mud is what delivers you to it
41d69d6f4 Dianoga canon expanded: the giant form is its own subject, and lavender is not canon
b0040410d rimflow: close SKILL_SIZE_SPLIT_PASS_1 at adea63eab
adea63eab SKILL_SIZE_SPLIT_PASS_1: rimworld-modding 659→451 into its references; sprites 887→366 + new rimworld-sprite-facings skill
197a6ceda rimflow: file SKILL_SIZE_SPLIT_PASS_1 (two SKILL.md files past 500 lines after the drain)
bda86e26d Transient: purge 679 uncited files older than 14 days (234 MB) — owner ruling 2026-09-23
b4ceabb8c LESSONS_INBOX: 18 more drained into git-efficiency; 11 homeless remain
ffe5916e2 LESSONS_INBOX: 308 of 337 entries drained into their owning skills; 29 homeless remain, each with a proposed home
6348c81e6 Second-pass drain: 96 more lessons into 15 skills; artpipe README gains "Operating the daemon — traps"
e0ca4e636 run_selftests: a test may declare its own timeout; deployed_biome_refs declares 720 s
7220ef3c2 selftest_artpipe: probe the grumpiness detector relative to artpiped's constants, not literal percentages
... 12 more: git log --oneline f1b8be402..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/codebase_health.html   MACBENCH — auto-regenerated by the health publisher, which `code_review_status.py` spawns on every prune/list; not hand-edited
 M Transient/codebase_health.json   MACBENCH — auto-regenerated by the health publisher, which `code_review_status.py` spawns on every prune/list; not hand-edited
 M Transient/codebase_health_artifact.html   MACBENCH — auto-regenerated by the health publisher, which `code_review_status.py` spawns on every prune/list; not hand-edited
 M infrastructure/dashboards/hub/data/health.json   MACBENCH — auto-regenerated by the health publisher, which `code_review_status.py` spawns on every prune/list; not hand-edited
 M infrastructure/state/codebase_health_last.json   MACBENCH — auto-regenerated by the health publisher, which `code_review_status.py` spawns on every prune/list; not hand-edited
 M infrastructure/state/queue/BENCH.md   MACBENCH — auto-regenerated by the health publisher, which `code_review_status.py` spawns on every prune/list; not hand-edited
 M infrastructure/state/queue/FOUNDRY.md   MACBENCH — auto-regenerated by the health publisher, which `code_review_status.py` spawns on every prune/list; not hand-edited
```

